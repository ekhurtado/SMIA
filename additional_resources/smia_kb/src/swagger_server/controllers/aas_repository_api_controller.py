import connexion
import six

from swagger_server.aas_infrastructure_tools.aas_open_api_tools import AASOpenAPITools
from swagger_server.aas_infrastructure_tools.aas_repository_information import AASRepositoryInformation
from swagger_server.aas_infrastructure_tools.aas_repository_infrastructure_info import AASRepositoryInfrastructureInfo
from swagger_server.models.datatypes import AASRepositoryURL  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server import util


def check_aas_repository(aas_repository_url=None):  # noqa: E501
    """Checks the availability of the AAS Repository.

    Checks the availability of the AAS Repository (if it is running and available). The AASRepositoryURL query parameter can be used to set the URL of the AAS Repository. If it is not set, the URL that the SMIA KB has predefined is taken. # noqa: E501

    :param aas_repository_url: The IP address and port of the AAS Repository (optional).
    :type aas_repository_url: dict | bytes

    :rtype: str
    """
    # If aas_repository_url is None, within check_availability method is taken the predefined URL
    try:
        return AASOpenAPITools.check_aas_repository_availability(aas_repository_url=aas_repository_url)
    except Exception as e:
        return Error(code='400', message=str(e))


def extract_css_from_aas_repository(aas_repository_url=None):  # noqa: E501
    """Extracts the CSS information from the AAS Repository.

    Gets all the AAS data from the AAS Repository API (if the repostiory is also OpenAPI-compliant), and extracts all the CSS information from it. The AASRepositoryURL query parameter can be used to set the URL of the AAS Repository. If it is not set, the URL that the SMIA KB has predefined is taken. # noqa: E501

    :param aas_repository_url: The IP address and port of the AAS Repository (optional).
    :type aas_repository_url: dict | bytes

    :rtype: str
    """
    try:
        predefined_aas_repo_url = None
        if aas_repository_url is not None:
            predefined_aas_repo_url = AASRepositoryInfrastructureInfo.get_aas_repository_url()
            AASRepositoryInfrastructureInfo.set_ip_address(aas_repository_url)
        aas = AASRepositoryInformation()
        aas.extract_css_information_from_aas_repository()
        if aas_repository_url is not None:
            # The predefined URL is set again
            AASRepositoryInfrastructureInfo.set_ip_address(predefined_aas_repo_url)
        return "CSS information successfully extracted."
    except Exception as e:
        return Error(code='400', message=str(e))
