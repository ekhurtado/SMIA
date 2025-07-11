import base64
import json
import logging

import requests

_logger = logging.getLogger(__name__)

OPEN_API_JSON_HEADERS = {"Accept": "application/json"}

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


# HTTP METHODS
# ------------
def send_openapi_http_get_request(url, headers = None, timeout: int = 5):
    """
    This method sends an HTTP GET request to the AAS Repository and obtains the response JSON.
    """
    if headers is None:
        # If headers are not set, the JSON headers are used
        headers = OPEN_API_JSON_HEADERS
    try:
        response = requests.get(url, headers=headers, timeout=timeout)

        # Try to parse JSON content
        try:
            content_json = response.json()
            if 'result' in content_json:
                return content_json['result']   # In OpenAPI data can be returned in this field
            else:
                return content_json
        except json.JSONDecodeError:
            print(f"WARNING: Response claimed to be JSON but couldn't be parsed: {response.text[:100]}...")

    except requests.exceptions.ConnectTimeout:
        _logger.error("ERROR: Connection timeout with {}".format(url))

    except requests.exceptions.ConnectionError:
        _logger.error("ERROR: Connection error with {}".format(url))

    except Exception as e:
        _logger.error("ERROR: Unexpected error with {}".format(url))

    return None

def send_openapi_http_post_request(url, headers = None, body = None, timeout: int = 5):
    """
    This method sends an HTTP GET request to the AAS Repository and obtains the response JSON.
    """
    if headers is None:
        # If headers are not set, the JSON headers are used
        headers = OPEN_API_JSON_HEADERS
    try:
        if isinstance(body, dict):
            response = requests.post(url, headers=headers, json=body, timeout=timeout)
        else:
            response = requests.post(url, headers=headers, data=body, timeout=timeout)

        # Try to parse JSON content
        try:
            content_json = response.json()
            # In OpenAPI data can be returned in 'result' field
            return content_json['result']  if 'result' in content_json else content_json
        except json.JSONDecodeError:
            print(f"WARNING: Response claimed to be JSON but couldn't be parsed: {response.text[:100]}...")

    except requests.exceptions.ConnectTimeout:
        _logger.error("ERROR: Connection timeout with {}".format(url))

    except requests.exceptions.ConnectionError:
        _logger.error("ERROR: Connection error with {}".format(url))

    except Exception as e:
        _logger.error("ERROR: Unexpected error with {}".format(url))

    return None


def check_and_get_response_error(response):
    """
    This method checks if the response is valid adn extracts the errors message if it is not valid.

    Args:
        response: response object

    Returns:
        str: '' if it is valid and "ERROR..." if it is not.
    """
    if response is None:  # TODO Analizar que devuelve cuando no hay instancias o cuando hay error
        return "ERROR: The response is Null"
    if isinstance(response, dict):
        if 'code' in response and 'message' in response:
            return f"ERROR with code {response['code']}: {response}."
    # TODO Think and analyze more scenarios
    return ''