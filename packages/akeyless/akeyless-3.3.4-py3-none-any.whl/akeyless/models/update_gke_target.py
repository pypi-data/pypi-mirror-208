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


class UpdateGKETarget(object):
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
        'gke_account_key': 'str',
        'gke_cluster_cert': 'str',
        'gke_cluster_endpoint': 'str',
        'gke_cluster_name': 'str',
        'gke_service_account_email': 'str',
        'json': 'bool',
        'keep_prev_version': 'str',
        'key': 'str',
        'name': 'str',
        'new_name': 'str',
        'token': 'str',
        'uid_token': 'str',
        'update_version': 'bool',
        'use_gw_cloud_identity': 'bool'
    }

    attribute_map = {
        'comment': 'comment',
        'description': 'description',
        'gke_account_key': 'gke-account-key',
        'gke_cluster_cert': 'gke-cluster-cert',
        'gke_cluster_endpoint': 'gke-cluster-endpoint',
        'gke_cluster_name': 'gke-cluster-name',
        'gke_service_account_email': 'gke-service-account-email',
        'json': 'json',
        'keep_prev_version': 'keep-prev-version',
        'key': 'key',
        'name': 'name',
        'new_name': 'new-name',
        'token': 'token',
        'uid_token': 'uid-token',
        'update_version': 'update-version',
        'use_gw_cloud_identity': 'use-gw-cloud-identity'
    }

    def __init__(self, comment=None, description=None, gke_account_key=None, gke_cluster_cert=None, gke_cluster_endpoint=None, gke_cluster_name=None, gke_service_account_email=None, json=False, keep_prev_version=None, key=None, name=None, new_name=None, token=None, uid_token=None, update_version=None, use_gw_cloud_identity=None, local_vars_configuration=None):  # noqa: E501
        """UpdateGKETarget - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._comment = None
        self._description = None
        self._gke_account_key = None
        self._gke_cluster_cert = None
        self._gke_cluster_endpoint = None
        self._gke_cluster_name = None
        self._gke_service_account_email = None
        self._json = None
        self._keep_prev_version = None
        self._key = None
        self._name = None
        self._new_name = None
        self._token = None
        self._uid_token = None
        self._update_version = None
        self._use_gw_cloud_identity = None
        self.discriminator = None

        if comment is not None:
            self.comment = comment
        if description is not None:
            self.description = description
        if gke_account_key is not None:
            self.gke_account_key = gke_account_key
        if gke_cluster_cert is not None:
            self.gke_cluster_cert = gke_cluster_cert
        if gke_cluster_endpoint is not None:
            self.gke_cluster_endpoint = gke_cluster_endpoint
        if gke_cluster_name is not None:
            self.gke_cluster_name = gke_cluster_name
        if gke_service_account_email is not None:
            self.gke_service_account_email = gke_service_account_email
        if json is not None:
            self.json = json
        if keep_prev_version is not None:
            self.keep_prev_version = keep_prev_version
        if key is not None:
            self.key = key
        self.name = name
        if new_name is not None:
            self.new_name = new_name
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        if update_version is not None:
            self.update_version = update_version
        if use_gw_cloud_identity is not None:
            self.use_gw_cloud_identity = use_gw_cloud_identity

    @property
    def comment(self):
        """Gets the comment of this UpdateGKETarget.  # noqa: E501

        Deprecated - use description  # noqa: E501

        :return: The comment of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """Sets the comment of this UpdateGKETarget.

        Deprecated - use description  # noqa: E501

        :param comment: The comment of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._comment = comment

    @property
    def description(self):
        """Gets the description of this UpdateGKETarget.  # noqa: E501

        Description of the object  # noqa: E501

        :return: The description of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UpdateGKETarget.

        Description of the object  # noqa: E501

        :param description: The description of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def gke_account_key(self):
        """Gets the gke_account_key of this UpdateGKETarget.  # noqa: E501

        GKE Service Account key file path  # noqa: E501

        :return: The gke_account_key of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._gke_account_key

    @gke_account_key.setter
    def gke_account_key(self, gke_account_key):
        """Sets the gke_account_key of this UpdateGKETarget.

        GKE Service Account key file path  # noqa: E501

        :param gke_account_key: The gke_account_key of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._gke_account_key = gke_account_key

    @property
    def gke_cluster_cert(self):
        """Gets the gke_cluster_cert of this UpdateGKETarget.  # noqa: E501

        GKE cluster CA certificate  # noqa: E501

        :return: The gke_cluster_cert of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._gke_cluster_cert

    @gke_cluster_cert.setter
    def gke_cluster_cert(self, gke_cluster_cert):
        """Sets the gke_cluster_cert of this UpdateGKETarget.

        GKE cluster CA certificate  # noqa: E501

        :param gke_cluster_cert: The gke_cluster_cert of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._gke_cluster_cert = gke_cluster_cert

    @property
    def gke_cluster_endpoint(self):
        """Gets the gke_cluster_endpoint of this UpdateGKETarget.  # noqa: E501

        GKE cluster URL endpoint  # noqa: E501

        :return: The gke_cluster_endpoint of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._gke_cluster_endpoint

    @gke_cluster_endpoint.setter
    def gke_cluster_endpoint(self, gke_cluster_endpoint):
        """Sets the gke_cluster_endpoint of this UpdateGKETarget.

        GKE cluster URL endpoint  # noqa: E501

        :param gke_cluster_endpoint: The gke_cluster_endpoint of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._gke_cluster_endpoint = gke_cluster_endpoint

    @property
    def gke_cluster_name(self):
        """Gets the gke_cluster_name of this UpdateGKETarget.  # noqa: E501

        GKE cluster name  # noqa: E501

        :return: The gke_cluster_name of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._gke_cluster_name

    @gke_cluster_name.setter
    def gke_cluster_name(self, gke_cluster_name):
        """Sets the gke_cluster_name of this UpdateGKETarget.

        GKE cluster name  # noqa: E501

        :param gke_cluster_name: The gke_cluster_name of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._gke_cluster_name = gke_cluster_name

    @property
    def gke_service_account_email(self):
        """Gets the gke_service_account_email of this UpdateGKETarget.  # noqa: E501

        GKE service account email  # noqa: E501

        :return: The gke_service_account_email of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._gke_service_account_email

    @gke_service_account_email.setter
    def gke_service_account_email(self, gke_service_account_email):
        """Sets the gke_service_account_email of this UpdateGKETarget.

        GKE service account email  # noqa: E501

        :param gke_service_account_email: The gke_service_account_email of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._gke_service_account_email = gke_service_account_email

    @property
    def json(self):
        """Gets the json of this UpdateGKETarget.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this UpdateGKETarget.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this UpdateGKETarget.

        Set output format to JSON  # noqa: E501

        :param json: The json of this UpdateGKETarget.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def keep_prev_version(self):
        """Gets the keep_prev_version of this UpdateGKETarget.  # noqa: E501

        Whether to keep previous version [true/false]. If not set, use default according to account settings  # noqa: E501

        :return: The keep_prev_version of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._keep_prev_version

    @keep_prev_version.setter
    def keep_prev_version(self, keep_prev_version):
        """Sets the keep_prev_version of this UpdateGKETarget.

        Whether to keep previous version [true/false]. If not set, use default according to account settings  # noqa: E501

        :param keep_prev_version: The keep_prev_version of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._keep_prev_version = keep_prev_version

    @property
    def key(self):
        """Gets the key of this UpdateGKETarget.  # noqa: E501

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :return: The key of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this UpdateGKETarget.

        The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)  # noqa: E501

        :param key: The key of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def name(self):
        """Gets the name of this UpdateGKETarget.  # noqa: E501

        Target name  # noqa: E501

        :return: The name of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UpdateGKETarget.

        Target name  # noqa: E501

        :param name: The name of this UpdateGKETarget.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def new_name(self):
        """Gets the new_name of this UpdateGKETarget.  # noqa: E501

        New target name  # noqa: E501

        :return: The new_name of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._new_name

    @new_name.setter
    def new_name(self, new_name):
        """Sets the new_name of this UpdateGKETarget.

        New target name  # noqa: E501

        :param new_name: The new_name of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._new_name = new_name

    @property
    def token(self):
        """Gets the token of this UpdateGKETarget.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this UpdateGKETarget.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this UpdateGKETarget.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this UpdateGKETarget.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this UpdateGKETarget.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this UpdateGKETarget.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def update_version(self):
        """Gets the update_version of this UpdateGKETarget.  # noqa: E501

        Deprecated  # noqa: E501

        :return: The update_version of this UpdateGKETarget.  # noqa: E501
        :rtype: bool
        """
        return self._update_version

    @update_version.setter
    def update_version(self, update_version):
        """Sets the update_version of this UpdateGKETarget.

        Deprecated  # noqa: E501

        :param update_version: The update_version of this UpdateGKETarget.  # noqa: E501
        :type: bool
        """

        self._update_version = update_version

    @property
    def use_gw_cloud_identity(self):
        """Gets the use_gw_cloud_identity of this UpdateGKETarget.  # noqa: E501


        :return: The use_gw_cloud_identity of this UpdateGKETarget.  # noqa: E501
        :rtype: bool
        """
        return self._use_gw_cloud_identity

    @use_gw_cloud_identity.setter
    def use_gw_cloud_identity(self, use_gw_cloud_identity):
        """Sets the use_gw_cloud_identity of this UpdateGKETarget.


        :param use_gw_cloud_identity: The use_gw_cloud_identity of this UpdateGKETarget.  # noqa: E501
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
        if not isinstance(other, UpdateGKETarget):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateGKETarget):
            return True

        return self.to_dict() != other.to_dict()
