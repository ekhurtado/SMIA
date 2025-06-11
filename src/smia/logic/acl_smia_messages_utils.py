import ast
import json
import random
import string

from smia.logic.exceptions import RequestDataError
from smia.logic.inter_smia_interactions_utils import check_received_request_data_structure, _logger

# Methods related to agent JIDs
# -----------------------------
async def get_xmpp_server_from_jid(agent_object_jid):
    """
    This method get the XMPP server from the JID of the agent.

    Args:
        agent_object_jid: the JID object of the SMIA SPADE agent.

    Returns:
        str: XMPP server.
    """
    try:
        return str(agent_object_jid.domain)
    except AttributeError:
        pass
    try:
        return str(agent_object_jid).split('@')[1]
    except AttributeError:
        pass
    return None

async def get_agent_id_from_jid(agent_object_jid):
    """
    This method get the identifier of the agent from the JID of the agent.

    Args:
        agent_object_jid: the JID object of the SMIA SPADE agent.

    Returns:
        str: XMPP server.
    """
    try:
        return str(agent_object_jid.localpart)
    except AttributeError:
        pass
    try:
        return str(agent_object_jid).split('@')[0]
    except AttributeError:
        pass
    return None


def get_sender_from_acl_msg(acl_msg):
    """
    This method returns the identifier of an agent from an ACL message, considering the suffixes that can be added
    by the XMPP server.

    Args:
        acl_msg (spade.message.Message): ACL message object.

    Returns:
        str: identifier of the sender of the message.
    """
    if '/' in str(acl_msg.sender):  # XMPP server can add a random string to differentiate the agent JID
        return str(acl_msg.sender).split('/')[0]
    else:
        return str(acl_msg.sender)

# Methods related to thread of the ACL messages
# ---------------------------------------------
async def create_random_thread(agent_object):
    """
    This method creates a value for the thread of a SPADE-ACL message, using the agent identifier and random string.

    Args:
        agent_object (spade.Agent): the SPADE agent object of the SMIA agent.

    Returns:
        str: thread value
    """
    return (f"{await get_agent_id_from_jid(agent_object.jid)}-"
            f"{''.join(random.choices(string.ascii_letters + string.digits, k=5)).lower()}")

# Methods related to body of the ACL messages
# -------------------------------------------
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
            raise ValueError(f"Missing required parameter: {field}")
        if kwargs[field] is None:
            raise ValueError(f"Missing required value for parameter: {field}")
        json_object[field] = kwargs[field]

    # Optional fields
    for field in properties:
        if field not in json_object and field in kwargs and kwargs[field] is not None:
            json_object[field] = kwargs[field]

    # Validate final message
    try:
        await check_received_request_data_structure(json_object, schema)
    except RequestDataError as e:
        _logger.warning('A JSON object cannot be created using the schema. Check the failed code.')
        return None

    return json_object

def get_parsed_body_from_acl_msg(acl_msg):
    """
    This method gets the body of an ACL message and returns parsed.

    Args:
        acl_msg (spade.message.Message): the ACL message object.

    Returns:
        parsed body of the ACL message.
    """
    # Let's try with JSON
    try:

        return json.loads(acl_msg.body)
    except (json.JSONDecodeError, TypeError):
        pass
    # Now let's try Python literal evaluation, to safely evaluate Python literals (list, tuple, int, etc.))
    try:
        return ast.literal_eval(acl_msg.body)
    except (ValueError, SyntaxError):
        pass

    return acl_msg.body

