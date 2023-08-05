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



from pydantic import BaseModel
from onelogin.models.saml_app_all_of_parameters_saml_username import SamlAppAllOfParametersSamlUsername

class SamlAppAllOfParameters(BaseModel):
    """
    SamlAppAllOfParameters
    """
    saml_username: SamlAppAllOfParametersSamlUsername = ...
    __properties = ["saml_username"]

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
    def from_json(cls, json_str: str) -> SamlAppAllOfParameters:
        """Create an instance of SamlAppAllOfParameters from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of saml_username
        if self.saml_username:
            _dict['saml_username'] = self.saml_username.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> SamlAppAllOfParameters:
        """Create an instance of SamlAppAllOfParameters from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return SamlAppAllOfParameters.parse_obj(obj)

        _obj = SamlAppAllOfParameters.parse_obj({
            "saml_username": SamlAppAllOfParametersSamlUsername.from_dict(obj.get("saml_username")) if obj.get("saml_username") is not None else None
        })
        return _obj

