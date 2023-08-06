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

from .base.client import Contracts


class TimeSeriesV2Contracts(Contracts):
    @classmethod
    def PrepareCreateTimeseriesDatasetV2Input(cls, input=None, schemaproperties=None, name=None, description=None, metadata=None, properties=None):
        body = input.copy() if input else {}
        tssch = cls.PrepareField(body, "timeSeriesSchema", {})
        cls.SetBodyField(tssch, "properties", schemaproperties, [])
        dsp = cls.PrepareField(body, "datasetProperties", {})
        cls.SetBodyField(dsp, "name", name)
        cls.SetBodyField(dsp, "description", description)
        cls.SetBodyField(dsp, "metadata", metadata, {})
        cls.SetBodyField(dsp, "properties", properties, {})
        return body

    @classmethod
    def PrepareAddTimeSeriesV2Input(cls, input=None, id=None, name=None, unit=None, item=None, datatype=None, timeseriestype=None, properties=None, datafileds=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "id", id)
        i = cls.PrepareField(body, "item", {})
        cls.SetBodyField(i, "name", name)
        cls.SetBodyField(i, "unit", unit)
        cls.SetBodyField(i, "item", item)
        cls.SetBodyField(i, "dataType", datatype)
        cls.SetBodyField(i, "timeSeriesType", timeseriestype)
        cls.SetBodyField(body, "properties", properties, {})
        cls.SetBodyField(body, "dataFileds", datafileds, [])
        return body


if __name__ == '__main__':
    print(__file__)
    print(dir())
