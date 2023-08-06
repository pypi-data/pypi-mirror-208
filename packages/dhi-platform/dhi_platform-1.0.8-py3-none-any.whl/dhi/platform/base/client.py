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

import json, os, sys, urllib.parse, uuid
from . import constants
from json.decoder import JSONDecodeError
from abc import ABC
from http.client import HTTPConnection, HTTPSConnection
from dhi.platform.authentication import MikeCloudIdentity
from .exceptions import MikeCloudException, MikeCloudRestApiException
from typing import Any, Dict, get_type_hints, get_origin, get_args
from enum import Enum
#from .fmt import Format
#import sys
#from argparse import ArgumentParser
#from http.client import HTTPConnection, HTTPSConnection
#from os import environ

class Response:
    def __init__(self, operationid, status, reason, headers, body=None, requestheaders=None, requestBody=None):
        self.__operationId = operationid
        self.__status = status
        self.__reason = reason
        self.__headers = headers
        self.__body = body
        self.__requestHeaders = requestheaders
        self.__requestBody = requestBody

    def Dump(self, file=sys.stdout):
        print(f"{self.Status} {self.Reason}", file=file)
        if self.Body:
            json.dump(self.Body, file, indent=True)

    @property
    def OperationId(self):
        return self.__operationId

    @property
    def Status(self):
        return self.__status

    @property
    def Reason(self):
        return self.__reason

    @property
    def Headers(self):
        return self.__headers

    @property
    def Body(self):
        return self.__body

    @property
    def RequestHeaders(self):
        return self.__requestHeaders

    @property
    def RequestBody(self):
        return self.__requestBody

    @property
    def IsOk(self):
        return self.Status >= 200 and self.Status < 300

    @property
    def IsError(self):
        return not self.IsOk


class Contracts:
    @staticmethod
    def SetBodyField(body, field, value, default=None):
        if value != None:
            body[field] = value
            return value
        if default != None and not field in body:
            body[field] = default
            return default
        return body.get(field)

    @classmethod
    def PrepareField(cls, body, fieldname, default):
        return cls.SetBodyField(body, fieldname, None, default)


class PlatformClientBase(ABC):
    def __init__(self, inspectFnc, verbose=0, **kwargs):
        self.__verbose = verbose
        self.__inspectFnc = inspectFnc

    def _Inspect(self, operationid, level, what, msg=None, obj=None):
        if self.__inspectFnc:
            self.__inspectFnc(operationid, self.__verbose, level, what, msg, obj)

    @property
    def Verbose(self):
        return self.__verbose

    @property
    def NextOperationId(self):
        return str(uuid.uuid1())

    @staticmethod
    def DefaultInspectFnc(operationid, verbose, level, what, msg, obj):
        if verbose and verbose >= level:
            if what:
                print(f"### {what}")
            if msg:
                print(f"{msg}")
            if obj:
                json.dump(obj, sys.stdout, indent=True)
                print("")


class DummyAuthenticator:
    def UpdateHeaders(self, headers):
        pass


class OpenApiKeyAuthenticator:
    def __init__(self, apikey):
        self.__apikey = apikey

    def UpdateHeaders(self, headers):
        if self.__apikey:
            headers["dhi-open-api-key"] = self.__apikey


class BearerAuthenticator:
    def __init__(self, accesstoken, customerid=None, userid=None):
        self.__accesstoken = accesstoken
        self.__customerid = customerid
        self.__userid = userid

    def UpdateHeaders(self, headers):
        if self.__accesstoken:
            headers["Authorization"] = f"Bearer {self.__accesstoken}"
        if self.__customerid:
            headers["dhi-customer-guid"] = self.__customerid
        if self.__userid:
            headers["dhi-user-id"] = self.__userid


