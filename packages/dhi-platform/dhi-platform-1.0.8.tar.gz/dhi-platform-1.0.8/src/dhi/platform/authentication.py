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

import codecs
import pickle
import platform
import uuid
from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential, TokenCachePersistenceOptions
from collections import namedtuple
from types import SimpleNamespace
from dhi.platform.base.exceptions import MikeCloudException
from dhi.platform.config import ClientConfig
from abc import ABC, abstractmethod


#import adal, azure.common.credentials, pickle
#from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, SharedTokenCacheCredential
#from msal_interactive_token_acquirer import MsalInteractiveTokenAcquirer
#from typing import NamedTuple


class ClientAuthentication:
    @classmethod
    def RefreshToken(cls, environment, accesstoken):
        info = cls.__GetAuthInfo(environment, "meta")
        if info:
            scopes = [f"{info.appid}/user_impersonation"]
            authsaved = accesstoken.get("authenticationrecord")
            if authsaved:
                options = _AuthenticationHelper.GetDefaultTokenCacheOptions()
                auth = pickle.loads(codecs.decode(authsaved.encode(), "base64"))
                credential = _AuthenticationHelper.GetDefaultInteractiveCredential(authentication_record=auth, cache_persistence_options=options)
                try:
                    token = credential.get_token(*scopes)
                except:
                    token = None
                if token:
                    auth = credential.authenticate(scopes=scopes)
                    authb64 = codecs.encode(pickle.dumps(auth), "base64").decode()
                    #return (cls.__AccessToken(token.token, token.expires_on, auth.username, authb64)._asdict(), token.token)
                    return (cls.__AccessToken(None, token.expires_on, auth.username, authb64)._asdict(), token.token)
        return (None, None)

    @classmethod
    def AcquireTokenInteractively(cls, environment):
        info = cls.__GetAuthInfo(environment, "meta")
        if info:
            #authorityUrl = f"https://login.microsoftonline.com/{tenant}"
            #context = adal.AuthenticationContext(authorityUrl, validate_authority=tenant != "adfs")
            #resource = "00000002-0000-0000-c000-000000000000"
            #clientSecret = ""
            #return context.acquire_token_with_client_credentials(resource, clientId, clientSecret)
            #return ontext.acquire_token(resource, userId, clientId)
            #
            #scopes = [f"{metaResourceId}/user_impersonation"]
            #msal = MsalInteractiveTokenAcquirer(tenant, clientId, scopes)
            #msal.acquire_token_interactively()
            #return msal.access_token()
            #
            #azure.common.credentials.InteractiveCredentials()
            #
            authority = "login.microsoftonline.com"
            scopes = [f"{info.appid}/user_impersonation"]
            #cacheCredential = SharedTokenCacheCredential(authority=authority, tenant_id=tenant)
            #token = cacheCredential.get_token(*scopes)
            options = _AuthenticationHelper.GetDefaultTokenCacheOptions()
            credential = _AuthenticationHelper.GetDefaultInteractiveCredential(authority=authority, tenant_id=info.tenant, client_id=info.clientid, cache_persistence_options=options)
            try:
                token = credential.get_token(*scopes)
            except:
                token = None
            if token:
                auth = credential.authenticate(scopes=scopes)
                authb64 = codecs.encode(pickle.dumps(auth), "base64").decode()
                #return (cls.__AccessToken(token.token, token.expires_on, auth.username, authb64)._asdict(), token.token)
                return (cls.__AccessToken(None, token.expires_on, auth.username, authb64)._asdict(), token.token)
        return (None, None)

    @classmethod
    def __GetAuthInfo(cls, environment, app):
        if env := cls.__config.get(environment):
            return SimpleNamespace(tenant=env.tenant, clientid=env.clientid, appid=env.apps.get(app))
        return None

    __AccessToken = namedtuple("__AccessToken", ["accesstoken", "expireson", "username", "authenticationrecord"])

    __EnvironmentAuthInfo = namedtuple("__EnvironmentAuthInfo", ["environment", "tenant", "clientid", "apps"])

    __config = {
        # PROD
        "prod": __EnvironmentAuthInfo("prod", "dhigroupext.onmicrosoft.com", "aa00293d-f5dd-4ab6-a3c8-28f894149572", {"meta": "0dc51ba3-5c5e-4703-ba89-322411a51197"}),
        # PREPROD ?
        "preprod": __EnvironmentAuthInfo("preprod", "dhigrouppreprod.onmicrosoft.com", "aa00293d-f5dd-4ab6-a3c8-28f894149572", {"meta": "0dc51ba3-5c5e-4703-ba89-322411a51197"}),
        # TEST
        "test": __EnvironmentAuthInfo("test", "dhigrouptest.onmicrosoft.com", "189228fc-e229-4f7d-99c2-ec5161f5d31a", {"meta": "14583d65-56bc-4bff-9ace-7e80cbdc8944"}),
        # DEV0 - dhi.core.dev.uitest app.
        "DEV0": __EnvironmentAuthInfo("DEV0", "dhigroupdev.onmicrosoft.com", "ffa42221-f5e6-47ac-8ab2-65ba5b23a272", {"meta": "5122f7bd-0a44-4bea-8043-d6da1b52b49b"}),
        # DEV0EU - dhi.core.dev.uitest app.
        "DEV0EU": __EnvironmentAuthInfo("DEV0EU", "dhigroupdev.onmicrosoft.com", "ffa42221-f5e6-47ac-8ab2-65ba5b23a272", {"meta": "5122f7bd-0a44-4bea-8043-d6da1b52b49b"}),
        # DEV - dhi.core.dev.uitest app.
        "DEV": __EnvironmentAuthInfo("DEV", "dhigroupdev.onmicrosoft.com", "ffa42221-f5e6-47ac-8ab2-65ba5b23a272", {"meta": "425386dd-16e2-4225-a966-dce5d6a07402"}),
        # DEV - external AD
        "dev": __EnvironmentAuthInfo("dev", "dhigroupdevext.onmicrosoft.com", "68803cd3-78d5-4343-a135-d4402491babd", {"meta": "cbc2864b-b8c2-465b-a440-9f5b32957bc8"}),
        # DEV0 - external AD
        "dev0": __EnvironmentAuthInfo("dev0", "dhigroupdevext.onmicrosoft.com", "68803cd3-78d5-4343-a135-d4402491babd", {"meta": "7c8997e4-7d1d-4b16-a562-c6165f99762a"}),
        # DEV0EU - external AD
        "dev0eu": __EnvironmentAuthInfo("dev0eu", "dhigroupdevext.onmicrosoft.com", "68803cd3-78d5-4343-a135-d4402491babd", {"meta": "7c8997e4-7d1d-4b16-a562-c6165f99762a"})
    }


