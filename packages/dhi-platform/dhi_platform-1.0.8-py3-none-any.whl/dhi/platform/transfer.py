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

import os
from pathlib import Path
import time
import uuid
import datetime
from abc import ABC, abstractmethod
from enum import Enum
from typing import Generator, List, Tuple
from dhi.platform.base.exceptions import MikeCloudException
from dhi.platform.raw import RawClientV2
from dhi.platform.transferhelper import TransferUploadHelper, download_file
from .generated.metadatagen import MetadataGenClientV1
from .metadata import MetadataClient, MetadataClientV2, MetadataClientV3, SubprojectInput
from .base import constants
from azure.storage.blob import BlobClient
from .commonmodels import DatasetType, PropertyDefinition, ItemId, TemporalValueFilter, UnitId, SpatialFilter, TemporalFilter, VerticalFilter


class ParameterDefinition:
    def __init__(self, name:str, description:str, data_type:str, required:bool, default:object=None, allowed:Tuple[object]=None) -> None:
        self._name = name
        self._description = description
        self._data_type = data_type
        self._required = required
        self._default = default
        self._allowed = allowed

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def data_type(self):
        return self._data_type

    @property
    def required(self):
        return self._required

    @property
    def default(self):
        return self._default

    @property
    def allowed(self):
        return self._allowed

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            name = body["name"],
            description = body.get("description", None),
            data_type = body["dataType"],
            required = bool(body.get("required", False)),
            default = body.get("defaultValue", None),
            allowed = body.get("allowedValues", None),
        )


class ConverterOutput:
    def __init__(self, name, description, format, parameters) -> None:
        self._name = name,
        self._description = description
        self._format = format
        self._parameters = parameters
    
    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def format(self):
        return self._format

    @property
    def parameters(self):
        return self._parameters

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            name = body["name"],
            description = body.get("description", None),
            format = body.get("datasetFormat"),
            parameters = [ParameterDefinition.from_body(p) for p in body.get("parameters", [])]
        )


class ConverterFilter(Enum):
    ALL = 0
    FILE = 1
    DEDICATED = 2


class TransferType(Enum):
    IMPORT = 0
    EXPORT = 1
    CONVERSION = 2
    APPEND = 3
    UPDATE = 4

    @classmethod
    def from_string(self, x:str):
        return {
            "import": TransferType.IMPORT,
            "export": TransferType.EXPORT,
            "conversion": TransferType.CONVERSION,
            "append": TransferType.APPEND,
            "update": TransferType.UPDATE,
        }[x.lower()]


class ImportDestination(Enum):
    DEDICATED = 0
    PROJECT = 1

    @classmethod
    def from_string(self, x:str):
        return {
            'dedicated': ImportDestination.DEDICATED, 
            'project': ImportDestination.PROJECT
        }.get(x.lower(), ImportDestination.PROJECT)


class TransferStatus(Enum):
    NONE = 0
    PENDING = 1
    INPROGRESS = 2
    COMPLETED = 3
    ERROR = 4

    @property
    def name(self):
        return "InProgress" if self is TransferStatus.INPROGRESS else super(TransferStatus, self).name.title()

    @classmethod
    def from_string(self, x:str):
        return {
            "none": TransferStatus.NONE,
            "pending": TransferStatus.PENDING,
            "inprogress": TransferStatus.INPROGRESS,
            "completed": TransferStatus.COMPLETED,
            "error": TransferStatus.ERROR,
        }.get(x.lower(), TransferStatus.NONE)

    
class AggregationType(Enum):
    MAX = 0
    MIN = 1
    AVG = 2

class CoordinateInterpretationType(Enum):
    CENTER_OF_CELL = 0
    BOTTOM_LEFT_BORDER = 1
    BORDERS = 2

    @property
    def name(self):
        return {
            CoordinateInterpretationType.CENTER_OF_CELL: "CenterOfCell",
            CoordinateInterpretationType.BOTTOM_LEFT_BORDER: "BottomLeftBorder",
            CoordinateInterpretationType.BORDERS: "Borders"
        }[self]

    @classmethod
    def from_string(self, x:str):
        return {
            "centerofcell": CoordinateInterpretationType.CENTER_OF_CELL,
            "bottomleftborder": CoordinateInterpretationType.BOTTOM_LEFT_BORDER,
            "borders": CoordinateInterpretationType.BORDERS,
        }.get(x.lower(), CoordinateInterpretationType.CENTER_OF_CELL)


class ImportParameters:
    def __init__(
        self,
        append_dataset_id,
        upload_url:str,
        file_name:str,
        srid:int,
        arguments:dict,
        destinations:Tuple[ImportDestination]
    ) -> None:
        self._append_dataset_id = append_dataset_id
        self._upload_url = upload_url
        self._file_name = file_name
        self._srid = srid
        self._arguments = arguments
        self._destinations = destinations

    @property
    def append_dataset_id(self):
        return self._append_dataset_id

    @property
    def upload_url(self):
        return self._upload_url

    @property
    def file_name(self):
        return self._file_name

    @property
    def srid(self):
        return self._srid

    @property
    def arguments(self):
        return self._arguments

    @property
    def destinations(self):
        return self._destinations
    
    @classmethod
    def from_body(cls, body:dict):
        return cls(
            append_dataset_id = body.get("appendDatasetId"),
            upload_url = body.get("uploadUrl"),
            file_name = body.get("fileName"),
            srid = body.get("srid"),
            arguments = body.get("arguments", {}),
            destinations = body.get("destinations", [])
        )


class ExportParameters:
    def __init__(
        self,
        dataset_id,
        output_file_name,
        srid:int,
        arguments:dict
    ) -> None:
        self._dataset_id = dataset_id
        self._output_file_name = output_file_name
        self._srid = srid
        self._arguments = arguments
    
    @property
    def dataset_id(self):
        return self._dataset_id
    
    @property
    def output_file_name(self):
        return self._output_file_name
    
    @property
    def srid(self):
        return self._srid
    
    @property
    def arguments(self):
        return self._arguments

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            dataset_id = body.get("datasetId"),
            output_file_name = body.get("outputFileName"),
            srid = body.get("srid"),
            arguments = body.get("arguments", {})
        )

class DatasetTransferInput:
    def __init__(self, name:str, description:str=None, metadata:dict=None, properties:dict=None) -> None:
        self._name = name
        self._description = description
        self._metadata = metadata
        self._properties = properties
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def metadata(self):
        return self._metadata

    @property
    def properties(self):
        return self._properties

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            name = body["name"],
            description = body.get("description"),
            metadata = body.get("metadata", {}),
            properties = body.get("properties", {})
        )
    
    def body(self):
        body = { "name": self._name }

        if self._description:
            body["description"] = self._description

        if self._metadata is not None:
            body["metadata"] = self._metadata

        if self._properties is not None:
            body["properties"] = self._properties

        return body


class ImportResult:
    def __init__(self, project_id, dataset_id) -> None:
        self._project_id = project_id
        self._dataset_id = dataset_id
    
    @property
    def project_id(self):
          return self._project_id
    
    @property
    def dataset_id(self):
          return self._dataset_id

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            project_id = body.get("projectId"),
            dataset_id = body.get("datasetId")
        )

        
def get_datetime_from_body(property_name:str, body:dict):
    if property_name not in body:
        return None
    else:
        property = body[property_name]
        count = len(property)
        if count == 19:
            return datetime.datetime.strptime(property, constants.DATETIMEFORMAT_SECONDS)
        else:
            return datetime.datetime.strptime(property[:26], constants.DATETIMEFORMAT)

class BaseEntityOutput:
    def __init__(
        self, 
        id,
        created_at,
        created_by,
        updated_at,
        updated_by,
        deleted_at,
        deleted_by
    ) -> None:
        self._id = id
        self._created_at = created_at
        self._created_by = created_by
        self._updated_at = updated_at
        self._updated_by = updated_by
        self._deleted_at = deleted_at
        self._deleted_by = deleted_by
    
    @property
    def id(self):
        return self._id
    
    @property
    def created_at(self):
        return self._created_at
    
    @property
    def created_by(self):
        return self._created_by
    
    @property
    def updated_at(self):
        return self._updated_at
    
    @property
    def updated_by(self):
        return self._updated_by
    
    @property
    def deleted_at(self):
        return self._deleted_at
    
    @property
    def deleted_by(self):
        return self._deleted_by

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            id = body["id"],
            created_at = get_datetime_from_body("createdAt", body),
            created_by = get_datetime_from_body("createdAy", body),
            updated_at = get_datetime_from_body("updatedAt", body),
            updated_by = get_datetime_from_body("updatedAy", body),
            deleted_at = get_datetime_from_body("deletedAt", body),
            deleted_by = get_datetime_from_body("deletedAy", body)
        )
        

