# """This module contains all OWL clases in form of Python classes, in order to add required methods to the correct
# execution of SMIA software. This module is associated to the OWL ontology since it is defined inside the file of the
# definition of OWL. When the owlready2 package loads the ontology, it will automatically import this Python module."""
import logging
from itertools import chain

from owlready2 import Thing, get_ontology, DataPropertyClass, DatatypeClass

from css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyInfo, CapabilitySkillOntologyUtils

import builtins

css_ontology = get_ontology(CapabilitySkillOntologyUtils.get_ontology_file_path())
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

        # The data properties associated to this instance class are found
        self.seek_associated_data_properties()

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

        # The data is also set as attribute of the instance
        if getattr(self, data_property_name) is not None and isinstance(getattr(self, data_property_name), list):
            if data_property_value not in getattr(self, data_property_name):
                getattr(self, data_property_name).append(data_property_value)
        else:
            setattr(self, data_property_name, data_property_value)

    def set_object_property_value(self, object_property_name, ontological_instance):
        """
        This method sets the value of an object property (a related ontological instances to the self through this property).

        Args:
            object_property_name (str): the name of the object property.
            ontological_instance (css_ontology.Ontology):
        """
        try:
            if ontological_instance not in getattr(self, object_property_name):
                getattr(self, object_property_name).append(ontological_instance)
        except AttributeError as e:
            print("ERROR: The class {} does not have the attribute {}".format(self, object_property_name))

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

    def seek_associated_data_properties(self):
        """
        This method seeks possible limited values for attributes of Capability, in order to validate when the attribute
        value is assigned. The possible values for limited attributes are stored in a global dictionary.
        """
        for prop in css_ontology.properties():
            if isinstance(prop, DataPropertyClass):
                if CapabilitySkillOntologyUtils.check_whether_part_of_domain(self, prop.domain):
                    # First, the data property object is saved
                    self.data_properties_dict.add(prop)
                    # The possible values of the data properties are also stored
                    for range_value in prop.range:
                        if isinstance(range_value, DatatypeClass):
                            possible_values = CapabilitySkillOntologyUtils.get_possible_values_of_datatype(range_value)
                            xsd_value_type = CapabilitySkillOntologyUtils.check_and_get_xsd_datatypes(range_value)
                            if possible_values is not None:
                                self.data_properties_types_dict[prop.name] = possible_values
                            elif xsd_value_type is not None:
                                self.data_properties_types_dict[prop.name] = xsd_value_type
                        else:
                            self.data_properties_types_dict[prop.name] = range_value

    def check_valid_data_property_value(self, data_property_name, data_property_value):
        """
        This method checks if the given value of a given data property is valid, in terms of the type of the data. If
        the data property type is simple, the type will be directly checked, and in case of an enumeration, if the given
        value is within the possible values will be checked.

        Args:
            data_property_name (str): the name of the data property.
            data_property_value (str): the value of the data property to be checked.
        """
        if data_property_name not in self.data_properties_types_dict:
           print("WARNING: The data property {} does not exist in this OWL class ({}).".format(data_property_name,
                                                                                                 self))
        else:
            data_property_type = self.data_properties_types_dict[data_property_name]
            if isinstance(data_property_type, set):
                if data_property_value not in data_property_type:
                    print("ERROR: The data property value {} for the OWL class {} is not within  the valid "
                          "values.".format(data_property_value, self))
            else:
                if not isinstance(data_property_value, data_property_type):
                    print("ERROR: The data property value {} for the OWL class {} is not valid."
                          .format(data_property_value, self))


class Capability(ExtendedThing):
    """
    This class represent the OWL class for Capabilities. It contains all necessary methods to ensure the correct
    execution of SMIA software.
    """
    # namespace = base_namespace

    # The associated SubmodelElement class of the AAS is also defined
    # _aas_sme_class = 1
    # aas_sme_class = extended_submodel.ExtendedCapability
    # aas_sme_class = basyx.aas.model.Capability
    # category = None

    # associated_assets = set()  # The associated assets are also saved in the SMIA KB

    def add_associated_asset(self, asset_id):
        if not hasattr(self, 'associated_assets'):
            self.associated_assets = set()
        self.associated_assets.add(asset_id)


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
        This method gets all associated assets, if there is no one, returns the None object.

        Returns:
            Set: list with all associated assets.
        """
        if len(self.isRestrictedBy) == 0:
            return None
        else:
            return self.isRestrictedBy

    def get_associated_assets(self):
        """
        This method gets all associated skill instances and, if there is no skill, returns the None object.

        Returns:
            IndividualValueList: generator with all associated skill instances.
        """
        if len(self.associated_assets) == 0:
            return None
        else:
            return self.associated_assets


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