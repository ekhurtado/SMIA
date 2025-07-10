import json
import logging

from smia.utilities.aas_related_services_info import AASRelatedServicesInfo

from external_infrastructures.aas_repository_infrastructure import AASRepositoryInfrastructure
from external_infrastructures.smia_kb_infrastructure import SMIAKBInfrastructure
from utilities.acl_open_api_utils import send_openapi_http_get_request, send_openapi_http_post_request, \
    check_and_get_response_error

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
        if 'ERROR' in check_and_get_response_error(smia_instances_json):
            return 'Cannot register SMIA instance. {}'.format(check_and_get_response_error(smia_instances_json))
        return {'status': 'success'}

    @staticmethod
    def register_css_elements(capabilities: list[dict], skills: list[dict]):
        """
        This method registers CSS elements (capabilities and skills) in the SMIA KB.
        """
        # First, the skills need to be registered
        if capabilities is None and skills is None:
            return "ERROR: Both the capabilities and skills cannot be null."

        _logger.warning("SKILLS: {}".format(skills))
        _logger.warning("CAPS: {}".format(capabilities))
        if skills is not None and len(skills) > 0:

            smia_kb_skills_url = SMIAKBInfrastructure.get_skills_url()
            for skill_json in skills:
                _logger.warning("SKILL JSON: {}".format(skill_json))
                skill_instance_json = send_openapi_http_post_request(smia_kb_skills_url, body=skill_json)
                if 'ERROR' in check_and_get_response_error(skill_instance_json):
                    return 'Cannot register skill. {}'.format(check_and_get_response_error(skill_instance_json))

        # Then, the capabilities can be registered
        if capabilities is not None and len(capabilities) > 0:
            smia_kb_capabilities_url = SMIAKBInfrastructure.get_capabilities_url()
            for capability_json in capabilities:
                cap_instance_json = send_openapi_http_post_request(smia_kb_capabilities_url, body=capability_json)
                if 'ERROR' in check_and_get_response_error(cap_instance_json):
                    return 'Cannot register capability. {}'.format(check_and_get_response_error(cap_instance_json))

        return {'status': 'success'}

    # ---------------------------------
    # Infrastructure discovery services
    # ---------------------------------
    # SMIA KB services --->
    @staticmethod
    def get_smia_instance_by_asset_id(asset_id):
        if asset_id is None:
            return "ERROR: The asset identifier cannot be null."
        # First, all the registered SMIA instances are obtained
        smia_kb_instances_url = SMIAKBInfrastructure.get_smia_instances_url()
        smia_instances_json = send_openapi_http_get_request(smia_kb_instances_url)
        if 'ERROR' in check_and_get_response_error(smia_instances_json):
            return 'Cannot obtain the SMIA instances. {}'.format(check_and_get_response_error(smia_instances_json))
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
        if 'ERROR' in check_and_get_response_error(smia_instance_json):
            return 'Cannot obtain the assetIDs. {}'.format(check_and_get_response_error(smia_instance_json))
        # Then, the associated SMIA instance is obtained
        return smia_instance_json['asset']['id']

    @staticmethod
    def get_assets_ids_of_capability(capability_iri):
        if capability_iri is None:
            return "ERROR: The capability IRI identifier cannot be null."
        # First, the capability with the given IRI is obtained
        smia_kb_capability_url = SMIAKBInfrastructure.get_assets_of_capability_url(capability_iri)
        assets_json = send_openapi_http_get_request(smia_kb_capability_url)
        if 'ERROR' in check_and_get_response_error(assets_json):
            return 'Cannot obtain the assetIDs. {}'.format(check_and_get_response_error(assets_json))
        assets_ids = [asset_data['id'] for asset_data in assets_json]
        return assets_ids

    # AAS Repository services --->
    @staticmethod
    def get_asset_adminitration_shell_by_id(aas_id):
        """
        This method gets the administration shell from the AAS Repository by its identifier.

        Args:
            aas_id (str): The AAS identifier.

        Returns:
            object: The AAS object from the AAS Repository.
        """
        if aas_id is None:
            return "ERROR: The AAS identifier cannot be null."
        # First, the AAS JSON object need to be obtained
        aas_json = send_openapi_http_get_request(AASRepositoryInfrastructure.get_aas_json_url_by_id(aas_id))
        if 'ERROR' in check_and_get_response_error(aas_json):
            return 'Cannot obtain the AAS. {}'.format(check_and_get_response_error(aas_json))
        aas_complete_json = {'assetAdministrationShells': [aas_json], 'submodels': []}
        # Then, each Submodel JSON related to the AAS need to bje obtained
        for submodel_ref_data in aas_json['submodels']:
            submodel_json = send_openapi_http_get_request(AASRepositoryInfrastructure.get_submodel_json_url_by_id(
                submodel_ref_data['keys'][0]['value']))
            aas_complete_json['submodels'].append(submodel_json)
        # Finally, the data will be cleaned to comply with the latest version of the AAS meta-model so that BaSyx SDK
        # does not present errors
        return AASRepositoryInfrastructure.clean_aas_json_information(aas_complete_json)



    ACLOpenAPIServicesMap = {
        # Registry Services
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_SERVICE_REGISTER_SMIA: register_smia_instance,
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_CSS_ELEMENTS: register_css_elements,
        # Discovery Services
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_SMIA_BY_ASSET: get_smia_instance_by_asset_id,
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ASSET_BY_SMIA: get_asset_id_by_smia_instance,
        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY: get_assets_ids_of_capability,

        AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_AAS_BY_ID: get_asset_adminitration_shell_by_id,    # TODO AÑADIRLO EN SMIA
        # 'GetAssetAdministrationShellById': get_asset_adminitration_shell_by_id,    # TODO AÑADIRLO EN SMIA
    }  #: This object maps the service identifiers with its associated execution methods