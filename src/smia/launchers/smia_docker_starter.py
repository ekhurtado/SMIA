"""
This is the SMIA launch file for Docker, which runs the program logic inside a virtualization container.
"""

import logging
import os

import smia
from smia.agents.smia_agent import SMIAAgent
from smia.utilities.general_utils import DockerUtils

_logger = logging.getLogger(__name__)

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()
    # When the AAS model path has been obtained, it is added to SMIA
    if aas_model_path is not None:
        _logger.info("The AAS model file has been added as environmental variable.")
        smia.load_aas_model(aas_model_path)

    # The AAS model is obtained from the environmental variables
    aas_id = DockerUtils.get_aas_model_from_env_var()
    # When the AAS model path has been obtained, it is added to SMIA
    if aas_id is not None:
        _logger.info("The AAS ID has been added as environmental variable.")
        smia.load_aas_id(aas_id)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PASSWD')

    # Create the agent object
    smia_agent = SMIAAgent(smia_jid, smia_psswd)
    smia.run(smia_agent)

if __name__ == '__main__':

    # Run main program with SMIA
    main()
