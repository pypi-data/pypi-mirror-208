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


class AssocTargetItem(object):
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
        'disable_previous_key_version': 'bool',
        'json': 'bool',
        'key_operations': 'list[str]',
        'keyring_name': 'str',
        'kms_algorithm': 'str',
        'location_id': 'str',
        'multi_region': 'str',
        'name': 'str',
        'project_id': 'str',
        'purpose': 'str',
        'regions': 'list[str]',
        'target_name': 'str',
        'tenant_secret_type': 'str',
        'token': 'str',
        'uid_token': 'str',
        'vault_name': 'str'
    }

    attribute_map = {
        'disable_previous_key_version': 'disable-previous-key-version',
        'json': 'json',
        'key_operations': 'key-operations',
        'keyring_name': 'keyring-name',
        'kms_algorithm': 'kms-algorithm',
        'location_id': 'location-id',
        'multi_region': 'multi-region',
        'name': 'name',
        'project_id': 'project-id',
        'purpose': 'purpose',
        'regions': 'regions',
        'target_name': 'target-name',
        'tenant_secret_type': 'tenant-secret-type',
        'token': 'token',
        'uid_token': 'uid-token',
        'vault_name': 'vault-name'
    }

    def __init__(self, disable_previous_key_version=False, json=False, key_operations=None, keyring_name=None, kms_algorithm=None, location_id=None, multi_region='false', name=None, project_id=None, purpose=None, regions=None, target_name=None, tenant_secret_type=None, token=None, uid_token=None, vault_name=None, local_vars_configuration=None):  # noqa: E501
        """AssocTargetItem - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._disable_previous_key_version = None
        self._json = None
        self._key_operations = None
        self._keyring_name = None
        self._kms_algorithm = None
        self._location_id = None
        self._multi_region = None
        self._name = None
        self._project_id = None
        self._purpose = None
        self._regions = None
        self._target_name = None
        self._tenant_secret_type = None
        self._token = None
        self._uid_token = None
        self._vault_name = None
        self.discriminator = None

        if disable_previous_key_version is not None:
            self.disable_previous_key_version = disable_previous_key_version
        if json is not None:
            self.json = json
        if key_operations is not None:
            self.key_operations = key_operations
        if keyring_name is not None:
            self.keyring_name = keyring_name
        if kms_algorithm is not None:
            self.kms_algorithm = kms_algorithm
        if location_id is not None:
            self.location_id = location_id
        if multi_region is not None:
            self.multi_region = multi_region
        self.name = name
        if project_id is not None:
            self.project_id = project_id
        if purpose is not None:
            self.purpose = purpose
        if regions is not None:
            self.regions = regions
        self.target_name = target_name
        if tenant_secret_type is not None:
            self.tenant_secret_type = tenant_secret_type
        if token is not None:
            self.token = token
        if uid_token is not None:
            self.uid_token = uid_token
        if vault_name is not None:
            self.vault_name = vault_name

    @property
    def disable_previous_key_version(self):
        """Gets the disable_previous_key_version of this AssocTargetItem.  # noqa: E501

        Automatically disable previous key version (required for azure targets)  # noqa: E501

        :return: The disable_previous_key_version of this AssocTargetItem.  # noqa: E501
        :rtype: bool
        """
        return self._disable_previous_key_version

    @disable_previous_key_version.setter
    def disable_previous_key_version(self, disable_previous_key_version):
        """Sets the disable_previous_key_version of this AssocTargetItem.

        Automatically disable previous key version (required for azure targets)  # noqa: E501

        :param disable_previous_key_version: The disable_previous_key_version of this AssocTargetItem.  # noqa: E501
        :type: bool
        """

        self._disable_previous_key_version = disable_previous_key_version

    @property
    def json(self):
        """Gets the json of this AssocTargetItem.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this AssocTargetItem.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this AssocTargetItem.

        Set output format to JSON  # noqa: E501

        :param json: The json of this AssocTargetItem.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def key_operations(self):
        """Gets the key_operations of this AssocTargetItem.  # noqa: E501

        A list of allowed operations for the key (required for azure targets)  # noqa: E501

        :return: The key_operations of this AssocTargetItem.  # noqa: E501
        :rtype: list[str]
        """
        return self._key_operations

    @key_operations.setter
    def key_operations(self, key_operations):
        """Sets the key_operations of this AssocTargetItem.

        A list of allowed operations for the key (required for azure targets)  # noqa: E501

        :param key_operations: The key_operations of this AssocTargetItem.  # noqa: E501
        :type: list[str]
        """

        self._key_operations = key_operations

    @property
    def keyring_name(self):
        """Gets the keyring_name of this AssocTargetItem.  # noqa: E501

        Keyring name of the GCP KMS (required for gcp targets)  # noqa: E501

        :return: The keyring_name of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._keyring_name

    @keyring_name.setter
    def keyring_name(self, keyring_name):
        """Sets the keyring_name of this AssocTargetItem.

        Keyring name of the GCP KMS (required for gcp targets)  # noqa: E501

        :param keyring_name: The keyring_name of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._keyring_name = keyring_name

    @property
    def kms_algorithm(self):
        """Gets the kms_algorithm of this AssocTargetItem.  # noqa: E501

        Algorithm of the key in GCP KMS (required for gcp targets)  # noqa: E501

        :return: The kms_algorithm of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._kms_algorithm

    @kms_algorithm.setter
    def kms_algorithm(self, kms_algorithm):
        """Sets the kms_algorithm of this AssocTargetItem.

        Algorithm of the key in GCP KMS (required for gcp targets)  # noqa: E501

        :param kms_algorithm: The kms_algorithm of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._kms_algorithm = kms_algorithm

    @property
    def location_id(self):
        """Gets the location_id of this AssocTargetItem.  # noqa: E501

        Location id of the GCP KMS (required for gcp targets)  # noqa: E501

        :return: The location_id of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._location_id

    @location_id.setter
    def location_id(self, location_id):
        """Sets the location_id of this AssocTargetItem.

        Location id of the GCP KMS (required for gcp targets)  # noqa: E501

        :param location_id: The location_id of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._location_id = location_id

    @property
    def multi_region(self):
        """Gets the multi_region of this AssocTargetItem.  # noqa: E501

        Set to 'true' to create a multi-region managed key. (Relevant only for Classic Key AWS targets)  # noqa: E501

        :return: The multi_region of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._multi_region

    @multi_region.setter
    def multi_region(self, multi_region):
        """Sets the multi_region of this AssocTargetItem.

        Set to 'true' to create a multi-region managed key. (Relevant only for Classic Key AWS targets)  # noqa: E501

        :param multi_region: The multi_region of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._multi_region = multi_region

    @property
    def name(self):
        """Gets the name of this AssocTargetItem.  # noqa: E501

        The item to associate  # noqa: E501

        :return: The name of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AssocTargetItem.

        The item to associate  # noqa: E501

        :param name: The name of this AssocTargetItem.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def project_id(self):
        """Gets the project_id of this AssocTargetItem.  # noqa: E501

        Project id of the GCP KMS (required for gcp targets)  # noqa: E501

        :return: The project_id of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this AssocTargetItem.

        Project id of the GCP KMS (required for gcp targets)  # noqa: E501

        :param project_id: The project_id of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def purpose(self):
        """Gets the purpose of this AssocTargetItem.  # noqa: E501

        Purpose of the key in GCP KMS (required for gcp targets)  # noqa: E501

        :return: The purpose of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._purpose

    @purpose.setter
    def purpose(self, purpose):
        """Sets the purpose of this AssocTargetItem.

        Purpose of the key in GCP KMS (required for gcp targets)  # noqa: E501

        :param purpose: The purpose of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._purpose = purpose

    @property
    def regions(self):
        """Gets the regions of this AssocTargetItem.  # noqa: E501

        The list of regions to create a copy of the key in (relevant for aws targets)  # noqa: E501

        :return: The regions of this AssocTargetItem.  # noqa: E501
        :rtype: list[str]
        """
        return self._regions

    @regions.setter
    def regions(self, regions):
        """Sets the regions of this AssocTargetItem.

        The list of regions to create a copy of the key in (relevant for aws targets)  # noqa: E501

        :param regions: The regions of this AssocTargetItem.  # noqa: E501
        :type: list[str]
        """

        self._regions = regions

    @property
    def target_name(self):
        """Gets the target_name of this AssocTargetItem.  # noqa: E501

        The target to associate  # noqa: E501

        :return: The target_name of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """Sets the target_name of this AssocTargetItem.

        The target to associate  # noqa: E501

        :param target_name: The target_name of this AssocTargetItem.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and target_name is None:  # noqa: E501
            raise ValueError("Invalid value for `target_name`, must not be `None`")  # noqa: E501

        self._target_name = target_name

    @property
    def tenant_secret_type(self):
        """Gets the tenant_secret_type of this AssocTargetItem.  # noqa: E501

        The tenant secret type [Data/SearchIndex/Analytics] (required for salesforce targets)  # noqa: E501

        :return: The tenant_secret_type of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._tenant_secret_type

    @tenant_secret_type.setter
    def tenant_secret_type(self, tenant_secret_type):
        """Sets the tenant_secret_type of this AssocTargetItem.

        The tenant secret type [Data/SearchIndex/Analytics] (required for salesforce targets)  # noqa: E501

        :param tenant_secret_type: The tenant_secret_type of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._tenant_secret_type = tenant_secret_type

    @property
    def token(self):
        """Gets the token of this AssocTargetItem.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this AssocTargetItem.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this AssocTargetItem.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this AssocTargetItem.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def vault_name(self):
        """Gets the vault_name of this AssocTargetItem.  # noqa: E501

        Name of the vault used (required for azure targets)  # noqa: E501

        :return: The vault_name of this AssocTargetItem.  # noqa: E501
        :rtype: str
        """
        return self._vault_name

    @vault_name.setter
    def vault_name(self, vault_name):
        """Sets the vault_name of this AssocTargetItem.

        Name of the vault used (required for azure targets)  # noqa: E501

        :param vault_name: The vault_name of this AssocTargetItem.  # noqa: E501
        :type: str
        """

        self._vault_name = vault_name

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
        if not isinstance(other, AssocTargetItem):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AssocTargetItem):
            return True

        return self.to_dict() != other.to_dict()
