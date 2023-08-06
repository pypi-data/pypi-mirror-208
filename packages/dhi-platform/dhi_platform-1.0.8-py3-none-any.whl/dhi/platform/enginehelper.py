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

import datetime
from .base.client import Contracts


class EnginesClientV2Contracts(Contracts):
    @classmethod
    def PrepareRunBody(cls, input=None, inputs=None, output=None, platformoutput=None, options=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "inputs", inputs, [])
        cls.SetBodyField(body, "output", output)
        cls.SetBodyField(body, "platformOutput", platformoutput)
        cls.SetBodyField(body, "options", options, {"poolType": "VM-S-5","nodeCount":1})
        return body

    @classmethod
    def PrepareRunPlatformBody(cls, input=None, models=None, output=None, options=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "models", models, [])
        cls.SetBodyField(body, "output", output)
        cls.SetBodyField(body, "options", options, {"poolType": "VM-S-5","nodeCount":1})
        return body

    @staticmethod
    def ComputeDuration(obj, fieldst="startedAt", fieldfin="finishedAt"):
        started = obj.get(fieldst)
        finished = obj.get(fieldfin)
        result = "-"
        if started and finished:
            tmpst = datetime.datetime.strptime(started[0:-2], "%Y-%m-%dT%H:%M:%S.%f")
            tmpfin = datetime.datetime.strptime(finished[0:-2], "%Y-%m-%dT%H:%M:%S.%f")
            result = f"{tmpfin-tmpst}"
        return result

    @classmethod
    def ComputePreparation(cls, obj, fieldst="createdAt", fieldfin="startedAt"):
        return cls.ComputeDuration(obj, fieldst, fieldfin)

    @classmethod
    def SetComputedDuration(cls, obj, field="duration", fieldst="startedAt", fieldfin="finishedAt"):
        if field:
            obj[field] = cls.ComputeDuration(obj, fieldst, fieldfin)
        return obj

    @classmethod
    def SetComputedPreparation(cls, obj, field="preparation", fieldst="createdAt", fieldfin="startedAt"):
        return cls.SetComputedDuration(obj, field, fieldst, fieldfin)


if __name__ == '__main__':
    print(__file__)
    print(dir())
