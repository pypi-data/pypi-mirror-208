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


class CreateRabbitMQTarget(object):
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
        'comment': 'str',
        'description': 'str',
        'json': 'bool',
        'key': 'str',
        'name': 'str',
        'rabbitmq_server_password': 'str',
        'rabbitmq_server_uri': 'str',
        'rabbitmq_server_user': 'str',
        'token': 'str',
        'uid_token': 'str'
    }

    attribute_map = {
        'comment': 'comment',
        'description': 'description',
        'json': 'json',
        'key': 'key',
        'name': 'name',
        'rabbitmq_server_password': 'rabbitmq-server-password',
        'rabbitmq_server_uri': 'rabbitmq-server-uri',
        'rabbitmq_server_user': 'rabbitmq-server-user',
        'token': 'token',
        'uid_token': 'uid-token'
    }

    def __init__(self, comment=None, description=None, json=False, key=None, name=None, rabbitmq_server_password=None, rabbitmq_server_uri=None, rabbitmq_server_user=None, token=None, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """CreateRabbitMQTarget - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._comment = None
        self._description = None
        self._json = None
        self._key = None
        self._name = None
        self._rabbitmq_server_password = None
        self._rabbitmq_server_uri = None
        self._rabbitmq_server_user = None
        self._token = None
        self._uid_token = None
        self.discriminator = None

        if comment is not None:
            self.comment = comment
        if description is not None:
            self.description = description
        if json is not None:
            self.json = json
        if key is not None:
            self.key = key
        self.name = name
        if rabbitmq_server_password is not None:
            self.rabbitmq_server_password = rabbitmq_server_password
        if rabbitmq_server_uri is not None:
            self.rabbitmq_server_uri = rabbitmq_server_uri
        if rabbitmq_server_user is not None:
            self.rabbitmq_server_user = rabbitmq_server_user
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def comment(self):
        """Gets the comment of this CreateRabbitMQTarget.  # noqa: E501

        Deprecated - use description  # noqa: E501

        :return: The comment of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """Sets the comment of this CreateRabbitMQTarget.

        Deprecated - use description  # noqa: E501

        :param comment: The comment of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._comment = comment

    @property
    def description(self):
        """Gets the description of this CreateRabbitMQTarget.  # noqa: E501

        Description of the object  # noqa: E501

        :return: The description of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateRabbitMQTarget.

        Description of the object  # noqa: E501

        :param description: The description of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def json(self):
        """Gets the json of this CreateRabbitMQTarget.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this CreateRabbitMQTarget.

        Set output format to JSON  # noqa: E501

        :param json: The json of this CreateRabbitMQTarget.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def key(self):
        """Gets the key of this CreateRabbitMQTarget.  # noqa: E501

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :return: The key of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this CreateRabbitMQTarget.

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :param key: The key of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def name(self):
        """Gets the name of this CreateRabbitMQTarget.  # noqa: E501

        Target name  # noqa: E501

        :return: The name of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateRabbitMQTarget.

        Target name  # noqa: E501

        :param name: The name of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def rabbitmq_server_password(self):
        """Gets the rabbitmq_server_password of this CreateRabbitMQTarget.  # noqa: E501


        :return: The rabbitmq_server_password of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._rabbitmq_server_password

    @rabbitmq_server_password.setter
    def rabbitmq_server_password(self, rabbitmq_server_password):
        """Sets the rabbitmq_server_password of this CreateRabbitMQTarget.


        :param rabbitmq_server_password: The rabbitmq_server_password of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._rabbitmq_server_password = rabbitmq_server_password

    @property
    def rabbitmq_server_uri(self):
        """Gets the rabbitmq_server_uri of this CreateRabbitMQTarget.  # noqa: E501


        :return: The rabbitmq_server_uri of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._rabbitmq_server_uri

    @rabbitmq_server_uri.setter
    def rabbitmq_server_uri(self, rabbitmq_server_uri):
        """Sets the rabbitmq_server_uri of this CreateRabbitMQTarget.


        :param rabbitmq_server_uri: The rabbitmq_server_uri of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._rabbitmq_server_uri = rabbitmq_server_uri

    @property
    def rabbitmq_server_user(self):
        """Gets the rabbitmq_server_user of this CreateRabbitMQTarget.  # noqa: E501


        :return: The rabbitmq_server_user of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._rabbitmq_server_user

    @rabbitmq_server_user.setter
    def rabbitmq_server_user(self, rabbitmq_server_user):
        """Sets the rabbitmq_server_user of this CreateRabbitMQTarget.


        :param rabbitmq_server_user: The rabbitmq_server_user of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._rabbitmq_server_user = rabbitmq_server_user

    @property
    def token(self):
        """Gets the token of this CreateRabbitMQTarget.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this CreateRabbitMQTarget.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this CreateRabbitMQTarget.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this CreateRabbitMQTarget.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this CreateRabbitMQTarget.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this CreateRabbitMQTarget.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this CreateRabbitMQTarget.  # noqa: E501
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
        if not isinstance(other, CreateRabbitMQTarget):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateRabbitMQTarget):
            return True

        return self.to_dict() != other.to_dict()
