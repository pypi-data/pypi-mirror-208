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

import json, pathlib
from datetime import datetime
from types import SimpleNamespace
from typing import Callable


class ClientConfig:
    __cachedconfigname = None
    __cachedcfg = None
    __cacheddefaultenv = None
    __cacheddefaultenvname = None

    @classmethod
    def GetEnvironmentFromConfiguration(cls, environment, configname=None):
        if not environment:
            environment = cls.GetDefaultEnvironmentName(environment, configname)
        return (environment, cls.GetEnvironment(environment, configname))

    @staticmethod
    def GetConfigname(args, configname=None):
        return configname if configname else args.config if hasattr(args, "config") else None

    @classmethod
    def UpdateEnvironmentFromConfiguration(cls, args, configname=None):
        configname = cls.GetConfigname(args, configname)
        (args.environment, envObj) = cls.GetEnvironmentFromConfiguration(args.environment, configname)
        return envObj

    @classmethod
    def UpdatePlatformFromConfiguration(cls, args, configname=None):
        envObj = cls.UpdateEnvironmentFromConfiguration(args, configname)
        if envObj:
            if not args.apikey:
                args.apikey = cls.GetApiKey(envObj)
            if args.preferapikey == None:
                args.preferapikey = cls.GetPreferApiKey(envObj)
            if not (args.preferapikey and args.apikey):
                if tokeninfo := cls.GetAccessTokenInfo(envObj):
                    if cls.IsValid(tokeninfo):
                        args.accesstoken = cls.GetToken(tokeninfo, args.environment)
                    elif cls.IsExpired(tokeninfo):
                        args.accesstoken = cls.RefreshToken(tokeninfo, args.environment)
        return envObj

    @classmethod
    def UpdateProjectFromConfiguration(cls, args, configname=None):
        envObj = cls.UpdatePlatformFromConfiguration(args, configname)
        if envObj:
            if not hasattr(args, 'projectid') or not args.projectid:
                args.projectid = cls.GetProjectid(envObj)
        return envObj

    @classmethod
    def UpdateDatasetFromConfiguration(cls, args, configname=None):
        envObj = cls.UpdateProjectFromConfiguration(args, configname)
        if envObj:
            if not hasattr(args, 'datasetid') or not args.projectid:
                args.datasetid = cls.GetDatasetid(envObj)
        return envObj

    @staticmethod
    def GetConfigurationFilePath(configname=None):
        filename = f".dhiplatform-{configname}.json" if configname else ".dhiplatform.json"
        return pathlib.Path.home().joinpath(filename)

    @classmethod
    def GetConfiguraton(cls, configname=None):
        if cls.__cachedcfg == None or cls.__cachedconfigname != configname:
            cfgfilepath = cls.GetConfigurationFilePath(configname)
            cls.__cachedconfigname = configname
            cls.__cachedcfg = cls.__LoadFile(cfgfilepath)
        return cls.__cachedcfg

    @classmethod
    def GetDefaultEnvironment(cls, environment=None, configname=None):
        if cls.__cacheddefaultenv == None:
            def getdefaultenvironment(cfgObj, envObj):
                if envObj != None:
                    return SimpleNamespace(envobj=envObj, envname=environment)
                defaultenv = cfgObj.get("default")
                return SimpleNamespace(envobj=cfgObj.get(defaultenv), envname=defaultenv) if defaultenv else None
            tmp = cls.__LoadConfiguration(environment, getdefaultenvironment, configname)
            if tmp:
                cls.__cacheddefaultenv = tmp.envobj
                cls.__cacheddefaultenvname = tmp.envname
        return cls.__cacheddefaultenv

    @classmethod
    def GetDefaultEnvironmentName(cls, environment=None, configname=None):
        cls.GetDefaultEnvironment(environment, configname)
        return cls.__cacheddefaultenvname

    @classmethod
    def GetDefaultEnvironmentAccessToken(cls, environment=None, configname=None):
        envObj = cls.GetDefaultEnvironment(environment, configname)
        return envObj.get("accesstoken") if envObj else None

    @classmethod
    def GetEnvironment(cls, environment, configname=None):
        return cls.__LoadConfiguration(environment, lambda _, envObj: envObj, configname)

    @classmethod
    def GetToken(cls, tokeninfo, env):
        result = tokeninfo.get("accesstoken") if tokeninfo else None
        if not result:
            result = cls.RefreshToken(tokeninfo, env)
        return result

    @classmethod
    def RefreshToken(cls, tokeninfo, env):
        from dhi.platform.authentication import ClientAuthentication
        (tokeninfo, result) = ClientAuthentication.RefreshToken(env, tokeninfo)
        if tokeninfo:
            cls.SaveUserTokenInfo(env, tokeninfo)
        return result

    @classmethod
    def AcquireAccessToken(cls, environment, configname=None, forcelogin=True):
        if not forcelogin:
            (environment, envObj) = cls.GetEnvironmentFromConfiguration(environment, configname)
            if tokeninfo := cls.GetAccessTokenInfo(envObj):
                if cls.IsValid(tokeninfo):
                    return cls.GetToken(tokeninfo, environment)
                elif cls.IsExpired(tokeninfo):
                    return cls.RefreshToken(tokeninfo, environment)
        from dhi.platform.authentication import ClientAuthentication
        (tokeninfo, result) = ClientAuthentication.AcquireTokenInteractively(environment)
        if tokeninfo:
            cls.SaveUserTokenInfo(environment, tokeninfo)
        return result

    @staticmethod
    def GetUsername(tokeninfo):
        return tokeninfo.get("username") if tokeninfo else None

    @staticmethod
    def GetExpiresOn(tokeninfo):
        tmp = tokeninfo.get("expireson") if tokeninfo else None
        return datetime.fromtimestamp(tmp) if tmp else None

    @staticmethod
    def IsExpired(tokeninfo):
        tmp = tokeninfo.get("expireson") if tokeninfo else None
        return datetime.fromtimestamp(tmp) < datetime.now() if tmp else None

    @staticmethod
    def IsValid(tokeninfo):
        tmp = tokeninfo.get("expireson") if tokeninfo else None
        return datetime.fromtimestamp(tmp) >= datetime.now() if tmp else False

    @staticmethod
    def GetAccessTokenInfo(envObj):
        return envObj.get("accesstoken") if envObj else None

    @staticmethod
    def GetApiKey(envObj):
        return envObj.get("apikey") if envObj else None

    @staticmethod
    def GetPreferApiKey(envObj):
        return envObj.get("preferapikey") if envObj else None

    @staticmethod
    def GetProjectid(envObj):
        return envObj.get("projectid") if envObj else None

    @staticmethod
    def GetDatasetid(envObj):
        return envObj.get("datasetid") if envObj else None

    @classmethod
    def ClearInfo(cls, environment, clearlogin=False, clearapikey=False, configname=None):
        def clearinfo(cfgObj, envObj):
            if clearlogin:
                envObj.pop("accesstoken", None)
            if clearapikey:
                envObj.pop("apikey", None)
                envObj.pop("preferapikey", None)
            cfgObj["default"] = environment
        cls.__UpdateConfiguration(environment, clearinfo, configname)

    @classmethod
    def SaveUserTokenInfo(cls, environment, token, configname=None):
        def settoken(cfgObj, envObj):
            envObj["accesstoken"] = token
            if token:
                envObj["preferapikey"] = False
            cfgObj["default"] = environment
        cls.__UpdateConfiguration(environment, settoken, configname)

    @classmethod
    def SaveApiKey(cls, environment, apikey, configname=None):
        def setapikey(cfgObj, envObj):
            envObj["apikey"] = apikey
            envObj["preferapikey"] = apikey != None
            cfgObj["default"] = environment
        cls.__UpdateConfiguration(environment, setapikey, configname)

    @classmethod
    def SetPreferApiKey(cls, environment, value, configname=None):
        def setpreferapikey(cfgObj, envObj):
            envObj["preferapikey"] = value
            cfgObj["default"] = environment
        cls.__UpdateConfiguration(environment, setpreferapikey, configname)

    @staticmethod
    def __LoadFile(filepath, default={}):
        obj = None
        if filepath.exists():
            with open(filepath, "r") as f:
                try:
                    obj = json.load(f)
                except:
                    obj = None
        return obj if obj else default

    @staticmethod
    def __SaveFile(obj, filepath):
        with open(filepath, "w") as f:
            json.dump(obj, f, indent=True)

    @staticmethod
    def __GetEnvironment(obj, environment):
        if environment:
            envObj = obj.get(environment)
            if not envObj:
                envObj = {}
                obj[environment] = envObj
            return envObj
        return None

    @classmethod
    def __LoadConfiguration(cls, environment, getter: Callable, configname=None):
        cfgObj = cls.GetConfiguraton(configname)
        if getter:
            envObj = cls.__GetEnvironment(cfgObj, environment)
            return getter(cfgObj, envObj)
        return None

    @classmethod
    def __UpdateConfiguration(cls, environment, update: Callable, configname=None):
        cfgObj = cls.GetConfiguraton(configname)
        if update:
            cfgfilepath = cls.GetConfigurationFilePath(configname)
            cfgObj = cls.__LoadFile(cfgfilepath)
            envObj = cls.__GetEnvironment(cfgObj, environment)
            update(cfgObj, envObj)
            cls.__SaveFile(cfgObj, cfgfilepath)


if __name__ == '__main__':
    print(__file__)
    print(dir())
