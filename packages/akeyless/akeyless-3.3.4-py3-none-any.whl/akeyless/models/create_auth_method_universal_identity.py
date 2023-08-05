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


class CreateAuthMethodUniversalIdentity(object):
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
        'access_expires': 'int',
        'bound_ips': 'list[str]',
        'deny_inheritance': 'bool',
        'deny_rotate': 'bool',
        'force_sub_claims': 'bool',
        'gw_bound_ips': 'list[str]',
        'json': 'bool',
        'jwt_ttl': 'int',
        'name': 'str',
        'token': 'str',
        'ttl': 'int',
        'uid_token': 'str'
    }

    attribute_map = {
        'access_expires': 'access-expires',
        'bound_ips': 'bound-ips',
        'deny_inheritance': 'deny-inheritance',
        'deny_rotate': 'deny-rotate',
        'force_sub_claims': 'force-sub-claims',
        'gw_bound_ips': 'gw-bound-ips',
        'json': 'json',
        'jwt_ttl': 'jwt-ttl',
        'name': 'name',
        'token': 'token',
        'ttl': 'ttl',
        'uid_token': 'uid-token'
    }

    def __init__(self, access_expires=0, bound_ips=None, deny_inheritance=None, deny_rotate=None, force_sub_claims=None, gw_bound_ips=None, json=False, jwt_ttl=0, name=None, token=None, ttl=60, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """CreateAuthMethodUniversalIdentity - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._access_expires = None
        self._bound_ips = None
        self._deny_inheritance = None
        self._deny_rotate = None
        self._force_sub_claims = None
        self._gw_bound_ips = None
        self._json = None
        self._jwt_ttl = None
        self._name = None
        self._token = None
        self._ttl = None
        self._uid_token = None
        self.discriminator = None

        if access_expires is not None:
            self.access_expires = access_expires
        if bound_ips is not None:
            self.bound_ips = bound_ips
        if deny_inheritance is not None:
            self.deny_inheritance = deny_inheritance
        if deny_rotate is not None:
            self.deny_rotate = deny_rotate
        if force_sub_claims is not None:
            self.force_sub_claims = force_sub_claims
        if gw_bound_ips is not None:
            self.gw_bound_ips = gw_bound_ips
        if json is not None:
            self.json = json
        if jwt_ttl is not None:
            self.jwt_ttl = jwt_ttl
        self.name = name
        if token is not None:
            self.token = token
        if ttl is not None:
            self.ttl = ttl
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def access_expires(self):
        """Gets the access_expires of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Access expiration date in Unix timestamp (select 0 for access without expiry date)  # noqa: E501

        :return: The access_expires of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: int
        """
        return self._access_expires

    @access_expires.setter
    def access_expires(self, access_expires):
        """Sets the access_expires of this CreateAuthMethodUniversalIdentity.

        Access expiration date in Unix timestamp (select 0 for access without expiry date)  # noqa: E501

        :param access_expires: The access_expires of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: int
        """

        self._access_expires = access_expires

    @property
    def bound_ips(self):
        """Gets the bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        A CIDR whitelist with the IPs that the access is restricted to  # noqa: E501

        :return: The bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: list[str]
        """
        return self._bound_ips

    @bound_ips.setter
    def bound_ips(self, bound_ips):
        """Sets the bound_ips of this CreateAuthMethodUniversalIdentity.

        A CIDR whitelist with the IPs that the access is restricted to  # noqa: E501

        :param bound_ips: The bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: list[str]
        """

        self._bound_ips = bound_ips

    @property
    def deny_inheritance(self):
        """Gets the deny_inheritance of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Deny from root to create children  # noqa: E501

        :return: The deny_inheritance of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: bool
        """
        return self._deny_inheritance

    @deny_inheritance.setter
    def deny_inheritance(self, deny_inheritance):
        """Sets the deny_inheritance of this CreateAuthMethodUniversalIdentity.

        Deny from root to create children  # noqa: E501

        :param deny_inheritance: The deny_inheritance of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: bool
        """

        self._deny_inheritance = deny_inheritance

    @property
    def deny_rotate(self):
        """Gets the deny_rotate of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Deny from the token to rotate  # noqa: E501

        :return: The deny_rotate of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: bool
        """
        return self._deny_rotate

    @deny_rotate.setter
    def deny_rotate(self, deny_rotate):
        """Sets the deny_rotate of this CreateAuthMethodUniversalIdentity.

        Deny from the token to rotate  # noqa: E501

        :param deny_rotate: The deny_rotate of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: bool
        """

        self._deny_rotate = deny_rotate

    @property
    def force_sub_claims(self):
        """Gets the force_sub_claims of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        if true: enforce role-association must include sub claims  # noqa: E501

        :return: The force_sub_claims of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: bool
        """
        return self._force_sub_claims

    @force_sub_claims.setter
    def force_sub_claims(self, force_sub_claims):
        """Sets the force_sub_claims of this CreateAuthMethodUniversalIdentity.

        if true: enforce role-association must include sub claims  # noqa: E501

        :param force_sub_claims: The force_sub_claims of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: bool
        """

        self._force_sub_claims = force_sub_claims

    @property
    def gw_bound_ips(self):
        """Gets the gw_bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        A CIDR whitelist with the GW IPs that the access is restricted to  # noqa: E501

        :return: The gw_bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: list[str]
        """
        return self._gw_bound_ips

    @gw_bound_ips.setter
    def gw_bound_ips(self, gw_bound_ips):
        """Sets the gw_bound_ips of this CreateAuthMethodUniversalIdentity.

        A CIDR whitelist with the GW IPs that the access is restricted to  # noqa: E501

        :param gw_bound_ips: The gw_bound_ips of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: list[str]
        """

        self._gw_bound_ips = gw_bound_ips

    @property
    def json(self):
        """Gets the json of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this CreateAuthMethodUniversalIdentity.

        Set output format to JSON  # noqa: E501

        :param json: The json of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def jwt_ttl(self):
        """Gets the jwt_ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Jwt TTL  # noqa: E501

        :return: The jwt_ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: int
        """
        return self._jwt_ttl

    @jwt_ttl.setter
    def jwt_ttl(self, jwt_ttl):
        """Sets the jwt_ttl of this CreateAuthMethodUniversalIdentity.

        Jwt TTL  # noqa: E501

        :param jwt_ttl: The jwt_ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: int
        """

        self._jwt_ttl = jwt_ttl

    @property
    def name(self):
        """Gets the name of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Auth Method name  # noqa: E501

        :return: The name of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateAuthMethodUniversalIdentity.

        Auth Method name  # noqa: E501

        :param name: The name of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def token(self):
        """Gets the token of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this CreateAuthMethodUniversalIdentity.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def ttl(self):
        """Gets the ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        Token ttl  # noqa: E501

        :return: The ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: int
        """
        return self._ttl

    @ttl.setter
    def ttl(self, ttl):
        """Sets the ttl of this CreateAuthMethodUniversalIdentity.

        Token ttl  # noqa: E501

        :param ttl: The ttl of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :type: int
        """

        self._ttl = ttl

    @property
    def uid_token(self):
        """Gets the uid_token of this CreateAuthMethodUniversalIdentity.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this CreateAuthMethodUniversalIdentity.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this CreateAuthMethodUniversalIdentity.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this CreateAuthMethodUniversalIdentity.  # noqa: E501
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
        if not isinstance(other, CreateAuthMethodUniversalIdentity):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateAuthMethodUniversalIdentity):
            return True

        return self.to_dict() != other.to_dict()
