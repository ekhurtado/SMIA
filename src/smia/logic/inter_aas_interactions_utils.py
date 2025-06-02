"""This class groups the methods related to the Inter AAS interactions between I4.0 SMIA entities."""
import json
import logging

import jsonschema
from jsonschema.exceptions import ValidationError
from smia.utilities.fipa_acl_info import FIPAACLInfo
from spade.message import Message

from smia.logic.exceptions import RequestDataError
from smia.utilities.smia_info import SMIAInteractionInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


def create_svc_json_data_from_acl_msg(acl_msg):
    """
    This method creates the dictionary with all the required data of a service related to an ACL message.

    Args:
        acl_msg (spade.message.Message): ACL message where to get the information

    Returns:
        dict: dictionary with all the information about the service
    """
    svc_req_data_json = {
        'performative': acl_msg.get_metadata('performative'),
        'ontology': acl_msg.get_metadata('ontology'),
        'thread': acl_msg.thread,
        'sender': GeneralUtils.get_sender_from_acl_msg(acl_msg),
        'receiver': str(acl_msg.to),
    }
    # The body of the ACL message contains the rest of the information
    svc_req_data_json.update(json.loads(acl_msg.body))
    return svc_req_data_json

# Methods related to the ACL-SMIA messages
# ----------------------------------------
def create_inter_smia_response_msg(receiver, thread, performative, ontology, service_id=None, service_type=None,
                                   service_params=None):
    """
    This method creates the Inter AAS interaction response object.

    Args:
        receiver (str): the JID of the receiver of the ACL message from which the service is requested.
        thread (str): the thread of the ACL message.
        performative (str): the performative of the ACL message.
        ontology (str): the ontology of the ACL message.
        service_id (str): the serviceID of the ACL message.
        service_type (str): the serviceType of the ACL message.
        service_params (str): the serviceParams of the "serviceData" section of the ACL message.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """

    request_msg = Message(to=receiver, thread=thread)
    request_msg.set_metadata('performative', performative)
    request_msg.set_metadata('ontology', ontology)
    # request_msg.set_metadata('ontology', 'SvcResponse')

    request_msg_body_json = {
        'serviceID': service_id,
        'serviceType': service_type,
        'serviceData': {
            'serviceCategory': 'service-response',
            'timestamp': GeneralUtils.get_current_timestamp(),
        }
    }
    if service_params is not None:
        request_msg_body_json['serviceData']['serviceParams'] = service_params
    request_msg.body = json.dumps(request_msg_body_json)
    return request_msg

async def create_acl_response_from_received_msg(received_msg, performative, response_body=None):
    """
    This method creates an Inter SMIA interaction response object from a received ACL message. Thus, some of the
    required data will be obtained from the received message (receiver, thread, ontology, protocol, encoding and
    language).

    Args:
        received_msg (spade.message.Message): the received ACL message.
        performative (str): the performative of the ACL message.
        response_body: the body of the ACL response message.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """

    # The response message is built with the data from the received message, adding the desired performative
    response_msg = Message(to=GeneralUtils.get_sender_from_acl_msg(received_msg), thread=received_msg.thread)
    response_msg.set_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB, performative)
    response_msg.set_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB,
                              received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB))
    if received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB) is not None:
        response_msg.set_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB,
                                  received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB))
    if received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB) is not None:
        response_msg.set_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB,
                                  received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB))
    if received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB) is not None:
        response_msg.set_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB,
                                  received_msg.get_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB))

    if response_body is not None:
        if isinstance(response_body, dict):
            response_msg.body = json.dumps(response_body)
        else:
            response_msg.body = str(response_body)
    return response_msg


async def create_acl_smia_message(receiver, thread, performative, ontology, msg_body=None, protocol=None, encoding=None,
                            language=None):
    """
    This method creates a FIPA-ACL-SMIA message for an Inter SMIA interaction. If optional attributes are set, they will
     be added to the message.

    Args:
        receiver (str): the JID of the receiver of the ACL message from which the service is requested.
        thread (str): the thread of the ACL message.
        performative (str): the performative of the ACL message.
        ontology (str): the ontology of the ACL message.
        msg_body: the vody of the ACL message.
        protocol (str): the protocol of the ACL message.
        encoding (str): the encoding of the ACL message.
        language (str): the language of the ACL message.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-SMIA-compliant.
    """

    # The response message is built with the data from the received message, adding the desired performative
    acl_smia_msg = Message(to=receiver, thread=thread)
    acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB, performative)
    acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB, ontology)
    # Optional attributes are added if they are set
    if protocol is not None:
        acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB, protocol)
    if encoding is not None:
        acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB, encoding)
    elif encoding is None:
        acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB, FIPAACLInfo.FIPA_ACL_DEFAULT_ENCODING)
    if language is not None:
        acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB, language)
    elif encoding is None:
        acl_smia_msg.set_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB, FIPAACLInfo.FIPA_ACL_DEFAULT_LANGUAGE)

    if msg_body is not None:
        if isinstance(msg_body, dict):
            acl_smia_msg.body = json.dumps(msg_body)
        else:
            acl_smia_msg.body = str(msg_body)
    return acl_smia_msg

