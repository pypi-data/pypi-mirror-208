# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "gis" "--classname" "GisGenClientV" "-n" "2" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\gisgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/gis/v2"
# 2022-01-13 19:02:32.131166Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/gis/v2
# DHI Water Data GIS API - Version 2
# API for managing features, feature attributes and feature collections
# 2

StringCollectionResponseV2Type = TypeVar("StringCollectionResponseV2Type", bound="StringCollectionResponseV2")

@attr.s(auto_attribs=True)
class StringCollectionResponseV2(DataContract):
    data: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: StringCollectionResponseV2Type, src_dict: Dict[str, Any]) -> StringCollectionResponseV2Type:
        obj = StringCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

SelectClauseV2Type = TypeVar("SelectClauseV2Type", bound="SelectClauseV2")

@attr.s(auto_attribs=True)
class SelectClauseV2(DataContract):
    outputSRID: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SelectClauseV2Type, src_dict: Dict[str, Any]) -> SelectClauseV2Type:
        obj = SelectClauseV2()
        obj.load_dict(src_dict)
        return obj

SelectAllAttributesV2Type = TypeVar("SelectAllAttributesV2Type", bound="SelectAllAttributesV2")

@attr.s(auto_attribs=True)
class SelectAllAttributesV2(SelectClauseV2):
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SelectClauseV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SelectAllAttributesV2Type, src_dict: Dict[str, Any]) -> SelectAllAttributesV2Type:
        obj = SelectAllAttributesV2()
        obj.load_dict(src_dict)
        return obj

ProjectOutputV2Type = TypeVar("ProjectOutputV2Type", bound="ProjectOutputV2")

@attr.s(auto_attribs=True)
class ProjectOutputV2(DataContract):
    inputSrid: int = None
    outputSrid: int = None
    geometries: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectOutputV2Type, src_dict: Dict[str, Any]) -> ProjectOutputV2Type:
        obj = ProjectOutputV2()
        obj.load_dict(src_dict)
        return obj

DeleteAttributeInputV2Type = TypeVar("DeleteAttributeInputV2Type", bound="DeleteAttributeInputV2")

@attr.s(auto_attribs=True)
class DeleteAttributeInputV2(DataContract):
    name: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DeleteAttributeInputV2Type, src_dict: Dict[str, Any]) -> DeleteAttributeInputV2Type:
        obj = DeleteAttributeInputV2()
        obj.load_dict(src_dict)
        return obj

QueryConditionV2Type = TypeVar("QueryConditionV2Type", bound="QueryConditionV2")

@attr.s(auto_attribs=True)
class QueryConditionV2(DataContract):
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: QueryConditionV2Type, src_dict: Dict[str, Any]) -> QueryConditionV2Type:
        obj = QueryConditionV2()
        obj.load_dict(src_dict)
        return obj

FeatureQueryV2Type = TypeVar("FeatureQueryV2Type", bound="FeatureQueryV2")

@attr.s(auto_attribs=True)
class FeatureQueryV2(DataContract):
    selectClause: SelectClauseV2 = None
    conditions: List[QueryConditionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FeatureQueryV2Type, src_dict: Dict[str, Any]) -> FeatureQueryV2Type:
        obj = FeatureQueryV2()
        obj.load_dict(src_dict)
        return obj

ProjectInputV2Type = TypeVar("ProjectInputV2Type", bound="ProjectInputV2")

@attr.s(auto_attribs=True)
class ProjectInputV2(DataContract):
    inputSrid: int = None
    outputSrid: int = None
    geometries: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectInputV2Type, src_dict: Dict[str, Any]) -> ProjectInputV2Type:
        obj = ProjectInputV2()
        obj.load_dict(src_dict)
        return obj

class SpatialOperatorV2(str, Enum):
    INTERSECTS = "Intersects"
    WITHIN = "Within"
    def __str__(self) -> str:
        return str(self.value)

SpatialQueryConditionV2Type = TypeVar("SpatialQueryConditionV2Type", bound="SpatialQueryConditionV2")

@attr.s(auto_attribs=True)
class SpatialQueryConditionV2(QueryConditionV2):
    geometry: str = None
    operator: SpatialOperatorV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SpatialQueryConditionV2Type, src_dict: Dict[str, Any]) -> SpatialQueryConditionV2Type:
        obj = SpatialQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

ProblemDetailsV2Type = TypeVar("ProblemDetailsV2Type", bound="ProblemDetailsV2")

