# Copyright (c) 2021 DHI A/S - DHI Water Environment Health 
# All rights reserved.
# 
# This code is licensed under the MIT License.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import asyncio, json, sys, uuid
from signalr_async.netcore import Hub, Client
from signalr_async.netcore.protocols import JsonProtocol, MessagePackProtocol
from types import TracebackType
from typing import List, Optional, Type
from datetime import datetime

class PubsubSession:
    def __init__(self, clientv2, clientv3, verbose, file=sys.stdout):
        self._clientv2 = clientv2
        self._clientv3 = clientv3
        self._verbose = verbose
        self._file = file
        self._pubsubconnectedevent = asyncio.Event()
        self._client = None
    async def __aenter__(self) -> "PubsubSession":
        await self.start()
        return self
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.stop()
    def print(self, msg):
        print(msg, file=self._file)
    async def wait_pubsubconnected(self):
        await self._pubsubconnectedevent.wait()
    def on_connect(self, sessionid, connectionid):
        if self._verbose > 1:
            self.print(f"CONNECT, {sessionid}, {connectionid}")
        self._pubsubconnectedevent.set()
    def on_reconnect(self, sessionid):
        if self._verbose > 1:
            self.print(f"RECONNECT, {sessionid}")
    def on_disconnect(self, sessionid):
        if self._verbose > 1:
            self.print(f"DISCONNECT, {sessionid}")
    def on_error(self, sessionid):
        self.print(f"ERROR({sessionid})")
        self._finishedevent.set()
    async def on_update(self, event):
        if self._verbose > 1:
            self.print(f"EVENT {json.dumps(event, indent=True)}")
        return True
    async def start(self):
        if self._client:
            await self._client.start()
    async def stop(self):
        if self._client:
            await self._client.stop()
    async def wait(self, timeout: Optional[float] = None):
        if self._client:
            await self._client.wait(timeout)
    def subscribe(self, projectid, sources: List[str], offset: int, offsetpoint: str):
        dhisastoken = self._clientv2.GetSasTokenV2(projectid).Body.get("data")
        huburl = self._clientv3.GetServiceUrlV3("pubsub").Body.get("data")
        if huburl.endswith("/api/"):
            huburl = huburl[0:-5]
        elif huburl.endswith("/api"):
            huburl = huburl[0:-4]
        subscribeurl = f"{huburl}/v1"

        hub = PubsubSubscribeHub(sources, offset, offsetpoint, self)

        headers = { "dhi-sas-token": dhisastoken }
        self._client = Client(subscribeurl, hub,
            connection_options = { #"protocol": MessagePackProtocol(),
                "http_client_options": { "headers": headers }, "ws_client_options": { "headers": headers, "timeout": 1.0 } })

        return self

class PubsubResourceSession(PubsubSession):
    def __init__(self, clientv2, clientv3, verbose, file=sys.stdout):
        super().__init__(clientv2, clientv3, verbose, file)
        self._resourceid = None
        self._resourcereadyevent = asyncio.Event()
    def set_resourceid(self, value):
        self._resourceid = value
        self._resourcereadyevent.set()
    async def on_update(self, event):
        await self._resourcereadyevent.wait()
        if event.get("resourceid") == self._resourceid:
            return await super().on_update(event)
        return False

