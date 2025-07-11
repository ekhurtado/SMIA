from urllib.parse import urlparse

class AASRepositoryInfrastructureInfo:
    """
        Class to store server connection information with dynamic URL generation.
        """
    # Default values
    _AAS_HOST_IP_ADDRESS = 'http://192.168.186.129'  # TODO DE MOMENTO ESTA LA IP DE LA MAQUINA VIRTUAL. PENSARLO SI AÑADIRLO DE FORMA QUE SEA PARAMETRIZABLE (p.e. con variable de entorno para Docker)
    _AAS_REPOSITORY_PORT = 8081
    _SELF_EXTRACT_CSS_FROM_AAS = False

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
        cls._AAS_REPOSITORY_PORT = parsed.port if parsed.port else (80 if parsed.scheme == "http" else 443)

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

    @classmethod
    def get_self_extract_css(cls):
        return cls._SELF_EXTRACT_CSS_FROM_AAS

    @classmethod
    def set_self_extract_css(cls, value):
        # Validate port is a number and in valid range
        try:
            value_bool = bool(value)
            cls._SELF_EXTRACT_CSS_FROM_AAS = value_bool

        except (ValueError, TypeError):
            raise ValueError(f"ERROR: Port must be a valid boolean, got {value}")

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
        from swagger_server import util     # Local import to avoid circular imports error
        submodel_id_encoded = util.encode_string_in_base64_url(submodel_id)
        return f"{cls._AAS_HOST_IP_ADDRESS}:{cls._AAS_REPOSITORY_PORT}/submodels/{submodel_id_encoded}"


    AAS_OPEN_API_COMMON_HEADERS = {"Accept": "application/json"}
