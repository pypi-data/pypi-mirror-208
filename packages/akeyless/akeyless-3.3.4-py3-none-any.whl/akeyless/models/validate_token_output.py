# coding: utf-8

"""
    Akeyless API

    The purpose of this application is to provide access to Akeyless API.  # noqa: E501

    The version of the OpenAPI document: 2.0
    Contact: support@akeyless.io
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from akeyless.configuration import Configuration


class ValidateTokenOutput(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'expiration': 'str',
        'is_valid': 'bool',
        'reason': 'str'
    }

    attribute_map = {
        'expiration': 'expiration',
        'is_valid': 'is_valid',
        'reason': 'reason'
    }

    def __init__(self, expiration=None, is_valid=None, reason=None, local_vars_configuration=None):  # noqa: E501
        """ValidateTokenOutput - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._expiration = None
        self._is_valid = None
        self._reason = None
        self.discriminator = None

        if expiration is not None:
            self.expiration = expiration
        if is_valid is not None:
            self.is_valid = is_valid
        if reason is not None:
            self.reason = reason

    @property
    def expiration(self):
        """Gets the expiration of this ValidateTokenOutput.  # noqa: E501


        :return: The expiration of this ValidateTokenOutput.  # noqa: E501
        :rtype: str
        """
        return self._expiration

    @expiration.setter
    def expiration(self, expiration):
        """Sets the expiration of this ValidateTokenOutput.


        :param expiration: The expiration of this ValidateTokenOutput.  # noqa: E501
        :type: str
        """

        self._expiration = expiration

    @property
    def is_valid(self):
        """Gets the is_valid of this ValidateTokenOutput.  # noqa: E501


        :return: The is_valid of this ValidateTokenOutput.  # noqa: E501
        :rtype: bool
        """
        return self._is_valid

    @is_valid.setter
    def is_valid(self, is_valid):
        """Sets the is_valid of this ValidateTokenOutput.


        :param is_valid: The is_valid of this ValidateTokenOutput.  # noqa: E501
        :type: bool
        """

        self._is_valid = is_valid

    @property
    def reason(self):
        """Gets the reason of this ValidateTokenOutput.  # noqa: E501


        :return: The reason of this ValidateTokenOutput.  # noqa: E501
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """Sets the reason of this ValidateTokenOutput.


        :param reason: The reason of this ValidateTokenOutput.  # noqa: E501
        :type: str
        """

        self._reason = reason

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ValidateTokenOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ValidateTokenOutput):
            return True

        return self.to_dict() != other.to_dict()
