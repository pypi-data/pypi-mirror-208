# coding: utf-8

"""
    OneLogin API

    OpenAPI Specification for OneLogin  # noqa: E501

    The version of the OpenAPI document: 3.1.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictStr

class ListMappingConditions200Response(BaseModel):
    """
    ListMappingConditions200Response
    """
    name: Optional[StrictStr] = Field(None, description="Name of Condition")
    value: Optional[StrictStr] = Field(None, description="The unique identifier of the condition. This should be used when defining conditions for a User Mapping")
    __properties = ["name", "value"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> ListMappingConditions200Response:
        """Create an instance of ListMappingConditions200Response from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ListMappingConditions200Response:
        """Create an instance of ListMappingConditions200Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ListMappingConditions200Response.parse_obj(obj)

        _obj = ListMappingConditions200Response.parse_obj({
            "name": obj.get("name"),
            "value": obj.get("value")
        })
        return _obj

