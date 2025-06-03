import asyncio
import logging
import random
import string

from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.specs.defaults import ServiceTask
from smia import CriticalError
from smia.logic import inter_aas_interactions_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo
from spade.behaviour import OneShotBehaviour

from utilities.smia_bpmn_info import SMIABPMNInfo
from utilities.smia_bpmn_utils import SMIABPMNUtils
from utilities.spia_aas_model_utils import SPIAAASModelUtils

_logger = logging.getLogger(__name__)

class BPMNPerformerBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles the execution of a CSS-driven BPMN flexible production plan.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        # The object to store the content of the associated BPMN file
        self.bpmn_file_bytes = None

        # This event object will allow waiting for the response of an ACL request message from SPIA to other SMIA
        # instances (when requesting data, requesting capabilities execution...). Since this behaviour is OneShot, when
        # it needs to wait for a response it will be blocked with this object. When the ACL response arrived, the
        # ReceiveACLBehaviour will unlock this behaviour, offering the response message content
        self.acl_request_event = asyncio.Event()
        # This object will be used to obtain the response message content. When the ReceiveACLBehaviour receives a
        # message, it will add the content with the thread of the message {'threadValue': 'ACLcontent'}
        self.acl_messages_responses = {}

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("BPMNPerformerBehaviour starting...")

        # The BPMN file content is obtained in bytes
        _logger.info("Obtaining the BPMN file content...")
        self.bpmn_file_bytes = SPIAAASModelUtils.get_bpmn_file_bytes_from_aas()
        if self.bpmn_file_bytes is None:
            CriticalError("BPMN file not found, so the SPIA cannot start.")
        _logger.info("The BPMN file content for this SPIA obtained and stored.")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # This behavior analyzes and performs a BPMN production plan based on CSS. The behavior is OneShot so it will
        # perform the plan and terminate itself. When requests need to be made to other SMIA instances it will remain
        # blocked until the response for this message arrives. A complementary Cyclic behavior has been developed to
        # receive all messages and unblock this behavior to continue with the production plan.

        # First, the BPMN parser is created, the SMIA namespace is added and the BPMN file content is loaded
        bpmn_parser = BpmnParser()
        bpmn_parser.namespaces['smia'] = SMIABPMNInfo.BPMN_SMIA_NAMESPACE
        bpmn_parser.add_bpmn_str(self.bpmn_file_bytes)

        # Let's get the parser of the process related to the production plan and all the values of the required
        # SMIA attributes
        process_parser = SMIABPMNUtils.get_process_parser(bpmn_parser)
        SMIABPMNUtils.add_smia_attributes_values(process_parser)
        self.process_parser = process_parser

        # To finalize the initialization of the BPMN file, the SMIA instances associated to the specified assets need
        # to be obtained
        await self.get_smia_instances_of_specified_assets()

        # When the BPMN file has been initialized, it can be started to execute
        await self.execute_workflow()


    async def get_smia_instances_of_specified_assets(self):
        """
        This method gets all the SMIA instances identifiers of the specified capabilities where the asset has been
        specified.
        """
        for spec_name, spec_instance in self.process_parser.get_spec().task_specs.items():
            if isinstance(spec_instance, ServiceTask):
                if spec_instance.smia_asset is not None:
                    # In this case the asset has been specified so it will need to request an AAS Infrastructure Service
                    # to get the SMIA identifier associated to this asset identifier
                    _logger.info("Requesting an AAS Infrastructure Service to obtain the SMIA instance identifier for "
                                 "asset [{}].".format(spec_instance.smia_asset))
                    spec_instance.smia_instance = await self.get_smia_instance_id_by_asset_id(spec_instance.smia_asset)
                    # TODO HACERLO (usar los metodos de ACL del final del behaviour)

    async def execute_workflow(self):
        """
        This method executes the BPMN workflow.
        """
        # Let's start from the beginning
        current_elem = self.process_parser.get_spec().start

        while current_elem is not None:
            # The BPMN element is performed and, when finished, the next one is obtained
            await self.execute_bpmn_element(current_elem)
            current_elem = SMIABPMNUtils.get_next_bpmn_element(self.process_parser, current_elem)
        # When it is arrived to an EndEvent the current_elem is None, so the BPMN can finish
        _logger.info("BPMN workflow completed successfully.")

    async def execute_bpmn_element(self, current_bpmn_elem):
        """
        This method executes a specific element of the BPMN workflow.

        Args:
            current_bpmn_elem: BPMN element object.
        """
        # Before executing the BPMN element it is necessary to check if some additional tasks need to be done
        if isinstance(current_bpmn_elem, ServiceTask) and len(current_bpmn_elem.smia_additional_tasks) > 0:
            await self.execute_additional_tasks_of_bpmn_element(current_bpmn_elem)
        _logger.info("Executing BPMN element {}".format(current_bpmn_elem.bpmn_name))
        # TODO
        print("TODO")

    async def execute_additional_tasks_of_bpmn_element(self, bpmn_element):
        """
        This method executes the additional tasks related to a specific element of the BPMN workflow.

        Args:
            bpmn_element: BPMN element object.
        """
        for task in bpmn_element.smia_additional_tasks:
            if task == SMIABPMNInfo.TASK_REQUEST_DISTRIBUTED_CNP:
                if (hasattr(bpmn_element, 'smia_asset') and bpmn_element.smia_asset is not None and
                        hasattr(bpmn_element, 'smia_instance') and bpmn_element.smia_instance is not None):
                    # In this case the CNP protocol has been performed in a previous step due to a request of a data for
                    # this instance
                    pass
                else:
                    _logger.info("The capability {} does not have specified an asset identifier specified, so it will "
                                 "be obtained through the CNP protocol.".format(bpmn_element.smia_capability))
                    # TODO: FALTA POR HACER (Habria que solicitar todos los IDs de las instancias SMIA de esta capacidad y enviarles un mensaje ACL a todos ellos)

            if task == SMIABPMNInfo.TASK_REQUEST_DATA_TO_PREVIOUS:
                for previous_request in bpmn_element.smia_request_to_previous:
                    previous_element = SMIABPMNUtils.get_previous_bpmn_element(self.process_parser, bpmn_element)
                    _logger.info("A data need to be requested to the SMIA instance {}".format(previous_element.smia_instance))
                    # TODO POR HACER: HABRIA QUE ENVIAR UN MENSAJE ACL
                    datavalue = 'dataValue' # TODO BORRAR ES UNA PRUEBA MANUAL
                    # When the data is obtained, it needs to be added to the BPMN element
                    SMIABPMNUtils.update_bpmn_element_with_requested_data(bpmn_element, previous_request, datavalue)
            if task == SMIABPMNInfo.TASK_REQUEST_DATA_TO_FOLLOWING:
                for following_request in bpmn_element.smia_request_to_following:
                    following_element = SMIABPMNUtils.get_next_bpmn_element(self.process_parser, bpmn_element)
                    if following_element.smia_asset is None:
                        # It cannot request to the following element because it needs to perform a distributed CNP
                        # protocol to obtain the asset and SMIA identifiers
                        # TODO ENVIAR UN CNP
                        pass
                        # When it has obtained the winner of the CNP protocol, it need to be added to the BPMN element
                        following_element.smia_asset = 'winner of CNP'  # TODO MODIFICAR ESTA MANUALMENTE
                        following_element.smia_instance = 'winner of CNP'  # TODO MODIFICAR ESTA MANUALMENTE

                    # Now the following element is specified, so the data can be requested
                    _logger.info("A data need to be requested to the SMIA instance {}".format(following_element.smia_instance))
                    # TODO POR HACER: HABRIA QUE ENVIAR UN MENSAJE ACL
                    datavalue = 'dataValue'  # TODO BORRAR ES UNA PRUEBA MANUAL
                    # When the data is obtained, it needs to be added to the BPMN element
                    SMIABPMNUtils.update_bpmn_element_with_requested_data(bpmn_element, following_request, datavalue)

            if task == SMIABPMNInfo.TASK_CHECK_TIMEOUT:
                # TODO BORRAR: ESTO ES UNA PRUEBA MANUAL PARA QUE NO FALLE DE MOMENTO. Se podria realizar de la
                #  siguiente forma: cuando se vaya a solicitar ejecutar la capacidad, se analizaría si tiene timeout.
                #  Si lo tiene, se lanzaria una capacidad OneShot que ejecutará una cuenta atras y si llega,
                #  desbloqueara este behaviour (estara esperando con un asyncio.Event) y eliminara de la cola de
                #  mensajes ACL a la espera, añadiendo como resultado "TIMEOUT REACHED" (si se recibe la respuesta
                #  ACL no se tendra en cuenta)
                bpmn_element.smia_timeout_reached = True  # Ponerlo a False si se quiere establecer que no se ha cumplido el timeout


    # Methods related to interactions with other SMIA instances
    # ---------------------------------------------------------
    @staticmethod
    async def create_random_thread():
        # TODO PENSARLO AÑADIRLO EN SMIA TAMBIEN
        """
        This method creates a value for the thread of a SPADE-ACL message, using the agent identifier and random string.

        Returns:
            str: thread value
        """
        return f"speia-{''.join(random.choices(string.ascii_letters + string.digits, k=4)).lower()}"

    async def send_acl_and_wait(self, acl_msg):
        """
        This method sends an ACL message and waits to the response.

        Args:
            acl_msg (spade.message.Message): the SPADE message object to be sent.
        """
        await self.send(acl_msg)
        # To warn that it is waiting for a value for a given thread, the thread will be added to the response object
        # with a null value
        self.acl_messages_responses[acl_msg.thread] = None
        # Now the behaviour will wait until the response message arrive to the Receiver Behaviour and unlocks the Event
        await self.acl_request_event.wait()
        # If the behaviour continues from this line, it means that the response has arrived, so the Event is cleared
        self.acl_request_event.clear()
        # The response content will be available in the 'acl_messages_responses' of the behaviour
        return self.acl_messages_responses[acl_msg.thread]

    # TODO PENSAR SI LLEVARLOS A utilities (que simplemente generen el mensaje ACL y despues desde aqui se hace el 'send')
    async def get_smia_instance_id_by_asset_id(self, asset_id):
        """
        This method gets the SMIA instance identifier associated to a given asset ID.

        Args:
            asset_id (str): identifier of the asset

        Returns:
            str: identifier of the associated SMIA instance.
        """
        try:
            # In order to obtain the data, an AAS Infrastructure Service need to be requested to SMIA ISM
            acl_msg_thread = await BPMNPerformerBehaviour.create_random_thread()
            request_acl_msg = await inter_aas_interactions_utils.create_acl_smia_message(
                f"gcis1@{str(self.myagent.jid).split('@')[1]}",   # TODO BORRAR
                # f"smia-ism@{str(self.myagent.jid).split('@')[1]}",   # TODO SE PODRIA HACER UN METODO EN SMIA PARA RECOGER EL XMPP SERVER
                acl_msg_thread, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
                ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE,
                msg_body={'serviceID': 'GetSMIAInstanceIDByAssetID', 'serviceType': 'DiscoveryService',
                          'serviceParams': asset_id})
            await self.send_acl_and_wait(request_acl_msg)


        except Exception as e:
            print(e)

    async def get_smia_instances_id_by_capability(self, capability):
        # TODO falta por hacer
        pass

    async def execute_acl_qp_aas_protocol(self, smia_instance_id, requested_aas_ref):
        """
        This method executes the FIPA-ACL QP interaction protocol (Query Protocol), to query an AAS element to a given
        SMIA instance.

        Args:
            smia_instance_id (str): identifier of SMIA instance to be the requested.
            requested_aas_ref (str): reference of the AAS element to be queried.

        Returns:
            object: returns the queried AAS element content.
        """
        # TODO falta por hacer
        pass

    async def execute_acl_cnp_protocol(self, smia_instance_ids):
        """
        This method executes the FIPA-ACL CNP interaction protocol (Contract Net Protocol), to obtain the best option among several.

        Args:
            smia_instance_ids (list): list with all the identifiers of SMIA instances to be the participants of the protocol.

        Returns:
            str, str: returns the asset identifier and the SMIA instance identifier of the best option.
        """
        # TODO falta por hacer
        pass

    async def execute_acl_rp_css_protocol(self, smia_instance_id, capability, skill, constraints=None, skill_parameters=None):
        """
        This method executes the FIPA-ACL RP interaction protocol (Request Protocol), to request the execution of
        an CSS-based capability.

        Args:
            smia_instance_id (str): identifier of SMIA instance to be the requested.
            capability (str): IRI of the capability to be requested
            skill (str): IRI of the skill to be requested
            constraints (list): IRIs of the constraints with their values
            skill_parameters (list): IRIs of the skill_parameters with their values

        Returns:
            object: returns the response content.
        """
        # TODO falta por hacer
        pass