# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "pubsub" "--classname" "PubSubGenClientV" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\pubsubgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/pubsub/v1"
# 2022-01-13 19:03:34.024669Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/pubsub/v1
# DHI Water Data Eventing API - Version 1
# API for publishing and subscribing to events
# 1

EventDataV1Type = TypeVar("EventDataV1Type", bound="EventDataV1")

@attr.s(auto_attribs=True)
class EventDataV1(DataContract):
    """See https://github.com/cloudevents/spec/blob/master/spec.md

    """
    source: str = None
    type: str = None
    subject: str = None
    dataSchema: str = None
    data: None = None
    time: str = None
    operationId: str = None
    resourceId: str = None
    isTransient: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: EventDataV1Type, src_dict: Dict[str, Any]) -> EventDataV1Type:
        obj = EventDataV1()
        obj.load_dict(src_dict)
        return obj

ProblemDetailsV1Type = TypeVar("ProblemDetailsV1Type", bound="ProblemDetailsV1")

@attr.s(auto_attribs=True)
class ProblemDetailsV1(DataContract):
    type: str = None
    title: str = None
    status: int = None
    detail: str = None
    instance: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProblemDetailsV1Type, src_dict: Dict[str, Any]) -> ProblemDetailsV1Type:
        obj = ProblemDetailsV1()
        obj.load_dict(src_dict)
        return obj

ValidationProblemDetailsV1Type = TypeVar("ValidationProblemDetailsV1Type", bound="ValidationProblemDetailsV1")

@attr.s(auto_attribs=True)
class ValidationProblemDetailsV1(ProblemDetailsV1):
    errors: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ProblemDetailsV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ValidationProblemDetailsV1Type, src_dict: Dict[str, Any]) -> ValidationProblemDetailsV1Type:
        obj = ValidationProblemDetailsV1()
        obj.load_dict(src_dict)
        return obj

class PubSubGenClientV1(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("pubsub"), **kwargs)

    def CreateEvent(self, projectid, body) -> Response:
        """Create cloud event

        Event
        POST /api/eventing/event
        """
        return self.PostRequest("/api/eventing/event", body, None, api_version="1", projectid=projectid)
