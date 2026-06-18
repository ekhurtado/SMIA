import json
import logging
from json import JSONDecodeError

from smia import GeneralUtils
from spade.behaviour import CyclicBehaviour

from smia.behaviours.specific_handle_behaviours.handle_negotiation_behaviour import HandleNegotiationBehaviour
from smia.logic import inter_smia_interactions_utils, acl_smia_messages_utils
from smia.logic.exceptions import RequestDataError, ServiceRequestExecutionError
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAJSONSchemas

_logger = logging.getLogger(__name__)


class NegotiatingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles the negotiation requests made by other standardized SMIAs
    through ACL messages in the I4.0 System.
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

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("NegotiationBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.aclinfo("         + Message received on SMIA (NegotiatingBehaviour) from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # This behaviour only manages interactions related to negotiations (FIPA-CNP protocol)

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
                    _logger.warning(
                        "The sender [{}] has sent an message with thread [{}] that has invalid data, therefore "
                        "it has been informed with a Refuse ACL message".format(
                            acl_smia_messages_utils.get_sender_from_acl_msg(msg), msg.thread))
                    return  # The run method is terminated to restart checking for new messages

            # When the message content has been validated, the specific behavior will be added to the agent to handle
            # the required actions within the FIPA-CNP protocol
            handle_neg_template_propose = GeneralUtils.create_acl_template(
                performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE,
                protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL, thread=msg.thread)
            handle_neg_template_request = GeneralUtils.create_acl_template(
                performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
                protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL, thread=msg.thread)
            handle_neg_template = handle_neg_template_propose | handle_neg_template_request
            # handle_neg_template = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_PROPOSE
            # handle_neg_template.thread = msg.thread
            specific_neg_handling_behaviour = HandleNegotiationBehaviour(self.agent, received_acl_msg=msg)
            self.myagent.add_behaviour(specific_neg_handling_behaviour, handle_neg_template)
            _logger.info("Specific behaviour added to the agent to handle the message with thread [{}].".format(
                msg.thread))


        else:
            _logger.info("         - No message received within 10 seconds on SMIA (NegotiatingBehaviour)")


