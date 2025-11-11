import connexion

from swagger_server.css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.smia_instance import SMIAinstance  # noqa: E501


def delete_smia_instance_by_id(smia_instance_identifier, api_key=None):  # noqa: E501
    """Deletes a SMIA instance within the SMIA KB.

    Deletes a SMIA instance within the SMIA KB. # noqa: E501

    :param smia_instance_identifier: SMIA instance id to delete
    :type smia_instance_identifier: int
    :param api_key:
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'

def get_all_smia_instances():  # noqa: E501
    """Finds all registered SMIA instances.

    Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing. # noqa: E501


    :rtype: List[SMIAinstance]
    """
    return CapabilitySkillOntology.get_instance().get_smia_instances_list()
    # return 'do some magic! I am returning all SMIA instances: instanceId1,instanceId2, instanceId3...'
    # return 'do some magic!'

def get_all_smia_instances_identifiers():  # noqa: E501
    """Returns all SMIA instances identifiers registered in the SMIA KB.

    Returns all SMIA instances identifiers registered in the SMIA KB. # noqa: E501


    :rtype: List[ReferenceSMIA]
    """
    return [smia_instance.id for smia_instance in CapabilitySkillOntology.get_instance().get_smia_instances_list()]
    # return 'do some magic!'


def get_smia_instance_by_id(smia_instance_identifier):  # noqa: E501
    """Returns a specific SMIA instance registered in the SMIA KB.

    Returns a specific SMIA instance registered in the SMIA KB. # noqa: E501

    :param smia_instance_identifier: The SMIA instance&#x27;s unique id
    :type smia_instance_identifier: str

    :rtype: SMIAinstance
    """
    if smia_instance_identifier is None:
        return Error(code='400', message="The SMIA identifier cannot be null.")
    registered_smia_instance = CapabilitySkillOntology.get_instance().get_smia_instance_by_id(smia_instance_identifier)
    if registered_smia_instance is None:
        return Error(code='400', message="The SMIA instance with identifier [{}] does not exist.".format(smia_instance_identifier))
    return registered_smia_instance
    # return 'do some magic!'


def post_smia_instance(body):  # noqa: E501
    """Add a new SMIA instance to the SMIA KB.

    Add a new SMIA instance to the SMIA KB. # noqa: E501

    :param body: SMIA instance object
    :type body: dict | bytes

    :rtype: SMIAinstance
    """
    new_smia_instance = None
    if connexion.request.is_json:
        new_smia_instance = SMIAinstance.from_dict(connexion.request.get_json())  # noqa: E501
    CapabilitySkillOntology.get_instance().add_new_smia_instance_to_database(new_smia_instance)
    return new_smia_instance

# def post_smi_ainstance(id, status, created_time_stamp, name, category, photo_urls, tags):  # noqa: E501
#     """Add a new SMIA instance to the SMIA KB.
#
#     Add a new SMIA instance to the SMIA KB. # noqa: E501
#
#     :param id:
#     :type id: str
#     :param status:
#     :type status: str
#     :param created_time_stamp:
#     :type created_time_stamp: int
#     :param name:
#     :type name: str
#     :param category:
#     :type category: dict | bytes
#     :param photo_urls:
#     :type photo_urls: List[str]
#     :param tags:
#     :type tags: list | bytes
#
#     :rtype: SMIAinstance
#     """
#     if connexion.request.is_json:
#         category = Category.from_dict(connexion.request.get_json())  # noqa: E501
#     if connexion.request.is_json:
#         tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
#     return 'do some magic!'


def put_smia_instance_by_id(body, smia_instance_identifier):  # noqa: E501
    """Updates an existing SMIA instance registered in the SMIA KB.

    Updates an existing SMIA instance registered in the SMIA KB. SMIA instances automatically register themselves when deployed. # noqa: E501

    :param body: SMIA instance object
    :type body: dict | bytes
    :param smia_instance_identifier: The SMIA instance&#x27;s unique id
    :type smia_instance_identifier: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = SMIAinstance.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


# def put_smi_ainstance_by_id(id, status, created_time_stamp, name, category, photo_urls, tags, smia_instance_identifier):  # noqa: E501
#     """Updates an existing SMIA instance registered in the SMIA KB.
#
#     Updates an existing SMIA instance registered in the SMIA KB. SMIA instances automatically register themselves when deployed. # noqa: E501
#
#     :param id:
#     :type id: str
#     :param status:
#     :type status: str
#     :param created_time_stamp:
#     :type created_time_stamp: int
#     :param name:
#     :type name: str
#     :param category:
#     :type category: dict | bytes
#     :param photo_urls:
#     :type photo_urls: List[str]
#     :param tags:
#     :type tags: list | bytes
#     :param smia_instance_identifier: The SMIA instance&#x27;s unique id
#     :type smia_instance_identifier: str
#
#     :rtype: None
#     """
#     if connexion.request.is_json:
#         category = Category.from_dict(connexion.request.get_json())  # noqa: E501
#     if connexion.request.is_json:
#         tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
#     return 'do some magic!'

