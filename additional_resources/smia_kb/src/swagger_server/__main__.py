#!/usr/bin/env python3
import io
import json
import logging
import sys

import connexion
import owlready2

import util
from aas_infrastructure_tools import AASOpenAPITools, AASRepositoryInformation
from css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server import encoder

# ontology = None

def main():

    # TODO PRUEBA PARA USO DE ONTOLOGIA (de momento se ha colocado la carga de la ontologia aqui, pero hay que pensar donde realizarla)
    # global ontology
    # ontology = owlready2.get_ontology('./css_smia_ontology/CSS-ontology-smia-without-module.owl')
    # try:
    #     ontology.load()
    # except owlready2.OwlReadyOntologyParsingError as e:
    #     print("Error with the ontology!: {}".format(e))
    ontology = CapabilitySkillOntology.get_instance()
    ontology.initialize_ontology()

    # Let's check the connection with the AAS Repository
    if not AASOpenAPITools.check_aas_repository_availability():
        print("The AAS repository is not available, please check it if any CSS information is to be extracted "
              "from AAS.", file=sys.stderr)

    # TODO PRUEBA (BORRAR)
    aas = AASRepositoryInformation()
    aas.extract_css_information_from_aas_repository()
    # aas.save_all_aas_repository_information()


    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'SMIA Knowledge Base (KB) | HTTP/REST | API Collection'}, pythonic_params=True)
    app.run(port=8080)


if __name__ == '__main__':
    main()
