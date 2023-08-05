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
from onelogin.models.risk_device import RiskDevice
from onelogin.models.risk_user import RiskUser
from onelogin.models.session import Session
from onelogin.models.source import Source

class TrackRiskEventRequest(BaseModel):
    """
    TrackRiskEventRequest
    """
    verb: StrictStr = Field(..., description="Verbs are used to distinguish between different types of events.")
    ip: StrictStr = Field(..., description="The IP address of the User's request.")
    user_agent: StrictStr = Field(..., description="The user agent of the User's request.")
    user: RiskUser = ...
    source: Optional[Source] = None
    session: Optional[Session] = None
    device: Optional[RiskDevice] = None
    fp: Optional[StrictStr] = Field(None, description="Set to the value of the __tdli_fp cookie.")
    published: Optional[StrictStr] = Field(None, description="Date and time of the event in IS08601 format. Useful for preloading old events. Defaults to date time this API request is received.")
    __properties = ["verb", "ip", "user_agent", "user", "source", "session", "device", "fp", "published"]

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
    def from_json(cls, json_str: str) -> TrackRiskEventRequest:
        """Create an instance of TrackRiskEventRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source
        if self.source:
            _dict['source'] = self.source.to_dict()
        # override the default output from pydantic by calling `to_dict()` of session
        if self.session:
            _dict['session'] = self.session.to_dict()
        # override the default output from pydantic by calling `to_dict()` of device
        if self.device:
            _dict['device'] = self.device.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> TrackRiskEventRequest:
        """Create an instance of TrackRiskEventRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return TrackRiskEventRequest.parse_obj(obj)

        _obj = TrackRiskEventRequest.parse_obj({
            "verb": obj.get("verb"),
            "ip": obj.get("ip"),
            "user_agent": obj.get("user_agent"),
            "user": RiskUser.from_dict(obj.get("user")) if obj.get("user") is not None else None,
            "source": Source.from_dict(obj.get("source")) if obj.get("source") is not None else None,
            "session": Session.from_dict(obj.get("session")) if obj.get("session") is not None else None,
            "device": RiskDevice.from_dict(obj.get("device")) if obj.get("device") is not None else None,
            "fp": obj.get("fp"),
            "published": obj.get("published")
        })
        return _obj

