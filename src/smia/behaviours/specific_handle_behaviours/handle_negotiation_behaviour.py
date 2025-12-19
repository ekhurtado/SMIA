import asyncio
import logging
import random

from spade.behaviour import CyclicBehaviour

from smia import GeneralUtils
from smia.css_ontology import css_operations
from smia.logic import negotiation_utils, inter_smia_interactions_utils, acl_smia_messages_utils
from smia.logic.exceptions import CapabilityRequestExecutionError, AssetConnectionError
from smia.utilities import smia_archive_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HandleNegotiationBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handle a particular negotiation.
    """
    myagent = None  #: the SPADE agent object of the SMIA agent.
    neg_value = None  #: value of the negotiation
    targets_processed = set()  #: targets that their values have been processed
    neg_value_event = None

    def __init__(self, agent_object, received_acl_msg):
        """
        The constructor method is rewritten to add the object of the agent
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

        if 'negRequester' not in self.received_body_json:
            # If it has not been added, it is added using the sender identifier
            self.received_body_json['negRequester'] = acl_smia_messages_utils.get_sender_from_acl_msg(
                self.received_acl_msg)

        # Negotiation-related variables are also initialized
        self.targets_processed = set()
        self.neg_value = 0.0
        self.myagent.tie_break = True   # In case of equal value neg is set as tie-breaker TODO check these cases (which need to be tie-breaker?)

        self.requested_timestamp = GeneralUtils.get_current_timestamp()

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleNegotiationBehaviour starting...")

        # Before starting, if the FIPA-CNP protocol is related to a CSS service, it will perform the capability checking
        if (self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB) ==
                ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE):
            result, reason = await css_operations.capability_checking(self.myagent, self.received_body_json)
            if not result:
                _logger.info("The SMIA has received a negotiation with failed capability checking [" +
                             self.received_acl_msg.thread + "]")

                # Since the capability check failed, it will reply to the sender with a Refuse message
                await inter_smia_interactions_utils.send_response_msg_from_received(
                    self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REFUSE,
                    response_body={'reason': 'CapabilityChecking failed: {}'.format(reason)})
                _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                + self.received_acl_msg.thread + "]")

                # The negotiation value will be -1 to lose all comparisons
                self.neg_value = -1.0


        # First, it will analyze whether it is the only participant in the negotiation, in which case it will be the
        # direct winner
        if len(self.received_body_json['negTargets']) == 1:
            # There is only one target available (therefore, it is the only one, so it is the winner)
            _logger.info("The SMIA has won the negotiation with thread [" + self.received_acl_msg.thread + "]")

            # As the winner, it will reply to the sender with the result of the negotiation
            await inter_smia_interactions_utils.send_response_msg_from_received(
                self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, response_body={'winner': True})
            _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                            + self.received_acl_msg.thread + "]")

            # The information will be stored in the log and the SMIA instance ends as the winner
            await self.exit_negotiation(is_winner=True)

        else:
            # In this case, there are multiple participants, so it will execute the FIPA-SMIA-CNP protocol

            await asyncio.sleep(1)  # Wait to ensure that other agents are ready to negotiate
            try:
                #  The value of the criterion must be obtained just before starting to manage the negotiation, so that at the
                #  time of sending the PROPOSE and receiving that of the others it will be the same value. Therefore, if to
                #  obtain the value you have to make an Intra AAS interaction request, the behaviour will not be able to start
                #  managing the negotiation until you get the answer to that request (together with the requested value).
                await self.get_neg_value_with_criteria()

                _logger.assetinfo(" ----- The neg value for thread [{}] is [{}]".format(self.received_acl_msg.thread, self.neg_value))      # TODO BORRAR

                # Once the negotiation value is reached, the negotiation management can begin. The first step is to send the
                # PROPOSE message with your own value to the other participants in the negotiation.
                propose_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
                    'N/A', await acl_smia_messages_utils.create_random_thread(self.myagent),
                    FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE,
                    self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
                    protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                    msg_body={**self.received_body_json, **{'negValue': self.neg_value}})
                # This PROPOSE FIPA-ACL message is sent to all participants of the negotiation (except for this SMIA)
                for jid_target in self.received_body_json['negTargets']:
                    if jid_target != str(self.agent.jid):
                        propose_acl_message.to = jid_target
                        await self.send(propose_acl_message)
                        _logger.aclinfo("ACL PROPOSE negotiation message sent to " + jid_target +
                                        " on negotiation with thread [" + self.received_acl_msg.thread + "]")
            except (CapabilityRequestExecutionError, AssetConnectionError) as cap_neg_error:
                if isinstance(cap_neg_error, AssetConnectionError):
                    cap_neg_error = CapabilityRequestExecutionError(self.received_acl_msg.thread,'Negotiation',
                                                                    f"The error [{cap_neg_error.error_type}] "
                                                                    f"has appeared during the asset connection. "
                                                                    f"Reason: {cap_neg_error.reason}.", self)

                await cap_neg_error.handle_capability_execution_error_old()
                return  # killing a behaviour does not cancel its current run loop


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(timeout=10)  # Timeout set to 10s so as not to continuously execute the behavior
        if msg:
            if msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE:
                # A PROPOSE ACL message has been received by the agent
                _logger.aclinfo("         + PROPOSE Message received on SMIA Agent (HandleNegotiationBehaviour "
                                "in charge of the negotiation with thread [" + self.received_acl_msg.thread + "])")
                _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

                # The msg body will be parsed to a JSON object
                propose_msg_body_json = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)

                # The negotiation information is obtained from the message
                # criteria = msg_json_body['serviceData']['serviceParams']['criteria']
                sender_agent_neg_value = propose_msg_body_json['negValue']

                _logger.assetinfo("Thread [{}] Received neg value from [{}]: [{}] and my value is [{}]".format(
                    msg.thread, msg.sender, sender_agent_neg_value, self.neg_value))  # TODO BORRAR

                # The value of this SMIA and the received value are compared
                if float(sender_agent_neg_value) > self.neg_value:
                    # As the received value is higher than this SMIA value, it must exit the negotiation.
                    await self.exit_negotiation(is_winner=False)
                    return  # killing a behaviour does not cancel its current run loop
                if float(sender_agent_neg_value) == self.neg_value:
                    # In this case the negotiation is tied, so it must be managed
                    if not await self.handle_neg_values_tie(acl_smia_messages_utils.get_sender_from_acl_msg(msg),
                                                            float(sender_agent_neg_value)):
                        _logger.assetinfo("The SMIA has not won  the negotiation tie")  # TODO BORRAR
                        await self.exit_negotiation(is_winner=False)
                        return  # killing a behaviour does not cancel its current run loop
                # The target is added as processed in the local object (as it is a Python 'set' object there is no problem
                # of duplicate agents)
                self.targets_processed.add(acl_smia_messages_utils.get_sender_from_acl_msg(msg))
                if len(self.targets_processed) == len(self.received_body_json['negTargets']) - 1:
                    # In this case all the values have already been received, so the value of this SMIA is the best
                    _logger.info("The SMIA has won the negotiation with thread [" + msg.thread + "]")

                    # As the winner, it will reply to the sender with the result of the negotiation
                    inform_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
                        self.received_body_json['negRequester'], self.received_acl_msg.thread,
                        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                        self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
                        protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                        msg_body={'winner': True})
                    await self.send(inform_acl_msg)
                    _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                    + msg.thread + "]")

                    # The negotiation can be terminated, in this case being the winner
                    await self.exit_negotiation(is_winner=True)
                    return

        else:
            _logger.info("         - No message received within 10 seconds on SMIA Agent (HandleNegotiationBehaviour)")

    async def get_neg_value_with_criteria(self):
        """
        This method gets the negotiation value based on a given criteria.

        Returns:
            int: value of the negotiation
        """
        _logger.info("Getting the negotiation value for [{}]...".format(self.received_acl_msg.thread))

        if self.neg_value != -1.0:

            # Since negotiation is a capability of the agent, it is necessary to analyze which skill has been defined.
            # The associated skill interface will be the one from which the value of negotiation can be obtained.
            # Thus, skill is the negotiation criterion for which the ontological instance will be obtained.
            neg_skill_instance = await self.myagent.css_ontology.get_ontology_instance_by_iri(
                self.received_body_json['negCriterion'])

            if neg_skill_instance is None:
                _logger.warning("This SMIA instance does not have the Skill Interface {} defined to obtain the "
                                "negotiation value. It will remain with the value 0.0.".format(
                    self.received_body_json['negCriterion']))
                return

            # The related skill interface will be obtained
            skill_interface = list(neg_skill_instance.get_associated_skill_interface_instances())[0]
            # The AAS element of the skill interface will be used to analyze the skill implementation
            aas_skill_interface_elem = await self.myagent.aas_model.get_object_by_reference(
                skill_interface.get_aas_sme_ref())

            parent_submodel = aas_skill_interface_elem.get_parent_submodel()
            if parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
                # In this case, the value need to be obtained through an asset service
                # With the AAS SubmodelElement of the asset interface the related Python class, able to connect to the
                # asset, can be obtained.
                aas_asset_interface_elem = aas_skill_interface_elem.get_associated_asset_interface()
                asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(aas_asset_interface_elem)
                _logger.assetinfo("The Asset connection of the Skill Interface has been obtained.")
                # Now the negotiation value can be obtained through an asset service
                _logger.assetinfo("Obtaining the negotiation value for [{}] through an asset service...".format(
                    self.received_acl_msg.thread))
                current_neg_value = await asset_connection_class.execute_asset_service(
                    interaction_metadata=aas_skill_interface_elem)
                _logger.assetinfo("Negotiation value for [{}] through an asset service obtained: {}.".format(
                    self.received_acl_msg.thread, current_neg_value))
                if not isinstance(current_neg_value, float):
                    try:
                        current_neg_value = float(current_neg_value)
                    except ValueError as e:
                        # TODO PENSAR OTRAS EXCEPCIONES EN NEGOCIACIONES (durante el asset connection...)
                        _logger.error(e)
                        raise CapabilityRequestExecutionError(self.received_acl_msg.thread, 'Negotiation',
                                                              "The requested negotiation {} cannot be executed because the "
                                                              "negotiation value returned by the asset does not have a valid"
                                                              " format.".format(self.received_acl_msg.thread), self)
            else:
                # In this case, the value need to be obtained through an agent service
                try:
                    current_neg_value = await self.myagent.agent_services.execute_agent_service_by_id(
                        aas_skill_interface_elem.id_short)
                except (KeyError, ValueError) as e:
                    _logger.error(e)
                    raise CapabilityRequestExecutionError(self.received_acl_msg.thread, 'Negotiation',
                                                          "The requested negotiation {} cannot be executed because the "
                                                          "negotiation value cannot be obtained through the agent service "
                                                          "{}.".format(self.received_acl_msg.thread,
                                                                       aas_skill_interface_elem.id_short), self)

            # Let's normalize the value between 0.0 and 1.0
            if 1.0 < current_neg_value <= 100.0:
                # Normalize within 0.0 and 100.0 range
                current_neg_value = (current_neg_value - 0.0) / 100.0
            self.neg_value = current_neg_value

    async def handle_neg_values_tie(self, received_agent_id, received_neg_value):
        """
        This method handles the situations where negotiation values tie. A seeded randomization process will be
        performed which will slightly modify the tied trading values and obtain a random winner. This method will be
        executed in all SMIA instances where the tie occurs, but since the ACL message thread is used as seed, they
        will all return the same result.

        Args:
            received_agent_id (str): identifier of the received SMIA agent proposal with the tie.
            received_neg_value (float): received tie negotiation value
        """
        if self.neg_value == -1.0 and received_neg_value == -1.0:
            # If both agents have not passed the Capability Check, neither of them can be the winner
            return False
        # First, the dictionary will be created with the agents that have the same negotiation value
        scores_dict = {str(self.myagent.jid): self.neg_value, received_agent_id: received_neg_value}
        # The pseudo-random number generator (PRNG) with the seed will give the same random values
        random.seed(self.received_acl_msg.thread)
        # As the negotiation values are the same, the following will be disturbed
        perturbations = {opt: random.uniform(-0.001, 0.001)
               for opt in sorted(scores_dict.keys())}
        scores_dict_disturbed = {opt: scores_dict[opt] * (1 + perturbations[opt])
                                 for opt in perturbations}

        _logger.assetinfo("Received value [{}] from [{}] to be compared with my value [{}]".format(
            received_agent_id, received_neg_value, self.neg_value))  # TODO BORRAR
        _logger.assetinfo("The SMIA has a negotiation tie with thread [{}], with values [{}]".format(
            self.received_acl_msg.thread, scores_dict_disturbed))  # TODO BORRAR

        if max(scores_dict_disturbed, key=lambda k: scores_dict_disturbed[k]) != str(self.myagent.jid):
            # In this case the SMIA instance has loosened the negotiation, so a False is returned
            return False
        return True

    async def exit_negotiation(self, is_winner):
        """
        This method is executed when the trade has ended, either as a winner or a loser. In any case, all the
        information of the negotiation is added to the global variable with all the information of all the negotiations
         of the agent. The thread is used to differentiate the information of each negotiation, since this is the
         identifier of each one of them.

        Args:
            is_winner (bool): it determines whether the SMIA has been the winner of the negotiation.

        """
        _logger.assetinfo("The SMIA has finished the negotiation with thread [{}], with the value [{}]"
                          ", so the result is {}".format(
            self.received_acl_msg.thread, self.neg_value, is_winner)) # TODO BORRAR

        if is_winner:
            _logger.info("The SMIA has finished the negotiation with thread [" + self.received_acl_msg.thread +
                         "] as the winner")
        else:
            _logger.info("The SMIA has finished the negotiation with thread [" + self.received_acl_msg.thread +
                         "] not as the winner")

        # The negotiation information is stored in the global object of the SMIA
        neg_data_json = negotiation_utils.create_neg_json_to_store(neg_requester_jid=self.received_body_json['negRequester'],
                                                                   participants=self.received_body_json['negTargets'],
                                                                   neg_criteria=self.received_body_json['negCriterion'],
                                                                   neg_value=self.neg_value, is_winner=is_winner)
        await self.myagent.save_negotiation_data(thread=self.received_acl_msg.thread, neg_data=neg_data_json)

        # The information will be stored in the log
        smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp, GeneralUtils.get_current_timestamp(),
            await inter_smia_interactions_utils.acl_message_to_json(self.received_acl_msg), {'winner': is_winner},
            self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB))

        # In order to correctly complete the negotiation process, this behavior is removed from the agent.
        self.kill(exit_code=10)
