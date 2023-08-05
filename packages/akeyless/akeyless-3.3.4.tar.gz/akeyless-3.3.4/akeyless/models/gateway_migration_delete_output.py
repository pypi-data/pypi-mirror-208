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


class GatewayMigrationDeleteOutput(object):
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
        'migration_id': 'str'
    }

    attribute_map = {
        'migration_id': 'migration_id'
    }

    def __init__(self, migration_id=None, local_vars_configuration=None):  # noqa: E501
        """GatewayMigrationDeleteOutput - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._migration_id = None
        self.discriminator = None

        if migration_id is not None:
            self.migration_id = migration_id

    @property
    def migration_id(self):
        """Gets the migration_id of this GatewayMigrationDeleteOutput.  # noqa: E501


        :return: The migration_id of this GatewayMigrationDeleteOutput.  # noqa: E501
        :rtype: str
        """
        return self._migration_id

    @migration_id.setter
    def migration_id(self, migration_id):
        """Sets the migration_id of this GatewayMigrationDeleteOutput.


        :param migration_id: The migration_id of this GatewayMigrationDeleteOutput.  # noqa: E501
        :type: str
        """

        self._migration_id = migration_id

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
        if not isinstance(other, GatewayMigrationDeleteOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GatewayMigrationDeleteOutput):
            return True

        return self.to_dict() != other.to_dict()
