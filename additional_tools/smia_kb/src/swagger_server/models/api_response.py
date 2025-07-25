# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict  # noqa: F401

from swagger_server import util
from swagger_server.models.base_model_ import Model


class ApiResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, code: int=None, type: str=None, message: str=None):  # noqa: E501
        """ApiResponse - a model defined in Swagger

        :param code: The code of this ApiResponse.  # noqa: E501
        :type code: int
        :param type: The type of this ApiResponse.  # noqa: E501
        :type type: str
        :param message: The message of this ApiResponse.  # noqa: E501
        :type message: str
        """
        self.swagger_types = {
            'code': int,
            'type': str,
            'message': str
        }

        self.attribute_map = {
            'code': 'code',
            'type': 'type',
            'message': 'message'
        }
        self._code = code
        self._type = type
        self._message = message

    @classmethod
    def from_dict(cls, dikt) -> 'ApiResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiResponse of this ApiResponse.  # noqa: E501
        :rtype: ApiResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self) -> int:
        """Gets the code of this ApiResponse.


        :return: The code of this ApiResponse.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code: int):
        """Sets the code of this ApiResponse.


        :param code: The code of this ApiResponse.
        :type code: int
        """

        self._code = code

    @property
    def type(self) -> str:
        """Gets the type of this ApiResponse.


        :return: The type of this ApiResponse.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this ApiResponse.


        :param type: The type of this ApiResponse.
        :type type: str
        """

        self._type = type

    @property
    def message(self) -> str:
        """Gets the message of this ApiResponse.


        :return: The message of this ApiResponse.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this ApiResponse.


        :param message: The message of this ApiResponse.
        :type message: str
        """

        self._message = message
