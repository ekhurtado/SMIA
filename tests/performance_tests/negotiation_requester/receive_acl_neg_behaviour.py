import logging

from smia import GeneralUtils

from smia.utilities.general_utils import DockerUtils
from spade.behaviour import CyclicBehaviour

from smia.logic import acl_smia_messages_utils
from neg_requester_utils import save_prefix_csv_metrics_timestamp, save_csv_neg_metrics, get_safe_env_var

_logger = logging.getLogger(__name__)

class ReceiveACLNegBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA NR (Negotiation Requester) will
     receive about completed negotiations between others SMIAs in the I4.0 System.
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

        self.num_iterations = get_safe_env_var('NUM_ITERATIONS', default=1, var_type=int)
        self.parallel_negotiations = get_safe_env_var('PARALLEL_NEGOTIATIONS', default=1, var_type=int)

        self.received_negs = 0
        self.myagent.received_negs_threads = set()


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(timeout=5)  # Timeout set to 10 seconds so as not to continuously execute the behavior
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
                    # await save_csv_neg_metrics_timestamp(
                    #     metrics_folder, self.myagent.jid, iteration=self.myagent.requested_negs_dict[msg.thread],
                    #     neg_thread=msg.thread, description='Negotiation error with thread [{}]: reason '
                    #                                        '[{}]'.format(msg.thread, msg_parsed_body['reason']))
                    csv_data = await self.get_csv_data_from_thread(msg.thread,
                                                                   GeneralUtils.get_current_timer_nanosecs())
                    if csv_data is not None:
                        csv_data['elapsed_time']= 'N/A'
                        await save_csv_neg_metrics(metrics_folder, **csv_data)
                        _logger.assetinfo("Saved error negotiation with thread {} in CSV file.".format(msg.thread))
                else:
                    winner_jid = acl_smia_messages_utils.get_sender_from_acl_msg(msg)
                    _logger.assetinfo("--> Received negotiation winner for thread [{}] ({}/{}): {}"
                                      .format(msg.thread, len(self.myagent.received_negs_threads) + 1,
                                              (self.num_iterations * self.parallel_negotiations), winner_jid))

                    # TODO BORRAR -> es para obtener los datos para el analisis
                    from smia.utilities import smia_archive_utils, smia_general_info
                    metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                    if metrics_folder is None:
                        metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                    # await save_csv_neg_metrics_timestamp(
                    #     metrics_folder, self.myagent.jid, iteration=self.myagent.requested_negs_dict[msg.thread],
                    #     neg_thread=msg.thread, description='Negotiation completed with thread [{}]: winner '
                    #                                        '[{}]'.format(msg.thread, winner_jid))
                    csv_data = await self.get_csv_data_from_thread(msg.thread, GeneralUtils.get_current_timer_nanosecs())
                    if csv_data is not None:
                        await save_csv_neg_metrics(metrics_folder, **csv_data)
                        _logger.assetinfo("Saved data of negotiation with thread {} in CSV file.".format(msg.thread))
                self.received_negs += 1
                self.myagent.received_negs_threads.add(msg.thread)

            if len(self.myagent.received_negs_threads) == (self.num_iterations * self.parallel_negotiations):
                _logger.assetinfo("#### ALL NEGOTIATION WINNERS RECEIVED ####")

                # TODO BORRAR -> es para obtener los datos para el analisis
                from smia.utilities import smia_archive_utils, smia_general_info
                metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                if metrics_folder is None:
                    metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                await save_prefix_csv_metrics_timestamp(metrics_folder, self.myagent.jid, 'ready-')

            else:
                _logger.info("There are yet negotiations that are not completed.")
        # else:
        #     _logger.info("         - No message received within 10 seconds on SMIA NR (ReceiveACLNegBehaviour)")



    async def get_csv_data_from_thread(self, thread, received_time):
        """
        This methods get all the required data of the negotiation to be saved in the CSV obtaining from the information
        in the agent using the thread.
        """
        if thread not in self.myagent.requested_negs_dict:
            _logger.warning("A thread has been received that does not belong to any requested negotiation.")
            return None

        neg_request_data = self.myagent.requested_negs_dict[thread]
        participants = self.myagent.negs_participants
        parallel_negs = get_safe_env_var('PARALLEL_NEGOTIATIONS', default=1, var_type=int)
        neg_iter = neg_request_data['negIter']
        experiment_iter = neg_request_data['experimentIter']

        return {'participants': participants, 'parallel_negs': parallel_negs,
                'neg_iter': neg_iter, 'experiment_iter': experiment_iter,
                'experiment_id': f"{participants}.{parallel_negs}.{neg_iter}.{experiment_iter}",
                'elapsed_time': received_time - neg_request_data['requestedTime']}
