import connexion

from swagger_server.controllers import controllers_util
from swagger_server.css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from swagger_server.css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.datatypes import ReferenceIRI
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.skill import Skill  # noqa: E501
from swagger_server.models.skill_parameter import SkillParameter  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501


def delete_skill_by_id(skill_identifier, api_key=None):  # noqa: E501
    """Deletes a skill related to the SMIA-CSS model.

    Deletes a skill related to the SMIA-CSS model. # noqa: E501

    :param skill_identifier: Pet id to delete
    :type skill_identifier: int
    :param api_key: 
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'


def delete_skill_parameter_by_skill_id(skill_parameter_identifier, skill_identifier, api_key=None):  # noqa: E501
    """Deletes a skill related to the SMIA-CSS model.

    Deletes a skill related to the SMIA-CSS model. # noqa: E501

    :param skill_parameter_identifier: The Skill parameter&#x27;s unique id
    :type skill_parameter_identifier: str
    :param skill_identifier: Pet id to delete
    :type skill_identifier: int
    :param api_key: 
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'



def get_all_skill_identifiers():  # noqa: E501
    """Returns all skills identifiers related to the SMIA-CSS model.

    Returns all skills identifiers related to the SMIA-CSS model. Skills are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501


    :rtype: List[ReferenceIRI]
    """
    skills_instances = CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)

    return [onto_instance.iri for onto_instance in skills_instances]


def get_all_skill_parameters_by_skill_id(skill_identifier):  # noqa: E501
    """Returns all skill parameters related to a specific SMIA-CSS skill.

    Returns all skill parameters related to the SMIA-CSS model. Skills are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: List[SkillParameter]
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    skill_instance = controllers_util.check_and_get_ontology_instance(skill_identifier)
    if isinstance(skill_instance, Error):
        return skill_instance
    else:
        capability_json = Skill.from_ontology_instance_to_json(skill_instance)
        return capability_json['hasParameter']
    # return 'do some magic!I am returning all skill parameters for skill with id {}: skillparam1, skillparam2...'.format(
    #     skill_identifier)


def get_all_skills():  # noqa: E501
    """Returns all skills related to the SMIA-CSS model.

    Returns all skills related to the SMIA-CSS model. Skills are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501


    :rtype: List[Skill]
    """
    skill_instances = CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)

    return [Skill.from_ontology_instance_to_json(onto_instance) for onto_instance in skill_instances]
    # return 'do some magic!I am returning all skills: skill1, skill2...'


def get_skill_by_id(skill_identifier):  # noqa: E501
    """Returns a specific skill related to the SMIA-CSS model.

    Returns a specific skill related to the SMIA-CSS model. Skills are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: Skill
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    skill_instance = controllers_util.check_and_get_ontology_instance(skill_identifier)
    if isinstance(skill_instance, Error):
        return skill_instance
    else:
        return Skill.from_ontology_instance_to_json(skill_instance)


