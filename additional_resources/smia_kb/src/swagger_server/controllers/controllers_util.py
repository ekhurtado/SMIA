import binascii

from swagger_server.css_smia_ontology.css_smia_ontology import CapabilitySkillOntology
from swagger_server.models import Error
from swagger_server import util


def check_and_get_ontology_instance(instance_iri):
    """
    This method checks a received ontology IRI and gets its associated instance. If data is not valid, it returns Error
     object with the reason.

    Args:
        instance_iri (string): IRI of the ontology instance

    Returns:
        Error: Error object with reason.
    """
    if instance_iri is None:
        return Error(code='400', message="The identifier cannot be Null. Add some identifier to get its associated assets.")
    try:
        instance_iri_decoded = util.decode_base64_url_in_string(instance_iri)
        ontology_instance = CapabilitySkillOntology.get_instance().get_ontology_instance_by_iri(instance_iri_decoded)
        if ontology_instance is None:
            return Error(code='404', message='The identifier is not valid, it does not exist an associated ontological instance.')
        return ontology_instance
    except (UnicodeDecodeError, binascii.Error) as e:
        return Error(code='400', message="The identifier is not in base64-url encoded, it is not valid.")