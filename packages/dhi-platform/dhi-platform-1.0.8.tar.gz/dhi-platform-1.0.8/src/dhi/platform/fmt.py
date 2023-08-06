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

import argparse, inspect, json, itertools, os, http.client, urllib.parse, sys, yaml

class Format:
    @staticmethod
    def PrintHeader(fmt, fields, file=sys.stdout):
        print(fmt.format(*fields), file=file)

    @staticmethod
    def PrintFields(fmt, obj, fields, file=sys.stdout):
        values = [obj.get(x) for x in fields]
        print(fmt.format(*values), file=file)

    @staticmethod
    def PrintItems(items, fmt, fields, printlen=True, printheader=True, file=sys.stdout):
        if printlen:
            print(f"{len(items)}", file=file)
        if printheader:
            Format.PrintHeader(fmt, fields, file=file)
        for i in items:
            Format.PrintFields(fmt, i, fields, file=file)

    @staticmethod
    def PrintObjFields(obj, fmt, fields, file=sys.stdout):
        for f in fields:
            print(f"{fmt.format(f)}\t{obj.get(f)}", file=file)

    @classmethod
    def DumpJson(cls, obj, file=sys.stdout):
        if obj:
            json.dump(obj, file, indent=True)
    
    @classmethod
    def DumpYaml(cls, obj, file=sys.stdout):
        if obj:
            yaml.dump(obj, file, default_flow_style=False)

    @classmethod
    def DumpPlain(cls, obj, fmt=None, file=sys.stdout, prefix=""):
        lines = cls.__GetLines(obj, prefix) if obj else None
        if lines:
            if not fmt:
                maxLen = max([len(x) for x, _ in lines])
                fmt = f"{{!s:{maxLen}}}"
            for p, v in lines:
                print(f"{fmt.format(p)}\t{v}", file=file)
    @classmethod
    def __GetLines(cls, obj, prefix):
        lines = []
        if isinstance(obj, dict):
            prefixp = (prefix+".") if prefix else prefix
            for i, v in obj.items():
                lines.extend(cls.__GetLines(v, f"{prefixp}{i}"))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                lines.extend(cls.__GetLines(v, f"{prefix}[{i}]"))
        else:
            lines = [(prefix, obj)]
        return lines

    @classmethod
    def DumpPlain2(cls, obj, fmt="{}", file=sys.stdout, prefix=""):
        stack = [(prefix, obj)]
        while stack:
            prefix, obj = stack.pop()
            if isinstance(obj, dict):
                for i, v in obj.items():
                    stack.append((prefix+"."+i, v))
            elif isinstance(obj, list):
                for v in obj:
                    stack.append((prefix+"[]", v))
            else:
                print(f"{fmt.format(prefix)}\t{obj}", file=file)

    @staticmethod
    def FormatResponses(responses, gettableoutput=None, format=None, tablefmt=None, tablefields=None, file=sys.stdout, errfile=sys.stderr):
        #if format=="yaml":
        #    Format.DumpYaml([r.Body for r in responses], file=file)
        #elif format=="json":
        #    Format.DumpJson([r.Body for r in responses], file=file)
        #elif format=="plain":
        #    Format.DumpPlain([r.Body for r in responses], file=file)
        #else:
        printclosingbracket = False
        for index, response in enumerate(responses):
            if response.IsOk:
                if format=="json":
                    print("[" if index == 0 else ",", file=file)
                    Format.DumpJson(response.Body, file=file)
                    printclosingbracket = True
                elif format=="yaml":
                    Format.DumpYaml([response.Body], file=file)
                elif format=="plain":
                    Format.DumpPlain(response.Body, prefix=f"[{index}]", file=file)
                elif format:
                    output = gettableoutput(response) if gettableoutput else None
                    if output and tablefields:
                        if index == 0:
                            Format.PrintHeader(tablefmt, tablefields, file=file)
                        if isinstance(output, list):
                            Format.PrintItems(output, tablefmt, tablefields, False, False, file=file)
                        else:
                            Format.PrintFields(tablefmt, output, tablefields, file=file)
                    else:
                        Format.DumpPlain(output, prefix=f"[{index}]", file=file)
            else:
                response.Dump(file=errfile)
        if printclosingbracket:
            print("]", file=file)

    @staticmethod
    def FormatResponse(response, gettableoutput=None, format=None, tablefmt=None, tablefields=None, file=sys.stdout, errfile=sys.stderr):
        if response.IsOk:
            if format=="json":
                Format.DumpJson(response.Body, file=file)
            elif format=="yaml":
                Format.DumpYaml(response.Body, file=file)
            elif format=="plain" or format and not tablefields:
                Format.DumpPlain(response.Body, file=file)
            elif format and tablefields and gettableoutput:
                output = gettableoutput(response)
                if isinstance(output, list):
                    if not tablefmt:
                        tablefmt = "\t".join((f"{{!s:{len(x)}}}" for x in tablefields))
                    Format.PrintItems(output, tablefmt, tablefields, file=file)
                else:
                    if not tablefmt:
                        maxlen = max([len(x) for x in tablefields])
                        tablefmt = f"{{!s:{maxlen}}}"
                    Format.PrintObjFields(output, tablefmt, tablefields, file=file)
        else:
            response.Dump(file=errfile)

    @staticmethod
    def FormatResponseItems(response, gettableoutputs=None, format=None, file=sys.stdout, errfile=sys.stderr):
        if response.IsOk:
            if format=="json":
                Format.DumpJson(response.Body, file=file)
            elif format=="plain":
                Format.DumpPlain(response.Body, file=file)
            elif format and gettableoutputs:
                outputs = gettableoutputs(response)
                for (output, tablefmt, tablefields) in outputs:
                    if not tablefmt:
                        tablefmt = "\t".join((f"{{!s:{len(x)}}}" for x in tablefields))
                    Format.PrintItems(output, tablefmt, tablefields, file=file)
        else:
            response.Dump(file=errfile)

if __name__ == '__main__':
    print(__file__)
    print(dir())
