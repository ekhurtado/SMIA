import json
import logging

from basyx.aas.adapter.json import AASToJsonEncoder

from smia.utilities.aas_related_services_info import AASRelatedServicesInfo

from smia.logic.services_utils import AgentServiceUtils
from spade.behaviour import OneShotBehaviour

from smia import GeneralUtils
from smia.aas_model.aas_model_utils import AASModelUtils
from smia.logic import inter_smia_interactions_utils, acl_smia_messages_utils
from smia.logic.exceptions import RequestDataError, ServiceRequestExecutionError, AASModelReadingError, \
    AssetConnectionError
from smia.utilities import smia_archive_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAJSONSchemas, ServiceTypes, ACLSMIAOntologyInfo
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HandleAASRelatedSvcBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles all the service requests that the SMIA has received. This
    request can arrive from an FIPA-ACL message as a :term:`Inter AAS Interaction` or from the AAS Core as an
    :term:`Intra AAS Interaction` message. This is a OneShotBehaviour because it handles an individual service request
    and then kills itself.
    """

    # TODO PENSAR SI AGRUPAR EN ESTA CLASE TANTO Requests como Responses ('HandleSvcBehaviour'), ya que para CSS solo
    #  hay CapabilityBehaviour. Dentro de esta se podria analizar la performativa (como ya se hace), para ver si es una
    #  peticion o una respuesta

    def __init__(self, agent_object, received_acl_msg):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
            received_acl_msg (spade.message.Message): the received ACL-SMIA message object
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.received_acl_msg = received_acl_msg
        self.received_body_json = acl_smia_messages_utils.get_parsed_body_from_acl_msg(self.received_acl_msg)

        self.requested_timestamp = GeneralUtils.get_current_timestamp()

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleAASRelatedSvcBehaviour starting to handle the service related to the message with thread"
                     " [{}]...".format(self.received_acl_msg.thread))

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # Depending on the type of service, the associated method will be launched
        match self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB):
            case (ACLSMIAOntologyInfo.ACL_ONTOLOGY_ASSET_RELATED_SERVICE |
                  ACLSMIAOntologyInfo.ACL_ONTOLOGY_AGENT_RELATED_SERVICE):
                await self.handle_asset_agent_related_service()
            case ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_SERVICE:
                await self.handle_aas_service()
            case ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE:
                await self.handle_aas_infrastructure_service()

        _logger.info("Management of the AAS-related service with thread {} finished.".format(self.received_acl_msg))

        # TODO BORRAR ENFOQUE ANTIGUO
        # # First, the performative of the request is obtained
        # match self.svc_req_data['performative']:
        #     case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:  # TODO actualizar dentro de todo el codigo los usos de performativas y ontologias de FIPA-ACL
        #         await self.handle_request()
        #     case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF:
        #         await self.handle_query_if()
        #     # TODO PensarOtros
        #     case _:
        #         _logger.error("Performative not available for service management.")

    # -------------------------------------
    # Asset-/agent-related services methods
    # -------------------------------------
    async def handle_asset_agent_related_service(self):
        """
        This method implements the logic to handle the asset- or agent-related type services.
        """
        try:
            match self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB):
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:
                    result = await self.handle_asset_agent_related_svc_request()
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                    _logger.aclinfo(f"The SMIA has been informed about the asset-/agent-related service related to the "
                                    f"thread [{self.received_acl_msg.thread}] with the content:{self.received_acl_msg.body}.")
                    # TODO
                case _:
                    unsupported_performative_msg = ("Cannot handle the asset-/agent-related service of the ACL "
                                                    "interaction with thread [{}] because the performative [{}] is not"
                                                    " yet supported.".format(
                        self.received_acl_msg.thread,
                        self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB)))
                    _logger.warning(unsupported_performative_msg)
                    raise RequestDataError(unsupported_performative_msg)

            # When the service is successfully performed the result will be sent to the requester
            await inter_smia_interactions_utils.send_response_msg_from_received(
                    self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, response_body=result)

            # The information will be stored in the log
            # TODO MODIFICAR ESTO CON LAS NUEVAS ESTRUCTURAS DE MENSAJES JSON
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.svc_req_data,
                                                           str(result),
                                                           self.svc_req_data['serviceType'])
        except (RequestDataError, ServiceRequestExecutionError,
                AASModelReadingError, AssetConnectionError) as svc_request_error:

            if isinstance(svc_request_error, RequestDataError):
                svc_request_error = ServiceRequestExecutionError(
                    self.received_acl_msg.thread, svc_request_error.message,
                    self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB), self)
            if isinstance(svc_request_error, AASModelReadingError):
                svc_request_error = ServiceRequestExecutionError(
                    self.received_acl_msg.thread, "{}. Reason:  {}".format(svc_request_error.message,
                                                                           svc_request_error.reason),
                    self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB), self)
            if isinstance(svc_request_error, AssetConnectionError):
                svc_request_error = ServiceRequestExecutionError(
                    self.received_acl_msg.thread,f"The error [{svc_request_error.error_type}] has appeared "
                                                 f"during the asset connection. Reason: {svc_request_error.reason}.",
                    self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB), self)

            await svc_request_error.handle_service_execution_error()
            return  # killing a behaviour does not cancel its current run loop

    async def handle_asset_agent_related_svc_request(self):
        """
        This method handles an Asset Related Service request. These services are part of I4.0 Application Component
        (application relevant).
        """
        # The asset/agent related service will be executed using a ModelReference to the related SubmodelElement related
        # with the execution method (in case of agent service) or element within AssetInterfacesSubmodel (in case of
        # asset service).

        # Since at this point the received data is valid, the AAS Reference object need to be created
        if isinstance(self.received_body_json['serviceRef'], str):
            self.received_body_json['serviceRef'] = await AASModelUtils.aas_model_reference_string_to_dict(
                self.received_body_json['serviceRef'])
        aas_asset_agent_service_ref = await AASModelUtils.create_aas_reference_object(
            'ModelReference', self.received_body_json['serviceRef'])
        aas_asset_agent_service_elem = await self.myagent.aas_model.get_object_by_reference(aas_asset_agent_service_ref)

        # If serviceParams is not defined in the JSON body is added None value to avoid errors
        if 'serviceParams' not in self.received_body_json:
            self.received_body_json['serviceParams'] = None

        # The asset connection class can be used to know the type of the service and it is also required to execute the
        # asset related service. It is obtained from the AAS asset service Reference object
        aas_asset_interface_ref = aas_asset_agent_service_elem.get_parent_ref_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE)
        if aas_asset_interface_ref is None:
            # In this case it is an agent-related service
            adapted_svc_params = await AgentServiceUtils.adapt_received_service_parameters(
                await self.myagent.agent_services.get_agent_service_by_id(aas_asset_agent_service_elem.id_short),
                self.received_body_json['serviceParams'])
            _logger.info(f"Executing agent service [{aas_asset_agent_service_elem.id_short}] "
                              f"within agent-related service of thread [{self.received_acl_msg.thread}]...")
            agent_service_execution_result = await self.myagent.agent_services.execute_agent_service_by_id(
                aas_asset_agent_service_elem.id_short, **adapted_svc_params)
            _logger.info(f"Successfully executed agent service [{aas_asset_agent_service_elem.id_short}] "
                              f"within agent-related service of thread [{self.received_acl_msg.thread}]...")
            return agent_service_execution_result
        else:
            # TODO PROBARLO (aunque deberia funcionar)
            asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(
                aas_asset_interface_ref)

            # With all necessary information obtained, the asset related service can be executed
            _logger.assetinfo(f"Executing asset service [{aas_asset_agent_service_elem.id_short}] "
                              f"within asset-related service of thread [{self.received_acl_msg.thread}]...")
            asset_service_execution_result = await asset_connection_class.execute_asset_service(
                interaction_metadata=aas_asset_agent_service_elem,
                service_input_data=self.received_body_json['serviceParams'])
            _logger.assetinfo(f"Executing asset service [{aas_asset_agent_service_elem.id_short}] "
                              f"within asset-related service of thread [{self.received_acl_msg.thread}]...")
            return asset_service_execution_result

    # --------------------
    # AAS services methods
    # --------------------
    async def handle_aas_service(self):
        """
        This method implements the logic to handle the AAS type services.
        """
        try:
            match self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB):
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_REF:
                    result = await self.handle_aas_svc_query_ref()
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                    _logger.aclinfo(f"The SMIA has been informed about the AAS service related to the thread"
                                    f" [{self.received_acl_msg.thread}] with the content:{self.received_acl_msg.body}.")
                    # TODO
                case _:
                    unsupported_performative_msg = ("Cannot handle the asset-/agent-related service of the ACL "
                                                    "interaction with thread [{}] because the performative [{}] is not"
                                                    " yet supported.".format(
                        self.received_acl_msg.thread,
                        self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB)))
                    _logger.warning(unsupported_performative_msg)
                    raise RequestDataError(unsupported_performative_msg)

            # When the service is successfully performed the result will be sent to the requester
            await inter_smia_interactions_utils.send_response_msg_from_received(
                self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, response_body=result)

            # The information will be stored in the log
            # TODO MODIFICAR ESTO CON LAS NUEVAS ESTRUCTURAS DE MENSAJES JSON
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.received_acl_msg,
                                                           str(result),
                                                           self.received_body_json['serviceType'])
        except (RequestDataError, ServiceRequestExecutionError, AASModelReadingError) as svc_request_error:
            if isinstance(svc_request_error, RequestDataError):
                svc_request_error = ServiceRequestExecutionError(self.received_acl_msg.thread,
                                                                 svc_request_error.message,
                                                                 self.received_body_json['serviceType'], self)
            if isinstance(svc_request_error, AASModelReadingError):
                svc_request_error = ServiceRequestExecutionError(self.received_acl_msg.thread,
                                                                 "{}. Reason: {}".format(svc_request_error.message,
                                                                                         svc_request_error.reason),
                                                                 self.received_body_json['serviceType'], self)
            await svc_request_error.handle_service_execution_error_old()
            return  # killing a behaviour does not cancel its current run loop

    async def handle_aas_svc_query_ref(self):
        """
        This method implements the logic to handle the Query-Ref performatives of AAS type services.
        """
        match self.received_body_json['serviceType']:
            case AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY:
                return await self.handle_aas_discovery_svc()
            case _:
                unsupported_service_type = ("Cannot handle the AAS service of the ACL interaction with thread [{}] "
                                            "because the service type [{}] is not yet supported.".format(
                    self.received_acl_msg.thread, self.received_body_json['serviceType']))
                _logger.warning(unsupported_service_type)
                raise RequestDataError(unsupported_service_type)

    async def handle_aas_discovery_svc(self):
        """
        This method implements the logic to handle the AAS type services of Discovery ServiceTypes.
        """
        match self.received_body_json['serviceID']:
            case (AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_BY_REF |
                  AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_VALUE_BY_REF):

                if isinstance(self.received_body_json['serviceParams'], str):
                    self.received_body_json['serviceParams'] = await AASModelUtils.aas_model_reference_string_to_dict(
                        self.received_body_json['serviceParams'])
                aas_object_ref = await AASModelUtils.create_aas_reference_object(
                    'ModelReference', self.received_body_json['serviceParams'])

                # When the appropriate Reference object is created, the requested SubmodelElement can be obtained
                requested_sme = await self.myagent.aas_model.get_object_by_reference(aas_object_ref)

                # When the AAS object has been obtained, the result is returned in JSON format
                if self.received_body_json['serviceID'] == AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_BY_REF:
                    return json.dumps(requested_sme, cls=AASToJsonEncoder)
                else:
                    if not hasattr(requested_sme, 'value'):
                        raise RequestDataError(f"The SubmodelElement queried with the reference ["
                                               f"{self.received_body_json['serviceParams']}] has not value, so it cannot"
                                               f" be returned")
                    if not isinstance(requested_sme.value, str):
                        return json.dumps(requested_sme.value, cls=AASToJsonEncoder)
                    return str(requested_sme.value)
            case AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_AAS_INFO:
                #TODO
                pass
            case AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_BY_ID:
                # TODO
                pass
            case _:
                unsupported_service_id = ("Cannot handle the AAS service of the ACL interaction with thread [{}] "
                                            "because the discovery service id [{}] is not yet supported.".format(
                    self.received_acl_msg.thread, self.received_body_json['serviceID']))
                _logger.warning(unsupported_service_id)
                raise RequestDataError(unsupported_service_id)

    # -----------------------------------
    # AAS infrastructure services methods
    # -----------------------------------
    async def handle_aas_infrastructure_service(self):
        """
        This method implements the logic to handle the Infrastructure services of AAS type services.
        """
        # The AAS Infrastructure Services are offered by the platform (in SMIA approach by SMIA ISM), not by SMIA
        # instances, so it will not realize any task
        pass

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # TODO BORRAR ENFOQUE ANTIGUO
    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_request(self):
        """
        This method handle capability requests to the DT.
        """
        # The type is analyzed to perform the appropriate service
        match self.svc_req_data['serviceType']:
            case ServiceTypes.ASSET_RELATED_SERVICE:
                # await self.handle_asset_related_svc()   # TODO
                await self.handle_asset_agent_related_svc_request()
            case ServiceTypes.AAS_INFRASTRUCTURE_SERVICE:
                await self.handle_aas_infrastructure_svc_request()  # TODO
            case ServiceTypes.AAS_SERVICE:
                await self.handle_aas_services_request()  # TODO
            case ServiceTypes.SUBMODEL_SERVICE:
                await self.handle_submodel_service_request()
            case _:
                _logger.error("Service type not available.")

    async def handle_query_if(self):
        """This method handle Query-If service requests. This request is received when the DT is asked about information
         related to a service."""
        pass
        # TODO FALTA POR HACER

    # -----------------------------------
    # Methods to handle specific services
    # -----------------------------------
    async def handle_aas_services_request(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info('AAS Service request: ' + str(self.svc_req_data))

    async def handle_aas_infrastructure_svc_request(self):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services
        (Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an AAS, but
        by the platform (computational infrastructure). These include the AAS Create Service (for creating AASs with unique
        identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery Services (for searching
        for AASs).

        """
        _logger.info('AAS Infrastructure Service request: ' + str(self.svc_req_data))




    async def send_response_msg_to_sender(self, performative, service_params):
        """
        This method creates and sends a FIPA-ACL message with the given serviceParams and performative.

        Args:
            performative (str): performative according to FIPA-ACL standard.
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_smia_interactions_utils.create_inter_smia_response_msg(
            receiver=self.svc_req_data['sender'],
            thread=self.svc_req_data['thread'],
            performative=performative,
            ontology='SvcResponse',
            service_id=self.svc_req_data['serviceID'],
            service_type=self.svc_req_data['serviceType'],
            service_params=json.dumps(service_params)
        )
        await self.send(acl_msg)