def get_skill_parameters_by_skill_id(skill_identifier, skill_parameter_identifier):  # noqa: E501
    """Returns a specific skill parameter related to the SMIA-CSS model.

    Returns a specific skill related to the SMIA-CSS model. Skills are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str
    :param skill_parameter_identifier: The Skill parameter&#x27;s unique id
    :type skill_parameter_identifier: str

    :rtype: SkillParameter
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    skill_instance = controllers_util.check_and_get_ontology_instance(skill_identifier)
    skill_parameter_instance = controllers_util.check_and_get_ontology_instance(skill_parameter_identifier)
    if isinstance(skill_instance, Error):
        return skill_instance
    elif isinstance(skill_parameter_instance, Error):
        return skill_parameter_instance
    else:
        capability_json = Skill.from_ontology_instance_to_json(skill_instance)
        for skill_param_data in capability_json['hasParameter']:
            if skill_param_data['iri'] == skill_parameter_instance.iri:
                return skill_param_data
        return Error(code='400', message="The specified constraint it is not associated to the specified capability.")


def post_skill(body):  # noqa: E501
    """Add a new Skill to the SMIA KB.

    Add a new Skill to the SMIA KB. # noqa: E501

    :param body: SMIA-CSS Skill object
    :type body: dict | bytes

    :rtype: Skill
    """
    new_skill = None
    if connexion.request.is_json:
        new_skill = Skill.from_dict(connexion.request.get_json())  # noqa: E501

    ontology = CapabilitySkillOntology.get_instance()

    skill_ontology_instance = ontology.get_ontology_instance_by_iri(new_skill.iri)
    if skill_ontology_instance is not None:
        # In this case the skills exists, so it only need to update some data
        skill_ontology_instance.name = new_skill.name

        if new_skill.has_implementation_type is not None:
            skill_ontology_instance.set_data_property_value('hasImplementationType', new_skill.has_implementation_type)
            # skill_ontology_instance.data_properties_values_dict['hasImplementationType'] = new_skill.has_implementation_type

        if new_skill.accessible_through is not None:
            for skill_interface_iri in new_skill.accessible_through:
                skill_interface_ontology_instance = ontology.get_ontology_instance_by_iri(skill_interface_iri)
                if skill_interface_ontology_instance is None:
                    skill_interface_name = skill_interface_iri.split('#')[1] if '#' in skill_interface_iri else (
                        skill_interface_iri)
                    skill_interface_ontology_instance = ontology.create_ontology_object_instance(
                        ontology.get_ontology_class_by_iri(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI),
                        skill_interface_name)

                # Hay que asociarle skill interface a la skill
                if skill_interface_ontology_instance not in skill_ontology_instance.accessibleThrough:
                    skill_ontology_instance.accessibleThrough.append(skill_interface_ontology_instance)

        if new_skill.has_parameter is not None:
            for new_skill_param in new_skill.has_parameter:
                new_skill_param_instance = ontology.get_ontology_instance_by_iri(new_skill_param.iri)
                if new_skill_param_instance is None:
                    new_skill_param_instance = ontology.create_ontology_object_instance(ontology.get_ontology_class_by_iri(
                        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_PARAMETER_IRI),
                        new_skill_param.name)

                new_skill_param_instance.iri = new_skill_param.iri
                if new_skill_param.has_type is not None:
                    new_skill_param_instance.set_data_property_value('hasType', new_skill_param.has_type)
                    # new_skill_param_instance.data_properties_values_dict['hasType'] = new_skill_param.has_type

                if new_skill_param_instance not in skill_ontology_instance.hasParameter:
                    skill_ontology_instance.hasParameter.append(new_skill_param_instance)

    else:
        # Se crea la instancia ontologica con los datos añadidos
        skill_ontology_class = ontology.get_ontology_class_by_iri(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)
        new_skill_instance = ontology.create_ontology_object_instance(skill_ontology_class,
                                                                           new_skill.name)
        new_skill_instance.iri = new_skill.iri

        if new_skill.has_implementation_type is not None:
            new_skill_instance.set_data_property_value('hasImplementationType', new_skill.has_implementation_type)
            # new_skill_instance.data_properties_values_dict['hasImplementationType'] = new_skill.has_implementation_type

        # Se añaden los datos opcionales
        if new_skill.accessible_through is not None:
            for skill_interface_iri in new_skill.accessible_through:
                skill_interface_ontology_instance = ontology.get_ontology_instance_by_iri(skill_interface_iri)
                if skill_interface_ontology_instance is None:
                    skill_interface_name = skill_interface_iri.split('#')[1] if '#' in skill_interface_iri else (
                        skill_interface_iri)
                    skill_interface_ontology_instance = ontology.create_ontology_object_instance(
                        ontology.get_ontology_class_by_iri(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI),
                        skill_interface_name)

                # Hay que asociarle skill parameters a la skill
                new_skill_instance.accessibleThrough.append(skill_interface_ontology_instance)

        if new_skill.has_parameter is not None:
            for new_skill_param in new_skill.has_parameter:
                new_skill_param_instance = ontology.get_ontology_instance_by_iri(new_skill_param.iri)
                if new_skill_param_instance is None:
                    new_skill_param_instance = ontology.create_ontology_object_instance(ontology.get_ontology_class_by_iri(
                        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_PARAMETER_IRI),
                        new_skill_param.name)

                new_skill_param_instance.iri = new_skill_param.iri
                if new_skill_param.has_type is not None:
                    new_skill_param_instance.set_data_property_value('hasType', new_skill_param.has_type)
                    # new_skill_param_instance.data_properties_values_dict['hasType'] = new_skill_param.has_type


                # La nueva CapabilityConstraint se asocia al Capability
                new_skill_instance.hasParameter.append(new_skill_param_instance)

    ontology.persistent_save_ontology()

    return new_skill  # Se ha especificado en el YAML que devuelve el JSON del objeto Skill


def post_skill_parameter_by_skill_id(body, skill_identifier):  # noqa: E501
    """Add a new Skill to the SMIA KB.

    Add a new Skill to the SMIA KB. # noqa: E501

    :param body: SMIA-CSS Skill object
    :type body: dict | bytes
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: Skill
    """
    if connexion.request.is_json:
        body = Skill.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


def post_skill_parameter_by_skill_id(id, name, category, photo_urls, tags, status, skill_identifier):  # noqa: E501
    """Add a new Skill to the SMIA KB.

    Add a new Skill to the SMIA KB. # noqa: E501

    :param id: 
    :type id: int
    :param name: 
    :type name: dict | bytes
    :param category: 
    :type category: dict | bytes
    :param photo_urls: 
    :type photo_urls: List[str]
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: Skill
    """
    if connexion.request.is_json:
        name = ReferenceIRI.from_dict(connexion.request.get_json())  # noqa: E501
        print(name)
    if connexion.request.is_json:
        category = Category.from_dict(connexion.request.get_json())  # noqa: E501
        print(category)
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        print(tags)
    return 'do some magic!'


def put_skill_by_id(body, skill_identifier):  # noqa: E501
    """Updates an existing skill related to the SMIA-CSS model.

    Updates an existing skill related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param body: SMIA-CSS Skill object
    :type body: dict | bytes
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = Skill.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