def GetAuthInfo(environment = "local"):
    if environment == "prod":
        # PROD
        tenant = "dhigroupext.onmicrosoft.com"
        clientId = "aa00293d-f5dd-4ab6-a3c8-28f894149572"
        metaResourceId = "0dc51ba3-5c5e-4703-ba89-322411a51197"
    elif environment == "preprod":
        # PREPROD ?
        tenant = "dhigroupext.onmicrosoft.com"
        clientId = "aa00293d-f5dd-4ab6-a3c8-28f894149572"
        metaResourceId = "0dc51ba3-5c5e-4703-ba89-322411a51197"
    elif environment == "test":
        # TEST
        tenant = "dhigrouptest.onmicrosoft.com"
        clientId = "189228fc-e229-4f7d-99c2-ec5161f5d31a"
        metaResourceId = "14583d65-56bc-4bff-9ace-7e80cbdc8944"
    elif environment == "DEV0" or environment == "DEV0EU":
        # DEV0 - dhi.core.dev.uitest app.
        tenant = "dhigroupdev.onmicrosoft.com"
        clientId = "ffa42221-f5e6-47ac-8ab2-65ba5b23a272"
        metaResourceId = "5122f7bd-0a44-4bea-8043-d6da1b52b49b"
    elif environment == "DEV":
        # DEV - dhi.core.dev.uitest app.
        tenant = "dhigroupdev.onmicrosoft.com"
        clientId = "ffa42221-f5e6-47ac-8ab2-65ba5b23a272"
        metaResourceId = "425386dd-16e2-4225-a966-dce5d6a07402"
    elif environment == "dev":
        # DEV - external AD
        tenant = "dhigroupdevext.onmicrosoft.com"
        clientId = "68803cd3-78d5-4343-a135-d4402491babd"
        metaResourceId = "cbc2864b-b8c2-465b-a440-9f5b32957bc8"
    elif environment == "dev0" or environment == "dev0eu":
        # DEV0 - external AD
        tenant = "dhigroupdevext.onmicrosoft.com"
        clientId = "68803cd3-78d5-4343-a135-d4402491babd"
        metaResourceId = "7c8997e4-7d1d-4b16-a562-c6165f99762a"
    else:
        return None, None, None
    return tenant, clientId, metaResourceId

