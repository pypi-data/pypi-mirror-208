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

import itertools
from .base.client import Contracts


class RawClientV2Contracts(Contracts):
    @classmethod
    def PrepareUploadBulkFilesInput(cls, input, id=None, sastoken=None, name=None, url=None, lastmodified=None, size=None, forcecopy=None):
        body = input.copy() if input else {}
        datasets = body.get("datasets")
        if not datasets:
            datasets = []
            body["datasets"] = datasets
        allfields = itertools.zip_longest(id if id else [], sastoken if sastoken else [], name if name else [], url if url else [], lastmodified if lastmodified else [], size if size else [], forcecopy if forcecopy else [])
        for i, sas, nm, u, lm, sz, fc in allfields:
            item = {}
            cls.SetBodyField(item, "id", i)
            cls.SetBodyField(item, "sastoken", sas)
            cls.SetBodyField(item, "name", nm)
            cls.SetBodyField(item, "url", u)
            cls.SetBodyField(item, "lastmodified", lm)
            cls.SetBodyField(item, "size", sz)
            cls.SetBodyField(item, "forcecopy", fc)
            datasets.append(item)
        return body

    @classmethod
    def PrepareGetCopyFileStatusInput(cls, input, id=None, copyoperationid=None):
        body = input.copy() if input else {}
        datasets = body.get("datasets")
        if not datasets:
            datasets = []
            body["datasets"] = datasets
        allfields = itertools.zip_longest(id if id else [], copyoperationid if copyoperationid else [])
        for i, cpi in allfields:
            item = {}
            cls.SetBodyField(item, "id", i)
            cls.SetBodyField(item, "copyOperationId", cpi)
            datasets.append(item)
        return body


if __name__ == '__main__':
    print(__file__)
    print(dir())