class LocalAuthenticator:
    def __init__(self, customerid=None, userid=None, userisadmin=None):
        self.__customerid = customerid
        self.__userid = userid
        self.__userisadmin = userisadmin

    def UpdateHeaders(self, headers):
        if self.__customerid:
            headers["dhi-customer-guid"] = self.__customerid
        if self.__userid:
            headers["dhi-user-id"] = self.__userid
        if self.__userisadmin:
            headers["dhi-user-is-admin"] = self.__userisadmin


class PlatformClient(PlatformClientBase):
    def __init__(self, inspectFnc, includeheaders=None, **kwargs):
        super().__init__(inspectFnc, **kwargs)

        if identity := kwargs.get("identity"):
            if not isinstance(identity, MikeCloudIdentity):
                 raise MikeCloudException("Invalid identity provided")
            kwargs.update(identity.get_parameters())
            kwargs.pop("identity")
            
        self.__InitCoreMetadataUrl(**kwargs)
        #self.__basicHeaders = {"Content-Type": "application/json; charset=UTF-8"}
        self.__basicHeaders = {"Content-Type": "application/json-patch+json", "Accept": "text/plain", "dhi-pythonsdk-version": constants.DHI_PYTHONSDK_VERSION}
        if includeheaders:
            self.__basicHeaders.update(includeheaders)
        self.__authenticator = self.__CreateAuthenticator(**kwargs)
        self._Inspect(self.NextOperationId, 3, "kwargs", None, kwargs)

    def __CreateAuthenticator(self, apikey=None, accesstoken=None, preferapikey=False, customerid=None, userid=None, userisadmin=None, **kwargs):
        if self.IsLocal:
            return LocalAuthenticator(customerid, userid, userisadmin)
        if accesstoken and (not apikey or not preferapikey):
            return BearerAuthenticator(accesstoken, customerid, userid)
        if apikey:
            return OpenApiKeyAuthenticator(apikey)
        return DummyAuthenticator()

    def GetHeaders(self, includeheaders=None, **kwargs):
        return self.GetBasicHeaders(includeheaders, **kwargs)

    @classmethod
    def GetQueryParams(cls, **kwargs):
        params = []
        for name, value in kwargs.items():
            if value:
                #key.capitalize() if capitalize else key
                if isinstance(value, list):
                    params.extend((cls.__FormatParam(name, x) for x in value))
                else:
                    params.append(cls.__FormatParam(name, value))
        return params

    def GetRequest(self, url, queryparams=None, includeheaders=None, **kwargs) -> Response:
        return self.__Request("GET", url, None, queryparams, includeheaders, **kwargs)

    def DeleteRequest(self, url, queryparams=None, includeheaders=None, **kwargs) -> Response:
        return self.__Request("DELETE", url, None, queryparams, includeheaders, **kwargs)

    def PostRequest(self, url, body, queryparams=None, includeheaders=None, **kwargs) -> Response:
        return self.__Request("POST", url, body, queryparams, includeheaders, **kwargs)

    def PutRequest(self, url, body, queryparams=None, includeheaders=None, **kwargs) -> Response:
        return self.__Request("PUT", url, body, queryparams, includeheaders, **kwargs)

    def PatchRequest(self, url, body, queryparams=None, includeheaders=None, **kwargs) -> Response:
        return self.__Request("PATCH", url, body, queryparams, includeheaders, **kwargs)

    @property
    def IsLocal(self):
        return self.__coremetadataaddr.startswith("localhost") or self.__coremetadataaddr.startswith("127.0.0.1")

    @staticmethod
    def GetServiceHeaders(service, headers=None):
        result = headers if headers else {}
        if service:
            result["dhi-service-id"] = service
        return result

    @staticmethod
    def GetVersionHeaders(version, headers=None):
        result = headers if headers else {}
        if version:
            result["api-version"] = version
        return result

    def GetBasicHeaders(self, includeheaders=None, api_version=None, content_type=None, noauthentication=False, **kwargs):
        #headers = {"dhi-open-api-key": apikey, "dhi-project-id": projectid, "dhi-service-id": "engine"}
        headers = self.__basicHeaders.copy()
        if not noauthentication:
            self.__authenticator.UpdateHeaders(headers)
        if api_version:
            headers["api-version"] = api_version
        if projectid := kwargs.get("projectid"):
            headers["dhi-project-id"] = projectid
        if datasetid := kwargs.get("datasetid"):
            headers["dhi-dataset-id"] = datasetid
        if recursivetoken := kwargs.get("recursivetoken"):
            headers["dhi-recursive-token"] = recursivetoken
        if content_type:
            headers["Content-Type"] = content_type
        if includeheaders:
            headers.update(includeheaders)
        return headers

    def GetBasicHeadersV2(self, **kwargs):
        return self.GetBasicHeaders(api_version="2", **kwargs)

    def GetBasicHeadersV3(self, **kwargs):
        return self.GetBasicHeaders(api_version="3", **kwargs)

    @staticmethod
    def __FormatParam(name, value):
        return f"{name}={urllib.parse.quote_plus(value) if isinstance(value, str) else value}"

    def __GetConnection(self, operationid):
        if self.__coremetadatasecure:
            self._Inspect(operationid, 1, "connection", f"https://{self.__coremetadataaddr}")
            return HTTPSConnection(self.__coremetadataaddr)
        else:
            self._Inspect(operationid, 1, "connection", f"http://{self.__coremetadataaddr}")
            return HTTPConnection(self.__coremetadataaddr)
        #self._Inspect(operationid, 1, "connection", "{0}://{1}".format(
        #    "HTTPS" if self.__coremetadatasecure else "HTTP", self.__coremetadataaddr))
        #return HTTPSConnection(self.__coremetadataaddr) if self.__coremetadatasecure else HTTPConnection(self.__coremetadataaddr)

    def __Request(self, method, url, body=None, queryparams=None, includeheaders=None, **kwargs) -> Response:
        try:
            self._Inspect(operationid := self.NextOperationId, 1, "{{")
            conn = self.__GetConnection(operationid)
            if queryparams:
                url = f"{url}{'?'}{'&'.join(queryparams)}"
            self._Inspect(operationid, 1, "request", f"{method} {url}")
            headers = self.GetHeaders(includeheaders, **kwargs)
            if headers:
                self._Inspect(operationid, 2, "headers", None, headers)
            if body:
                self._Inspect(operationid, 2, "requestbody", None, body)
            
            if isinstance(body, str):
                conn.request(method, url, body if body else None, headers=headers)
            else:
                conn.request(method, url, json.dumps(body) if body else None, headers=headers)

            response = conn.getresponse()
            self._Inspect(operationid, 1, "response", f"{response.status} {response.reason}")
            self._Inspect(operationid, 2, "responseheaders", None, dict(response.headers))
            responsestr = response.read()
            conn.close()            
            if responsestr:
                self._Inspect(operationid, 1, "responsebodysize", f"{len(responsestr)}")
                self._Inspect(operationid, 3, "responsebody", responsestr)
                if response.headers.get("Content-Type", "application/json") == "application/x-binary":
                    responsejson = responsestr
                else:
                    responsejson = json.loads(responsestr)
                    self._Inspect(operationid, 2, "responsebodyjson", None, responsejson)
            self.__Raise_if_response_not_ok(response, responsestr)
            if responsestr:
                return Response(operationid, response.status, response.reason, response.headers, responsejson, headers, body)
            return Response(operationid, response.status, response.reason, dict(response.headers), None, headers, body)
        finally:
            self._Inspect(operationid, 1, "}}")

    def __InitCoreMetadataUrl(self, **kwargs):
        if self.__InitUrlAddressAndSecure(**kwargs):
            return True
        else:
            platformenv = self.__GetEnvironment("prod", **kwargs)
            if platformenv and platformenv.lower().endswith("eu"):
                tmp = platformenv.lower()[:-2]
                self.__coremetadataaddr = f"metadata-mike-platform-{tmp}.eu.mike-cloud-{tmp}.com"
                self.__coremetadatasecure = True
            elif platformenv and platformenv == "prod":
                #self.__coremetadataaddr = "metadata-mike-platform-prod.eu.mike-cloud.com"
                self.__coremetadataaddr = "api.mike-cloud.com"
                self.__coremetadatasecure = True
            elif platformenv and platformenv != "local":
                self.__coremetadataaddr = f"api.mike-cloud-{platformenv.lower()}.com"
                self.__coremetadatasecure = True
            else:
                self.__coremetadataaddr = "localhost:51499"
                self.__coremetadatasecure = False

    def __GetEnvironment(self, defaultenvironment, environment=None, **kwargs):
        return environment if environment else defaultenvironment

    def __InitUrlAddressAndSecure(self, metaurl=None, **kwargs):
        if metaurl:
            url = urllib.parse.urlparse(metaurl)
            self.__coremetadataaddr = f"{url.hostname}:{url.port}" if url.port else url.hostname
            self.__coremetadatasecure = url.scheme == "https"
            return True
        return False
    
    def __Raise_if_response_not_ok(self, response, responsestr):
        status = response.status
        if status <200 or status>=400:
            message = f"REST API call failed with status code {response.status}"
            detail = ""
            try:
                if responsestr:
                    problemdetails = json.loads(responsestr)
                    # Problem Details come out with Capitalized keys, this line fixes it:
                    problemdetails = dict(map(lambda k:(k.lower(),problemdetails[k]),problemdetails.keys()))

                    message = problemdetails.get("title", message)
                    detail = problemdetails.get("detail", detail)
                    type = problemdetails.get("type", None)
                    instance = problemdetails.get("instance", None)
                    errors = problemdetails.get("errors", None)

                    if errors:
                        try:
                            detail += json.dumps(errors)
                        except:
                            detail += str(errors) 

                    if detail and not message:
                        message = detail

                    raise MikeCloudRestApiException(message, detail, status, type, instance)
                else:
                    message = "Response body is empty"
                    detail = "Problem Details are not available"
                    raise MikeCloudRestApiException(message, detail, status, responsestr)
            except JSONDecodeError as er:
                raise MikeCloudRestApiException(message, detail, status, responsestr, er)

