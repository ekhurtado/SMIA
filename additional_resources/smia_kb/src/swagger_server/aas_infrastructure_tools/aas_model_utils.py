import sys

import basyx.aas
from basyx.aas import model
from basyx.aas.util import traversal


class AASModelUtils:

    @staticmethod
    def get_submodel_elements_by_semantic_id(submodel_object_json, semantic_id_external_ref):
        rels_elements = []
        try:
            if isinstance(submodel_object_json, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(submodel_object_json):
                    if isinstance(submodel_element, model.SubmodelElement):
                        if AASModelUtils.check_semantic_id_exist(submodel_element, semantic_id_external_ref):
                            # An ontological AAS element has been found
                            rels_elements.append(submodel_element)
                        if isinstance(submodel_element, basyx.aas.model.Operation):
                            # In case of Operation, OperationVariables need to be analyzed
                            rels_elements.extend(AASModelUtils.get_operation_variables_by_semantic_id(
                                submodel_element, semantic_id_external_ref))
        except Exception as e:
            print("ERROR: It cannot obtain AAS element with ontological semantic identifiers from the submodel.",
                  file=sys.stderr)
            return []
        return rels_elements

    @staticmethod
    def check_semantic_id_exist(submodel_elem_json, semantic_id_reference):
        """
        This method checks if a specific semanticID exists in an AAS meta-model element.

        Args:
            semantic_id_reference (str): semantic identifier.

        Returns:
            bool: result of the check (only True if the semanticID exists).
        """
        if submodel_elem_json.semantic_id is None:
            return False
        for reference in submodel_elem_json.semantic_id.key:
            if reference.value == semantic_id_reference:
                return True
        return False

    @staticmethod
    def get_operation_variables_by_semantic_id(aas_operation_object, semantic_id):
        """
        This method gets all operation variables that have the given semanticID.

        Args:
            aas_operation_object (model.Operation): JSON object of the AAS operation SubmodelElement.
            semantic_id (str):  semantic identifier of the operation variables to find.

        Returns:
            list: all valid operation variables in form of a list of SubmodelElements.
        """
        operation_variables = []
        all_var_sets = [aas_operation_object.input_variable, aas_operation_object.output_variable,
                        aas_operation_object.in_output_variable]
        for var_set in all_var_sets:
            for operation_variable in var_set:
                if AASModelUtils.check_semantic_id_exist(operation_variable, semantic_id):
                # if operation_variable.check_semantic_id_exist(semantic_id):
                    operation_variables.append(operation_variable)
        return operation_variables

    @staticmethod
    def get_asset_id_from_aas(aas_model_object):
        if aas_model_object.asset_information.global_asset_id is not None:
            return aas_model_object.asset_information.global_asset_id
        elif aas_model_object.asset_information.specific_asset_id is not None and len(aas_model_object.asset_information.specific_asset_id) > 0:
            return aas_model_object.asset_information.specific_asset_id[0].value
        return None

    @staticmethod
    def get_qualifier_value_by_semantic_id(aas_qualifiable_object, qualifier_semantic_id):
        """
        This method gets the value of the qualifier that has a given semanticID.

        Args:
            aas_qualifiable_object (model.SubmodelElement): JSON object of the AAS Qualifiable SubmodelElement.
            qualifier_semantic_id (str): semanticID of the qualifier.

        Returns:
            str: value of the qualifier with the given type
        """
        try:
            if len(aas_qualifiable_object.qualifier) == 0:
                return None
            for qualifier in aas_qualifiable_object.qualifier:
                if AASModelUtils.check_semantic_id_exist(qualifier, qualifier_semantic_id) is True:
                    return qualifier.value
            else:
                return None

        except KeyError as e:
            print("ERRRO: Qualifier with semanticID {} not found in the element {}".format(
                qualifier_semantic_id, aas_qualifiable_object), file=sys.stderr)