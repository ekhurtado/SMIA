import logging
from basyx.aas.model import SubmodelElement, SubmodelElementCollection, ModelReference

from smia.logic import acl_smia_messages_utils, inter_smia_interactions_utils
from smia.utilities.aas_related_services_info import AASRelatedServicesInfo
from smia.utilities.fipa_acl_info import ACLSMIAJSONSchemas, FIPAACLInfo, ACLSMIAOntologyInfo
from smia.utilities.general_utils import DockerUtils

_logger = logging.getLogger(__name__)

# --------------
# AAS UTILITIES
# --------------
async def extract_supervised_assets_data(supervised_assets_list: SubmodelElement):
    """
    This method extracts all the data about the assets to be supervised from the AAS SubmodelElement.

    Args:
        basyx.aas.model.SubmodelElement: SubmodelElementList with all the information about the assets to be
        supervised.

    Returns:
        dict: all the information about the assets to be supervised, in form of a JSON object.
    """
    supervised_assets_json = {}
    for supervised_asset_data_sme in supervised_assets_list:
        if not isinstance(supervised_asset_data_sme, SubmodelElementCollection):
            _logger.warning("SubmodelElement [{}] representing a data collection for an asset to be supervised is "
                            "not a SubmodelElementCollection, skipping it.".format(supervised_asset_data_sme))
            continue
        try:
            replenishment_cap_sme = supervised_asset_data_sme.get_sm_element_by_semantic_id(
                HealthSupervisorSemantics.SEMANTICID_OHS_REPLENISHMENT_CAPABILITY)
            replenishment_skill_sme = supervised_asset_data_sme.get_sm_element_by_semantic_id(
                HealthSupervisorSemantics.SEMANTICID_OHS_REPLENISHMENT_SKILL)
            health_property_sme = supervised_asset_data_sme.get_sm_element_by_semantic_id(
                HealthSupervisorSemantics.SEMANTICID_OHS_HEALTH_ASSET_PROPERTY)
            health_provision_cap_sme = supervised_asset_data_sme.get_sm_element_by_semantic_id(
                HealthSupervisorSemantics.SEMANTICID_OHS_HEALTH_PROVISION_CAPABILITY)
            health_provision_skill_sme = supervised_asset_data_sme.get_sm_element_by_semantic_id(
                HealthSupervisorSemantics.SEMANTICID_OHS_HEALTH_PROVISION_SKILL)

            is_approach_a_valid = (
                    replenishment_cap_sme is not None
                    and replenishment_skill_sme is not None
                    and health_property_sme is not None
            )
            is_approach_b_valid = (
                    replenishment_cap_sme is not None
                    and replenishment_skill_sme is not None
                    and health_provision_cap_sme is not None
                    and health_provision_skill_sme is not None
            )

            if not (is_approach_a_valid or is_approach_b_valid):
                raise Exception()

        except Exception as e:
            _logger.warning("SubmodelElement [{}] representing a data collection for an asset to be supervised does"
                            " not contain all the required information (neither Approach A nor Approach "
                            "B).".format(supervised_asset_data_sme))
            continue

        supervised_assets_json[replenishment_cap_sme.id_short]= {
            'replenishmentSkill': replenishment_skill_sme.id_short if replenishment_skill_sme is not None else None,
            'healthProvisionCapability': health_provision_cap_sme.id_short if health_provision_cap_sme is not None else None,
            'healthProvisionSkill': health_provision_skill_sme.id_short if health_provision_skill_sme is not None else None,
            'healthProperty': health_property_sme.id_short if health_property_sme is not None else None}

    return supervised_assets_json

# -----------------------
# COMMUNICATION UTILITIES
# -----------------------
async def create_discover_acl_msg_to_smia_ism(agent_object, service_id: str, service_params):
    """
    This method creates an SMIACL message that will be sent to SMIA ISM for a discovery infrastructure service.

    Args:
        agent_object (smia.agents.smia_agent.SMIAAgent): SMIA Agent object.
        service_id (str): identifier of the serviceID required in the content of the message.
        service_params: parameters of the service required in the content of the message.

    Returns:
        spade.message.Message: SMIACL discovery message that will be sent to SMIA ISM.
    """
    smia_i_kb_body = await acl_smia_messages_utils.generate_json_from_schema(
        ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
        serviceID=service_id, serviceType=AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY,
        serviceParams=service_params)
    return await inter_smia_interactions_utils.create_acl_smia_message(
        f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
        f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(agent_object.jid)}",
        await acl_smia_messages_utils.create_random_thread(agent_object),
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE,
        protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=smia_i_kb_body)

