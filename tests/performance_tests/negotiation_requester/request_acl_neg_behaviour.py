import asyncio
import logging
import os

from spade.behaviour import CyclicBehaviour

from neg_requester_utils import save_csv_neg_metrics_timestamp
from smia import CriticalError
from smia.logic import acl_smia_messages_utils, inter_smia_interactions_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas
from smia.utilities.general_utils import DockerUtils

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
        from smia.utilities import smia_general_info
        metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
        if metrics_folder is None:
            metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
        await save_csv_neg_metrics_timestamp(metrics_folder, self.myagent.jid, description='SMIA NR started')

        self.num_negotiations = DockerUtils.get_env_var('NUM_NEGOTIATIONS')
        if self.num_negotiations is None:
            self.num_negotiations = 1
        else:
            self.num_negotiations = int(self.num_negotiations)

        self.req_cycle_time = DockerUtils.get_env_var('REQUEST_CYCLE_TIME')
        if self.req_cycle_time is None:
            self.req_cycle_time = 5.0
        else:
            self.req_cycle_time = float(self.req_cycle_time)

        self.requested_negs = 0
        self.smia_instances_ids = DockerUtils.get_env_var('TARGET_IDS')
        if self.smia_instances_ids is None:
            CriticalError("The SMIA Negotiation Requester needs the identifiers of SMIA instances to request the negotiations.")
        else:
            self.smia_instances_ids = [item.strip() for item in self.smia_instances_ids.split(',') if item.strip()]

        self.myagent.requested_negs_threads = set()

        _logger.info("Waiting {} seconds until the target instances are ready..."
                     "".format(0.5*len(self.smia_instances_ids)))
        # Wait until the target instances are ready (0.5 seconds for each instance)
        await asyncio.sleep(0.5*len(self.smia_instances_ids))

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        if self.requested_negs < self.num_negotiations:

            cfp_thread = await acl_smia_messages_utils.create_random_thread(self.myagent)

            # Since this behavior is specific to the messages with these threads, it reserves it so that the generic
            # ACLHandlingBehavior does not process them.
            await self.myagent.add_reserved_thread(cfp_thread)

            for smia_instance_id in self.smia_instances_ids:
                # await asyncio.sleep(1)  # Wait 1 second between negotiation requests
                cfp_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
                    smia_instance_id, cfp_thread, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
                    ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE, protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                    msg_body=await acl_smia_messages_utils.generate_json_from_schema(
                        ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE,
                        capabilityIRI='http://www.w3id.org/upv-ehu/gcis/css-smia#Negotiation',
                        skillIRI='http://www.w3id.org/hsu-aut/css#NegotiationBasedOnRAM',
                        negCriterion='http://www.w3id.org/hsu-aut/css#NegotiationBasedOnRAM',
                        negRequester=str(self.myagent.jid), negTargets=self.smia_instances_ids))
                await self.send(cfp_acl_message)

            _logger.aclinfo("FIPA-CNP to thread [{}] initiated with SMIA candidates {}"
                            .format(cfp_thread, self.smia_instances_ids))
            self.myagent.requested_negs_threads.add(cfp_thread)

            # TODO BORRAR -> es para obtener los datos para el analisis
            from smia.utilities import smia_general_info
            metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
            if metrics_folder is None:
                metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
            await save_csv_neg_metrics_timestamp(
                metrics_folder, self.myagent.jid, neg_num=self.requested_negs, neg_thread=cfp_thread,
                description='Negotiation requested with thread [{}]'.format(cfp_thread))

            await asyncio.sleep(self.req_cycle_time)
            #await asyncio.sleep(120)

            self.requested_negs += 1

        else:
            _logger.info("All the negotiations have been sent.")

            await asyncio.sleep(20)

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

