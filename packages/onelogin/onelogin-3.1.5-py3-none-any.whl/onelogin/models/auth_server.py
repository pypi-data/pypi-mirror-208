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
from onelogin.models.auth_server_configuration import AuthServerConfiguration

class AuthServer(BaseModel):
    """
    base resource for configuring api authorization in OneLogin
    """
    id: Optional[StrictInt] = Field(None, description="Auth server unique ID in Onelogin")
    name: StrictStr = Field(..., description="Name of the API.")
    description: StrictStr = Field(..., description="Description of what the API does.")
    configuration: AuthServerConfiguration = ...
    __properties = ["id", "name", "description", "configuration"]

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
    def from_json(cls, json_str: str) -> AuthServer:
        """Create an instance of AuthServer from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                            "id",
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of configuration
        if self.configuration:
            _dict['configuration'] = self.configuration.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> AuthServer:
        """Create an instance of AuthServer from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return AuthServer.parse_obj(obj)

        _obj = AuthServer.parse_obj({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "configuration": AuthServerConfiguration.from_dict(obj.get("configuration")) if obj.get("configuration") is not None else None
        })
        return _obj

