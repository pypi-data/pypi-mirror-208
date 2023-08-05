# coding: utf-8

"""
    Akeyless API

    The purpose of this application is to provide access to Akeyless API.  # noqa: E501

    The version of the OpenAPI document: 2.0
    Contact: support@akeyless.io
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import akeyless
from akeyless.models.hmac import Hmac  # noqa: E501
from akeyless.rest import ApiException

class TestHmac(unittest.TestCase):
    """Hmac unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Hmac
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = akeyless.models.hmac.Hmac()  # noqa: E501
        if include_optional :
            return Hmac(
                display_id = '0', 
                hash_function = 'sha-256', 
                input_format = '0', 
                item_id = 56, 
                json = True, 
                key_name = '0', 
                plaintext = '0', 
                token = '0', 
                uid_token = '0'
            )
        else :
            return Hmac(
                key_name = '0',
        )

    def testHmac(self):
        """Test Hmac"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
