import asyncio
import logging
from typing import Any

from basyx.aas.model import ModelReference
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from examples.tutorials.SMIA_simulated_assets_guided_tutorial.OperationalHealthSupervisor.utilities import \
    create_asset_service_acl_msg
from smia import AASModelUtils
from smia.utilities.smia_info import AssetInterfacesInfo
from utilities import HealthSupervisorSemantics, create_discover_acl_msg_to_smia_ism, extract_supervised_assets_data, \
    create_aas_service_discover_acl_msg
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from smia.logic import acl_smia_messages_utils
from smia.utilities.aas_related_services_info import AASRelatedServicesInfo

_logger = logging.getLogger(__name__)

class HealthSupervisorBehaviour(CyclicBehaviour):

    def __init__(self, agent_object):
        super().__init__()

        self.interaction_num = 0
        self.myagent = agent_object

        # Variables influencing coordination among the Health Supervisor's behaviors
        self.myagent.ohs_acl_requests_event = asyncio.Event()
        self.myagent.ohs_acl_responses = {}

        # Health Supervisor-specific variables
        self.supervision_interval: float = None
        self.health_threshold: float = None
        self.supervised_assets_dict: dict = None
        self.platform_smia_instances: dict = {}

        # The additional behaviour for receiving, collecting, and interpreting ACL messages from other SMIA agents is
        # added to the agent
        receive_acl_behav = OHSReceiveACLBehaviour(agent_object=self.myagent)
        self.myagent.add_new_agent_capability(receive_acl_behav)


    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HealthSupervisorBehaviour starting... configuring the necessary information...")

        # All the information necessary for the behaviour to function will be obtained
        self.supervision_interval = (await self.get_critical_sm_element_by_semantic_id(
            HealthSupervisorSemantics.SEMANTICID_OHS_SUPERVISION_INTERVAL)).value
        self.health_threshold = (await self.get_critical_sm_element_by_semantic_id(
            HealthSupervisorSemantics.SEMANTICID_OHS_HEALTH_THRESHOLD)).value

        self.supervised_assets_dict = await extract_supervised_assets_data(
            supervised_assets_list=await self.get_critical_sm_element_by_semantic_id(
            HealthSupervisorSemantics.SEMANTICID_OHS_SUPERVISED_ASSETS))

        _logger.info("HealthSupervisorBehaviour initialization complete")


    async def run(self) -> None:

        # In each iteration, the health of all assets to be supervised will be analyzed, and a replenishment action
        # will be requested for those that require it
        for supervised_capability, supervised_asset_data in self.supervised_assets_dict.items():
            # For each capability, we will first identify all SMIA agents of the assets possessing that capability
            smia_instances_list = await self.get_platform_smia_instances_by_capability(supervised_capability)
            _logger.warning("LISTA DE INSTANCIAS SMIA: {}".format(smia_instances_list)) # TODO BORRAR

            for smia_instance_id in smia_instances_list:
                # For each SMIA instance, health asset data will be requested. To do this, first the ModelReference
                # within the instance's submodel must be obtained
                health_property_ref = await self.health_property_model_reference(
                    smia_instance_id, supervised_asset_data['healthProperty'])
                _logger.warning("REFERENCIA HEALTH PROPERTY: {}".format(health_property_ref))  # TODO BORRAR

                # With the valid ModelReference, you can request the value of the property from the associated SMIA
                health_property_value = await self.health_property_value_from_smia_instance(smia_instance_id, health_property_ref)
                _logger.warning("VALOR HEALTH PROPERTY: {}".format(health_property_value)) # TODO BORRAR



        # Wait for the defined interval before the next iteration
        await asyncio.sleep(self.supervision_interval)



    async def get_critical_sm_element_by_semantic_id(self, semantic_id):
        """
        This method gets a critical SubmodelElement for the functioning of Operational Health Supervisor using a
        specific semantic identifier.

        Args:
            semantic_id (str): semantic id to find the SubmodelElement, in form of an external reference.

        Returns:
            basyx.aas.model.SubmodelElement: SubmodelElement with the specified semantic id.
        """
        submodel_elem = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(semantic_id)
        if submodel_elem is None or len(submodel_elem) == 0:
            # Since this is critical data for the operation of Operational Health Supervisor, an error message will be
            # displayed and the behavior will be killed.
            _logger.error("A critical data for Operational Health Supervisor is missing. Please, add the "
                          "SubmodelElement with the required data and include the semanticID: {}".format(semantic_id))
            self.kill(exit_code=10)
        if isinstance(submodel_elem, list):
            submodel_elem = submodel_elem[0]

        return submodel_elem

    async def get_platform_smia_instances_by_capability(self, capability_name):
        """
        This method retrieves the SMIA instances deployed within the platform (MAS) that have the specified capacity.
        To do this, an infrastructure service request is sent to SMIA ISM so that it can retrieve the global information
         from the SMIA-I KB.

        Args:
            capability_name (str): name of the required asset capability to build the ontological identifier.

        Returns:
            list(str): list with all SMIA instances identifiers within the platform (MAS).
        """
        # First, it will obtain all the asset identifiers associated to the given capability
        capability_iri = '{}{}'.format(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SMIA_NAMESPACE, capability_name)
        assets_request_acl_msg = await create_discover_acl_msg_to_smia_ism(self.myagent,
            service_id=AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY,
            service_params=capability_iri)
        assets_id_list = await self.send_acl_and_wait(assets_request_acl_msg)

        # The data will not be requested if it has already been obtained; it will be included in the behavior dictionary.
        smia_instances_cap_list = set()
        for asset_id in assets_id_list:
            if asset_id in self.platform_smia_instances:
                smia_instances_cap_list.add(self.platform_smia_instances[asset_id])
            else:
                # In this case it must be requested to the SMIA ISM, in order to obtain from the SMIA-I KB
                smia_request_acl_msg = await create_discover_acl_msg_to_smia_ism(self.myagent,
                    service_id=AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_SMIA_BY_ASSET,
                    service_params=asset_id)
                smia_instance_id = await self.send_acl_and_wait(smia_request_acl_msg)

                if smia_instance_id is not None:
                    smia_instances_cap_list.add(str(smia_instance_id))

        return smia_instances_cap_list

    async def health_property_model_reference(self, smia_instance_id: str, health_property: str):
        """
        This method

        Args:
            smia_instance_id(str): identifier of the SMIA instance to be requested the model reference of the asset
            health property.

        Returns:
            basyx.aas.model.base.ModelReference: AAS model reference of the asset health property.
        """
        # First, we must obtain the AID (submodel identifier) for that SMIA instance. This will be done by sending a
        # request to an AAS service.
        aas_svc_msg = await create_aas_service_discover_acl_msg(self.myagent,
            smia_instance_id, service_id=AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_BY_SEMANTICID,
            service_params=AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        aid_submodel_json = await self.send_acl_and_wait(aas_svc_msg)
        if aid_submodel_json is None or 'id' not in aid_submodel_json or 'submodelElements' not in aid_submodel_json:
            _logger.warning("The SMIA instance [{}] does not have the submodel AssetInterfacesDescription".format(
                smia_instance_id))
            return None
        # Using the submodel identifier, we can create the ModelReference

        return {'keys': [
        # return await AASModelUtils.create_aas_reference_object(
        #     reference_type='ModelReference', keys_dict=[
                {'type': 'SUBMODEL', 'value': aid_submodel_json['id']},
                {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': aid_submodel_json['submodelElements'][0]['idShort']},
                {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'InteractionMetadata'},
                {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'properties'},
                {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': health_property},
            ]}
            # ])

    async def health_property_value_from_smia_instance(self, smia_instance_id, health_property_ref: ModelReference):
        """
        This method gets the health property value from the SubmodelElement of the associated SMIA instance.

        Args:
            smia_instance_id (str): identifier of the SMIA instance to be requested the property value.
            health_property_ref (basyx.aas.model.base.ModelReference): AAS model reference to the Health property object.

        Return:
            obj: value of the health property, obtained from the SMIA instance.
        """
        asset_svc_acl_msg = await create_asset_service_acl_msg(self.myagent, receiver_id=smia_instance_id,
                                                               service_ref=health_property_ref)
        return await self.send_acl_and_wait(asset_svc_acl_msg)

    async def send_acl_and_wait(self, acl_msg: Message) -> Any:
        """
        This method sends an ACL message and waits to the response.

        Args:
            acl_msg (spade.message.Message): the SPADE message object to be sent.
        """
        await self.myagent.add_reserved_thread(acl_msg.thread)
        self.myagent.ohs_acl_responses[acl_msg.thread] = None

        await self.send(acl_msg)

        # Now the behaviour will wait until the response message arrive to the Receiver Behaviour and unlocks the Event
        await self.myagent.ohs_acl_requests_event.wait()
        # If the behaviour continues from this line, it means that the response has arrived, so the Event is cleared
        self.myagent.ohs_acl_requests_event.clear()
        # The response content will be available in the 'ohs_acl_responses' of the behaviour
        return self.myagent.ohs_acl_responses[acl_msg.thread]


class OHSReceiveACLBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA will receive from the
    others SMIAs in the I4.0 System. If some of these messages are responses to previous SMIA OHS requests, the
    HealthSupervisorBehaviour will be unlocked to continue its operation.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("OHSReceiveACLBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            _logger.aclinfo("Analyzing ACL message... Checking if it is a response from previous SMIA OHS request... ")
            if msg.thread in self.myagent.ohs_acl_responses:
                _logger.info("Unlocking HealthSupervisorBehaviour...")
                msg_parsed_body = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)
                _logger.warning("VALUE : {}".format(msg_parsed_body))
                self.myagent.ohs_acl_responses[msg.thread] = msg_parsed_body
                # The behaviour is unlocked
                self.myagent.ohs_acl_requests_event.set()