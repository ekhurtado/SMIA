import logging

from owlready2 import OneOf

_logger = logging.getLogger(__name__)


class CapabilitySkillOntologyUtils:
    """This class contains all information about the proposal of the ontology based on Capability-Skill model. This
    information groups the required semanticIDs or the qualifiers to analyze AAS models."""

    @staticmethod
    def get_ontology_file_path():
        """
        This method gets the valid file path of the ontology file. The file is obtained from the AASX package or from
        the configuration folder inside the SMIA Archive, depending on the definition in the properties file.

        Returns:
            str: file path to the ontology file.
        """
        # TODO PENSAR SI DEJAR LA POSIBILIDAD DE AÑADIR EL ARCHIVO ONTOLOGICO COMO PARAMETRO (p.e. variable de entorno para Docker)
        # return './css_smia_ontology/CSS-ontology-smia.owl'
        # return './css_smia_ontology/CSS-ontology-smia-without-module.owl'
        return './css_smia_ontology/CSS-SMIA-KB-ontology.owl'

    @staticmethod
    def get_possible_values_of_datatype(datatype):
        """
        This method returns all possible values of an OWL data type. If the data type does not have the equivalent
        'OneOf', so the values do not need to be constrained and validated, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            set: possible values of datatype in form of a list of strings.
        """
        possible_values = set()
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.add(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

    @staticmethod
    def check_and_get_xsd_datatypes(datatype):
        """
        This method checks whether the given OWL data type is one of those defined in XSD and, if true, returns the
        associated data type. If false, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            object: value of datatype defined in XSD (None if it is not found).
        """
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if equivalent == str:
                    return str
            return None

    @staticmethod
    def check_whether_part_of_domain(owl_instance, domain):
        """
        This method checks whether a given instance class is part of a given domain.

        Args:
            owl_instance (ThingClass): instance of the OWL class to be checked.
            domain (CallbackList): list of all classes within the given domain.

        Returns:
            bool: result of the check.
        """
        for domain_class in domain:
            for owl_class in owl_instance.is_a:
                if owl_class == domain_class or domain_class in owl_class.ancestors():
                    return True
        return False

    # Types of Capabilities
    MANUFACTURING_CAPABILITY_TYPE = 'ManufacturingCapability'
    ASSET_CAPABILITY_TYPE = 'AssetCapability'
    AGENT_CAPABILITY_TYPE = 'AgentCapability'
    CAPABILITY_TYPE_POSSIBLE_VALUES = [MANUFACTURING_CAPABILITY_TYPE, ASSET_CAPABILITY_TYPE, AGENT_CAPABILITY_TYPE]

    # Qualifiers for Capabilities
    QUALIFIER_CAPABILITY_TYPE = 'ExpressionSemantic'
    QUALIFIER_CAPABILITY_POSSIBLE_VALUES = ['REQUIREMENT', 'OFFER', 'ASSURANCE']

    # Qualifiers for Skills
    QUALIFIER_SKILL_TYPE = 'SkillImplementationType'
    QUALIFIER_SKILL_POSSIBLE_VALUES = ['STATE', 'TRIGGER', 'OPERATION', 'FUNCTIONBLOCK']

    # Qualifiers for Feasibility Checking
    QUALIFIER_FEASIBILITY_CHECKING_TYPE = 'FeasibilityCheckingCondition'
    QUALIFIER_FEASIBILITY_CHECKING_POSSIBLE_VALUES = ['PRECONDITION', 'INVARIANT', 'POSTCONDITION']

    # IDs for Negotiation AgentCapability
    CONCEPT_DESCRIPTION_ID_NEGOTIATION_CRITERIA = 'urn:ehu:gcis:conceptdescriptions:1:1:negotiationcriteria'


class CapabilitySkillOntologyInfo:
    """
    This class contains information related to the ontology of Capability-Skill: namespaces, OWL file...
    """
    CSS_ONTOLOGY_BASE_NAMESPACE = 'http://www.w3id.org/hsu-aut/css#'
    CSS_ONTOLOGY_SMIA_NAMESPACE = 'http://www.w3id.org/upv-ehu/gcis/css-smia#'

    # SemanticIDs (IRIs) of Capabilities
    CSS_ONTOLOGY_CAPABILITY_IRI = 'http://www.w3id.org/hsu-aut/css#Capability'
    CSS_ONTOLOGY_AGENT_CAPABILITY_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#AgentCapability'
    CSS_ONTOLOGY_ASSET_CAPABILITY_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability'
    CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI = 'http://www.w3id.org/hsu-aut/css#CapabilityConstraint'

    # SemanticIDs (IRIs) of Skills
    CSS_ONTOLOGY_SKILL_IRI = 'http://www.w3id.org/hsu-aut/css#Skill'
    CSS_ONTOLOGY_SKILL_INTERFACE_IRI = 'http://www.w3id.org/hsu-aut/css#SkillInterface'
    CSS_ONTOLOGY_SKILL_PARAMETER_IRI = 'http://www.w3id.org/hsu-aut/css#SkillParameter'
    CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI = 'http://www.w3id.org/hsu-aut/css#StateMachine'

    # SemanticIDs (IRIs) of Object Properties (relationship between classes)
    CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI = 'http://www.w3id.org/hsu-aut/css#isRealizedBy'
    CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI = 'http://www.w3id.org/hsu-aut/css#isRestrictedBy'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI = 'http://www.w3id.org/hsu-aut/css#accessibleThrough'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_ASSET_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#accessibleThroughAssetService'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_AGENT_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#accessibleThroughAgentService'
    CSS_ONTOLOGY_PROP_HASPARAMETER_IRI = 'http://www.w3id.org/hsu-aut/css#hasParameter'
    CSS_ONTOLOGY_PROP_BEHAVIOURSCONFORMSTO_IRI = 'http://www.w3id.org/hsu-aut/css#behaviorConformsTo'

    CSS_ONTOLOGY_THING_CLASSES_IRIS = [CSS_ONTOLOGY_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_AGENT_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_ASSET_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI,
                                       CSS_ONTOLOGY_SKILL_IRI,
                                       CSS_ONTOLOGY_SKILL_INTERFACE_IRI,
                                       CSS_ONTOLOGY_SKILL_PARAMETER_IRI,
                                       CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI,
                                       ]

    CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS = [CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI,
                                           CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_ASSET_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_AGENT_IRI,
                                           CSS_ONTOLOGY_PROP_HASPARAMETER_IRI,
                                           CSS_ONTOLOGY_PROP_BEHAVIOURSCONFORMSTO_IRI
                                           ]

