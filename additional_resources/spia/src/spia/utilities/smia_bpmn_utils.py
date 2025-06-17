import asyncio
import logging
import re

from SpiffWorkflow.bpmn.specs.defaults import EndEvent, ExclusiveGateway, StartEvent
from SpiffWorkflow.bpmn.specs.defaults import ServiceTask

from utilities.smia_bpmn_info import SMIABPMNInfo

_logger = logging.getLogger(__name__)

class SMIABPMNUtils:

    # Methods related to the BPMN file
    # --------------------------------

    @staticmethod
    def get_process_parser(bpmn_parser):
        """
        This method gets the process parser from the BPMN parser.

        Args:
            bpmn_parser (SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser): BPMN parser instance.

        Returns:

        """
        # It is always analyzed the first process
        process_id = bpmn_parser.get_process_ids()[0]
        return bpmn_parser.get_process_parser(process_id)

    @staticmethod
    def get_node_smia_attrib(node, attrib_name):
        """
        This method gets the node smia attrib from the XML node.

        Args:
            node: XML node object.
            attrib_name (str): name of the attribute

        Returns:
            value of the attribute.
        """
        prefix = '{' + node.nsmap.get('smia') + '}'
        return node.attrib.get(f'{prefix}{attrib_name}')

    @staticmethod
    def add_smia_attributes_values(process_parser):
        """
        This method adds all the values of the SMIA attributes required to be set in the BPMN file. The

        Args:
            process_parser (SpiffWorkflow.bpmn.parser.ProcessParser): BPMN process parser instance.
        """
        # First, the attributes values of the Service Tasks are added
        SMIABPMNUtils.add_smia_service_tasks_attributes_values(process_parser)

        # Then, the attributes values of the Gateways are added
        SMIABPMNUtils.add_smia_gateways_attributes_values(process_parser)

        _logger.assetinfo("All SMIA attributes values have been added to the process parser objects.")


    @staticmethod
    def add_smia_service_tasks_attributes_values(process_parser):
        """
        This method adds all the values of the SMIA attributes required to be set in the ServiceTasks defined in the
        BPMN file.

        Args:
            process_parser (SpiffWorkflow.bpmn.parser.ProcessParser): BPMN process parser instance.
        """
        service_task_node_list = process_parser.xpath(f"./{SMIABPMNInfo.BPMN_SERVICE_TASK_XML_TAG}")
        for node in service_task_node_list:
            for spec_name, spec_instance in process_parser.get_spec().task_specs.items():
                # Let's find the spec instance associated to each node
                if node.get('id') == spec_name:
                    spec_instance.smia_capability = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_CAPABILITY_ATTRIBUTE)
                    spec_instance.smia_skill = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_SKILL_ATTRIBUTE)
                    spec_instance.smia_skill_parameters = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_SKILL_PARAMETERS_ATTRIBUTE)
                    spec_instance.smia_constraints = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_CAPABILITY_CONSTRAINTS_ATTRIBUTE)
                    spec_instance.smia_asset = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_ASSET_ATTRIBUTE)

                    spec_instance.smia_request_to_previous = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_REQUEST_PREVIOUS_ATTRIBUTE)
                    spec_instance.smia_request_to_following = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.SERVICE_TASK_REQUEST_FOLLOWING_ATTRIBUTE)

                    # The obtained data will be processed in order to be more accessible
                    if spec_instance.smia_skill_parameters is not None:
                        spec_instance.smia_skill_parameters = SMIABPMNUtils.get_json_from_string(
                            spec_instance.smia_skill_parameters)
                    if spec_instance.smia_constraints is not None:
                        spec_instance.smia_constraints = SMIABPMNUtils.get_json_from_string(
                            spec_instance.smia_constraints)
                    if spec_instance.smia_request_to_previous is not None:
                        spec_instance.smia_request_to_previous = SMIABPMNUtils.get_requested_data_json_list(
                            spec_instance.smia_request_to_previous)
                    if spec_instance.smia_request_to_following is not None:
                        spec_instance.smia_request_to_following = SMIABPMNUtils.get_requested_data_json_list(
                            spec_instance.smia_request_to_following)

                    # Now the possible additional tasks will be obtained
                    additional_tasks = []
                    if spec_instance.smia_asset is None:
                        # An asset has not been specified, so this task need to request a distributed CNP protocol
                        additional_tasks.append(SMIABPMNInfo.TASK_REQUEST_DISTRIBUTED_CNP)
                    # TODO: recoger el ID de instancia del activo se hace en un metodo del BPMN performer
                    # elif spec_instance.smia_asset is not None:
                    #
                    #     print(
                    #         "\t\t Since an asset has been specified, it will be requested for its associated SMIA instance to the SMIA KB.")
                    #     print("\t\t ...")
                    #     spec_instance.smia_instance = 'smiainstance' + spec_instance.bpmn_name  # TODO BORRAR (se ha hecho manualmente)
                    #     print("\t\t SMIA instance: {}".format(spec_instance.smia_instance))
                    if spec_instance.smia_request_to_previous is not None:
                        # This ServiceTask needs a data from the previous ServiceTask of the flow
                        additional_tasks.append(SMIABPMNInfo.TASK_REQUEST_DATA_TO_PREVIOUS)
                    if spec_instance.smia_request_to_following is not None:
                        # This ServiceTask needs a data from the following ServiceTask of the flow
                        additional_tasks.append(SMIABPMNInfo.TASK_REQUEST_DATA_TO_FOLLOWING)
                    spec_instance.smia_additional_tasks = additional_tasks

    @staticmethod
    def add_smia_gateways_attributes_values(process_parser):
        """
        This method adds all the values of the SMIA attributes required to be set in the Gateways defined in the
        BPMN file.

        Args:
            process_parser (SpiffWorkflow.bpmn.parser.ProcessParser): BPMN process parser instance.
        """
        exclusive_gateway_node_list = process_parser.xpath(f"./{SMIABPMNInfo.BPMN_GATEWAY_XML_TAG}")
        for node in exclusive_gateway_node_list:
            for spec_name, spec_instance in process_parser.get_spec().task_specs.items():
                if node.get('id') == spec_name:
                    spec_instance.timeout_value = SMIABPMNUtils.get_node_smia_attrib(
                        node, SMIABPMNInfo.GATEWAY_TIMEOUT_ATTRIBUTE)

                    if hasattr(spec_instance, 'timeout_value') and spec_instance.timeout_value != 0:
                        # This ExclusiveGateway needs to be checked with a timeout in the previous element
                        previous_element = SMIABPMNUtils.get_previous_bpmn_element(process_parser, spec_instance)
                        previous_element.smia_additional_tasks.append(SMIABPMNInfo.TASK_CHECK_TIMEOUT)
                        previous_element.timeout_value = getattr(spec_instance, 'timeout_value')

    # Methods related to the BPMN workflow
    # ------------------------------------
    @staticmethod
    def get_previous_bpmn_element(process_parser, current_elem):
        for bpmn_name, bpmn_elem in process_parser.get_spec().task_specs.items():
            if current_elem in bpmn_elem.outputs:  # Como se trabajan con flujos simples siempre se escoge el primero de los siguientes outputs
                return bpmn_elem
        return None

    @staticmethod
    def get_next_bpmn_element(process_parser, current_elem):

        if isinstance(current_elem, EndEvent):
            return None
        else:
            # The element is remove as the current execution step
            if hasattr(current_elem, 'current_exec_elem'):
                delattr(current_elem, 'current_exec_elem')

            if isinstance(current_elem, ExclusiveGateway):
                previous_element = SMIABPMNUtils.get_previous_bpmn_element(process_parser, current_elem)
                for condition, following_element_id in current_elem.cond_task_specs:
                    if condition.args[0].lower() in ('yes', 'true', 't', '1') and previous_element.smia_timeout_reached:
                        print(
                            "The condition \"YES\" of the Timeout gateway has been met (so the timeout has been reached).")
                        return SMIABPMNUtils.get_bpmn_element_by_id(process_parser, following_element_id)
                    if condition.args[0].lower() in ('no', 'false', 'f', '0') and not previous_element.smia_timeout_reached:
                        print(
                            "The condition \"NO\" of the Timeout gateway has been met (so the timeout has not been reached).")
                        return SMIABPMNUtils.get_bpmn_element_by_id(process_parser, following_element_id)
                return None
            else:
                for bpmn_name, bpmn_elem in process_parser.get_spec().task_specs.items():
                    if bpmn_elem == current_elem.outputs[0]:
                        # Como se trabajan con flujos simples siempre se escoge el primero de los siguientes outputs
                        # TODO PENSAR SI SE QUIERE AÑADIR GESTION DE FLUJOS COMPLEJOS: habria que pensar una forma de manejar en
                        #  paralelo multiples tasks. Por ejemplo, se podrian crear comportamientos SPADE de la misma forma que
                        #  SMIA, usando la naturaleza asincrona para manejar en paralelo.
                        return bpmn_elem

    @staticmethod
    def get_bpmn_element_by_id(process_parser, bpmn_element_id):
        for current_name, current_elem in process_parser.get_spec().task_specs.items():
            if current_elem.bpmn_id == bpmn_element_id:
                return current_elem
        return None

    @staticmethod
    def get_bpmn_element_smia_instance_by_asset_id(process_parser, asset_id):
        for current_name, current_elem in process_parser.get_spec().task_specs.items():
            if hasattr(current_elem, 'smia_asset') and hasattr(current_elem, 'smia_instance'):
                if current_elem.smia_asset == asset_id:
                    return current_elem.smia_instance
        return None

    @staticmethod
    def get_required_data_from_bpmn_element(bpmn_element, requested_element):
        match requested_element['elementType']:
            case 'SkillParameter':
                attribute_to_get = 'smia_skill_parameters'
            case 'Constraint':
                attribute_to_get = 'smia_constraints'
            case _:
                # This case is not available
                return

        for param_name, param_value in getattr(bpmn_element, attribute_to_get).items():
            if param_name == requested_element['attrib']:
                return getattr(bpmn_element, attribute_to_get)[param_name]
        return None

    @staticmethod
    def update_bpmn_element_with_requested_data(bpmn_element, requested_element, data_value):
        attribute_to_update = None
        match requested_element['elementType']:
            case 'SkillParameter':
                attribute_to_update = 'smia_skill_parameters'
            case 'Constraint':
                attribute_to_update = 'smia_constraints'
            case _:
                # This case is not available
                return

        for param_name, param_value in getattr(bpmn_element, attribute_to_update).items():
            if param_name == requested_element['attrib']:
                print(
                    "Hay que actualizar el [{}] desde el viejo valor [{}] con el nuevo [{}]".format(param_name,
                                                                                                    param_value,
                                                                                                    data_value))
                getattr(bpmn_element, attribute_to_update)[param_name] = data_value
        return bpmn_element

    @staticmethod
    def get_bpmn_display_name(bpmn_element):
        if isinstance(bpmn_element, ServiceTask):
            if bpmn_element.smia_capability is not None:
                # Let's get the name from the Capability IRI
                return bpmn_element.smia_capability.split('#')[1]
        if isinstance(bpmn_element, ExclusiveGateway):
            if hasattr(bpmn_element, 'timeout_value') and bpmn_element.timeout_value != 0:
                return f"Timeout {bpmn_element.timeout_value}s"
        if isinstance(bpmn_element, StartEvent):
            return "Start"
        if isinstance(bpmn_element, EndEvent):
            return "End"
        return bpmn_element.bpmn_name


    # Methods related to the BPMN SMIA attribute values format
    # --------------------------------------------------------
    @staticmethod
    def get_json_from_string(content_string):
        json_object = {}
        for param_data in content_string.split(';'):
            param_name, param_value = param_data.split('=')
            json_object[param_name] = param_value
        return json_object

    @staticmethod
    def get_requested_data_json_list(requested_data_string):
        requested_data_json_list = []
        for request_data in requested_data_string.split(';'):
            try:
                match = re.fullmatch(SMIABPMNInfo.REQUEST_DATA_SPLIT_PATTERN, request_data)
                if match:
                    elem_type, attrib = match.groups()
                    requested_data_json_list.append({'elementType': elem_type, 'attrib': attrib})
                else:
                    raise ValueError("String format is incorrect for requested data {}. Expected format: "
                                     "'Element[attribute]'".format(requested_data_string))
            except ValueError:
                _logger.warning("The requested data in BPMN {} is not in a valid format.".format(requested_data_string))
        return requested_data_json_list


    @staticmethod
    async def perform_bpmn_timeout_check(agent_object, msg_thread, timeout_value):
        """
        This method performs a timeout for an execution of a BPMN element. As the BPMNPerformerBehaviour will be waiting
         for the response ACL message, in case of reaching the timeout value, it will check if the behaviour is still
         waiting (ACL response has not received, so the BPMN element has not finished), and if true it will unlock the
         BPMNPerformerBehaviour setting as response data ('ERROR: Timeout reached').

         Args:
             agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
             msg_thread (str): thread of the ACL message
             timeout_value: value of the timeout to be check
        """
        # Para usar este metodo habra que añadir esto justo antes de solicitar ejecutar la capacidad que tenga definido un timeout
        # asyncio.create_task(SMIABPMNUtils.perform_bpmn_timeout_check())
        await asyncio.sleep(float(timeout_value))
        for behaviour in agent_object.behaviours:
                if str(behaviour.__class__.__name__) == 'BPMNPerformerBehaviour':
                    for thread, content in behaviour.acl_messages_responses.items():
                        if thread == msg_thread and content is None:
                            # In this case the ACL response has not received, so the timeout has been reached before the
                            # BPMN element has finished
                            _logger.warning(f"Timeout reached of {timeout_value} seconds for ACL thread {msg_thread}")
                            behaviour.acl_messages_responses[thread] = "ERROR: TIMEOUT REACHED"
                            # The behaviour is also unlocked
                            behaviour.acl_request_event.set()
                            _logger.info("BPMNPerformerBehaviour unlocked by the timeout management method.")