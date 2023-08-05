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


class SignJWTWithClassicKey(object):
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
        'display_id': 'str',
        'json': 'bool',
        'jwt_claims': 'str',
        'signing_method': 'str',
        'token': 'str',
        'uid_token': 'str',
        'version': 'int'
    }

    attribute_map = {
        'display_id': 'display-id',
        'json': 'json',
        'jwt_claims': 'jwt-claims',
        'signing_method': 'signing-method',
        'token': 'token',
        'uid_token': 'uid-token',
        'version': 'version'
    }

    def __init__(self, display_id=None, json=False, jwt_claims=None, signing_method=None, token=None, uid_token=None, version=None, local_vars_configuration=None):  # noqa: E501
        """SignJWTWithClassicKey - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._display_id = None
        self._json = None
        self._jwt_claims = None
        self._signing_method = None
        self._token = None
        self._uid_token = None
        self._version = None
        self.discriminator = None

        self.display_id = display_id
        if json is not None:
            self.json = json
        self.jwt_claims = jwt_claims
        self.signing_method = signing_method
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        self.version = version

    @property
    def display_id(self):
        """Gets the display_id of this SignJWTWithClassicKey.  # noqa: E501

        The name of the key to use in the sign JWT process  # noqa: E501

        :return: The display_id of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._display_id

    @display_id.setter
    def display_id(self, display_id):
        """Sets the display_id of this SignJWTWithClassicKey.

        The name of the key to use in the sign JWT process  # noqa: E501

        :param display_id: The display_id of this SignJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and display_id is None:  # noqa: E501
            raise ValueError("Invalid value for `display_id`, must not be `None`")  # noqa: E501

        self._display_id = display_id

    @property
    def json(self):
        """Gets the json of this SignJWTWithClassicKey.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this SignJWTWithClassicKey.

        Set output format to JSON  # noqa: E501

        :param json: The json of this SignJWTWithClassicKey.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def jwt_claims(self):
        """Gets the jwt_claims of this SignJWTWithClassicKey.  # noqa: E501

        JWTClaims  # noqa: E501

        :return: The jwt_claims of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._jwt_claims

    @jwt_claims.setter
    def jwt_claims(self, jwt_claims):
        """Sets the jwt_claims of this SignJWTWithClassicKey.

        JWTClaims  # noqa: E501

        :param jwt_claims: The jwt_claims of this SignJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and jwt_claims is None:  # noqa: E501
            raise ValueError("Invalid value for `jwt_claims`, must not be `None`")  # noqa: E501

        self._jwt_claims = jwt_claims

    @property
    def signing_method(self):
        """Gets the signing_method of this SignJWTWithClassicKey.  # noqa: E501

        SigningMethod  # noqa: E501

        :return: The signing_method of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._signing_method

    @signing_method.setter
    def signing_method(self, signing_method):
        """Sets the signing_method of this SignJWTWithClassicKey.

        SigningMethod  # noqa: E501

        :param signing_method: The signing_method of this SignJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and signing_method is None:  # noqa: E501
            raise ValueError("Invalid value for `signing_method`, must not be `None`")  # noqa: E501

        self._signing_method = signing_method

    @property
    def token(self):
        """Gets the token of this SignJWTWithClassicKey.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this SignJWTWithClassicKey.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this SignJWTWithClassicKey.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this SignJWTWithClassicKey.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this SignJWTWithClassicKey.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this SignJWTWithClassicKey.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def version(self):
        """Gets the version of this SignJWTWithClassicKey.  # noqa: E501

        classic key version  # noqa: E501

        :return: The version of this SignJWTWithClassicKey.  # noqa: E501
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this SignJWTWithClassicKey.

        classic key version  # noqa: E501

        :param version: The version of this SignJWTWithClassicKey.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and version is None:  # noqa: E501
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501

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
        if not isinstance(other, SignJWTWithClassicKey):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SignJWTWithClassicKey):
            return True

        return self.to_dict() != other.to_dict()
