import connexion
import six

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
    # TODO PROBARLO CON AAS REPOSITORY
    if connexion.request.is_json:
        aas_repository_url = AASRepositoryURL.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def extract_css_from_aas_repository(aas_repository_url=None):  # noqa: E501
    """Extracts the CSS information from the AAS Repository.

    Gets all the AAS data from the AAS Repository API (if the repostiory is also OpenAPI-compliant), and extracts all the CSS information from it. The AASRepositoryURL query parameter can be used to set the URL of the AAS Repository. If it is not set, the URL that the SMIA KB has predefined is taken. # noqa: E501

    :param aas_repository_url: The IP address and port of the AAS Repository (optional).
    :type aas_repository_url: dict | bytes

    :rtype: str
    """
    # TODO PROBARLO CON AAS REPOSITORY
    if connexion.request.is_json:
        aas_repository_url = AASRepositoryURL.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