class TransferOutput(BaseEntityOutput):
    def __init__(
        self,
        id,
        created_at,
        created_by,
        updated_at,
        updated_by,
        deleted_at,
        deleted_by,
        transfer_type,
        status,
        format,
        project_id,
        import_parameters,
        export_parameters,
        dataset_import_data,
        download_path,
        error_message,
        import_results
    ) -> None:
        super(TransferOutput, self).__init__(id, created_at, created_by, updated_at, updated_by, deleted_at, deleted_by)
        self._transfer_type = transfer_type
        self._status = status
        self._format = format
        self._project_id = project_id
        self._import_parameters = import_parameters
        self._export_parameters = export_parameters
        self._dataset_import_data = dataset_import_data
        self._download_path = download_path
        self._error_message = error_message
        self._import_results = import_results
    
    @property
    def transfer_type(self):
        return self._transfer_type
    
    @property
    def status(self):
        return self._status
    
    @property
    def format(self):
        return self._format
    
    @property
    def project_id(self):
        return self._project_id
    
    @property
    def import_parameters(self):
        return self._import_parameters
    
    @property
    def export_parameters(self):
        return self._export_parameters
    
    @property
    def dataset_import_data(self):
        return self._dataset_import_data
    
    @property
    def download_path(self):
        return self._download_path
    
    @property
    def error_message(self):
        return self._error_message
    
    @property
    def import_results(self) -> List[ImportResult]:
        return self._import_results

    @classmethod
    def from_body(cls, body: dict):

        import_parameters_body = body.get("importParameters")
        import_parameters = ImportParameters.from_body(import_parameters_body) if import_parameters_body else None
        export_parameters_body = body.get("exportParameters")
        export_parameters = ExportParameters.from_body(export_parameters_body) if export_parameters_body else None
        dataset_import_data_body = body.get("datasetImportData")
        dataset_import_data = DatasetTransferInput.from_body(dataset_import_data_body) if dataset_import_data_body else None
        import_results = [ImportResult.from_body(r) for r in body.get("importResults", [])]

        return cls(
            id = body.get("id"),
            created_at = body.get("createdAt"),
            created_by = body.get("createdBy"),
            updated_at = body.get("updatedAt"),
            updated_by = body.get("updatedBy"),
            deleted_at = body.get("deletedAt"),
            deleted_by = body.get("deletedBy"),
            transfer_type = TransferType.from_string(body.get("type")),
            status = TransferStatus.from_string(body.get("status")),
            format = body.get("format"),
            project_id = body.get("projectId"),
            import_parameters = import_parameters,
            export_parameters = export_parameters,
            dataset_import_data = dataset_import_data,
            download_path = body.get("downloadPath", None),
            error_message = body.get("errorMessage", None),
            import_results = import_results
        )


class SucceededUploadOutput:
    def __init__(self, file_name, dataset_id) -> None:
        self._file_name = file_name
        self._dataset_id = dataset_id
    
    @property
    def file_name(self):
        return self._file_name
    
    @property
    def dataset_id(self):
        return self._dataset_id
    
    @classmethod
    def from_body(cls, body:dict):
        return cls(
            file_name = body["fileName"],
            dataset_id = body["datasetId"]
        )


class FailedUploadOutput:
    def __init__(self, file_name, message) -> None:
        self._file_name = file_name
        self._messsage = message
    
    @property
    def file_name(self): 
        return self._file_name
    
    @property
    def message(self):
        return self._messsage

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            file_name = body["fileName"],
            message = body.get("message")
        )


class StagedFileUploadInput:
    def __init__(self, url:str, file_name:str) -> None:
        self._url = url
        self._file_name = file_name
    
    @property
    def url(self):
        return self._url
    
    @property
    def file_name(self):
        return self._file_name
    
    def body(self):
        return {
            "url": self._url,
            "fileName": self._file_name
        }


class StagedFilesUploadInput:
    def __init__(self, files:Tuple[StagedFileUploadInput], destination_path:str=None, create_destination_path_if_not_exists:bool=True) -> None:
        self._files = files
        self._destination_path = destination_path
        self._create_destination_path_if_not_exists = create_destination_path_if_not_exists
    
    
    @property
    def files(self):
            return self._files
    
    @property
    def destination_path(self): 
            return self._destination_path
    
    @property
    def create_destination_path_if_not_exists(self): 
            return self._create_destination_path_if_not_exists

    def body(self):
        body = {
            "files": [s.body() for s in self._files],
            "createDestinationPathIfNotExists": self._create_destination_path_if_not_exists
        }
        
        if self._destination_path:
            body["destingationPath"] = self._destination_path
            
        return body

class StagedFilesUploadOutput:
    def __init__(self, datasets:Tuple[SucceededUploadOutput], failures:Tuple[FailedUploadOutput]) -> None:
        self._datasets = datasets
        self._failures = failures

    @property
    def datasets(self):
        return self._datasets
    
    @property
    def failures(self):
        return self._failures

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            datasets = [SucceededUploadOutput.from_body(d) for d in body["datasets"]],
            failures = [FailedUploadOutput.from_body(d) for d in body["failures"]]
        )

class TransferSummaryOutput:
    def __init__(
        self,
        id, 
        created_at,
        created_by,
        transfer_type:TransferType,
        format,
        status:TransferStatus
    ) -> None:
        self._id = id
        self._created_at = created_at
        self._created_by = created_by
        self._transfer_type = transfer_type
        self._format = format
        self._status = status
    
    @property
    def id(self):
        return self._id
    
    @property
    def created_at(self):
        return self._created_at
    
    @property
    def created_by(self):
        return self._created_by
    
    @property
    def transfer_type(self):
        return self._transfer_type
    
    @property
    def format(self):
        return self._format
    
    @property
    def status(self):
        return self._status

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            id = body["id"], 
            created_at = get_datetime_from_body("createdAt", body),
            created_by = body.get("createdBy", None),
            transfer_type = TransferType.from_string(body["type"]),
            format = body.get("format"),
            status = TransferStatus.from_string(body.get("status"))
        )


class TransformationBase:
    pass

    @abstractmethod
    def body(self) -> dict:
        return {}

class CrsTransformation(TransformationBase):
    def __init__(self, output_srid:int, override_input_srid:int=None) -> None:
        super().__init__()
        self._output_srid = output_srid
        self._override_input_srid = override_input_srid

    @property
    def output_srid(self):
        return self._output_srid

    @property
    def override_input_srid(self):
        return self._override_input_srid
    
    def body(self) -> dict:
        body = { 
            "type": "CrsTransformation",
            "outputSrid": self._output_srid 
        }
        if self._override_input_srid:
            body["inputSrid": self._override_input_srid]
        return body
        

class ItemsFilter:
    pass

    @abstractmethod
    def body(self):
        pass


class ItemIndexFilter(ItemsFilter):
    def __init__(self, item_indices:Tuple[int]) -> None:
        super().__init__()
        self._item_indices = item_indices
    
    def body(self) -> dict:
        return { "itemIndices": list(self._item_indices) }
    

class ItemNameFilter(ItemsFilter):
    def __init__(self, names:Tuple[str]) -> None:
        super().__init__()
        self._names = names
    
    def body(self) -> dict:
        return { "names": list(self._names) }


class Aggregation:
    def __init__(self, items_filter:ItemsFilter, aggregation_type:AggregationType) -> None:
        self._items_filter = items_filter
        self._aggregation_type = aggregation_type
    
    def body(self) -> dict:
        return {
            "itemsFilter": self._items_filter.body(),
            "aggregationType": self._aggregation_type.name.title()
        }


class AggregationTransformation(TransformationBase):
    def __init__(self, aggregations:Tuple[Aggregation]) -> None:
        super().__init__()
        self._aggregations = aggregations

    def body(self) -> dict:
        return {
            "type": "AggregationTransformation",
            "aggregations": [a.body() for a in self._aggregations] 
        }


class CsScriptValueTransformation(TransformationBase):
    """Not implemented in Python SDK"""

    def __init__(self) -> None:
        super().__init__()
        raise NotImplementedError("CsScriptValueTransformation is not implemented in the Python SDK")


class ItemFilterTransformation(TransformationBase):
    def __init__(self, item_filter:Tuple[ItemsFilter]) -> None:
        super().__init__()
        self._item_filter = item_filter

    def body(self) -> dict:
        return { 
            "type": "ItemFilterTransformation",
            "itemFilter": [i.body() for i in self._item_filter] 
        }


class ItemRedefinition:
    def __init__(self, original_name:str, new_name:str, new_item_id:ItemId, new_unit_id:UnitId) -> None:
        self._original_name = original_name
        self._new_name = new_name
        self._new_item_id = new_item_id
        self._new_unit_id = new_unit_id

    def body(self) -> dict:
        body = {
            "originalName": self._original_name,
            "newName": self._new_name,
            "newItemId": self._new_item_id,
            "newUnitId": self._new_unit_id            
        }
        return body


class ItemTransformation(TransformationBase):
    def __init__(self, item_redefinitions:Tuple[ItemRedefinition]) -> None:
        super().__init__()
        self._item_redefinitions = item_redefinitions

    def body(self) -> dict:
        body = {
            "type": "ItemTransformation",
            "itemRedefinitions": [r.body() for r in self._item_redefinitions]
        }
        return body

class SpatialFilterTransformation(TransformationBase):
    def __init__(self, spatial_filter:SpatialFilter) -> None:
        super().__init__()
        self._spatial_filter = spatial_filter
    
    def body(self) -> dict:
        body = {
            "type": "SpatialFilterTransformation",
            "spatialFilter": self._spatial_filter.body()
        }
        return body


