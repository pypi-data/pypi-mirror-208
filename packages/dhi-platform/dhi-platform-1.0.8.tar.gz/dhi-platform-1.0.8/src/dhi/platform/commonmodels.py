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
from abc import abstractmethod
from dhi.platform.base.client import DataContract
from dhi.platform.base.exceptions import MikeCloudException
from .base import constants
from enum import Enum
from typing import Tuple
from .generated.metadatagen import UnitIdV3, ItemIdV3


UnitId = UnitIdV3

ItemId = ItemIdV3

class SpatialFilter(DataContract):
    def __init__(self, geometry:str, srid:int=None) -> None:
        """
        SpatialFilter for transfer/conversion spatial filter transformation.

        :param geometry: WKT geometry (polygon) to filter by
        :param srid: Spatial Reference ID of the geometry if different from the dataset SRID
        """
        self._geometry = geometry
        self._srid = srid
    
    def body(self) -> dict:
        body = {
            "geometry": self._geometry,
        }
        if self._srid:
            body["SRID"] = self._srid
        return body

    def to_dict(self) -> dict:
        return self.body()


class TemporalFilter(DataContract):
    pass

    @abstractmethod
    def body(self) -> dict:
        return {}

    @abstractmethod
    def to_dict(self) -> dict:
        return self.body()
    
    @classmethod
    def create_index_filter(cls, from_:int=None, to:int=None):
        return TemporalIndexFilter(from_, to)

    @classmethod
    def create_value_filter(cls, from_:datetime.datetime, to:datetime.datetime):
        return TemporalValueFilter(from_, to)

    @classmethod
    def create_index_list_filter(cls, indices:Tuple[int]):
        return TemporalIndexListFilter(indices)


class TemporalIndexFilter(TemporalFilter):
    def __init__(self, from_:int=None, to:int=None) -> None:
        super().__init__()
        if from_ is None and to is None:
            raise MikeCloudException("At least one of from_ or to parameters must be specified")
        self._from = from_
        self._to = to

    def body(self) -> dict:
        body = { "type": "TemporalIndexFilter" }

        if self._from is not None:
            body["from"] = self._from

        if self._to is not None:
            body["to"] = self._to
        
        return body

        
class TemporalValueFilter(TemporalFilter):
    def __init__(self, from_:datetime.datetime, to:datetime.datetime) -> None:
        super().__init__()
        if from_ is None and to is None:
            raise MikeCloudException("At least one of from_ or to parameters must be specified")
        self._from = from_
        self._to = to
    
    def body(self) -> dict:
        body = { "type": "TemporalValueFilter" }

        if self._from:
            body["from"] = self._from.strftime(constants.DATETIMEFORMAT)
        if self._to:
            body["to"] = self._to.strftime(constants.DATETIMEFORMAT)

        return body

        
class TemporalIndexListFilter(TemporalFilter):
    def __init__(self, indices:Tuple[int]) -> None:
        super().__init__()
        self._indices = indices
    
    def body(self) -> dict:
        return { 
            "type": "TemporalIndexListFilter",
            "indices": self._indices 
        }


class VerticalFilter(DataContract):
    pass 

    @abstractmethod
    def body(self) -> dict:
        return {}

    @abstractmethod
    def to_dict(self) -> dict:
        return self.body()

    @classmethod
    def create_index_filter(cls, from_:int=None, to:int=None):
        return VerticalIndexFilter(from_, to)


class VerticalIndexFilter(VerticalFilter):
    def __init__(self, from_:int=None, to:int=None) -> None:
        if from_ is None and to is None:
            raise MikeCloudException("At least one of from_ or to parameters must be specified")
        self._from = from_
        self._to = to

    def body(self) -> dict:
        body = {
            "type": "VerticalIndexFilter",
        }
        
        if self._from:
            body["from"] = self._from
        if self._to:
            body["to"] = self._to

        return body


class AttributeDataType(Enum):
    TEXT = "Text"
    DATE = "Date"
    INT32 = "Int32"
    INT64 = "Int64"
    SINGLE = "Single"
    DOUBLE = "Double"
    INT16 = "Int16"

    @property
    def name(self):
        return self.value

    @classmethod
    def from_string(cls, x:str):
        return {
            "text": AttributeDataType.TEXT,
            "date": AttributeDataType.DATE,
            "int32": AttributeDataType.INT32,
            "int64": AttributeDataType.INT64,
            "single": AttributeDataType.SINGLE,
            "double": AttributeDataType.DOUBLE,
            "int16": AttributeDataType.INT16
        }[x.lower()]


