import smia

from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from internal_logic import HealthSupervisorBehaviour

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()

    # The AAS model is added to SMIA
    aas_model_path = smia.utilities.general_utils.DockerUtils.get_aas_model_from_env_var()
    # aas_model_path = smia.utilities.general_utils.DockerUtils.get_aas_model_from_env_var()
    smia.load_aas_model('../SimulatedAssets_OperationalHealthSupervisor.aasx')

    # Create and run the extensible agent object
    ohs_extensible_smia_agent = ExtensibleSMIAAgent('gcis1@xmpp.jp', 'gcis1234')

    # Add its extended capability
    ohs_extended_cap = HealthSupervisorBehaviour(agent_object=ohs_extensible_smia_agent)
    ohs_extensible_smia_agent.add_new_agent_capability(ohs_extended_cap)

    smia.run(ohs_extensible_smia_agent)

if __name__ == '__main__':
    main()