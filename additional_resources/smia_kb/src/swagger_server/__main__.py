#!/usr/bin/env python3
import io
import json
import logging
import sys

import connexion
import owlready2

import util
from aas_infrastructure_tools.aas_open_api_tools import AASOpenAPITools
from aas_infrastructure_tools.aas_repository_information import AASRepositoryInformation
from css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server import encoder

# ontology = None

def main():

    # First, whether the user has configured the SMIA KB is check
    util.configure_smia_kb(sys.argv[1:])

    # Then, the ontology is initialized
    ontology = CapabilitySkillOntology.get_instance()
    ontology.initialize_ontology()

    # When the application has been started, the banner can be printed
    util.print_smia_kb_banner()

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
