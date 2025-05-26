import json
import logging

from smia.logic import inter_aas_interactions_utils
from smia.logic.agent_services import AgentServices
from spade.behaviour import CyclicBehaviour

from smia.utilities.fipa_acl_info import FIPAACLInfo

from behaviours.handle_acl_openapi_behaviour import HandleACLOpenAPIBehaviour
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
            if not SMIAACLMessageInfo.SMIA_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE.match(msg):
                _logger.warning("Invalid message received on SMIA ISM: ACL message with invalid template.")
                return  # If it does not match the template, the ACL message is for SMIA ISM


            # An ACL message has been received by a SMIA agent, so it needs to perform some service related to the OpenAPI
            _logger.aclinfo("         + Message received on SMIA ISM (ACLOpenAPIHandlingBehaviour) from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # TODO BORRAR (para pruebas con GUI Agent): {"serviceID": "serviceID", "serviceType": "InfrastructureService","SMIAInfrastructureService": "GetAssetIDsOfCapability", "serviceParams": {"capability_iri": "http://www.w3id.org/upv-ehu/gcis/css-smia#Negotiation"}}

            # Depending on the performative of the message, the agent will have to perform some actions or others
            match msg.get_metadata('performative'):
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:
                    _logger.aclinfo("The performative of the message is Request, so the SMIA sender needs a service "
                                    "related to OpenAPI infrastructures to be performed. A specific behavior will be "
                                    "triggered to handle this request..")
                    svc_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                    specific_handling_behav = HandleACLOpenAPIBehaviour(self.agent, svc_req_data)
                    self.myagent.add_behaviour(specific_handling_behav)
                # TODO pensar mas performativas
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                    _logger.aclinfo("The performative of the message is Request, so the SMIA sender wants to inform about something")

                case _:
                    _logger.error("ACL performative type not available.")

        else:
            _logger.info("         - No message received within 10 seconds on SMIA ISM (ACLOpenAPIHandlingBehaviour)")