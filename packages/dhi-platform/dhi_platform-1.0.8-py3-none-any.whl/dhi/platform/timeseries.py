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
import pandas as pd
from dateutil import parser

from dhi.platform.base.utils import sanitize_from_to
from dhi.platform.metadata import MetadataClient
from .base import constants
from enum import Enum
from typing import Generator, List, Tuple
from dhi.platform.commonmodels import ItemDefinition, PropertyDefinition, QueryCondition
from .generated.timeseriesgen import TimeSeriesGenClientV2

class TimeseriesDatasetOutput:

    def __init__(
        self,
        id,
        items:Tuple[ItemDefinition],
        timeseries_properties:Tuple[PropertyDefinition],
        metadata:dict={}
    ) -> None:
        self._id = id
        self._items = items
        self._timeseries_properties = timeseries_properties
        self._metadata = metadata
    
    @property
    def id(self):
        return self._id
    
    @property
    def items(self) -> Tuple[ItemDefinition]:
        return self._items

    
    @property
    def timeseries_properties(self) -> Tuple[PropertyDefinition]:
        return self._timeseries_properties

    @property
    def metadata(self) -> dict:
        return self._metadata

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            id = body["id"],
            items = [ItemDefinition.from_body(i) for i in body["items"]],
            timeseries_properties = [PropertyDefinition.from_body(p) for p in body.get("timeSeriesProperties", ())],
            metadata = body.get("metadata", {})
        )

class TimeSeriesDatasetInput:

    def __init__(
        self,
        name:str,
        description:str=None,
        timeseries_schema:Tuple[PropertyDefinition]=(),
        metadata:dict=None,
        properties:dict=None        
    ) -> None:
        self._name = name
        self._description = description
        self._timeseries_schema = timeseries_schema
        self._metadata = metadata
        self._properties = properties

    def body(self) -> dict:
        
        dataset_properties = { "name": self._name }
        
        if self._description is not None:
            dataset_properties["description"] = self._description
        if self._metadata is not None:
            dataset_properties["metadata"] = self._metadata
        if self._properties is not None:
            dataset_properties["properties"] = self._properties
        
        timeseries_properties = [p.body() for p in self._timeseries_schema]
        
        return {
            "timeSeriesSchema": {
                    "properties": timeseries_properties
                },
            "datasetProperties": dataset_properties
        }


class DataFieldDataType(Enum):
    DATETIME = "DateTime"
    SINGLE = "Single"
    DOUBLE = "Double"
    FLAG = "Flag"
    TEXT = "Text"

    @property
    def name(self):
        return self.value

    @classmethod
    def from_string(self, x:str):
        return {
            "datetime": DataFieldDataType.DATETIME,
            "single": DataFieldDataType.SINGLE,
            "double": DataFieldDataType.DOUBLE,
            "flag": DataFieldDataType.FLAG,
            "text": DataFieldDataType.TEXT
        }[x.lower()]


class FlagDefinition:

    def __init__(self, id:int, name:str, level:int, description:str=None) -> None:
        self._id = id
        self._name = name
        self._description = description
        self._level = level
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def level(self) -> int:
        return self._level

    def body(self) -> dict:
        body = {
            "id": self._id,
            "name": self._name,
            "level": self._level
        }

        if self._description is not None:
            body["description"] = self._description

        return body

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            id = body["id"],
            name = body["name"],
            level = body["level"],
            description = body.get("description", None)
        )
    

class DataFieldDefinition:

    def __init__(self, name:str, data_type:DataFieldDataType, flags:Tuple[FlagDefinition]=()) -> None:
        self._name = name
        self._data_type = data_type
        self._flags = flags
    
    @property
    def name(self) -> str: 
        return self._name
    
    @property
    def data_type(self) -> DataFieldDataType: 
        return self._data_type
    
    @property
    def flags(self) -> Tuple[FlagDefinition]: 
        return self._name

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            name = body["name"],
            data_type = DataFieldDataType.from_string(body["dataType"]),
            flags = [FlagDefinition.from_body(f) for f in body.get("flags", ())]
        )

    def body(self) -> dict:
        return {
            "name": self._name,
            "dataType": self._data_type.name,
            "flags": [f.body() for f in self._flags]
        }


