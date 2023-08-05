# coding: utf-8

"""
    Fabric Orchestrator API

    This is Fabric Orchestrator API  # noqa: E501

    OpenAPI spec version: 1.0.1
    Contact: kthare10@unc.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Status200OkNoContent(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'data': 'list[Status200OkNoContentData]',
        'type': 'str',
        'size': 'int',
        'status': 'int'
    }

    attribute_map = {
        'data': 'data',
        'type': 'type',
        'size': 'size',
        'status': 'status'
    }

    def __init__(self, data=None, type='no_content', size=1, status=200):  # noqa: E501
        """Status200OkNoContent - a model defined in Swagger"""  # noqa: E501
        self._data = None
        self._type = None
        self._size = None
        self._status = None
        self.discriminator = None
        if data is not None:
            self.data = data
        if type is not None:
            self.type = type
        if size is not None:
            self.size = size
        if status is not None:
            self.status = status

    @property
    def data(self):
        """Gets the data of this Status200OkNoContent.  # noqa: E501


        :return: The data of this Status200OkNoContent.  # noqa: E501
        :rtype: list[Status200OkNoContentData]
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this Status200OkNoContent.


        :param data: The data of this Status200OkNoContent.  # noqa: E501
        :type: list[Status200OkNoContentData]
        """

        self._data = data

    @property
    def type(self):
        """Gets the type of this Status200OkNoContent.  # noqa: E501


        :return: The type of this Status200OkNoContent.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Status200OkNoContent.


        :param type: The type of this Status200OkNoContent.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def size(self):
        """Gets the size of this Status200OkNoContent.  # noqa: E501


        :return: The size of this Status200OkNoContent.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this Status200OkNoContent.


        :param size: The size of this Status200OkNoContent.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def status(self):
        """Gets the status of this Status200OkNoContent.  # noqa: E501


        :return: The status of this Status200OkNoContent.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Status200OkNoContent.


        :param status: The status of this Status200OkNoContent.  # noqa: E501
        :type: int
        """

        self._status = status

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Status200OkNoContent, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Status200OkNoContent):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
