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


class GatewayUpdateProducerGithub(object):
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
        'delete_protection': 'str',
        'github_app_id': 'int',
        'github_app_private_key': 'str',
        'github_base_url': 'str',
        'installation_id': 'int',
        'installation_repository': 'str',
        'json': 'bool',
        'name': 'str',
        'new_name': 'str',
        'target_name': 'str',
        'token': 'str',
        'token_permissions': 'list[str]',
        'token_repositories': 'list[str]',
        'uid_token': 'str'
    }

    attribute_map = {
        'delete_protection': 'delete_protection',
        'github_app_id': 'github-app-id',
        'github_app_private_key': 'github-app-private-key',
        'github_base_url': 'github-base-url',
        'installation_id': 'installation-id',
        'installation_repository': 'installation-repository',
        'json': 'json',
        'name': 'name',
        'new_name': 'new-name',
        'target_name': 'target-name',
        'token': 'token',
        'token_permissions': 'token-permissions',
        'token_repositories': 'token-repositories',
        'uid_token': 'uid-token'
    }

    def __init__(self, delete_protection=None, github_app_id=None, github_app_private_key=None, github_base_url='https://api.github.com/', installation_id=None, installation_repository=None, json=False, name=None, new_name=None, target_name=None, token=None, token_permissions=None, token_repositories=None, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """GatewayUpdateProducerGithub - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._delete_protection = None
        self._github_app_id = None
        self._github_app_private_key = None
        self._github_base_url = None
        self._installation_id = None
        self._installation_repository = None
        self._json = None
        self._name = None
        self._new_name = None
        self._target_name = None
        self._token = None
        self._token_permissions = None
        self._token_repositories = None
        self._uid_token = None
        self.discriminator = None

        if delete_protection is not None:
            self.delete_protection = delete_protection
        if github_app_id is not None:
            self.github_app_id = github_app_id
        if github_app_private_key is not None:
            self.github_app_private_key = github_app_private_key
        if github_base_url is not None:
            self.github_base_url = github_base_url
        if installation_id is not None:
            self.installation_id = installation_id
        if installation_repository is not None:
            self.installation_repository = installation_repository
        if json is not None:
            self.json = json
        self.name = name
        if new_name is not None:
            self.new_name = new_name
        if target_name is not None:
            self.target_name = target_name
        if token is not None:
            self.token = token
        if token_permissions is not None:
            self.token_permissions = token_permissions
        if token_repositories is not None:
            self.token_repositories = token_repositories
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def delete_protection(self):
        """Gets the delete_protection of this GatewayUpdateProducerGithub.  # noqa: E501

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :return: The delete_protection of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._delete_protection

    @delete_protection.setter
    def delete_protection(self, delete_protection):
        """Sets the delete_protection of this GatewayUpdateProducerGithub.

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :param delete_protection: The delete_protection of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._delete_protection = delete_protection

    @property
    def github_app_id(self):
        """Gets the github_app_id of this GatewayUpdateProducerGithub.  # noqa: E501

        Github app id  # noqa: E501

        :return: The github_app_id of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: int
        """
        return self._github_app_id

    @github_app_id.setter
    def github_app_id(self, github_app_id):
        """Sets the github_app_id of this GatewayUpdateProducerGithub.

        Github app id  # noqa: E501

        :param github_app_id: The github_app_id of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: int
        """

        self._github_app_id = github_app_id

    @property
    def github_app_private_key(self):
        """Gets the github_app_private_key of this GatewayUpdateProducerGithub.  # noqa: E501

        App private key  # noqa: E501

        :return: The github_app_private_key of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._github_app_private_key

    @github_app_private_key.setter
    def github_app_private_key(self, github_app_private_key):
        """Sets the github_app_private_key of this GatewayUpdateProducerGithub.

        App private key  # noqa: E501

        :param github_app_private_key: The github_app_private_key of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._github_app_private_key = github_app_private_key

    @property
    def github_base_url(self):
        """Gets the github_base_url of this GatewayUpdateProducerGithub.  # noqa: E501

        Base URL  # noqa: E501

        :return: The github_base_url of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._github_base_url

    @github_base_url.setter
    def github_base_url(self, github_base_url):
        """Sets the github_base_url of this GatewayUpdateProducerGithub.

        Base URL  # noqa: E501

        :param github_base_url: The github_base_url of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._github_base_url = github_base_url

    @property
    def installation_id(self):
        """Gets the installation_id of this GatewayUpdateProducerGithub.  # noqa: E501

        Github app installation id  # noqa: E501

        :return: The installation_id of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: int
        """
        return self._installation_id

    @installation_id.setter
    def installation_id(self, installation_id):
        """Sets the installation_id of this GatewayUpdateProducerGithub.

        Github app installation id  # noqa: E501

        :param installation_id: The installation_id of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: int
        """

        self._installation_id = installation_id

    @property
    def installation_repository(self):
        """Gets the installation_repository of this GatewayUpdateProducerGithub.  # noqa: E501

        Repository that the app installation has access to  # noqa: E501

        :return: The installation_repository of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._installation_repository

    @installation_repository.setter
    def installation_repository(self, installation_repository):
        """Sets the installation_repository of this GatewayUpdateProducerGithub.

        Repository that the app installation has access to  # noqa: E501

        :param installation_repository: The installation_repository of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._installation_repository = installation_repository

    @property
    def json(self):
        """Gets the json of this GatewayUpdateProducerGithub.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this GatewayUpdateProducerGithub.

        Set output format to JSON  # noqa: E501

        :param json: The json of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def name(self):
        """Gets the name of this GatewayUpdateProducerGithub.  # noqa: E501

        Producer name  # noqa: E501

        :return: The name of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GatewayUpdateProducerGithub.

        Producer name  # noqa: E501

        :param name: The name of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def new_name(self):
        """Gets the new_name of this GatewayUpdateProducerGithub.  # noqa: E501

        Producer name  # noqa: E501

        :return: The new_name of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._new_name

    @new_name.setter
    def new_name(self, new_name):
        """Sets the new_name of this GatewayUpdateProducerGithub.

        Producer name  # noqa: E501

        :param new_name: The new_name of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._new_name = new_name

    @property
    def target_name(self):
        """Gets the target_name of this GatewayUpdateProducerGithub.  # noqa: E501

        Target name  # noqa: E501

        :return: The target_name of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """Sets the target_name of this GatewayUpdateProducerGithub.

        Target name  # noqa: E501

        :param target_name: The target_name of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._target_name = target_name

    @property
    def token(self):
        """Gets the token of this GatewayUpdateProducerGithub.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this GatewayUpdateProducerGithub.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def token_permissions(self):
        """Gets the token_permissions of this GatewayUpdateProducerGithub.  # noqa: E501

        Optional - installation token's allowed permissions  # noqa: E501

        :return: The token_permissions of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: list[str]
        """
        return self._token_permissions

    @token_permissions.setter
    def token_permissions(self, token_permissions):
        """Sets the token_permissions of this GatewayUpdateProducerGithub.

        Optional - installation token's allowed permissions  # noqa: E501

        :param token_permissions: The token_permissions of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: list[str]
        """

        self._token_permissions = token_permissions

    @property
    def token_repositories(self):
        """Gets the token_repositories of this GatewayUpdateProducerGithub.  # noqa: E501

        Optional - installation token's allowed repositories  # noqa: E501

        :return: The token_repositories of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: list[str]
        """
        return self._token_repositories

    @token_repositories.setter
    def token_repositories(self, token_repositories):
        """Sets the token_repositories of this GatewayUpdateProducerGithub.

        Optional - installation token's allowed repositories  # noqa: E501

        :param token_repositories: The token_repositories of this GatewayUpdateProducerGithub.  # noqa: E501
        :type: list[str]
        """

        self._token_repositories = token_repositories

    @property
    def uid_token(self):
        """Gets the uid_token of this GatewayUpdateProducerGithub.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this GatewayUpdateProducerGithub.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this GatewayUpdateProducerGithub.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this GatewayUpdateProducerGithub.  # noqa: E501
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
        if not isinstance(other, GatewayUpdateProducerGithub):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GatewayUpdateProducerGithub):
            return True

        return self.to_dict() != other.to_dict()
