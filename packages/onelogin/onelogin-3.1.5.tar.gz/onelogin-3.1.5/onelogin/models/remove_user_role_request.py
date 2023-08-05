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


from typing import List
from pydantic import BaseModel, conlist
from onelogin.models.remove_user_role_request_role_id_array_inner import RemoveUserRoleRequestRoleIdArrayInner

class RemoveUserRoleRequest(BaseModel):
    """
    RemoveUserRoleRequest
    """
    role_id_array: conlist(RemoveUserRoleRequestRoleIdArrayInner) = ...
    __properties = ["role_id_array"]

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
    def from_json(cls, json_str: str) -> RemoveUserRoleRequest:
        """Create an instance of RemoveUserRoleRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in role_id_array (list)
        _items = []
        if self.role_id_array:
            for _item in self.role_id_array:
                if _item:
                    _items.append(_item.to_dict())
            _dict['role_id_array'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> RemoveUserRoleRequest:
        """Create an instance of RemoveUserRoleRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return RemoveUserRoleRequest.parse_obj(obj)

        _obj = RemoveUserRoleRequest.parse_obj({
            "role_id_array": [RemoveUserRoleRequestRoleIdArrayInner.from_dict(_item) for _item in obj.get("role_id_array")] if obj.get("role_id_array") is not None else None
        })
        return _obj

