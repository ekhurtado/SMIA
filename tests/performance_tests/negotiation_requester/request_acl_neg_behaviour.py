import asyncio
import csv
import logging
import os

from smia import CriticalError, GeneralUtils

from smia.logic import acl_smia_messages_utils, inter_smia_interactions_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas
from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)

class RequestACLNegBehaviour(CyclicBehaviour):
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
        _logger.info("RequestACLNegBehaviour starting...")

        # TODO BORRAR -> es para obtener los datos para el analisis
        from smia.utilities import smia_archive_utils, smia_general_info
        import os
        metrics_folder = os.environ.get('METRICS_FOLDER')
        if metrics_folder is None:
            metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
        await smia_archive_utils.save_csv_metrics_timestamp(metrics_folder, self.myagent.jid, 'SMIA NR started')

        self.num_negotiations = RequestACLNegBehaviour.get_env_var('NUM_NEGOTIATIONS')
        if self.num_negotiations is None:
            self.num_negotiations = 1
        else:
            self.num_negotiations = int(self.num_negotiations)

        self.requested_negs = 0
        self.smia_instances_ids = RequestACLNegBehaviour.get_env_var('TARGET_IDS')
        if self.smia_instances_ids is None:
            CriticalError("The SMIA Negotiation Requester needs the identifiers of SMIA instances to request the negotiations.")
        else:
            self.smia_instances_ids = [item.strip() for item in self.smia_instances_ids.split(',') if item.strip()]

        self.myagent.requested_negs_threads = set()

        _logger.info("Waiting 10 seconds until the target instances are ready...")
        #await asyncio.sleep(5)
        await asyncio.sleep(0.5*len(self.smia_instances_ids))  # Wait until the target instances are ready (2 seconds for each instance)




    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        if self.requested_negs < self.num_negotiations:

            cfp_thread = await acl_smia_messages_utils.create_random_thread(self.myagent)
            for smia_instance_id in self.smia_instances_ids:
                # await asyncio.sleep(1)  # Wait 1 second between negotiation requests
                cfp_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
                    smia_instance_id, cfp_thread, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
                    ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE, protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                    msg_body=await acl_smia_messages_utils.generate_json_from_schema(
                        ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE, capabilityIRI='http://www.w3id.org/upv-ehu/gcis/css-smia#Negotiation',
                        skillIRI='http://www.w3id.org/hsu-aut/css#NegotiationBasedOnRAM',
                        negCriterion='http://www.w3id.org/hsu-aut/css#NegotiationBasedOnRAM',
                        negRequester=str(self.myagent.jid), negTargets=self.smia_instances_ids))
                await self.send(cfp_acl_message)

            _logger.aclinfo("FIPA-CNP to thread [{}] initiated with SMIA candidates {}".format(cfp_thread, self.smia_instances_ids))
            

            self.myagent.requested_negs_threads.add(cfp_thread)

            # Since this behavior is specific to the messages with these threads, it reserves it so that the generic
            # ACLHandlingBehavior does not process them.
            await self.myagent.add_reserved_thread(cfp_thread)

            # TODO BORRAR -> es para obtener los datos para el analisis
            from smia.utilities import smia_archive_utils, smia_general_info
            import os
            metrics_folder = os.environ.get('METRICS_FOLDER')
            if metrics_folder is None:
                metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
            await smia_archive_utils.save_csv_metrics_timestamp(
                metrics_folder, self.myagent.jid, 'Negotiation requested with thread [{}]'.format(cfp_thread))

            await asyncio.sleep(5)
            #await asyncio.sleep(120)

            self.requested_negs += 1

            # # Wait for a message with the standard ACL template to arrive.
            # msg = await self.receive(
            #     timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
            # if msg:
            #     _logger.assetinfo("\n --------------- OLD BEHAVIOUR MSG RECEIVED --------------\nmsg: {}\n".format(msg))    # TODO BORRAR !!!!!!!!!!!!!!!!!!!!!!!!!!!


            #     # This method will receive all ACL messages to the SMIA NR, so it will check if some of them are responses to
            #     # previous SMIA NR requests
            #     _logger.aclinfo("Analyzing ACL message... Checking if it is a response from previous SMIA NR message... "
            #                     "Unlocking SMIA NR...")
            #     _logger.aclinfo(msg)
            #     msg_parsed_body = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)
            #     _logger.aclinfo(msg_parsed_body)

            #     _logger.assetinfo("\n --------------- Parsed msg: {}\n".format(msg_parsed_body))    # TODO BORRAR !!!!!!!!!!!!!!!!!!!!!!!!!!!

            #     if 'winner' in msg_parsed_body:

            #         _logger.assetinfo("\n --------------- Winner of {} ".format(msg.thread))    # TODO BORRAR !!!!!!!!!!!!!!!!!!!!!!!!!!!

            #         winner_jid = acl_smia_messages_utils.get_sender_from_acl_msg(msg)

            #         _logger.assetinfo("\n ---------------   + {} ".format(winner_jid))    # TODO BORRAR !!!!!!!!!!!!!!!!!!!!!!!!!!!

            #         _logger.aclinfo("Received negotiation winner for thread [{}]: {}".format(
            #             msg.thread, winner_jid))

            #         # TODO BORRAR -> es para obtener los datos para el analisis
            #         from smia.utilities import smia_archive_utils, smia_general_info
            #         import os
            #         metrics_folder = os.environ.get('METRICS_FOLDER')
            #         if metrics_folder is None:
            #             metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
            #         await smia_archive_utils.save_csv_metrics_timestamp(
            #             metrics_folder, self.myagent.jid,
            #             'Negotiation completed with thread [{}]: winner [{}]'.format(msg.thread, winner_jid))
            # else:
            #     _logger.info("         - No message received within 10 seconds on SMIA NR (RequestACLNegBehaviour)")
        else:
            _logger.info("All the negotiations have been sent.")

            # # TODO BORRAR -> es para obtener los datos para el analisis
            # from smia.utilities import smia_archive_utils, smia_general_info
            # import os
            # metrics_folder = os.environ.get('METRICS_FOLDER')
            # if metrics_folder is None:
            #     metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
            # await self.save_ready_csv_metrics_timestamp(metrics_folder)

            await asyncio.sleep(10)

    @staticmethod
    def get_env_var(env_var_name):
        """
        This method returns the value obtained from a specific environmental variable.

        Returns:
            str: value of the environmental variable.
        """
        env_var_value = os.environ.get(env_var_name)
        if env_var_value is None:
            _logger.warning("The environment variable [{}] is not set, so check that it is not "
                            "necessary.".format(env_var_name))
            return None
        return env_var_value

    async def save_ready_csv_metrics_timestamp(self, folder_path):

        agent_jid = await acl_smia_messages_utils.get_agent_id_from_jid(self.myagent.jid)
        description = 'SMIA NR all negotiations requested'
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)  # If necessary, the folder is created

        file_path = f"{folder_path}/ready-{agent_jid}-metrics.csv"
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                    writer.writerow(['AgentID', 'Timestamp', 'Description'])
                writer.writerow(
                    [f"{agent_jid}", f"{GeneralUtils.get_current_timestamp_microsecs():.4f}", f"{description}"])
        except Exception as e:
            print(f"Error writing to file: {e}")