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


class Detokenize(object):
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
        'ciphertext': 'str',
        'json': 'bool',
        'token': 'str',
        'tokenizer_name': 'str',
        'tweak': 'str',
        'uid_token': 'str'
    }

    attribute_map = {
        'ciphertext': 'ciphertext',
        'json': 'json',
        'token': 'token',
        'tokenizer_name': 'tokenizer-name',
        'tweak': 'tweak',
        'uid_token': 'uid-token'
    }

    def __init__(self, ciphertext=None, json=False, token=None, tokenizer_name=None, tweak=None, uid_token=None, local_vars_configuration=None):  # noqa: E501
        """Detokenize - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._ciphertext = None
        self._json = None
        self._token = None
        self._tokenizer_name = None
        self._tweak = None
        self._uid_token = None
        self.discriminator = None

        self.ciphertext = ciphertext
        if json is not None:
            self.json = json
        if token is not None:
            self.token = token
        self.tokenizer_name = tokenizer_name
        if tweak is not None:
            self.tweak = tweak
        if uid_token is not None:
            self.uid_token = uid_token

    @property
    def ciphertext(self):
        """Gets the ciphertext of this Detokenize.  # noqa: E501

        Data to be decrypted  # noqa: E501

        :return: The ciphertext of this Detokenize.  # noqa: E501
        :rtype: str
        """
        return self._ciphertext

    @ciphertext.setter
    def ciphertext(self, ciphertext):
        """Sets the ciphertext of this Detokenize.

        Data to be decrypted  # noqa: E501

        :param ciphertext: The ciphertext of this Detokenize.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and ciphertext is None:  # noqa: E501
            raise ValueError("Invalid value for `ciphertext`, must not be `None`")  # noqa: E501

        self._ciphertext = ciphertext

    @property
    def json(self):
        """Gets the json of this Detokenize.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this Detokenize.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this Detokenize.

        Set output format to JSON  # noqa: E501

        :param json: The json of this Detokenize.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def token(self):
        """Gets the token of this Detokenize.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this Detokenize.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this Detokenize.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this Detokenize.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def tokenizer_name(self):
        """Gets the tokenizer_name of this Detokenize.  # noqa: E501

        The name of the tokenizer to use in the decryption process  # noqa: E501

        :return: The tokenizer_name of this Detokenize.  # noqa: E501
        :rtype: str
        """
        return self._tokenizer_name

    @tokenizer_name.setter
    def tokenizer_name(self, tokenizer_name):
        """Sets the tokenizer_name of this Detokenize.

        The name of the tokenizer to use in the decryption process  # noqa: E501

        :param tokenizer_name: The tokenizer_name of this Detokenize.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and tokenizer_name is None:  # noqa: E501
            raise ValueError("Invalid value for `tokenizer_name`, must not be `None`")  # noqa: E501

        self._tokenizer_name = tokenizer_name

    @property
    def tweak(self):
        """Gets the tweak of this Detokenize.  # noqa: E501

        Base64 encoded tweak for vaultless encryption  # noqa: E501

        :return: The tweak of this Detokenize.  # noqa: E501
        :rtype: str
        """
        return self._tweak

    @tweak.setter
    def tweak(self, tweak):
        """Sets the tweak of this Detokenize.

        Base64 encoded tweak for vaultless encryption  # noqa: E501

        :param tweak: The tweak of this Detokenize.  # noqa: E501
        :type: str
        """

        self._tweak = tweak

    @property
    def uid_token(self):
        """Gets the uid_token of this Detokenize.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this Detokenize.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this Detokenize.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this Detokenize.  # noqa: E501
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
        if not isinstance(other, Detokenize):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Detokenize):
            return True

        return self.to_dict() != other.to_dict()
