import datetime
import json
import logging
import threading
from typing import List
from signalrcore import hub_connection_builder
import uuid
from dhi.platform.base.exceptions import MikeCloudException
from dhi.platform.metadata import MetadataClient


class EngineSubscription():
    def __init__(self) -> None:
        self._resourceId = None
        self._resourceIdEvent = threading.Event()
        self._synchronization_event = threading.Event()

    def wait(self):
        self._synchronization_event.wait()

    def set(self):
        self._synchronization_event.set()

    def set_resource_id(self, resourceId):
        self._resourceId = resourceId
        self._resourceIdEvent.set()

    def handle_message(self, event:List[str], on_success_handler, on_failed_handler, on_cancelled_handler):
        """
        This function shuold be used as engine execution message handler to control engine execution process.
        :param synchronization_event: threading.Event to signal finished engine execution
        :param on_success_handler: callable to run on sucess with one parameter (the event)
        :param on_failed_handler: callable to run on failure with one parameter (the event)
        :param on_cancelled_handler: callable to run on cancellation with one parameter (the event)
        """
        if not callable(on_success_handler):
            raise MikeCloudException("Parameters on_success_handler must be callable")

        if not callable(on_failed_handler):
            raise MikeCloudException("Parameter on_failed_handler must be callable")
        
        if not callable(on_cancelled_handler):
            raise MikeCloudException("Parameter on_cancelled_handler must be callable")

        if len(event) !=1:
            raise MikeCloudException("Expected a single event, obtained " + str(len(event)), event)
        event = event[0]

        try:
            event = json.loads(event)
        except Exception as ex:
            raise MikeCloudException("Cannot deserialize event message", ex)

        self._resourceIdEvent.wait()
        if event["type"] == "dhi.waterdata.engines.eventing.contracts.messages.v3.engineexecutionstatuschangedmessage":
            resourceId = event.get("resourceid", None)
            if resourceId == self._resourceId:
                data = event["data"]
                status = data["Status"]
                if data.get("Status", None) == "Success":
                    if data["RunningSetupIndex"] + 1 == data["TotalNumberOfSetups"]:
                        # the execution has finished we can stop the subscription (set subscription connectionid stopped on a synchronization object)
                        on_success_handler(event)
                        self._synchronization_event.set()
                    else:
                        # one stage in execution has finished
                        pass
                if status == "Failed" or status == "Failure":
                    # we can stop the subscription (set subscription connectionid stopped on a synchronization object)
                    on_failed_handler(event)
                    self._synchronization_event.set()
                if status == "Cancelled":
                    # we can stop the subscription (set subscription connectionid stopped on a synchronization object)
                    on_cancelled_handler(event)
                    self._synchronization_event.set()


class EventSubscription():
    def __init__(self, hub_connection) -> None:
        self._hub_connection = hub_connection
        self._hub_connection.on_open(self._subscribe)
        self._subscription_id = str(uuid.uuid4())

    def _subscribe(self):
        sub = {
            "SubscriptionId": self._subscription_id
        }

        if self._filter:
            sub["Filter"] = self._filter

        sub["Condition"] = { 
            "Offset": self._offset
        }

        if self._offset_point:
            sub["Condition"]["OffsetPoint"] = self._offset_point

        self._hub_connection.send("Subscribe", [sub])

    def start_and_subscribe(self, filter:dict=None, offset:int=200, offset_point:str=None) -> str:
        """
        Start the subscription and subscribe to the events.
        :param filter: limit the events to read, e.g. {"Sources": ["/someservice/someoperation/v1/"]}
        :param offset: How many events to skip at the beginning of reading, e.g. 100 = Beginning, 200 = End, 300 = Point
        :param offset_point: Indicates where reading of events should start if offset is 300, e.g. "1057"
        :returns: Subscription ID
        :rtype: str
        """
        self._filter = filter
        self._offset = offset
        self._offset_point = offset_point
        self._hub_connection.start()

    def stop(self):
        """
        Stop the connection
        """
        self._hub_connection.stop()


