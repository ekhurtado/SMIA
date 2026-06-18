import json
import logging
from json import JSONDecodeError

from smia.logic.exceptions import RequestDataError, ServiceRequestExecutionError
from spade.behaviour import CyclicBehaviour

from smia.behaviours.specific_handle_behaviours.handle_capability_behaviour import HandleCapabilityBehaviour
from smia.behaviours.specific_handle_behaviours.handle_aas_related_svc_behaviour import HandleAASRelatedSvcBehaviour
from smia.logic import inter_smia_interactions_utils, acl_smia_messages_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAJSONSchemas, ACLSMIAOntologyInfo

_logger = logging.getLogger(__name__)


class ACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA will receive from the
    others standardized SMIAs in the I4.0 System.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("ACLHandlingBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        try:
            # Wait for a message with the standard ACL template to arrive.
            msg = await self.receive(
                timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
            if msg:
                # An ACL message has been received by the agent
                _logger.aclinfo("         + Message received on SMIA (ACLHandlingBehaviour) from {}".format(msg.sender))
                _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

                # If the ontology value is not within the valid values in the SMIA approach, a 'not understood' ACL message
                # is returned.
                if (msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB) not in
                        ACLSMIAJSONSchemas.JSON_SCHEMA_ACL_SMIA_ONTOLOGIES_MAP.keys()):
                    await inter_smia_interactions_utils.send_response_msg_from_received(
                        self, msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_NOT_UNDERSTOOD)
                    return  # The run method is terminated to restart checking for new messages

                # Only if the thread is not reserved it needs to be processed
                if msg.thread not in self.myagent.reserved_threads:
                    # First, the message body will be checked against the associated ontology JSON Schema (only if it is not an
                    # inform message, since this type of message can be strings)
                    if msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) != FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                        try:
                            # The msg body will be parsed to a JSON object
                            msg_json_body = json.loads(msg.body)

                            await inter_smia_interactions_utils.check_received_request_data_structure(
                                msg_json_body, ACLSMIAJSONSchemas.JSON_SCHEMA_ACL_SMIA_ONTOLOGIES_MAP.get(
                                    msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB)))
                        except (RequestDataError, JSONDecodeError) as cap_request_error:
                            # The added data are not valid, so a Refuse message to the requester must be sent
                            if isinstance(cap_request_error, JSONDecodeError):
                                cap_request_error.message = f"JSON error: {str(cap_request_error)}"
                            svc_execution_error = ServiceRequestExecutionError(msg.thread, cap_request_error.message,
                                                                               msg.get_metadata(
                                                                                   FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB), self)
                            await svc_execution_error.handle_service_execution_error()
                            _logger.warning("The sender [{}] has sent an message with thread [{}] that has invalid data, therefore "
                                            "it has been informed with a Refuse ACL message".format(
                                acl_smia_messages_utils.get_sender_from_acl_msg(msg), msg.thread))
                            return  # The run method is terminated to restart checking for new messages

                    # Depending on the message ontology, the associated specific behavior will be added to the agent to handle
                    # the required actions
                    match msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB):
                        case ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE:
                            specific_handling_behaviour = HandleCapabilityBehaviour(self.myagent, received_acl_msg=msg)
                        case _:
                            specific_handling_behaviour = HandleAASRelatedSvcBehaviour(self.myagent, received_acl_msg=msg)
                    self.myagent.add_behaviour(specific_handling_behaviour)
                    _logger.info("Specific behaviour added to the agent to handle the message with thread [{}].".format(
                        msg.thread))

            else:
                _logger.info("         - No message received within 10 seconds on SMIA (ACLHandlingBehaviour)")
        except Exception as e:
            _logger.error("ERROR in ACLHandlingBehaviour: {}".format(e))
