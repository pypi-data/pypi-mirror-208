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


class CreateEventForwarder(object):
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
        'admin_name': 'str',
        'admin_pwd': 'str',
        'comment': 'str',
        'description': 'str',
        'email_to': 'str',
        'event_source_locations': 'list[str]',
        'event_source_type': 'str',
        'event_types': 'list[str]',
        'every': 'str',
        'forwarder_type': 'str',
        'host': 'str',
        'json': 'bool',
        'key': 'str',
        'name': 'str',
        'runner_type': 'str',
        'token': 'str',
        'uid_token': 'str'
    }

    attribute_map = {
        'admin_name': 'admin-name',
        'admin_pwd': 'admin-pwd',
        'comment': 'comment',
        'description': 'description',
        'email_to': 'email-to',
        'event_source_locations': 'event-source-locations',
        'event_source_type': 'event-source-type',
        'event_types': 'event-types',
        'every': 'every',
        'forwarder_type': 'forwarder-type',
        'host': 'host',
        'json': 'json',
        'key': 'key',
        'name': 'name',
        'runner_type': 'runner-type',
        'token': 'token',
        'uid_token': 'uid-token'
    }

    def __init__(self, admin_name=None, admin_pwd=None, comment=None, description=None, email_to=None, event_source_locations=None, event_source_type='item', event_types=None, every=None, forwarder_type=None, host=None, json=False, key=None, name=None, runner_type=None, token=None, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """CreateEventForwarder - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._admin_name = None
        self._admin_pwd = None
        self._comment = None
        self._description = None
        self._email_to = None
        self._event_source_locations = None
        self._event_source_type = None
        self._event_types = None
        self._every = None
        self._forwarder_type = None
        self._host = None
        self._json = None
        self._key = None
        self._name = None
        self._runner_type = None
        self._token = None
        self._uid_token = None
        self.discriminator = None

        if admin_name is not None:
            self.admin_name = admin_name
        if admin_pwd is not None:
            self.admin_pwd = admin_pwd
        if comment is not None:
            self.comment = comment
        if description is not None:
            self.description = description
        if email_to is not None:
            self.email_to = email_to
        self.event_source_locations = event_source_locations
        if event_source_type is not None:
            self.event_source_type = event_source_type
        if event_types is not None:
            self.event_types = event_types
        if every is not None:
            self.every = every
        self.forwarder_type = forwarder_type
        if host is not None:
            self.host = host
        if json is not None:
            self.json = json
        if key is not None:
            self.key = key
        self.name = name
        self.runner_type = runner_type
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def admin_name(self):
        """Gets the admin_name of this CreateEventForwarder.  # noqa: E501

        Workstation Admin Name  # noqa: E501

        :return: The admin_name of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._admin_name

    @admin_name.setter
    def admin_name(self, admin_name):
        """Sets the admin_name of this CreateEventForwarder.

        Workstation Admin Name  # noqa: E501

        :param admin_name: The admin_name of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._admin_name = admin_name

    @property
    def admin_pwd(self):
        """Gets the admin_pwd of this CreateEventForwarder.  # noqa: E501

        Workstation Admin password  # noqa: E501

        :return: The admin_pwd of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._admin_pwd

    @admin_pwd.setter
    def admin_pwd(self, admin_pwd):
        """Sets the admin_pwd of this CreateEventForwarder.

        Workstation Admin password  # noqa: E501

        :param admin_pwd: The admin_pwd of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._admin_pwd = admin_pwd

    @property
    def comment(self):
        """Gets the comment of this CreateEventForwarder.  # noqa: E501

        Deprecated - use description  # noqa: E501

        :return: The comment of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """Sets the comment of this CreateEventForwarder.

        Deprecated - use description  # noqa: E501

        :param comment: The comment of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._comment = comment

    @property
    def description(self):
        """Gets the description of this CreateEventForwarder.  # noqa: E501

        Description of the object  # noqa: E501

        :return: The description of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateEventForwarder.

        Description of the object  # noqa: E501

        :param description: The description of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def email_to(self):
        """Gets the email_to of this CreateEventForwarder.  # noqa: E501

        A comma seperated list of email addresses to send event to (relevant only for \\\"email\\\" Event Forwarder)  # noqa: E501

        :return: The email_to of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._email_to

    @email_to.setter
    def email_to(self, email_to):
        """Sets the email_to of this CreateEventForwarder.

        A comma seperated list of email addresses to send event to (relevant only for \\\"email\\\" Event Forwarder)  # noqa: E501

        :param email_to: The email_to of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._email_to = email_to

    @property
    def event_source_locations(self):
        """Gets the event_source_locations of this CreateEventForwarder.  # noqa: E501

        Event sources  # noqa: E501

        :return: The event_source_locations of this CreateEventForwarder.  # noqa: E501
        :rtype: list[str]
        """
        return self._event_source_locations

    @event_source_locations.setter
    def event_source_locations(self, event_source_locations):
        """Sets the event_source_locations of this CreateEventForwarder.

        Event sources  # noqa: E501

        :param event_source_locations: The event_source_locations of this CreateEventForwarder.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and event_source_locations is None:  # noqa: E501
            raise ValueError("Invalid value for `event_source_locations`, must not be `None`")  # noqa: E501

        self._event_source_locations = event_source_locations

    @property
    def event_source_type(self):
        """Gets the event_source_type of this CreateEventForwarder.  # noqa: E501

        Event Source type [item, target]  # noqa: E501

        :return: The event_source_type of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._event_source_type

    @event_source_type.setter
    def event_source_type(self, event_source_type):
        """Sets the event_source_type of this CreateEventForwarder.

        Event Source type [item, target]  # noqa: E501

        :param event_source_type: The event_source_type of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._event_source_type = event_source_type

    @property
    def event_types(self):
        """Gets the event_types of this CreateEventForwarder.  # noqa: E501

        Event types  # noqa: E501

        :return: The event_types of this CreateEventForwarder.  # noqa: E501
        :rtype: list[str]
        """
        return self._event_types

    @event_types.setter
    def event_types(self, event_types):
        """Sets the event_types of this CreateEventForwarder.

        Event types  # noqa: E501

        :param event_types: The event_types of this CreateEventForwarder.  # noqa: E501
        :type: list[str]
        """

        self._event_types = event_types

    @property
    def every(self):
        """Gets the every of this CreateEventForwarder.  # noqa: E501

        Rate of periodic runner repetition in hours  # noqa: E501

        :return: The every of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._every

    @every.setter
    def every(self, every):
        """Sets the every of this CreateEventForwarder.

        Rate of periodic runner repetition in hours  # noqa: E501

        :param every: The every of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._every = every

    @property
    def forwarder_type(self):
        """Gets the forwarder_type of this CreateEventForwarder.  # noqa: E501


        :return: The forwarder_type of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._forwarder_type

    @forwarder_type.setter
    def forwarder_type(self, forwarder_type):
        """Sets the forwarder_type of this CreateEventForwarder.


        :param forwarder_type: The forwarder_type of this CreateEventForwarder.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and forwarder_type is None:  # noqa: E501
            raise ValueError("Invalid value for `forwarder_type`, must not be `None`")  # noqa: E501

        self._forwarder_type = forwarder_type

    @property
    def host(self):
        """Gets the host of this CreateEventForwarder.  # noqa: E501

        Workstation Host  # noqa: E501

        :return: The host of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """Sets the host of this CreateEventForwarder.

        Workstation Host  # noqa: E501

        :param host: The host of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._host = host

    @property
    def json(self):
        """Gets the json of this CreateEventForwarder.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this CreateEventForwarder.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this CreateEventForwarder.

        Set output format to JSON  # noqa: E501

        :param json: The json of this CreateEventForwarder.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def key(self):
        """Gets the key of this CreateEventForwarder.  # noqa: E501

        The name of a key that used to encrypt the EventForwarder secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :return: The key of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this CreateEventForwarder.

        The name of a key that used to encrypt the EventForwarder secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :param key: The key of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def name(self):
        """Gets the name of this CreateEventForwarder.  # noqa: E501

        EventForwarder name  # noqa: E501

        :return: The name of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateEventForwarder.

        EventForwarder name  # noqa: E501

        :param name: The name of this CreateEventForwarder.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def runner_type(self):
        """Gets the runner_type of this CreateEventForwarder.  # noqa: E501


        :return: The runner_type of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._runner_type

    @runner_type.setter
    def runner_type(self, runner_type):
        """Sets the runner_type of this CreateEventForwarder.


        :param runner_type: The runner_type of this CreateEventForwarder.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and runner_type is None:  # noqa: E501
            raise ValueError("Invalid value for `runner_type`, must not be `None`")  # noqa: E501

        self._runner_type = runner_type

    @property
    def token(self):
        """Gets the token of this CreateEventForwarder.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this CreateEventForwarder.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this CreateEventForwarder.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this CreateEventForwarder.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this CreateEventForwarder.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this CreateEventForwarder.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this CreateEventForwarder.  # noqa: E501
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
        if not isinstance(other, CreateEventForwarder):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateEventForwarder):
            return True

        return self.to_dict() != other.to_dict()
