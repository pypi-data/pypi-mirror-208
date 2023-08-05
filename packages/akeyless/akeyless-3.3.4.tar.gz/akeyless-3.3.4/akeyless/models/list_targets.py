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


class ListTargets(object):
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
        'filter': 'str',
        'json': 'bool',
        'pagination_token': 'str',
        'token': 'str',
        'type': 'list[str]',
        'uid_token': 'str'
    }

    attribute_map = {
        'filter': 'filter',
        'json': 'json',
        'pagination_token': 'pagination-token',
        'token': 'token',
        'type': 'type',
        'uid_token': 'uid-token'
    }

    def __init__(self, filter=None, json=False, pagination_token=None, token=None, type=None, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """ListTargets - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._filter = None
        self._json = None
        self._pagination_token = None
        self._token = None
        self._type = None
        self._uid_token = None
        self.discriminator = None

        if filter is not None:
            self.filter = filter
        if json is not None:
            self.json = json
        if pagination_token is not None:
            self.pagination_token = pagination_token
        if token is not None:
            self.token = token
        if type is not None:
            self.type = type
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def filter(self):
        """Gets the filter of this ListTargets.  # noqa: E501

        Filter by auth method name or part of it  # noqa: E501

        :return: The filter of this ListTargets.  # noqa: E501
        :rtype: str
        """
        return self._filter

    @filter.setter
    def filter(self, filter):
        """Sets the filter of this ListTargets.

        Filter by auth method name or part of it  # noqa: E501

        :param filter: The filter of this ListTargets.  # noqa: E501
        :type: str
        """

        self._filter = filter

    @property
    def json(self):
        """Gets the json of this ListTargets.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this ListTargets.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this ListTargets.

        Set output format to JSON  # noqa: E501

        :param json: The json of this ListTargets.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def pagination_token(self):
        """Gets the pagination_token of this ListTargets.  # noqa: E501

        Next page reference  # noqa: E501

        :return: The pagination_token of this ListTargets.  # noqa: E501
        :rtype: str
        """
        return self._pagination_token

    @pagination_token.setter
    def pagination_token(self, pagination_token):
        """Sets the pagination_token of this ListTargets.

        Next page reference  # noqa: E501

        :param pagination_token: The pagination_token of this ListTargets.  # noqa: E501
        :type: str
        """

        self._pagination_token = pagination_token

    @property
    def token(self):
        """Gets the token of this ListTargets.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this ListTargets.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this ListTargets.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this ListTargets.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def type(self):
        """Gets the type of this ListTargets.  # noqa: E501

        The target types list . In case it is empty, all types of targets will be returned. options: [hanadb cassandra aws ssh gke eks mysql mongodb snowflake mssql redshift artifactory azure rabbitmq k8s venafi gcp oracle dockerhub ldap github chef web salesforce postgres]  # noqa: E501

        :return: The type of this ListTargets.  # noqa: E501
        :rtype: list[str]
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ListTargets.

        The target types list . In case it is empty, all types of targets will be returned. options: [hanadb cassandra aws ssh gke eks mysql mongodb snowflake mssql redshift artifactory azure rabbitmq k8s venafi gcp oracle dockerhub ldap github chef web salesforce postgres]  # noqa: E501

        :param type: The type of this ListTargets.  # noqa: E501
        :type: list[str]
        """

        self._type = type

    @property
    def uid_token(self):
        """Gets the uid_token of this ListTargets.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this ListTargets.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this ListTargets.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this ListTargets.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

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
        if not isinstance(other, ListTargets):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListTargets):
            return True

        return self.to_dict() != other.to_dict()
