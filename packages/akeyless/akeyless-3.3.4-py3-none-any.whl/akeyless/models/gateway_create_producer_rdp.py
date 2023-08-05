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


class GatewayCreateProducerRdp(object):
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
        'allow_user_extend_session': 'int',
        'delete_protection': 'str',
        'fixed_user_only': 'str',
        'json': 'bool',
        'name': 'str',
        'producer_encryption_key_name': 'str',
        'rdp_admin_name': 'str',
        'rdp_admin_pwd': 'str',
        'rdp_host_name': 'str',
        'rdp_host_port': 'str',
        'rdp_user_groups': 'str',
        'secure_access_allow_external_user': 'bool',
        'secure_access_enable': 'str',
        'secure_access_host': 'list[str]',
        'secure_access_rdp_domain': 'str',
        'secure_access_rdp_user': 'str',
        'tags': 'list[str]',
        'target_name': 'str',
        'token': 'str',
        'uid_token': 'str',
        'user_ttl': 'str',
        'warn_user_before_expiration': 'int'
    }

    attribute_map = {
        'allow_user_extend_session': 'allow-user-extend-session',
        'delete_protection': 'delete_protection',
        'fixed_user_only': 'fixed-user-only',
        'json': 'json',
        'name': 'name',
        'producer_encryption_key_name': 'producer-encryption-key-name',
        'rdp_admin_name': 'rdp-admin-name',
        'rdp_admin_pwd': 'rdp-admin-pwd',
        'rdp_host_name': 'rdp-host-name',
        'rdp_host_port': 'rdp-host-port',
        'rdp_user_groups': 'rdp-user-groups',
        'secure_access_allow_external_user': 'secure-access-allow-external-user',
        'secure_access_enable': 'secure-access-enable',
        'secure_access_host': 'secure-access-host',
        'secure_access_rdp_domain': 'secure-access-rdp-domain',
        'secure_access_rdp_user': 'secure-access-rdp-user',
        'tags': 'tags',
        'target_name': 'target-name',
        'token': 'token',
        'uid_token': 'uid-token',
        'user_ttl': 'user-ttl',
        'warn_user_before_expiration': 'warn-user-before-expiration'
    }

    def __init__(self, allow_user_extend_session=None, delete_protection=None, fixed_user_only='false', json=False, name=None, producer_encryption_key_name=None, rdp_admin_name=None, rdp_admin_pwd=None, rdp_host_name=None, rdp_host_port='22', rdp_user_groups=None, secure_access_allow_external_user=False, secure_access_enable=None, secure_access_host=None, secure_access_rdp_domain=None, secure_access_rdp_user=None, tags=None, target_name=None, token=None, uid_token=None, user_ttl='60m', warn_user_before_expiration=None, local_vars_configuration=None):  # noqa: E501
        """GatewayCreateProducerRdp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._allow_user_extend_session = None
        self._delete_protection = None
        self._fixed_user_only = None
        self._json = None
        self._name = None
        self._producer_encryption_key_name = None
        self._rdp_admin_name = None
        self._rdp_admin_pwd = None
        self._rdp_host_name = None
        self._rdp_host_port = None
        self._rdp_user_groups = None
        self._secure_access_allow_external_user = None
        self._secure_access_enable = None
        self._secure_access_host = None
        self._secure_access_rdp_domain = None
        self._secure_access_rdp_user = None
        self._tags = None
        self._target_name = None
        self._token = None
        self._uid_token = None
        self._user_ttl = None
        self._warn_user_before_expiration = None
        self.discriminator = None

        if allow_user_extend_session is not None:
            self.allow_user_extend_session = allow_user_extend_session
        if delete_protection is not None:
            self.delete_protection = delete_protection
        if fixed_user_only is not None:
            self.fixed_user_only = fixed_user_only
        if json is not None:
            self.json = json
        self.name = name
        if producer_encryption_key_name is not None:
            self.producer_encryption_key_name = producer_encryption_key_name
        if rdp_admin_name is not None:
            self.rdp_admin_name = rdp_admin_name
        if rdp_admin_pwd is not None:
            self.rdp_admin_pwd = rdp_admin_pwd
        if rdp_host_name is not None:
            self.rdp_host_name = rdp_host_name
        if rdp_host_port is not None:
            self.rdp_host_port = rdp_host_port
        if rdp_user_groups is not None:
            self.rdp_user_groups = rdp_user_groups
        if secure_access_allow_external_user is not None:
            self.secure_access_allow_external_user = secure_access_allow_external_user
        if secure_access_enable is not None:
            self.secure_access_enable = secure_access_enable
        if secure_access_host is not None:
            self.secure_access_host = secure_access_host
        if secure_access_rdp_domain is not None:
            self.secure_access_rdp_domain = secure_access_rdp_domain
        if secure_access_rdp_user is not None:
            self.secure_access_rdp_user = secure_access_rdp_user
        if tags is not None:
            self.tags = tags
        if target_name is not None:
            self.target_name = target_name
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        if user_ttl is not None:
            self.user_ttl = user_ttl
        if warn_user_before_expiration is not None:
            self.warn_user_before_expiration = warn_user_before_expiration

    @property
    def allow_user_extend_session(self):
        """Gets the allow_user_extend_session of this GatewayCreateProducerRdp.  # noqa: E501

        AllowUserExtendSession  # noqa: E501

        :return: The allow_user_extend_session of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: int
        """
        return self._allow_user_extend_session

    @allow_user_extend_session.setter
    def allow_user_extend_session(self, allow_user_extend_session):
        """Sets the allow_user_extend_session of this GatewayCreateProducerRdp.

        AllowUserExtendSession  # noqa: E501

        :param allow_user_extend_session: The allow_user_extend_session of this GatewayCreateProducerRdp.  # noqa: E501
        :type: int
        """

        self._allow_user_extend_session = allow_user_extend_session

    @property
    def delete_protection(self):
        """Gets the delete_protection of this GatewayCreateProducerRdp.  # noqa: E501

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :return: The delete_protection of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._delete_protection

    @delete_protection.setter
    def delete_protection(self, delete_protection):
        """Sets the delete_protection of this GatewayCreateProducerRdp.

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :param delete_protection: The delete_protection of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._delete_protection = delete_protection

    @property
    def fixed_user_only(self):
        """Gets the fixed_user_only of this GatewayCreateProducerRdp.  # noqa: E501

        Allow access using externally (IdP) provided username [true/false]  # noqa: E501

        :return: The fixed_user_only of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._fixed_user_only

    @fixed_user_only.setter
    def fixed_user_only(self, fixed_user_only):
        """Sets the fixed_user_only of this GatewayCreateProducerRdp.

        Allow access using externally (IdP) provided username [true/false]  # noqa: E501

        :param fixed_user_only: The fixed_user_only of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._fixed_user_only = fixed_user_only

    @property
    def json(self):
        """Gets the json of this GatewayCreateProducerRdp.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this GatewayCreateProducerRdp.

        Set output format to JSON  # noqa: E501

        :param json: The json of this GatewayCreateProducerRdp.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def name(self):
        """Gets the name of this GatewayCreateProducerRdp.  # noqa: E501

        Producer name  # noqa: E501

        :return: The name of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GatewayCreateProducerRdp.

        Producer name  # noqa: E501

        :param name: The name of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def producer_encryption_key_name(self):
        """Gets the producer_encryption_key_name of this GatewayCreateProducerRdp.  # noqa: E501

        Dynamic producer encryption key  # noqa: E501

        :return: The producer_encryption_key_name of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._producer_encryption_key_name

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, producer_encryption_key_name):
        """Sets the producer_encryption_key_name of this GatewayCreateProducerRdp.

        Dynamic producer encryption key  # noqa: E501

        :param producer_encryption_key_name: The producer_encryption_key_name of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._producer_encryption_key_name = producer_encryption_key_name

    @property
    def rdp_admin_name(self):
        """Gets the rdp_admin_name of this GatewayCreateProducerRdp.  # noqa: E501

        RDP Admin Name  # noqa: E501

        :return: The rdp_admin_name of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._rdp_admin_name

    @rdp_admin_name.setter
    def rdp_admin_name(self, rdp_admin_name):
        """Sets the rdp_admin_name of this GatewayCreateProducerRdp.

        RDP Admin Name  # noqa: E501

        :param rdp_admin_name: The rdp_admin_name of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._rdp_admin_name = rdp_admin_name

    @property
    def rdp_admin_pwd(self):
        """Gets the rdp_admin_pwd of this GatewayCreateProducerRdp.  # noqa: E501

        RDP Admin password  # noqa: E501

        :return: The rdp_admin_pwd of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._rdp_admin_pwd

    @rdp_admin_pwd.setter
    def rdp_admin_pwd(self, rdp_admin_pwd):
        """Sets the rdp_admin_pwd of this GatewayCreateProducerRdp.

        RDP Admin password  # noqa: E501

        :param rdp_admin_pwd: The rdp_admin_pwd of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._rdp_admin_pwd = rdp_admin_pwd

    @property
    def rdp_host_name(self):
        """Gets the rdp_host_name of this GatewayCreateProducerRdp.  # noqa: E501

        Hostname  # noqa: E501

        :return: The rdp_host_name of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._rdp_host_name

    @rdp_host_name.setter
    def rdp_host_name(self, rdp_host_name):
        """Sets the rdp_host_name of this GatewayCreateProducerRdp.

        Hostname  # noqa: E501

        :param rdp_host_name: The rdp_host_name of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._rdp_host_name = rdp_host_name

    @property
    def rdp_host_port(self):
        """Gets the rdp_host_port of this GatewayCreateProducerRdp.  # noqa: E501

        Port  # noqa: E501

        :return: The rdp_host_port of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._rdp_host_port

    @rdp_host_port.setter
    def rdp_host_port(self, rdp_host_port):
        """Sets the rdp_host_port of this GatewayCreateProducerRdp.

        Port  # noqa: E501

        :param rdp_host_port: The rdp_host_port of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._rdp_host_port = rdp_host_port

    @property
    def rdp_user_groups(self):
        """Gets the rdp_user_groups of this GatewayCreateProducerRdp.  # noqa: E501

        Groups  # noqa: E501

        :return: The rdp_user_groups of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._rdp_user_groups

    @rdp_user_groups.setter
    def rdp_user_groups(self, rdp_user_groups):
        """Sets the rdp_user_groups of this GatewayCreateProducerRdp.

        Groups  # noqa: E501

        :param rdp_user_groups: The rdp_user_groups of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._rdp_user_groups = rdp_user_groups

    @property
    def secure_access_allow_external_user(self):
        """Gets the secure_access_allow_external_user of this GatewayCreateProducerRdp.  # noqa: E501

        Allow providing external user for a domain users  # noqa: E501

        :return: The secure_access_allow_external_user of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: bool
        """
        return self._secure_access_allow_external_user

    @secure_access_allow_external_user.setter
    def secure_access_allow_external_user(self, secure_access_allow_external_user):
        """Sets the secure_access_allow_external_user of this GatewayCreateProducerRdp.

        Allow providing external user for a domain users  # noqa: E501

        :param secure_access_allow_external_user: The secure_access_allow_external_user of this GatewayCreateProducerRdp.  # noqa: E501
        :type: bool
        """

        self._secure_access_allow_external_user = secure_access_allow_external_user

    @property
    def secure_access_enable(self):
        """Gets the secure_access_enable of this GatewayCreateProducerRdp.  # noqa: E501

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :return: The secure_access_enable of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_enable

    @secure_access_enable.setter
    def secure_access_enable(self, secure_access_enable):
        """Sets the secure_access_enable of this GatewayCreateProducerRdp.

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :param secure_access_enable: The secure_access_enable of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._secure_access_enable = secure_access_enable

    @property
    def secure_access_host(self):
        """Gets the secure_access_host of this GatewayCreateProducerRdp.  # noqa: E501

        Target servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers)  # noqa: E501

        :return: The secure_access_host of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: list[str]
        """
        return self._secure_access_host

    @secure_access_host.setter
    def secure_access_host(self, secure_access_host):
        """Sets the secure_access_host of this GatewayCreateProducerRdp.

        Target servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers)  # noqa: E501

        :param secure_access_host: The secure_access_host of this GatewayCreateProducerRdp.  # noqa: E501
        :type: list[str]
        """

        self._secure_access_host = secure_access_host

    @property
    def secure_access_rdp_domain(self):
        """Gets the secure_access_rdp_domain of this GatewayCreateProducerRdp.  # noqa: E501

        Required when the Dynamic Secret is used for a domain user  # noqa: E501

        :return: The secure_access_rdp_domain of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_rdp_domain

    @secure_access_rdp_domain.setter
    def secure_access_rdp_domain(self, secure_access_rdp_domain):
        """Sets the secure_access_rdp_domain of this GatewayCreateProducerRdp.

        Required when the Dynamic Secret is used for a domain user  # noqa: E501

        :param secure_access_rdp_domain: The secure_access_rdp_domain of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._secure_access_rdp_domain = secure_access_rdp_domain

    @property
    def secure_access_rdp_user(self):
        """Gets the secure_access_rdp_user of this GatewayCreateProducerRdp.  # noqa: E501

        Override the RDP Domain username  # noqa: E501

        :return: The secure_access_rdp_user of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_rdp_user

    @secure_access_rdp_user.setter
    def secure_access_rdp_user(self, secure_access_rdp_user):
        """Sets the secure_access_rdp_user of this GatewayCreateProducerRdp.

        Override the RDP Domain username  # noqa: E501

        :param secure_access_rdp_user: The secure_access_rdp_user of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._secure_access_rdp_user = secure_access_rdp_user

    @property
    def tags(self):
        """Gets the tags of this GatewayCreateProducerRdp.  # noqa: E501

        Add tags attached to this object  # noqa: E501

        :return: The tags of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this GatewayCreateProducerRdp.

        Add tags attached to this object  # noqa: E501

        :param tags: The tags of this GatewayCreateProducerRdp.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def target_name(self):
        """Gets the target_name of this GatewayCreateProducerRdp.  # noqa: E501

        Target name  # noqa: E501

        :return: The target_name of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """Sets the target_name of this GatewayCreateProducerRdp.

        Target name  # noqa: E501

        :param target_name: The target_name of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._target_name = target_name

    @property
    def token(self):
        """Gets the token of this GatewayCreateProducerRdp.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this GatewayCreateProducerRdp.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this GatewayCreateProducerRdp.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this GatewayCreateProducerRdp.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def user_ttl(self):
        """Gets the user_ttl of this GatewayCreateProducerRdp.  # noqa: E501

        User TTL  # noqa: E501

        :return: The user_ttl of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: str
        """
        return self._user_ttl

    @user_ttl.setter
    def user_ttl(self, user_ttl):
        """Sets the user_ttl of this GatewayCreateProducerRdp.

        User TTL  # noqa: E501

        :param user_ttl: The user_ttl of this GatewayCreateProducerRdp.  # noqa: E501
        :type: str
        """

        self._user_ttl = user_ttl

    @property
    def warn_user_before_expiration(self):
        """Gets the warn_user_before_expiration of this GatewayCreateProducerRdp.  # noqa: E501

        WarnBeforeUserExpiration  # noqa: E501

        :return: The warn_user_before_expiration of this GatewayCreateProducerRdp.  # noqa: E501
        :rtype: int
        """
        return self._warn_user_before_expiration

    @warn_user_before_expiration.setter
    def warn_user_before_expiration(self, warn_user_before_expiration):
        """Sets the warn_user_before_expiration of this GatewayCreateProducerRdp.

        WarnBeforeUserExpiration  # noqa: E501

        :param warn_user_before_expiration: The warn_user_before_expiration of this GatewayCreateProducerRdp.  # noqa: E501
        :type: int
        """

        self._warn_user_before_expiration = warn_user_before_expiration

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
        if not isinstance(other, GatewayCreateProducerRdp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GatewayCreateProducerRdp):
            return True

        return self.to_dict() != other.to_dict()
