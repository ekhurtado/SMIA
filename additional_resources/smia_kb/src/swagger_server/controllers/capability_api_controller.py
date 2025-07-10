import os

import connexion
import owlready2
import six
from owlready2 import get_ontology

import __main__
from swagger_server.controllers import controllers_util
from swagger_server.css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from swagger_server.css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server.models.capability import Capability  # noqa: E501
from swagger_server.models.capability_constraint import CapabilityConstraint  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.skill import Skill  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server import util


all_capabilities = []

def delete_capability_by_id(capability_identifier, api_key=None):  # noqa: E501
    """Deletes a capability related to the SMIA-CSS model.

    Deletes a capability related to the SMIA-CSS model. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: int
    :param api_key: 
    :type api_key: str

    :rtype: None
    """
    if capability_identifier is None:
        return 'ERROR: the identifier cannot be Null. Add some identifier to delete the related Capability.'
    # print('The api key value is {}'.format(api_key))
    ontology = CapabilitySkillOntology.get_instance()
    capability_instance = ontology.get_ontology_instance_by_iri(capability_identifier)
    if capability_instance is None:
        return 'ERROR: the identifier is not valid: it does not exist a Capability with this IRI within the ontology.'
    ontology.delete_ontology_instance(capability_instance)

    for cap in all_capabilities:
        if cap.name == capability_identifier:   # TODO de momento buscaremos por nombre (el id esta como numero)
            all_capabilities.remove(cap)
            return 'Capability with name {} successfully deleted!'.format(capability_identifier)

    return 'do some magic! Capability not found!'


def delete_capability_constraint_by_capability_id(capability_identifier, capability_constraint_identifier, api_key=None):  # noqa: E501
    """Deletes a capability constraint related to the SMIA-CSS model.

    Deletes a capability related to the SMIA-CSS model. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str
    :param capability_constraint_identifier: Pet id to delete
    :type capability_constraint_identifier: int
    :param api_key: 
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'


def get_all_assets_by_capability_id(capability_identifier):  # noqa: E501
    """Returns all assets related to the capability of the SMIA-CSS model.

    Returns all assets related to the capability of the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: List[str]
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    capability_instance = controllers_util.check_and_get_ontology_instance(capability_identifier)
    if isinstance(capability_instance, Error):
        return capability_instance
    else:
        capability_json = Capability.from_ontology_instance_to_json(capability_instance)
        return capability_json['assets']
    # return 'do some magic! I am returning all assets for capability with id {}: asset1, asset2...'.format(capability_identifier)


def get_all_capabilities():  # noqa: E501
    """Returns all capabilities related to the SMIA-CSS model.

    Returns all capabilities related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501


    :rtype: List[Capability]
    """
    capability_instances = (CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI) +
                            CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI) +
                            CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI))

    return [Capability.from_ontology_instance_to_json(onto_instance) for onto_instance in capability_instances]
    # return 'do some magic! I am returning all capability: {}...'.format(all_cap_string)


def get_all_capabilities_constraints_by_capability_id(capability_identifier):  # noqa: E501
    """Returns all capabilities constraints related to the SMIA-CSS model.

    Returns all capabilities constraints related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: List[CapabilityConstraint]
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    capability_instance = controllers_util.check_and_get_ontology_instance(capability_identifier)
    if isinstance(capability_instance, Error):
        return capability_instance
    else:
        capability_json = Capability.from_ontology_instance_to_json(capability_instance)
        return capability_json['isRestrictedBy']


def get_all_capabilities_identifiers():  # noqa: E501
    """Returns all capabilities identifiers related to the SMIA-CSS model.

    Returns all capabilities identifiers related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501


    :rtype: List[CSSidentifier]
    """
    capability_instances = (CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI) +
                            CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
                                CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI) +
                            CapabilitySkillOntology.get_instance().get_ontology_instances_by_class_iri(
                                CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI))

    return [onto_instance.iri for onto_instance in capability_instances]
    # return 'do some magic! I am returning all capability identifiers: capabilityId1,capabilityId2,capabilityId3...'


def get_all_skill_refs_by_capability_id(capability_identifier):  # noqa: E501
    """Returns all references to the skills related to a specific capability of the SMIA KB.

    Returns all references to the skills related to a specific capability of the SMIA KB. Associated skills of capabilities are extracted from the AAS-CSS model and they are available through the Skill API. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: List[CSSidentifier]
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    capability_instance = controllers_util.check_and_get_ontology_instance(capability_identifier)
    if isinstance(capability_instance, Error):
        return capability_instance
    else:
        capability_json = Capability.from_ontology_instance_to_json(capability_instance)
        return capability_json['isRealizedBy']
    # return 'do some magic! The capability identifier is not valid. It does not exist an associated ontological instance.'


