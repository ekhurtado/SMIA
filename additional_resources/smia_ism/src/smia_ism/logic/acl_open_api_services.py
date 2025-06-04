import logging

from smia.utilities.aas_related_services_info import AASRelatedServicesInfo

from external_infrastructures.smia_kb_infrastructure import SMIAKBInfrastructure
from utilities.acl_open_api_utils import send_openapi_http_get_request, send_openapi_http_post_request

_logger = logging.getLogger(__name__)

class ACLOpenAPIServices:
    """
    This class implements the logic of all the ACL-OpenAPI services.
    """

    # --------------------------------
    # Infrastructure registry services
    # --------------------------------
    @staticmethod
    def register_smia_instance(id, asset: dict, aasID, status, startedTimeStamp, smiaVersion):
        """
        This method registers the smia instance in the SMIA KB.
        """
        if id is None or asset is None:
            return "ERROR: The SMIA or asset identifier cannot be null."
        smia_kb_instances_url = SMIAKBInfrastructure.get_smia_instances_url()
        # The body JSON is built with the parameters names and values of the method (id, asset...)
        body_json = {arg_name: arg_value for arg_name, arg_value in locals().items()}
        smia_instances_json = send_openapi_http_post_request(smia_kb_instances_url, body=body_json)
        if smia_instances_json is None:
            return "ERROR: Cannot register SMIA instance (SMIA KB has returned null body)."
        return {'status': 'success'}

    # ---------------------------------
    # Infrastructure discovery services
    # ---------------------------------
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
            if smia_instance['asset']['id'] == asset_id:
                return smia_instance['id']
        return "ERROR: SMIA instance for asset identifier [{}] not found.".format(asset_id)

    @staticmethod
    def get_asset_id_by_smia_instance(smia_instance_id):
        if smia_instance_id is None:
            return "ERROR: The SMIA instance identifier cannot be null."
        # First, all the registered SMIA instances are obtained
        smia_kb_smia_instance_url = SMIAKBInfrastructure.get_smia_instance_url(smia_instance_id)
        smia_instance_json = send_openapi_http_get_request(smia_kb_smia_instance_url)
        if smia_instance_json is None:  # TODO Analizar que devuelve cuando no hay instancias o cuando hay error
            return "ERROR: No SMIA instance is registered."
        # Then, the associated SMIA instance is obtained
        return smia_instance_json['asset']['id']

    @staticmethod
    def get_assets_ids_of_capability(capability_iri):
        if capability_iri is None:
            return "ERROR: The capability IRI identifier cannot be null."
        # First, the capability with the given IRI is obtained
        smia_kb_capability_url = SMIAKBInfrastructure.get_assets_of_capability_url(capability_iri)
        assets_json = send_openapi_http_get_request(smia_kb_capability_url)
        if assets_json is None:  # TODO Analizar que devuelve cuando no hay instancias o cuando hay error
            return "ERROR: No SMIA instance is registered."
        assets_ids = [asset_data['id'] for asset_data in assets_json]
        return assets_ids



    ACLOpenAPIServicesMap = {
        # Registry Services
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_SERVICE_REGISTER_SMIA: register_smia_instance,
        # Discovery Services
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_SMIA_BY_ASSET: get_smia_instance_by_asset_id,
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ASSET_BY_SMIA: get_asset_id_by_smia_instance,
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY: get_assets_ids_of_capability,
    }  #: This object maps the service identifiers with its associated execution methods