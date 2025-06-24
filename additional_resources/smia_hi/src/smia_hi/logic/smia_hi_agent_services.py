import asyncio
import logging

from smia import GeneralUtils
from smia.logic import acl_smia_messages_utils

_logger = logging.getLogger(__name__)

class SMIAHIAgentServices:

    def __init__(self, agent_object):
        """
        The constructor method adds the object of the agent to have access to its information.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        self.services_map = {
            'HumanTransportGUI': self.human_transport_gui,
            'VisuallyInspectGUI': self.visually_inspect_gui,

        }  #: This object maps the service identifiers with its associated execution methods

    async def human_transport_gui(self, Initial, Final):
        _logger.info("Running the transport service using the human through SPADE web GUI")
        # First, a new received CSS task will be added in the GUI Agent
        random_task_id = await acl_smia_messages_utils.create_random_thread(self.myagent)
        self.myagent.received_css_tasks[random_task_id] = {
            'capName': 'Transportation', 'requestedTime': str(GeneralUtils.get_current_date_time()),
            'skillParams': {'Initial': Initial, 'Final': Final}
        }

        # Then, it will wait until the task is completed
        while random_task_id + '-done' not in self.myagent.completed_css_tasks:
            await asyncio.sleep(1)  # wait for 1 second
        # Here the task has been completed, so it will return OK
        return {'status': 'success'}


    async def visually_inspect_gui(self):
        # TODO
        _logger.info("Running the transport service using the human through SPADE web GUI")
        # First, a new received CSS task will be added in the GUI Agent
        random_task_id = await acl_smia_messages_utils.create_random_thread(self.myagent)
        self.myagent.received_css_tasks[random_task_id] = {
            'capName': 'VisualInspection', 'requestedTime': str(GeneralUtils.get_current_date_time())
        }

        # Then, it will wait until the task is completed
        while random_task_id + '-done' not in self.myagent.completed_css_tasks:
            await asyncio.sleep(1)  # wait for 1 second
        # Here the task has been completed, so it will return OK
        return {'status': 'success'}

