import logging

from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)

class ReceiveACLBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA HI will receive from the
    others SMIAs in the I4.0 System.
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
        _logger.info("ReceiveACLBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # This method will receive all ACL messages to the SMIA HI
            _logger.aclinfo("Analyzing ACL message... Checking if it is a message for SMIA HI ... ")
            # TODO
        else:
            _logger.info("         - No message received within 10 seconds on SMIA HI (ReceiveACLBehaviour)")