class TimeSeriesDefinition:

    def __init__(
        self,
        id:str,
        item:ItemDefinition,
        properties:dict,
        data_fields:Tuple[DataFieldDefinition]=()
    ) -> None:
        self._id = id
        self._item = item
        self._properties = properties
        self._data_fields = data_fields
    
    @property
    def id(self) -> str: 
        return self._id
    
    @property
    def item(self) -> ItemDefinition: 
        return self._item
    
    @property
    def properties(self) -> dict: 
        return self._properties
    
    @property
    def data_fields(self) -> Tuple[DataFieldDefinition]: 
        return self._data_fields

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            id = body.get("id", None),
            item = ItemDefinition.from_body(body["item"]),
            properties = body.get("properties", {}),
            data_fields = [DataFieldDefinition.from_body(f) for f in body.get("dataFields", ())]
        )

    def body(self) -> dict:
        body = {
            "item": self._item.body(),
            "dataFields": [f.body() for f in self._data_fields]
        }

        if self._properties is not None:
            body["properties"] = self._properties

        if self._id:
            body["id"] = self._id
        
        return body


class TimeSeriesClientV2(TimeSeriesGenClientV2):
    def __init__(self, inspectFnc=TimeSeriesGenClientV2.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)

class TimeSeriesClient():
    
    def __init__(self, inspectFnc=TimeSeriesGenClientV2.DefaultInspectFnc, **kwargs):
        self._metadata = kwargs.get("MetadataClient", MetadataClient(inspectFnc, **kwargs))
        self._ts2 = kwargs.get("TimeSeriesGenClientV2", TimeSeriesGenClientV2(inspectFnc, **kwargs))

    def _read_timeseries_data_from_response_data(self, data, data_fields:Tuple[DataFieldDefinition]=()):
        date_times = []
        values = []
        field_values = {}
        for field in data_fields:
            field_values[field.name] = []
        
        for row in data:
            s = row[0]
            t = parser.parse(s)
            date_times.append(t)
            v = row[1]
            values.append(None if v is None else v)
            for f, field in enumerate(data_fields):
                field_value = row[2+f]
                field_values[field.name].append(field_value)
        
        field_values.update({"values": values})
        timeseries_data = pd.DataFrame(field_values, index=date_times)

        return timeseries_data

    def get_timeseries_dataset(self, project_id, dataset_id) -> TimeseriesDatasetOutput:
        """
        Get details about time series dataset
        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :return: Time series dataset
        :rtype: TimeseriesDatasetOutput
        """
        response = self._ts2.GetTimeSeriesDatasetV2(project_id, dataset_id)
        return TimeseriesDatasetOutput.from_body(response.Body)
    
    def create_timeseries_dataset(self, project_id, input:TimeSeriesDatasetInput):
        """
        Create a new time series dataset

        :param project_id: ID of the project with the timeseries dataset
        :param input: Timeseries dataset input
        :return: Timeseries dataset
        :rtype: TimeseriesDatasetOutput
        """
        response = self._ts2.CreateTimeseriesDatasetV2(project_id, input.body())
        output = TimeseriesDatasetOutput.from_body(response.Body)
        self._metadata.wait_until_dataset_exists(output.id)
        return output

    def create_timeseries_dataset_from_schema(self, project_id, name:str, description:str=None, timeseries_schema:Tuple[PropertyDefinition]=()):
        """
        Create a new timeseries dataset
        
        :param project_id: ID of the project with the timeseries dataset
        :param name: Dataset name
        :param description: Dataset description
        :param timeseries_schema: Definition of the properties each time series should have
        :return: Timeseries dataset
        :rtype: TimeSeriesDatasetOutput
        """
        input = TimeSeriesDatasetInput(name, description, timeseries_schema)
        response = self._ts2.CreateTimeseriesDatasetV2(project_id, input.body())
        output =  TimeseriesDatasetOutput.from_body(response.Body)
        self._metadata.wait_until_dataset_exists(output.id)
        return output
    
    def add_timeseries_dataset_properties(self, project_id, properties:Tuple[PropertyDefinition]) -> bool:
        """
        Add new property definitions into time series dataset.
        
        :param project_id: ID of the project with the timeseries dataset
        :param properties: Property definitions
        :return: True if the dataset was created successfully
        :rtype: bool
        """
        input = {"properties": [p.body() for p in properties]}
        response = self._ts2.AddDatasetSchemaPropertiesV2(project_id, input)
        return response.IsOk

    def get_timeseries(self, project_id, dataset_id, timeseries_id) -> TimeSeriesDefinition:
        """
        Get details about time series
        
        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries to get
        :return: Timeseries definition
        :rtype: TimeSeriesDefinition
        """
        response = self._ts2.GetTimeSeriesByIdV2(project_id, dataset_id, timeseries_id)
        return TimeSeriesDefinition.from_body(response.Body)

    def get_timeseries_values(self, project_id, dataset_id, timeseries_id, from_:datetime.datetime=None, to:datetime.datetime=None) -> pd.DataFrame:
        """
        Get time series values
        
        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries to get values from
        :return: Pandas DataFrame
        """
        from_, to = sanitize_from_to(from_, to)
        ts = self.get_timeseries(project_id, dataset_id, timeseries_id)
        response = self._ts2.GetTimeSeriesDataV2(project_id, dataset_id, timeseries_id, from_, to)
        data = response.Body["data"]
        return self._read_timeseries_data_from_response_data(data, ts.data_fields)
    
    def list_timeseries(self, project_id, dataset_id) -> Generator[TimeSeriesDefinition, None, None]:
        """
        Get list of dataset's time series
        
        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :return: Generator of timeseries definitions
        """
        response = self._ts2.GetAllTimeSeriesV2(project_id, dataset_id)
        data = response.Body["data"]
        return (TimeSeriesDefinition.from_body(t) for t in data)

    def query_timeseries(self, project_id, dataset_id, conditions:Tuple[QueryCondition]) -> Generator[TimeSeriesDefinition, None, None]:
        """
        Query time series by name or property value(s)
        
        Query filter example to get "Rainfall" time series with "CX" property equal to {1}: 
        conditions = (  AttributeQueryCondition("Item", "Equal", "Rainfall"),
                        "AttributeQueryCondition("CX", "Equal", 1),
                    )

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param conditions: QueryConditions the timeseries should fulfill.
        :return: Generator of timeseries definitions
        """
        input = { "conditions": [c.body() for c in conditions] }
        response = self._ts2.GetQueryTimeSeriesV2(project_id, input, dataset_id)
        return (TimeSeriesDefinition.from_body(t) for t in response.Body["data"])
    
    def get_multiple_timeseries_values(self, project_id, dataset_id, timeseries_ids:Tuple[str], from_=None, to=None) -> Generator[pd.DataFrame, None, None]:
        """
        Get timeseries values

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries
        :param timeseries_ids: IDs of the timeseries to get values from
        :return: Generator of data frames where each data frame corresponds to a timeseries id
        """
        from_, to = sanitize_from_to(from_, to)

        data_fields = [self.get_timeseries(project_id, dataset_id, i).data_fields for i in timeseries_ids]
        response = self._ts2.GetMultiTimeSeriesDataV2(project_id, timeseries_ids, dataset_id, from_, to)
        data = response.Body["data"]

        for i, d in enumerate(data):
            yield self._read_timeseries_data_from_response_data(d, data_fields[i])
        
    def add_timeseries(self, project_id, dataset_id, item:ItemDefinition, properties:dict=None, data_fields:Tuple[DataFieldDefinition]=()):
        """
        Create a new timeseries

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param item: Definition of the timeseries item
        :param properties: Name-value dictionary of timeseries properties
        :param data_fields: Definition of the data fields of the timeseries
        :return: Timeseries definition
        :rtype: TimeSeriesDefinition
        """
        return self.add_timeseries_with_id(project_id, dataset_id, None, item, properties, data_fields)     

    def add_timeseries_with_id(self, project_id, dataset_id, timeseries_id:str, item:ItemDefinition, properties:dict=None, data_fields:Tuple[DataFieldDefinition]=()):
        """
        Create a new timeseries

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: Desired ID of the timeseries
        :param item: Definition of the timeseries item
        :param properties: Name-value dictionary of timeseries properties
        :param data_fields: Definition of the data fields of the timeseries
        :return: Timeseries definition
        :rtype: TimeSeriesDefinition
        """
        input = TimeSeriesDefinition(
            timeseries_id,
            item,
            properties,
            data_fields
        )
        
        response = self._ts2.AddTimeSeriesV2(project_id, input.body(), dataset_id)
        return TimeSeriesDefinition.from_body(response.Body)
    
    def update_timeseries_properties(self, project_id, dataset_id, timeseries_id, properties:dict) -> bool:
        """
        Update all timeseries properties

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries
        :param properties: Name-value dictionary of the new properties for the timeseries.
            Note that properties not included in the dictionary will be set to None.
            Always include full set of properties as you want it to look after the update
        :return: True if the timeseries properties were updated successfully
        :rtype: bool
        """
        input = { "properties": properties }
        response = self._ts2.SetAllTimeSeriesPropertiesV2(project_id, input, dataset_id, timeseries_id)
        return response.IsOk

    def delete_timeseries(self, project_id, dataset_id, timeseries_id) -> bool:
        """
        Delete timeseries from dataset

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries
        :return: True if the timeseries was removed successfully
        :rtype: bool
        """
        response = self._ts2.DeleteTimeSeriesV2(project_id, dataset_id, timeseries_id)
        return response.IsOk

    def update_timeseries_property(self, project_id, dataset_id, timeseries_id, property_name, property_value) -> bool:
        """
        Update a single timeseries property

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries
        :param property_name: Name of the property to update
        :param property_value: New value for the property to update
        :return: True if the value was updated successfully
        :rtype: bool
        """
        input = { "property": property_name, "value": property_value }
        response = self._ts2.SetTimeSeriesPropertyV2(project_id, input, dataset_id, timeseries_id)
        return response.IsOk

    def delete_timeseries_values(self, project_id, dataset_id, timeseries_id, from_:datetime.datetime=None, to:datetime.datetime=None) -> bool:
        """
        Delete timeseries values

        :param project_id: ID of the project with the timeseries dataset
        :param dataset_id: ID of the timeseries dataset
        :param timeseries_id: ID of the timeseries
        :param from_: optional time from which the values should be removed
        :param to: optional time to which the values should be removed
        :return: True if the values were removed successfully
        :rtype: bool
        """
        from_, to = sanitize_from_to(from_, to)

        response = self._ts2.DeleteTimeSeriesValuesV2(project_id, dataset_id, timeseries_id, from_, to)
        return response.IsOk

    def add_timeseries_values(self, project_id, dataset_id, timeseries_id, data:pd.DataFrame,
        datetimeindex=0, valueindex=1, flagindex=None
    ) -> bool:
        """
        Add timeseries values to a timeseries
        
        :param data: Pandas data frame with index of datetime.datetime and one column matching the timeseries data type
        :param datetimeindex: Optional parameter indicating the datetime field index in the data frame, default is 0
        :param valueindex: Optional parameter indicating the value field index in the data frame, default is 1
        :param flagindex: Optional, if the data frame contains a flag, provide the flag field index using this parameter, default is None
        :return: A value indicating whether the operation was successfull (True) or not (False)
        :rtype: bool
        """
        separator = ";"
        input = data.to_csv(sep=separator, date_format=constants.DATETIMEFORMAT_SECONDS, header=False)
        response = self._ts2.UploadCsvDataV2(project_id, input, dataset_id, timeseries_id, datetimeindex=datetimeindex, delimiter=separator, decimalseparator=".", valueindex=valueindex, flagindex=flagindex, content_type="text/plain")
        return response.IsOk


if __name__ == '__main__':
    print(__file__)
    print(dir())
