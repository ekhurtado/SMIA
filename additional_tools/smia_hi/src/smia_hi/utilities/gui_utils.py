import logging
import ntpath
import os

from aiohttp import web
from smia import GeneralUtils

_logger = logging.getLogger(__name__)




class GUIControllers:
    """This class contains all the controller to be added to SMIA in order to manage the operator actions."""

    def __init__(self, agent_object):
        self.myagent = agent_object


    @staticmethod
    async def hello_controller(request):
        """
        Generic controller during the request of SMIA GUI webpages via HTTP GET call.
        """
        return {"status": "OK"}

    async def smia_hi_gui_get_controller(self, request):
        """
        The controller during the request of SMIA PE Dashboard.
        """
        return {"status": "success"}

    async def smia_hi_task_done_controller(self, request):
        """
        The controller during the request of SMIA PE Dashboard.
        """
        data = await request.json()

        # First, the taskID is obtained and is used to remove the information from the received task dictionary
        task_id = data.get("TaskID", None)
        if task_id is None:
            return {"status": "error", "message": "Task ID is missing"}
        self.myagent.received_css_tasks.pop(task_id)

        # Then, the information is saved in completed task dictionary
        self.myagent.completed_css_tasks[task_id + '-done'] = {'capName': data.get("capName"),
                                                     'requestedTime': data.get("requestedTime"),
                                                     'completedTime': str(GeneralUtils.get_current_date_time()),
                                                     'constraints': data.get("constraints", None),
                                                     'skillParams': data.get("skillParams")}

        return {'status': 'success'}
        # return web.json_response({'status': 'success'})
        # return {"status": "success", "reason": "success reason"}

class GUIFeatures:
    """This class contains the methods related to SPADE web interface customization."""
    # FAVICON_PATH = './htmls/static/SMIA_favicon.ico' # TODO BORRAR
    FAVICON_PATH = '/htmls/static/SMIA_favicon.ico'

    @staticmethod
    async def add_new_menu_entry(agent, entry_name, entry_url, entry_icon):
        """
        This method adds a new entry to the SPADE web interface menu.

        Args:
            agent (smia.agents.smia_agent.SMIAAgent): SMIA SPADE agent object.
            entry_name (str): name of the new entry.
            entry_url (str): url to access the new entry.
            entry_icon (str): icon identifier from Font Awesome collection.
        """
        # The menu entry is added with the SPADE web module
        agent.web.add_menu_entry(entry_name, entry_url, entry_icon)

        # Then, the information is added to the attribute with the dictionary in the agent, so that it is accessible
        # to HTML templates.
        agent.web_menu_entries[entry_name] = {"url": entry_url, "icon": entry_icon}

    @staticmethod
    async def handle_favicon(request):
        """
        This method represents the controller that will handle the requests when the Favicon is requested.

        Args:
            request: request object to get the favicon file.

        Returns:
            web.FileResponse: response to the web browser.
        """
        favicon_path = os.path.join(GUIFeatures.FAVICON_PATH)
        return web.FileResponse(GUIFeatures.FAVICON_PATH)

    @staticmethod
    async def add_custom_favicon(agent):
        """
        This method adds a custom Favicon to the SMIA GUI.

        Args:
            agent (spade.agent.Agent): SMIA SPADE agent object.
        """
        # The favicon is accessed with an HTTP request to a specific URL, and needs a controller
        agent.web.app.router.add_get('/favicon.ico', GUIFeatures.handle_favicon)
        # The static folder also need to be added to static files view.
        favicon_folder_path = ntpath.split(GUIFeatures.FAVICON_PATH)[0]
        agent.web.app.router.add_static('/static/', path=favicon_folder_path)

    @staticmethod
    def build_avatar_url(jid: str) -> str:
        """
        This method overrides the original SPADE method to use the Favicon as the avatar in SMIA SPADE web interface.
        """
        return '/favicon.ico'