def put_skill_by_id(id, name, category, photo_urls, tags, status, skill_identifier):  # noqa: E501
    """Updates an existing skill related to the SMIA-CSS model.

    Updates an existing skill related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param id: 
    :type id: int
    :param name: 
    :type name: dict | bytes
    :param category: 
    :type category: dict | bytes
    :param photo_urls: 
    :type photo_urls: List[str]
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        category = Category.from_dict(connexion.request.get_json())  # noqa: E501
        print(category)
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        print(tags)
    return 'do some magic!'


def put_skill_parameter_by_skill_id(body, skill_identifier, skill_parameter_identifier):  # noqa: E501
    """Updates an existing skill related to the SMIA-CSS model.

    Updates an existing skill related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param body: SMIA-CSS Skill object
    :type body: dict | bytes
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str
    :param skill_parameter_identifier: The Skill parameter&#x27;s unique id
    :type skill_parameter_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = Skill.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


def put_skill_parameter_by_skill_id(id, name, category, photo_urls, tags, status, skill_identifier, skill_parameter_identifier):  # noqa: E501
    """Updates an existing skill related to the SMIA-CSS model.

    Updates an existing skill related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param id: 
    :type id: int
    :param name: 
    :type name: dict | bytes
    :param category: 
    :type category: dict | bytes
    :param photo_urls: 
    :type photo_urls: List[str]
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str
    :param skill_identifier: The Skill&#x27;s unique id
    :type skill_identifier: str
    :param skill_parameter_identifier: The Skill parameter&#x27;s unique id
    :type skill_parameter_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        category = Category.from_dict(connexion.request.get_json())  # noqa: E501
        print(category)
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        print(tags)
    return 'do some magic!'
