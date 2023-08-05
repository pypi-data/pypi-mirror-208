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
from onelogin.models.brand_req import BrandReq  # noqa: E501
from onelogin.rest import ApiException

class TestBrandReq(unittest.TestCase):
    """BrandReq unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test BrandReq
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `BrandReq`
        """
        model = onelogin.models.brand_req.BrandReq()  # noqa: E501
        if include_optional :
            return BrandReq(
                id = 912, 
                enabled = True, 
                name = 'ACME'
            )
        else :
            return BrandReq(
        )
        """

    def testBrandReq(self):
        """Test BrandReq"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
