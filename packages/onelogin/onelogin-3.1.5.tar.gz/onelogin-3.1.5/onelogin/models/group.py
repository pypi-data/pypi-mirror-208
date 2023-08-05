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
from pydantic import BaseModel, Field, StrictInt, StrictStr

class Group(BaseModel):
    """
    Group
    """
    id: Optional[StrictInt] = Field(None, description="Group's unique Onelogin ID")
    name: Optional[StrictStr] = Field(None, description="Group name")
    reference: Optional[StrictStr] = Field(None, description="Deprecated. Will always show the attribute nil=\"true\".")
    __properties = ["id", "name", "reference"]

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
    def from_json(cls, json_str: str) -> Group:
        """Create an instance of Group from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Group:
        """Create an instance of Group from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Group.parse_obj(obj)

        _obj = Group.parse_obj({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "reference": obj.get("reference")
        })
        return _obj

