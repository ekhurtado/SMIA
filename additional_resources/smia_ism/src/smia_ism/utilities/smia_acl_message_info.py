from smia import GeneralUtils
from smia.utilities.fipa_acl_info import ServiceTypes, FIPAACLInfo, ACLSMIAOntologyInfo
from spade.template import Template


class SMIAACLMessageInfo:
    """
    This class contains the information related to FIPA-ACL messages.
    """

    SMIA_ACL_SERVICE_ATTRIBUTE = 'SMIAInfrastructureService'    # TODO PENSAR COMO SERIA
    SMIA_ACL_SERVICE_ONTOLOGY_RESPONSE = 'SMIAInfrastructureSvcResponse'    # TODO PENSAR COMO SERIA

    # Individual templates
    SMIA_ACL_INFRASTRUCTURE_REQUEST_TEMPLATE = GeneralUtils.create_acl_template(
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE)
    SMIA_ACL_INFRASTRUCTURE_QUERY_REF_TEMPLATE = GeneralUtils.create_acl_template(
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_REF, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE)
    SMIA_ACL_INFRASTRUCTURE_QUERY_IF_TEMPLATE = GeneralUtils.create_acl_template(
        FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE)

    # Complex templates
    SMIA_ISM_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE = (
        SMIA_ACL_INFRASTRUCTURE_REQUEST_TEMPLATE | SMIA_ACL_INFRASTRUCTURE_QUERY_REF_TEMPLATE |
        SMIA_ACL_INFRASTRUCTURE_QUERY_IF_TEMPLATE
    )