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


class UpdateAWSTarget(object):
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
        'access_key': 'str',
        'access_key_id': 'str',
        'comment': 'str',
        'description': 'str',
        'json': 'bool',
        'keep_prev_version': 'str',
        'key': 'str',
        'name': 'str',
        'new_name': 'str',
        'region': 'str',
        'session_token': 'str',
        'token': 'str',
        'uid_token': 'str',
        'update_version': 'bool',
        'use_gw_cloud_identity': 'bool'
    }

    attribute_map = {
        'access_key': 'access-key',
        'access_key_id': 'access-key-id',
        'comment': 'comment',
        'description': 'description',
        'json': 'json',
        'keep_prev_version': 'keep-prev-version',
        'key': 'key',
        'name': 'name',
        'new_name': 'new-name',
        'region': 'region',
        'session_token': 'session-token',
        'token': 'token',
        'uid_token': 'uid-token',
        'update_version': 'update-version',
        'use_gw_cloud_identity': 'use-gw-cloud-identity'
    }

    def __init__(self, access_key=None, access_key_id=None, comment=None, description=None, json=False, keep_prev_version=None, key=None, name=None, new_name=None, region='us-east-2', session_token=None, token=None, uid_token=None, update_version=None, use_gw_cloud_identity=None, local_vars_configuration=None):  # noqa: E501
        """UpdateAWSTarget - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._access_key = None
        self._access_key_id = None
        self._comment = None
        self._description = None
        self._json = None
        self._keep_prev_version = None
        self._key = None
        self._name = None
        self._new_name = None
        self._region = None
        self._session_token = None
        self._token = None
        self._uid_token = None
        self._update_version = None
        self._use_gw_cloud_identity = None
        self.discriminator = None

        self.access_key = access_key
        self.access_key_id = access_key_id
        if comment is not None:
            self.comment = comment
        if description is not None:
            self.description = description
        if json is not None:
            self.json = json
        if keep_prev_version is not None:
            self.keep_prev_version = keep_prev_version
        if key is not None:
            self.key = key
        self.name = name
        if new_name is not None:
            self.new_name = new_name
        if region is not None:
            self.region = region
        if session_token is not None:
            self.session_token = session_token
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        if update_version is not None:
            self.update_version = update_version
        if use_gw_cloud_identity is not None:
            self.use_gw_cloud_identity = use_gw_cloud_identity

    @property
    def access_key(self):
        """Gets the access_key of this UpdateAWSTarget.  # noqa: E501

        AWS secret access key  # noqa: E501

        :return: The access_key of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._access_key

    @access_key.setter
    def access_key(self, access_key):
        """Sets the access_key of this UpdateAWSTarget.

        AWS secret access key  # noqa: E501

        :param access_key: The access_key of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and access_key is None:  # noqa: E501
            raise ValueError("Invalid value for `access_key`, must not be `None`")  # noqa: E501

        self._access_key = access_key

    @property
    def access_key_id(self):
        """Gets the access_key_id of this UpdateAWSTarget.  # noqa: E501

        AWS access key ID  # noqa: E501

        :return: The access_key_id of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._access_key_id

    @access_key_id.setter
    def access_key_id(self, access_key_id):
        """Sets the access_key_id of this UpdateAWSTarget.

        AWS access key ID  # noqa: E501

        :param access_key_id: The access_key_id of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and access_key_id is None:  # noqa: E501
            raise ValueError("Invalid value for `access_key_id`, must not be `None`")  # noqa: E501

        self._access_key_id = access_key_id

    @property
    def comment(self):
        """Gets the comment of this UpdateAWSTarget.  # noqa: E501

        Deprecated - use description  # noqa: E501

        :return: The comment of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """Sets the comment of this UpdateAWSTarget.

        Deprecated - use description  # noqa: E501

        :param comment: The comment of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._comment = comment

    @property
    def description(self):
        """Gets the description of this UpdateAWSTarget.  # noqa: E501

        Description of the object  # noqa: E501

        :return: The description of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UpdateAWSTarget.

        Description of the object  # noqa: E501

        :param description: The description of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def json(self):
        """Gets the json of this UpdateAWSTarget.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this UpdateAWSTarget.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this UpdateAWSTarget.

        Set output format to JSON  # noqa: E501

        :param json: The json of this UpdateAWSTarget.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def keep_prev_version(self):
        """Gets the keep_prev_version of this UpdateAWSTarget.  # noqa: E501

        Whether to keep previous version [true/false]. If not set, use default according to account settings  # noqa: E501

        :return: The keep_prev_version of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._keep_prev_version

    @keep_prev_version.setter
    def keep_prev_version(self, keep_prev_version):
        """Sets the keep_prev_version of this UpdateAWSTarget.

        Whether to keep previous version [true/false]. If not set, use default according to account settings  # noqa: E501

        :param keep_prev_version: The keep_prev_version of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._keep_prev_version = keep_prev_version

    @property
    def key(self):
        """Gets the key of this UpdateAWSTarget.  # noqa: E501

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :return: The key of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this UpdateAWSTarget.

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :param key: The key of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def name(self):
        """Gets the name of this UpdateAWSTarget.  # noqa: E501

        Target name  # noqa: E501

        :return: The name of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UpdateAWSTarget.

        Target name  # noqa: E501

        :param name: The name of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def new_name(self):
        """Gets the new_name of this UpdateAWSTarget.  # noqa: E501

        New target name  # noqa: E501

        :return: The new_name of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._new_name

    @new_name.setter
    def new_name(self, new_name):
        """Sets the new_name of this UpdateAWSTarget.

        New target name  # noqa: E501

        :param new_name: The new_name of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._new_name = new_name

    @property
    def region(self):
        """Gets the region of this UpdateAWSTarget.  # noqa: E501

        AWS region  # noqa: E501

        :return: The region of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this UpdateAWSTarget.

        AWS region  # noqa: E501

        :param region: The region of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._region = region

    @property
    def session_token(self):
        """Gets the session_token of this UpdateAWSTarget.  # noqa: E501

        Required only for temporary security credentials retrieved using STS  # noqa: E501

        :return: The session_token of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._session_token

    @session_token.setter
    def session_token(self, session_token):
        """Sets the session_token of this UpdateAWSTarget.

        Required only for temporary security credentials retrieved using STS  # noqa: E501

        :param session_token: The session_token of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._session_token = session_token

    @property
    def token(self):
        """Gets the token of this UpdateAWSTarget.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this UpdateAWSTarget.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this UpdateAWSTarget.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this UpdateAWSTarget.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this UpdateAWSTarget.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this UpdateAWSTarget.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def update_version(self):
        """Gets the update_version of this UpdateAWSTarget.  # noqa: E501

        Deprecated  # noqa: E501

        :return: The update_version of this UpdateAWSTarget.  # noqa: E501
        :rtype: bool
        """
        return self._update_version

    @update_version.setter
    def update_version(self, update_version):
        """Sets the update_version of this UpdateAWSTarget.

        Deprecated  # noqa: E501

        :param update_version: The update_version of this UpdateAWSTarget.  # noqa: E501
        :type: bool
        """

        self._update_version = update_version

    @property
    def use_gw_cloud_identity(self):
        """Gets the use_gw_cloud_identity of this UpdateAWSTarget.  # noqa: E501

        Use the GW's Cloud IAM  # noqa: E501

        :return: The use_gw_cloud_identity of this UpdateAWSTarget.  # noqa: E501
        :rtype: bool
        """
        return self._use_gw_cloud_identity

    @use_gw_cloud_identity.setter
    def use_gw_cloud_identity(self, use_gw_cloud_identity):
        """Sets the use_gw_cloud_identity of this UpdateAWSTarget.

        Use the GW's Cloud IAM  # noqa: E501

        :param use_gw_cloud_identity: The use_gw_cloud_identity of this UpdateAWSTarget.  # noqa: E501
        :type: bool
        """

        self._use_gw_cloud_identity = use_gw_cloud_identity

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
        if not isinstance(other, UpdateAWSTarget):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateAWSTarget):
            return True

        return self.to_dict() != other.to_dict()