class TimeSeriesDataType(Enum):
    INSTANTANEOUS = "Instantaneous"
    ACCUMULATED = "Accumulated"
    STEP_ACCUMULATED = "StepAccumulated"
    MEAN_STEP_BACKWARD = "MeanStepBackward"
    MEAN_STEP_FORWARD = "MeanStepForward"

    @property
    def name(self):
        return self.value

    @classmethod
    def from_string(cls, x:str):
        return {
            "instantaneous": TimeSeriesDataType.INSTANTANEOUS,
            "accumulated": TimeSeriesDataType.ACCUMULATED,
            "stepaccumulated":TimeSeriesDataType.STEP_ACCUMULATED,
            "meanstepbackward": TimeSeriesDataType.MEAN_STEP_BACKWARD,
            "meanstepforward": TimeSeriesDataType.MEAN_STEP_FORWARD
        }[x.lower()]



class ItemDefinition:
    
    def __init__(
        self,
        name:str,
        unit:str,
        item:str,
        data_type:AttributeDataType,
        timeseries_data_type: TimeSeriesDataType=None,
        no_data_value:float=None,
        has_layers:bool=False
    ) -> None:
        self._name = name
        self._unit = unit
        self._item = item
        self._data_type = data_type
        self._timeseries_data_type = timeseries_data_type
        self._no_data_value = no_data_value
        self._has_layers = has_layers
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def unit(self):
        return self._unit
    
    @property
    def item(self):
        return self._item

    @property
    def data_type(self):
        return self._data_type
        
    @property
    def timeseries_data_type(self):
        return self._timeseries_data_type
    
    @property
    def no_data_value(self):
        return self._no_data_value
    
    @property
    def has_layers(self) -> bool:
        return self._has_layers

    def body(self) -> dict:
        body = {
            "name": self._name,
            "unit": self._unit,
            "item": self._item,
            "dataType": self._data_type.name
        }
        
        if self._no_data_value is not None:
            body["noDataValue"] = self._no_data_value
        
        if self._has_layers is not None:
            body["hasLayers"] = self._has_layers
        
        if self._timeseries_data_type:
            body["timeSeriesType"] = self._timeseries_data_type.name
        
        return body

    @classmethod
    def from_body(cls, body:dict):
        ts_type = body.get("timeSeriesType", None)
        ts_data_type = None if ts_type is None else TimeSeriesDataType.from_string(ts_type)

        return cls(
            name = body["name"],
            unit = body["unit"],
            item = body["item"],
            data_type = AttributeDataType.from_string(body["dataType"]),
            timeseries_data_type = ts_data_type,
            no_data_value = body.get("noDataValue", None),
            has_layers = bool(body.get("hasLayers", False))
        )


class PropertyDataType(Enum):
    DATETIME = "DateTime"
    LONG = "Long"
    DOUBLE = "Double"
    BOOLEAN = "Boolean"
    TEXT = "Text"

    @classmethod
    def from_string(cls, x:str):
        return {
            "datetime": PropertyDataType.DATETIME,
            "long": PropertyDataType.LONG,
            "double": PropertyDataType.DOUBLE,
            "boolean": PropertyDataType.BOOLEAN,
            "text": PropertyDataType.TEXT,
        }[x.lower()]

    @property
    def name(self):
        return self.value


class PropertyDefinition:

    def __init__(self, name, data_type:PropertyDataType) -> None:
        self._name = name
        self._data_type = data_type

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def data_type(self) -> PropertyDataType:
        return self._data_type

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            name=body["name"],
            data_type=PropertyDataType.from_string(body["dataType"])
        )
    
    def body(self) -> dict:
        return { "name": self._name, "dataType": self._data_type.name }


class AttributeOperator(Enum):
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    GREATER_THAN = "GreaterThan"
    LESS_THAN = "LessThan"
    GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
    LESS_THAN_OR_EQUAL = "LessThanOrEqual"
    CONTAINS = "Contains"
    STARTS_WITH = "StartsWith"

    @property
    def name(self):
        return self.value


