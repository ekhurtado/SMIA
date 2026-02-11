import logging

from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo

import smia

from smia import GeneralUtils

from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas
from spade.behaviour import State

from smia.behaviours.init_aas_model_behaviour import InitAASModelBehaviour
from smia.logic import inter_smia_interactions_utils, acl_smia_messages_utils
from smia.utilities import smia_archive_utils, properties_file_utils
from smia.utilities.aas_related_services_info import AASRelatedServicesInfo
from smia.utilities.general_utils import SMIAGeneralInfo

_logger = logging.getLogger(__name__)


class StateBooting(State):
    """
    This class contains the Boot state of the common SMIA.
    """

    async def run(self):
        """
        This method implements the boot state of the common SMIA. Here all the required initialization tasks
        are performed.
        """

        await self.booting_state_logic()
        self.set_next_state(SMIAGeneralInfo.RUNNING_STATE_NAME)

    async def booting_state_logic(self):
        """
        This method contains the logic of the boot state of the common SMIA. This method can be used by any
        inherited class.
        """
        _logger.info("## STATE 1: BOOTING ##  (Initial state)")

        # First, it is ensured that the attributes of the SMIA are initialized
        self.agent.initialize_smia_attributes()

        # The ontology has to be initialized in order to be available during the AAS model analysis
        await self.agent.css_ontology.initialize_ontology()

        # The submodels also have to be initialized, so its behaviour is also added
        init_aas_model_behav = InitAASModelBehaviour(self.agent)
        self.agent.add_behaviour(init_aas_model_behav)

        # Wait until the behaviours have finished because the AAS Archive has to be initialized to pass to running state
        await init_aas_model_behav.join()

        # If the initialization behaviour has completed, SMIA is in the InitializationReady status
        smia_archive_utils.update_status('InitializationReady')

        # When all initialization tasks have been completed, if the SMIA has been configured to register on the
        # SMIA-I KB, it will try to register through an infrastructure service provided by the SMIA ISM
        if str(properties_file_utils.get_dt_general_property('smia-i-kb-registration')).lower() in ('yes', 'true', 't', '1'):
            if await acl_smia_messages_utils.get_agent_id_from_jid(self.agent.jid) != AASRelatedServicesInfo.SMIA_ISM_ID:
                # The extracted CSS elements in the self-configuration process will be registered in the SMIA KB
                await self.send_register_css_elements_acl_msg()

                # The SMIA instance itself will be also registered in the SMIA KB
                await self.send_register_instance_acl_msg()

        # Finished the Boot State the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Boot state.")


    async def send_register_css_elements_acl_msg(self):
        """
        This method sends the ACL message to register all the CSS elements of the instance, extracted from the
        self-configuration process. All the CSS elements will be registered in the SMIA KB  through an infrastructure
        service provided by the SMIA ISM. It will wait 5 seconds for the 'inform' performative message with the
        registration confirmation. If it does not receive any message, it will just show a warning message and continue
        its execution.
        """
        css_elements_json = {'capabilities': [], 'skills': []}
        # First, the JSON of each capability will be obtained
        for capability in (filter(None,
                (await self.agent.css_ontology.get_ontology_instances_by_class_iri(
                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI) or []) +
                (await self.agent.css_ontology.get_ontology_instances_by_class_iri(
                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI) or []) +
                (await self.agent.css_ontology.get_ontology_instances_by_class_iri(
                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI) or []))):
            capability_json = capability.from_ontology_instance_to_json()   # The JSON is created from OWL instance
            # The asset information is also added
            capability_json['assets'] = [{
                'id': await self.agent.aas_model.get_asset_information_attribute_value('asset_id'),
                'kind': await self.agent.aas_model.get_asset_information_attribute_value('asset_kind'),
                'type': await self.agent.aas_model.get_asset_information_attribute_value('asset_type')}]
            css_elements_json['capabilities'].append(capability_json)

        # Then, the JSON of each skill will be obtained
        for skill in await self.agent.css_ontology.get_ontology_instances_by_class_iri(
                CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
            # The JSON is created from OWL instance
            css_elements_json['skills'].append(skill.from_ontology_instance_to_json())


        smia_ism_jid = (f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
                        f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(self.agent.jid)}")
        register_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            # 'gcis1@xmpp.jp', await acl_smia_messages_utils.create_random_thread(self.agent),
            smia_ism_jid, await acl_smia_messages_utils.create_random_thread(self.agent),
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE,
            protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE, serviceID=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_CSS_ELEMENTS, serviceType=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_SERVICE_TYPE_REGISTRY, serviceParams=css_elements_json))
        _logger.info("Sending the infrastructure service request to {} to register all the CSS elements of the SMIA "
                     "instance in the SMIA KB.".format(smia_ism_jid))
        await self.send(register_acl_msg)
        _logger.info("Waiting for the confirmation of the registry in the SMIA KB...")
        msg = await self.receive(timeout=60)  # Timeout set to 10 seconds
        if msg:
            valid_msg_template = GeneralUtils.create_acl_template(
                FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE)
            if valid_msg_template.match(msg) and msg.thread == register_acl_msg.thread:
                _logger.aclinfo("CSS elements successfully registered in the SMIA KB")
            else:
                ("A message arrived but it is not about the CSS elements. Sender [{}], Performative [{}], "
                 "Ontology [{}]".format(acl_smia_messages_utils.get_sender_from_acl_msg(msg),
                                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB),
                                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB)))
        else:
            _logger.warning("The registry of CSS elements has not been completed. Check the SMIA ISM or the SMIA KB.")

    async def send_register_instance_acl_msg(self):
        """
        This method sends the ACL message to register its instance in the SMIA KB  through an infrastructure service
        provided by the SMIA ISM. It will wait 5 seconds for the 'inform' performative message with the registration
        confirmation. If it does not receive any message, it will just show a warning message and continue its execution.
        """
        smia_instance_json = {'id': str(self.agent.jid), 'asset':
            {'id': await self.agent.aas_model.get_asset_information_attribute_value('asset_id'),
             'kind': await self.agent.aas_model.get_asset_information_attribute_value('asset_kind'),
             'type': await self.agent.aas_model.get_asset_information_attribute_value('asset_type')},
                              'aasID':await self.agent.aas_model.get_aas_attribute_value('id'),
                              'status': 'Running', 'startedTimeStamp': GeneralUtils.get_current_timestamp(),
                              'smiaVersion': smia.__version__}
        smia_ism_jid = (f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
                        f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(self.agent.jid)}")
        register_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            # 'gcis1@xmpp.jp', await acl_smia_messages_utils.create_random_thread(self.agent),
            smia_ism_jid, await acl_smia_messages_utils.create_random_thread(self.agent),
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE,
            protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE, serviceID=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_SERVICE_REGISTER_SMIA, serviceType=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_SERVICE_TYPE_REGISTRY, serviceParams=smia_instance_json))
        _logger.info("Sending the infrastructure service request to {} to register the SMIA instance in the SMIA "
                     "KB.".format(smia_ism_jid))
        await self.send(register_acl_msg)
        _logger.info("Waiting for the confirmation of the registry in the SMIA KB...")
        msg = await self.receive(timeout=60)  # TODO DELETE: CHANGED FOR REGISTRATION PERFORMANCE TEST
        # msg = await self.receive(timeout=5)  # Timeout set to 5 seconds
        _logger.assetinfo("HA PASADO DEL RECEIVE")  # TODO BORRAR
        if msg:
            _logger.assetinfo("MENSAJE RECEIVE: {}".format(msg))  # TODO BORRAR
            valid_msg_template = GeneralUtils.create_acl_template(
                FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE)
            if valid_msg_template.match(msg) and msg.thread == register_acl_msg.thread:
                _logger.aclinfo("SMIA instance successfully registered in the SMIA KB")

                # TODO DELETE: REGISTRATION PERFORMANCE TEST
                from smia.utilities import smia_archive_utils, smia_general_info
                import os
                registered_time = GeneralUtils.get_current_timer_nanosecs()
                metrics_folder = os.environ.get('METRICS_FOLDER')
                if metrics_folder is None:
                    metrics_folder = smia_general_info.SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/metrics'
                if self.agent.setup_time is None:
                    _logger.error("The registration time could not be obtained because the agent does not have the "
                                  "specified start time.")
                else:
                    await smia_archive_utils.save_csv_calculated_metrics(metrics_folder, self.agent.jid,
                                                                         registered_time-self.agent.setup_time,
                                                                         'Time elapsed for SMIA registration')
                    _logger.assetinfo("ALMACENADO TIEMPO {} en {}".format(metrics_folder,
                                                                          registered_time-self.agent.setup_time))  # TODO BORRAR

            else:
                ("A message arrived but it is not about the registration. Sender [{}], Performative [{}], "
                 "Ontology [{}]".format(acl_smia_messages_utils.get_sender_from_acl_msg(msg),
                                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB),
                                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB)))
        else:
            _logger.warning("The registry of the SMIA instance {} has not been completed. Check the SMIA ISM or the "
                            "SMIA KB.".format(str(self.agent.jid)))
