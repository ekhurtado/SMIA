import logging

from smia.utilities.general_utils import DockerUtils
from spade.behaviour import CyclicBehaviour

from smia.logic import acl_smia_messages_utils
from neg_requester_utils import save_ready_csv_metrics_timestamp, save_csv_neg_metrics_timestamp

_logger = logging.getLogger(__name__)

class ReceiveACLNegBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA PE will receive from the
    others SMIAs in the I4.0 System. If some of these messages are responses to previous SMIA PE requests, the associated
    BPMNPerformerBehaviour will be unlocked to continue execution of the production plan.
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
        _logger.info("ReceiveACLNegBehaviour starting...")

        self.num_negotiations = DockerUtils.get_env_var('NUM_NEGOTIATIONS')
        if self.num_negotiations is None:
            self.num_negotiations = 1
        else:
            self.num_negotiations = int(self.num_negotiations)
        self.received_negs = 0

        self.myagent.received_negs_threads = set()


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior
        if msg:
            # This method will receive all ACL messages to the SMIA NR, so it will check if some of them are responses to
            # previous SMIA NR requests
            _logger.aclinfo("Analyzing ACL message... Checking if it is a response from previous SMIA NR message... ")
            _logger.aclinfo(msg)
            msg_parsed_body = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)

            if (('winner' in msg_parsed_body and msg.thread not in self.myagent.received_negs_threads)
                or ('reason' in msg_parsed_body and msg.thread not in self.myagent.received_negs_threads)):

                if 'reason' in msg_parsed_body:
                    _logger.warning("--> Error in negotiation with thread {}: {}".format(msg.thread,
                                                                                            msg_parsed_body['reason']))

                    # TODO BORRAR -> es para obtener los datos para el analisis
                    from smia.utilities import smia_archive_utils, smia_general_info
                    metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                    if metrics_folder is None:
                        metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                    await save_csv_neg_metrics_timestamp(metrics_folder, self.myagent.jid, neg_thread=msg.thread,
                                                         description='Negotiation error with thread [{}]: reason [{}]'
                                                         .format(msg.thread, msg_parsed_body['reason']))
                else:
                    winner_jid = acl_smia_messages_utils.get_sender_from_acl_msg(msg)
                    _logger.aclinfo("--> Received negotiation winner for thread [{}]: {}".format(
                        msg.thread, winner_jid))

                    # TODO BORRAR -> es para obtener los datos para el analisis
                    from smia.utilities import smia_archive_utils, smia_general_info
                    metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                    if metrics_folder is None:
                        metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                    await save_csv_neg_metrics_timestamp(metrics_folder, self.myagent.jid, neg_thread=msg.thread,
                                                         description='Negotiation completed with thread [{}]: winner '
                                                                     '[{}]'.format(msg.thread, winner_jid))

                self.received_negs += 1
                self.myagent.received_negs_threads.add(msg.thread)

            if len(self.myagent.received_negs_threads) == self.num_negotiations:
                _logger.info("--> ALL NEGOTIATION WINNERS RECEIVED")

                # TODO BORRAR -> es para obtener los datos para el analisis
                from smia.utilities import smia_archive_utils, smia_general_info
                metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                if metrics_folder is None:
                    metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                await save_ready_csv_metrics_timestamp(metrics_folder)

            else:
                _logger.info("There are yet negotiations that are not completed.")
        else:
            _logger.info("         - No message received within 10 seconds on SMIA NR (ReceiveACLNegBehaviour)")


