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
from onelogin.models.get_risk_scores200_response import GetRiskScores200Response  # noqa: E501
from onelogin.rest import ApiException

class TestGetRiskScores200Response(unittest.TestCase):
    """GetRiskScores200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test GetRiskScores200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `GetRiskScores200Response`
        """
        model = onelogin.models.get_risk_scores200_response.GetRiskScores200Response()  # noqa: E501
        if include_optional :
            return GetRiskScores200Response(
                scores = onelogin.models.get_risk_scores_200_response_scores.getRiskScores_200_response_scores(
                    minimal = 56, 
                    low = 56, 
                    medium = 56, 
                    high = 56, 
                    very_high = 56, ), 
                total = 56
            )
        else :
            return GetRiskScores200Response(
        )
        """

    def testGetRiskScores200Response(self):
        """Test GetRiskScores200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
