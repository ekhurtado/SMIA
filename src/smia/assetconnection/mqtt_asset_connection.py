import json
import logging
from urllib.parse import urlparse

import aiomqtt

from smia.logic.exceptions import AssetConnectionError

from smia.utilities.smia_info import AssetInterfacesInfo
from smia.assetconnection.asset_connection import AssetConnection

_logger = logging.getLogger(__name__)


class MQTTAssetConnection(AssetConnection):
    """
    This class implements the asset connection for MQTT protocol. It inherits from the valid official class defined by
    SMIA.
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.PUBSUB

        # Common data
        self.interface_title = None
        self.base = None
        self.endpoint_metadata_elem = None
        self.security_scheme_elem = None

        # Data of each request
        self.broker = None
        self.port = 1883
        self.topic = None
        self.qos = 0
        self.retain = False
        self.control_packet = None
        self.request_body = None

        # TODO analizar si son necesarias mas variables globales


    async def configure_connection_by_aas_model(self, interface_aas_elem):
        # The Interface element is first checked
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
        if content_type_elem is not None:
            self.request_content_type = content_type_elem.value     # TODO check (it is not used)

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

        # We extract the broker and port from the base
        if self.base is not None and self.base.value:
            base_str = self.base.value
            parsed_url = urlparse(self.base.value)
            if not parsed_url.netloc:
                parsed_url = urlparse(f"//{base_str}", scheme='mqtt')   # If 'netloc' is empty, the '//' is missing
            elif not parsed_url.scheme:
                parsed_url = parsed_url._replace(scheme='mqtt')     # If there is no scheme, e.g., '//broker.com:1883'

            self.broker = parsed_url.hostname
            if parsed_url.port:
                self.port = parsed_url.port
            elif parsed_url.scheme == 'mqtts':
                self.port = 8883
            else:
                self.port = 1883

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        if interaction_metadata is None:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "InteractionMetadata object is None", "invalid method parameter",
                                       "InteractionMetadata object is None")

        await self.extract_general_interaction_metadata(interaction_metadata)

        # Then, the data of the skill is added in the required field. To do that, the 'SkillParameterExposedThrough'
        # relationship should be obtained, which indicates where the parameter data should be added
        if service_input_data is not None and len(service_input_data) > 0:
            await self.add_asset_service_data(interaction_metadata, service_input_data)

        # At this point, the MQTT request is performed
        mqtt_response = await self.send_mqtt_request()
        if mqtt_response:
            _logger.assetinfo("MQTT communication successfully completed.")
            return True
        return None


    async def receive_msg_from_asset(self):
        pass


    # ---------------------
    # MQTT specific methods
    # ---------------------
    async def extract_general_interaction_metadata(self, interaction_metadata):
        """
        This method extracts the general interaction information from the interaction metadata object. Since this is an
        MQTT Asset Connection, information about the topic, QoS, retain and control packet is obtained. All information
        is saved in the global variables of the class.

        Args:
             interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
        """
        # The interaction_metada element will be an SMC of the MQTT interface.
        await self.check_interaction_metadata(interaction_metadata)

        # First, the full valid topic of the MQTT request is obtained.
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)

        await self.get_topic(forms_elem)

        # Then, MQTT parameters are obtained
        await self.get_mqtt_parameters(forms_elem)

    async def get_topic(self, forms_elem):
        """
        This method gets the complete request Topic from the forms element within the InteractionMetadata element. The
        information is saved in the global variables of the class.

        Args:
          forms_elem (basyx.aas.model.SubmodelElementCollection): SubmodelElement of forms within InteractionMetadata.
        """
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        if href_elem is not None and href_elem.value:
            parsed_topic = urlparse(href_elem.value)
            path = parsed_topic.path

            if parsed_topic.scheme in ('mqtt', 'mqtts'):
                self.topic = path.lstrip('/')   # We remove the leading space to extract the exact topic
            elif path.startswith('.//'):
                self.topic = f"/{path[3:]}"
            else:
                self.topic = path


    async def get_mqtt_parameters(self, forms_elem):
        """
        This method gets the MQTT specific parameters from the forms element within the InteractionMetadata element.
        The information is saved in the global variables of the class.

        Args:
            forms_elem (basyx.aas.model.SubmodelElementCollection): SubmodelElement of forms within InteractionMetadata.
        """
        retain_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_RETAIN)
        if retain_elem is not None and retain_elem.value is not None:
            self.retain = str(retain_elem.value).lower() in ['true', '1']
        else:
            self.retain = False

        control_packet_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_CONTROL_PACKET)
        if control_packet_elem is not None and control_packet_elem.value is not None:
            self.control_packet = control_packet_elem.value

        qos_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_QOS)
        if qos_elem is not None and qos_elem.value is not None:
            try:
                self.qos = int(qos_elem.value)
            except ValueError:
                self.qos = 0
        else:
            self.qos = 0

    async def add_asset_service_data(self, interaction_metadata, service_input_data):
        """
        This method adds the required data of the asset service, using the skill params information (exposure element
        and skill input data). The information is saved in the global variables of the class.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            service_input_data (dict): dictionary containing the input data of the asset service.
        """
        # TODO revisar si habria que añadir los parametros en el modelo AAS, de momento simplemente se añaden
        #  dependiendo el tipo
        self.request_body = await self.serialize_data_by_content_type(interaction_metadata, service_input_data)

    async def serialize_data_by_content_type(self, interaction_metadata, service_data):
        """
        This method serializes the data for the given InteractionMetadata.

        Args:
            interaction_metadata(basyx.aas.model.SubmodelElementCollection): interactionMetadata Python object.
            service_data (dict): the data to be serialized in JSON format.

        Returns:
            str: service data in the content-type format.
        """
        content_type = await self.get_interaction_metadata_content_type(interaction_metadata)
        if content_type is None or content_type.value is None:
            return json.dumps(service_data)

        match content_type.value:
            case 'application/json':
                return json.dumps(service_data)   # Data should be sent in string format
            case 'text/plain':
                return json.dumps(service_data)
            case 'application/xml':
                pass  # Add the method to convert a JSON into XML
            case _:
                return str(service_data)

    async def send_mqtt_request(self):
        """
        This method sends the required MQTT message to the asset. All the required information is obtained from
        the global variables of the class.

        Returns:
            bool: True if communication succeeded.
        """
        if not self.broker:
            raise AssetConnectionError("MQTT broker is not defined.", "BrokerNotDefined", "Missing Broker")

        if self.topic is None:
            raise AssetConnectionError("MQTT topic is not defined.", "TopicNotDefined", "Missing Topic")

        try:
            async with aiomqtt.Client(hostname=self.broker, port=self.port) as client:
                if self.control_packet in ['publish', None]:
                    payload = self.request_body if self.request_body is not None else ""
                    await client.publish(self.topic, payload=payload, qos=self.qos, retain=self.retain)
                    return True
                else:
                    _logger.warning("Control packet {} is not supported for execute_asset_"
                                    "service.".format(self.control_packet))
                    return False
        except aiomqtt.MqttError as error:
            raise AssetConnectionError("The connection with the asset has raised an MQTT exception.",
                                       error.__class__.__name__, str(error))
        except Exception as e:
            raise AssetConnectionError("The connection with the asset has raised an exception.",
                                       e.__class__.__name__, str(e))

class MQTTAssetInterfaceSemantics:
    """
    This class contains the specific semanticIDs of HTTP interfaces.
    """

    SEMANTICID_MQTT_INTERFACE_RETAIN = 'https://www.w3.org/2019/wot/mqtt#hasRetainFlag'
    SEMANTICID_MQTT_INTERFACE_CONTROL_PACKET = 'https://www.w3.org/2019/wot/mqtt#ControlPacket'
    SEMANTICID_MQTT_INTERFACE_QOS = 'https://www.w3.org/2019/wot/mqtt#hasQoSFlag'