def AcquireTokenInteractively(environment):
    tenant, clientId, metaResourceId = GetAuthInfo(environment)
    if tenant and clientId and metaResourceId:
        #authorityUrl = f"https://login.microsoftonline.com/{tenant}"
        #context = adal.AuthenticationContext(authorityUrl, validate_authority=tenant != "adfs")
        #resource = "00000002-0000-0000-c000-000000000000"
        #clientSecret = ""
        #return context.acquire_token_with_client_credentials(resource, clientId, clientSecret)
        #return ontext.acquire_token(resource, userId, clientId)

        #scopes = [f"{metaResourceId}/user_impersonation"]
        #msal = MsalInteractiveTokenAcquirer(tenant, clientId, scopes)
        #msal.acquire_token_interactively()
        #return msal.access_token()

        #azure.common.credentials.InteractiveCredentials()

        authority = "login.microsoftonline.com"
        scopes = [f"{metaResourceId}/user_impersonation"]

        #cacheCredential = SharedTokenCacheCredential(authority=authority, tenant_id=tenant)
        #token = cacheCredential.get_token(*scopes)
        credential = _AuthenticationHelper.GetDefaultInteractiveCredential(authority=authority, tenant_id=tenant, client_id=clientId)
        token = credential.get_token(*scopes)
        #auth = credential.authenticate(scopes=scopes)
        return token

    return None

class MikeCloudIdentity(ABC):

    @abstractmethod
    def get_parameters(self):
        return {}

class ApiKeyIdentity(MikeCloudIdentity):
    """Identity to log in with open api key"""

    def __init__(self, customer_id, apikey, environment=None):
        super().__init__()

        try:
            id = uuid.UUID(apikey)
        except ValueError:
            parameter_name = f"{apikey=}".split("=")[0]
            raise MikeCloudException(f"Parameter {parameter_name} must be a uuid, not {apikey}")

        self._customer_id = customer_id
        self._apikey = apikey
        self._environment = environment if environment else "prod"

    @property
    def apikey(self):
        return self._apikey

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def environment(self):
        return self._environment

    def get_parameters(self):
        data = {
            'apikey': self.apikey,
            'environment': self.environment
        }

        if self.customer_id:
            data["customer_id"] = self.customer_id

        return data


class InteractiveIdentity(MikeCloudIdentity):
    """Identity for interactive user authentication"""

    _token = None
    _environment = None

    def __init__(self, environment=None, forcelogin=True) -> None:
        super().__init__()
        self._environment = environment if environment else "prod"
        self._token = ClientConfig.AcquireAccessToken(self._environment, forcelogin=forcelogin)
    
    @property
    def token(self):
        if self._token:
            return self._token
        else:
            raise MikeCloudException("Interactive token does not exist yet")

    @property
    def environment(self):
        return self._environment

    def get_parameters(self):
        return {
            'accesstoken': self.token,
            'environment': self.environment
        }


class _AuthenticationHelper:
    @staticmethod
    def GetDefaultInteractiveCredential(**kwargs):
        if platform.system() == 'Linux':
            return DeviceCodeCredential(**kwargs)
        return InteractiveBrowserCredential(**kwargs)

    @staticmethod
    def GetDefaultTokenCacheOptions(**kwargs):
        allowunencryptedstorage = platform.system() == 'Linux'
        return TokenCachePersistenceOptions(name="dhi-platform-sdk-py", allow_unencrypted_storage=allowunencryptedstorage)


if __name__ == '__main__':
    print(__file__)
    print(dir())