class ExecutionSession(PubsubResourceSession):
    def __init__(self, showlog, clientv2, clientv3, verbose, file=sys.stdout):
        super().__init__(clientv2, clientv3, verbose, file)
        self._showlog = showlog
        self._resourceid = None
        self._resourcereadyevent = asyncio.Event()
        self._finishedevent = asyncio.Event()
    async def wait_finished(self):
        await self._finishedevent.wait()
    def on_error(self, sessionid):
        super().on_error(sessionid)
        self._finishedevent.set()
    async def on_update(self, event):
        if await super().on_update(event):
            self._showrunprogress(event)
            if self._is_finished_event(event):
                self._finishedevent.set()
    def _is_finished_event(self, event):
        eventtype = event.get("type")
        eventdata = event.get("data")
        if eventtype == "dhi.waterdata.engines.eventing.contracts.messages.v3.engineexecutionstatuschangedmessage" and eventdata:
            eventdatastatus = eventdata.get("Status")
            if eventdatastatus == "Success" and eventdata["RunningSetupIndex"]+1 == eventdata["TotalNumberOfSetups"] \
                or eventdatastatus == "Failure" or eventdatastatus == "Cancelled":
                return True
        return False
    def _showrunprogress(self, event):
        eventtype = event.get("type")
        eventdata = event.get("data")
        msg = None
        if self._showlog:
            if eventtype == "dhi.waterdata.engines.eventing.contracts.messages.v3.engineexecutionlogupdatemessage" and eventdata:
                logfile = eventdata.get("LogFile")
                loglines = eventdata.get("LogLines")
                for line in loglines:
                    self.print(f"{logfile}:{line}")
        if self._verbose > 0:
            if eventtype == "dhi.waterdata.engines.eventing.contracts.messages.v3.engineexecutionstatuschangedmessage" and eventdata:
                status = eventdata.get("Status")
                message = eventdata.get("Message")
                index = eventdata.get("RunningSetupIndex")
                index = index+1 if index != None else ""
                count = eventdata.get("TotalNumberOfSetups")
                msg = f"status={status}, {index}/{count}, {message}" if message else f"status={status}, {index}/{count}"
            elif eventtype == "dhi.waterdata.engines.eventing.contracts.messages.v3.engineexecutionprogressmessage" and eventdata:
                progressinfo = eventdata.get("EngineExecutionProgress")
                if progressinfo:
                    progre = progressinfo.get("PROGRE")
                    index = eventdata.get("RunningSetupIndex")
                    index = index+1 if index != None else ""
                    count = eventdata.get("TotalNumberOfSetups")
                    msg = f"progress={progre}, {index}/{count}"
            else:
                if not eventtype.startswith("dhi.waterdata.engines.eventing.contracts.messages.v2."):
                    msg = f"event={eventtype}"
        if msg:
            self.print(f"{msg}")

class PubsubSubscribeHub(Hub):
    def __init__(self, sources: List[str], offset: int, offsetpoint: str, pubsubsession: PubsubSession):
        super().__init__("subscribe")
        self._subscriptionid = f"dhi-platform-sdk-py-{datetime.now():%Y%m%dT%H%M%S%f}-{uuid.uuid4().hex}"
        self._sources = sources
        self._offset = offset
        self._offsetpoint = offsetpoint
        self._pubsubsession = pubsubsession
    async def on_connect(self, connection_id: str) -> None:
        """Will be awaited after connection established"""
        await self.subscribe()
        if self._pubsubsession:
            self._pubsubsession.on_connect(self._subscriptionid, connection_id)
    async def on_disconnect(self) -> None:
        """Will be awaited after client disconnection"""
        if self._pubsubsession:
            self._pubsubsession.on_disconnect(self._subscriptionid)
    async def on_reconnect(self) -> None:
        if self._pubsubsession:
            self._pubsubsession.on_reconnect(self._subscriptionid)
    async def on_error(self) -> None:
        if self._pubsubsession:
            self._pubsubsession.on_error(self._subscriptionid)
    async def on_Update(self, event) -> None:
        """Invoked by server on (Update)"""
        if self._pubsubsession:
            await self._pubsubsession.on_update(json.loads(event))
    async def subscribe(self) -> bool:
        """Invoke (Subscribe) on server"""
        sub = {
            "SubscriptionId": self._subscriptionid,
            "Filter": { "Sources": self._sources },
            "Condition": { "Offset": self._offset, "OffsetPoint": self._offsetpoint } }
        return await self.invoke("Subscribe", sub)

if __name__ == '__main__':
    print(__file__)
    print(dir())
