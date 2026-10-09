import asyncio
import json
import logging
from typing import Any, Dict, Optional, Tuple

import aiohttp
from aiohttp import ClientConnectorError, ClientConnectionError, ServerConnectionError
from basyx.aas.model import SubmodelElementCollection
from basyx.aas.util import traversal

from smia.assetconnection.asset_connection import AssetConnection
from smia.logic.exceptions import AssetConnectionError
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)

# Although there is no limit on when the asset can respond, a considerably long timeout is set
DEFAULT_REQUEST_TIMEOUT = total=1000

# Methods that may carry a body. GET/DELETE/HEAD never send it.
METHODS_WITH_BODY = frozenset({'POST', 'PUT', 'PATCH'})


class HTTPAssetConnection(AssetConnection):
    """
    This class implements the asset connection for HTTP protocol. It inherits from the valid official class defined by
    SMIA.

    Coroutine-safe: per-request data (uri, headers, params, method, body) is kept in local variables.
    """

    def __init__(self, request_timeout: Optional[int] = None):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.CLIENTSERVER

        # Configuration data
        self.interface_title = None
        self.base = None
        self.endpoint_metadata_elem = None
        self.security_scheme_elem = None
        self.default_headers: Dict[str, str] = {}
        self.request_timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(request_timeout or DEFAULT_REQUEST_TIMEOUT)

    async def configure_connection_by_aas_model(self, interface_aas_elem):

        # The Interface element need to be checked
        await self.check_interface_element(interface_aas_elem)

        # Let's retrieve the necessary data from the AAS model to configure the HTTP connection
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        # General information about the connection to the asset is defined in the SMC 'EndpointMetadata'
        self.endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)

        # The endpointMetadata element need to be checked
        await self.check_endpoint_metadata()

        self.base = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        content_type_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        if content_type_elem is not None and getattr(content_type_elem, 'value', None):
            self.default_headers['Content-Type'] = content_type_elem.value

        security_definitions_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        if security_definitions_elem is not None:
            self.security_scheme_elem = security_definitions_elem.value
        # TODO: pensar como añadir el resto , p.e. tema de seguridad o autentificacion (bearer).
        #  De momento se ha dejado sin seguridad (nosec_sc)

        # The InteractionMetadata elements also need to be checked
        interaction_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
        for interaction_metadata_type in interaction_metadata_elem:
            # Interaction metadata can be properties, actions or events
            for interaction_element in interaction_metadata_type:
                await self.check_interaction_metadata(interaction_element)

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data = None):
        if interaction_metadata is None:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "InteractionMetadata object is None", "invalid method parameter",
                                       "InteractionMetadata object is None")
        # First, the general data of the request is obtained
        request_uri, request_headers, request_method = await self.extract_general_interaction_metadata(
            interaction_metadata)

        # Then, the specific data of the request is obtained
        request_params: Optional[Dict[str, Any]] = None
        request_body: Any = None
        if service_input_data is not None and len(service_input_data) > 0:
            request_params, request_body = await self.add_asset_service_data(
                interaction_metadata, service_input_data, request_method)

        status, response_text = await self.send_http_request(
            request_uri, request_method, request_headers, request_params, request_body)

        if not 200 <= status < 300:
            _logger.warning("The HTTP request has not been answered correctly. "
                            "Status: %s Response: %s", status, response_text)
            raise AssetConnectionError(
                "The HTTP request has not been answered correctly. Status: {}".format(status),
                "AssetHttpError", response_text)
        _logger.info("HTTP communication successfully completed.")
        return await self.get_response_content(interaction_metadata, response_text)

    async def receive_msg_from_asset(self):
        pass

    # ---------------------
    # HTTP specific methods
    # ---------------------
    async def extract_general_interaction_metadata(self, interaction_metadata) -> Tuple[str, Dict[str, str], str]:
        """
        Extract URI, headers and method name from the interaction metadata.

        Returns:
            tuple: (request_uri, request_headers, request_method). No instance state is modified.
        """
        await self.check_interaction_metadata(interaction_metadata)
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        request_uri = await self.get_complete_request_uri(forms_elem)
        request_headers = await self.get_headers(forms_elem)
        request_method = await self.get_method_name(forms_elem)
        return request_uri, request_headers, request_method

    async def get_complete_request_uri(self, forms_elem) -> str:
        """
        This method builds the complete request URI from the forms element within the InteractionMetadata element.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.

        Returns:
            str: complete request URI.
        """
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        if href_elem is None or not getattr(href_elem, 'value', None):
            raise AssetConnectionError("The InteractionMetadata forms element does not define 'href'.",
                                       'Invalid interface SubmodelElement', 'MissingAttribute')
        href_value = href_elem.value.strip()  # Extract and clean the value (remove leading and trailing spaces)
        if href_value.startswith('http://') or href_value.startswith('https://'):
            return href_value
        if self.base is None or not getattr(self.base, 'value', None):
            raise AssetConnectionError("The HTTP connection has no base URI configured.",
                                       'Invalid connection state', 'MissingBase')
        return self.base.value.strip().rstrip('/') + '/' + href_value.lstrip('/')

    async def get_headers(self, forms_elem) -> Dict[str, str]:
        """
        This method builds the request headers merging the configured default headers with
        the per-interaction headers from the forms element within the InteractionMetadata element.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.

        Returns:
            dict: new headers dict for this request (the configured defaults are never mutated).
        """
        request_headers: Dict[str, str] = dict(self.default_headers)
        headers_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_HEADERS)
        if not headers_elem:
            # This Interaction element does not have headers
            return request_headers
        for header_smc in headers_elem:
            field_name_elem = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_NAME)
            field_value_elem = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_VALUE)
            if field_name_elem is None or field_value_elem is None:
                continue
            request_headers[field_name_elem.value] = field_value_elem.value
        return request_headers

    async def get_method_name(self, forms_elem) -> str:
        """
        This method gets the HTTP method name from the forms element within the InteractionMetadata element.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.

        Returns:
            str: upper-case method name, 'GET' by default if not defined.
        """
        method_name_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_METHOD_NAME)
        if method_name_elem is None or not getattr(method_name_elem, 'value', None):
            return 'GET'
        return str(method_name_elem.value).strip().upper() or 'GET'

    async def add_asset_service_data(self, interaction_metadata, service_input_data,
                                     request_method: str) -> Tuple[Optional[Dict[str, Any]], Any]:
        """
        This method adds the service input data into the query params and/or the body of the request. Both locations
        can be used within the same request (the data added in the params is not repeated in the body).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            service_input_data (dict): dictionary containing the input data of the asset service.
            request_method (str): HTTP method of the request (it determines whether the data can be placed in the body
                    of the message or not).

        Returns:
            tuple: (request_params, request_body). No instance state is modified.
        """
        method = request_method.strip().upper()
        request_params = {}
        for submodel_element in traversal.walk_submodel(interaction_metadata):
            # TODO AQUI QUEDA COMPROBAR QUE EXISTE EL SEMANTICID PARA DETERMINAR DONDE HAY QUE AÑADIR LOS DATOS (hay que
            #  pensar el nombre, pero algo estilo 'InputDataLocation')
            # TODO DE MOMENTO SE DEJA CON SOLO PARAMS DE HTTP
            if submodel_element.check_semantic_id_exist(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAMS):
                if not isinstance(submodel_element, SubmodelElementCollection):
                    # It declares params but it is not a collection, so it cannot contain a paramName element
                    continue
                param_name_elem = submodel_element.get_sm_element_by_semantic_id(
                    HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAM_NAME)
                if param_name_elem is None:
                    continue
                param_name = param_name_elem.value
                if param_name in service_input_data:
                    request_params[param_name] = service_input_data[param_name]
            # TODO PENSAR EN MAS OPCIONES DE AÑADIR LOS PARAMETROS (P.E. EN LA URI)
        # The data that has not been added in any param can be placed in the body of the message, but only if the HTTP
        # method supports it
        remaining_service_data = {param_name: param_value for param_name, param_value in service_input_data.items()
                                  if param_name not in request_params}
        request_body = None
        if remaining_service_data and method in METHODS_WITH_BODY:
            # As it is e.g. a POST configured without params, the data will be placed in the body of the message
            request_body = await self.serialize_data_by_content_type(interaction_metadata, remaining_service_data)
        elif remaining_service_data:
            _logger.warning("The service input data [%s] cannot be added to the HTTP request: the method [%s] does "
                            "not support a body and no params have been defined for it.",
                            ', '.join(remaining_service_data), method)
        if request_params or request_body is not None:
            return request_params or None, request_body
        # In this case, no location has been defined for the input data, so it cannot be added to the request
        # TODO PENSAR MAS CASOS
        raise AssetConnectionError("The interface need input data but there is no location defined for it.",
                                   'Invalid interface SubmodelElement', 'MissingAttribute')

    async def send_http_request(self, request_uri: str, request_method: str,
                                request_headers: Optional[Dict[str, str]] = None,
                                request_params: Optional[Dict[str, Any]] = None,
                                request_body: Any = None) -> Tuple[int, str]:
        """
        This method sends a HTTP request to the asset. A new ClientSession is created per call. All the required
        information is obtained from the local variables.

        Args:
            request_uri (str): complete URI of the request.
            request_method (str): HTTP method ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD').
            request_headers (dict, optional): headers of the request.
            request_params (dict, optional): query parameters of the request.
            request_body (dict, optional): payload of the request. Only used for methods that support a body
                ('POST', 'PUT', 'PATCH'); if it is a dict it is sent as JSON, otherwise it is sent as data.

        Returns:
            tuple: (status, response_text). The body is fully read inside the
                session context, so the caller never touches a closed response.
        """
        method = request_method.strip().upper()
        body_kwargs: Dict[str, Any] = {}
        if request_body is not None and method in METHODS_WITH_BODY:
            if isinstance(request_body, dict):
                body_kwargs['json'] = request_body
            else:
                body_kwargs['data'] = request_body
        async with aiohttp.ClientSession(timeout=self.request_timeout) as session:
            try:
                async with session.request(url=request_uri, method=method,
                                           headers=request_headers,
                                           params=request_params,
                                           **body_kwargs) as resp:
                    status = resp.status
                    text = await resp.text()
                return status, text
            except ClientConnectorError as connection_error:
                raise AssetConnectionError("The request to asset failed, so the asset is not available",
                                           "AssetConnectError", str(connection_error)) from connection_error
            except ClientConnectionError as connection_error:
                reason = str(connection_error)
                args0 = connection_error.args[0] if connection_error.args else None
                if hasattr(args0, 'reason'):
                    reason = str(args0.reason)
                raise AssetConnectionError("The connection with the asset has raised an exception.",
                                           connection_error.__class__.__name__, reason) from connection_error
            except ServerConnectionError as connection_error:
                raise AssetConnectionError("The asset server has raised a connection exception.",
                                           connection_error.__class__.__name__,
                                           str(connection_error)) from connection_error
            except asyncio.TimeoutError as timeout_error:
                raise AssetConnectionError("The request to asset timed out, so the asset is not available.",
                                           "AssetConnectTimeout", "The asset connection timed out"
                                           ) from timeout_error
            except aiohttp.ClientError as client_error:
                raise AssetConnectionError("The HTTP request to the asset has failed.",
                                           client_error.__class__.__name__,
                                           str(client_error)) from client_error

    async def serialize_data_by_content_type(self, interaction_metadata, service_data):
        """
        This method serializes the data for the given InteractionMetadata.

        Args:
            interaction_metadata(basyx.aas.model.SubmodelElementCollection): interactionMetadata Python object.
            service_data (dict): the data to be serialized in JSON format.

        Returns:
            obj: service data in the content-type format.
        """
        content_type_elem = await self.get_interaction_metadata_content_type(interaction_metadata)
        if content_type_elem is None or not getattr(content_type_elem, 'value', None):
            return service_data
        mime_type = str(content_type_elem.value).split(';')[0].strip().lower()
        if mime_type == 'application/json':
            return service_data
        elif mime_type == 'text/plain':
            if isinstance(service_data, str):
                return service_data
            return json.dumps(service_data)
        elif mime_type == 'application/xml':
            _logger.warning("XML serialization is not supported for HTTP asset connection.",
                                       'Unsupported content type', 'application/xml')
            return service_data  # Add the method to convert a JSON into XML
        else:
            return service_data


class HTTPAssetInterfaceSemantics:
    """
    This class contains the specific semanticIDs of HTTP interfaces.
    """

    SEMANTICID_HTTP_INTERFACE_METHOD_NAME = 'https://www.w3.org/2011/http#methodName'
    SEMANTICID_HTTP_INTERFACE_HEADERS = 'https://www.w3.org/2011/http#headers'
    SEMANTICID_HTTP_INTERFACE_FIELD_NAME = 'https://www.w3.org/2011/http#fieldName'
    SEMANTICID_HTTP_INTERFACE_FIELD_VALUE = 'https://www.w3.org/2011/http#fieldValue'

    # Extensions for the submodel "Asset Description Interfaces"
    SEMANTICID_HTTP_INTERFACE_PARAMS = 'https://www.w3.org/2011/http#params'
    SEMANTICID_HTTP_INTERFACE_PARAM_NAME = 'https://www.w3.org/2011/http#paramName'
    SEMANTICID_HTTP_INTERFACE_PARAM_VALUE = 'https://www.w3.org/2011/http#paramValue'
