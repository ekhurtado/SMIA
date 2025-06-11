import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils

from behaviours.bpmn_performer_behaviour import BPMNPerformerBehaviour
from behaviours.receive_acl_behaviour import ReceiveACLBehaviour

_logger = logging.getLogger(__name__)

# This is the starter file to launch the SPIA (Self-configurable Planning Industrial Agents)

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SPIA ...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PASSWD')

    # TODO BORRAR (para pruebas)
    # smia_jid = "smia-pe@xmpp.jp"
    # smia_psswd = "gcis1234"
    # smia.load_aas_model('../smia_archive/config/aas/SPEIA_CeDRI_ScenarioA.aasx')

    # Create the agent object
    spia_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    # The behavior to receive all ACL messages and check if they are replies to previous SPIA messages is added
    receive_acl_behaviour = ReceiveACLBehaviour(spia_agent)
    spia_agent.add_new_agent_capability(receive_acl_behaviour)

    # The behaviour for executing the CSS-driven BPMN production plan is added
    bpmn_performer_behaviour = BPMNPerformerBehaviour(spia_agent)
    spia_agent.add_new_agent_capability(bpmn_performer_behaviour)

    smia.run(spia_agent)

if __name__ == '__main__':

    # Run main program with SMIA
    main()