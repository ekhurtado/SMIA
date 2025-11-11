from swagger_server import util


def deserialize(body):  # noqa: E501
    """Deserializes a UTF8-BASE64-URL-encoded format necessary to use within the SMIA KB API to a string.

    Serializes a string to the UTF8-BASE64-URL-encoded format necessary to use within the SMIA KB API. The AAS and ontology identifiers need to be added in this format, as they are passed in the path. This method allows to decode a identifier of UTF8-BASE64-URL format in string. # noqa: E501

    :param body: Identifier in string format
    :type body: dict | bytes

    :rtype: None
    """
    body = body.decode('utf-8').translate(str.maketrans('', '', '\'"'))  # Both single (') and double (") quotes are removed
    return util.decode_base64_url_in_string(body)


def serialize(body):  # noqa: E501
    """Serializes a string to the UTF8-BASE64-URL-encoded format necessary to use within the SMIA KB API.

    Serializes a string to the UTF8-BASE64-URL-encoded format necessary to use within the SMIA KB API. The AAS and ontology identifiers need to be added in this format, as they are passed in the path. This method allows to encode a identifier of string format in UTF8-BASE64-URL. # noqa: E501

    :param body: Identifier in string format
    :type body: dict | bytes

    :rtype: None
    """
    body = body.decode('utf-8').translate(str.maketrans('', '', '\'"'))     # Both single (') and double (") quotes are removed
    return util.encode_string_in_base64_url(body)
