# coding: utf-8

"""
    OneLogin API

    OpenAPI Specification for OneLogin  # noqa: E501

    The version of the OpenAPI document: 3.1.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import unittest
import datetime

import onelogin
from onelogin.models.role import Role  # noqa: E501
from onelogin.rest import ApiException

class TestRole(unittest.TestCase):
    """Role unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Role
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Role`
        """
        model = onelogin.models.role.Role()  # noqa: E501
        if include_optional :
            return Role(
                id = 56, 
                name = '', 
                apps = [234,567,777], 
                users = [
                    56
                    ], 
                admins = [
                    56
                    ]
            )
        else :
            return Role(
                name = '',
        )
        """

    def testRole(self):
        """Test Role"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
