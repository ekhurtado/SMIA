import base64
import datetime

import six
import typing

from art import text2art

from swagger_server import type_util


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool, bytearray):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif type_util.is_generic(klass):
        if type_util.is_list(klass):
            return _deserialize_list(data, klass.__args__[0])
        if type_util.is_dict(klass):
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return an original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        if data is not None \
                and instance.attribute_map[attr] in data \
                and isinstance(data, (list, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type)
            for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type)
            for k, v in six.iteritems(data)}


def encode_string_in_base64_url(content_string):
    """
    This method encodes a string in a base64 url format. This is required as the AAS and ontology identifiers need to
    be added in HTTP request paths.
    """
    content_bytes = content_string.encode('utf-8')
    encoded_content = base64.urlsafe_b64encode(content_bytes)
    return encoded_content.decode('utf-8')

def decode_base64_url_in_string(content_base64_url_string):
    """
    This method encodes a string in a base64 url format. This is required as the AAS and ontology identifiers need to
    be added in HTTP request paths.
    """
    content_base64_url_bytes = content_base64_url_string.encode('utf-8')
    decoded_content = base64.urlsafe_b64decode(content_base64_url_bytes)
    return decoded_content.decode('utf-8')


def remove_key_recursive(data, key_to_remove):
    """
    Recursively removes all instances of a specified key from a JSON-like dictionary or list.

    Args:
        data (dict or list): The JSON-like data to process.
        key_to_remove (str): The key to remove from the data.

    Returns:
        dict or list: The cleaned data with the specified key removed.
    """
    if isinstance(data, dict):
        # Create a new dictionary excluding the specified key
        return {
            key: remove_key_recursive(value, key_to_remove)
            for key, value in data.items() if key != key_to_remove
        }
    elif isinstance(data, list):
        # Apply recursively to each item in the list
        return [remove_key_recursive(item, key_to_remove) for item in data]
    else:
        # If it's neither a dict nor a list, just return it
        return data


def print_smia_kb_banner():
    """
    This method prints the SMIA KB banner as a string. The banner has been created with Python 'art' library.
    """
    # The banner for the SMIA is set as string, avoiding installing 'art' library (which has been used to create it)
    # The code to create the banner with the 'art' library is commented
    # smia_name = "SMIA"
    # kb_name = "KB"
    # ascii_art_smia = text2art(smia_name, font="varsity")
    # ascii_art_kb = text2art(kb_name, font="varsity")
    # combined = []
    # smia_lines = ascii_art_smia.split('\n')
    # kb_lines = ascii_art_kb.split('\n')
    # combined.append("-" * 73)
    # for i in range(len(smia_lines)):
    #     combined.append(smia_lines[i] + "   " + "\033[95m" + kb_lines[i] + "\033[0m")
    # combined.append("-" * 73)
    # combined_banner = '\n'.join(combined)
    # print(combined_banner)

    # The string result for the banner of SMIA_KB is the following
    str_banner =   """
-------------------------------------------------------------------------
  ______    ____    ____   _____        _          [95m ___  ____    ______    [0m
.' ____ \  |_   \  /   _| |_   _|      / \         [95m|_  ||_  _|  |_   _ \   [0m
| (___ \_|   |   \/   |     | |       / _ \        [95m  | |_/ /      | |_) |  [0m
 _.____`.    | |\  /| |     | |      / ___ \       [95m  |  __'.      |  __'.  [0m
| \____) |  _| |_\/_| |_   _| |_   _/ /   \ \_     [95m _| |  \ \_   _| |__) | [0m
 \______.' |_____||_____| |_____| |____| |____|    [95m|____||____| |_______/  [0m
                                                   [95m                        [0m
-------------------------------------------------------------------------
                                                                   v0.1.0
-------------------------------------------------------------------------
"""
    print(str_banner)
