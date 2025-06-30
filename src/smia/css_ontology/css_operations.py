from smia.css_ontology.css_ontology_utils import CapabilitySkillACLInfo


async def capability_checking(agent_object, received_css_json):
    """
    This method executes the Capability Checking operation. In this step, the capabilities offered by this SMIA are
    matched against the received request. In the future, reallocation logic can be applied to infer the capacity
    request received, or advanced techniques such as auto-discovery can be adopted to discover capacities automatically.

    Args:
        agent_object (smia.agents.SMIAAgent): SMIA agent object.
        received_css_json (dict): received CSS data within the SMIA-ACL body message.

    Returns:
        bool, str: boolean with the result of the checking and, if false, reason of the fail
    """
    # First, the ontology instance of the capability is obtained
    cap_name = received_css_json[CapabilitySkillACLInfo.ATTRIB_CAPABILITY_IRI]
    cap_ontology_instance = await agent_object.css_ontology.get_ontology_instance_by_iri(cap_name)

    # The associated constraints and received values for them are also obtained
    constraint_instance_list = cap_ontology_instance.get_associated_constraint_instances()
    if constraint_instance_list is not None:
        received_constraint_data = received_css_json[CapabilitySkillACLInfo.ATTRIB_CAPABILITY_CONSTRAINTS]

        # At this point, the data received has already been verified, so that the values of the constraints can be
        # checked directly.
        for constraint_instance in constraint_instance_list:
            aas_cap_constraint_elem = await agent_object.aas_model.get_object_by_reference(
                constraint_instance.get_aas_sme_ref())
            result = aas_cap_constraint_elem.check_constraint(received_constraint_data[constraint_instance.iri])
            if not result:
                return False, 'The constraint {} with data {} is not valid'.format(constraint_instance.name,
                                                                                   received_constraint_data[
                                                                                       constraint_instance.iri])
    # If all capability constraint are valid, the checking valid
    # TODO PENSAR MAS VALIDACIONES DURANTE EL CAPABILITY CHECKING
    return True, ''



async def feasibility_checking(agent_object, received_css_json):
    """
    This method executes the Feasibility Checking operation. The objective of this step is to ensure that the necessary
     conditions hold so that it is feasible for the selected resource to perform its task. These conditions can be
     pre-conditions, post-conditions or invariants (hold over the entire duration).

    Args:
        agent_object (smia.agents.SMIAAgent): SMIA agent object.
        received_css_json (dict): received CSS data within the SMIA-ACL body message.

    Returns:
        bool, str: boolean with the result of the checking and, if false, reason of the fail
    """
    # TODO
    pass