import logging

_logger = logging.getLogger(__name__)

class SMIAHIAgentServices:


    @staticmethod
    async def human_transport_gui(Initial, Final):
        # TODO
        _logger.info("Running the transport service using the human through SPADE web GUI")
        pass

    @staticmethod
    async def visually_inspect_gui():
        # TODO
        _logger.info("Running the transport service using the human through SPADE web GUI")
        pass

    SMIAHIAgentServicesMap = {
        'HumanTransportGUI': human_transport_gui,
        'VisuallyInspectGUI': visually_inspect_gui,

    }  #: This object maps the service identifiers with its associated execution methods