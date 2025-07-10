#!/usr/bin/env python3
import sys

import connexion

from swagger_server.aas_infrastructure_tools.aas_repository_infrastructure_info import AASRepositoryInfrastructureInfo
from swagger_server.aas_infrastructure_tools.aas_open_api_tools import AASOpenAPITools
from swagger_server.aas_infrastructure_tools.aas_repository_information import AASRepositoryInformation
from swagger_server.css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server import encoder, util

def main():

    # First, whether the user has configured the SMIA KB is checked
    util.configure_smia_kb(sys.argv[1:])

    # Then, the ontology is initialized
    CapabilitySkillOntology.get_instance().initialize_ontology()

    # If there is an SQLite persistence file with ontology data, it will be loaded
    # TODO De momento sin implementar
    # CapabilitySkillOntology.get_instance().load_ontology_from_persistence()

    # When the application has been started, the banner can be printed
    util.print_smia_kb_banner()

    if AASRepositoryInfrastructureInfo.get_self_extract_css():
        # In this case it has been configured to self-extract CSS information from the AAS Repository
        # Now let's check the connection with the AAS Repository in order to obtain AAS information
        if not AASOpenAPITools.check_aas_repository_availability():
            print("The AAS repository is not available, please check it if any CSS information is to be extracted "
                  "from AAS.", file=sys.stderr)
        else:
            # If the AAS Repository is available, all the CSS information will be extracted from the AAS data
            aas = AASRepositoryInformation()
            aas.extract_css_information_from_aas_repository()

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'SMIA Knowledge Base (KB) | HTTP/REST | API Collection'}, pythonic_params=True)
    app.run(port=8080)


if __name__ == '__main__':
    main()
