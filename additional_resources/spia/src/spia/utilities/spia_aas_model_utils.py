import logging
from os import path

from basyx.aas.adapter import aasx
from smia import SMIAGeneralInfo
from smia.utilities import properties_file_utils

_logger = logging.getLogger(__name__)

class SPIAAASModelUtils:

    @staticmethod
    def get_bpmn_file_bytes_from_aas():
        """
        This method gets the BPMN file for SPIA from the AAS model. If the AAS model is within an AASX package, it will
         find inside it.

        Returns:
            obj: the content of the BPMN file in the form of bytes.
        """
        # First, if the AAS model is an AASX package will be analyzed
        aas_model_file_name, aas_model_file_extension = path.splitext(SMIAGeneralInfo.CM_AAS_MODEL_FILENAME)
        if aas_model_file_extension == '.aasx':
            # Since the AAS model is an AASX package, the BPMN file can be obtained from inside it
            # First, it will find all BPMN type files
            bpmn_files_within_aasx = SPIAAASModelUtils.get_all_bpmn_files_bytes_within_aasx()
            if len(bpmn_files_within_aasx) > 1:
                _logger.warning("More than one BPMN file has been added into the AASX package. It need to be established which is the valid one.")
                # TODO: it need to think some mechanism to determine which BPMN file is the valid one (e.g. checking
                #  if it is part of an SkillParameter AAS element or with a specific semantic ID): it is not developed yet
            else:
                return bpmn_files_within_aasx[0]
        else:
            # TODO in this case it would be necessary to request the content of the file to the AAS Repository: it is not developed yet
            print("The AAS model is not an AASX package.")
            return None

    @staticmethod
    def get_all_bpmn_files_bytes_within_aasx():
        """
        This method gets all the files of type BPMN from the AASX package defined as AAS model for the SPIA.

        Returns:
            list: list of all BPMN files content in bytes.
        """
        bpmn_files_bytes = []
        with aasx.AASXReader(properties_file_utils.get_aas_model_filepath()) as aasx_reader:
            for part_name, content_type in aasx_reader.reader.list_parts():
                file_name, file_extension = path.splitext(part_name)
                if file_extension == '.bpmn':
                    bpmn_files_bytes.append(aasx_reader.reader.open_part(part_name).read())
                    break
            else:
                _logger.warning("No BPMN file exists within the AASX Package.")
            return bpmn_files_bytes
