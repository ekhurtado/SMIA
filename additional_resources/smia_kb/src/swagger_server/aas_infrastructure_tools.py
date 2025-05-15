import io
import json
import sys
import time

import requests
import basyx.aas.adapter.json
from basyx.aas import model
from basyx.aas.util import traversal

import util
from css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from css_smia_ontology.css_smia_ontology import CapabilitySkillOntology


class AASRepositoryInfo:
    """
        Class to store server connection information with dynamic URL generation.
        """
    # Default values
    _AAS_HOST_IP_ADDRESS = 'http://192.168.186.129'  # TODO DE MOMENTO ESTA LA IP DE LA MAQUINA VIRTUAL. PENSARLO SI AÑADIRLO DE FORMA QUE SEA PARAMETRIZABLE (p.e. con variable de entorno para Docker)
    _AAS_REPOSITORY_PORT = 8081

    @classmethod
    def get_ip_address(cls):
        return cls._AAS_HOST_IP_ADDRESS

    @classmethod
    def set_ip_address(cls, ip_address):
        # Validate and normalize the IP address format
        if ip_address and not ip_address.startswith(('http://', 'https://')):
            ip_address = 'http://' + ip_address
        cls._AAS_HOST_IP_ADDRESS = ip_address

    @classmethod
    def get_port(cls):
        return cls._AAS_REPOSITORY_PORT

    @classmethod
    def set_port(cls, port):
        # Validate port is a number and in valid range
        try:
            port_num = int(port)
            if 1 <= port_num <= 65535:
                cls._AAS_REPOSITORY_PORT = port_num
            else:
                raise ValueError(f"ERROR: Port must be between 1-65535, got {port}")
        except (ValueError, TypeError):
            raise ValueError(f"ERROR: Port must be a valid integer, got {port}")

    # ---------------------------------------------
    # Methods to create URLs for the AAS Repository
    # ---------------------------------------------
    @classmethod
    def get_aas_repository_url(cls):
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}"

    @classmethod
    def get_all_aas_json_url(cls):
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/shells"

    @classmethod
    def get_submodel_json_url_by_id(cls, submodel_id):
        """
        This method returns the URL to obtain the information of a specific Submodel in JSON format. The Submodel
        identifier must be added in Base64-URL-encoded.
        """
        submodel_id_encoded = util.encode_string_in_base64_url(submodel_id)
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/submodels/{submodel_id_encoded}"


    # AAS_TOOLS_IP_ADDRESS = 'http://192.168.186.129'  # TODO DE MOMENTO ESTA LA IP DE LA MAQUINA VIRTUAL. PENSARLO SI AÑADIRLO DE FORMA QUE SEA PARAMETRIZABLE (p.e. con variable de entorno para Docker)
    # AAS_REPOSITORY_PORT = 8081
    # AAS_REPOSITORY_URL = AAS_TOOLS_IP_ADDRESS + ':' + str(AAS_REPOSITORY_PORT)  # TODO CUIDADO DE CUANDO SI MODIFIQUE EL IP ADDRESS (tambien hay que actualizar este)

    AAS_OPEN_API_COMMON_HEADERS = {"Accept": "application/json"}

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
                # for submodel_data in aas_model_object.submodel:
                #     submodel_json = self.aas_model_object_store.get_identifiable(submodel_data.key[0].value)
                    # submodel_json = self.aas_model_object_store[submodel_data.key[0].value]
                self.create_ontology_instances_from_aas(aas_model_object)
                # Once the ontological instances have been created, the relationships between them are analyzed.
                self.create_ontology_relationships_from_aas(aas_model_object)

                # Todo borrar
                print("PARA EL AAS CON ID [{}] SE HAN GENERADO ESTAS CLASES ONTOLOGICAS".format(aas_id))
                for onto in CapabilitySkillOntology.get_instance().get_ontology().individuals():
                    print("\t{} de la clase {}".format(onto, onto.is_a))

    def create_ontology_instances_from_aas(self, aas_model_object):
        for submodel_data in aas_model_object.submodel:
            submodel_object = self.aas_model_object_store.get_identifiable(submodel_data.key[0].value)

            for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
                sme_list = AASModelUtils.get_submodel_elements_by_semantic_id(submodel_object, ontology_class_iri)
                for submodel_element in sme_list:
                    ontology_class = CapabilitySkillOntology.get_instance().get_ontology_class_by_iri(ontology_class_iri)
                    if ontology_class is None:
                        print("ERROR:The ontology class with IRI {} does not exist in the given OWL ontology. Check the "
                              "ontology file.", file=sys.stderr)
                        break
                    ontology_instance = CapabilitySkillOntology.get_instance().create_ontology_object_instance(
                        ontology_class, submodel_element.id_short)
                    ontology_required_value_iris = ontology_instance.get_data_properties_iris()
                    print()

    def create_ontology_relationships_from_aas(self, aas_model_object):
        for submodel_data in aas_model_object.submodel:
            submodel_json = self.aas_model_object_store.get_identifiable(submodel_data.key[0].value)

            # TODO FALTA POR AÑADIR

    def save_all_aas_repository_information(self):
        """
        This method get the information all the AAS and their SubmodelElements from the AAS Repository and saves it.
        """
        # First, all the AAS JSON objects will be obtained
        print(f"Trying to obtain all the AAS JSON definitions from the repository")
        aas_json = AASOpenAPITools.send_http_get_request(AASRepositoryInfo.get_all_aas_json_url())
        # aas_json = AASOpenAPITools.send_http_get_request(AASRepositoryInfo.get_aas_repository_url() + '/shells')
        if aas_json is None:
            print("ERROR: No AAS has been obtained.", file=sys.stderr)
            return
        self.all_aas_information_json['assetAdministrationShells'] = aas_json
        for aas_info in aas_json:
            aas_id = util.encode_string_in_base64_url(aas_info['id'])
            for submodel_ref_data in aas_info['submodels']:
                # submodel_ref = util.encode_string_in_base64_url(submodel_ref_data['keys'][0]['value'])
                # submodel_json = AASOpenAPITools.send_http_get_request(
                #     AASRepositoryInfo.get_aas_repository_url() + '/submodels/' + submodel_ref)
                submodel_json = AASOpenAPITools.send_http_get_request(
                        AASRepositoryInfo.get_submodel_json_url_by_id(submodel_ref_data['keys'][0]['value']))
                # TODO PENSAR SI RECOGER LAS URLS DE LA CLASE AASRepositoryInfo: es decir, le pasas la referencia y te crea la url
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
            if 'ExternalDescriptor' in data.values():
                print()
            return {
                key: (None if 'modelType' in data.keys() and data['modelType'] == 'File' and value == ""
                      # else "NoneIdShort" if key == 'idShort' and value == ""
                else self.clean_aas_json_information(value))
                # key: self.clean_aas_json_information(value)
                for key, value in data.items()
                if (key not in ['category']) # Add old attributes to be removed
                   and not (key == 'idShort' and value == "") # If idShort is not defined, it is removed
                # if key not in ['category'] # Add old attributes to be removed
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


class AASOpenAPITools:

    COMMON_TIMEOUT = 5

    @staticmethod
    def check_aas_repository_availability(timeout: int = COMMON_TIMEOUT, max_retries: int = 3,
                                          retry_delay: int = 1) -> bool:
        """
        Checks if a server is available by making an HTTP request.

        Args:
            timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            bool: true if it is available, else false
        """
        aas_repository_url = AASRepositoryInfo.get_aas_repository_url()
        # Try to make request with retries
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries} checking AAS Repository at {aas_repository_url}")
                response = requests.head(aas_repository_url, timeout=timeout, allow_redirects=True)

                # Success criteria: <5xx status codes
                if 200 <= response.status_code < 500:
                    print(f"AAS Repository available: {aas_repository_url}")
                    return True
                else:
                    print(f"Non-success status from {aas_repository_url}: {response.status_code}")

            except requests.exceptions.ConnectTimeout:
                print(f"\tERROR: Connection timeout for {aas_repository_url}", file=sys.stderr)

            except requests.exceptions.ConnectionError:
                print(f"\tERROR: Connection error for {aas_repository_url}", file=sys.stderr)

            except Exception as e:
                print(f"\tERROR: Unexpected error checking {aas_repository_url}: {str(e)}", file=sys.stderr)

            # If we're not on the last attempt, wait before retrying
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        # # After the last attempt, the AAS Repository is currently unavailable.
        return False



    # HTTP METHODS
    # ------------
    @staticmethod
    def send_http_get_request(url, headers = None, timeout: int = COMMON_TIMEOUT):
        """
        This method sends an HTTP GET request to the AAS Repository and obtains the response JSON.
        """
        if headers is None:
            headers = AASRepositoryInfo.AAS_OPEN_API_COMMON_HEADERS
        try:
            response = requests.get(url, headers=headers, timeout=timeout)

            # Try to parse JSON content
            try:
                content_json = response.json()
                if 'result' in content_json:
                    return content_json['result']   # In OpenAPI data can be returned in this field
                else:
                    return content_json
            except json.JSONDecodeError:
                print(f"WARNING: Response claimed to be JSON but couldn't be parsed: {response.text[:100]}...")

        except requests.exceptions.ConnectTimeout:
            print("\tERROR: Connection timeout with the AAS Repository", file=sys.stderr)

        except requests.exceptions.ConnectionError:
            print("\tERROR: Connection error with the AAS Repository", file=sys.stderr)

        except Exception as e:
            print(f"\tERROR: Unexpected error with the AAS Repository: {str(e)}", file=sys.stderr)

        return None


