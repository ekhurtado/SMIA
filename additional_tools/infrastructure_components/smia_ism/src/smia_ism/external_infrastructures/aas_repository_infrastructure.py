from urllib.parse import urlparse

from utilities.acl_open_api_utils import encode_string_in_base64_url

class AASRepositoryInfrastructure:
    """
    Class to store information about the SMIA KB infrastructure.
    """
    # Default values
    _AAS_HOST_IP_ADDRESS = 'http://192.168.186.129'  # TODO DE MOMENTO ESTA LA IP DE LA MAQUINA VIRTUAL. PENSARLO SI AÑADIRLO DE FORMA QUE SEA PARAMETRIZABLE (p.e. con variable de entorno para Docker)
    _AAS_REPOSITORY_PORT = 8081

    AAS_OPEN_API_VERSION = '/api/v3'
    AAS_OPEN_API_COMMON_HEADERS = {"Accept": "application/json"}

    @classmethod
    def get_ip_address(cls):
        return cls._AAS_HOST_IP_ADDRESS

    @classmethod
    def set_ip_address_host(cls, ip_address):
        # Validate and normalize the IP address format
        if ip_address and not ip_address.startswith(('http://', 'https://')):
            ip_address = 'http://' + ip_address
        cls._AAS_HOST_IP_ADDRESS = ip_address

    @classmethod
    def set_ip_address(cls, ip_address):
        # Validate and normalize the IP address format
        if ip_address and not ip_address.startswith(('http://', 'https://')):
            ip_address = 'http://' + ip_address
        parsed = urlparse(ip_address)
        cls._AAS_HOST_IP_ADDRESS = f"{parsed.scheme}://{parsed.hostname}"
        cls._AAS_REPOSITORY_PORT = parsed.port if parsed.port else (8080 if parsed.scheme == "http" else 443)

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

    # -------------------------------------------------
    # Methods to create URLs for the AAS Repository API
    # -------------------------------------------------
    @classmethod
    def get_aas_repository_url(cls):
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}"

    @classmethod
    def get_all_aas_json_url(cls):
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/shells"

    @classmethod
    def get_aas_json_url_by_id(cls, aas_id):
        """
        This method returns the URL to obtain the information of a specific AAS in JSON format. The AAS
        identifier must be added in Base64-URL-encoded.
        """
        aas_id_encoded = encode_string_in_base64_url(aas_id)
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/shells/{aas_id_encoded}"

    @classmethod
    def get_submodel_json_url_by_id(cls, submodel_id):
        """
        This method returns the URL to obtain the information of a specific Submodel in JSON format. The Submodel
        identifier must be added in Base64-URL-encoded.
        """
        submodel_id_encoded = encode_string_in_base64_url(submodel_id)
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/submodels/{submodel_id_encoded}"

    # -------------------------------------------
    # Utils methods related to the AAS Repository
    # -------------------------------------------
    @staticmethod
    def clean_aas_json_information(data):
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
                      else AASRepositoryInfrastructure.clean_aas_json_information(value))
                for key, value in data.items()
                if (key not in ['category'])  # Add old attributes to be removed
                and not (key == 'idShort' and value == "")  # If idShort is not defined, it is removed
            }
        elif isinstance(data, list):
            # Apply recursively to each item in the list
            return [AASRepositoryInfrastructure.clean_aas_json_information(item) for item in data]
        else:
            # If it's neither a dict nor a list, just return it
            return data