@attr.s(auto_attribs=True)
class ProblemDetailsV2(DataContract):
    type: str = None
    title: str = None
    status: int = None
    detail: str = None
    instance: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProblemDetailsV2Type, src_dict: Dict[str, Any]) -> ProblemDetailsV2Type:
        obj = ProblemDetailsV2()
        obj.load_dict(src_dict)
        return obj

ValidationProblemDetailsV2Type = TypeVar("ValidationProblemDetailsV2Type", bound="ValidationProblemDetailsV2")

@attr.s(auto_attribs=True)
class ValidationProblemDetailsV2(ProblemDetailsV2):
    errors: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ProblemDetailsV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ValidationProblemDetailsV2Type, src_dict: Dict[str, Any]) -> ValidationProblemDetailsV2Type:
        obj = ValidationProblemDetailsV2()
        obj.load_dict(src_dict)
        return obj

class ComparisonOperatorV2(str, Enum):
    EQUAL = "Equal"
    NOTEQUAL = "NotEqual"
    GREATERTHAN = "GreaterThan"
    LESSTHAN = "LessThan"
    GREATERTHANOREQUAL = "GreaterThanOrEqual"
    LESSTHANOREQUAL = "LessThanOrEqual"
    def __str__(self) -> str:
        return str(self.value)

class AttributeOperatorV2(str, Enum):
    EQUAL = "Equal"
    NOTEQUAL = "NotEqual"
    GREATERTHAN = "GreaterThan"
    LESSTHAN = "LessThan"
    GREATERTHANOREQUAL = "GreaterThanOrEqual"
    LESSTHANOREQUAL = "LessThanOrEqual"
    CONTAINS = "Contains"
    STARTSWITH = "StartsWith"
    def __str__(self) -> str:
        return str(self.value)

AttributeQueryConditionV2Type = TypeVar("AttributeQueryConditionV2Type", bound="AttributeQueryConditionV2")

@attr.s(auto_attribs=True)
class AttributeQueryConditionV2(QueryConditionV2):
    name: str = None
    operator: AttributeOperatorV2 = None
    value: None = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AttributeQueryConditionV2Type, src_dict: Dict[str, Any]) -> AttributeQueryConditionV2Type:
        obj = AttributeQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

IdsQueryConditionV2Type = TypeVar("IdsQueryConditionV2Type", bound="IdsQueryConditionV2")

@attr.s(auto_attribs=True)
class IdsQueryConditionV2(QueryConditionV2):
    ids: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IdsQueryConditionV2Type, src_dict: Dict[str, Any]) -> IdsQueryConditionV2Type:
        obj = IdsQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

FullTextQueryConditionV2Type = TypeVar("FullTextQueryConditionV2Type", bound="FullTextQueryConditionV2")

@attr.s(auto_attribs=True)
class FullTextQueryConditionV2(QueryConditionV2):
    searchString: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FullTextQueryConditionV2Type, src_dict: Dict[str, Any]) -> FullTextQueryConditionV2Type:
        obj = FullTextQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

CreatedAtQueryConditionV2Type = TypeVar("CreatedAtQueryConditionV2Type", bound="CreatedAtQueryConditionV2")

@attr.s(auto_attribs=True)
class CreatedAtQueryConditionV2(QueryConditionV2):
    createdAt: str = None
    operator: ComparisonOperatorV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CreatedAtQueryConditionV2Type, src_dict: Dict[str, Any]) -> CreatedAtQueryConditionV2Type:
        obj = CreatedAtQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

IFeatureV2Type = TypeVar("IFeatureV2Type", bound="IFeatureV2")

@attr.s(auto_attribs=True)
class IFeatureV2(DataContract):
    id: int = None
    geometry: str = None
    attributes: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IFeatureV2Type, src_dict: Dict[str, Any]) -> IFeatureV2Type:
        obj = IFeatureV2()
        obj.load_dict(src_dict)
        return obj

CoordinateSystemOutputV2Type = TypeVar("CoordinateSystemOutputV2Type", bound="CoordinateSystemOutputV2")

@attr.s(auto_attribs=True)
class CoordinateSystemOutputV2(DataContract):
    id: int = None
    name: str = None
    authority: str = None
    wkt: str = None
    proj4String: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CoordinateSystemOutputV2Type, src_dict: Dict[str, Any]) -> CoordinateSystemOutputV2Type:
        obj = CoordinateSystemOutputV2()
        obj.load_dict(src_dict)
        return obj