class TemporalFilterTransformation(TransformationBase):
    def __init__(self, temporal_filter:TemporalFilter) -> None:
        super().__init__()
        self._temporal_filter = temporal_filter
    
    def body(self) -> dict:
        body = {
            "type": "TemporalFilterTransformation",
            "temporalFilter": self._temporal_filter.body()
        }
        return body
        

class VerticalFilterTransformation(TransformationBase):
    def __init__(self, vertical_filter:VerticalFilter) -> None:
        super().__init__()
        self._vertical_filter = vertical_filter
    
    def body(self) -> dict:
        body = {
            "type": "VerticalFilterTransformation",
            "verticalFilter": self._vertical_filter.body()
        }
        return body


class TransferWriterBase:
    def __init__(self, parameters:tuple = ()) -> None:
        self._parameters = list(parameters)

    def __repr__(self) -> str:
        return "Writer " + str(getattr(self, "name", None))
    
    def add_parameter(self, parameter):
        self._parameters.append(parameter)
    
    @property
    def parameters(self):
        return self._parameters

    def _with_timeseries_properties_impl(self, properties:Tuple[PropertyDefinition]):
        self._parameters.append((
                "TimeSeriesProperties",
                [p.body() for p in properties]
        ))
        return self

    def _with_write_as_float_impl(self):
        self._parameters(("WriteAsFloat", True))
        return self


class GenericWriter(TransferWriterBase):
    def __init__(self, name:str, parameters: tuple = ()) -> None:
        super().__init__(parameters=parameters)
        self._name = name
    
    @property
    def name(self):
        return self._name
    
    def with_timeseries_properties(self, properties: tuple):
        return super()._with_timeseries_properties_impl(properties)
    
    def with_write_as_float(self):
        return super()._with_write_as_float_impl()


