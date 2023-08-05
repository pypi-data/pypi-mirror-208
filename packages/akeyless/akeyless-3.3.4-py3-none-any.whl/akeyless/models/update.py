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


class Update(object):
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
        'artifact_repository': 'str',
        'json': 'bool',
        'show_changelog': 'bool',
        'version': 'str'
    }

    attribute_map = {
        'artifact_repository': 'artifact-repository',
        'json': 'json',
        'show_changelog': 'show-changelog',
        'version': 'version'
    }

    def __init__(self, artifact_repository=None, json=False, show_changelog=None, version='latest', local_vars_configuration=None):  # noqa: E501
        """Update - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._artifact_repository = None
        self._json = None
        self._show_changelog = None
        self._version = None
        self.discriminator = None

        if artifact_repository is not None:
            self.artifact_repository = artifact_repository
        if json is not None:
            self.json = json
        if show_changelog is not None:
            self.show_changelog = show_changelog
        if version is not None:
            self.version = version

    @property
    def artifact_repository(self):
        """Gets the artifact_repository of this Update.  # noqa: E501

        Alternative CLI repository url. e.g. https://artifacts.site2.akeyless.io  # noqa: E501

        :return: The artifact_repository of this Update.  # noqa: E501
        :rtype: str
        """
        return self._artifact_repository

    @artifact_repository.setter
    def artifact_repository(self, artifact_repository):
        """Sets the artifact_repository of this Update.

        Alternative CLI repository url. e.g. https://artifacts.site2.akeyless.io  # noqa: E501

        :param artifact_repository: The artifact_repository of this Update.  # noqa: E501
        :type: str
        """

        self._artifact_repository = artifact_repository

    @property
    def json(self):
        """Gets the json of this Update.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this Update.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this Update.

        Set output format to JSON  # noqa: E501

        :param json: The json of this Update.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def show_changelog(self):
        """Gets the show_changelog of this Update.  # noqa: E501

        Show the changelog between the current version and the latest one and exit (update will not be performed)  # noqa: E501

        :return: The show_changelog of this Update.  # noqa: E501
        :rtype: bool
        """
        return self._show_changelog

    @show_changelog.setter
    def show_changelog(self, show_changelog):
        """Sets the show_changelog of this Update.

        Show the changelog between the current version and the latest one and exit (update will not be performed)  # noqa: E501

        :param show_changelog: The show_changelog of this Update.  # noqa: E501
        :type: bool
        """

        self._show_changelog = show_changelog

    @property
    def version(self):
        """Gets the version of this Update.  # noqa: E501

        The CLI version  # noqa: E501

        :return: The version of this Update.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Update.

        The CLI version  # noqa: E501

        :param version: The version of this Update.  # noqa: E501
        :type: str
        """

        self._version = version

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
        if not isinstance(other, Update):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Update):
            return True

        return self.to_dict() != other.to_dict()
