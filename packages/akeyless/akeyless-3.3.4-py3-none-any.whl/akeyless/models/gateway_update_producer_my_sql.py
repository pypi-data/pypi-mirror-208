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


class GatewayUpdateProducerMySQL(object):
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
        'mysql_dbname': 'str',
        'mysql_host': 'str',
        'mysql_password': 'str',
        'mysql_port': 'str',
        'mysql_revocation_statements': 'str',
        'mysql_screation_statements': 'str',
        'mysql_username': 'str',
        'name': 'str',
        'new_name': 'str',
        'producer_encryption_key_name': 'str',
        'secure_access_bastion_issuer': 'str',
        'secure_access_enable': 'str',
        'secure_access_host': 'list[str]',
        'secure_access_web': 'bool',
        'ssl': 'bool',
        'ssl_certificate': 'str',
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
        'mysql_dbname': 'mysql-dbname',
        'mysql_host': 'mysql-host',
        'mysql_password': 'mysql-password',
        'mysql_port': 'mysql-port',
        'mysql_revocation_statements': 'mysql-revocation-statements',
        'mysql_screation_statements': 'mysql-screation-statements',
        'mysql_username': 'mysql-username',
        'name': 'name',
        'new_name': 'new-name',
        'producer_encryption_key_name': 'producer-encryption-key-name',
        'secure_access_bastion_issuer': 'secure-access-bastion-issuer',
        'secure_access_enable': 'secure-access-enable',
        'secure_access_host': 'secure-access-host',
        'secure_access_web': 'secure-access-web',
        'ssl': 'ssl',
        'ssl_certificate': 'ssl-certificate',
        'tags': 'tags',
        'target_name': 'target-name',
        'token': 'token',
        'uid_token': 'uid-token',
        'user_ttl': 'user-ttl'
    }

    def __init__(self, db_server_certificates=None, db_server_name=None, delete_protection=None, json=False, mysql_dbname=None, mysql_host='127.0.0.1', mysql_password=None, mysql_port='3306', mysql_revocation_statements=None, mysql_screation_statements=None, mysql_username=None, name=None, new_name=None, producer_encryption_key_name=None, secure_access_bastion_issuer=None, secure_access_enable=None, secure_access_host=None, secure_access_web=False, ssl=False, ssl_certificate=None, tags=None, target_name=None, token=None, uid_token=None, user_ttl='60m', local_vars_configuration=None):  # noqa: E501
        """GatewayUpdateProducerMySQL - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._db_server_certificates = None
        self._db_server_name = None
        self._delete_protection = None
        self._json = None
        self._mysql_dbname = None
        self._mysql_host = None
        self._mysql_password = None
        self._mysql_port = None
        self._mysql_revocation_statements = None
        self._mysql_screation_statements = None
        self._mysql_username = None
        self._name = None
        self._new_name = None
        self._producer_encryption_key_name = None
        self._secure_access_bastion_issuer = None
        self._secure_access_enable = None
        self._secure_access_host = None
        self._secure_access_web = None
        self._ssl = None
        self._ssl_certificate = None
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
        if mysql_dbname is not None:
            self.mysql_dbname = mysql_dbname
        if mysql_host is not None:
            self.mysql_host = mysql_host
        if mysql_password is not None:
            self.mysql_password = mysql_password
        if mysql_port is not None:
            self.mysql_port = mysql_port
        if mysql_revocation_statements is not None:
            self.mysql_revocation_statements = mysql_revocation_statements
        if mysql_screation_statements is not None:
            self.mysql_screation_statements = mysql_screation_statements
        if mysql_username is not None:
            self.mysql_username = mysql_username
        self.name = name
        if new_name is not None:
            self.new_name = new_name
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
        if ssl is not None:
            self.ssl = ssl
        if ssl_certificate is not None:
            self.ssl_certificate = ssl_certificate
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
        """Gets the db_server_certificates of this GatewayUpdateProducerMySQL.  # noqa: E501

        (Optional) DB server certificates  # noqa: E501

        :return: The db_server_certificates of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._db_server_certificates

    @db_server_certificates.setter
    def db_server_certificates(self, db_server_certificates):
        """Sets the db_server_certificates of this GatewayUpdateProducerMySQL.

        (Optional) DB server certificates  # noqa: E501

        :param db_server_certificates: The db_server_certificates of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._db_server_certificates = db_server_certificates

    @property
    def db_server_name(self):
        """Gets the db_server_name of this GatewayUpdateProducerMySQL.  # noqa: E501

        (Optional) Server name for certificate verification  # noqa: E501

        :return: The db_server_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._db_server_name

    @db_server_name.setter
    def db_server_name(self, db_server_name):
        """Sets the db_server_name of this GatewayUpdateProducerMySQL.

        (Optional) Server name for certificate verification  # noqa: E501

        :param db_server_name: The db_server_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._db_server_name = db_server_name

    @property
    def delete_protection(self):
        """Gets the delete_protection of this GatewayUpdateProducerMySQL.  # noqa: E501

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :return: The delete_protection of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._delete_protection

    @delete_protection.setter
    def delete_protection(self, delete_protection):
        """Sets the delete_protection of this GatewayUpdateProducerMySQL.

        Protection from accidental deletion of this item [true/false]  # noqa: E501

        :param delete_protection: The delete_protection of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._delete_protection = delete_protection

    @property
    def json(self):
        """Gets the json of this GatewayUpdateProducerMySQL.  # noqa: E501

        Set output format to JSON  # noqa: E501

        :return: The json of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: bool
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this GatewayUpdateProducerMySQL.

        Set output format to JSON  # noqa: E501

        :param json: The json of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: bool
        """

        self._json = json

    @property
    def mysql_dbname(self):
        """Gets the mysql_dbname of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL DB Name  # noqa: E501

        :return: The mysql_dbname of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_dbname

    @mysql_dbname.setter
    def mysql_dbname(self, mysql_dbname):
        """Sets the mysql_dbname of this GatewayUpdateProducerMySQL.

        MySQL DB Name  # noqa: E501

        :param mysql_dbname: The mysql_dbname of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_dbname = mysql_dbname

    @property
    def mysql_host(self):
        """Gets the mysql_host of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Host  # noqa: E501

        :return: The mysql_host of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_host

    @mysql_host.setter
    def mysql_host(self, mysql_host):
        """Sets the mysql_host of this GatewayUpdateProducerMySQL.

        MySQL Host  # noqa: E501

        :param mysql_host: The mysql_host of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_host = mysql_host

    @property
    def mysql_password(self):
        """Gets the mysql_password of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Password  # noqa: E501

        :return: The mysql_password of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_password

    @mysql_password.setter
    def mysql_password(self, mysql_password):
        """Sets the mysql_password of this GatewayUpdateProducerMySQL.

        MySQL Password  # noqa: E501

        :param mysql_password: The mysql_password of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_password = mysql_password

    @property
    def mysql_port(self):
        """Gets the mysql_port of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Port  # noqa: E501

        :return: The mysql_port of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_port

    @mysql_port.setter
    def mysql_port(self, mysql_port):
        """Sets the mysql_port of this GatewayUpdateProducerMySQL.

        MySQL Port  # noqa: E501

        :param mysql_port: The mysql_port of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_port = mysql_port

    @property
    def mysql_revocation_statements(self):
        """Gets the mysql_revocation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Revocation statements  # noqa: E501

        :return: The mysql_revocation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_revocation_statements

    @mysql_revocation_statements.setter
    def mysql_revocation_statements(self, mysql_revocation_statements):
        """Sets the mysql_revocation_statements of this GatewayUpdateProducerMySQL.

        MySQL Revocation statements  # noqa: E501

        :param mysql_revocation_statements: The mysql_revocation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_revocation_statements = mysql_revocation_statements

    @property
    def mysql_screation_statements(self):
        """Gets the mysql_screation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Creation statements  # noqa: E501

        :return: The mysql_screation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_screation_statements

    @mysql_screation_statements.setter
    def mysql_screation_statements(self, mysql_screation_statements):
        """Sets the mysql_screation_statements of this GatewayUpdateProducerMySQL.

        MySQL Creation statements  # noqa: E501

        :param mysql_screation_statements: The mysql_screation_statements of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_screation_statements = mysql_screation_statements

    @property
    def mysql_username(self):
        """Gets the mysql_username of this GatewayUpdateProducerMySQL.  # noqa: E501

        MySQL Username  # noqa: E501

        :return: The mysql_username of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._mysql_username

    @mysql_username.setter
    def mysql_username(self, mysql_username):
        """Sets the mysql_username of this GatewayUpdateProducerMySQL.

        MySQL Username  # noqa: E501

        :param mysql_username: The mysql_username of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._mysql_username = mysql_username

    @property
    def name(self):
        """Gets the name of this GatewayUpdateProducerMySQL.  # noqa: E501

        Producer name  # noqa: E501

        :return: The name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GatewayUpdateProducerMySQL.

        Producer name  # noqa: E501

        :param name: The name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def new_name(self):
        """Gets the new_name of this GatewayUpdateProducerMySQL.  # noqa: E501

        Producer name  # noqa: E501

        :return: The new_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._new_name

    @new_name.setter
    def new_name(self, new_name):
        """Sets the new_name of this GatewayUpdateProducerMySQL.

        Producer name  # noqa: E501

        :param new_name: The new_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._new_name = new_name

    @property
    def producer_encryption_key_name(self):
        """Gets the producer_encryption_key_name of this GatewayUpdateProducerMySQL.  # noqa: E501

        Dynamic producer encryption key  # noqa: E501

        :return: The producer_encryption_key_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._producer_encryption_key_name

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, producer_encryption_key_name):
        """Sets the producer_encryption_key_name of this GatewayUpdateProducerMySQL.

        Dynamic producer encryption key  # noqa: E501

        :param producer_encryption_key_name: The producer_encryption_key_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._producer_encryption_key_name = producer_encryption_key_name

    @property
    def secure_access_bastion_issuer(self):
        """Gets the secure_access_bastion_issuer of this GatewayUpdateProducerMySQL.  # noqa: E501

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :return: The secure_access_bastion_issuer of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_bastion_issuer

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, secure_access_bastion_issuer):
        """Sets the secure_access_bastion_issuer of this GatewayUpdateProducerMySQL.

        Path to the SSH Certificate Issuer for your Akeyless Bastion  # noqa: E501

        :param secure_access_bastion_issuer: The secure_access_bastion_issuer of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._secure_access_bastion_issuer = secure_access_bastion_issuer

    @property
    def secure_access_enable(self):
        """Gets the secure_access_enable of this GatewayUpdateProducerMySQL.  # noqa: E501

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :return: The secure_access_enable of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._secure_access_enable

    @secure_access_enable.setter
    def secure_access_enable(self, secure_access_enable):
        """Sets the secure_access_enable of this GatewayUpdateProducerMySQL.

        Enable/Disable secure remote access [true/false]  # noqa: E501

        :param secure_access_enable: The secure_access_enable of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._secure_access_enable = secure_access_enable

    @property
    def secure_access_host(self):
        """Gets the secure_access_host of this GatewayUpdateProducerMySQL.  # noqa: E501

        Target DB servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts)  # noqa: E501

        :return: The secure_access_host of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: list[str]
        """
        return self._secure_access_host

    @secure_access_host.setter
    def secure_access_host(self, secure_access_host):
        """Sets the secure_access_host of this GatewayUpdateProducerMySQL.

        Target DB servers for connections (In case of Linked Target association, host(s) will inherit Linked Target hosts)  # noqa: E501

        :param secure_access_host: The secure_access_host of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: list[str]
        """

        self._secure_access_host = secure_access_host

    @property
    def secure_access_web(self):
        """Gets the secure_access_web of this GatewayUpdateProducerMySQL.  # noqa: E501

        Enable Web Secure Remote Access  # noqa: E501

        :return: The secure_access_web of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: bool
        """
        return self._secure_access_web

    @secure_access_web.setter
    def secure_access_web(self, secure_access_web):
        """Sets the secure_access_web of this GatewayUpdateProducerMySQL.

        Enable Web Secure Remote Access  # noqa: E501

        :param secure_access_web: The secure_access_web of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: bool
        """

        self._secure_access_web = secure_access_web

    @property
    def ssl(self):
        """Gets the ssl of this GatewayUpdateProducerMySQL.  # noqa: E501

        Enable/Disable SSL [true/false]  # noqa: E501

        :return: The ssl of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: bool
        """
        return self._ssl

    @ssl.setter
    def ssl(self, ssl):
        """Sets the ssl of this GatewayUpdateProducerMySQL.

        Enable/Disable SSL [true/false]  # noqa: E501

        :param ssl: The ssl of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: bool
        """

        self._ssl = ssl

    @property
    def ssl_certificate(self):
        """Gets the ssl_certificate of this GatewayUpdateProducerMySQL.  # noqa: E501

        SSL connection certificate  # noqa: E501

        :return: The ssl_certificate of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._ssl_certificate

    @ssl_certificate.setter
    def ssl_certificate(self, ssl_certificate):
        """Sets the ssl_certificate of this GatewayUpdateProducerMySQL.

        SSL connection certificate  # noqa: E501

        :param ssl_certificate: The ssl_certificate of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._ssl_certificate = ssl_certificate

    @property
    def tags(self):
        """Gets the tags of this GatewayUpdateProducerMySQL.  # noqa: E501

        Add tags attached to this object  # noqa: E501

        :return: The tags of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this GatewayUpdateProducerMySQL.

        Add tags attached to this object  # noqa: E501

        :param tags: The tags of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def target_name(self):
        """Gets the target_name of this GatewayUpdateProducerMySQL.  # noqa: E501

        Target name  # noqa: E501

        :return: The target_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """Sets the target_name of this GatewayUpdateProducerMySQL.

        Target name  # noqa: E501

        :param target_name: The target_name of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._target_name = target_name

    @property
    def token(self):
        """Gets the token of this GatewayUpdateProducerMySQL.  # noqa: E501

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :return: The token of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this GatewayUpdateProducerMySQL.

        Authentication token (see `/auth` and `/configure`)  # noqa: E501

        :param token: The token of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def uid_token(self):
        """Gets the uid_token of this GatewayUpdateProducerMySQL.  # noqa: E501

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :return: The uid_token of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._uid_token

    @uid_token.setter
    def uid_token(self, uid_token):
        """Sets the uid_token of this GatewayUpdateProducerMySQL.

        The universal identity token, Required only for universal_identity authentication  # noqa: E501

        :param uid_token: The uid_token of this GatewayUpdateProducerMySQL.  # noqa: E501
        :type: str
        """

        self._uid_token = uid_token

    @property
    def user_ttl(self):
        """Gets the user_ttl of this GatewayUpdateProducerMySQL.  # noqa: E501

        User TTL  # noqa: E501

        :return: The user_ttl of this GatewayUpdateProducerMySQL.  # noqa: E501
        :rtype: str
        """
        return self._user_ttl

    @user_ttl.setter
    def user_ttl(self, user_ttl):
        """Sets the user_ttl of this GatewayUpdateProducerMySQL.

        User TTL  # noqa: E501

        :param user_ttl: The user_ttl of this GatewayUpdateProducerMySQL.  # noqa: E501
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
        if not isinstance(other, GatewayUpdateProducerMySQL):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GatewayUpdateProducerMySQL):
            return True

        return self.to_dict() != other.to_dict()
