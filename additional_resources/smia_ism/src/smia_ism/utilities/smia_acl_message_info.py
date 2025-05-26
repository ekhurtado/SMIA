from smia.utilities.fipa_acl_info import ServiceTypes
from spade.template import Template


class SMIAACLMessageInfo:
    """
    This class contains the information related to FIPA-ACL messages.
    """

    SMIA_ACL_SERVICE_ATTRIBUTE = 'SMIAInfrastructureService'    # TODO PENSAR COMO SERIA
    SMIA_ACL_SERVICE_ONTOLOGY_RESPONSE = 'SMIAInfrastructureSvcResponse'    # TODO PENSAR COMO SERIA

    SMIA_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE = Template()
    SMIA_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE.metadata = {'Classification': ServiceTypes.AAS_INFRASTRUCTURE_SERVICE}     # TODO PENSAR SI USAR ESTOS METADATOS