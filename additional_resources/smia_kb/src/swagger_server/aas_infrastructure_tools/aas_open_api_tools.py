import json
import sys
import time

import requests

from swagger_server.aas_infrastructure_tools.aas_repository_infrastructure_info import AASRepositoryInfrastructureInfo


class AASOpenAPITools:

    COMMON_TIMEOUT = 5

    @staticmethod
    def check_aas_repository_availability(timeout: int = COMMON_TIMEOUT, max_retries: int = 3,
                                          retry_delay: int = 1, aas_repository_url=None) -> bool:
        """
        Checks if a server is available by making an HTTP request.

        Args:
            timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            aas_repository_url (str, optional): The URL of the AAS Repository
        Returns:
            bool: true if it is available, else false
        """
        if aas_repository_url is None:
            aas_repository_url = AASRepositoryInfrastructureInfo.get_aas_repository_url()
        # Try to make request with retries
        for attempt in range(max_retries):
            try:
                if attempt != 0:
                    print(f"Attempt {attempt + 1}/{max_retries} checking AAS Repository at {aas_repository_url}")
                response = requests.head(aas_repository_url, timeout=timeout, allow_redirects=True)

                # Success criteria: <5xx status codes
                if 200 <= response.status_code < 500:
                    print(f"AAS Repository available at: {aas_repository_url}")
                    return True
                else:
                    print(f"Non-success status from AAS Repository at {aas_repository_url}: {response.status_code}")

            except requests.exceptions.ConnectTimeout:
                print(f"\tERROR: Connection timeout for AAS Repository at {aas_repository_url}", file=sys.stderr)

            except requests.exceptions.ConnectionError:
                print(f"\tERROR: Connection error for AAS Repository at {aas_repository_url}", file=sys.stderr)

            except Exception as e:
                print(f"\tERROR: Unexpected error checking AAS Repository at {aas_repository_url}: {str(e)}", file=sys.stderr)

            # If we're not on the last attempt, wait before retrying
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        # # After the last attempt, the AAS Repository is currently unavailable.
        return False



    # HTTP METHODS
    # ------------
    @staticmethod
    def send_http_get_request(url, headers = None, timeout: int = COMMON_TIMEOUT):
        """
        This method sends an HTTP GET request to the AAS Repository and obtains the response JSON.
        """
        if headers is None:
            headers = AASRepositoryInfrastructureInfo.AAS_OPEN_API_COMMON_HEADERS
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
            print("\tERROR: Connection timeout with the AAS Repository", file=sys.stderr)

        except requests.exceptions.ConnectionError:
            print("\tERROR: Connection error with the AAS Repository", file=sys.stderr)

        except Exception as e:
            print(f"\tERROR: Unexpected error with the AAS Repository: {str(e)}", file=sys.stderr)

        return None
