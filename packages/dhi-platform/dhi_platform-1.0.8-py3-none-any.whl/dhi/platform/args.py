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

import argparse, inspect, json, itertools, os, pkgutil, sys
from typing import Callable
#from .config import ClientConfig

class ClientArgs:
    @staticmethod
    def ListPackageModules(pkgpath):
        print(f"Commands in {os.path.basename(pkgpath)}:")
        for m in pkgutil.iter_modules([pkgpath]):
            if not m.ispkg:
                print(f"    {m.name}")

    @classmethod
    def LoadJson(cls, inputFile, default=None, encoding="utf-8-sig"):
        if inputFile:
            if inputFile == "-":
                return json.load(sys.stdin)
            else:
                with open(inputFile, "r", encoding=encoding) as inputf:
                    return json.load(inputf)
        return default

    @classmethod
    def DumpJson(cls, obj, outFile):
        json.dump(obj, outFile, indent=True)

    @classmethod
    def LoadJsonStr(cls, str, default=None):
        return json.loads(str) if str else default

    @classmethod
    def ParseBasic(cls, prog=None, description=None, init=None):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserBasic(p, init))

    @classmethod
    def ParseEnvironment(cls, prog=None, description=None, init=None):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserEnvironment(p, init))

    @classmethod
    def ParseApiKey(cls, prog=None, description=None, init=None):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserApiKey(p, init))

    @classmethod
    def ParsePlatform(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserPlatform(p, init, defaultformat))

    @classmethod
    def ParseForProject(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserProject(p, init, defaultformat))

    @classmethod
    def ParseForProjectList(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserProjectList(p, init, defaultformat))

    @classmethod
    def ParseForDataset(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserDataset(p, init, defaultformat))

    @classmethod
    def ParseForDatasetList(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserDatasetList(p, init, defaultformat))

    @classmethod
    def ParseForDatasetListOpt(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserDatasetListOpt(p, init, defaultformat))

    @classmethod
    def ParseForDatasetPos(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserDatasetPos(p, init, defaultformat))

    @classmethod
    def ParseForTimeseriesList(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserTimeseriesList(p, init, defaultformat))

    @classmethod
    def ParseForExecutionRunList(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserExecutionRunList(p, init, defaultformat))

    @classmethod
    def ParseForEngineRun(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserEngineRun(p, init, defaultformat))

    @classmethod
    def ParseForEngineRuns(cls, prog=None, description=None, init=None, defaultformat="table"):
        return cls.__Parse(prog, description, lambda p: cls.__InitParserEngineRuns(p, init, defaultformat))

    @staticmethod
    def GetDefault(name, default=None):
        result = os.environ.get(name)
        return result if result else default

    @staticmethod
    def GetDefaultL(name, default: Callable=None):
        result = os.environ.get(name)
        return result if result else default() if default else None

    @classmethod
    def __Parse(cls, prog=None, description=None, init=None):
        parser = cls.__CreateArgumentParser(prog, description, init)
        try:
            return parser.parse_args()
        except:
            sys.exit(1)

    @classmethod
    def __CreateArgumentParser(cls, prog=None, description=None, init=None):
        parser = argparse.ArgumentParser(prog=prog, description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        if init:
            init(parser)
        return parser

    @classmethod
    def __InitParserBasic(cls, parser, init=None):
        if init:
            init(parser)
        #parser.add_argument("--dump", dest="dump", help="Dump the output", action="store_true")
        parser.add_argument("-v", "--verbose", default=0, help="Make the operation more talkative (increase verbosity), dump the output", action="count")

    @classmethod
    def __InitParserEnvironment(cls, parser, init=None, initParserBasic=True):
        if init:
            init(parser)
        #def getdefaultenvironment():
        #    tmp = ClientConfig.GetDefaultEnvironmentName(configname=cls.GetDefault("DHICONFIG"))
        #    return tmp if tmp else "prod"
        #parser.add_argument("-e", "--environment", default=cls.GetDefaultL("DHIPLATFORMENV", getdefaultenvironment), help="Environment", choices=["local", "dev", "DEV", "dev0", "DEV0", "test", "preprod", "prod"])
        parser.add_argument("-e", "--environment", default=cls.GetDefault("DHIPLATFORMENV"), help="Environment", choices=["local", "dev", "DEV", "dev0", "DEV0", "test", "preprod", "prod"])
        parser.add_argument("--config", help="Configuration name", default=cls.GetDefault("DHICONFIG"))
        if initParserBasic:
            cls.__InitParserBasic(parser)

    @classmethod
    def __InitParserApiKey(cls, parser, init=None, initParserEnvironment=True, initParserBasic=True):
        if init:
            init(parser)
        parser.add_argument("-a", "--apikey", default=cls.GetDefault("DHIAPIKEY"), help="API key")
        if initParserEnvironment:
            cls.__InitParserEnvironment(parser, None, initParserBasic)
        
    @classmethod
    def __InitParserPlatform(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        # %(default)s
        cls.__InitParserApiKey(parser,None, False, False)
        parser.add_argument("--preferapikey", default=None, help="Prefer API key", action="store_true")
        cls.__InitParserEnvironment(parser, None, False)
        parser.add_argument("-m", "--metaurl", default=cls.GetDefault("DHICOREMETADATAURL"), help="Metadata service URL")
        parser.add_argument("--customerid", default=cls.GetDefault("DHICUSTOMERGUID"), help="Customer id")
        parser.add_argument("--userid", default=cls.GetDefault("DHIUSERID"), help="User id")
        parser.add_argument("--userisadmin", choices=["true", "false"], default=cls.GetDefault("DHIUSERISADMIN"), help="true if user is admin")
        parser.add_argument("--format", help="Output format", choices=["plain", "table", "json", "yaml"], default=cls.GetDefault("DHIOUTPUTFORMAT", defaultformat))
        parser.add_argument("--output", help="Output file", default=cls.GetDefault("DHIOUTPUTFILE"))
        cls.__InitParserBasic(parser)

    @classmethod
    def __InitParserProject(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("-p", "--projectid", default=cls.GetDefault("DHIPROJECTID"), help="Project id")
        cls.__InitParserPlatform(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserProjectList(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("projectids", metavar="projectid", help="Project id", nargs="+")
        cls.__InitParserPlatform(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserDataset(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("-d", "--datasetid", default=cls.GetDefault("DHIDATASETID"), help="Dataset id")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserDatasetList(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("datasetids", metavar="datasetid", help="Dataset id", nargs="+")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserDatasetListOpt(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("datasetids", metavar="datasetid", help="Dataset id", nargs="*")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserDatasetPos(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("datasetid", help="Dataset id")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserTimeseriesList(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("tsids", metavar="tsid", help="Timeseries id", nargs="+")
        cls.__InitParserDataset(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserExecutionRunList(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("executionids", metavar="executionid", help="Execution run id", nargs="+")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserEngineRun(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("-x", "--executionid", default=cls.GetDefault("DHIEXECUTIONID"), help="Execution run id")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

    @classmethod
    def __InitParserEngineRuns(cls, parser, init=None, defaultformat="table"):
        if init:
            init(parser)
        parser.add_argument("-r", "--runno", default=cls.GetDefault("DHIRUNNO"), help="Run number")
        parser.add_argument("-u", "--run", help="Run path", default=".")
        cls.__InitParserProject(parser, defaultformat=defaultformat)

if __name__ == '__main__':
    print(__file__)
    print(dir())
