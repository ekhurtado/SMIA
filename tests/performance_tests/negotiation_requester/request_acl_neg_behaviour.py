import asyncio
import logging
import os

from spade.behaviour import CyclicBehaviour

from neg_requester_utils import get_safe_env_var
from smia import CriticalError, GeneralUtils
from smia.logic import acl_smia_messages_utils, inter_smia_interactions_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas
from smia.utilities.general_utils import DockerUtils

_logger = logging.getLogger(__name__)

class RequestACLNegBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA NR (Negotiation Requester) will
     send to start negotiations between others SMIAs in the I4.0 System.
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

        # # TODO BORRAR -> es para obtener los datos para el analisis
        # from smia.utilities import smia_general_info
        # metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
        # if metrics_folder is None:
        #     metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
        # await save_csv_neg_metrics_timestamp(metrics_folder, self.myagent.jid, description='SMIA NR started')

        # try:
        #     self.num_iterations = int(DockerUtils.get_env_var('NUM_ITERATIONS'))
        # except (TypeError, ValueError):
        #     self.num_iterations = 1
        # try:
        #     self.parallel_negotiations = int(DockerUtils.get_env_var('PARALLEL_NEGOTIATIONS'))
        # except (TypeError, ValueError):
        #     self.parallel_negotiations = 1
        #
        # try:
        #     self.req_cycle_time = float(DockerUtils.get_env_var('REQUEST_CYCLE_TIME'))
        # except (TypeError, ValueError):
        #     self.req_cycle_time = 5.0

        self.num_iterations = get_safe_env_var('NUM_ITERATIONS', default=1, var_type=int)
        self.parallel_negotiations = get_safe_env_var('PARALLEL_NEGOTIATIONS', default=1, var_type=int)
        self.req_cycle_time = get_safe_env_var('REQUEST_CYCLE_TIME', default=5.0, var_type=float)

        self.smia_instances_ids = DockerUtils.get_env_var('TARGET_IDS')
        if self.smia_instances_ids is None:
            CriticalError("The SMIA Negotiation Requester needs the identifiers of SMIA instances to request the negotiations.")
        else:
            self.smia_instances_ids = [item.strip() for item in self.smia_instances_ids.split(',') if item.strip()]

        self.requested_all_negs = False
        self.myagent.requested_negs_threads = set()
        self.myagent.requested_negs_dict = {}
        self.myagent.negs_participants = len(self.smia_instances_ids)

        _logger.info("Waiting {} seconds until the target instances are ready..."
                     "".format(0.5*len(self.smia_instances_ids)))
        # Wait until the target instances are ready (0.5 seconds for each instance)
        await asyncio.sleep(0.5*len(self.smia_instances_ids))

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # if self.requested_negs_num < self.num_iterations:
        if not self.requested_all_negs:
            for experiment_iter in range(1, self.num_iterations + 1):

                for neg_iter in range(1, self.parallel_negotiations + 1):
                    cfp_thread = await acl_smia_messages_utils.create_random_thread(self.myagent)
                    cfp_thread += f":{experiment_iter}:{neg_iter}"

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
                    self.myagent.requested_negs_dict[cfp_thread] = {
                        'requestedTime': GeneralUtils.get_current_timer_nanosecs(),
                        'experimentIter': experiment_iter, 'negIter': neg_iter}

                    # # TODO BORRAR -> es para obtener los datos para el analisis
                    # from smia.utilities import smia_general_info
                    # metrics_folder = DockerUtils.get_env_var('METRICS_FOLDER')
                    # if metrics_folder is None:
                    #     metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                    # await save_csv_neg_metrics_timestamp(
                    #     metrics_folder, self.myagent.jid, iteration=self.myagent.requested_negs_dict[cfp_thread],
                    #     neg_thread=cfp_thread, description='Negotiation requested with thread [{}]'.format(cfp_thread))

                _logger.info("Waiting {} until the next iteration...".format(self.req_cycle_time))
                await asyncio.sleep(self.req_cycle_time)
                #await asyncio.sleep(120)

            self.requested_all_negs = True

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