class MDWriter(TransferWriterBase):
    def __init__(self, parameters:Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "MDWriter"


class Dfs2Writer(TransferWriterBase):
    def __init__(self, parameters:Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "Dfs2Writer"

    def with_write_as_float(self):
        return super()._with_write_as_float_impl()


class TSWriter(TransferWriterBase):
    def __init__(self, parameters:Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "TSWriter"

    def with_timeseries_properties(self, properties: tuple):
        return super()._with_timeseries_properties_impl(properties)


class FileWriter(TransferWriterBase):
    def __init__(self) -> None:
        super().__init__(parameters=())
    
    @property
    def name(self):
        return "FileWriter"


class TransferReaderBase:
    def __init__(self, parameters:tuple = ()) -> None:
        self._parameters = list(parameters)

    def __repr__(self) -> str:
        return "Reader " + str(getattr(self, "name", None))

    def add_parameter(self, parameter):
        self._parameters.append(parameter)
    
    @property
    def parameters(self):
        return self._parameters

    def _with_srid_impl(self, srid:int):
        self._parameters.append(('SRID', srid))
    
    def _with_coordinate_interpretation_type_impl(self, coordinate_interpretation_type:CoordinateInterpretationType):
        self._parameters.append(('CoordinateInterpretationType', coordinate_interpretation_type.name))

    def _with_allowed_items_impl(self, allowed_items:Tuple[str]):
        self._parameters.append(("AllowedItemNames", list(allowed_items)))


class GenericReader(TransferReaderBase):
    def __init__(self, name:str, parameters: tuple = ()) -> None:
        super().__init__(parameters=parameters)
        self._name = name
    
    @property
    def name(self):
        return self._name
    
    def with_srid(self, srid:int):
        super()._with_srid_impl(srid)
    
    def with_coordinate_interpretation_type(self, coordinate_interpretation_type: CoordinateInterpretationType):
        return super()._with_coordinate_interpretation_type_impl(coordinate_interpretation_type)
    
    def with_allowed_items(self, allowed_items: Tuple[str]):
        return super()._with_allowed_items_impl(allowed_items)


class MDReader(TransferReaderBase):
    def __init__(self, parameters:Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "MDReader"


class DfsuReader(TransferReaderBase):
    def __init__(self, parameters: Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "DfsuReader"
    
    def with_srid(self, srid: int):
        return super()._with_srid_impl(srid)

    def with_allowed_items(self, allowed_items: Tuple[str]):
        return super()._with_allowed_items_impl(allowed_items)   


class Dfs2Reader(TransferReaderBase):
    def __init__(self, parameters: Tuple = ()) -> None:
        super().__init__(parameters=parameters)
    
    @property
    def name(self):
        return "Dfs2Reader"
    
    def with_allowed_items(self, allowed_items: Tuple[str]):
        return super()._with_allowed_items_impl(allowed_items)

    def with_coordinate_interpretation_type(self, coordinate_interpretation_type: CoordinateInterpretationType):
        return super()._with_coordinate_interpretation_type_impl(coordinate_interpretation_type)

    def with_srid(self, srid: int):
        return super()._with_srid_impl(srid)


class FileReader(TransferReaderBase):
    def __init__(self) -> None:
        super().__init__(parameters=())
    
    @property
    def name(self):
        return "FileReader"


class TransferPipeline:
    def __init__(self, reader, writer, transformations=[]) -> None:
        self._reader = reader
        self._writer = writer
        self._transformations = transformations
    
    @property
    def reader(self):
        return self._reader
    
    @property
    def writer(self):
        return self._writer
    
    @property
    def transformations(self):
        return self._transformations
    
    def with_reader(self, value):
        self._reader = value
        return self

    def with_reader_and_parameters(self, reader_name:str, parameters:Tuple=()):
        self._reader = GenericReader(reader_name, parameters)
        return self

    def with_writer(self, value):
        self._writer = value
        return self

    def with_writer_and_parameters(self, writer_name:str, parameters:Tuple=()):
        self._writer = GenericWriter(writer_name, parameters)
        return self
    
    def clear_transformations(self):
        self._transformations = []
        return self
    
    def with_transformation(self, transformation):
        self._transformations.append(transformation)
        return self
    

class TransferSource:
    pass


class DatasetTransferSource(TransferSource):
    def __init__(self, dataset_id) -> None:
        super().__init__()
        self._dataset_id = dataset_id

    @property
    def dataset_id(self):
        return self._dataset_id


class LocalFileTransferSource(TransferSource):
    def __init__(self, file_path, original_file_name:str=None, max_parallelism:int=2, block_size:int=20*1024*1024) -> None:
        super().__init__()
        self._file_path = file_path
        self._original_file_name = original_file_name
        self._max_parallelism = max_parallelism
        self._block_size = block_size

    @property
    def file_path(self):
        return self._file_path

    @property
    def original_file_name(self):
        return self._original_file_name

    @property
    def max_parallelism(self):
        return self._max_parallelism

    @property
    def block_size(self):
        return self._block_size


class StreamTransferSource(TransferSource):
    def __init__(self, stream, original_file_name:str=None, max_parallelism:int=2, block_size:int=20*1024*1024) -> None:
        super().__init__()
        self._stream = stream
        self._original_file_name = original_file_name
        self._max_parallelism = max_parallelism
        self._block_size = block_size

    @property
    def stream(self):
        return self._stream

    @property
    def original_file_name(self):
        return self._original_file_name

    @property
    def max_parallelism(self):
        return self._max_parallelism

    @property
    def block_size(self):
        return self._block_size


class UrlTransferSource(TransferSource):
    def __init__(self, url:str, original_file_name:str=None) -> None:
        super().__init__()
        self._url = url
        self._original_file_name = original_file_name
    
    @property
    def url(self):
        return self._url

    @property
    def original_file_name(self):
        return self._original_file_name


class DownloadTransferOutput:
    def __init__(self, url) -> None:
        self._url = url

    @property
    def url(self):
        return self._url

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            url = body["url"]
        )


class NewDatasetOutput:
    def __init__(self, project_id, dataset_id) -> None:
        self._project_id = project_id
        self._dataset_id = dataset_id

    @property
    def project_id(self):
        return self._project_id

    @property
    def dataset_id(self):
        return self._dataset_id

    @classmethod
    def from_body(cls, body:dict):
        return cls(
            project_id = body["projectId"],
            dataset_id = body["datasetId"]
        )


class EmptyTransferOutput:
    pass

    @classmethod
    def from_body(cls, body:dict):
        return cls()


class TransferProcessOutput:
    def __init__(self, transfer_id) -> None:
        self._transfer_id = transfer_id

    @property
    def transfer_id(self):
        return self._transfer_id
    
    @classmethod
    def from_body(cls, body:dict):
        return cls(body["transferId"])


class ConvertUploadInput:
    def __init__(
        self,
        original_file_name,
        upload_url,
        output_dataset_data: DatasetTransferInput,
        project_id,
        reader_parameters: Tuple,
        writer_parameters: Tuple,
        reader_name: str,
        writer_name: str,
        transformations: Tuple[TransformationBase]
    ) -> None:
        self._original_file_name = original_file_name
        self._upload_url = upload_url
        self._output_dataset_data = output_dataset_data
        self._project_id = project_id
        self._reader_parameters = list(reader_parameters)
        self._writer_parameters = list(writer_parameters)
        self._reader_name = reader_name
        self._writer_name = writer_name
        self._transformations = transformations

    @property
    def upload_url(self):
        return self._upload_url

    @upload_url.setter
    def upload_url(self, value):
        self._upload_url = value

    def body(self):
        body = {
            "originalFileName": self._original_file_name if self._original_file_name is not None else self._output_dataset_data.name,
            "uploadUrl": self._upload_url,
            "outputDatasetData": self._output_dataset_data.body(),
            "projectId": self._project_id,
            "writerName": self._writer_name
        }

        if self._reader_name is not None:
            body["readerName"] = self._reader_name

        if self._transformations:
            body["transformations"] = [t.body() for t in self._transformations]
        
        if self._reader_parameters:
            body["readerParameters"] = [{"name": p[0], "value": p[1]} for p in self._reader_parameters]
        
        if self._writer_parameters:
            body["writerParameters"] = [{"name": p[0], "value": p[1]} for p in self._writer_parameters]

        return body

class ConvertFileUpdateInput:
    def __init__(
        self,
        original_file_name:str,
        upload_url:str,
        reader_name:str,
        writer_name:str,
        reader_parameters:Tuple=None,
        writer_parameters:Tuple=None,
        transformations:Tuple=None
    ) -> None:
        self._original_file_name = original_file_name
        self._upload_url = upload_url
        self._reader_name = reader_name
        self._writer_name = writer_name
        self._reader_parameters = reader_parameters
        self._writer_parameters = writer_parameters
        self._transformations = transformations
    
    @property
    def upload_url(self):
        return self._upload_url

    @upload_url.setter
    def upload_url(self, value):
        self._upload_url = value

    def body(self) -> dict:
        body = {
            "originalFileName": self._original_file_name,
            "uploadUrl": self._upload_url,
            "readerName": self._reader_name,
            "writerName": self._writer_name
        }
        
        if self._transformations:
            body["transformations"] = [t.body() for t in self._transformations]

        if self._reader_parameters:
            body["readerParameters"] = [{"name": p[0], "value": p[1]} for p in self._reader_parameters]
        
        if self._writer_parameters:
            body["writerParameters"] = [{"name": p[0], "value": p[1]} for p in self._writer_parameters]
        
        return body

class ConvertInputBase:
    def __init__(
        self,
        reader_name:str,
        writer_name:str,
        reader_parameters:Tuple=None,
        writer_parameters:Tuple=None,
        transformations:Tuple[TransformationBase]=None
    ) -> None:
        self._reader_name = reader_name
        self._writer_name = writer_name
        self._reader_parameters = reader_parameters
        self._writer_parameters = writer_parameters
        self._transformations = transformations
    
    def body(self) -> dict:
        body = {}
        
        if self._reader_name:
            body["readerName"] = self._reader_name
        
        if self._writer_name:
            body["writerName"] = self._writer_name
        
        if self._transformations:
            body["transformations"] = [t.body() for t in self._transformations]

        if self._reader_parameters:
            body["readerParameters"] = [{"name": p[0], "value": p[1]} for p in self._reader_parameters]
        
        if self._writer_parameters:
            body["writerParameters"] = [{"name": p[0], "value": p[1]} for p in self._writer_parameters]
        
        return body


class ConvertDatasetUpdateInput(ConvertInputBase):
    def __init__(self, reader_name: str, writer_name: str, reader_parameters: Tuple = None, writer_parameters: Tuple = None, transformations: Tuple = None) -> None:
        super().__init__(reader_name, writer_name, reader_parameters=reader_parameters, writer_parameters=writer_parameters, transformations=transformations)
    
    def body(self) -> dict:
        return super().body()


class ConvertDownloadInput(ConvertInputBase):
    def __init__(self, reader_name: str, writer_name: str, reader_parameters: Tuple = None, writer_parameters: Tuple = None, transformations: Tuple = None) -> None:
        super().__init__(reader_name, writer_name, reader_parameters=reader_parameters, writer_parameters=writer_parameters, transformations=transformations)
    
    def body(self) -> dict:
        return super().body()


class ConvertExistingInput(ConvertInputBase):
    def __init__(
        self,
        output_dataset_data:DatasetTransferInput,
        project_id,
        reader_name: str,
        writer_name: str,
        reader_parameters: Tuple = None,
        writer_parameters: Tuple = None,
        transformations: Tuple = None
    ) -> None:
        super().__init__(reader_name, writer_name, reader_parameters=reader_parameters, writer_parameters=writer_parameters, transformations=transformations)
        self._output_dataset_data = output_dataset_data
        self._project_id = project_id

    def body(self) -> dict:
        body = super().body()
        body["projectId"] = self._project_id
        body["outputDatasetData"] = self._output_dataset_data.body()
        return body


class TransferProcessAwaiter:
    def __init__(self, metadataclient2:MetadataClientV2):
        self._metadata2 = metadataclient2
    
    def wait_for_finish(self, transfer_id) -> TransferOutput:
        transfer_response = self._metadata2.GetTransferV2(transfer_id)
        transfer = TransferOutput.from_body(transfer_response.Body)

        while (transfer.status != TransferStatus.COMPLETED) and (transfer.status != TransferStatus.ERROR):
            time.sleep(2)
            transfer_response = self._metadata2.GetTransferV2(transfer_id)
            transfer = TransferOutput.from_body(transfer_response.Body)
        
        return transfer


class TransferProcessInvoker:
    def __init__(self, metadataclient2:MetadataClientV2, metadataclient3:MetadataClientV3, transfer_upload_helper:TransferUploadHelper):
        self._metadata2 = metadataclient2
        self._metadata3 = metadataclient3
        self._upload_helper = transfer_upload_helper
    
    def invoke(self, process):
        
        if isinstance(process, NewDatasetTransferProcess):

            transfer_source = process.transfer_source

            if isinstance(transfer_source, LocalFileTransferSource):
                input = self._process_to_convert_upload_input(process, "http://dummyUrl", transfer_source.original_file_name)
                
                url = self._upload_helper.stage_file(transfer_source.file_path)
                    
                input.upload_url = url

                response = self._metadata3.UploadConvertV3(input.body())
            
            elif isinstance(transfer_source, UrlTransferSource):
                input = self._process_to_convert_upload_input(process, transfer_source.url, transfer_source.original_file_name)

                response = self._metadata3.UploadConvertV3(input.body())

            elif isinstance(transfer_source, StreamTransferSource):
                input = self._process_to_convert_upload_input(process, "http://dummyUrl", transfer_source.original_file_name)

                url = self._upload_helper.stage_stream(transfer_source.stream, transfer_source.max_parallelism, transfer_source.block_size)

                input.upload_url = url
                
                response = self._metadata3.UploadConvertV3(input.body())

            elif isinstance(transfer_source, DatasetTransferSource):
                input = self._process_to_convert_existing_input(process)

                response = self._metadata3.ConvertDatasetV3(input.body(), transfer_source.dataset_id)

            else:
                raise NotImplementedError("Unsupported type of transfer source: " + transfer_source + " for process " + process)

            transfer = TransferSummaryOutput.from_body(response.Body)
            return TransferProcessOutput(transfer.id)
        
        elif isinstance(process, InPlaceDatasetTransferProcess):

            transfer_source = process.transfer_source
            update_source = process.update_source

            if isinstance(update_source, UrlTransferSource):
                input = self._process_to_convert_update_input(update_source.url, update_source.original_file_name, process)
                
                response = self._metadata3.UpdateFromFileV3(input.body(), transfer_source.dataset_id)
                transfer = TransferSummaryOutput.from_body(response.Body)

            elif isinstance(update_source, StreamTransferSource):
                input = self._process_to_convert_update_input("http://dummyUrl", update_source.original_file_name, process)

                url = self._upload_helper.stage_stream(update_source.stream, update_source.max_parallelism, update_source.block_size)

                input.upload_url = url
                
                response = self._metadata3.UpdateFromFileV3(input.body(), transfer_source.dataset_id)
                transfer = TransferSummaryOutput.from_body(response.Body)
            
            elif isinstance(update_source, LocalFileTransferSource):
                input = self._process_to_convert_update_input("http://dummyUrl", update_source.original_file_name, process)

                url = self._upload_helper.stage_file(update_source.file_path, update_source.max_parallelism, update_source.block_size)

                input.upload_url = url

                response = self._metadata3.UpdateFromFileV3(input.body(), transfer_source.dataset_id)
                transfer = TransferSummaryOutput.from_body(response.Body)

            elif isinstance(update_source, DatasetTransferSource):
                input = self._process_to_convert_dataset_upload_input(process)

                response = self._metadata3.UpdateFromDatasetV3(input.body(), transfer_source.dataset_id, update_source.dataset_id)
                transfer = TransferSummaryOutput.from_body(response.Body)

            else:
                raise NotImplementedError("Unsupported type of transfer source: " + transfer_source + " for process " + process)

            return TransferProcessOutput(transfer.id)
        
        elif isinstance(process, DownloadTransferProcess):
            input = self._process_to_convert_download_input(process)

            response = self._metadata3.DownloadConvertDatasetV3(input.body(), process.transfer_source.dataset_id)
            transfer = TransferSummaryOutput.from_body(response.Body)
            return TransferProcessOutput(transfer.id)

        else:
            
            raise NotImplementedError("Unsupported type of transfer process: " + str(process))

    def _process_to_convert_upload_input(self, process, url:str, original_name:str) -> ConvertUploadInput:
        reader_parameters = None
        reader_name = None
        writer_parameters = None
        writer_name = None
        transfer_pipeline = process.transfer_pipeline

        if hasattr(transfer_pipeline, "reader"):
            reader_parameters = getattr(transfer_pipeline.reader, "parameters", ())
            reader_name = transfer_pipeline.reader.name

        if hasattr(transfer_pipeline, "writer"):
            writer_parameters = getattr(transfer_pipeline.writer, "parameters", ())
            writer_name = transfer_pipeline.writer.name

        return ConvertUploadInput(
            original_file_name=original_name,
            upload_url=url,
            output_dataset_data=process.dataset_info,
            project_id=process.destination_project_id,
            reader_parameters=reader_parameters,
            reader_name=reader_name,
            writer_parameters=writer_parameters,
            writer_name=writer_name,
            transformations=transfer_pipeline.transformations
        )

    def _process_to_convert_update_input(self, url, original_name, process) -> ConvertFileUpdateInput:
        reader_parameters = None
        reader_name = None
        writer_parameters = None
        writer_name = None
        transfer_pipeline = process.transfer_pipeline

        if hasattr(transfer_pipeline, "reader"):
            reader_parameters = getattr(transfer_pipeline.reader, "parameters", ())
            reader_name = transfer_pipeline.reader.name

        if hasattr(transfer_pipeline, "writer"):
            writer_parameters = getattr(transfer_pipeline.writer, "parameters", ())
            writer_name = transfer_pipeline.writer.name

        return ConvertFileUpdateInput(
            original_file_name=original_name,
            upload_url=url,
            reader_name=reader_name,
            writer_name=writer_name,
            reader_parameters=reader_parameters,
            writer_parameters=writer_parameters,
            transformations=transfer_pipeline.transformations
        )

    def _process_to_convert_dataset_upload_input(self, process) -> ConvertDatasetUpdateInput:
        reader_parameters = None
        reader_name = None
        writer_parameters = None
        writer_name = None
        transfer_pipeline = process.transfer_pipeline

        if hasattr(transfer_pipeline, "reader"):
            reader_parameters = getattr(transfer_pipeline.reader, "parameters", ())
            #reader_name = transfer_pipeline.reader.name
            reader_name = getattr(transfer_pipeline.reader, "name", None)

        if hasattr(transfer_pipeline, "writer"):
            writer_parameters = getattr(transfer_pipeline.writer, "parameters", ())
            #writer_name = transfer_pipeline.writer.name
            writer_name = getattr(transfer_pipeline.writer, "name", None)
            # HERE

        return ConvertDatasetUpdateInput(
            reader_name=reader_name,
            writer_name=writer_name,
            reader_parameters=reader_parameters,
            writer_parameters=writer_parameters,
            transformations=transfer_pipeline.transformations
        )

    def _process_to_convert_download_input(self, process) -> ConvertDownloadInput:
        reader_parameters = None
        reader_name = None
        writer_parameters = None
        writer_name = None
        transfer_pipeline = process.transfer_pipeline

        if hasattr(transfer_pipeline, "reader"):
            reader_parameters = getattr(transfer_pipeline.reader, "parameters", ())
            reader_name = transfer_pipeline.reader.name

        if hasattr(transfer_pipeline, "writer"):
            writer_parameters = getattr(transfer_pipeline.writer, "parameters", ())
            writer_name = transfer_pipeline.writer.name

        return ConvertDownloadInput(
            reader_name=reader_name,
            writer_name=writer_name,
            reader_parameters=reader_parameters,
            writer_parameters=writer_parameters,
            transformations=transfer_pipeline.transformations
        )

    def _process_to_convert_existing_input(self, process) -> ConvertExistingInput:
        reader_parameters = None
        reader_name = None
        writer_parameters = None
        writer_name = None
        transfer_pipeline = process.transfer_pipeline

        if hasattr(transfer_pipeline, "reader"):
            reader_parameters = getattr(transfer_pipeline.reader, "parameters", ())
            reader_name = getattr(transfer_pipeline.reader, "name", None)

        if hasattr(transfer_pipeline, "writer"):
            writer_parameters = getattr(transfer_pipeline.writer, "parameters", ())
            writer_name = getattr(transfer_pipeline.writer, "name", None)
            if writer_name is None:
                raise MikeCloudException("Writer must be specified for transfer pipeline on existing dataset")

        dataset_info = process.dataset_info

        dataset_input = DatasetTransferInput(
            name=dataset_info.name,
            description=dataset_info.description,
            metadata=dataset_info.metadata,
            properties=dataset_info.properties
        )

        return ConvertExistingInput(
            output_dataset_data = dataset_input,
            project_id=process.destination_project_id,
            reader_name = reader_name,
            writer_name = writer_name,
            reader_parameters = reader_parameters,
            writer_parameters = writer_parameters,
            transformations=transfer_pipeline.transformations
        )


class TransferProcess:
    def __init__(
        self,
        transfer_source:TransferSource,
        transfer_pipeline:TransferPipeline,
        awaiter:TransferProcessAwaiter
    ) -> None:
        self._transfer_source = transfer_source
        self._transfer_pipeline = transfer_pipeline
        self._awaiter = awaiter

    @property
    def transfer_pipeline(self) -> TransferPipeline:
        return self._transfer_pipeline

    @property
    def transfer_source(self):
        return self._transfer_source

    def execute_and_wait(self):
        transfer_process_output = self.execute()
        final_output = self._awaiter.wait_for_finish(transfer_process_output.transfer_id)
        
        if final_output.status == TransferStatus.ERROR:
            raise MikeCloudException(f"Transfer {final_output.id} finished with error: {final_output.error_message}")

        return self.create_transfer_result(final_output)

    def execute(self) -> TransferProcessOutput:
        self.validate_before_execution()
        return self.execute_self()
    
    @abstractmethod
    def validate_before_execution(self):
        pass

    @abstractmethod
    def create_transfer_result(self, transfer_output: TransferOutput):
        pass

    @abstractmethod
    def execute_self(self) -> TransferProcessOutput:
        pass

    def with_reader_and_parameters(self, reader_name:str, parameters:Tuple=()):
        self._transfer_pipeline = self._transfer_pipeline.with_reader_and_parameters(reader_name, parameters)
        return self

    def with_reader(self, reader):
        self._transfer_pipeline = self._transfer_pipeline.with_reader(reader)
        return self

    def with_writer_and_parameters(self, writer_name:str, parameters:Tuple=()):
        self._transfer_pipeline = self._transfer_pipeline.with_writer_and_parameters(writer_name, parameters)
        return self

    def with_writer(self, writer):
        self._transfer_pipeline = self._transfer_pipeline.with_writer(writer)
        return self
    
    def with_transformation(self, transformation):
        self._transfer_pipeline = self._transfer_pipeline.with_transformation(transformation)
        return self
    
    def _with_specific_reader(self, reader, configure_reader=None):
        if configure_reader and callable(configure_reader):
            configure_reader(reader)
        self.with_reader(reader)
        return self

    def _with_specific_writer(self, writer, configure_writer=None):
        if configure_writer and callable(configure_writer):
            configure_writer(writer)
        self.with_writer(writer)
        return self

    def with_dfs2_reader(self, configure_reader=None):
        """
        :param configure_reader: Optional callable to configure reader properties, e.g. to add parameters
        """
        return self._with_specific_reader(Dfs2Reader(), configure_reader)

    def with_dfsu_reader(self, configure_reader=None):
        """
        :param configure_reader: Optional callable to configure reader properties, e.g. to add parameters
        """
        return self._with_specific_reader(DfsuReader(), configure_reader)

    def with_multidimensional_writer(self, configure_writer=None):
        """
        :param configure_writer: Optional callable to configure writer properties, e.g. to add parameters
        """
        return self._with_specific_writer(MDWriter(), configure_writer)

    def with_dfs2_writer(self, configure_writer=None):
        """
        :param configure_writer: Optional callable to configure writer properties, e.g. to add parameters
        """
        return self._with_specific_writer(Dfs2Writer(), configure_writer)

    def with_timeseries_writer(self, configure_writer=None):
        """
        :param configure_writer: Optional callable to configure writer properties, e.g. to add parameters
        """
        return self._with_specific_writer(TSWriter(), configure_writer)

    def with_coordinate_system_transformation(self, output_srid:int, override_input_srid:int=None):
        """
        Include coordinate system transformation in the transfer pipeline.

        :param output_srid: Desired Spatial Reference ID of output
        :param override_input_srid: Optional Spatial Reference ID of input if different than automatically detected SRID should be used
        """
        crs_transformation = CrsTransformation(output_srid, override_input_srid)
        self._transfer_pipeline.with_transformation(crs_transformation)
        return self
    
    def with_item_filtering_transformation(self, item_indices:Tuple[int]):
        """
        Include item filtering transformation in the transfer pipeline.

        :param item_indices: Indices of the items to be included in the output
        """
        item_filter_transformation = ItemFilterTransformation(item_indices)
        self._transfer_pipeline.with_transformation(item_filter_transformation)
        return self

    def with_time_filtering_transformation(self, from_:datetime.datetime=None, to:datetime.datetime=None):
        """
        Include temporal filtering transformation in the transfer pipeline.

        :param from_: Include time slices after this time
        :param to: Include time slices before this time
        """
        if not (from_ or to):
            raise MikeCloudException("At least one of from_ or to parameters must be specified")

        if (from_ and to) and  (to < from_):
            raise MikeCloudException("Parameter from_ must be lower than parameter to")

        temporal_value_filter = TemporalValueFilter(from_, to)
        temporal_filter_transformation = TemporalFilterTransformation(temporal_value_filter)
        self._transfer_pipeline.with_transformation(temporal_filter_transformation)
        return self

    def with_spatial_filtering_transformation(self, geometry:str, srid:int=None):
        """
        Include spatial filtering transformation in the transfer pipeline.

        :param geometry: WKT polygon to select data within
        :param srid: Spatial Reference ID of the geometry if diffrent from data Spatial Reference ID
        """
        spatial_filter = SpatialFilter(geometry, srid)
        spatial_transformation = SpatialFilterTransformation(spatial_filter)
        self._transfer_pipeline.with_transformation(spatial_transformation)
        return self
    

class InPlaceDatasetTransferProcess(TransferProcess):
    def __init__(
        self, 
        transfer_source: TransferSource, 
        update_source: TransferSource,
        transfer_pipeline: TransferPipeline, 
        awaiter: TransferProcessAwaiter,
        invoker: TransferProcessInvoker
    ) -> None:
        super().__init__(transfer_source, transfer_pipeline, awaiter)
        self._update_source = update_source
        self._invoker = invoker
    
    @property
    def update_source(self) -> TransferSource:
        return self._update_source
    
    def create_transfer_result(self, transfer_output:TransferOutput) -> EmptyTransferOutput:
        return EmptyTransferOutput()
    
    def execute_self(self) -> TransferProcessOutput:
        return self._invoker.invoke(self)


class DownloadTransferProcess(TransferProcess):
    def __init__(
        self, 
        transfer_source: TransferSource, 
        transfer_pipeline: TransferPipeline,
        awaiter: TransferProcessAwaiter,
        invoker: TransferProcessInvoker,
    ) -> None:
        super().__init__(transfer_source, transfer_pipeline, awaiter)
        self._invoker = invoker

    def create_transfer_result(self, transfer_output:TransferOutput) -> DownloadTransferOutput:
        return DownloadTransferOutput(transfer_output.download_path)

    def execute_self(self) -> TransferProcessOutput:
        return self._invoker.invoke(self)


class NewDatasetTransferProcess(TransferProcess):
    def __init__(
        self,
        transfer_source: TransferSource,
        transfer_pipeline:TransferPipeline,
        destination_project_id,
        dataset_info:DatasetTransferInput,
        awaiter: TransferProcessAwaiter,
        invoker: TransferProcessInvoker
    ) -> None:
        super().__init__(transfer_source, transfer_pipeline, awaiter)
        self._destination_project_id = destination_project_id
        self._dataset_info = dataset_info
        self._invoker = invoker
    
    @property
    def dataset_info(self) -> DatasetTransferInput:
        return self._dataset_info

    @dataset_info.setter
    def dataset_info(self, value):
        self._dataset_info = value

    @property
    def transfer_source(self):
        return self._transfer_source

    @property
    def destination_project_id(self):
        return self._destination_project_id

    def with_dataset_description(self, description:str):
        self._dataset_info.description = description
        return self
    
    def with_dataset_name(self, name:str):
        self._dataset_info.name = name
        return self

    def with_dataset_metadata(self, name:str, description:str, metadata:dict=None, properties:dict=None):
        self.dataset_info = DatasetTransferInput(name, description, metadata, properties)
        return self

    def create_transfer_result(self, transfer_output:TransferOutput) -> NewDatasetOutput:
        if transfer_output.import_results and len(transfer_output.import_results) == 1:
            import_result = transfer_output.import_results[0]
            return NewDatasetOutput(import_result.project_id, import_result.dataset_id)
        
        raise MikeCloudException("Expected at least one import result of a transfer")
    
    def execute_self(self) -> TransferProcessOutput:
        return self._invoker.invoke(self)


class TransferClient():
    
    def __init__(self, inspectFnc=MetadataGenClientV1.DefaultInspectFnc, **kwargs):
        self._metadata2 = kwargs.get("MetadataClientV2", MetadataClientV2(inspectFnc, **kwargs))
        self._metadata3 = kwargs.get("MetadataClientV3", MetadataClientV3(inspectFnc, **kwargs))
        self._metadata_client = kwargs.get("MetadataClient", MetadataClient(inspectFnc, **kwargs))
        self._raw2 = kwargs.get("RawClientV2", RawClientV2(inspectFnc, **kwargs))
        self._transfer_upload_helper = TransferUploadHelper(self._metadata2)
        self._transfer_process_invoker = TransferProcessInvoker(self._metadata2, self._metadata3, self._transfer_upload_helper)
        self._transfer_process_awaiter = TransferProcessAwaiter(self._metadata2)

    def upload_file(self, local_file_path:str, project_id:str, name:str=None, description:str=None, metadata:dict=None, verbose:bool=False, timeout=60, reporter=lambda message: print(message)) -> str:
        """
        Upload a file from local path to a project in MIKE Cloud Platform.
        :param local_file_path: Path to the file to upload.
        :param project_id: ID of the project to upload to.
        :param name: Desired name of the resulting dataset, default is None for name of the file. Platform naming restrictions apply.
        :param description: Description of the dataset, default is None for no description
        :param metadata: Dictionary of any relevant metadata.
        :param verbose: True if this call should report messages, otherwise False.
        :param reporter: Function for reporting messages, takes one parameter - the message.
        :return: Dataset id of the uploaded file.
        :rtype: str
        """

        if(verbose):
            reporter("Preparing upload {}...".format(local_file_path))
        blob_url = self._metadata2.GetUploadUrlV2().Body["data"]
        blob = BlobClient.from_blob_url(blob_url)
        
        if(verbose):
            reporter("Uploading to {}...".format(blob_url))
        with open(local_file_path, "rb") as data:
            blob.upload_blob(data)
        
        if(verbose):
            reporter("Uploaded as {}".format(blob.url))
            reporter("Importing...")
        
        file_name = os.path.basename(local_file_path)
        
        output_dataset_data = { "name": file_name }
        if description:
            output_dataset_data["description"] = description
        if metadata:
            output_dataset_data["metadata"] = metadata
        
        upload_convert_input = {
            "originalFileName": file_name,
            "uploadUrl": blob_url,
            "outputDatasetData": output_dataset_data,
            "readerName": "FileReader",
            "writerName": "FileWriter",
            "projectId": project_id
        }
        
        conversion = self._metadata3.UploadConvertV3(upload_convert_input)
        transfer_id = conversion.Body["id"]

        start_time = datetime.datetime.now()
        
        waiting_times = (2, 3, 5, 8, 13, 21)
        i = 0
        while(True):
            t = datetime.datetime.now()
            
            if (start_time - t).total_seconds() >= timeout:
                raise MikeCloudException(f"Upload timed out for {local_file_path}")
            
            transfer = self._metadata2.GetTransferV2(transfer_id)
            status = transfer.Body["status"].lower()
            
            if(verbose):
                reporter(f"transfer {transfer_id} {status}")
            

            pause = waiting_times[i] if i < len(waiting_times) else waiting_times[-1]
            time.sleep(pause)
            i += 1

            if(transfer.Body["status"].lower() == "completed"):
                
                dataset_id = transfer.Body["importResults"][0]["datasetId"]
                
                if(verbose):
                    reporter(f"Imported dataset id is {dataset_id}")
                
                return dataset_id
    
    def download_file(self, project_id:str, dataset_id:str, local_file_destination:str, mode:str="w", verbose:bool=False, reporter=lambda message: print(message)) -> str:
        """
        Download dataset from a project to a local file.

        Only dataset type 'file' can be downloaded this way, no conversion is available.

        :param project_id: ID of the project to download data from
        :param dataset_id: ID of the dataset to download
        :param local_file_destination: file path to download to
        :param mode: File mode - "x" for fail if local file already exists, default is "w" for owewrite local file if already exists
        :return: path to the downloaded file
        :rtype: str
        """

        mode = mode.lower()
        if mode not in ('w', 'x', ):
            raise MikeCloudException(f"Invalid parameter mode, must be 'w' or 'x', not {mode}.")
        
        if(verbose):
            reporter("Preparing download...")
        
        response = self._raw2.GetFileSasUrlV2(project_id, dataset_id)
        blob_url = response.Body["data"]
        blob = BlobClient.from_blob_url(blob_url)
        
        if(verbose):
            reporter("Downloading...")
        
        mode += "b"
        with open(local_file_destination, mode) as f:
            download_stream = blob.download_blob()
            f.write(download_stream.readall())
        
        return local_file_destination

    def get_readers(self, filter:ConverterFilter=ConverterFilter.ALL) -> Generator[ConverterOutput, None, None]:
        response = self._metadata2.GetReadersListV2(filter.name.title())
        for d in response.Body["data"]:
            yield ConverterOutput.from_body(d)

    def get_writers(self, filter:ConverterFilter=ConverterFilter.ALL):
        response = self._metadata2.GetWritersListV2(filter.name.title())
        for d in response.Body["data"]:
            yield ConverterOutput.from_body(d)

    def get_transfer(self, transfer_id:uuid) -> TransferOutput:
        response = self._metadata2.GetTransferV2(transfer_id)
        return TransferOutput.from_body(response.Body)

    def stage_file(self, file_path:str, max_parallelism=2, block_size=20*1024*1024) -> str:
        """
        Prepare a file for import into the platform by uploading it into a staging area.

        :param file_path: Input file
        :param max_parallelism: maximum concurrency to use when files are over 64 MB
        :param block_size: max_block_size - The maximum chunk size for uploading a block blob in chunks.
        :return: Url with the staged file (the url can be used as an input for transfer operations)
        :rtype: str
        """
        return self._transfer_upload_helper.stage_file(file_path, max_parallelism, block_size) 
    
    def stage_stream(self, stream, max_parallelism:int=2, block_size:int=20*1024*1024) -> str:
        """
        Prepare a stream for import into the platform by uploading it into a staging area.

        :param stream: Input stream
        :param max_parallelism: maximum concurrency to use when files are over 64 MB
        :param block_size: max_block_size - The maximum chunk size for uploading a block blob in chunks.
        :return: Url with the staged stream (the url can be used as an input for transfer operations)
        :rtype: str
        """
        return self._transfer_upload_helper.stage_stream(stream, max_parallelism, block_size)

    
    def create_file_import(self, destination_project_id, file_path:str, max_parallelism:int=2, block_size:int=20*1024*1024) -> NewDatasetTransferProcess:
        """
        Creates a file import task based on a local file. The import will create a new dataset when executed.
        :param destination_project_id: Project id where the new dataset will end up.
        :param file_path: Path to the local file
        :param max_parallelism: Optional settings controlling the physical upload
        :param block_size: Optional settings controlling the physical upload
        :returns: Object representing the import task. Has to be executed in order for it to start.
        :rtype: NewDatasetTransferProcess
        """
        source = LocalFileTransferSource(file_path, None, max_parallelism=max_parallelism, block_size=block_size)
        pipeline = TransferPipeline(FileReader(), FileWriter())
        dataset_transfer_input = DatasetTransferInput(os.path.basename(file_path), None, None, None)

        return NewDatasetTransferProcess(
            transfer_source=source,
            transfer_pipeline=pipeline,
            destination_project_id=destination_project_id,
            dataset_info=dataset_transfer_input,
            invoker=self._transfer_process_invoker,
            awaiter=self._transfer_process_awaiter
        )


    def create_stream_import(self, destination_project_id, stream, dataset_name:str, original_file_name:str=None, max_parallelism:int=2, block_size:int=20*1024*1024) -> NewDatasetTransferProcess:
        """
        Creates a file import task based on a stream. The import will create a new dataset when executed.

        :param destination_project_id: Project id where the new dataset will end up.
        :param stream: Input stream
        :param dataset_name: Name of the output dataset
        :param original_file_name: Name representing the stream as if it was a file (the name could be important because of the file extension)
        :param max_parallelism: Optional settings controlling the physical upload
        :param block_size: Optional settings controlling the physical upload
        :returns: Object representing the import task. Has to be executed in order for it to start.
        :rtype: NewDatasetTransferProcess
        """
        source = StreamTransferSource(stream, original_file_name, max_parallelism, block_size)
        pipeline = TransferPipeline(FileReader(), FileWriter())
        dataset_transfer_input = DatasetTransferInput(dataset_name)
        
        return NewDatasetTransferProcess(
            transfer_source=source,
            transfer_pipeline=pipeline,
            destination_project_id=destination_project_id,
            dataset_info=dataset_transfer_input,
            invoker=self._transfer_process_invoker,
            awaiter=self._transfer_process_awaiter
        )


    def create_url_import(self, destination_project_id, remote_url:str, dataset_name:str, original_file_name:str=None) -> NewDatasetTransferProcess:
        """
        Creates a file import task based on a url. The import will create a new dataset when executed.

        :param destination_project_id: Project id where the new dataset will end up.
        :param remote_url: Url representing the file to be imported
        :param dataset_name: Name of the output dataset
        :param original_file_name: Name representing the stream as if it was a file (the name could be important because of the file extension)
        :returns: Object representing the import task. Has to be executed in order for it to start.
        :rtype: NewDatasetTransferProcess
        """
        source = UrlTransferSource(remote_url, original_file_name)
        pipeline = TransferPipeline(FileReader(), FileWriter())
        dataset_transfer_input = DatasetTransferInput(dataset_name)
        
        return NewDatasetTransferProcess(
            transfer_source=source,
            transfer_pipeline=pipeline,
            destination_project_id=destination_project_id,
            dataset_info=dataset_transfer_input,
            invoker=self._transfer_process_invoker,
            awaiter=self._transfer_process_awaiter
        )


    def create_dataset_copy(self, source_project_id, source_dataset_id, destination_project_id, dataset_name) -> NewDatasetTransferProcess:
        """
        Creates a dataset copy/conversion task. When executed, the task will create a new dataset based on an existing dataset.

        :param source_project_id: Parent project id of the source dataset
        :param source_dataset_id: Id of the source dataset
        :param destination_project_id: Project id for the new dataset
        :param dataset_name: Name of the new dataset        
        :returns: Object representing the copy/convert task. Has to be executed in order for it to start.
        :rtype: NewDatasetTransferProcess
        """
        source = DatasetTransferSource(source_dataset_id)
        pipeline = TransferPipeline(None, None)
        dataset_transfer_input = DatasetTransferInput(dataset_name)
        
        return NewDatasetTransferProcess(
            transfer_source=source,
            transfer_pipeline=pipeline,
            destination_project_id=destination_project_id,
            dataset_info=dataset_transfer_input,
            invoker=self._transfer_process_invoker,
            awaiter=self._transfer_process_awaiter
        )

    def create_dataset_download(self, source_project_id, source_dataset_id) -> DownloadTransferProcess:
        """
        Creates a dataset download/convert task. When executed, the task will create a url where the output of the conversion can be downloaded.

        :param source_project_id: Parent project id of the source dataset
        :param source_dataset_id: Id of the source dataset
        :returns: Object representing the download/convert task. Has to be executed in order for it to start.
        :rtype: DownloadTransferProcess
        """
        source = DatasetTransferSource(source_dataset_id)
        pipeline = TransferPipeline(None, FileWriter())
        return DownloadTransferProcess(source, pipeline, self._transfer_process_awaiter, self._transfer_process_invoker)

    def create_dataset_update_from_file(self, project_id, dataset_id, file_path:str, original_file_name:str, max_parallelism:int=2, block_size:int=20*1024*1024) -> InPlaceDatasetTransferProcess:
        """
        Creates a dataset download/convert task. When executed, the task will create a url where the output of the conversion can be downloaded.

        :param project_id: Parent project id of the target dataset
        :param dataset_id: Id of the target dataset
        :param file_path: Path to the local file
        :param max_parallelism: Optional settings controlling the physical upload
        :param block_size: Optional settings controlling the physical upload
        :returns: Object representing the dataset update task. Has to be executed in order for it to start.
        :rtype: InPlaceDatasetTransferProcess 
        """
        transfer_source = DatasetTransferSource(dataset_id)
        pipeline = TransferPipeline(None, None)
        update_source = LocalFileTransferSource(file_path, original_file_name, max_parallelism, block_size)
        return InPlaceDatasetTransferProcess(
            transfer_source,
            update_source,
            pipeline,
            self._transfer_process_awaiter,
            self._transfer_process_invoker
        )
    
    def create_dataset_update_from_stream(self, project_id, dataset_id, stream, original_file_name:str, max_parallelism:int=2, block_size:int=20*1024*1024) -> InPlaceDatasetTransferProcess:
        """
        Creates a dataset update task based on a stream. When executed, the task will update an existing dataset with the contents of the source file.

        :param project_id: Parent project id of the target dataset
        :param dataset_id: Id of the target dataset
        :param stream: Stream containing the data
        :param max_parallelism: Optional settings controlling the physical upload
        :param block_size: Optional settings controlling the physical upload
        :returns: Object representing the dataset update task. Has to be executed in order for it to start.
        :rtype: InPlaceDatasetTransferProcess 
        """
        transfer_source = DatasetTransferSource(dataset_id)
        pipeline = TransferPipeline(None, None)
        update_source = StreamTransferSource(stream, original_file_name, max_parallelism, block_size)
        return InPlaceDatasetTransferProcess(
            transfer_source,
            update_source,
            pipeline,
            self._transfer_process_awaiter,
            self._transfer_process_invoker
        )

    def create_dataset_update_from_url(self, project_id, dataset_id, remote_url:str, original_file_name:str) -> InPlaceDatasetTransferProcess:
        """
        Creates a dataset update task based on a remote url. When executed, the task will update an existing dataset with the contents of the source file.

        :param project_id: Parent project id of the target dataset
        :param dataset_id: Id of the target dataset
        :param remote_url: Url containing the data
        :param max_parallelism: Optional settings controlling the physical upload
        :param block_size: Optional settings controlling the physical upload
        :returns: Object representing the dataset update task. Has to be executed in order for it to start.
        :rtype: InPlaceDatasetTransferProcess 
        """
        transfer_source = DatasetTransferSource(dataset_id)
        pipeline = TransferPipeline(None, None)
        update_source = UrlTransferSource(remote_url, original_file_name)
        return InPlaceDatasetTransferProcess(
            transfer_source,
            update_source,
            pipeline,
            self._transfer_process_awaiter,
            self._transfer_process_invoker
        )

    def create_dataset_update_from_dataset(self, source_dataset_id, target_dataset_id) -> InPlaceDatasetTransferProcess:
        """
        Creates a dataset update task based on another dataset. When executed, the task will update an existing dataset with the contents of another dataset.
        
        :param source_dataset_id: Id of the source dataset providing updating data
        :param target_dataset_id: Id of the target dataset to be updated
        :return: Object representing the dataset update task. Has to be executed in order for it to start.
        :rtype: InPlaceDatasetTransferProcess
        """
        transfer_source = DatasetTransferSource(target_dataset_id)
        pipeline = TransferPipeline(None, None)
        update_source = DatasetTransferSource(source_dataset_id)
        return InPlaceDatasetTransferProcess(
            transfer_source,
            update_source,
            pipeline,
            self._transfer_process_awaiter,
            self._transfer_process_invoker
        )

    def list_project_transfers(self, project_id, from_:datetime.datetime=None, to:datetime.datetime=None, statuses:Tuple[TransferStatus]=()) -> Generator[TransferSummaryOutput, None, None]:
        """
        Yield transfers for specified project
        :param project_id: Id of the project
        :param from_: filter only transfers after this time
        :param to: filter only transfers before this time
        :param statuses: filter only specified transfer statuses
        :return: transfer summaries
        :rtype: Generator[TransferSummaryOutput, None, None]        
        """
        limit = 1000
        offset = 0
        first_query = True
        while True:
            if not first_query:
                if not response.Body["data"]:
                    break
            response = self._metadata2.GetProjectTransferListV2(project_id, from_=from_, to=to, status=statuses, offset=offset, limit=limit, datasetid=None)
            for i in response.Body["data"]:
                yield TransferSummaryOutput.from_body(i)
            offset = offset + limit + 1
            first_query = False
    
    def list_dataset_transfers(self, project_id, dataset_id, from_:datetime.datetime=None, to:datetime.datetime=None, statuses:Tuple[TransferStatus]=()) -> Generator[TransferSummaryOutput, None, None]:
        """
        Yield transfers for specified dataset
        :param project_id: Id of the project that holds the dataset
        :param dataset_id: Id of the dataset
        :param from_: filter only transfers after this time
        :param to: filter only transfers before this time
        :param statuses: filter only specified transfer statuses
        :return: transfer summaries
        :rtype: Generator[TransferSummaryOutput, None, None]
        """
        limit = 1000
        offset = 0
        first_query = True
        while True:
            if not first_query:
                if not response.Body["data"]:
                    break
            response = self._metadata2.GetProjectTransferListV2(projectid=project_id, from_=from_, to=to, status=statuses, offset=offset, limit=limit, datasetid=dataset_id)
            for i in response.Body["data"]:
                yield TransferSummaryOutput.from_body(i)
            offset = offset + limit + 1
            first_query = False

    def is_dataset_locked(self, project_id, dataset_id) -> bool:
        """
        Determines whether a dataset is locked by a running transfer
        
        :param project_id: Project id
        :param dataset_id: Dataset id
        :return: True if dataset is locked by a running transfer, false otherwise
        :rtype: bool
        """
        transfers = self.list_dataset_transfers(project_id, dataset_id, statuses = (TransferStatus.NONE, TransferStatus.PENDING, TransferStatus.INPROGRESS))
        return bool(next(transfers, None))

    def upload_staged_files(self, project_id, input:StagedFilesUploadInput) -> StagedFilesUploadOutput:
        """
        Uploads files prepared in stage blobs
        
        :param project_id: Project id
        :param input: Info about uploaded files
        :return: Info about succeeded and failed uploads
        :rtype: StagedFilesUploadOutput
        """
        response = self._metadata2.UploadStagedFilesV2(input.body(), project_id)
        return StagedFilesUploadOutput.from_body(response.Body)
    
    def _get_or_create_subproject(self, project_id, path, description="", members=None, metadata=None):
        name = os.path.basename(path)
        existing_subprojects = self._metadata_client.list_subprojects(project_id)
        existing_subproject = [p for p in existing_subprojects if p.name == name]
        if len(existing_subproject) > 0:
            return existing_subproject[0].id
        else:
            subproject = self._metadata_client.create_subproject(project_id, SubprojectInput(name, description, metadata, members))
            return subproject.id

    def _upload_files_to_project(self, project_id, files:list, progress_reporter = None) -> List[str]:
        uploaded = []
        for f in files:

            if progress_reporter is not None:
                progress_reporter(f)

            dataset_id = self.upload_file(f, project_id)
            uploaded.append((f, project_id, dataset_id))
        
        return uploaded

    def _remove_existing_datasets(self, subproject_id:str, files:List[str], permanently):
        datasets = self._metadata_client.list_datasets(subproject_id)
        dataset_lookup = dict([(d.name, d.id) for d in datasets])
        for f in files:
            name = os.path.basename(f)
            if name in dataset_lookup:
                self._metadata_client.delete_dataset(dataset_lookup[name], permanently=permanently)
    
    def upload_folder_to_project(self, directory, project_id, overwrite=True, filter=None, permanently=False, progress_reporter=lambda p: print(p)) -> List[tuple]:
        """
        Upload folder recursively to a project. Files are uploaded as 'File' datasets.

        Note that 'overwrite' parameter affects only datasets. If a subproject with the same name exists, it is reused. 
        This can lead to problems when for example the identity has right to read the project but not upload data there.
        To avoid any of these problems, upload to an empty project.

        :param directory: Local directory to upload from
        :param project_id: ID of the project to upload to
        :param overwrite: Overwrite datasets with the same name if they already exist, default is True.
        :param filter: Callable that takes local file path and returns True if the dataset should be downloaded. Default is None for all files. Note that this does not affect folders.
        :param progress_reporter: Callable that takes file path as parameter and prints a message when uploading the file. Set to None for no reporting.
        :param permanently: If overwrite is True. If True, datasets with conflicting names will be permanently removed, if False, they will only be moved to recycle bin
        :return: Generator of uploaded (file path, project id, dataset id)
        :rtype: Generator[str, str, str]
        """
        results = []

        projects = {directory: project_id}

        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        if filter is not None:
            files = [f for f in files if filter(f)]

        if overwrite:
            self._remove_existing_datasets(project_id, files, permanently)

        self._upload_files_to_project(project_id, files, progress_reporter)

        for (dirpath, dirnames, filenames) in os.walk(directory):
            if dirpath != directory:
                parent_folder = os.path.dirname(dirpath)
                parent_project_id = projects.get(parent_folder, None)
                
                if parent_project_id is None:
                    raise Exception(f'Invalid folder, no parent project id found for folder {parent_folder}')
                
                subproject_id = projects.get(dirpath, None)
                if subproject_id is None:
                    subproject_id = self._get_or_create_subproject(parent_project_id, dirpath)
                    projects[dirpath] = subproject_id

                files = [os.path.join(dirpath, f) for f in filenames]

                if filter is not None:
                    files = [f for f in files if filter(f)]

                if overwrite:
                    self._remove_existing_datasets(subproject_id, files, permanently)
                    
                uploaded = self._upload_files_to_project(subproject_id, files, progress_reporter)
                for u in uploaded:
                    results.append(u)

        return results


    def download_project_to_folder(self, project_id, directory, overwrite = True, filter = None, progress_reporter=lambda d: print(os.path.join(d.relativePath, d.name))) -> List[str]:
        """
        Download project content recursively to local folder. Only 'File' datasets are downloaded.

        :param project_id: ID of the project to download from
        :param directory: Local directory to download to. It will be created if not exists
        :param overwrite: Overwrite files if they already exists, default is True
        :param filter: Callable that takes DatasetRecursiveListOutput and returns True if the dataset should be downloaded. Default is None for all files.
        :param progress_reporter: Callable that takes DatasetRecursiveListOutput and prints a message when downloading the file. Set to None for no reporting.
        :return: List of downloaded file paths
        :rtype: List[str]
        """
        file_paths = []
        
        datasets = self._metadata_client.list_datasets_recursive(project_id, includesastokens = True, dataset_type = DatasetType.FILE)
        for d in datasets:
            dirpath = os.path.join(directory, d.relativePath)
            Path(dirpath).mkdir(parents=True, exist_ok=True)
            file_path = os.path.join(dirpath, d.name)
            
            if filter is not None:
                if not filter(d):
                    continue
            
            if progress_reporter is not None:
                progress_reporter(d)
            
            if os.path.isfile(file_path):
                if overwrite:
                    os.remove(file_path)
                    download_file(d.datasetUrl, file_path)
                    file_paths.append(file_path)
            else:
                download_file(d.datasetUrl, file_path)
                file_paths.append(file_path)
        
        return file_paths


if __name__ == '__main__':
    print(__file__)
    print(dir())