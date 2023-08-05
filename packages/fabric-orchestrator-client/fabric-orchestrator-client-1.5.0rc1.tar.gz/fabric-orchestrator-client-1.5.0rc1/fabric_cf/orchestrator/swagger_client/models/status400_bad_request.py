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

class Status400BadRequest(object):
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
        'errors': 'list[Status400BadRequestErrors]'
    }

    attribute_map = {
        'errors': 'errors'
    }

    def __init__(self, errors=None):  # noqa: E501
        """Status400BadRequest - a model defined in Swagger"""  # noqa: E501
        self._errors = None
        self.discriminator = None
        if errors is not None:
            self.errors = errors

    @property
    def errors(self):
        """Gets the errors of this Status400BadRequest.  # noqa: E501


        :return: The errors of this Status400BadRequest.  # noqa: E501
        :rtype: list[Status400BadRequestErrors]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this Status400BadRequest.


        :param errors: The errors of this Status400BadRequest.  # noqa: E501
        :type: list[Status400BadRequestErrors]
        """

        self._errors = errors

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
        if issubclass(Status400BadRequest, dict):
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
        if not isinstance(other, Status400BadRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
