#!/usr/bin/env python

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

import argparse, datetime, fileinput, glob, heapq, json, os, os.path, re, random, requests, sys, urllib.request
from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE, HTTPConnection, HTTPSConnection

def __initParser(parser):
    parser.add_argument("files", help="OpenAPI file", metavar="url", nargs="*")
    parser.add_argument("-c", "--classname", help="Class name", default="OpenapiClient")
    parser.add_argument("-n", "--classnum", help="First class number", type=int, default=1)
    parser.add_argument("-s", "--dhiservice", help="Platform service id")
    parser.add_argument("-r", "--headerparams", help="Header parameters", metavar="PARAMETERS")
    parser.add_argument("-i", "--inputtoheader", help="Input to header parameters", metavar="INPUTPARAMETERS")
    parser.add_argument("-k", "--kwargsfor", help="Operation to use **kwargs", metavar="OPERATIONS")
    parser.add_argument("-f", "--headersfor", help="Additional headers for endpoints", metavar="HEADERDEF")
    parser.add_argument("-p", "--skipheadersfor", help="Skip headers for endpoints", metavar="SKIPHEADERDEF")
    parser.add_argument("-a", "--skipauthfor", help="Skip authentication for endpoints", metavar="SKIPAUTHDEF")
    parser.add_argument("-t", "--datafields", help="Additional data fields for data contracts", metavar="FIELDDEF")
    parser.add_argument("-d", "--includedeprecated", help="Include deprecated methods", metavar="OPERATIONS")
    parser.add_argument("-o", "--output", default="-", help="Write output to a file")
    #parser.add_argument("--relative", help="show relative paths", action="store_false")
    #parser.add_argument("--transitivedeps", help="show transitive dependencies", action="store_false")
    #parser.add_argument("--shownotfound", help="show not found projects", action="store_true")
    #parser.add_argument("--shownotfounddeps", help="show not found dependencies", action="store_true")
    #parser.add_argument("-f", "--format", help="output format", choices=["plain", "json", "xml"], default="plain")
    #parser.add_argument("--debug", help="show debug output", action="store_true")
    parser.add_argument("-v", "--verbose", default=0, help="Make the operation more talkative (increase verbosity), show debug output", action="count")

def main():
    args = __parseBasic(description="Create Python wrapper classes from OpenAPI", init=__initParser)
    if args.verbose:
        print(f"args:{args}")

    if args.output and args.output != "-":
        with open(args.output, "w") as outfile:
            writeFiles(args, outfile)
    else:
        writeFiles(args, sys.stdout)
    #with urllib.urlopen(f) as response:
    #    obj = json.load(f)
    #    print(obj)
    #    #html = response.read()

def writeFiles(args, outfile):
    n = 0
    kwargsoperations = set()
    if args.kwargsfor:
        kwargsoperations.update(args.kwargsfor.split(","))
    headersfor = Helper.initheadersfor(args.headersfor)
    skipheadersfor = Helper.initskipheadersfor(args.skipheadersfor)
    skipauthfor = set()
    if args.skipauthfor:
        skipauthfor.update(args.skipauthfor.split(","))
    datafields = Helper.initdatafields(args.datafields)
    includedeprecated = set()
    if args.includedeprecated:
        includedeprecated.update(args.includedeprecated.split(","))
    headerparams = []
    if args.headerparams:
        headerparams.extend(args.headerparams.split(","))
    inputtoheader = {}
    if args.inputtoheader:
        inputtoheader.update(dict([reversed(x.split('=')) for x in args.inputtoheader.split(",")]))
    Helper.writeFileHeader(outfile)
    for inputfile in args.files:
        openapiObj = Helper.getOpenApiObj(inputfile)
        classname = f"{args.classname}{n+args.classnum}"
        suffix = f"V{n+args.classnum}"
        Helper.generateApiClasses(openapiObj, suffix, inputfile, classname, kwargsoperations, headersfor, skipheadersfor, skipauthfor, datafields, headerparams, inputtoheader, includedeprecated, args.dhiservice, outfile)
        n += 1
        #with urllib.urlopen(f) as response:
        #    obj = json.load(f)
        #    print(obj)
        #    #html = response.read()

