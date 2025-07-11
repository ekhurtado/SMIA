import argparse
import calendar
import logging
import os
import time
from datetime import datetime

from smia.utilities.fipa_acl_info import FIPAACLInfo

import smia
from spade.message import Message
from spade.template import Template

from smia.logic.exceptions import CriticalError
from smia.utilities import properties_file_utils
from smia.utilities.smia_general_info import SMIAGeneralInfo

class GeneralUtils:
    """
    This class contains some general utils to ben used by any module.
    """


    @staticmethod
    def configure_logging():
        """
        This method configures the logging to be used by all modules. It specifies different colors to improve the
        readability of the console and adds new levels to the printouts related to ACL and interaction messages.
        """
        asset_level_num = 35
        fipa_acl_level_num = 36

        if ((logging.getLevelName("ASSETINFO")) == asset_level_num or
                (logging.getLevelName("ACLINFO") == fipa_acl_level_num)):
            # In this case the logging is already configured
            return

        logging.addLevelName(asset_level_num, "ASSETINFO")
        logging.addLevelName(fipa_acl_level_num, "ACLINFO")

        def assetinfo(self, message, *args, **kwargs):
            if self.isEnabledFor(asset_level_num):
                self._log(asset_level_num, message, args, **kwargs)

        logging.Logger.assetinfo = assetinfo

        def aclinfo(self, message, *args, **kwargs):
            if self.isEnabledFor(fipa_acl_level_num):
                self._log(fipa_acl_level_num, message, args, **kwargs)

        logging.Logger.aclinfo = aclinfo

        handler = logging.StreamHandler()
        formatter = GeneralUtils.ColoredFormatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger('').addHandler(handler)
        logging.getLogger('').setLevel(logging.INFO)  # Set the default logging level

        # Create a file handler
        file_handler = logging.FileHandler(SMIAGeneralInfo.LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.SMIA_LOG_FILENAME)
        file_handler.setFormatter(logging.Formatter(GeneralUtils.ColoredFormatter.FORMAT_COMPLEX))
        logging.getLogger('').addHandler(file_handler)

    class ColoredFormatter(logging.Formatter):
        """
        This class contains the format of all the levels of the logging, including the color of each of them.
        """
        FORMAT_SIMPLE = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
        FORMAT_COMPLEX = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s line:%(lineno)d"
        RESET = '\x1b[0m'

        COLORS = {
            logging.DEBUG: '\x1b[94m' + FORMAT_SIMPLE + RESET,  # Blue
            logging.INFO: '\x1b[39;20m' + FORMAT_SIMPLE + RESET,  # White
            logging.WARNING: '\x1b[93m' + FORMAT_COMPLEX + RESET,  # Yellow
            logging.ERROR: '\x1b[91m' + FORMAT_COMPLEX + RESET,  # Red
            logging.CRITICAL: '\x1b[41m' + FORMAT_COMPLEX + RESET,  # White on Red
            35: '\x1b[38;2;255;150;20m' + FORMAT_SIMPLE + RESET,  # Purple (for the interaction level)
            36: '\x1b[38;2;0;255;255m' + FORMAT_SIMPLE + RESET  # Cyan (for the FIP-ACL level)
        }

        def format(self, record):
            log_fmt = self.COLORS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    @staticmethod
    def print_smia_banner():
        """
        This method prints the SMIA banner as a string. The banner has been created with Python 'art' library.
        """
        # The banner for the SMIA is set as string, avoiding installing 'art' library (which has been used to create it)
        banner_str = ("===============================================\n" +
                      "  ______    ____    ____   _____        _\n" +
                      ".' ____ \  |_   \  /   _| |_   _|      / \      \n" +
                      "| (___ \_|   |   \/   |     | |       / _ \     \n" +
                      " _.____`.    | |\  /| |     | |      / ___ \    \n" +
                      "| \____) |  _| |_\/_| |_   _| |_   _/ /   \ \_  \n" +
                      " \______.' |_____||_____| |_____| |____| |____| \n" +
                      # "                                                \n" +
                      "===============================================\n" +
                      f"                                       v{smia.__version__} \n" +
                      "===============================================\n")
        print(banner_str)

    @staticmethod
    def update_aas_model(new_aas_model_file):
        """
        This method updates the AAS model file defined for the SMIA. It updates the global variable for the AAS model
        file name and the value within the properties file of the SMIA Archive.

        Args:
            new_aas_model_file (str): name of the file of the new AAS model to update SMIA.
        """
        # The global variable is updated
        SMIAGeneralInfo.CM_AAS_MODEL_FILENAME = new_aas_model_file

        # The properties file is updated
        file_name, file_ext = os.path.splitext(new_aas_model_file)
        properties_file_utils.set_aas_general_property('model.file', new_aas_model_file)
        properties_file_utils.set_aas_general_property('model.serialization', file_ext)

    @staticmethod
    def create_acl_template(performative=None, ontology=None, thread=None, protocol=None):
        """
        This method creates a template aligned with FIPA-ACL standard.

        Args:
            performative(str): The performative of the ACL message template.
            ontology(str): The ontology of the ACL message template.
            thread(str): The thread of the ACL message template.
            protocol (str): The protocol of the ACL message template.

        Returns:
            spade.template.Template: a SPADE template object.
        """
        custom_template = Template()
        if performative is not None:
            custom_template.set_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB, performative)
        if ontology is not None:
            custom_template.set_metadata(FIPAACLInfo.FIPA_ACL_ONTOLOGY_ATTRIB, ontology)
        if thread is not None:
            custom_template.thread = thread
        if protocol is not None:
            custom_template.set_metadata(FIPAACLInfo.FIPA_ACL_PROTOCOL_ATTRIB, protocol)
        return custom_template

    @staticmethod
    def create_acl_msg(receiver, thread, performative, ontology, body):
        """
        This method creates an FIPA-ACL message.

        Args:
            receiver (str): The SPADE agent receiver of the ACL message.
            thread (str): The thread of the ACL message.:
            performative (str): The performative of the ACL message.
            ontology (str): The ontology of the ACL message.
            body: The body of the ACL message.

        Returns:
            spade.message.Message: SPADE message object FIPA-ACL-compliant.
        """
        msg = Message(to=receiver, thread=thread)
        msg.set_metadata('performative', performative)
        msg.set_metadata('ontology', ontology)

        msg.body = body  # TODO Pensar si iria tambien en metadatos o todo en el body
        return msg

    @staticmethod
    def get_current_timestamp():
        """
        This method returns the current timestamp of the SMIA.

        Returns:
            int: current timestamp in milliseconds
        """
        return calendar.timegm(time.gmtime())

    @staticmethod
    def get_current_timestamp_microsecs():
        """
        This method returns the current timestamp of the SMIA in microseconds.

        Returns:
            int: current timestamp in microseconds
        """
        return time.time()

    @staticmethod
    def get_current_date_time():
        """
        This method returns the current DateTime of the SMIA. The DateTime is obtained from the UNIX timestamp.

        Returns:
            str: current DateTime.
        """
        return datetime.fromtimestamp(GeneralUtils.get_current_timestamp())