async def create_aas_service_discover_acl_msg(agent_object, receiver_jid: str, service_id, service_params):
    """
    This method creates an SMIACL message that will be sent to an SMIA instance for a discovery AAS service.

    Args:
        agent_object (smia.agents.smia_agent.SMIAAgent): SMIA Agent object.
        receiver_jid (str): identifier of the SMIA instance that will receive the message.
        service_id (str): identifier of the serviceID required in the content of the message.
        service_params: parameters of the service required in the content of the message.

    Returns:
        spade.message.Message: SMIACL discovery message that will be sent to SMIA ISM.
    """
    aas_service_body = await acl_smia_messages_utils.generate_json_from_schema(
        ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_SERVICE,
        serviceID=service_id,
        serviceType=AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY,
        serviceParams=service_params)
    return await inter_smia_interactions_utils.create_acl_smia_message(
        receiver_jid,
        await acl_smia_messages_utils.create_random_thread(agent_object),
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_REF,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_SERVICE,
        protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=aas_service_body)

async def create_asset_service_acl_msg(agent_object, receiver_jid: str, service_ref: ModelReference,
                                       service_params=None):
    """
    This method creates an SMIACL message that will be sent to an SMIA instance for a discovery AAS service.

    Args:
        agent_object (smia.agents.smia_agent.SMIAAgent): SMIA Agent object.
        receiver_jid (str): identifier of the SMIA instance that will receive the message.
        service_ref (basyx.aas.model.base.ModelReference): ModelReference of the asset service.
        service_params: parameters of the service required in the content of the message.

    Returns:
        spade.message.Message: SMIACL discovery message that will be sent to SMIA ISM.
    """
    asset_service_body = await acl_smia_messages_utils.generate_json_from_schema(
        ACLSMIAJSONSchemas.JSON_SCHEMA_ASSET_AGENT_RELATED_SERVICE, serviceRef=service_ref,
        service_params=service_params)
    return await inter_smia_interactions_utils.create_acl_smia_message(
        receiver_jid, await acl_smia_messages_utils.create_random_thread(agent_object),
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_ASSET_RELATED_SERVICE,
        protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=asset_service_body)

async def create_capability_request_acl_msg(agent_object, receiver_jid: str, capability_iri, skill_iri):
    """
    This method creates an SMIACL message that will be sent to an SMIA instance for a CSS capability execution.

    Args:
        agent_object (smia.agents.smia_agent.SMIAAgent): SMIA Agent object.
        receiver_jid (str): identifier of the SMIA instance that will receive the message.
        capability_iri (str): IRI identifier of the capabilityIRI required in the content of the message.
        skill_iri (str): IRI identifier of the skillIRI required in the content of the message.
    Returns:
        spade.message.Message: SMIACL discovery message that will be sent to SMIA ISM.
    """
    cap_request_body = await acl_smia_messages_utils.generate_json_from_schema(
        ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE, capabilityIRI=capability_iri, skillIRI=skill_iri)
    return await inter_smia_interactions_utils.create_acl_smia_message(
        receiver_jid, await acl_smia_messages_utils.create_random_thread(agent_object),
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE,
        protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=cap_request_body)

# ---------------
# OTHER UTILITIES
# ---------------
def get_acquisition_approach_env_var(behav_obj):
    """
    Gets the specific environment variable for health property acquisition approach (A/B) and returns the associated
    method.

    Args:
        behav_obj: SPADE behaviour of HealthSupervisorBehaviour.

    Returns:
        executable method associated to the specific approach specified (and default approach B if invalid data is
        added in the environment variable).
    """
    value = str(DockerUtils.get_env_var('ACQUISITION_APPROACH'))
    if value == 'A':
        return behav_obj.get_health_property_value_by_aid_semantic_id
    else:
        # Default approach: if it is 'B' or None (if not defined)
        return behav_obj.get_health_property_value_by_capability_request

class HealthSupervisorSemantics:
    """
    This class contains the specific semanticIDs of Operational Health Supervisor extended agent.
    """

    SEMANTICID_OHS_SUPERVISION_INTERVAL = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:SupervisionInterval'
    SEMANTICID_OHS_HEALTH_THRESHOLD = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:HealthThreshold'
    SEMANTICID_OHS_SUPERVISED_ASSETS = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:SupervisedAssets'
    SEMANTICID_OHS_REPLENISHMENT_CAPABILITY = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:ReplenishmentCapability'
    SEMANTICID_OHS_REPLENISHMENT_SKILL = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:ReplenishmentSkill'
    SEMANTICID_OHS_SUPERVISED_ASSET_ID = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:SupervisedAssetID'

    # SemanticID for approach A
    SEMANTICID_OHS_HEALTH_ASSET_PROPERTY = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:HealthAssetProperty'

    # SemanticIDs for approach B
    SEMANTICID_OHS_HEALTH_PROVISION_CAPABILITY = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:HealthProvisionCapability'
    SEMANTICID_OHS_HEALTH_PROVISION_SKILL = 'urn:ehu:gcis:OperationalHealthSupervisor:1:1:HealthProvisionSkill'

