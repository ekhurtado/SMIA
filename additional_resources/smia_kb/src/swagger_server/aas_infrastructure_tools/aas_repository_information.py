import io
import json
import sys

import basyx.aas.adapter.json
from basyx.aas import model

import util
from aas_infrastructure_tools.aas_model_utils import AASModelUtils
from aas_infrastructure_tools.aas_open_api_tools import AASOpenAPITools
from aas_infrastructure_tools.aas_repository_info import AASRepositoryInfo
from css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from css_smia_ontology.css_smia_ontology import CapabilitySkillOntology


class AASRepositoryInformation:

    def __init__(self):
        self.all_aas_information_json = {'assetAdministrationShells': [], 'submodels': [], 'conceptDescriptions': []}
        self.aas_model_object_store: model.DictObjectStore[model.Identifiable] = None

    def extract_css_information_from_aas_repository(self):
        """
        This method gets all the AAS data in the AAS Repository, analyzes it, and extracts all the CSS information
        by creating the OWL ontological instances.
        """
        # First, the data is obtained from the AAS Repository
        self.save_all_aas_repository_information()

        # Then, the JSON data is transformed in Python AAS classes using BaSyx SDK
        self.read_aas_json_information()

        # Once objects are created, all AAS and their submodels will be analyzed to obtain the CSS data
        for aas_model_object in self.aas_model_object_store:
            if isinstance(aas_model_object, model.AssetAdministrationShell):
                aas_id = aas_model_object.id
                # First the ontological instances are created
                self.create_ontology_instances_from_aas(aas_model_object)
                # Once the ontological instances have been created, the relationships between them are analyzed.
                self.create_ontology_relationships_from_aas(aas_model_object)

                # # Todo borrar
                # print("PARA EL AAS CON ID [{}] SE HAN GENERADO ESTAS CLASES ONTOLOGICAS".format(aas_id))
                # for onto in CapabilitySkillOntology.get_instance().get_ontology().individuals():
                #     print("\t{} de la clase {}".format(onto, onto.is_a))
                #     print("\t\t y tiene las propiedades: {}".format(onto.data_properties_values_dict))
                #     cap_class = CapabilitySkillOntology.get_instance().get_ontology_class_by_iri(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
                #     if isinstance(onto, cap_class):
                #         print("\t\tEsta capacidad tiene las skills [{}] esta asociada al activo {}".format(onto.isRealizedBy, onto.get_associated_assets()))

    def create_ontology_instances_from_aas(self, aas_model_object):
        for submodel_data in aas_model_object.submodel:
            submodel_object = self.aas_model_object_store.get_identifiable(submodel_data.key[0].value)

            for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
                sme_list = AASModelUtils.get_submodel_elements_by_semantic_id(submodel_object, ontology_class_iri)
                ontology_class = CapabilitySkillOntology.get_instance().get_ontology_class_by_iri(ontology_class_iri)
                if ontology_class is None:
                    print("ERROR:The ontology class with IRI {} does not exist in the given OWL ontology. Check the "
                          "ontology file.", file=sys.stderr)
                    break
                for submodel_element in sme_list:
                    ontology_instance = CapabilitySkillOntology.get_instance().create_ontology_object_instance(
                        ontology_class, submodel_element.id_short)
                    capability_class = CapabilitySkillOntology.get_instance().get_ontology_class_by_iri(
                        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
                    if isinstance(ontology_instance, capability_class):
                        # The asset is associated to the created capability (or to the existing capability)
                        ontology_instance.add_associated_asset(AASModelUtils.get_asset_id_from_aas(aas_model_object))
                    ontology_required_value_iris = ontology_instance.get_data_properties_iris()
                    for required_value_iri in ontology_required_value_iris:
                        required_value = AASModelUtils.get_qualifier_value_by_semantic_id(submodel_element, required_value_iri)
                        required_value_name = ontology_instance.get_data_property_name_by_iri(required_value_iri)
                        ontology_instance.set_data_property_value(required_value_name, required_value)

    def create_ontology_relationships_from_aas(self, aas_model_object):
        for submodel_data in aas_model_object.submodel:
            submodel_object = self.aas_model_object_store.get_identifiable(submodel_data.key[0].value)
            for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS:
                rel_ontology_class = CapabilitySkillOntology.get_instance().get_ontology_class_by_iri(ontology_class_iri)
                if rel_ontology_class is None:
                    print("ERROR:The ontology class with IRI {} does not exist in the given OWL ontology. Check the "
                          "ontology file.", file=sys.stderr)
                    break
                sme_rels_list = AASModelUtils.get_submodel_elements_by_semantic_id(submodel_object, ontology_class_iri)
                for relationship_sm_elem in sme_rels_list:
                    first_rel_elem = AASModelUtils.get_object_by_reference(
                        self.aas_model_object_store, relationship_sm_elem.first)
                    second_rel_elem = AASModelUtils.get_object_by_reference(
                        self.aas_model_object_store, relationship_sm_elem.second)
                    if first_rel_elem is None or second_rel_elem is None:
                        print("WARNING: The relationship {} does not have the first and second elements well defined.".format(relationship_sm_elem))
                        break
                    domain_rel_elem, range_rel_elem = AASModelUtils.get_ontology_related_ordered_elements(
                        first_rel_elem, second_rel_elem, rel_ontology_class)
                    if domain_rel_elem is None or range_rel_elem is None:
                        # It is not a valid relationship
                        break
                    # At this point it is a valid relationship
                    # The ontological instances are obtained with the name since they are created by the same way
                    domain_instance = CapabilitySkillOntology.get_instance().get_ontology_instance_by_name(domain_rel_elem.id_short)
                    range_instance = CapabilitySkillOntology.get_instance().get_ontology_instance_by_name(range_rel_elem.id_short)
                    domain_instance.set_object_property_value(rel_ontology_class.name, range_instance)


    def save_all_aas_repository_information(self):
        """
        This method get the information all the AAS and their SubmodelElements from the AAS Repository and saves it.
        """
        # First, all the AAS JSON objects will be obtained
        print(f"Trying to obtain all the AAS JSON definitions from the repository")
        aas_json = AASOpenAPITools.send_http_get_request(AASRepositoryInfo.get_all_aas_json_url())
        if aas_json is None:
            print("ERROR: No AAS has been obtained.", file=sys.stderr)
            return
        self.all_aas_information_json['assetAdministrationShells'] = aas_json
        for aas_info in aas_json:
            aas_id = util.encode_string_in_base64_url(aas_info['id'])
            for submodel_ref_data in aas_info['submodels']:
                submodel_json = AASOpenAPITools.send_http_get_request(
                        AASRepositoryInfo.get_submodel_json_url_by_id(submodel_ref_data['keys'][0]['value']))
                self.all_aas_information_json['submodels'].append(submodel_json)

            # TODO Pensar si hace falta recoger los ConceptDescriptions

        # Lastly, the data will be cleaned to meet with the last version of the AAS meta-model
        self.all_aas_information_json = self.clean_aas_json_information(self.all_aas_information_json)

    def clean_aas_json_information(self, data):
        """
        This method removes all the data from previous versions of the AAS meta-model so that it can be read by BaSyx
        SDK. For instance, the attribute 'Referable/Category' is deprecated, so it must be removed if it is defined.
        """
        # The attribute 'Referable/Category' will be removed
        if isinstance(data, dict):
            # Create a new dictionary, removing the specified key and processing each value
            return {
                key: (None if 'modelType' in data.keys() and data['modelType'] == 'File' and value == ""
                      # else "NoneIdShort" if key == 'idShort' and value == ""
                else self.clean_aas_json_information(value))
                for key, value in data.items()
                if (key not in ['category']) # Add old attributes to be removed
                   and not (key == 'idShort' and value == "") # If idShort is not defined, it is removed
            }
        elif isinstance(data, list):
            # Apply recursively to each item in the list
            return [self.clean_aas_json_information(item) for item in data]
        else:
            # If it's neither a dict nor a list, just return it
            return data

    def read_aas_json_information(self):
        """
        This method uses BaSyx SDK to read all the AAS model JSON data from the repository and transforms it into
        Python AAS classes.
        """
        try:
            file_like_aas_json = io.StringIO(json.dumps(self.all_aas_information_json))   # BaSyx method needs a file-like object
            self.aas_model_object_store = basyx.aas.adapter.json.read_aas_json_file(file_like_aas_json)
        except ValueError as e:
            print("ERROR: Failed to read AAS model: invalid file. Reason: {}".format(e))
