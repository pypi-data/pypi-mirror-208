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


class VerifyJWTWithClassicKey(object):
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
        'jwt': 'str',
        'required_claims': 'str',
        'token': 'str',
        'uid_token': 'str',
        'version': 'int'
    }

    attribute_map = {
        'display_id': 'display-id',
        'json': 'json',
        'jwt': 'jwt',
        'required_claims': 'required-claims',
        'token': 'token',
        'uid_token': 'uid-token',
        'version': 'version'
    }

    def __init__(self, display_id=None, json=False, jwt=None, required_claims=None, token=None, uid_token=None, version=None, local_vars_configuration=None):  # noqa: E501
        """VerifyJWTWithClassicKey - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._display_id = None
        self._json = None
        self._jwt = None
        self._required_claims = None
        self._token = None
        self._uid_token = None
        self._version = None
        self.discriminator = None

        self.display_id = display_id
        if json is not None:
            self.json = json
        self.jwt = jwt
        self.required_claims = required_claims
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        self.version = version

    @property
    def display_id(self):
        """Gets the display_id of this VerifyJWTWithClassicKey.  # noqa: E501

        The name of the key to use in the verify JWT process  # noqa: E501

        :return: The display_id of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._display_id

    @display_id.setter
    def display_id(self, display_id):
        """Sets the display_id of this VerifyJWTWithClassicKey.

        The name of the key to use in the verify JWT process  # noqa: E501

        :param display_id: The display_id of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and display_id is None:  # noqa: E501
            raise ValueError("Invalid value for `display_id`, must not be `None`")  # noqa: E501

        self._display_id = display_id

    @property
    def json(self):
        """Gets the json of this VerifyJWTWithClassicKey.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this VerifyJWTWithClassicKey.

        Set output format to JSON  # noqa: E501

        :param json: The json of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def jwt(self):
        """Gets the jwt of this VerifyJWTWithClassicKey.  # noqa: E501

        JWT  # noqa: E501

        :return: The jwt of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._jwt

    @jwt.setter
    def jwt(self, jwt):
        """Sets the jwt of this VerifyJWTWithClassicKey.

        JWT  # noqa: E501

        :param jwt: The jwt of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and jwt is None:  # noqa: E501
            raise ValueError("Invalid value for `jwt`, must not be `None`")  # noqa: E501

        self._jwt = jwt

    @property
    def required_claims(self):
        """Gets the required_claims of this VerifyJWTWithClassicKey.  # noqa: E501

        RequiredClaims  # noqa: E501

        :return: The required_claims of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._required_claims

    @required_claims.setter
    def required_claims(self, required_claims):
        """Sets the required_claims of this VerifyJWTWithClassicKey.

        RequiredClaims  # noqa: E501

        :param required_claims: The required_claims of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and required_claims is None:  # noqa: E501
            raise ValueError("Invalid value for `required_claims`, must not be `None`")  # noqa: E501

        self._required_claims = required_claims

    @property
    def token(self):
        """Gets the token of this VerifyJWTWithClassicKey.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this VerifyJWTWithClassicKey.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this VerifyJWTWithClassicKey.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this VerifyJWTWithClassicKey.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this VerifyJWTWithClassicKey.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def version(self):
        """Gets the version of this VerifyJWTWithClassicKey.  # noqa: E501

        classic key version  # noqa: E501

        :return: The version of this VerifyJWTWithClassicKey.  # noqa: E501
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this VerifyJWTWithClassicKey.

        classic key version  # noqa: E501

        :param version: The version of this VerifyJWTWithClassicKey.  # noqa: E501
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
        if not isinstance(other, VerifyJWTWithClassicKey):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, VerifyJWTWithClassicKey):
            return True

        return self.to_dict() != other.to_dict()
