import logging

from spade.behaviour import OneShotBehaviour

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

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("BPMNPerformerBehaviour starting...")

        # TODO here the BPMN file need to be obtained from the associated AAS

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # This behavior analyzes and performs a BPMN production plan based on CSS. The behavior is OneShot so it will
        # perform the plan and terminate itself. When requests need to be made to other SMIA instances it will remain
        # blocked until the response for this message arrives. A complementary Cyclic behavior has been developed to
        # receive all messages and unblock this behavior to continue with the production plan.
        print("Reading BPMN... Executing each step...")