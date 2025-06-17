import logging
from collections import OrderedDict

import graphviz
from spade.behaviour import OneShotBehaviour

from utilities.gui_utils import GUIFeatures, GUIControllers

_logger = logging.getLogger(__name__)

class SPIAGUIBehaviour(OneShotBehaviour):
    """
    This behavior handles the web interface for the SMIA PE agent and its GUI related resources (HTML web pages and
    drivers).
    """

    async def run(self) -> None:
        # First, the dictionary is initialized to add the menu entries that are required in runtime. The name of the
        # SMIA SPADE agent is also initialized to be used in the added HTMLs templates
        self.agent.web_menu_entries = OrderedDict()
        # self.agent.agent_name = str(self.agent.jid).split('@')[0]  # tambien se puede lograr mediante agent.jid.localpart
        self.agent.build_avatar_url = GUIFeatures.build_avatar_url

        # The dictionaries related to the HTML webpage are also initialized
        self.agent.bpmn_execution_status = True
        self.agent.bpmn_info = {'ServiceTasks': 0, 'ExclusiveGateways': 0, 'Capabilities': 0, 'Skills': 0, 'Assets': 0}
        self.agent.bpmn_graphviz_info = "digraph SMIA_PE_workflow { rankdir=LR; node [fixedsize=true];}"
        self.agent.to_graphviz =  GUIFeatures.to_graphviz

        _logger.info("SMIA SPADE web interface required resources initialized.")

        # The SMIA icon is added as the avatar of the GUI
        await GUIFeatures.add_custom_favicon(self.agent)
        _logger.info("Added SMIA Favicon to the web interface.")

        # The controllers class is also created offering the agent object
        self.operator_gui_controllers = GUIControllers(self.agent)
        # Then, the required HTML webpages are added to the SMIA SPADE web module
        self.agent.web.add_get('/smia_pe_dashboard', self.operator_gui_controllers.spia_gui_get_controller,
                               '/htmls/smia_pe_dashboard.html')
        self.agent.web.add_post('/smia_pe_dashboard', self.operator_gui_controllers.spia_gui_post_controller,
                               None)

        # The new webpages need also to be added in the manu of the web interface
        # await GUIFeatures.add_new_menu_entry(self.agent,'System view', '/system_view', 'fa fa-eye')
        self.agent.web.add_menu_entry("SMIA PE Dashboard", "/smia_pe_dashboard", "fa fa-user-cog")
        _logger.info("Added new web pages to the web interface.")

        # Once all the configuration is done, the web interface is enabled in the SMIA SPADE agent
        self.agent.web.start(hostname="0.0.0.0", port="10000")
        _logger.info("Started SMIA SPADE web interface.")

