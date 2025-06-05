class AASRelatedServicesInfo:

    # The SMIA ISM identifier should always be the same, but if it changes, it should be changed here as well.
    SMIA_ISM_ID = 'smia-ism'

    # AAS Services information
    # ------------------------
    # AAS Services types
    AAS_SERVICE_TYPE_SUBMODEL_REGISTRY = 'SubmodelRegistryService'
    AAS_SERVICE_TYPE_METAINFORMATION = 'MetaInformationManagementService'
    AAS_SERVICE_TYPE_DISCOVERY = 'DiscoveryService'

    # AAS Discovery Services identifiers
    AAS_DISCOVERY_SERVICE_GET_SM_BY_REF = 'GetSubmodelElementByReference'
    AAS_DISCOVERY_SERVICE_GET_SM_VALUE_BY_REF = 'GetSubmodelElementValueByReference'
    AAS_DISCOVERY_SERVICE_GET_AAS_INFO = 'GetAASInformationElement'
    AAS_DISCOVERY_SERVICE_GET_SM_BY_ID = 'GetSubmodelBySubmodelID'
    AAS_DISCOVERY_SERVICE_SET_SM_VALUE_BY_REF = 'SetSubmodelElementValueByReference'

    # AAS Infrastructure Services information
    # ---------------------------------------
    # AAS Infrastructure Services types
    AAS_INFRASTRUCTURE_SERVICE_TYPE_REGISTRY = 'RegistryService'
    AAS_INFRASTRUCTURE_SERVICE_TYPE_DISCOVERY = 'DiscoveryService'

    # AAS Infrastructure Registry Services identifiers
    AAS_INFRASTRUCTURE_REGISTRY_SERVICE_REGISTER_SMIA = 'RegisterSMIAInstance'

    # AAS Infrastructure Discovery Services identifiers
    AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_SMIA_BY_ASSET = 'GetSMIAInstanceIDByAssetID'
    AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ASSET_BY_SMIA = 'GetAssetIDBySMIAInstanceID'
    AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY = 'GetAllAssetIDByCapability'