class CLIUtils:
    """This class contains utility methods related to the Command Line Interface."""

    @staticmethod
    def get_information_from_cli(cli_args):
        """
        This method gets all the information from the Command Line Interface (CLI). This information includes the
        initial configuration properties or the AAS model or. None of them is mandatory, but they must be consistent
        (i.e., if only the AAS model is offered, it must be an AASX which include the configuration file).

        Args:
            cli_args (list): arguments of the command line interface

        Returns:
            str, str, str: init_config, aas_model and ontology values (None if not specified).
        """
        parser = argparse.ArgumentParser(description='Parser for SMIA CLI arguments')
        parser.add_argument("-m", "--model")
        # parser.add_argument("-o", "--ontology")
        parser.add_argument("-c", "--config")
        parser.add_argument("-a-id", "--aas-id")
        args = parser.parse_args(cli_args)
        return args.config, args.model

    @staticmethod
    def check_and_save_cli_information(init_config, aas_model, aas_id):
        """
        This method checks the information added in the CLI and, depending on the result of the check, it gets the
        necessary information and saves it in the appropriate variable.

        Args:
            init_config (str): path to the initialization configuration properties file.
            aas_model (str): path to the AAS model file.
        """
        # The libraries are imported locally to avoid circular import error
        from smia.aas_model.aas_model_utils import AASModelUtils
        from smia.utilities import smia_archive_utils
        from smia.utilities import properties_file_utils
        import ntpath

        # First, the AAS identifier is saved if it has been set
        if aas_id is not None:
            SMIAGeneralInfo.CM_AAS_ID = aas_id

        if (init_config is None) and (aas_model is None):
            # If all are none, the CLI information is invalid
            raise CriticalError("The CLI information is invalid: no argument has been specified. Please specify at "
                                "least one")
        elif init_config is not None:
            # If the configuration properties file is defined, its variable is updated
            init_config_file_name = ntpath.split(init_config)[1] or ntpath.basename(ntpath.split(init_config)[0])
            SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME = init_config_file_name

            if aas_model is None:
                # If the configuration file is specified, but not the AAS model, the AAS must be defined in the file
                # and obtained from there.
                aas_model_folder_path = properties_file_utils.get_aas_general_property('model.folder')
                aas_model_file_name = properties_file_utils.get_aas_general_property('model.file')
                if (aas_model_file_name is None) or (aas_model_folder_path is None):
                    raise CriticalError("The CLI information is invalid: the AAS model has not been specified either "
                                        "in the CLI or in the configuration properties file.")

                smia_archive_utils.copy_file_into_archive(aas_model_folder_path + '/' + aas_model_file_name,
                                                          SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
                GeneralUtils.update_aas_model(aas_model_file_name)
                # SMIAGeneralInfo.CM_AAS_MODEL_FILENAME = aas_model_file_name

        elif aas_model is not None:
            # If the AAS model file is defined, its variable is updated
            aas_model_file_name = ntpath.split(aas_model)[1] or ntpath.basename(ntpath.split(aas_model)[0])
            GeneralUtils.update_aas_model(aas_model_file_name)
            # SMIAGeneralInfo.CM_AAS_MODEL_FILENAME = aas_model_file_name

            if init_config is None:
                # If the configuration properties file is not defined, it is obtained from inside the AASX package
                if aas_model_file_name.split(".")[1] != 'aasx':
                    # If it is not an AASX package, the configuration file is not specified
                    raise CriticalError("The configuration file is not specified and is not inside the AAS model as it "
                                        "is not an AASX package. Please specify the configuration file or add it to "
                                        "an AASX package and pass it as an AAS model.")
                config_file_path = AASModelUtils.get_configuration_file_path_from_standard_submodel()
                # smia_archive_utils.copy_file_into_archive(config_file_path,
                #                                           SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
                init_config_file_name = ntpath.split(config_file_path)[1] or ntpath.basename(ntpath.split(config_file_path)[0])
                # The file must be obtained from the AASX package
                config_file_bytes = AASModelUtils.get_file_bytes_from_aasx_by_path(config_file_path)
                if config_file_bytes is None:
                    CriticalError("The CLI information is invalid: the initialization configuration file has not "
                                    "been specified either in the CLI or inside the AAS model.")
                with open(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + init_config_file_name,
                          "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(config_file_bytes)
                SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME = init_config_file_name

_logger = logging.getLogger(__name__)

class DockerUtils:
    """This class contains utility methods related to SMIA execution in Docker containers."""

    @staticmethod
    def get_aas_model_from_env_var():
        """
        This method returns the AAS model path, obtained from the required 'AAS_MODEL_NAME' environmental variable.

        Returns:
            str: path to the AAS model to be loaded.
        """
        aas_model_name = os.environ.get('AAS_MODEL_NAME')
        if aas_model_name is None:
            _logger.warning("The environment variable 'AAS_MODEL_NAME' for the AAS model is not set, so check that it "
                            "is not necessary. Please add the information (or the AAS id) and restart the container.")
            return None
        _logger.info('Loaded AAS model: {}'.format(aas_model_name))
        aas_model_path = SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/' + aas_model_name
        return aas_model_path

    @staticmethod
    def get_aas_id_from_env_var():
        """
        This method returns the AAS identifier, obtained from the required 'AAS_ID' environmental variable.

        Returns:
            str: path to the AAS model to be loaded.
        """
        aas_id = os.environ.get('AAS_ID')
        if aas_id is None:
            _logger.warning("The environment variable 'AAS_ID' for the AAS model is not set, so check that it is not "
                            "necessary. Please add the information (or the AAS model path) and restart the container.")
            return None
        _logger.info('Loaded AAS ID: {}'.format(aas_id))
        return aas_id