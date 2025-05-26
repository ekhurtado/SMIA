import logging

from external_infrastructures.smia_kb_infrastructure import SMIAKBInfrastructure
from utilities.acl_open_api_utils import send_openapi_http_get_request

_logger = logging.getLogger(__name__)

class ACLOpenAPIServices:
    """
    This class implements the logic of all the ACL-OpenAPI services.
    """

    @staticmethod
    def get_smia_instance_by_asset_id(asset_id):
        if asset_id is None:
            return "ERROR: The asset identifier cannot be null."
        # First, all the registered SMIA instances are obtained
        smia_kb_instances_url = SMIAKBInfrastructure.get_smia_instances_url()
        smia_instances_json = send_openapi_http_get_request(smia_kb_instances_url)
        if smia_instances_json is None:  # TODO Analizar que devuelve cuando no hay instancias o cuando hay error
            return "ERROR: No SMIA instance is registered."
        # Then, the associated SMIA instance is obtained
        for smia_instance in smia_instances_json:
            if smia_instance['asset']['asset_id'] == asset_id:
                return smia_instance['id']
        return "ERROR: SMIA instance for asset identifier [{}] not found.".format(asset_id)

    @staticmethod
    def get_assets_ids_of_capability(capability_iri):
        if capability_iri is None:
            return "ERROR: The capability IRI identifier cannot be null."
        # First, the capability with the given IRI is obtained
        smia_kb_capability_url = SMIAKBInfrastructure.get_assets_of_capability_url(capability_iri)
        assets_json = send_openapi_http_get_request(smia_kb_capability_url)
        if assets_json is None:  # TODO Analizar que devuelve cuando no hay instancias o cuando hay error
            return "ERROR: No SMIA instance is registered."
        assets_ids = [asset_data['asset_id'] for asset_data in assets_json]
        return assets_ids



    ACLOpenAPIServicesMap = {
        'GetSMIAInstanceByAssetId': get_smia_instance_by_asset_id,
        'GetAssetIDsOfCapability': get_assets_ids_of_capability,
    }  #: This object maps the service identifiers with its associated execution methods