async def acl_message_to_json(acl_message):
    """
    This method converts a FIPA-ACL-SMIA message to JSON object.
    Args:
        acl_message (spade.message.Message): SPADE message object FIPA-ACL-SMIA-compliant.

    Returns:
        dict: JSON object with all the information of the ACL message.
    """
    return {
        'sender': GeneralUtils.get_sender_from_acl_msg(acl_message),
        'receiver': str(acl_message.to),
        'thread': acl_message.thread,
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB: acl_message.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB),
        FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB: acl_message.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB),
        FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB: acl_message.get_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB),
        FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB: acl_message.get_metadata(FIPAACLInfo.FIPA_ACL_ENCODING_ATTRIB),
        FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB: acl_message.get_metadata(FIPAACLInfo.FIPA_ACL_LANGUAGE_ATTRIB),
        'body': json.loads(acl_message.body),
    }

# Methods related to the body of ACL-SMIA messages
# ------------------------------------------------
async def generate_json_from_schema(schema: dict, **kwargs) -> dict:
    """
    This method generates a valid JSON from a predefined JSON Schema.

    Args:
        schema (dict): JSON schema object.
        **kwargs: attributes along with their values to build the JSON.

    Returns:
        dict: valid JSON object regarding the given schema.
    """
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    json_object = {}

    # Mandatory fields
    for field in required_fields:
        if field not in kwargs:
            raise ValueError(f"Missing required field: {field}")
        json_object[field] = kwargs[field]

    # Optional fields
    for field in properties:
        if field not in json_object and field in kwargs:
            json_object[field] = kwargs[field]

    # Validate final message
    try:
        await check_received_request_data_structure(json_object, schema)
    except RequestDataError as e:
        _logger.warning('A JSON object cannot be created using the schema. Check the failed code.')
        return None

    return json_object

async def check_received_request_data_structure_old(received_data, json_schema):
    """
    This method checks if the received data for a request is valid. The JSON object with the specific
    data is also validated against the given associated JSON Schema. In any case, if it is invalid, it raises a
    RequestDataError exception.

    Args:
        received_data (dict): received data in form of a JSON object.
        json_schema (dict): JSON Schema in form of a JSON object.
    """
    # TODO modificarlo cuando se piense la estructura del lenguaje I4.0
    if 'serviceData' not in received_data:
        raise RequestDataError("The received request is invalid due to missing #serviceData field in the"
                               "request message.")
    if 'serviceParams' not in received_data['serviceData']:
        raise RequestDataError("The received request is invalid due to missing #serviceParams field within "
                               "the #serviceData section of the request message.")
    # The received JSON object is also validated against the associated JSON Schema
    try:
        jsonschema.validate(instance=received_data['serviceData']['serviceParams'],
                            schema=json_schema)
    except ValidationError as e:
        raise RequestDataError("The received JSON data within the request message is invalid against the required "
                               "JSON schema. Invalid part: {}. Reason: {}.".format(e.instance, e.message))

async def check_received_request_data_structure(received_data, json_schema):
    """
    This method checks if the received data for a request is valid. So, the JSON object with the specific
    data is validated against the given associated JSON Schema for FIPA-ACL-SMIA messages. In any case, if it is
    invalid, it raises a RequestDataError exception.

    Args:
        received_data (dict): received data in form of a JSON object.
        json_schema (dict): JSON Schema in form of a JSON object.
    """
    # The received JSON object is validated against the associated JSON Schema
    try:
        jsonschema.validate(instance=received_data, schema=json_schema)
    except ValidationError as e:
        raise RequestDataError("The received JSON data within the request message is invalid against the required "
                               "JSON schema. Invalid part: {}. Reason: {}.".format(e.instance, e.message))

# Methods related to SMIA instances interactions
# ----------------------------------------------
async def send_response_msg_from_received(agent_behav, received_msg, performative, response_body=None):
    """
    This method sends a response message from a received one, adding the desired data: performative and body.

    Args:
        agent_behav (AgentBehavior): Agent behaviour object.
        received_msg (spade.message.Message): the received ACL message.
        performative (str): the performative of the ACL message.
        response_body: the body of the ACL response message.
    """
    response_msg = await create_acl_response_from_received_msg(received_msg, performative, response_body)
    await agent_behav.send(response_msg)