def __parseBasic(prog=None, description=None, init=None):
    parser = argparse.ArgumentParser(prog=prog, description=description)
    if init:
        init(parser)
    try:
        return parser.parse_args()
    except:
        sys.exit(1)

class ContractInfo:
    def __init__(self, name, content, dependson = set()):
        self.refcount = 0
        self.name = name
        self.content = content
        self.dependson = dependson
        self.dependsonme = set()
    def __lt__(self, other):
        return self.refcount < other.refcount

class Helper:
    TITLE = "title"
    DESCRIPTION = "description"
    VERSION = "version"
    NAME = "name"
    IN = "in"
    OPERATIONID = "operationId"
    SUMMARY = "summary"
    SCHEMA = "schema"
    DEFAULT = "default"
    REQUESTBODY = "requestBody"
    MethodNumbers = {}

    @classmethod
    def writeFileHeader(cls, out=sys.stdout):
        #print("#!/usr/bin/env python", file=out)
        print(f"# Generated using {os.path.basename(__file__)}", file=out)
        cmdline = " ".join([os.path.basename(x) if i == 0 else f"\"{x}\"" for i, x in enumerate(sys.argv)])
        print(f"# {cmdline}", file=out)
        print(f"# {datetime.datetime.utcnow()}Z", file=out)
        print("from typing import Any, Dict, List, NewType, Type, TypeVar, Union", file=out)
        print("from enum import Enum", file=out)
        print("import attr", file=out)
        print("from ..base.client import DataContract, PlatformClient, Response", file=out)

    @classmethod
    def getOpenApiObj(cls, inputfile):
        return requests.get(inputfile).json()

    @classmethod
    def initheadersfor(cls, headersfor):
        result = dict()
        if headersfor:
            for h in headersfor.split(","):
                parts = h.split(":")
                if len(parts) != 3:
                    sys.exit(f"wrong format in header info (endpoint:header:value): {h}")
                if op := parts[0]:
                    content = { parts[1]: f"\"{parts[2]}\"" }
                    if headers := result.get(op):
                        headers.update(content)
                    else:
                        result[op] = content
        return result

    @classmethod
    def initskipheadersfor(cls, skipheadersfor):
        result = dict()
        if skipheadersfor:
            for h in skipheadersfor.split(","):
                parts = h.split(":")
                if len(parts) != 2:
                    sys.exit(f"wrong format in skip header info (endpoint:header): {h}")
                if op := parts[0]:
                    content = set([parts[1]])
                    if headers := result.get(op):
                        headers.update(content)
                    else:
                        result[op] = content
        return result

    @classmethod
    def initdatafields(cls, datafields):
        result = dict()
        if datafields:
            for d in datafields.split(","):
                parts = d.split(":")
                if len(parts) != 4:
                    sys.exit(f"wrong format in data field info (datacontract:field:type:value): {d}")
                if dc := parts[0]:
                    content = { parts[1]: f"{parts[2]} = \"{parts[3]}\"" }
                    if fields := result.get(dc):
                        fields.update(content)
                    else:
                        result[dc] = content
        return result

    @classmethod
    def generateApiClasses(cls, openapiObj, suffix, inputfile, className, kwargsoperations, headersfor, skipheadersfor, skipauthfor, datafields, headerparams, inputtoheader, includedeprecated, service=None, out=sys.stdout):
        info = openapiObj["info"]
        print(file=out)
        print(file=out)
        cls.__writeApiInfo(info, inputfile, out)
        cls.__generateContracts(openapiObj, info, suffix, inputfile, className, kwargsoperations, datafields, headerparams, inputtoheader, includedeprecated, service, out)
        cls.__generateEndpointsClass(openapiObj, info, suffix, inputfile, className, kwargsoperations, headersfor, skipheadersfor, skipauthfor, headerparams, inputtoheader, includedeprecated, service, out)

    @classmethod
    def __writeApiInfo(cls, info, inputfile, out):
        print(f"# {inputfile}", file=out)
        print(f"# {info[cls.TITLE]}", file=out)
        print(f"# {info[cls.DESCRIPTION]}", file=out)
        print(f"# {info[cls.VERSION]}", file=out)

    @classmethod
    def __generateContracts(cls, openapiObj, info, suffix, inputfile, className, kwargsoperations, datafields, headerparams, inputtoheader, includedeprecated, service, out):
        if components := openapiObj["components"]:
            if schemas := components["schemas"]:
                allcontracts = dict()
                for name, content in schemas.items():
                    allcontracts[name] = ContractInfo(name, content, cls.__getContractDependson(name, content))
                for name, info in allcontracts.items():
                    for dep in info.dependson:
                        if d := allcontracts.get(dep):
                            d.dependsonme.add(name)
                            info.refcount += 1
                contractslist = [x for x in allcontracts.values()]
                heapq.heapify(contractslist)
                while contractslist:
                    heapq.heapify(contractslist)
                    top = heapq.heappop(contractslist)
                    name = top.name
                    content = top.content
                    for dep in top.dependsonme:
                        if deponmeitem := allcontracts.get(dep):
                            deponmeitem.refcount -= 1
                    cls.__generateContract(name, datafields.get(name), content, openapiObj, info, suffix, inputfile, className, kwargsoperations, headerparams, inputtoheader, includedeprecated, service, out)

    @classmethod
    def __getContractDependson(cls, name, schema):
        result = set()
        if schema.get("type") == "object":
            if parentclassname := cls.__getParentClassType(schema, ""):
                result.add(parentclassname)
            properties = schema.get("properties")
            if properties:
                for _, propertyinfo in properties.items():
                    if propertytype := cls.__getParentClassType(propertyinfo, ""):
                        result.add(propertytype)
                    else:
                        if tmp := propertyinfo.get("type"):
                            if tmp == "array":
                                #TODO: if it is multidimensional array, it should get nested item type
                                result.add(cls.__getArrayItemType(propertyinfo, ""))
        return result

    @classmethod
    def __generateContract(cls, name, customfields, schema, openapiObj, info, suffix, inputfile, className, kwargsoperations, headerparams, inputtoheader, includedeprecated, service, out):
        classname = f"{name}{suffix}"
        print(file=out)
        if enuminfo := schema.get("enum"):
            print(f"class {classname}(str, Enum):", file=out)
            description = schema.get(cls.DESCRIPTION)
            cls.__printLines2([description], "    \"\"\"", "    ", "    \"\"\"", out=out)
            # enum values
            for e in enuminfo:
                print(f"    {e.upper()} = \"{e}\"", file=out)
            # methods
            print("    def __str__(self) -> str:", file=out)
            print("        return str(self.value)", file=out)
        elif schema.get("type") == "object":
            if not (parentclassname := cls.__getParentClassType(schema, suffix)):
                parentclassname = "DataContract"
            #print(f"{classname}Type = NewType(\"{classname}\", {parentclassname})", file=out)
            print(f"{classname}Type = TypeVar(\"{classname}Type\", bound=\"{classname}\")", file=out)
            print(file=out)
            print("@attr.s(auto_attribs=True)", file=out)
            print(f"class {classname}({parentclassname}):", file=out)
            description = schema.get(cls.DESCRIPTION)
            cls.__printLines2([description], "    \"\"\"", "    ", "    \"\"\"", out=out)
            # custom fields
            if customfields:
                for cfname, cfdef in customfields.items():
                    print(f"    {cfname}: {cfdef}", file=out)
            # properties
            renamedproperties = {}
            properties = schema.get("properties")
            if properties:
                for originalpropertyname, propertyinfo in properties.items():
                    propertyname = cls.__safeParam(originalpropertyname, {})
                    propertytype = cls.__getPropertyType(propertyinfo, suffix)
                    if originalpropertyname != propertyname:
                        renamedproperties[originalpropertyname] = propertyname
                    print(f"    {propertyname}: {propertytype} = None", file=out)
            renamedlist = ", ".join([f"\"{o}\": \"{p}\"" for o, p in renamedproperties.items()])
            print(f"    __renamed = {{ {renamedlist} }}", file=out)
            #renamedlist = ", ".join([f"\"{p}\": \"{o}\"" for o, p in renamedproperties.items()])
            #print(f"    __renamedr = {{ {renamedlist} }}", file=out)
            # methods
            print("    def to_dict(self) -> Dict[str, Any]:", file=out)
            print("        return self.get_dictionary(self.get_renamed())", file=out)
            print("    def load_dict(self, src_dict: Dict[str, Any]) -> None:", file=out)
            print("        DataContract.load_from_directory(self, src_dict, self.get_renamed())", file=out)
            print("    @classmethod", file=out)
            print("    def get_renamed(cls) -> Dict[str, str]:", file=out)
            print(f"        result = {parentclassname}.get_renamed().copy()", file=out)
            print(f"        result.update(cls.__renamed)", file=out)
            print(f"        return result", file=out)
            print("    @classmethod", file=out)
            print(f"    def from_dict(cls: {classname}Type, src_dict: Dict[str, Any]) -> {classname}Type:", file=out)
            print(f"        obj = {classname}()", file=out)
            print(f"        obj.load_dict(src_dict)", file=out)
            print(f"        return obj", file=out)

    @classmethod
    def __getPropertyType(cls, propertyinfo, suffix):
        if propertyinfo:
            propertytype = cls.__getParentClassType(propertyinfo, suffix)
            if propertytype:
                return propertytype
            if type := propertyinfo.get("type"):
                if type == "string":
                    return "str"
                elif type == "integer":
                    return "int"
                elif type == "number":
                    return "float"
                elif type == "array":
                    return f"List[{cls.__getArrayItemType(propertyinfo, suffix)}]"
                return "str"
            return cls.__getReftype(propertyinfo.get("$ref"), suffix)
        return None

    @classmethod
    def __getArrayItemType(cls, propertyinfo, suffix):
        if itemsinfo := propertyinfo.get("items"):
            if itemtype := cls.__getReftype(itemsinfo.get("$ref"), suffix):
                return itemtype
            return cls.__getPropertyType(itemsinfo, suffix)
        return None

    @classmethod
    def __getParentClassType(cls, schema, suffix):
        if schema:
            if allOf := schema.get("allOf"):
                for _, reftype in allOf[0].items():
                    return cls.__getReftype(reftype, suffix)
        return None

    @classmethod
    def __getReftype(cls, reftype, suffix):
        if reftype:
            if reftype == "string":
                return "str"
            elif reftype == "integer":
                return "int"
            elif reftype == "number":
                return "float"
            elif (reftype.startswith("#/components/schemas/")):
                tmp = reftype.replace("#/components/schemas/", "")
                return f"{tmp}{suffix}"
        return reftype

    @classmethod
    def __generateEndpointsClass(cls, openapiObj, info, suffix, inputfile, className, kwargsoperations, headersfor, skipheadersfor, skipauthfor, addheaderparams, inputtoheader, includedeprecated, service, out):
        print(file=out)
        print(f"class {className}(PlatformClient):", file=out)
        print(f"    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):", file=out)
        includeheaders = f", includeheaders=PlatformClient.GetServiceHeaders({cls.__getInitParam(service)})" if service else ""
        print(f"        super().__init__(inspectFnc{includeheaders}, **kwargs)", file=out)
        for url, ops in openapiObj["paths"].items():
            for method, opObj in ops.items():
                operation = cls.__getOperationId(opObj, method)
                if operation and (operation in includedeprecated or not opObj.get("deprecated")):
                    renamedparams = {}
                    queryparams = []
                    queryoptparams = []
                    pathparams = []
                    headers = {}
                    headerparams = {}
                    methodwithbody = method in ["post", "put", "patch"]
                    bodyparam = ", body" if methodwithbody and cls.REQUESTBODY in opObj else ""
                    callbodyparam = bodyparam if bodyparam else (", None" if methodwithbody else "")
                    if parameterslist := opObj.get("parameters"):
                        for p in parameterslist:
                            paramname = p[cls.NAME]
                            renamedparams[paramname] = cls.__safeParam(paramname.lower(), renamedparams)

                            if tmpH := inputtoheader.get(paramname):
                                headerparams[tmpH] = renamedparams[paramname]
                            if (tmpIn := p[cls.IN]) == "query":
                                pschema = p[cls.SCHEMA]
                                if pschema.get("nullable") or pschema.get("default") is None:
                                    queryoptparams.append(paramname)
                                else:
                                    queryparams.append(paramname)
                            elif tmpIn == "path":
                                pathparams.append(paramname)
                            elif tmpIn == "header":
                                headers[paramname] = p[cls.SCHEMA].get(cls.DEFAULT)
                    print(file=out)
                    hfparams = []
                    if hf := headersfor.get(operation):
                        hfparams = [f"{h}={v}" for h, v in hf.items()]

                    opheaderparams = addheaderparams
                    skiphf = skipheadersfor.get(operation)
                    if skiphf:
                        opheaderparams = [x for x in addheaderparams if x not in skiphf]
                    headerparamsstr1 = ", ".join(opheaderparams)
                    headerparamsstr1 = f", {headerparamsstr1}" if headerparamsstr1 else headerparamsstr1
                    headerparamsstr2 = ", ".join([f"{x}={x}" for x in opheaderparams]) if opheaderparams else ""
                    headerparamsstr2 = f", {headerparamsstr2}" if headerparamsstr2 else headerparamsstr2

                    skipauth = ", noauthentication=True" if operation in skipauthfor else ""

                    hfparamsstr = ", ".join(hfparams)
                    hfparamsstr = f", {hfparamsstr}" if hfparamsstr else ""
                    kwargsparam = ", **kwargs" if operation in kwargsoperations or "*" in kwargsoperations else ""
                    print(f"    def {operation}(self{headerparamsstr1}{bodyparam}{cls.__convertParams(pathparams, renamedparams)}{cls.__convertParams(queryparams, renamedparams)}{cls.__convertOptParams(queryoptparams, renamedparams)}{kwargsparam}) -> Response:", file=out)
                    doclines = []
                    if tmp := opObj.get(cls.SUMMARY):
                        doclines.append(tmp)
                    for tmp in opObj["tags"]:
                        doclines.append(tmp)
                    doclines.append(f"{method.upper()} {url}")
                    cls.__printLines2(doclines, "        \"\"\"", "        ", "        \"\"\"", out=out)
                    if queryparams or queryoptparams:
                        allqueryparams = queryparams+queryoptparams
                        reservedparams = [x for x in allqueryparams if cls.__isReserved(x)]
                        otherparams = [x for x in allqueryparams if not cls.__isReserved(x)]
                        if reservedparams:
                            print(f"        kw = {{{cls.__convertReservedParams(reservedparams, renamedparams)}}}", file=out)
                            kwparam = ", **kw" if otherparams else "**kw"
                        else:
                            kwparam = ""
                        print(f"        queryparams = self.GetQueryParams({cls.__convertQueryParams(otherparams, renamedparams)}{kwparam})", file=out)
                        qp = "queryparams"
                    else:
                        qp = "None"
                    ppf = "f" if pathparams else ""
                    requestUrl = cls.__convertUrl(url, renamedparams) if ppf else url
                    print(f"        return self.{method.capitalize()}Request({ppf}\"{requestUrl}\"{callbodyparam}, {qp}{cls.__convertHeaders(headers)}{headerparamsstr2}{cls.__convertHeaders(headerparams, params=True)}{hfparamsstr}{skipauth}{kwargsparam})", file=out)

    @staticmethod
    def __printLines(lines, prefix, suffix="", out=sys.stdout):
        if lines:
            for l in lines.splitlines():
                print(f"{prefix}{l}{suffix}", file=out)

    @staticmethod
    def __printLines2(lines, prefix1, prefix2, suffix="", out=sys.stdout):
        if lines:
            firstline = True
            for line in lines:
                if line:
                    isfirst = firstline
                    for l in line.splitlines():
                        if firstline:
                            print(f"{prefix1}{l}", file=out)
                            firstline = False
                        else:
                            print(f"{prefix2}{l}", file=out)
                    if isfirst and not firstline:
                        print("", file=out)
            if not firstline:
                print(suffix, file=out)

    @classmethod
    def __getOperationId(cls, op, method):
        #result = op.get(cls.OPERATIONID)
        #tmp = "operation"
        #return result if result else f"{method.capitalize()}Operation{cls.__nextNum(tmp)}"
        result = op.get(cls.OPERATIONID)
        return result.replace(" ", "_") if result else None

    @classmethod
    def __nextNum(cls, method):
        num = cls.MethodNumbers.get(method)
        num = num+1 if num else 1
        cls.MethodNumbers[method] = num
        return num

    @staticmethod
    def __isReserved(param):
        return param.find("@") >= 0 or param in ["from", "def", "import", "class", "return", "if", "else", "in", "body", "array"]

    @staticmethod
    def __mangleReserved(param, renamedparams):
        attempt = 0
        p = param
        while True:
            attempt += 1
            if attempt == 1 and p.find("@") >= 0:
                p = p.replace("@", "_")
            else:
                #p = f"{param}param{random.randint(0, 1000)}"
                p = f"{p}_"
            if p not in renamedparams:
                return p 

    @classmethod
    def __safeParam(cls, param, renamedparams):
        return cls.__mangleReserved(param, renamedparams) if cls.__isReserved(param) else param

    @classmethod
    def __convertReservedParams(cls, params, renamedparams):
        return ", ".join([f"\"{x}\": {renamedparams.get(x)}" for x in params])

    @classmethod
    def __convertParams(cls, params, renamedparams, sep=", ", withprefix=True):
        result = sep.join([renamedparams.get(x) for x in params])
        return f"{sep}{result}" if result and withprefix else result

    @classmethod
    def __convertOptParams(cls, params, renamedparams, sep=", ", withprefix=True):
        result = sep.join([f"{renamedparams.get(x)}=None" for x in params])
        return f"{sep}{result}" if result and withprefix else result

    @staticmethod
    def __convertQueryParams(params, renamedparams, sep=", ", withprefix=False):
        result = sep.join([f"{x}={renamedparams.get(x)}" for x in params])
        return f"{sep}{result}" if result and withprefix else result

    @staticmethod
    def __convertHeaders(headers, sep=", ", withprefix=True, params=False):
        fixvarname = lambda x: x.replace("-", "_")
        rightside = (lambda x: x) if params else (lambda x: f"\"{x}\"")
        tmp = [f"{fixvarname(n)}={rightside(v)}" for n, v in headers.items()]
        result = sep.join(tmp)
        return f"{sep}{result}" if result and withprefix else result

    @staticmethod
    def __convertUrl(url, renamedparams):
        pattern = re.compile(r'{([^}]*)}')
        return pattern.sub(lambda m: f"{{{renamedparams.get(m.group(1))}}}", url)

    @staticmethod
    def __getInitParam(value):
        return f"\"{value}\"" if value else "None"

if __name__ == '__main__':
    main()