class EventSubscriptionBuilder():
    def __init__(self, metadata_client:MetadataClient, project_id) -> None:
        self._project_id = project_id
        self._automatic_reconnect_options = {
            "type": "raw",
            "keep_alive_interval": 10,
            "reconnect_interval": 5,
            "max_attempts": 5
        }
        self._logging_level = logging.ERROR
        self._on_close_handler = lambda: None
        self._on_update_handler = lambda m: None
        self._eventing_on_error = lambda m: None
        self._metadata3 = metadata_client

    def _validate(self):
        messages = []

        if not self._automatic_reconnect_options:
            messages.append("Event subscription token is required")

        if messages:
            raise MikeCloudException("Invalid connection", messages)

    def _handle_error_and_stop_events(self, handler):
        if self._engine_message_handler:
            self._engine_message_handler.set()
        handler()
        
    def with_logging_level(self, logging_level=logging.ERROR):
        """Override default logging level"""
        self._logging_level = logging_level
        return self

    def with_on_close_handler(self, handler):
        """Configure a function to run when the connection is closed
        :param handler: callable with zero parameters
        """
        if not callable(handler):
            raise MikeCloudException("Parameter handler must be callable")
        self._on_close_handler = handler
        return self
    
    def with_message_handler(self, handler):
        """Configure a function to run when the connection receives an event
        :param handler: callable with one parameter (the event)
        """
        if not callable(handler):
            raise MikeCloudException("Parameter handler must be callable")
        self._on_update_handler = handler
        return self

    def with_eventing_error_handler(self, handler):
        """Configure a function to run when the event communication fails
        :param handler: callable with zero parameters
        """
        self._eventing_on_error = lambda: self._handle_error_and_stop_events(handler)
        return self

    def with_engine_handler(self, engine_message_handler:EngineSubscription, on_success_handler, on_failed_handler, on_cancelled_handler):
        """Configure engine execution message handling.
        This method is intended to be used only when subscribing for events in the context of DHI MIKE Cloud Engine Execution
        :param synchronization_event: threadding.Event to be used to by the calling code to detect when engine execution has finished
        :param on_success_handler: callable to run on sucess with one parameter (the event)
        :param on_failed_handler: callable to run on failure with one parameter (the event)
        :param on_cancelled_handler: callable to run on cancellation with one parameter (the event)
        """
        if not callable(on_success_handler):
            raise MikeCloudException("Parameters on_success_handler must be callable")

        if not callable(on_failed_handler):
            raise MikeCloudException("Parameter on_failed_handler must be callable")
    
        if not callable(on_cancelled_handler):
            raise MikeCloudException("Parameter on_cancelled_handler must be callable")
        
        self._engine_message_handler = engine_message_handler
        self._engine_on_success_handler = on_success_handler
        self._engine_on_failed_handler = on_failed_handler
        self._engine_on_cancelled_handler = on_cancelled_handler

        return self

    def with_automatic_reconnect_options(self, keep_alive_interval:int=10, reconnect_interval:int=5, max_attempts:int=5, type="raw"):
        """Override default automatic reconnect options"""
        self._automatic_reconnect_options["keep_alive_interval"] = keep_alive_interval
        self._automatic_reconnect_options["reconnect_interval"] = reconnect_interval
        self._automatic_reconnect_options["max_attempts"] = max_attempts
        self._automatic_reconnect_options["type"] = type
        return self
    
    def build(self) -> EventSubscription:
        self._validate()

        url = self._metadata3.get_service_url("pubsub")
        url = url.rstrip("api").rstrip("api/")

        expiration = datetime.timedelta(hours=23)
        token = self._metadata3.get_sas_token_string(self._project_id, None, expiration)

        hub_connection = hub_connection_builder.HubConnectionBuilder()\
            .with_url(url + "/v1/subscribe",
                options={
                    "headers": {
                        "dhi-sas-token": token
                    },
                    "verify_ssl": False # TODO: REMOVE
                })\
            .configure_logging(self._logging_level, socket_trace=True)\
            .with_automatic_reconnect(self._automatic_reconnect_options)\
            .build()

        if self._on_close_handler:
            hub_connection.on_close(self._on_close_handler)

        if self._on_update_handler:
            hub_connection.on("Update", self._on_update_handler)
        
        if self._eventing_on_error:
            hub_connection.on_error(self._eventing_on_error)
        
        if self._engine_message_handler:
            hub_connection.on("Update", lambda m: self._engine_message_handler.handle_message(m, self._engine_on_success_handler, self._engine_on_failed_handler, self._engine_on_cancelled_handler))

        return EventSubscription(hub_connection)
