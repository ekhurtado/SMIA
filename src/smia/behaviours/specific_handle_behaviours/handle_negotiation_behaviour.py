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
        self.neg_thread = self.received_acl_msg.thread
        self.all_targets_list = set(self.received_body_json['negTargets'])
        if str(self.myagent.jid) in self.all_targets_list:
            self.all_targets_list.remove(str(self.myagent.jid))   # Removes its own JID
        self.targets_processed = set()
        self.targets_remaining = set(self.received_body_json['negTargets'])

        self.neg_value = 0.0
        self.negotiation_result = None

        # If not all proposals have been received, three retries are set to request them again (using request)
        self.max_retries = 3
        self.current_retries = 0

        # The safe iterations (to keep the behavior alive in case the other participants have not finished processing)
        # are set depending on the number of participants in the negotiation. The total number of iterations is at
        # least 10 or based on the number of targets
        self.safe_iterations = max(10, int(len(self.received_body_json['negTargets'])*0.2))

        self.requested_timestamp = GeneralUtils.get_current_timestamp()

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleNegotiationBehaviour starting for [{}]...".format(self.neg_thread))

        # Since this behavior is specific to the messages in this thread, it reserves it so that the generic
        # ACLHandlingBehavior does not process them.
        await self.myagent.add_reserved_thread(self.neg_thread)

        # Before starting, if the FIPA-CNP protocol is related to a CSS service, it will perform the capability checking
        if (self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB) ==
                ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE):
            result, reason = await css_operations.capability_checking(self.myagent, self.received_body_json)
            if not result:
                _logger.info("The SMIA has received a negotiation with failed capability checking [" +
                             self.neg_thread + "]")

                # Since the capability check failed, it will reply to the sender with a Refuse message
                await inter_smia_interactions_utils.send_response_msg_from_received(
                    self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REFUSE,
                    response_body={'reason': 'CapabilityChecking failed: {}'.format(reason)})
                _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                + self.neg_thread + "]")

                # The negotiation value will be -1 to lose all comparisons
                self.neg_value = -1.0

        # First, it will analyze whether it is the only participant in the negotiation, in which case it will be the
        # direct winner
        if len(self.received_body_json['negTargets']) == 1:
            # There is only one target available (therefore, it is the only one, so it is the winner)
            _logger.info("The SMIA has won the negotiation with thread [" + self.neg_thread + "]")

            # As the winner, it will reply to the sender with the result of the negotiation
            await inter_smia_interactions_utils.send_response_msg_from_received(
                self, self.received_acl_msg, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, response_body={'winner': True})
            _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                            + self.neg_thread + "]")

            # The information will be stored in the log and the SMIA instance ends as the winner
            await self.exit_negotiation(is_winner=True)

        else:
            # In this case, there are multiple participants, so it will execute the FIPA-SMIA-CNP protocol
            try:
                # First, the times between message transmissions and active waiting times for reception are calculated.
                # Dynamic wait time between messages: wait time to allow incoming messages to be processed while other
                # messages are being sent.
                time_base = 0.005   # is set as the minimum time to serialize an XMPP message.
                time_jitter = 0.001 # Randomness to avoid scenarios where everyone sends at the same time
                time_sleep_base = time_base + (len(self.received_body_json['negTargets']) * time_jitter)
                time_sleep_range = time_sleep_base * 0.1    # 10 %
                self.time_sleep = time_sleep_base + random.uniform(-time_sleep_range, 0)

                # Dynamic recovery timeout: waiting time to process messages to be received once all messages have been
                # sent (e.g., when sending retry requests)
                security_factor = 3.0   # A multiplier to absorb network delays
                total_transmission_time = (len(self.received_body_json['negTargets']) - 1) * self.time_sleep
                self.recovery_wait = total_transmission_time * security_factor

                #  The value of the criterion must be obtained just before starting to manage the negotiation, so that at the
                #  time of sending the PROPOSE and receiving that of the others it will be the same value.
                await self.get_neg_value_with_criteria()

                # Once the negotiation value is reached, the negotiation management can begin (run method).
            except (CapabilityRequestExecutionError, AssetConnectionError) as cap_neg_error:
                if isinstance(cap_neg_error, AssetConnectionError):
                    cap_neg_error = CapabilityRequestExecutionError(self.neg_thread,'Negotiation',
                                                                    f"The error [{cap_neg_error.error_type}] "
                                                                    f"has appeared during the asset connection. "
                                                                    f"Reason: {cap_neg_error.reason}.", self)

                await cap_neg_error.handle_capability_execution_error_old()
                return  # killing a behaviour does not cancel its current run loop


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # if self.initial_iteration:
        #     # In the first iteration, each agent waits for a set amount of time relative to the number of participants
        #     # in the negotiation to ensure that everyone has arrived at their run method.
        #     await asyncio.sleep(max(3, 0.05*len(self.all_targets_list)))
        #     self.initial_iteration = False

        # The first step in each iteration is to send the PROPOSE message with your own value to the other participants
        # in the negotiation. In this case, one iteration is performed to distribute the communication load.
        await self.send_propose_acl_msgs()  # Envia los propose en la primera iteracion de espera

        if len(self.targets_remaining) == 0:
            timeout = self.recovery_wait
            # await asyncio.sleep(self.recovery_wait)
        else:
            timeout = 0
            # await asyncio.sleep(random.uniform(0.2, 2))

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(timeout=timeout)  # Timeout set to 0s to continuously execute the behavior
        if msg:
            if msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE:
                # A PROPOSE ACL message has been received by the agent
                _logger.aclinfo("         + PROPOSE Message received on SMIA Agent (HandleNegotiationBehaviour "
                                "in charge of the negotiation with thread [" + self.neg_thread + "])")
                _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

                # The msg body will be parsed to a JSON object
                propose_msg_body_json = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)

                # The negotiation information is obtained from the message
                # criteria = msg_json_body['serviceData']['serviceParams']['criteria']
                sender_agent_neg_value = propose_msg_body_json['negValue']

                if self.negotiation_result is None:
                    # Only if the negotiation is not resolved by this agent are the proposed messages analyzed
                    # The value of this SMIA and the received value are compared
                    if float(sender_agent_neg_value) > self.neg_value:
                        # As the received value is higher than this SMIA value, it must exit the negotiation.
                        self.negotiation_result = {'winner': False, 'timestamp': GeneralUtils.get_current_timestamp()}
                    if float(sender_agent_neg_value) == self.neg_value:
                        # In this case the negotiation is tied, so it must be managed
                        if not await self.handle_neg_values_tie(acl_smia_messages_utils.get_sender_from_acl_msg(msg),
                                                                float(sender_agent_neg_value)):
                            self.negotiation_result = {'winner': False,
                                                       'timestamp': GeneralUtils.get_current_timestamp()}

                # The target is added as processed in the local object (as it is a Python 'set' object there is no
                # problem of duplicate agents)
                self.targets_processed.add(acl_smia_messages_utils.get_sender_from_acl_msg(msg))

                if (len(self.targets_processed) == len(self.all_targets_list)) and self.negotiation_result is None:
                    # In this case all the values have already been received and the result is None, so the value of
                    # this SMIA is the best
                    _logger.info("The SMIA has won the negotiation with thread [" + msg.thread + "]")

                    # As the winner, it will reply to the sender with the result of the negotiation
                    inform_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
                        self.received_body_json['negRequester'], self.neg_thread,
                        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                        self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
                        protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                        msg_body={'winner': True})
                    await self.send(inform_acl_msg)
                    _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                    + msg.thread + "]")

                    # The negotiation can be terminated, in this case being the winner
                    self.negotiation_result = {'winner': True, 'timestamp': GeneralUtils.get_current_timestamp()}

            elif msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:
                # In this case some action is requested within the negotiation
                request_msg_body_json = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)
                if request_msg_body_json['requestedData'] == 'negValue':
                    sender_agent_jid = acl_smia_messages_utils.get_sender_from_acl_msg(msg)
                    _logger.aclinfo("         + REQUEST Message received on SMIA Agent (HandleNegotiationBehaviour) "
                                    "from " + sender_agent_jid + " with thread ["
                                    + self.neg_thread + "]) requesting the neg value")
                    # The neg value is sent with a PROPOSE message
                    self.targets_remaining.add(sender_agent_jid)
                    _logger.info("PROPOSE message sent with the requested neg value within thread [{}] to {}".format(
                        self.neg_thread, sender_agent_jid))

        else:
            # No ACL message has been received in this iteration
            if len(self.targets_remaining) == 0:
                # In this case, all PROPOSE messages have been sent
                if len(self.targets_processed) < len(self.all_targets_list):
                    if self.current_retries < self.max_retries:
                        # In this case, not all agents have been processed and there are still retries remaining
                        _logger.info("The negotiation with thread [{}] has not been resolved yet. Retry number {} "
                                     "requesting the negotiation value from the remaining targets."
                                     .format(self.neg_thread, self.current_retries + 1))
                        await self.request_remaining_neg_acl_msgs()
                        # 0.2 seconds are waited for each agent to receive messages
                        # await asyncio.sleep(0.2*(len(self.all_targets_list)-len(self.targets_processed)))
                        # await asyncio.sleep(random.uniform(0.2, 2))
                        # await asyncio.sleep(self.recovery_wait)
                        self.current_retries += 1
                else:
                    # In this case, all agents have been processed, so this agent has resolved the negotiation
                    if self.safe_iterations > 0:
                        # In safe iterations, it waits 0.1 second in case there is any agent that has not completed
                        # its processing
                        await asyncio.sleep(0.5)
                        self.safe_iterations -= 1
                    else:
                        if self.negotiation_result is not None:
                            # In this case the negotiation is resolved, so the behaviour can be killed
                            _logger.info("The negotiation with thread [{}] is resolved, so the behavior is killed"
                                         .format(self.neg_thread))
                            await self.exit_negotiation(is_winner=self.negotiation_result['winner'],
                                                        resolved_timestamp=self.negotiation_result['timestamp'])
                            return  # killing a behaviour does not cancel its current run loop
                        else:
                            # In this case  the negotiation is not resolved, so a failure message is sent to the requester
                            _logger.info(
                                "The negotiation with thread [{}] has not been resolved in {} safe iterations, so the "
                                "behavior is sending a 'FAILURE' message to the requester if it has not been resolved."
                                .format(self.neg_thread, self.safe_iterations))

                            missing_msgs = sum(
                                1 for jid_target in self.all_targets_list
                                if jid_target not in self.targets_processed
                            )

                            failure_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
                                self.received_body_json['negRequester'], self.neg_thread,
                                FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                                self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
                                msg_body={
                                    'reason': "Negotiation not resolved ({} propose messages are not received).".format(
                                        missing_msgs), 'exceptionType': 'CapabilityRequestExecutionError',
                                    'affectedElement': self.received_body_json['capabilityIRI']})
                            await self.send(failure_acl_msg)
                            _logger.aclinfo("ACL failure message sent for the negotiation request with thread ["
                                            + self.neg_thread + "]")
                            await self.exit_negotiation(is_winner=False)
                            return  # killing a behaviour does not cancel its current run loop


    async def get_neg_value_with_criteria(self):
        """
        This method gets the negotiation value based on a given criteria.

        Returns:
            int: value of the negotiation
        """
        _logger.info("Getting the negotiation value for [{}]...".format(self.neg_thread))

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
                    self.neg_thread))
                current_neg_value = await asset_connection_class.execute_asset_service(
                    interaction_metadata=aas_skill_interface_elem)
                _logger.assetinfo("Negotiation value for [{}] through an asset service obtained: {}.".format(
                    self.neg_thread, current_neg_value))
                if not isinstance(current_neg_value, float):
                    try:
                        current_neg_value = float(current_neg_value)
                    except ValueError as e:
                        # TODO PENSAR OTRAS EXCEPCIONES EN NEGOCIACIONES (durante el asset connection...)
                        _logger.error(e)
                        raise CapabilityRequestExecutionError(self.neg_thread, 'Negotiation',
                                                              "The requested negotiation {} cannot be executed because the "
                                                              "negotiation value returned by the asset does not have a valid"
                                                              " format.".format(self.neg_thread), self)
            else:
                # In this case, the value need to be obtained through an agent service
                try:
                    current_neg_value = await self.myagent.agent_services.execute_agent_service_by_id(
                        aas_skill_interface_elem.id_short)
                except (KeyError, ValueError) as e:
                    _logger.error(e)
                    raise CapabilityRequestExecutionError(self.neg_thread, 'Negotiation',
                                                          "The requested negotiation {} cannot be executed because the "
                                                          "negotiation value cannot be obtained through the agent service "
                                                          "{}.".format(self.neg_thread,
                                                                       aas_skill_interface_elem.id_short), self)

            # Let's normalize the value between 0.0 and 1.0
            if 1.0 < current_neg_value <= 100.0:
                # Normalize within 0.0 and 100.0 range
                current_neg_value = (current_neg_value - 0.0) / 100.0
            self.neg_value = current_neg_value

    async def send_propose_acl_msgs(self, targets=None):
        """
        This method sends the FIPA-ACL messages with the PROPOSE performative in order to offer the negotiation value.
        If no targets are set, only a message is sent to distribute the communication load.

        Args:
            targets (list, optional): the targets to whom the proposal message should be sent.
        """

        if targets is None:
            if len(self.targets_remaining) == 0:
                return
            targets = [self.targets_remaining.pop()]

        propose_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
            'N/A', self.neg_thread,
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE,
            self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
            protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
            msg_body={**self.received_body_json, **{'negValue': self.neg_value}})

        # This PROPOSE FIPA-ACL message is sent to all participants of the negotiation (except for this SMIA)
        for jid_target in targets:
            if jid_target != str(self.myagent.jid):
                propose_acl_message.to = jid_target
                await self.send(propose_acl_message)
                _logger.aclinfo("ACL PROPOSE negotiation message sent to " + jid_target +
                                "with neg value " + str(self.neg_value) +
                                " on negotiation with thread [" + self.neg_thread + "]")
                # await asyncio.sleep(0.01)   # It waits 0.01 second for each agent involved
                # await asyncio.sleep(random.uniform(0.005, 0.025))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                # await asyncio.sleep(random.uniform(0.015, 0.035))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                # await asyncio.sleep(random.uniform(0.025, 0.045))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                await asyncio.sleep(self.time_sleep)   # Calculated sleep time for each sent message

    async def request_remaining_neg_acl_msgs(self):
        """
        This method sends the FIPA-ACL messages with a request for the PROPOSE message in order to obtain their
        negotiation value.
        """
        request_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
            'N/A', self.neg_thread,
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
            self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
            protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
            msg_body={'requestedData': 'negValue'})

        # This REQUEST FIPA-ACL message is sent to all participants of the negotiation (except for this SMIA)
        for jid_target in self.all_targets_list:
            if (jid_target not in self.targets_processed) and (jid_target != str(self.myagent.jid)):
                request_acl_message.to = jid_target
                await self.send(request_acl_message)
                _logger.aclinfo("ACL REQUEST negotiation message sent to " + jid_target +
                                "requesting the neg value on thread [" + self.neg_thread + "]")
                # await asyncio.sleep(0.01)    # It waits 0.01 second for each agent involved
                # await asyncio.sleep(random.uniform(0.005, 0.025))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                # await asyncio.sleep(random.uniform(0.015, 0.035))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                # await asyncio.sleep(random.uniform(0.025, 0.045))   # It waits random seconds for each agent. 5–25 ms, with enough jitter to break synchronization.
                await asyncio.sleep(self.time_sleep)  # Calculated sleep time for each sent message

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
        random.seed(self.neg_thread)
        # As the negotiation values are the same, the following will be disturbed
        perturbations = {opt: random.uniform(-0.001, 0.001)
               for opt in sorted(scores_dict.keys())}
        scores_dict_disturbed = {opt: scores_dict[opt] * (1 + perturbations[opt])
                                 for opt in perturbations}

        if max(scores_dict_disturbed, key=lambda k: scores_dict_disturbed[k]) != str(self.myagent.jid):
            # In this case the SMIA instance has loosened the negotiation, so a False is returned
            return False
        return True


    async def exit_negotiation(self, is_winner, resolved_timestamp=None):
        """
        This method is executed when the trade has ended, either as a winner or a loser. In any case, all the
        information of the negotiation is added to the global variable with all the information of all the negotiations
         of the agent. The thread is used to differentiate the information of each negotiation, since this is the
         identifier of each one of them.

        Args:
            is_winner (bool): it determines whether the SMIA has been the winner of the negotiation.
            resolved_timestamp (int): timestamp when the negotiation is resolved.
        """
        if is_winner:
            _logger.info("The SMIA has finished the negotiation with thread [" + self.neg_thread +
                         "] as the winner")
        else:
            _logger.info("The SMIA has finished the negotiation with thread [" + self.neg_thread +
                         "] not as the winner")

        # The negotiation information is stored in the global object of the SMIA
        neg_data_json = negotiation_utils.create_neg_json_to_store(neg_requester_jid=self.received_body_json['negRequester'],
                                                                   participants=self.received_body_json['negTargets'],
                                                                   neg_criteria=self.received_body_json['negCriterion'],
                                                                   neg_value=self.neg_value, is_winner=is_winner)
        await self.myagent.save_negotiation_data(thread=self.neg_thread, neg_data=neg_data_json)

        # The information will be stored in the log
        if resolved_timestamp is None:
            resolved_timestamp = GeneralUtils.get_current_timestamp()
        smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp, resolved_timestamp,
                                                       await inter_smia_interactions_utils.acl_message_to_json(self.received_acl_msg), {'winner': is_winner},
                                                       self.received_acl_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB))

        # Since this behavior is specific to the messages in this thread, it releases it so that the generic
        # ACLHandlingBehavior can process them in the future.
        await self.myagent.remove_reserved_thread(self.neg_thread)

        # In order to correctly complete the negotiation process, this behavior is removed from the agent.
        self.kill(exit_code=10)
