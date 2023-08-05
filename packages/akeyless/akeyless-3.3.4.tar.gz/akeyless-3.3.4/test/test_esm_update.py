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
from akeyless.models.esm_update import EsmUpdate  # noqa: E501
from akeyless.rest import ApiException

class TestEsmUpdate(unittest.TestCase):
    """EsmUpdate unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test EsmUpdate
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = akeyless.models.esm_update.EsmUpdate()  # noqa: E501
        if include_optional :
            return EsmUpdate(
                binary_value = True, 
                description = '0', 
                esm_name = '0', 
                json = True, 
                secret_id = '0', 
                tags = {
                    'key' : '0'
                    }, 
                token = '0', 
                uid_token = '0', 
                value = '0'
            )
        else :
            return EsmUpdate(
                esm_name = '0',
                secret_id = '0',
                value = '0',
        )

    def testEsmUpdate(self):
        """Test EsmUpdate"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
