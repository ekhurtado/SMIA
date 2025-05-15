# """This module contains all OWL clases in form of Python classes, in order to add required methods to the correct
# execution of SMIA software. This module is associated to the OWL ontology since it is defined inside the file of the
# definition of OWL. When the owlready2 package loads the ontology, it will automatically import this Python module."""
import logging
from itertools import chain

import basyx.aas.model
from owlready2 import Thing, get_ontology, DataPropertyClass, DatatypeClass

from css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from css_smia_ontology.css_smia_ontology import CapabilitySkillOntology

import builtins

css_ontology = CapabilitySkillOntology.get_instance()
css_ontology.initialize_ontology()
base_namespace = css_ontology.get_namespace(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_BASE_NAMESPACE)


class ExtendedThing(Thing):

    # The namespace of the base CSS ontology must be defined
    namespace = base_namespace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Some dictionaries related to the Data Properties are initialized
        self.data_properties_dict = set()
        self.data_properties_types_dict = {}
        self.data_properties_values_dict = {}

        # The reference to the associated AAS model element will be also necessary.
        self.aas_sme_ref = None

    def set_data_property_value(self, data_property_name, data_property_value):
        """
        This method sets the value of a data property associated to the self instance only if the given value is within
         the possible values for this attribute.

        Args:
            data_property_name (str): the name of the data property.
            data_property_value (str): the value of the data property to be stored.
        """
        self.check_valid_data_property_value(data_property_name, data_property_value)
        # If the result of the check is True the execution reaches this point
        self.data_properties_values_dict[data_property_name] = data_property_value

    def get_data_properties_names(self):
        """
        This method gets all names of the data properties associated to the self instance class (obtained during the
        initialization of the class).

        Returns:
            list(str): list with all names of the data properties.
        """
        data_properties_iris = []
        for prop in self.data_properties_dict:
            data_properties_iris.append(prop.name)
        return data_properties_iris

    def get_data_properties_iris(self):
        """
        This method gets all IRIs of the data properties associated to the self instance class (obtained during the
        initialization of the class).

        Returns:
            list(str): list with all IRIs of the data properties.
        """
        data_properties_iris = []
        for prop in self.data_properties_dict:
            data_properties_iris.append(prop.iri)
        return data_properties_iris

    def get_data_property_name_by_iri(self, property_iri):
        """
        This method gets the name of the data property associated to the self instance class (obtained during the
        initialization of the class). It is found by its IRI.

        Args:
            property_iri (str): IRI of the data property to find.

        Returns:
            str: name of the desired data property.
        """
        for prop in self.data_properties_dict:
            if prop.iri == property_iri:
                return prop.name
        print("WARNING: The data property with IRI {} does not exist in class {}".format(property_iri, self))
        return None

    def get_aas_sme_ref(self):
        """
        This method gets the AAS submodel element (SME) related to this instance class.

        Returns:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        return self.aas_sme_ref

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to this instance class.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref

    def check_and_get_related_instance_by_instance_name(self, other_instance_name):
        """
        This method checks if there is some Object Property defined that connects the self instance class with the given
        instance class,i.e., if the instances are related within the ontology. If the relation is valid, it also
        returns the related ThingClass.

        Args:
            other_instance_name (ThingClass): name of the other instance class.

        Returns:
            bool, ThingClass: the result of the check, and if True, the class of the related instance
        """
        for prop in self.get_properties():
            for related_instance in getattr(self, prop.name):
                if other_instance_name == related_instance.name:
                    return True, related_instance
        return False, None


class Capability(ExtendedThing):
    """
    This class represent the OWL class for Capabilities. It contains all necessary methods to ensure the correct
    execution of SMIA software.
    """

    # The associated SubmodelElement class of the AAS is also defined
    # _aas_sme_class = 1
    # aas_sme_class = extended_submodel.ExtendedCapability
    # aas_sme_class = basyx.aas.model.Capability
    # category = None

    def set_category(self, category_value):
        """
        This method sets the category of the capability: AgentCapability or AssetCapability.
        """
        self.category = category_value

    def set_lifecycle(self, lifecycle_value):
        """
        This method sets the lifecycle of the capability: AgentCapability or AssetCapability.
        """
        self.has_lifecycle = lifecycle_value

    def get_associated_skill_instances(self):
        """
        This method gets all associated skill instances and, if there is no skill, returns the None object.

        Returns:
            IndividualValueList: generator with all associated skill instances.
        """
        if len(self.isRealizedBy) == 0:
            return None
        else:
            return self.isRealizedBy

    def get_associated_constraint_instances(self):
        """
        This method gets all associated constraint instances and, if there is no one, returns the None object.

        Returns:
            IndividualValueList: generator with all associated constraint instances.
        """
        if len(self.isRestrictedBy) == 0:
            return None
        else:
            return self.isRestrictedBy

class CapabilityConstraint(ExtendedThing):

    # The associated SubmodelElement class of the AAS is also defined
    # aas_sme_class = None
    # aas_sme_class = basyx.aas.model.SubmodelElement
    # aas_sme_class = extended_submodel.ExtendedCapabilityConstraint

    def set_condition(self, condition_value):
        """
        This method sets the condition of the capability constraint: INVARIANT, POSTCONDITION or PRECONDITION.
        """
        self.has_condition = condition_value


class Skill(ExtendedThing):

    # The associated SubmodelElement class of the AAS is also defined
    # aas_sme_class = None
    # aas_sme_class = extended_submodel.ExtendedSkill

    def get_associated_skill_interface_instances(self):
        """
        This method gets all associated skill interface instances and, if there is no one, returns the None object.

        Returns:
            IndividualValueList: generator with all associated skill interface instances.
        """
        if len(self.accessibleThrough) + len(self.accessibleThroughAgentService) + len(self.accessibleThroughAssetService) == 0:
            return None
        else:
            return chain(self.accessibleThrough, self.accessibleThroughAgentService, self.accessibleThroughAssetService)

    def get_associated_skill_parameter_instances(self):
        """
        This method gets all associated skill parameter instances and, if there is no one, returns the None object.

        Returns:
            IndividualValueList: generator with all associated skill parameter instances.
        """
        if len(self.hasParameter) == 0:
            return None
        else:
            return self.hasParameter


class SkillInterface(ExtendedThing):

    # The associated SubmodelElement class of the AAS is also defined
    # aas_sme_class = None
    # aas_sme_class = extended_submodel.ExtendedSkillInterface

    def check_instance(self):
        """
        This method checks whether the SkillInterface instance is valid: if the required attributes are set and if all
        the added properties are valid. In case of invalid SkillInterface, it raises the exception related to the
        checking error.
        """
        pass
        # TODO pensar mas comprobaciones


class SkillParameter(ExtendedThing):

    def is_skill_parameter_type(self, parameter_type_values):
        """
        This method checks whether the SkillParameter instance has one of the given values for the related DataType.

        Args:
            parameter_type_values: the values to check the SkillParameter instance for.

        Returns:
            bool: True if the SkillParameter instance has one of the given values for the related DataType.
        """
        # First, if only one value is passed, a list is created.
        if not isinstance(parameter_type_values, list):
            parameter_type_values = [parameter_type_values]
        for values in self.data_properties_types_dict.values():
            for value in values:
                if value in parameter_type_values:
                    return True
        return False



class StateMachine(ExtendedThing):
    pass