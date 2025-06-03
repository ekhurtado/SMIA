import json
import logging
import os

from smia import GeneralUtils
from smia.logic import inter_aas_interactions_utils
from smia.logic.agent_services import AgentServices
from smia.logic.exceptions import RequestDataError, ServiceRequestExecutionError
from spade.behaviour import CyclicBehaviour

from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAJSONSchemas

from behaviours.handle_acl_openapi_behaviour import HandleACLOpenAPIBehaviour
from external_infrastructures.smia_kb_infrastructure import SMIAKBInfrastructure
from logic.acl_open_api_services import ACLOpenAPIServices
from utilities.smia_acl_message_info import SMIAACLMessageInfo

_logger = logging.getLogger(__name__)


class ACLOpenAPIHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA ISM will receive from the
    others SMIAs in the I4.0 System to perform some service related to OpenAPI infrastructures.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        # Let's take advantage of SMIA 'AgentServices' class to save service method identifiers with its associated
        # execution method to simplify the code of handling each service request
        self.myagent.acl_openapi_services = AgentServices(self.myagent)

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("ACLOpenAPIHandlingBehaviour starting...")

        # Let's register all Infrastructure Services of SMIA ISM in relation with ACL-OpenAPI
        for service_id, service_method in ACLOpenAPIServices.ACLOpenAPIServicesMap.items():
            await self.myagent.acl_openapi_services.save_agent_service(service_id, service_method)
        _logger.info("Successfully loaded all Infrastructure Services with their associated execution methods.")

        # The OpenAPI connectivity information also need to be configured (for now only through environmental variables)
        if os.environ.get('SMIA_KB_IP') is not None:
            SMIAKBInfrastructure.set_ip_address(os.environ.get('SMIA_KB_IP'))
        if os.environ.get('SMIA_KB_HOST') is not None:
            SMIAKBInfrastructure.set_ip_address_host(os.environ.get('SMIA_KB_HOST'))
        if os.environ.get('SMIA_KB_PORT') is not None:
            SMIAKBInfrastructure.set_port(int(os.environ.get('SMIA_KB_PORT')))

        # TODO TEST
        # try:
        #     params = {'asset_id': 'http://example.com/ids/asset001'}
        #     result = await self.myagent.acl_openapi_services.execute_agent_service_by_id('GetSMIAInstanceByAssetId',
        #                                                                                  **params)
        #     params = {'capability_iri': 'http://www.w3id.org/upv-ehu/gcis/css-smia#Negotiation'}
        #     result = await self.myagent.acl_openapi_services.execute_agent_service_by_id('GetAssetIDsOfCapability',
        #                                                                                  **params)
        # except ValueError as e:
        #     if "required parameters have not been provided" in str(e):
        #         print("Aqui habria que responder con failure por el motivo (no se ha enviado el parametro)")


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            if not SMIAACLMessageInfo.SMIA_ISM_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE.match(msg):
                # If it does not match the SMIA ISM template, there is no need to parse the message as it is not for
                # this behaviour.
                _logger.warning("Invalid message received on SMIA ISM: ACL message with invalid template.")
                return  # If it does not match the template, the ACL message is for SMIA ISM


            # An ACL message has been received by a SMIA agent, so it needs to perform some service related to the OpenAPI
            _logger.aclinfo("         + Message received on SMIA ISM (ACLOpenAPIHandlingBehaviour) from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The message body will be converted to a JSON object and validated against the AAS Infrastructure Service
            # schema
            msg_json_body = json.loads(msg.body)
            try:
                await inter_aas_interactions_utils.check_received_request_data_structure(
                    msg_json_body, ACLSMIAJSONSchemas.JSON_SCHEMA_ACL_SMIA_ONTOLOGIES_MAP.get(
                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB)))
            except RequestDataError as cap_request_error:
                # The added data are not valid, so a Refuse message to the requester must be sent
                # TODO MODIFICAR LA RESPUESTA CON LA NUEVA ESTRUCTURA
                svc_execution_error = ServiceRequestExecutionError(msg.thread, cap_request_error.message,
                    msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB), self)
                await svc_execution_error.handle_service_execution_error()
                _logger.warning("The sender [{}] has sent an message with thread [{}] that has invalid data, therefore "
                                "the requester has been informed with a Refuse ACL message".format(
                    GeneralUtils.get_sender_from_acl_msg(msg), msg.thread))
                return  # The run method is terminated to restart checking for new messages.

            # At this point, the received data for the AAS Infrastructure Service is valid, so the behaviour to manage
            # this specific interaction can be triggered
            # TODO BORRAR (para pruebas con GUI Agent): {"serviceID": "serviceID", "serviceType": "InfrastructureService","SMIAInfrastructureService": "GetAssetIDsOfCapability", "serviceParams": {"capability_iri": "http://www.w3id.org/upv-ehu/gcis/css-smia#Negotiation"}}
            _logger.aclinfo("The SMIA sender [{}], within thread [{}], needs a service related to OpenAPI "
                            "infrastructures to be performed. A specific behavior will be triggered to handle this "
                            "request..".format(GeneralUtils.get_sender_from_acl_msg(msg), msg.thread))
            specific_handling_behav = HandleACLOpenAPIBehaviour(self.agent, received_acl_msg=msg)
            self.myagent.add_behaviour(specific_handling_behav)

        else:
            _logger.info("         - No message received within 10 seconds on SMIA ISM (ACLOpenAPIHandlingBehaviour)")