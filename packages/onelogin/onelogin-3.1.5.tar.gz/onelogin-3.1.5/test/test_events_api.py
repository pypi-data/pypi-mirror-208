# coding: utf-8

"""
    OneLogin API

    OpenAPI Specification for OneLogin  # noqa: E501

    The version of the OpenAPI document: 3.1.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import unittest

import onelogin
from onelogin.api.events_api import EventsApi  # noqa: E501
from onelogin.rest import ApiException


class TestEventsApi(unittest.TestCase):
    """EventsApi unit test stubs"""

    def setUp(self):
        self.api = onelogin.api.events_api.EventsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_event_by_id(self):
        """Test case for get_event_by_id

        Get Event by ID  # noqa: E501
        """
        pass

    def test_get_event_types(self):
        """Test case for get_event_types

        Get Event Types  # noqa: E501
        """
        pass

    def test_get_events(self):
        """Test case for get_events

        Get Events  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
