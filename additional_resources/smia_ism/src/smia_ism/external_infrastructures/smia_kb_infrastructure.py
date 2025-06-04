from urllib.parse import urlparse

from utilities.acl_open_api_utils import encode_string_in_base64_url


class SMIAKBInfrastructure:
    """
    Class to store information about the SMIA KB infrastructure.
    """
    # Default values
    _SMIA_KB_HOST_IP_ADDRESS = 'http://192.168.186.129'  # TODO DE MOMENTO ESTA LA IP DE LA MAQUINA VIRTUAL. PENSARLO SI AÑADIRLO DE FORMA QUE SEA PARAMETRIZABLE (p.e. con variable de entorno para Docker)
    _SMIA_KB_HOST_PORT = 8090

    SMIA_KB_OPEN_API_VERSION = '/api/v3'
    SMIA_KB_OPEN_API_COMMON_HEADERS = {"Accept": "application/json"}

    @classmethod
    def get_ip_address(cls):
        return cls._SMIA_KB_HOST_IP_ADDRESS

    @classmethod
    def set_ip_address_host(cls, ip_address):
        # Validate and normalize the IP address format
        if ip_address and not ip_address.startswith(('http://', 'https://')):
            ip_address = 'http://' + ip_address
        cls._SMIA_KB_HOST_IP_ADDRESS = ip_address

    @classmethod
    def set_ip_address(cls, ip_address):
        # Validate and normalize the IP address format
        if ip_address and not ip_address.startswith(('http://', 'https://')):
            ip_address = 'http://' + ip_address
        parsed = urlparse(ip_address)
        cls._SMIA_KB_HOST_IP_ADDRESS = f"{parsed.scheme}://{parsed.hostname}"
        cls._SMIA_KB_HOST_PORT = parsed.port if parsed.port else (8080 if parsed.scheme == "http" else 443)

    @classmethod
    def get_port(cls):
        return cls._SMIA_KB_HOST_PORT

    @classmethod
    def set_port(cls, port):
        # Validate port is a number and in valid range
        try:
            port_num = int(port)
            if 1 <= port_num <= 65535:
                cls._SMIA_KB_HOST_PORT = port_num
            else:
                raise ValueError(f"ERROR: Port must be between 1-65535, got {port}")
        except (ValueError, TypeError):
            raise ValueError(f"ERROR: Port must be a valid integer, got {port}")

    # ------------------------------------------------------------
    # Methods to create URLs for the Capability API of the SMIA KB
    # ------------------------------------------------------------
    @classmethod
    def get_capability_url(cls, capability_iri):
        """
        This method returns the URL to obtain the information of a specific Capability within SMIA KB in JSON format.
        The Capability identifier must be added Base64-URL-encoded.
        """
        capability_iri_encoded = encode_string_in_base64_url(capability_iri)
        return (f"{cls._SMIA_KB_HOST_IP_ADDRESS}:{cls._SMIA_KB_HOST_PORT}{cls.SMIA_KB_OPEN_API_VERSION}"
                f"/capabilities/{capability_iri_encoded}")

    @classmethod
    def get_assets_of_capability_url(cls, capability_iri):
        """
        This method returns the URL to obtain the information of a specific Capability within SMIA KB in JSON format.
        The Capability identifier must be added Base64-URL-encoded.
        """
        return f"{cls.get_capability_url(capability_iri)}/assets"

    # ------------------------------------------------------
    # Methods to create URLs for the SMIA API of the SMIA KB
    # ------------------------------------------------------
    @classmethod
    def get_smia_instances_url(cls):
        """
        This method returns the URL to obtain all the registered SMIA instances in the SMIA KB.
        """
        return f"{cls._SMIA_KB_HOST_IP_ADDRESS}:{cls._SMIA_KB_HOST_PORT}{cls.SMIA_KB_OPEN_API_VERSION}/smiaInstances"

    @classmethod
    def get_smia_instance_url(cls, instance_id):
        """
        This method returns the URL to obtain the information of a specific Capability within SMIA KB in JSON format.
        The Capability identifier must be added Base64-URL-encoded.
        """
        return (f"{cls._SMIA_KB_HOST_IP_ADDRESS}:{cls._SMIA_KB_HOST_PORT}{cls.SMIA_KB_OPEN_API_VERSION}"
                f"/smiaInstances/{instance_id}")


    # @classmethod
    # def get_submodel_json_url_by_id(cls, submodel_id):
    #     """
    #     This method returns the URL to obtain the information of a specific Submodel in JSON format. The Submodel
    #     identifier must be added in Base64-URL-encoded.
    #     """
    #     from swagger_server import util  # Local import to avoid circular imports error
    #
    #     return f"{cls._SMIA_KB_HOST_IP_ADDRESS}:{cls._SMIA_KB_HOST_PORT}/submodels/{submodel_id_encoded}"