CoordinateSystemOutputCollectionResponseV2Type = TypeVar("CoordinateSystemOutputCollectionResponseV2Type", bound="CoordinateSystemOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class CoordinateSystemOutputCollectionResponseV2(DataContract):
    data: List[CoordinateSystemOutputV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CoordinateSystemOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> CoordinateSystemOutputCollectionResponseV2Type:
        obj = CoordinateSystemOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

SelectCustomAttributesV2Type = TypeVar("SelectCustomAttributesV2Type", bound="SelectCustomAttributesV2")

@attr.s(auto_attribs=True)
class SelectCustomAttributesV2(SelectClauseV2):
    attributes: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SelectClauseV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SelectCustomAttributesV2Type, src_dict: Dict[str, Any]) -> SelectCustomAttributesV2Type:
        obj = SelectCustomAttributesV2()
        obj.load_dict(src_dict)
        return obj

class DatasetTypeV2(str, Enum):
    FILE = "file"
    MULTIDIMENSIONAL = "multidimensional"
    TIMESERIES = "timeseries"
    GISVECTORDATA = "gisvectordata"
    TILES = "tiles"
    def __str__(self) -> str:
        return str(self.value)

DatasetTypeQueryConditionV2Type = TypeVar("DatasetTypeQueryConditionV2Type", bound="DatasetTypeQueryConditionV2")

@attr.s(auto_attribs=True)
class DatasetTypeQueryConditionV2(QueryConditionV2):
    datasetType: DatasetTypeV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DatasetTypeQueryConditionV2Type, src_dict: Dict[str, Any]) -> DatasetTypeQueryConditionV2Type:
        obj = DatasetTypeQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

class AttributeDataTypeV2(str, Enum):
    TEXT = "Text"
    DATE = "Date"
    INT32 = "Int32"
    INT64 = "Int64"
    SINGLE = "Single"
    DOUBLE = "Double"
    INT16 = "Int16"
    def __str__(self) -> str:
        return str(self.value)

IFeatureAttributeV2Type = TypeVar("IFeatureAttributeV2Type", bound="IFeatureAttributeV2")

@attr.s(auto_attribs=True)
class IFeatureAttributeV2(DataContract):
    dataType: AttributeDataTypeV2 = None
    defaultValue: None = None
    label: str = None
    length: int = None
    name: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IFeatureAttributeV2Type, src_dict: Dict[str, Any]) -> IFeatureAttributeV2Type:
        obj = IFeatureAttributeV2()
        obj.load_dict(src_dict)
        return obj

IFeatureClassV2Type = TypeVar("IFeatureClassV2Type", bound="IFeatureClassV2")

@attr.s(auto_attribs=True)
class IFeatureClassV2(DataContract):
    attributes: List[IFeatureAttributeV2] = None
    features: List[IFeatureV2] = None
    id: str = None
    srid: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IFeatureClassV2Type, src_dict: Dict[str, Any]) -> IFeatureClassV2Type:
        obj = IFeatureClassV2()
        obj.load_dict(src_dict)
        return obj

CatalogIdQueryConditionV2Type = TypeVar("CatalogIdQueryConditionV2Type", bound="CatalogIdQueryConditionV2")

@attr.s(auto_attribs=True)
class CatalogIdQueryConditionV2(QueryConditionV2):
    catalogId: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CatalogIdQueryConditionV2Type, src_dict: Dict[str, Any]) -> CatalogIdQueryConditionV2Type:
        obj = CatalogIdQueryConditionV2()
        obj.load_dict(src_dict)
        return obj

class GisGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("gis"), **kwargs)

    def GetAuthorities(self, projectid) -> Response:
        """Gets list of unique authorities of all coordinate systems

        CoordinateSystem
        GET /api/crs/coordinate-system/authority
        """
        return self.GetRequest("/api/crs/coordinate-system/authority", None, api_version="2", projectid=projectid)

    def GetAllCoordinateSystems(self, projectid, nametext=None, fulltext=None, authority=None) -> Response:
        """Gets list of coordinate systems with optional filters

        CoordinateSystem
        GET /api/crs/coordinate-system/list
        """
        queryparams = self.GetQueryParams(nametext=nametext, fulltext=fulltext, authority=authority)
        return self.GetRequest("/api/crs/coordinate-system/list", queryparams, api_version="2", projectid=projectid)

    def GetCoordinateSystem(self, projectid, id) -> Response:
        """Gets coordinate system by spatial reference id

        CoordinateSystem
        GET /api/crs/coordinate-system/{id}
        """
        return self.GetRequest(f"/api/crs/coordinate-system/{id}", None, api_version="2", projectid=projectid, datasetid=id)

    def GetProjectedGeometries(self, projectid, body) -> Response:
        """Returns geometries projected to a selected coordinate system

        CoordinateSystem
        POST /api/crs/project
        """
        return self.PostRequest("/api/crs/project", body, None, api_version="2", projectid=projectid)

    def GetFeatureClassAsFeatureCollection(self, projectid, id, outputsrid=None) -> Response:
        """Gets a feature class as feature collection

        FeatureClass
        GET /api/gis/dataset/{id}
        """
        queryparams = self.GetQueryParams(outputSRID=outputsrid)
        return self.GetRequest(f"/api/gis/dataset/{id}", queryparams, api_version="2", projectid=projectid, datasetid=id)

    def AddAttribute(self, projectid, body, id) -> Response:
        """Add attribute to feature class

        FeatureClass
        PATCH /api/gis/dataset/{id}/add-attribute
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/add-attribute", body, None, api_version="2", projectid=projectid, datasetid=id)

    def AddFeatures(self, projectid, body, id) -> Response:
        """Adds features

        FeatureClass
        PATCH /api/gis/dataset/{id}/add-features
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/add-features", body, None, api_version="2", projectid=projectid, datasetid=id)

    def DeleteAttribute(self, projectid, body, id) -> Response:
        """Delete attribute from feature class

        FeatureClass
        PATCH /api/gis/dataset/{id}/delete-attribute
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/delete-attribute", body, None, api_version="2", projectid=projectid, datasetid=id)

    def DeleteFeatures(self, projectid, body, id) -> Response:
        """Deletes a features

        FeatureClass
        PATCH /api/gis/dataset/{id}/delete-features
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/delete-features", body, None, api_version="2", projectid=projectid, datasetid=id)

    def GetFeatureClassExtent(self, projectid, id, outputsrid=None) -> Response:
        """Gets feature class extent

        FeatureClass
        GET /api/gis/dataset/{id}/extent
        """
        queryparams = self.GetQueryParams(outputSRID=outputsrid)
        return self.GetRequest(f"/api/gis/dataset/{id}/extent", queryparams, api_version="2", projectid=projectid, datasetid=id)

    def AddFeatureV2(self, projectid, body, id) -> Response:
        """Creates a new feature

        Feature
        POST /api/gis/dataset/{id}/feature
        """
        return self.PostRequest(f"/api/gis/dataset/{id}/feature", body, None, api_version="2", projectid=projectid, datasetid=id)

    def UpdateFeatureV2(self, projectid, body, id) -> Response:
        """Updates a feature

        Feature
        PUT /api/gis/dataset/{id}/feature
        """
        return self.PutRequest(f"/api/gis/dataset/{id}/feature", body, None, api_version="2", projectid=projectid, datasetid=id)

    def DeleteFeatureV2(self, projectid, id, featureid) -> Response:
        """Deletes a feature

        Feature
        DELETE /api/gis/dataset/{id}/feature/{featureId}
        """
        return self.DeleteRequest(f"/api/gis/dataset/{id}/feature/{featureid}", None, api_version="2", projectid=projectid, datasetid=id)

    def UpdateFeatureAttributesV2(self, projectid, body, id, featureid) -> Response:
        """Updates a feature attributes

        Feature
        PATCH /api/gis/dataset/{id}/feature/{featureId}
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/feature/{featureid}", body, None, api_version="2", projectid=projectid, datasetid=id)

    def GetFeatureV2(self, projectid, id, featureid) -> Response:
        """Gets a feature

        Feature
        GET /api/gis/dataset/{id}/feature/{featureId}
        """
        return self.GetRequest(f"/api/gis/dataset/{id}/feature/{featureid}", None, api_version="2", projectid=projectid, datasetid=id)

    def QueryFeatureClass(self, projectid, body, id) -> Response:
        """Gets results of a query on a feature class as feature collection

        FeatureClass
        POST /api/gis/dataset/{id}/query
        """
        return self.PostRequest(f"/api/gis/dataset/{id}/query", body, None, api_version="2", projectid=projectid, datasetid=id)

    def UpdateFeatures(self, projectid, body, id) -> Response:
        """Updates a features

        FeatureClass
        PATCH /api/gis/dataset/{id}/update-features
        """
        return self.PatchRequest(f"/api/gis/dataset/{id}/update-features", body, None, api_version="2", projectid=projectid, datasetid=id)