class DataContract(object):
    def to_dict(self) -> Dict[str, Any]:
        return dict()

    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        pass

    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        return dict()

    def get_dictionary(self, renamed: Dict[str, str]) -> Dict[str, Any]:
        result = vars(self)
        for name, value in result.items():
            if isinstance(value, list):
                result[name] = [x.to_dict() if isinstance(x, DataContract) else x for x in value]
            elif isinstance(value, DataContract):
                result[name] = value.to_dict()
        for o, n in renamed.items():
            if n in result:
                result[o] = result.pop(n)
        return result

    @staticmethod
    def load_from_directory(obj, src_dict: Dict[str, Any], renamed) -> None:
        hints = get_type_hints(type(obj))
        for k, v in src_dict.items():
            if k in renamed:
                k = renamed[k]
            h = hints.get(k)
            if isinstance(h, type):
                if issubclass(h, DataContract):
                    v = h.from_dict(v)
                elif issubclass(h, Enum):
                    v = h(v)
            elif get_origin(h) == list:
                hargs = get_args(h)
                hargstype = hargs[0]
                if issubclass(hargstype, DataContract):
                    v = [hargstype.from_dict(x) for x in v]
                elif issubclass(hargstype, Enum):
                    v = [hargstype(x) for x in v]
            setattr(obj, k, v)

    @staticmethod
    def __has_method(obj, name) -> bool:
        m = getattr(obj, name, None)
        return callable(m)

if __name__ == '__main__':
    print(__file__)
    print(dir())
