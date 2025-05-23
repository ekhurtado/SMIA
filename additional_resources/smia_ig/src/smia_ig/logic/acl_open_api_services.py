import logging

_logger = logging.getLogger(__name__)

class ACLOpenAPIServices:
    """
    This class implements the logic of all the ACL-OpenAPI services.
    """

    @staticmethod
    def printeo():
        _logger.aclinfo("KAIXO---------------------")



    ACLOpenAPIServicesMap = {
        'printeo': printeo
    }  #: This object maps the service identifiers with its associated execution methods