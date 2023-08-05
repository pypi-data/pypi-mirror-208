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
from onelogin.models.get_enrolled_factors200_response import GetEnrolledFactors200Response  # noqa: E501
from onelogin.rest import ApiException

class TestGetEnrolledFactors200Response(unittest.TestCase):
    """GetEnrolledFactors200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test GetEnrolledFactors200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `GetEnrolledFactors200Response`
        """
        model = onelogin.models.get_enrolled_factors200_response.GetEnrolledFactors200Response()  # noqa: E501
        if include_optional :
            return GetEnrolledFactors200Response(
                status = onelogin.models.error.Error(
                    error = False, 
                    code = 200, 
                    type = 'Success', 
                    message = 'Success', ), 
                data = onelogin.models.get_enrolled_factors_200_response_data.getEnrolledFactors_200_response_data(
                    otp_devices = [
                        onelogin.models.get_enrolled_factors_200_response_data_otp_devices_inner.getEnrolledFactors_200_response_data_otp_devices_inner(
                            active = True, 
                            default = False, 
                            state_token = 'f2402de2b446abd86ea5aa1f79b3fa72b4befacd', 
                            auth_factor_name = 'Onelogin SMS', 
                            phone_number = '+1xxxxxxxxxx', 
                            type_display_name = 'Onelogin SMS', 
                            needs_trigger = True, 
                            user_display_name = 'Rich's Phone', 
                            id = 525509, )
                        ], )
            )
        else :
            return GetEnrolledFactors200Response(
        )
        """

    def testGetEnrolledFactors200Response(self):
        """Test GetEnrolledFactors200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
