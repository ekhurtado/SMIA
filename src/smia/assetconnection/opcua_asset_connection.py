import asyncio
import json
import logging
from urllib.parse import unquote

from asyncua import Client, ua

from smia.assetconnection.asset_connection import AssetConnection
from smia.logic.exceptions import AssetConnectionError
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class OPCUAAssetConnection(AssetConnection):
    """
    This class implements the asset connection for OPC UA protocol. It inherits from the valid official class defined
    by SMIA.
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.CLIENTSERVER

        # Common data
        self.interface_title = None
        self.base = None
        self.endpoint_metadata_elem = None
        self.security_scheme_elem = None

        # Data of the OPC UA session, shared by the requests and the subscription to the observable interaction elements
        self.observable_elements = {}
        self.monitored_nodes = {}
        self.last_values = {}
        self.received_msgs_queue = asyncio.Queue()
        self.opcua_client = None
        self.subscription = None
        self.connected = False
        self.connection_lock = asyncio.Lock()

        # Data of each request
        self.request_node_id = None
        self.request_operation = None
        self.request_value = None

    async def configure_connection_by_aas_model(self, interface_aas_elem):

        # The Interface element need to be checked
        await self.check_interface_element(interface_aas_elem)

        # Let's retrieve the necessary data from the AAS model to configure the OPC UA connection
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        # General information about the connection to the asset is defined in the SMC 'EndpointMetadata'
        self.endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)

        # The endpointMetadata element need to be checked
        await self.check_endpoint_metadata()

        # The base of an OPC UA interface is the endpoint URL of the OPC UA server
        self.base = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        if not self.base.value.strip().startswith('opc.tcp://'):
            raise AssetConnectionError("The base of the OPC UA interface must start with 'opc.tcp://'",
                                       "invalid endpoint metadata", "Invalid OPC UA endpoint URL")

        security_definitions_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        if security_definitions_elem is not None:
            self.security_scheme_elem = security_definitions_elem.value
        # TODO: add OPC UA security (user/password, certificates). For now, no security (nosec_sc)

        # The InteractionMetadata elements also need to be checked
        interaction_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
        for interaction_metadata_type in interaction_metadata_elem:
            # Interaction metadata can be properties, actions or events
            for interaction_element in interaction_metadata_type:
                await self.check_interaction_metadata(interaction_element)
                # The observable interaction elements will be monitored through an OPC UA subscription
                if await self.is_observable(interaction_element):
                    self.observable_elements[interaction_element.id_short] = await self.get_node_id(
                        interaction_element)

        _logger.info("OPC UA connection configured for the endpoint {} ({} observable elements)".format(
            self.base.value, len(self.observable_elements)))

    async def check_asset_connection(self):
        if not self.connected or self.opcua_client is None:
            return False
        try:
            # The state of the server is a standard node that every OPC UA server has
            server_state_node = self.opcua_client.get_node(ua.NodeId(ua.ObjectIds.Server_ServerStatus_State))
            await server_state_node.read_value()
            return True
        except Exception:
            _logger.warning("The OPC UA session with {} has been lost.".format(self.base.value))
            self.connected = False
            return False

    async def connect_with_asset(self):
        # The lock avoids that two simultaneous calls open two different sessions
        async with self.connection_lock:
            if self.connected:
                return
            # If there is an old session, it is closed before opening a new one
            await self.close_opcua_session()
            try:
                if self.base is None or not hasattr(self.base, 'value'):
                    raise AssetConnectionError("Unable to open the OPC UA session due to 'base' data is missing in "
                                               "EndpointMetadata.", "invalid endpoint metadata",
                                               "Invalid AssetInterface ('base' missing in EndpointMetadata)")
                self.opcua_client = Client(url=self.base.value.strip(),
                                           timeout=OPCUAAssetInterfaceSemantics.DEFAULT_TIMEOUT)
                await self.opcua_client.connect()

                if self.observable_elements:
                    # TODO DUDA: Si es observable hay que suscribirse directamente? O quizas es mas optimo realizar la suscripcion solo si se solicita (y ahí comprobar que sea observable)
                    handler = OPCUASubscriptionHandler(self)
                    self.subscription = await self.opcua_client.create_subscription(
                        OPCUAAssetInterfaceSemantics.SUBSCRIPTION_PERIOD, handler)
                    for element_name, node_id in self.observable_elements.items():
                        node = self.opcua_client.get_node(node_id)
                        self.monitored_nodes[node.nodeid] = element_name
                        await self.subscription.subscribe_data_change(node)

                self.connected = True
                _logger.info("OPC UA session opened with {}".format(self.base.value))
            except Exception as e:
                await self.close_opcua_session()
                raise AssetConnectionError("Unable to open the OPC UA session with {}: {}".format(
                    self.base.value, e), "connection error", type(e).__name__)

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        if interaction_metadata is None:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "InteractionMetadata object is None", "invalid method parameter",
                                       "InteractionMetadata object is None")

        # First, the general data of the request are obtained from the AAS
        await self.extract_general_interaction_metadata(interaction_metadata)

        # Then, the data to be sent to the asset (if there is) are added, and the operation is defined
        await self.add_asset_service_data(interaction_metadata, service_input_data)

        # At this point, the OPC UA request can be performed
        opcua_response = await self.send_opcua_request()

        # The response is processed in the same way as in the rest of SMIA asset connections
        return await self.get_response_content(interaction_metadata, opcua_response)

    async def receive_msg_from_asset(self):
        while True:
            # If there are messages already received, they are delivered first
            if not self.received_msgs_queue.empty():
                return self.received_msgs_queue.get_nowait()

            # The session is opened (or reopened) if it is not available
            if not await self.check_asset_connection():
                await self.connect_with_asset()

            try:
                return await asyncio.wait_for(self.received_msgs_queue.get(),
                                              timeout=OPCUAAssetInterfaceSemantics.CONNECTION_CHECK_PERIOD)
            except asyncio.TimeoutError:
                # No message has arrived, so the session is checked again before continuing waiting
                continue

    # -----------------------
    # OPC UA specific methods
    # -----------------------
    async def extract_general_interaction_metadata(self, interaction_metadata):
        """
        This method extracts the general interaction information from the interaction metadata object. Since this is
        an OPC UA Asset Connection, the NodeId of the variable is obtained from the 'href' element.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
        """
        self.request_node_id = await self.get_node_id(interaction_metadata)

    async def add_asset_service_data(self, interaction_metadata, service_input_data):
        """
        This method adds the data of the asset service and defines the OPC UA operation: if a value is received, it
        will be written in the variable; otherwise, the variable will be read.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            service_input_data (dict): dictionary containing the input data of the asset service.
        """
        self.request_value = await self.get_single_input_value(service_input_data)
        if self.request_value is None:
            self.request_operation = OPCUAAssetInterfaceSemantics.OPERATION_READ
        else:
            self.request_operation = OPCUAAssetInterfaceSemantics.OPERATION_WRITE

    async def send_opcua_request(self, node_id=None, operation=None, new_value=None):
        """
        This method sends the required OPC UA request (read or write) to the asset through the single persistent
        session. If the session is not open, it is opened automatically; if it has been lost, it is reopened once
         and the request is retried.

        When called without arguments, the request data previously stored by 'extract_general_interaction_metadata'
        and 'add_asset_service_data' are used. The optional arguments allow concurrent requests without overwriting
        them.

        Args:
            node_id (str, optional): NodeId of the variable. Defaults to the stored request NodeId.
            operation (str, optional): 'read' or 'write'. Defaults to the stored request operation.
            new_value (optional): raw value to be written. Defaults to the stored request value.

        Returns:
            object: the value read from the variable, or the written value.
        """
        if node_id is None:
            node_id = self.request_node_id
        if operation is None:
            operation = self.request_operation
        if new_value is None:
            new_value = self.request_value

        for attempt in (1, 2):
            try:
                if not await self.check_asset_connection():
                    await self.connect_with_asset()
                async with self.connection_lock:
                    node = self.opcua_client.get_node(node_id)

                    if operation == OPCUAAssetInterfaceSemantics.OPERATION_READ:
                        value = await node.read_value()
                        _logger.info("OPC UA read of {} completed: {}".format(node_id, self.value_to_log_text(value)))
                        return value

                    # To write, the exact OPC UA data type of the variable is required (otherwise the server rejects it)
                    variant_type = await node.read_data_type_as_variant_type()
                    value = await self.convert_value_to_variant_type(new_value, variant_type)
                    if isinstance(value, list):
                        # The size of an OPC UA array cannot be changed, so it must match the current one
                        current_value = await node.read_value()
                        if isinstance(current_value, list) and len(current_value) != len(value):
                            raise AssetConnectionError("The array {} has {} elements, but {} were received".format(
                                node_id, len(current_value), len(value)), "invalid asset service request",
                                "Invalid array size")
                    # Siemens OPC UA servers do not accept writes with timestamps
                    await node.write_value(ua.DataValue(Value=ua.Variant(value, variant_type),
                                                        SourceTimestamp=None, ServerTimestamp=None))
                    _logger.info("OPC UA write of {} completed: {}".format(node_id, self.value_to_log_text(value)))
                    return value

            except AssetConnectionError:
                raise
            except (ua.UaStatusCodeError, ConnectionError, OSError, asyncio.TimeoutError) as e:
                session_lost = not await self.check_asset_connection()
                if session_lost:
                    await self.close_opcua_session()
                if attempt == 1 and session_lost:
                    # The session expired while idle: reopen it and retry the request once
                    continue
                if isinstance(e, ua.UaStatusCodeError):
                    raise AssetConnectionError("The OPC UA server rejected the {} of {}: {}".format(
                        operation, node_id, e), "asset service error", type(e).__name__)
                raise AssetConnectionError("Unable to communicate with the OPC UA server {}: {}".format(
                    self.base.value, e), "connection error", type(e).__name__)
            except Exception as e:
                raise AssetConnectionError("Unexpected error during the {} of {}: {}".format(
                    operation, node_id, e), "asset service error", type(e).__name__)

    def save_received_msg(self, node, value):
        """
        This method saves a change notified by the OPC UA subscription as a message for SMIA, together with the
        previous value of the variable (None if it is the first notification).

        Args:
            node (asyncua.Node): node of the variable that has changed.
            value: new value of the variable.
        """
        element_name = self.monitored_nodes.get(node.nodeid)
        previous_value = self.last_values.get(element_name)
        if element_name in self.last_values and previous_value == value:
            # Repeated notification after reopening the session: there is no real change
            return
        self.last_values[element_name] = value
        self.received_msgs_queue.put_nowait({'interaction_element': element_name, 'value': value,
                                             'previous_value': previous_value})

    async def close_opcua_session(self):
        """
        This method closes the subscription and the OPC UA session, ignoring the errors if the session is lost.
        """
        if self.subscription is not None:
            try:
                await self.subscription.delete()
            except Exception:
                pass
        if self.opcua_client is not None:
            try:
                await self.opcua_client.disconnect()
            except Exception:
                pass
        self.subscription = None
        self.opcua_client = None
        self.monitored_nodes = {}
        self.connected = False

    @staticmethod
    def value_to_log_text(value):
        """
        This method returns a short text of a value for the log messages (arrays are summarized).

        Args:
            value: value read or written.

        Returns:
            str: text of the value.
        """
        if isinstance(value, list):
            return "array of {} elements".format(len(value))
        return str(value)

    @staticmethod
    async def get_node_id(interaction_metadata):
        """
        This method obtains the NodeId of the variable of an interaction element from its 'href' element. The format
        defined by the OPC UA Binding for WoT (OPC 10101) is supported ('[opc.tcp://<address>:<port>]/?id=<nodeId>'),
        as well as the NodeId directly.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.

        Returns:
            str: NodeId of the OPC UA variable.
        """
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        href = href_elem.value.strip()
        if '?id=' in href:
            # The NodeId is after '?id=', and it may contain percent-encoded characters (e.g. '%23' for '#')
            href = unquote(href.split('?id=', 1)[1])
        return href

    @staticmethod
    async def is_observable(interaction_metadata):
        """
        This method checks if an interaction element is observable, that is, if its 'observable' element is true.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.

        Returns:
            bool: True if the interaction element is observable.
        """
        observable_elem = interaction_metadata.get_sm_element_by_semantic_id(
            OPCUAAssetInterfaceSemantics.SEMANTICID_INTERFACE_OBSERVABLE)
        if observable_elem is None:
            return False
        return str(observable_elem.value).strip().lower() == 'true'

    @staticmethod
    async def get_single_input_value(service_input_data):
        """
        This method obtains the value to be written from the input data of the asset service. An OPC UA variable only
        accepts one value (that can be an array).

        Args:
            service_input_data: input data of the asset service (usually a dictionary with the skill parameters).

        Returns:
            object: the value to be written, or None if there is no input data.
        """
        if service_input_data is None:
            return None
        if isinstance(service_input_data, dict):
            if len(service_input_data) == 0:
                return None
            if len(service_input_data) > 1:
                raise AssetConnectionError("An OPC UA variable only accepts one value, but {} were received"
                                           "".format(len(service_input_data)), "invalid asset service request",
                                           "Too many input values")
            return next(iter(service_input_data.values()))
        return service_input_data

    @staticmethod
    async def convert_value_to_variant_type(value, variant_type):
        """
        This method converts a value to the Python type required by an OPC UA data type. It is necessary because the
        input data of SMIA usually arrives as text. Arrays can be received as lists or as text in JSON format, and
        each element of an integer array can also be given as a list of bits (see 'convert_array_element').

        Args:
            value: value to be converted.
            variant_type (asyncua.ua.VariantType): OPC UA data type of the variable (of each element, for arrays).

        Returns:
            object: the converted value.
        """
        # Arrays: a list, or a text with the form of a list (e.g. "[1, 2, 3]")
        if isinstance(value, str) and value.strip().startswith('['):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                raise AssetConnectionError("The value {} is not a valid array: {}".format(value, e),
                                           "invalid asset service request", "Invalid array format")
        if isinstance(value, (list, tuple)):
            return [await OPCUAAssetConnection.convert_array_element(element, variant_type) for element in value]

        try:
            if variant_type == ua.VariantType.Boolean:
                if isinstance(value, str):
                    if value.strip().lower() in ('true', '1'):
                        return True
                    if value.strip().lower() in ('false', '0'):
                        return False
                    raise ValueError("'{}' is not a valid boolean value".format(value))
                return bool(value)
            if variant_type in OPCUAAssetInterfaceSemantics.INTEGER_RANGES:
                integer_value = int(value)
                minimum, maximum = OPCUAAssetInterfaceSemantics.INTEGER_RANGES[variant_type]
                if not minimum <= integer_value <= maximum:
                    raise ValueError("it must be between {} and {}".format(minimum, maximum))
                return integer_value
            if variant_type in (ua.VariantType.Float, ua.VariantType.Double):
                return float(value)
            if variant_type == ua.VariantType.String:
                return str(value)
            return value
        except (ValueError, TypeError) as e:
            raise AssetConnectionError("The value {} cannot be converted to the OPC UA type {}: {}".format(
                value, variant_type.name, e), "invalid asset service request", "Invalid value type")

    @staticmethod
    async def convert_array_element(element, variant_type):
        """
        This method converts an element of an array. In integer arrays, an element can also be given as a list of
        bits, starting with the least significant bit (X0). This is useful for Siemens WORD tables in which each
        element is a row of bits (e.g. [0, 1, 0, 0, 1, 1, 1, 0] is the value 114).

        Args:
            element: element of the array (a value, or a list of bits).
            variant_type (asyncua.ua.VariantType): OPC UA data type of the elements of the array.

        Returns:
            object: the converted element.
        """
        if isinstance(element, (list, tuple)):
            if variant_type not in OPCUAAssetInterfaceSemantics.INTEGER_RANGES:
                raise AssetConnectionError("Only the elements of integer arrays can be given as a list of bits, but "
                                           "the array type is {}".format(variant_type.name),
                                           "invalid asset service request", "Invalid array format")
            element = await OPCUAAssetConnection.bits_to_integer(element)
        return await OPCUAAssetConnection.convert_value_to_variant_type(element, variant_type)

    @staticmethod
    async def bits_to_integer(bits):
        """
        This method obtains the integer value of a list of bits, starting with the least significant bit (X0).

        Args:
            bits (list): list of bits (0/1, '0'/'1' or False/True).

        Returns:
            int: integer value of the bits.
        """
        value = 0
        for position, bit in enumerate(bits):
            if isinstance(bit, str):
                bit = bit.strip()
            if bit in (1, '1'):
                value = value + 2 ** position
            elif bit not in (0, '0'):
                raise AssetConnectionError("The value {} in position {} is not a valid bit".format(bit, position),
                                           "invalid asset service request", "Invalid bit value")
        return value


class OPCUASubscriptionHandler:
    """
    This class receives the notifications of the OPC UA subscription and gives them to the asset connection.
    """

    def __init__(self, asset_connection):
        self.asset_connection = asset_connection

    def datachange_notification(self, node, val, data):
        self.asset_connection.save_received_msg(node, val)

    def status_change_notification(self, status):
        # The subscription has been lost (e.g. timeout of the server), so the session must be reopened
        _logger.warning("The OPC UA subscription has changed its status: {}".format(status.Status.name))
        self.asset_connection.connected = False


class OPCUAAssetInterfaceSemantics:
    """
    This class contains the specific semanticIDs and values of OPC UA interfaces.
    """
    # Element of the interaction elements that indicates that they can be monitored (W3C WoT Thing Description)
    SEMANTICID_INTERFACE_OBSERVABLE = 'https://www.w3.org/2019/wot/td#isObservable'

    # Operations supported by this asset connection
    OPERATION_READ = 'read'
    OPERATION_WRITE = 'write'

    # Valid ranges of the OPC UA integer data types
    INTEGER_RANGES = {
        ua.VariantType.SByte: (-128, 127),
        ua.VariantType.Byte: (0, 255),
        ua.VariantType.Int16: (-32768, 32767),
        ua.VariantType.UInt16: (0, 65535),
        ua.VariantType.Int32: (-2147483648, 2147483647),
        ua.VariantType.UInt32: (0, 4294967295),
        ua.VariantType.Int64: (-9223372036854775808, 9223372036854775807),
        ua.VariantType.UInt64: (0, 18446744073709551615),
    }

    # Maximum time (in seconds) to wait for the responses of the OPC UA server
    DEFAULT_TIMEOUT = 10
    # Maximum frequency (in milliseconds) of the notifications of the OPC UA subscription
    SUBSCRIPTION_PERIOD = 200
    # Time (in seconds) between the checks of the monitoring session while waiting for messages
    CONNECTION_CHECK_PERIOD = 5