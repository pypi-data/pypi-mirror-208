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
from onelogin.models.oauth_token import OauthToken  # noqa: E501
from onelogin.rest import ApiException

class TestOauthToken(unittest.TestCase):
    """OauthToken unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test OauthToken
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `OauthToken`
        """
        model = onelogin.models.oauth_token.OauthToken()  # noqa: E501
        if include_optional :
            return OauthToken(
                access_token = 'xx508xx63817x752xx74004x30705xx92x58349x5x78f5xx34xxxxx51', 
                created_at = '2015-11-11T03:36:18.714Z', 
                expires_in = 36000, 
                refresh_token = 'deprecated', 
                token_type = 'bearer', 
                account_id = 555555
            )
        else :
            return OauthToken(
        )
        """

    def testOauthToken(self):
        """Test OauthToken"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
