class ExtendedAssetAdministrationShell:
    """This class contains methods to be added to AssetAdministrationShell class of Basyx Python SDK model."""

    def print_aas_information(self):
        print("AAS information:")
        print("\tid: " + self.id)
        print("\tid_short: " + self.id_short)
        print("\tdisplayName:{}".format(self.display_name))
        print("\tdescription:{}".format(self.description))
        print("\tcategory: {}".format(self.category))
        print("\tderivedFrom: {}".format(self.derived_from))
        print("\tadministration: {}".format(ExtendedGeneralMethods.print_administration(self.administration)))
        print("\textension: " + "{}".format(ExtendedGeneralMethods.print_namespace_set(self.extension)))
        print("\tdataSpecifications: " + "{}".format(
            ExtendedGeneralMethods.print_data_specifications(self.embedded_data_specifications)))


class ExtendedAssetInformation:
    """This class contains methods to be added to AssetInformation class of Basyx Python SDK model."""

    def print_asset_information(self):
        print("Asset information:")
        print("\tassetKind: {}".format(self.asset_kind))
        print("\tassetType: {}".format(self.asset_type))
        print("\tspecificAssetId: {}".format(self.specific_asset_id))
        print("\tglobalAssetId: {}".format(self.global_asset_id))
        print("\tdefaultThumbnail: {}".format(self.default_thumbnail))

    def get_asset_id(self):
        """
        This method gets the asset identifier: if 'global_asset_id' is set, it is returned. If not, it checks if
        'specific_asset_id' has been added, and returns if true. Returns None if both are empty.

        Returns:

        """
        if self.global_asset_id is not None:
            return self.global_asset_id
        elif self.specific_asset_id is not None:
            return self.specific_asset_id[0].value if self.specific_asset_id[0].value is not None else None
        return None

class ExtendedGeneralMethods:

    @staticmethod
    def print_administration(administration):
        if administration:
            return "version[{}".format(administration.version) + "], revision[{}".format(
                administration.revision) + "], creator[{}".format(administration.creator) + "], templateId[{}".format(
                administration.template_id) + "]"
        else:
            return ""

    @staticmethod
    def print_namespace_set(namespace_set):
        string = ""
        for item in namespace_set:
            string += str(item) + ","
        return string

    @staticmethod
    def print_data_specifications(embedded_data_specifications):
        string = ""
        for item in embedded_data_specifications:
            string += ("(Reference: {}".format(item.data_specification) +
                       " | Content: {}".format(item.data_specification_content) + "),")
        return string