class DatasetType(Enum):
    FILE = "file"
    MULTIDIMENSIONAL = "multidimensional"
    TIMESERIES = "timeseries"
    GISVECTORDATA = "gisvectordata"
    TILES = "tiles"

    @property
    def name(self) -> str:
        return self.value


class SpatialOperator(Enum):
    WITHIN = "Within"
    INTERSECTS = "Intersects"

    @property
    def name(self):
        return self.value


class ComparisonOperator(Enum):
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    GREATER_THAN = "GreaterThan"
    LESS_THAN = "LessThan"
    GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
    LESS_THAN_OR_EQUAL = "LessThanOrEqual"

    @property
    def name(self):
        return self.value


class QueryCondition:

    def __init__(self, type:str):
        self._type = type
    
    @classmethod
    def create_attribute_query_condition(self, name, operator, value):
        return AttributeQueryCondition(name, operator, value)

    @classmethod
    def create_dataset_type_query_condition(self, dataset_type:DatasetType):
        return DatasetTypeQueryCondition(dataset_type)

    @classmethod
    def create_fultlext_query_condition(self, search_string):
        return FullTextQueryCondition(search_string)

    @classmethod
    def create_ids_query_condition(self, ids=Tuple[object]):
        return IdsQueryCondition(ids)

    @classmethod
    def create_spatial_query_condition(self, geometry, operator:SpatialOperator=SpatialOperator.WITHIN):
        return SpatialQueryCondition(geometry, operator)
    
    @classmethod
    def create_created_at_query_condition(self, created_at:datetime.datetime, operator:ComparisonOperator=ComparisonOperator.EQUAL):
        return CreatedAtQueryCondition(created_at, operator)
    
    @classmethod
    def create_catalog_query_condition(self, catalog_id):
        return CatalogIdQueryCondition(catalog_id)

    def body(self) -> dict:
        return { "type": self._type }


class AttributeQueryCondition(QueryCondition):

    def __init__(self, name:str, operator:AttributeOperator, value):
        super().__init__(type(self).__name__)
        self._name = name
        self._operator = operator
        self._value = value
    
    def body(self) -> dict:
        body = super().body()
        body.update({
            "name": self._name,
            "operator": self._operator.name,
            "value": self._value
        })
        return body


class DatasetTypeQueryCondition(QueryCondition):

    def __init__(self, dataset_type:DatasetType):
        super().__init__(type(self).__name__)
        self._dataset_type = dataset_type

    def body(self) -> dict:
        body = super().body()
        body.update({
            "datasetType": self._dataset_type.name
        })
        return body


class FullTextQueryCondition(QueryCondition):

    def __init__(self, search_string:str):
        super().__init__(type(self).__name__)
        self._search_string = search_string

    def body(self) -> dict:
        body = super().body()
        body.update({
            "searchString": self._search_string
        })
        return body


class IdsQueryCondition(QueryCondition):

    def __init__(self, ids=Tuple[object]):
        super().__init__(type(self).__name__)
        self._ids = ids

    def body(self) -> dict:
        body = super().body()
        body.update({
            "ids": self._ids
        })
        return body


class SpatialQueryCondition(QueryCondition):

    def __init__(self, geometry:object, operator:SpatialOperator=SpatialOperator.WITHIN):
        super().__init__(type(self).__name__)
        self._geometry = geometry
        self._operator = operator

    def body(self) -> dict:
        body = super().body()
        body.update({
            "geometry": self._geometry,
            "operator": self._operator.name
        })
        return body


class CreatedAtQueryCondition(QueryCondition):

    def __init__(self, created_at:datetime.datetime, operator:ComparisonOperator=ComparisonOperator.EQUAL):
        super().__init__(type(self).__name__)
        self._created_at = created_at
        self._operator = operator

    def body(self) -> dict:
        body = super().body()
        body.update({
            "createdAt": self._created_at.strftime(constants.DATETIMEFORMAT),
            "operator": self._operator.name
        })
        return body


class CatalogIdQueryCondition(QueryCondition):

    def __init__(self, catalog_id):
        super().__init__(type(self).__name__)
        self._catalog_id = catalog_id

    def body(self) -> dict:
        body = super().body()
        body.update({
            "catalogId": self._catalog_id
        })
        return body