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


class CreateSecret(object):
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
        'accessibility': 'str',
        'delete_protection': 'str',
        'description': 'str',
        'json': 'bool',
        'metadata': 'str',
        'multiline_value': 'bool',
        'name': 'str',
        'password_manager_custom_field': 'dict(str, str)',
        'password_manager_inject_url': 'list[str]',
        'password_manager_password': 'str',
        'password_manager_username': 'str',
        'protection_key': 'str',
        'secure_access_bastion_issuer': 'str',
        'secure_access_enable': 'str',
        'secure_access_host': 'list[str]',
        'secure_access_rdp_user': 'str',
        'secure_access_ssh_creds': 'str',
        'secure_access_ssh_user': 'str',
        'secure_access_url': 'str',
        'secure_access_web_browsing': 'bool',
        'secure_access_web_proxy': 'bool',
        'tags': 'list[str]',
        'token': 'str',
        'type': 'str',
        'uid_token': 'str',
        'value': 'str'
    }

    attribute_map = {
        'accessibility': 'accessibility',
        'delete_protection': 'delete_protection',
        'description': 'description',
        'json': 'json',
        'metadata': 'metadata',
        'multiline_value': 'multiline_value',
        'name': 'name',
        'password_manager_custom_field': 'password-manager-custom-field',
        'password_manager_inject_url': 'password-manager-inject-url',
        'password_manager_password': 'password-manager-password',
        'password_manager_username': 'password-manager-username',
        'protection_key': 'protection_key',
        'secure_access_bastion_issuer': 'secure-access-bastion-issuer',
        'secure_access_enable': 'secure-access-enable',
        'secure_access_host': 'secure-access-host',
        'secure_access_rdp_user': 'secure-access-rdp-user',
        'secure_access_ssh_creds': 'secure-access-ssh-creds',
        'secure_access_ssh_user': 'secure-access-ssh-user',
        'secure_access_url': 'secure-access-url',
        'secure_access_web_browsing': 'secure-access-web-browsing',
        'secure_access_web_proxy': 'secure-access-web-proxy',
        'tags': 'tags',
        'token': 'token',
        'type': 'type',
        'uid_token': 'uid-token',
        'value': 'value'
    }

    def __init__(self, accessibility='regular', delete_protection=None, description=None, json=False, metadata=None, multiline_value=None, name=None, password_manager_custom_field=None, password_manager_inject_url=None, password_manager_password=None, password_manager_username=None, protection_key=None, secure_access_bastion_issuer=None, secure_access_enable=None, secure_access_host=None, secure_access_rdp_user=None, secure_access_ssh_creds=None, secure_access_ssh_user=None, secure_access_url=None, secure_access_web_browsing=False, secure_access_web_proxy=False, tags=None, token=None, type='generic', uid_token=None, value=None, local_vars_configuration=None):  # noqa: E501
        """CreateSecret - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._accessibility = None
        self._delete_protection = None
        self._description = None
        self._json = None
        self._metadata = None
        self._multiline_value = None
        self._name = None
        self._password_manager_custom_field = None
        self._password_manager_inject_url = None
        self._password_manager_password = None
        self._password_manager_username = None
        self._protection_key = None
        self._secure_access_bastion_issuer = None
        self._secure_access_enable = None
        self._secure_access_host = None
        self._secure_access_rdp_user = None
        self._secure_access_ssh_creds = None
        self._secure_access_ssh_user = None
        self._secure_access_url = None
        self._secure_access_web_browsing = None
        self._secure_access_web_proxy = None
        self._tags = None
        self._token = None
        self._type = None
        self._uid_token = None
        self._value = None
        self.discriminator = None

        if accessibility is not None:
            self.accessibility = accessibility
        if delete_protection is not None:
            self.delete_protection = delete_protection
        if description is not None:
            self.description = description
        if json is not None:
            self.json = json
        if metadata is not None:
            self.metadata = metadata
        if multiline_value is not None:
            self.multiline_value = multiline_value
        self.name = name
        if password_manager_custom_field is not None:
            self.password_manager_custom_field = password_manager_custom_field
        if password_manager_inject_url is not None:
            self.password_manager_inject_url = password_manager_inject_url
        if password_manager_password is not None:
            self.password_manager_password = password_manager_password
        if password_manager_username is not None:
            self.password_manager_username = password_manager_username
        if protection_key is not None:
            self.protection_key = protection_key
        if secure_access_bastion_issuer is not None:
            self.secure_access_bastion_issuer = secure_access_bastion_issuer
        if secure_access_enable is not None:
            self.secure_access_enable = secure_access_enable
        if secure_access_host is not None:
            self.secure_access_host = secure_access_host
        if secure_access_rdp_user is not None:
            self.secure_access_rdp_user = secure_access_rdp_user
        if secure_access_ssh_creds is not None:
            self.secure_access_ssh_creds = secure_access_ssh_creds
        if secure_access_ssh_user is not None:
            self.secure_access_ssh_user = secure_access_ssh_user
        if secure_access_url is not None:
            self.secure_access_url = secure_access_url
        if secure_access_web_browsing is not None:
            self.secure_access_web_browsing = secure_access_web_browsing
        if secure_access_web_proxy is not None:
            self.secure_access_web_proxy = secure_access_web_proxy
        if tags is not None:
            self.tags = tags
        if token is not None:
            self.token = token
        if type is not None:
            self.type = type
        if uid_token is not None:
            self.uid_token = uid_token
        self.value = value

    @property
    def accessibility(self):
        """Gets the accessibility of this CreateSecret.  # noqa: E501

        for personal password manager  # noqa: E501

        :return: The accessibility of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._accessibility

    @accessibility.setter
    def accessibility(self, accessibility):
        """Sets the accessibility of this CreateSecret.

        for personal password manager  # noqa: E501

        :param accessibility: The accessibility of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._accessibility = accessibility

    @property
    def delete_protection(self):
        """Gets the delete_protection of this CreateSecret.  # noqa: E501

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :return: The delete_protection of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._delete_protection

    @delete_protection.setter
    def delete_protection(self, delete_protection):
        """Sets the delete_protection of this CreateSecret.

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :param delete_protection: The delete_protection of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._delete_protection = delete_protection

    @property
    def description(self):
        """Gets the description of this CreateSecret.  # noqa: E501

        Description of the object  # noqa: E501

        :return: The description of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateSecret.

        Description of the object  # noqa: E501

        :param description: The description of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def json(self):
        """Gets the json of this CreateSecret.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this CreateSecret.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this CreateSecret.

        Set output format to JSON  # noqa: E501

        :param json: The json of this CreateSecret.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def metadata(self):
        """Gets the metadata of this CreateSecret.  # noqa: E501

        Deprecated - use description  # noqa: E501

        :return: The metadata of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this CreateSecret.

        Deprecated - use description  # noqa: E501

        :param metadata: The metadata of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._metadata = metadata

    @property
    def multiline_value(self):
        """Gets the multiline_value of this CreateSecret.  # noqa: E501

        The provided value is a multiline value (separated by '\\n')  # noqa: E501

        :return: The multiline_value of this CreateSecret.  # noqa: E501
        :rtype: bool
        """
        return self._multiline_value

    @multiline_value.setter
    def multiline_value(self, multiline_value):
        """Sets the multiline_value of this CreateSecret.

        The provided value is a multiline value (separated by '\\n')  # noqa: E501

        :param multiline_value: The multiline_value of this CreateSecret.  # noqa: E501
        :type: bool
        """

        self._multiline_value = multiline_value

    @property
    def name(self):
        """Gets the name of this CreateSecret.  # noqa: E501

        Secret name  # noqa: E501

        :return: The name of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateSecret.

        Secret name  # noqa: E501

        :param name: The name of this CreateSecret.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def password_manager_custom_field(self):
        """Gets the password_manager_custom_field of this CreateSecret.  # noqa: E501

        For Password Management use, additional fields  # noqa: E501

        :return: The password_manager_custom_field of this CreateSecret.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._password_manager_custom_field

    @password_manager_custom_field.setter
    def password_manager_custom_field(self, password_manager_custom_field):
        """Sets the password_manager_custom_field of this CreateSecret.

        For Password Management use, additional fields  # noqa: E501

        :param password_manager_custom_field: The password_manager_custom_field of this CreateSecret.  # noqa: E501
        :type: dict(str, str)
        """

        self._password_manager_custom_field = password_manager_custom_field

    @property
    def password_manager_inject_url(self):
        """Gets the password_manager_inject_url of this CreateSecret.  # noqa: E501

        For Password Management use, reflect the website context  # noqa: E501

        :return: The password_manager_inject_url of this CreateSecret.  # noqa: E501
        :rtype: list[str]
        """
        return self._password_manager_inject_url

    @password_manager_inject_url.setter
    def password_manager_inject_url(self, password_manager_inject_url):
        """Sets the password_manager_inject_url of this CreateSecret.

        For Password Management use, reflect the website context  # noqa: E501

        :param password_manager_inject_url: The password_manager_inject_url of this CreateSecret.  # noqa: E501
        :type: list[str]
        """

        self._password_manager_inject_url = password_manager_inject_url

    @property
    def password_manager_password(self):
        """Gets the password_manager_password of this CreateSecret.  # noqa: E501

        For Password Management use, additional fields  # noqa: E501

        :return: The password_manager_password of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._password_manager_password

    @password_manager_password.setter
    def password_manager_password(self, password_manager_password):
        """Sets the password_manager_password of this CreateSecret.

        For Password Management use, additional fields  # noqa: E501

        :param password_manager_password: The password_manager_password of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._password_manager_password = password_manager_password

    @property
    def password_manager_username(self):
        """Gets the password_manager_username of this CreateSecret.  # noqa: E501

        For Password Management use  # noqa: E501

        :return: The password_manager_username of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._password_manager_username

    @password_manager_username.setter
    def password_manager_username(self, password_manager_username):
        """Sets the password_manager_username of this CreateSecret.

        For Password Management use  # noqa: E501

        :param password_manager_username: The password_manager_username of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._password_manager_username = password_manager_username

    @property
    def protection_key(self):
        """Gets the protection_key of this CreateSecret.  # noqa: E501

        The name of a key that used to encrypt the secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :return: The protection_key of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._protection_key

    @protection_key.setter
    def protection_key(self, protection_key):
        """Sets the protection_key of this CreateSecret.

        The name of a key that used to encrypt the secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :param protection_key: The protection_key of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._protection_key = protection_key

    @property
    def secure_access_bastion_issuer(self):
        """Gets the secure_access_bastion_issuer of this CreateSecret.  # noqa: E501

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :return: The secure_access_bastion_issuer of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_bastion_issuer

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, secure_access_bastion_issuer):
        """Sets the secure_access_bastion_issuer of this CreateSecret.

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :param secure_access_bastion_issuer: The secure_access_bastion_issuer of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_bastion_issuer = secure_access_bastion_issuer

    @property
    def secure_access_enable(self):
        """Gets the secure_access_enable of this CreateSecret.  # noqa: E501

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :return: The secure_access_enable of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_enable

    @secure_access_enable.setter
    def secure_access_enable(self, secure_access_enable):
        """Sets the secure_access_enable of this CreateSecret.

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :param secure_access_enable: The secure_access_enable of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_enable = secure_access_enable

    @property
    def secure_access_host(self):
        """Gets the secure_access_host of this CreateSecret.  # noqa: E501

        Target servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers)  # noqa: E501

        :return: The secure_access_host of this CreateSecret.  # noqa: E501
        :rtype: list[str]
        """
        return self._secure_access_host

    @secure_access_host.setter
    def secure_access_host(self, secure_access_host):
        """Sets the secure_access_host of this CreateSecret.

        Target servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers)  # noqa: E501

        :param secure_access_host: The secure_access_host of this CreateSecret.  # noqa: E501
        :type: list[str]
        """

        self._secure_access_host = secure_access_host

    @property
    def secure_access_rdp_user(self):
        """Gets the secure_access_rdp_user of this CreateSecret.  # noqa: E501

        Remote Desktop Username  # noqa: E501

        :return: The secure_access_rdp_user of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_rdp_user

    @secure_access_rdp_user.setter
    def secure_access_rdp_user(self, secure_access_rdp_user):
        """Sets the secure_access_rdp_user of this CreateSecret.

        Remote Desktop Username  # noqa: E501

        :param secure_access_rdp_user: The secure_access_rdp_user of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_rdp_user = secure_access_rdp_user

    @property
    def secure_access_ssh_creds(self):
        """Gets the secure_access_ssh_creds of this CreateSecret.  # noqa: E501

        Static-Secret values contains SSH Credentials, either Private Key or Password [password/private-key]  # noqa: E501

        :return: The secure_access_ssh_creds of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_ssh_creds

    @secure_access_ssh_creds.setter
    def secure_access_ssh_creds(self, secure_access_ssh_creds):
        """Sets the secure_access_ssh_creds of this CreateSecret.

        Static-Secret values contains SSH Credentials, either Private Key or Password [password/private-key]  # noqa: E501

        :param secure_access_ssh_creds: The secure_access_ssh_creds of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_ssh_creds = secure_access_ssh_creds

    @property
    def secure_access_ssh_user(self):
        """Gets the secure_access_ssh_user of this CreateSecret.  # noqa: E501

        Override the SSH username as indicated in SSH Certificate Issuer  # noqa: E501

        :return: The secure_access_ssh_user of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_ssh_user

    @secure_access_ssh_user.setter
    def secure_access_ssh_user(self, secure_access_ssh_user):
        """Sets the secure_access_ssh_user of this CreateSecret.

        Override the SSH username as indicated in SSH Certificate Issuer  # noqa: E501

        :param secure_access_ssh_user: The secure_access_ssh_user of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_ssh_user = secure_access_ssh_user

    @property
    def secure_access_url(self):
        """Gets the secure_access_url of this CreateSecret.  # noqa: E501

        Destination URL to inject secrets  # noqa: E501

        :return: The secure_access_url of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_url

    @secure_access_url.setter
    def secure_access_url(self, secure_access_url):
        """Sets the secure_access_url of this CreateSecret.

        Destination URL to inject secrets  # noqa: E501

        :param secure_access_url: The secure_access_url of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._secure_access_url = secure_access_url

    @property
    def secure_access_web_browsing(self):
        """Gets the secure_access_web_browsing of this CreateSecret.  # noqa: E501

        Secure browser via Akeyless Web Access Bastion  # noqa: E501

        :return: The secure_access_web_browsing of this CreateSecret.  # noqa: E501
        :rtype: bool
        """
        return self._secure_access_web_browsing

    @secure_access_web_browsing.setter
    def secure_access_web_browsing(self, secure_access_web_browsing):
        """Sets the secure_access_web_browsing of this CreateSecret.

        Secure browser via Akeyless Web Access Bastion  # noqa: E501

        :param secure_access_web_browsing: The secure_access_web_browsing of this CreateSecret.  # noqa: E501
        :type: bool
        """

        self._secure_access_web_browsing = secure_access_web_browsing

    @property
    def secure_access_web_proxy(self):
        """Gets the secure_access_web_proxy of this CreateSecret.  # noqa: E501

        Web-Proxy via Akeyless Web Access Bastion  # noqa: E501

        :return: The secure_access_web_proxy of this CreateSecret.  # noqa: E501
        :rtype: bool
        """
        return self._secure_access_web_proxy

    @secure_access_web_proxy.setter
    def secure_access_web_proxy(self, secure_access_web_proxy):
        """Sets the secure_access_web_proxy of this CreateSecret.

        Web-Proxy via Akeyless Web Access Bastion  # noqa: E501

        :param secure_access_web_proxy: The secure_access_web_proxy of this CreateSecret.  # noqa: E501
        :type: bool
        """

        self._secure_access_web_proxy = secure_access_web_proxy

    @property
    def tags(self):
        """Gets the tags of this CreateSecret.  # noqa: E501

        Add tags attached to this object  # noqa: E501

        :return: The tags of this CreateSecret.  # noqa: E501
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this CreateSecret.

        Add tags attached to this object  # noqa: E501

        :param tags: The tags of this CreateSecret.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def token(self):
        """Gets the token of this CreateSecret.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this CreateSecret.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def type(self):
        """Gets the type of this CreateSecret.  # noqa: E501

        The secret sub type [generic/password]  # noqa: E501

        :return: The type of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this CreateSecret.

        The secret sub type [generic/password]  # noqa: E501

        :param type: The type of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def uid_token(self):
        """Gets the uid_token of this CreateSecret.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this CreateSecret.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this CreateSecret.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def value(self):
        """Gets the value of this CreateSecret.  # noqa: E501

        The secret value  # noqa: E501

        :return: The value of this CreateSecret.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this CreateSecret.

        The secret value  # noqa: E501

        :param value: The value of this CreateSecret.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and value is None:  # noqa: E501
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

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
        if not isinstance(other, CreateSecret):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateSecret):
            return True

        return self.to_dict() != other.to_dict()
