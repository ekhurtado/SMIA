import logging
from collections import OrderedDict

from spade.behaviour import OneShotBehaviour

from utilities.gui_utils import GUIFeatures, GUIControllers

_logger = logging.getLogger(__name__)

class SMIAHIGUIBehaviour(OneShotBehaviour):
    """
    This behavior handles the web interface for the SMIA HI and its GUI related resources (HTML web pages and
    drivers).
    """

    async def run(self) -> None:
        # First, the dictionary is initialized to add the menu entries that are required in runtime. The name of the
        # SMIA SPADE agent is also initialized to be used in the added HTMLs templates
        self.agent.web_menu_entries = OrderedDict()
        self.agent.build_avatar_url = GUIFeatures.build_avatar_url

        # The dictionaries related to the HTML webpage are also initialized
        self.agent.received_css_tasks = {}
        self.agent.completed_css_tasks = {}

        # TODO BORRAR
        # self.agent.received_css_tasks['taskID2154'] = {'capName': 'Transport', 'requestedTime': '24/06/2025 11:54',
        #                                                'constraints': {'Weight': '1 kg'}, 'skillParams': {'Initial': 'warehouse', 'Final': 'PB'}}
        # self.agent.received_css_tasks['taskID8763'] = {'capName': 'Transport', 'requestedTime': '24/06/2025 11:54',
        #                                                'constraints': {'Weight': '1 kg'}, 'skillParams': {'Initial': 'warehouse', 'Final': 'PB'}}
        # self.agent.received_css_tasks['taskID5433'] = {'capName': 'Transport', 'requestedTime': '24/06/2025 11:54',
        #                                                'constraints': {'Weight': '1 kg'}, 'skillParams': {'Initial': 'warehouse', 'Final': 'PB'}}
        # self.agent.completed_css_tasks['taskID2154-done'] = {'capName': 'Transport', 'requestedTime': '24/06/2025 11:54',
        #                                                 'completedTime': '24/06/2025 11:58',
        #                                                'constraints': {'Weight': '1 kg'},
        #                                                'skillParams': {'Initial': 'warehouse', 'Final': 'PB'}}
        # TODO FIN BORRAR

        _logger.info("SMIA SPADE web interface required resources initialized.")

        # The SMIA icon is added as the avatar of the GUI
        await GUIFeatures.add_custom_favicon(self.agent)
        _logger.info("Added SMIA Favicon to the web interface.")

        # The controllers class is also created offering the agent object
        self.operator_gui_controllers = GUIControllers(self.agent)
        # Then, the required HTML webpages are added to the SMIA SPADE web module
        self.agent.web.add_get('/smia_hi_dashboard', self.operator_gui_controllers.smia_hi_gui_get_controller,
                               '/htmls/smia_hi_dashboard.html')
        self.agent.web.add_post('/smia_hi_dashboard', self.operator_gui_controllers.smia_hi_task_done_controller, None)

        # The new webpages need also to be added in the manu of the web interface
        # await GUIFeatures.add_new_menu_entry(self.agent,'System view', '/system_view', 'fa fa-eye')
        self.agent.web.add_menu_entry("SMIA HI Dashboard", "/smia_hi_dashboard", "fa fa-user-cog")
        _logger.info("Added new web pages to the web interface.")

        # Once all the configuration is done, the web interface is enabled in the SMIA SPADE agent
        self.agent.web.start(hostname="0.0.0.0", port="20000")
        _logger.info("Started SMIA HI SPADE web interface.")
