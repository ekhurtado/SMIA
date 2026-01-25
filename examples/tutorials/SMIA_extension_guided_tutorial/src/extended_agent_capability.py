import asyncio
import logging

import smia
from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)

class DiagnosisAgentCapability(CyclicBehaviour):

    def __init__(self, agent_object):
        super().__init__()

        self.interaction_num = 0
        self.event_threshold = 60.0
        self.myagent = agent_object

    async def run(self) -> None:

        _logger.info("Hi! I am an extended DiagnosisAgentCapability with interaction number: {}".format(self.interaction_num))
        self.interaction_num += 1

        try:
            if self.interaction_num == 5:
                # Let's execute the new extended agent service
                _logger.info("---------------------")
                result = await self.myagent.agent_services.execute_agent_service_by_id(
                    'ExtendedAgentService', extended_param=self.interaction_num)
                _logger.info("The result of the new agent service ExtendedAgentService is {}".format(result))
                _logger.info("---------------------")

            # Let's execute an asset service using the new Asset Connection
            aas_interface_ref = await smia.AASModelUtils.create_aas_reference_object(
                reference_type='ModelReference', keys_dict=[
                    {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'InteractionMetadata'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'properties'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'AssetSpecificData'},
                ])
            aas_interface_elem = await self.myagent.aas_model.get_object_by_reference(aas_interface_ref)
            new_asset_conn_ref = await smia.AASModelUtils.create_aas_reference_object(
                reference_type='ModelReference', keys_dict=[
                    {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
                ])
            new_asset_conn_class = await self.myagent.get_asset_connection_class_by_ref(new_asset_conn_ref)
            result = await new_asset_conn_class.execute_asset_service(interaction_metadata=aas_interface_elem)
            _logger.info("An asset service has been executed with the new MyExtendedInterface with result: {}".format(
                    result))
            if result > self.event_threshold:
                _logger.warning("The asset data has exceeded the defined threshold. An event must be triggered.")

        except Exception as e:
            _logger.error("An error occurred: {}".format(e))

        await asyncio.sleep(3)    # waits 3 seconds in every cyclic execution