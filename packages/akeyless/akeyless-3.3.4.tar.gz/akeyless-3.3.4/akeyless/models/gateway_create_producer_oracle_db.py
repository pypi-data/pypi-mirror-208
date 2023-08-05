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


class GatewayCreateProducerOracleDb(object):
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
        'db_server_certificates': 'str',
        'db_server_name': 'str',
        'delete_protection': 'str',
        'json': 'bool',
        'name': 'str',
        'oracle_host': 'str',
        'oracle_password': 'str',
        'oracle_port': 'str',
        'oracle_screation_statements': 'str',
        'oracle_service_name': 'str',
        'oracle_username': 'str',
        'producer_encryption_key_name': 'str',
        'secure_access_bastion_issuer': 'str',
        'secure_access_enable': 'str',
        'secure_access_host': 'list[str]',
        'secure_access_web': 'bool',
        'tags': 'list[str]',
        'target_name': 'str',
        'token': 'str',
        'uid_token': 'str',
        'user_ttl': 'str'
    }

    attribute_map = {
        'db_server_certificates': 'db-server-certificates',
        'db_server_name': 'db-server-name',
        'delete_protection': 'delete_protection',
        'json': 'json',
        'name': 'name',
        'oracle_host': 'oracle-host',
        'oracle_password': 'oracle-password',
        'oracle_port': 'oracle-port',
        'oracle_screation_statements': 'oracle-screation-statements',
        'oracle_service_name': 'oracle-service-name',
        'oracle_username': 'oracle-username',
        'producer_encryption_key_name': 'producer-encryption-key-name',
        'secure_access_bastion_issuer': 'secure-access-bastion-issuer',
        'secure_access_enable': 'secure-access-enable',
        'secure_access_host': 'secure-access-host',
        'secure_access_web': 'secure-access-web',
        'tags': 'tags',
        'target_name': 'target-name',
        'token': 'token',
        'uid_token': 'uid-token',
        'user_ttl': 'user-ttl'
    }

    def __init__(self, db_server_certificates=None, db_server_name=None, delete_protection=None, json=False, name=None, oracle_host='127.0.0.1', oracle_password=None, oracle_port='1521', oracle_screation_statements=None, oracle_service_name=None, oracle_username=None, producer_encryption_key_name=None, secure_access_bastion_issuer=None, secure_access_enable='false', secure_access_host=None, secure_access_web=False, tags=None, target_name=None, token=None, uid_token=None, user_ttl='60m', local_vars_configuration=None):  # noqa: E501
        """GatewayCreateProducerOracleDb - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._db_server_certificates = None
        self._db_server_name = None
        self._delete_protection = None
        self._json = None
        self._name = None
        self._oracle_host = None
        self._oracle_password = None
        self._oracle_port = None
        self._oracle_screation_statements = None
        self._oracle_service_name = None
        self._oracle_username = None
        self._producer_encryption_key_name = None
        self._secure_access_bastion_issuer = None
        self._secure_access_enable = None
        self._secure_access_host = None
        self._secure_access_web = None
        self._tags = None
        self._target_name = None
        self._token = None
        self._uid_token = None
        self._user_ttl = None
        self.discriminator = None

        if db_server_certificates is not None:
            self.db_server_certificates = db_server_certificates
        if db_server_name is not None:
            self.db_server_name = db_server_name
        if delete_protection is not None:
            self.delete_protection = delete_protection
        if json is not None:
            self.json = json
        self.name = name
        if oracle_host is not None:
            self.oracle_host = oracle_host
        if oracle_password is not None:
            self.oracle_password = oracle_password
        if oracle_port is not None:
            self.oracle_port = oracle_port
        if oracle_screation_statements is not None:
            self.oracle_screation_statements = oracle_screation_statements
        if oracle_service_name is not None:
            self.oracle_service_name = oracle_service_name
        if oracle_username is not None:
            self.oracle_username = oracle_username
        if producer_encryption_key_name is not None:
            self.producer_encryption_key_name = producer_encryption_key_name
        if secure_access_bastion_issuer is not None:
            self.secure_access_bastion_issuer = secure_access_bastion_issuer
        if secure_access_enable is not None:
            self.secure_access_enable = secure_access_enable
        if secure_access_host is not None:
            self.secure_access_host = secure_access_host
        if secure_access_web is not None:
            self.secure_access_web = secure_access_web
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

    @property
    def db_server_certificates(self):
        """Gets the db_server_certificates of this GatewayCreateProducerOracleDb.  # noqa: E501

        (Optional) DB server certificates  # noqa: E501

        :return: The db_server_certificates of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._db_server_certificates

    @db_server_certificates.setter
    def db_server_certificates(self, db_server_certificates):
        """Sets the db_server_certificates of this GatewayCreateProducerOracleDb.

        (Optional) DB server certificates  # noqa: E501

        :param db_server_certificates: The db_server_certificates of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._db_server_certificates = db_server_certificates

    @property
    def db_server_name(self):
        """Gets the db_server_name of this GatewayCreateProducerOracleDb.  # noqa: E501

        (Optional) Server name for certificate verification  # noqa: E501

        :return: The db_server_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._db_server_name

    @db_server_name.setter
    def db_server_name(self, db_server_name):
        """Sets the db_server_name of this GatewayCreateProducerOracleDb.

        (Optional) Server name for certificate verification  # noqa: E501

        :param db_server_name: The db_server_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._db_server_name = db_server_name

    @property
    def delete_protection(self):
        """Gets the delete_protection of this GatewayCreateProducerOracleDb.  # noqa: E501

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :return: The delete_protection of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._delete_protection

    @delete_protection.setter
    def delete_protection(self, delete_protection):
        """Sets the delete_protection of this GatewayCreateProducerOracleDb.

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :param delete_protection: The delete_protection of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._delete_protection = delete_protection

    @property
    def json(self):
        """Gets the json of this GatewayCreateProducerOracleDb.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this GatewayCreateProducerOracleDb.

        Set output format to JSON  # noqa: E501

        :param json: The json of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def name(self):
        """Gets the name of this GatewayCreateProducerOracleDb.  # noqa: E501

        Producer name  # noqa: E501

        :return: The name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GatewayCreateProducerOracleDb.

        Producer name  # noqa: E501

        :param name: The name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def oracle_host(self):
        """Gets the oracle_host of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle Host  # noqa: E501

        :return: The oracle_host of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_host

    @oracle_host.setter
    def oracle_host(self, oracle_host):
        """Sets the oracle_host of this GatewayCreateProducerOracleDb.

        Oracle Host  # noqa: E501

        :param oracle_host: The oracle_host of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_host = oracle_host

    @property
    def oracle_password(self):
        """Gets the oracle_password of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle Password  # noqa: E501

        :return: The oracle_password of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_password

    @oracle_password.setter
    def oracle_password(self, oracle_password):
        """Sets the oracle_password of this GatewayCreateProducerOracleDb.

        Oracle Password  # noqa: E501

        :param oracle_password: The oracle_password of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_password = oracle_password

    @property
    def oracle_port(self):
        """Gets the oracle_port of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle Port  # noqa: E501

        :return: The oracle_port of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_port

    @oracle_port.setter
    def oracle_port(self, oracle_port):
        """Sets the oracle_port of this GatewayCreateProducerOracleDb.

        Oracle Port  # noqa: E501

        :param oracle_port: The oracle_port of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_port = oracle_port

    @property
    def oracle_screation_statements(self):
        """Gets the oracle_screation_statements of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle Creation statements  # noqa: E501

        :return: The oracle_screation_statements of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_screation_statements

    @oracle_screation_statements.setter
    def oracle_screation_statements(self, oracle_screation_statements):
        """Sets the oracle_screation_statements of this GatewayCreateProducerOracleDb.

        Oracle Creation statements  # noqa: E501

        :param oracle_screation_statements: The oracle_screation_statements of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_screation_statements = oracle_screation_statements

    @property
    def oracle_service_name(self):
        """Gets the oracle_service_name of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle DB Name  # noqa: E501

        :return: The oracle_service_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_service_name

    @oracle_service_name.setter
    def oracle_service_name(self, oracle_service_name):
        """Sets the oracle_service_name of this GatewayCreateProducerOracleDb.

        Oracle DB Name  # noqa: E501

        :param oracle_service_name: The oracle_service_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_service_name = oracle_service_name

    @property
    def oracle_username(self):
        """Gets the oracle_username of this GatewayCreateProducerOracleDb.  # noqa: E501

        Oracle Username  # noqa: E501

        :return: The oracle_username of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._oracle_username

    @oracle_username.setter
    def oracle_username(self, oracle_username):
        """Sets the oracle_username of this GatewayCreateProducerOracleDb.

        Oracle Username  # noqa: E501

        :param oracle_username: The oracle_username of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._oracle_username = oracle_username

    @property
    def producer_encryption_key_name(self):
        """Gets the producer_encryption_key_name of this GatewayCreateProducerOracleDb.  # noqa: E501

        Dynamic producer encryption key  # noqa: E501

        :return: The producer_encryption_key_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._producer_encryption_key_name

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, producer_encryption_key_name):
        """Sets the producer_encryption_key_name of this GatewayCreateProducerOracleDb.

        Dynamic producer encryption key  # noqa: E501

        :param producer_encryption_key_name: The producer_encryption_key_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._producer_encryption_key_name = producer_encryption_key_name

    @property
    def secure_access_bastion_issuer(self):
        """Gets the secure_access_bastion_issuer of this GatewayCreateProducerOracleDb.  # noqa: E501

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :return: The secure_access_bastion_issuer of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_bastion_issuer

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, secure_access_bastion_issuer):
        """Sets the secure_access_bastion_issuer of this GatewayCreateProducerOracleDb.

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :param secure_access_bastion_issuer: The secure_access_bastion_issuer of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._secure_access_bastion_issuer = secure_access_bastion_issuer

    @property
    def secure_access_enable(self):
        """Gets the secure_access_enable of this GatewayCreateProducerOracleDb.  # noqa: E501

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :return: The secure_access_enable of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_enable

    @secure_access_enable.setter
    def secure_access_enable(self, secure_access_enable):
        """Sets the secure_access_enable of this GatewayCreateProducerOracleDb.

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :param secure_access_enable: The secure_access_enable of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._secure_access_enable = secure_access_enable

    @property
    def secure_access_host(self):
        """Gets the secure_access_host of this GatewayCreateProducerOracleDb.  # noqa: E501

        Target DB servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts)  # noqa: E501

        :return: The secure_access_host of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: list[str]
        """
        return self._secure_access_host

    @secure_access_host.setter
    def secure_access_host(self, secure_access_host):
        """Sets the secure_access_host of this GatewayCreateProducerOracleDb.

        Target DB servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts)  # noqa: E501

        :param secure_access_host: The secure_access_host of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: list[str]
        """

        self._secure_access_host = secure_access_host

    @property
    def secure_access_web(self):
        """Gets the secure_access_web of this GatewayCreateProducerOracleDb.  # noqa: E501

        Enable Web Secure Remote Access  # noqa: E501

        :return: The secure_access_web of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: bool
        """
        return self._secure_access_web

    @secure_access_web.setter
    def secure_access_web(self, secure_access_web):
        """Sets the secure_access_web of this GatewayCreateProducerOracleDb.

        Enable Web Secure Remote Access  # noqa: E501

        :param secure_access_web: The secure_access_web of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: bool
        """

        self._secure_access_web = secure_access_web

    @property
    def tags(self):
        """Gets the tags of this GatewayCreateProducerOracleDb.  # noqa: E501

        Add tags attached to this object  # noqa: E501

        :return: The tags of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this GatewayCreateProducerOracleDb.

        Add tags attached to this object  # noqa: E501

        :param tags: The tags of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def target_name(self):
        """Gets the target_name of this GatewayCreateProducerOracleDb.  # noqa: E501

        Target name  # noqa: E501

        :return: The target_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """Sets the target_name of this GatewayCreateProducerOracleDb.

        Target name  # noqa: E501

        :param target_name: The target_name of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._target_name = target_name

    @property
    def token(self):
        """Gets the token of this GatewayCreateProducerOracleDb.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this GatewayCreateProducerOracleDb.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this GatewayCreateProducerOracleDb.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this GatewayCreateProducerOracleDb.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def user_ttl(self):
        """Gets the user_ttl of this GatewayCreateProducerOracleDb.  # noqa: E501

        User TTL  # noqa: E501

        :return: The user_ttl of this GatewayCreateProducerOracleDb.  # noqa: E501
        :rtype: str
        """
        return self._user_ttl

    @user_ttl.setter
    def user_ttl(self, user_ttl):
        """Sets the user_ttl of this GatewayCreateProducerOracleDb.

        User TTL  # noqa: E501

        :param user_ttl: The user_ttl of this GatewayCreateProducerOracleDb.  # noqa: E501
        :type: str
        """

        self._user_ttl = user_ttl

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
        if not isinstance(other, GatewayCreateProducerOracleDb):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GatewayCreateProducerOracleDb):
            return True

        return self.to_dict() != other.to_dict()
