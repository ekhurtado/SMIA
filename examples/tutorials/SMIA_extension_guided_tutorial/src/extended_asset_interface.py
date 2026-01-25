import asyncio
import logging
import random

import smia
from smia.assetconnection.asset_connection import AssetConnection
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)

class MyExtendedInterface(AssetConnection):

    def __init__(self):
        # If the constructor will be overridden remember to add 'super().__init__()'.
        pass

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        # The Interface element need to be checked
        await self.check_interface_element(interface_aas_elem)

        # General information about the connection to the asset is defined in the SMC 'EndpointMetadata'.
        self.endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)

        # The endpointMetadata element need to be checked
        await self.check_endpoint_metadata()

        base_property = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        _logger.assetinfo("Base endpoint of extended interface: {}".format(base_property.id_short))

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        _logger.info("Hi! I am an Extended Interface that can simulate the connection to an asset.")
        _logger.info("The given AAS element is {}".format(interaction_metadata.id_short))

        if interaction_metadata.id_short == 'ExtendedAssetService':
            _logger.assetinfo("Executing the requested extended asset service...")
            steps = 5
            for i in range(steps + 1):
                await asyncio.sleep(.5)
                bar = '>>' * i + '-' * (steps - i) * 2
                _logger.assetinfo(f"[{bar}] {int((i / steps) * 100)}%")
            _logger.assetinfo("Extended asset service completed successfully.")
            result = {'status': 'OK'}
        elif interaction_metadata.id_short == 'AssetSpecificData':
            _logger.assetinfo("Obtaining the requested asset data...")
            result = round(random.uniform(0, 100), 2)
            _logger.assetinfo("The requested asset data value is: {}".format(result))
        else:
            result = {'status': 'OK'}

        return result

    async def receive_msg_from_asset(self):
        pass


async def test_asset_connection(myagent):

    aas_interface_ref = await smia.AASModelUtils.create_aas_reference_object(
        reference_type='ModelReference', keys_dict=[
            {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
            {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
            {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'InteractionMetadata'},
            {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'properties'},
            # {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'ExtendedAssetService'},
            {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'AssetSpecificData'},
        ])

    aas_interface_elem = await myagent.aas_model.get_object_by_reference(aas_interface_ref)
    new_asset_conn_ref = await smia.AASModelUtils.create_aas_reference_object(
        reference_type='ModelReference', keys_dict=[
            {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
            {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
        ])
    new_asset_conn_class = await myagent.get_asset_connection_class_by_ref(new_asset_conn_ref)
    result = await new_asset_conn_class.execute_asset_service(interaction_metadata=aas_interface_elem)
    _logger.info("An asset service has been executed with the new MyExtendedAssetConnection with result: {}".format(result))