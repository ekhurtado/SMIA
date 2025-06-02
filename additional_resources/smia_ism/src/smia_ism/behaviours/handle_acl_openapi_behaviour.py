import json
import logging

from smia.logic import inter_aas_interactions_utils
from smia.logic.exceptions import ServiceRequestExecutionError
from smia.utilities.fipa_acl_info import FIPAACLInfo
from spade.behaviour import OneShotBehaviour

from logic.acl_open_api_services import ACLOpenAPIServices
from utilities.smia_acl_message_info import SMIAACLMessageInfo

_logger = logging.getLogger(__name__)

class HandleACLOpenAPIBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles a request related to the capabilities of the Digital Twin.
    """

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
        self.received_json_data = json.loads(received_acl_msg.body)

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleCapabilityBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        match self.received_acl_msg.get_metadata('ontology'):
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:
                await self.handle_acl_openapi_request()
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF | FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_REF:
                await self.handle_acl_openapi_query()

    async def handle_acl_openapi_request(self):
        """
        This method implements the logic for handling requests to perform AAS Infrastructure Services.
        """
        # This behaviour receives a service to perform from other SMIA instance. All the available SMIA ISM services are
        # mapped with the service identifier and the associated execution method. This behaviour will get the service
        # identifier and will execute its associated service method. All services will respond with a boolean status
        # object (True if it has been correctly executed and False if it not) and the content for the ACL reply message
        try:
            requested_infrastructure_svc = self.received_json_data['serviceID']
            if requested_infrastructure_svc not in ACLOpenAPIServices.ACLOpenAPIServicesMap:
                # TODO MODIFICAR CON EL NUEVO METODO UTILS
                await inter_aas_interactions_utils.send_response_msg(
                    self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                    response_body={'reason': 'ACL-OpenAPI infrastructure service not found',
                                   'affectedElement': requested_infrastructure_svc, 'exceptionType': 'ServiceRequestExecutionError'})
            # At this point the Infrastructure Service can be executed
            _logger.info("The AAS Infrastructure Service {} has been requested.".format(requested_infrastructure_svc))
            result = await self.myagent.acl_openapi_services.execute_agent_service_by_id(requested_infrastructure_svc,
                                                                                         **self.received_json_data['serviceParams'])  # TODO PENSAR DONDE IRAN LOS PARAMETROS
            _logger.info("The AAS Infrastructure Service {} has been successfully executed.".format(requested_infrastructure_svc))
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'result': result})  # TODO PENSAR COMO SERIA EL MENSAJE DE RESPUESTA VALIDA
        except ServiceRequestExecutionError as svc_execution_error:
            # TODO PROGRAMARLO
            print("Usar este para responder aqui con un failure")

    async def handle_acl_openapi_query(self):
        """
        This method implements the logic for handling queries (Query-If or Query-Ref).
        """
        # TODO POR HACER
        pass

    async def send_response_msg_to_sender(self, received_msg, performative, response_body=None):
        """
        This method creates and sends a FIPA-ACL message with the given serviceParams and performative.

        Args:
            performative (str): performative according to FIPA-ACL standard.
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_aas_interactions_utils.create_acl_response_from_received_msg(received_msg, performative,
                                                                                     response_body)
        await self.send(acl_msg)