def get_capability_by_id(capability_identifier):  # noqa: E501
    """Returns a specific capability related to the SMIA-CSS model.

    Returns a specific capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: Capability
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    capability_instance = controllers_util.check_and_get_ontology_instance(capability_identifier)
    if isinstance(capability_instance, Error):
        return capability_instance
    else:
        return Capability.from_ontology_instance_to_json(capability_instance)


def get_capability_constraint_by_capability_id(capability_identifier, capability_constraint_identifier):  # noqa: E501
    """Returns a specific capability constraint related to the SMIA-CSS model.

    Returns a specific capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str
    :param capability_constraint_identifier: The Capability&#x27;s unique id
    :type capability_constraint_identifier: str

    :rtype: CapabilityConstraint
    """
    # The ontology instance is obtained (if data is invalid, Error object is returned)
    capability_instance = controllers_util.check_and_get_ontology_instance(capability_identifier)
    capability_constraint_instance = controllers_util.check_and_get_ontology_instance(capability_constraint_identifier)
    if isinstance(capability_instance, Error):
        return capability_instance
    elif isinstance(capability_constraint_instance, Error):
        return capability_constraint_instance
    else:
        capability_json = Capability.from_ontology_instance_to_json(capability_instance)
        for constraint_data in capability_json['isRestrictedBy']:
            if constraint_data['iri'] == capability_constraint_instance.iri:
                return constraint_data
        return Error(code='400', message="The specified constraint it is not associated to the specified capability.")


def post_asset_to_capability(body, capability_identifier):  # noqa: E501
    """Add a new asset to a specific Capability of the SMIA KB.

    Add a new asset to a specific Capability of the SMIA KB. # noqa: E501

    :param body: SMIA-CSS Capability asset identifier
    :type body: dict | bytes
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: Capability
    """
    if connexion.request.is_json:
        body = str.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def post_capability(body):  # noqa: E501
    """Add a new Capability to the SMIA KB.

    Add a new Capability to the SMIA KB. # noqa: E501

    :param body: SMIA-CSS Capability object
    :type body: dict | bytes

    :rtype: Capability
    """

    # TODO BORRAR
    print("LO QUE HA LLEGADO a POST Capability !!!!!!!!!!!!!!!!!!")
    print(connexion.request.get_json())

    new_capability = None
    if connexion.request.is_json:
        new_capability = Capability.from_dict(connexion.request.get_json())  # noqa: E501
    # En este punto se ha creado la capacidad a partir de los datos añadidos en el body del mensaje HTTP
    # Ahora se va a crear una nueva instancia ontológica si esta no existe.
    ontology = CapabilitySkillOntology.get_instance()

    cap_ontology_instance = ontology.get_ontology_instance_by_iri(new_capability.iri)
    if cap_ontology_instance is not None:
        # In this case the capability exists, so it only need to update some data
        cap_ontology_instance.name = new_capability.name

        if new_capability.category is not None:
            cap_ontology_instance.set_category(new_capability.category)

        if new_capability.has_lifecycle:
            cap_ontology_instance.data_properties_values_dict['hasLifecycle'] = new_capability.has_lifecycle

        if new_capability.is_realized_by is not None:
            for skill_iri in new_capability.is_realized_by:
                # Hay que asociarle skills a la capacidad
                skill_instance = ontology.get_ontology_instance_by_iri(skill_iri)
                if skill_instance is None:
                    print("The associated Skill with IRI [{}] does not exist. Please, register first and then "
                          "link to the Capability.".format(skill_iri))

                if skill_instance not in cap_ontology_instance.isRealizedBy:
                    cap_ontology_instance.isRealizedBy.append(skill_instance)

        if new_capability.is_restricted_by is not None:
            for new_cap_constraint in new_capability.is_restricted_by:
                new_cap_constraint_instance = ontology.get_ontology_instance_by_iri(new_cap_constraint.iri)
                if new_cap_constraint_instance is None:
                    cap_constraint_ontology_class = ontology.get_ontology_class_by_iri(
                        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
                    new_cap_constraint_instance = ontology.create_ontology_object_instance(cap_constraint_ontology_class,
                                                                                           new_cap_constraint.name)
                new_cap_constraint_instance.iri = new_cap_constraint.iri
                new_cap_constraint_instance.set_condition(new_cap_constraint.has_condition)

                # La nueva CapabilityConstraint se asocia al Capability
                if new_cap_constraint_instance not in cap_ontology_instance.isRestrictedBy:
                    cap_ontology_instance.isRestrictedBy.append(new_cap_constraint_instance)

        if new_capability.assets is not None:
            for asset_info in new_capability.assets:
                if cap_ontology_instance.get_associated_asset_by_id(asset_info.id) is None:
                    cap_ontology_instance.add_associated_asset(asset_info.id, asset_info.kind, asset_info.type)

    else:

        # Se crea la instancia ontologica con los datos añadidos
        capability_ontology_class = ontology.get_ontology_class_by_iri(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
        new_capability_instance = ontology.create_ontology_object_instance(capability_ontology_class, new_capability.name)
        new_capability_instance.iri = new_capability.iri
        new_capability_instance.set_category(new_capability.category)

        if new_capability.has_lifecycle is not None:
            new_capability_instance.data_properties_values_dict['hasLifecycle'] = new_capability.has_lifecycle

        # Se añaden los datos opcionales
        if new_capability.is_realized_by is not None:
            for skill_iri in new_capability.is_realized_by:
                # Hay que asociarle skills a la capacidad
                skill_instance = ontology.get_ontology_instance_by_iri(skill_iri)
                if skill_instance is None:
                    print("The associated Skill with IRI [{}] does not exist. Please, register first and then "
                          "link to the Capability.".format(skill_iri))
                new_capability_instance.isRealizedBy.append(skill_instance)
        if new_capability.is_restricted_by is not None:
            for new_cap_constraint in new_capability.is_restricted_by:
                cap_constraint_ontology_class = ontology.get_ontology_class_by_iri(
                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
                new_cap_constraint_instance = ontology.create_ontology_object_instance(cap_constraint_ontology_class,
                                                                                       new_cap_constraint.name)
                new_cap_constraint_instance.iri = new_cap_constraint.iri
                new_cap_constraint_instance.set_condition(new_cap_constraint.has_condition)

                # La nueva CapabilityConstraint se asocia al Capability
                new_capability_instance.isRestrictedBy.append(new_cap_constraint_instance)

        if new_capability.assets is not None:
            for asset_info in new_capability.assets:
                new_capability_instance.add_associated_asset(asset_info.id, asset_info.kind, asset_info.type)

    ontology.persistent_save_ontology()

    return new_capability   # Se ha especificado en el YAML que devuelve el JSON del objeto Capability


def post_capability_constraint(body, capability_identifier):  # noqa: E501
    """Add a new Capability Constraint to the SMIA KB.

    Add a new Capability Constraint to the SMIA KB. # noqa: E501

    :param body: SMIA-CSS Capability Constraint object
    :type body: dict | bytes
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: Capability
    """
    if connexion.request.is_json:
        body = CapabilityConstraint.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def post_capability_constraint(id, tags, status, capability_identifier):  # noqa: E501
    """Add a new Capability Constraint to the SMIA KB.

    Add a new Capability Constraint to the SMIA KB. # noqa: E501

    :param id: 
    :type id: int
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: Capability
    """
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def post_skill_ref_to_capability(body, capability_identifier):  # noqa: E501
    """Add a new skill reference to a specific capability of the SMIA KB.

    Add a new skill reference to a specific capability of the SMIA KB. # noqa: E501

    :param body: SMIA-CSS identifier of the Skill to be associated to the desired capability.
    :type body: dict | bytes
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: Capability
    """
    if capability_identifier is None or body is None:
        return 'The Capability or Skill identifier cannot be None'
    skill_identifier = bytes.decode(body)  # the body string is the CSS Skill identifier
    capability, skill = None, None
    for onto_class in __main__.ontology.individuals():
        if onto_class.name == capability_identifier:
            capability = onto_class
        if onto_class.name == skill_identifier:
            skill = onto_class
    if capability is None or skill is None:
        return 'The Capability or Skill identifier are not valid. There are not exist ontological instances with these identifiers.'

    # En este punto los dos objetos existen, por lo que se puede asociar la skill a la capacidad
    capability.isRealizedBy.append(skill)
    return 'Skill with identifier {} successfully associated to Capability {}'.format(skill_identifier, capability_identifier)
    # return 'do some magic!'


def put_capability_by_id(body, capability_identifier):  # noqa: E501
    """Updates an existing capability related to the SMIA-CSS model.

    Updates an existing capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param body: SMIA-CSS Capability object
    :type body: dict | bytes
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str

    :rtype: None
    """
    new_capability = None
    if connexion.request.is_json:
        new_capability = Capability.from_dict(connexion.request.get_json())  # noqa: E501

    if capability_identifier is None:
        # TODO PENSAR COMO MOSTRAR LOS ERRORES
        return -1
    for cap in all_capabilities:
        if cap.name == capability_identifier:   # TODO de momento lo hacemos por el nombre, el id podría valer solo como identificador único dentro del SMIA KB
        # if cap.id == capability_identifier:
            print("This is the desired capability.")
            all_capabilities.remove(cap)
            all_capabilities.append(new_capability)
            return 'do some magic! Capability with name {} updated'.format(capability_identifier)

    return 'do some magic! Capability not found'


# def put_capability_by_id(id, name, category, skills, constraints, tags, status, capability_identifier):  # noqa: E501
#     """Updates an existing capability related to the SMIA-CSS model.
#
#     Updates an existing capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501
#
#     :param id:
#     :type id: int
#     :param name:
#     :type name: str
#     :param category:
#     :type category: dict | bytes
#     :param skills:
#     :type skills: list | bytes
#     :param constraints:
#     :type constraints: list | bytes
#     :param tags:
#     :type tags: list | bytes
#     :param status:
#     :type status: str
#     :param capability_identifier: The Capability&#x27;s unique id
#     :type capability_identifier: str
#
#     :rtype: None
#     """
#     if connexion.request.is_json:
#         category = Category.from_dict(connexion.request.get_json())  # noqa: E501
#     if connexion.request.is_json:
#         skills = [Skill.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
#     if connexion.request.is_json:
#         constraints = [CapabilityConstraint.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
#     if connexion.request.is_json:
#         tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
#     return 'do some magic!'


def put_capability_constraint_by_capability_id(body, capability_identifier, capability_constraint_identifier):  # noqa: E501
    """Updates an existing capability related to the SMIA-CSS model.

    Updates an existing capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param body: SMIA-CSS Capability Constraints object
    :type body: dict | bytes
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str
    :param capability_constraint_identifier: The Capability Constraint&#x27;s unique id
    :type capability_constraint_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = CapabilityConstraint.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def put_capability_constraint_by_capability_id(id, tags, status, capability_identifier, capability_constraint_identifier):  # noqa: E501
    """Updates an existing capability related to the SMIA-CSS model.

    Updates an existing capability related to the SMIA-CSS model. Capabilities are extracted from the AAS repository or added by the user through the SMIA KB API. # noqa: E501

    :param id: 
    :type id: int
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str
    :param capability_identifier: The Capability&#x27;s unique id
    :type capability_identifier: str
    :param capability_constraint_identifier: The Capability Constraint&#x27;s unique id
    :type capability_constraint_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
