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
from onelogin.models.user import User  # noqa: E501
from onelogin.rest import ApiException

class TestUser(unittest.TestCase):
    """User unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test User
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `User`
        """
        model = onelogin.models.user.User()  # noqa: E501
        if include_optional :
            return User(
                id = 56, 
                username = '', 
                email = '', 
                firstname = '', 
                lastname = '', 
                title = '', 
                department = '', 
                company = '', 
                comment = '', 
                group_id = 56, 
                role_ids = [
                    56
                    ], 
                phone = '', 
                state = 0, 
                status = 0, 
                directory_id = 56, 
                trusted_idp_id = 56, 
                manager_ad_id = '', 
                manager_user_id = '', 
                samaccountname = '', 
                member_of = '', 
                userprincipalname = '', 
                distinguished_name = '', 
                external_id = '', 
                activated_at = '', 
                last_login = '', 
                invitation_sent_at = '', 
                updated_at = '', 
                preferred_locale_code = '', 
                created_at = '', 
                invalid_login_attempts = 56, 
                locked_until = '', 
                password_changed_at = '', 
                password = '', 
                password_confirmation = '', 
                password_algorithm = '', 
                salt = ''
            )
        else :
            return User(
        )
        """

    def testUser(self):
        """Test User"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
