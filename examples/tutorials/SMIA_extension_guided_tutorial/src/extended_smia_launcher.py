import asyncio

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from extended_services import extended_agent_service
from extended_asset_interface import MyExtendedInterface, test_asset_connection
from extended_agent_capability import DiagnosisAgentCapability


def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()

    # The AAS model is added to SMIA
    smia.load_aas_model('../SMIA_extension_guided_tutorial.aasx')

    # Create and run the extensible agent object
    my_extensible_smia_agent = ExtensibleSMIAAgent('gcis1@xmpp.jp', 'gcis1234')

    # ---
    # Add the extended agent service
    my_extensible_smia_agent.add_new_agent_service('ExtendedAgentService', extended_agent_service)

    # # Executing agent services...
    # try:
    #     asyncio.run(my_extensible_smia_agent.agent_services.execute_agent_service_by_id('ExtendedAgentService', extended_param=26))
    # except Exception as e:
    #     print("ERROR: An agent service cannot be executed.")

    # ---
    # Add the extended Asset Interface (AssetConnection)
    extended_asset_interface = MyExtendedInterface()
    my_extensible_smia_agent.add_new_asset_connection('MyExtendedInterface', extended_asset_interface)

    # # Executing asset service in extended interface...
    # asyncio.run(test_asset_connection(my_extensible_smia_agent))

    # ---
    # Add the extended agent capability
    extended_agent_cap = DiagnosisAgentCapability(agent_object=my_extensible_smia_agent)
    my_extensible_smia_agent.add_new_agent_capability(extended_agent_cap)

    smia.run(my_extensible_smia_agent)

if __name__ == '__main__':
    main()