class AASModelUtils:

    @staticmethod
    def get_submodel_elements_by_semantic_id(submodel_object_json, semantic_id_external_ref):
        rels_elements = []
        try:
            if isinstance(submodel_object_json, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(submodel_object_json):
                    if isinstance(submodel_element, model.SubmodelElement):
                        if AASModelUtils.check_semantic_id_exist(submodel_element, semantic_id_external_ref):
                            # An ontological AAS element has been found
                            rels_elements.append(submodel_element)
                        if isinstance(submodel_element, basyx.aas.model.Operation):
                            # In case of Operation, OperationVariables need to be analyzed
                            rels_elements.extend(AASModelUtils.get_operation_variables_by_semantic_id(
                                submodel_element, semantic_id_external_ref))
        except Exception as e:
            print("ERROR: It cannot obtain AAS element with ontological semantic identifiers from the submodel.",
                  file=sys.stderr)
            return []
        return rels_elements

    @staticmethod
    def check_semantic_id_exist(submodel_elem_json, semantic_id_reference):
        """
        This method checks if a specific semanticID exists in an AAS meta-model element.

        Args:
            semantic_id_reference (str): semantic identifier.

        Returns:
            bool: result of the check (only True if the semanticID exists).
        """
        if submodel_elem_json.semantic_id is None:
            return False
        for reference in submodel_elem_json.semantic_id.key:
            if reference.value == semantic_id_reference:
                return True
        return False

    @staticmethod
    def get_operation_variables_by_semantic_id(aas_operation_object, semantic_id):
        """
        This method gets all operation variables that have the given semanticID.

        Args:
            aas_operation_object (model.Operation): JSON object of the AAS operation SubmodelElement.
            semantic_id (str):  semantic identifier of the operation variables to find.

        Returns:
            list: all valid operation variables in form of a list of SubmodelElements.
        """
        operation_variables = []
        all_var_sets = [aas_operation_object.input_variable, aas_operation_object.output_variable,
                        aas_operation_object.in_output_variable]
        for var_set in all_var_sets:
            for operation_variable in var_set:
                if AASModelUtils.check_semantic_id_exist(operation_variable, semantic_id):
                # if operation_variable.check_semantic_id_exist(semantic_id):
                    operation_variables.append(operation_variable)
        return operation_variables