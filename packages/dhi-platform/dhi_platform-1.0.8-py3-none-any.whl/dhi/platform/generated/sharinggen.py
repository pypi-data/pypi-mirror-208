# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "sharing" "--classname" "SharingGenClientV" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\sharinggen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/sharing/v1"
# 2022-01-13 19:04:23.671606Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/sharing/v1
# DHI Sharing API - Version 1
# API for managing data publications and subscriptions
# 1

class CatalogTypeV1(str, Enum):
    INTRATENANT = "IntraTenant"
    PUBLIC = "Public"
    def __str__(self) -> str:
        return str(self.value)

class DatasetTypeV1(str, Enum):
    FILE = "file"
    MULTIDIMENSIONAL = "multidimensional"
    TIMESERIES = "timeseries"
    GISVECTORDATA = "gisvectordata"
    TILES = "tiles"
    def __str__(self) -> str:
        return str(self.value)

CreateCatalogOutputV1Type = TypeVar("CreateCatalogOutputV1Type", bound="CreateCatalogOutputV1")

@attr.s(auto_attribs=True)
class CreateCatalogOutputV1(DataContract):
    catalogId: str = None
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
    def from_dict(cls: CreateCatalogOutputV1Type, src_dict: Dict[str, Any]) -> CreateCatalogOutputV1Type:
        obj = CreateCatalogOutputV1()
        obj.load_dict(src_dict)
        return obj

class ComparisonOperatorV1(str, Enum):
    EQUAL = "Equal"
    NOTEQUAL = "NotEqual"
    GREATERTHAN = "GreaterThan"
    LESSTHAN = "LessThan"
    GREATERTHANOREQUAL = "GreaterThanOrEqual"
    LESSTHANOREQUAL = "LessThanOrEqual"
    def __str__(self) -> str:
        return str(self.value)

class SortOrderV1(str, Enum):
    ASC = "Asc"
    DESC = "Desc"
    def __str__(self) -> str:
        return str(self.value)

CreatePublicationOutputV1Type = TypeVar("CreatePublicationOutputV1Type", bound="CreatePublicationOutputV1")

@attr.s(auto_attribs=True)
class CreatePublicationOutputV1(DataContract):
    publicationId: str = None
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
    def from_dict(cls: CreatePublicationOutputV1Type, src_dict: Dict[str, Any]) -> CreatePublicationOutputV1Type:
        obj = CreatePublicationOutputV1()
        obj.load_dict(src_dict)
        return obj

EditPublicationInputV1Type = TypeVar("EditPublicationInputV1Type", bound="EditPublicationInputV1")

@attr.s(auto_attribs=True)
class EditPublicationInputV1(DataContract):
    id: str = None
    name: str = None
    description: str = None
    discoverable: str = None
    location: str = None
    resourceId: str = None
    metadata: str = None
    properties: str = None
    rowVersion: str = None
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
    def from_dict(cls: EditPublicationInputV1Type, src_dict: Dict[str, Any]) -> EditPublicationInputV1Type:
        obj = EditPublicationInputV1()
        obj.load_dict(src_dict)
        return obj

CatalogOutputV1Type = TypeVar("CatalogOutputV1Type", bound="CatalogOutputV1")

@attr.s(auto_attribs=True)
class CatalogOutputV1(DataContract):
    id: str = None
    name: str = None
    catalogType: CatalogTypeV1 = None
    createdBy: str = None
    createdAt: str = None
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
    def from_dict(cls: CatalogOutputV1Type, src_dict: Dict[str, Any]) -> CatalogOutputV1Type:
        obj = CatalogOutputV1()
        obj.load_dict(src_dict)
        return obj

CatalogOutputCursorResponseV1Type = TypeVar("CatalogOutputCursorResponseV1Type", bound="CatalogOutputCursorResponseV1")

@attr.s(auto_attribs=True)
class CatalogOutputCursorResponseV1(DataContract):
    cursor: str = None
    data: List[CatalogOutputV1] = None
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
    def from_dict(cls: CatalogOutputCursorResponseV1Type, src_dict: Dict[str, Any]) -> CatalogOutputCursorResponseV1Type:
        obj = CatalogOutputCursorResponseV1()
        obj.load_dict(src_dict)
        return obj

class SpatialOperatorV1(str, Enum):
    INTERSECTS = "Intersects"
    WITHIN = "Within"
    def __str__(self) -> str:
        return str(self.value)

ProblemDetailsV1Type = TypeVar("ProblemDetailsV1Type", bound="ProblemDetailsV1")

@attr.s(auto_attribs=True)
class ProblemDetailsV1(DataContract):
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
    def from_dict(cls: ProblemDetailsV1Type, src_dict: Dict[str, Any]) -> ProblemDetailsV1Type:
        obj = ProblemDetailsV1()
        obj.load_dict(src_dict)
        return obj

ValidationProblemDetailsV1Type = TypeVar("ValidationProblemDetailsV1Type", bound="ValidationProblemDetailsV1")

@attr.s(auto_attribs=True)
class ValidationProblemDetailsV1(ProblemDetailsV1):
    errors: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ProblemDetailsV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ValidationProblemDetailsV1Type, src_dict: Dict[str, Any]) -> ValidationProblemDetailsV1Type:
        obj = ValidationProblemDetailsV1()
        obj.load_dict(src_dict)
        return obj

class AttributeOperatorV1(str, Enum):
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

CreateSubscriptionOutputV1Type = TypeVar("CreateSubscriptionOutputV1Type", bound="CreateSubscriptionOutputV1")

@attr.s(auto_attribs=True)
class CreateSubscriptionOutputV1(DataContract):
    subscriptionId: str = None
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
    def from_dict(cls: CreateSubscriptionOutputV1Type, src_dict: Dict[str, Any]) -> CreateSubscriptionOutputV1Type:
        obj = CreateSubscriptionOutputV1()
        obj.load_dict(src_dict)
        return obj

CreateCatalogInputV1Type = TypeVar("CreateCatalogInputV1Type", bound="CreateCatalogInputV1")

@attr.s(auto_attribs=True)
class CreateCatalogInputV1(DataContract):
    name: str = None
    catalogType: CatalogTypeV1 = None
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
    def from_dict(cls: CreateCatalogInputV1Type, src_dict: Dict[str, Any]) -> CreateCatalogInputV1Type:
        obj = CreateCatalogInputV1()
        obj.load_dict(src_dict)
        return obj

class ResourceTypeV1(str, Enum):
    DATASET = "Dataset"
    FOLDER = "Folder"
    def __str__(self) -> str:
        return str(self.value)

ResourceDetailOutputV1Type = TypeVar("ResourceDetailOutputV1Type", bound="ResourceDetailOutputV1")

@attr.s(auto_attribs=True)
class ResourceDetailOutputV1(DataContract):
    customerId: str = None
    resourceId: str = None
    resourceType: ResourceTypeV1 = None
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
    def from_dict(cls: ResourceDetailOutputV1Type, src_dict: Dict[str, Any]) -> ResourceDetailOutputV1Type:
        obj = ResourceDetailOutputV1()
        obj.load_dict(src_dict)
        return obj

CreateSubscriptionInputV1Type = TypeVar("CreateSubscriptionInputV1Type", bound="CreateSubscriptionInputV1")

@attr.s(auto_attribs=True)
class CreateSubscriptionInputV1(DataContract):
    reference: str = None
    publicationId: str = None
    endDate: str = None
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
    def from_dict(cls: CreateSubscriptionInputV1Type, src_dict: Dict[str, Any]) -> CreateSubscriptionInputV1Type:
        obj = CreateSubscriptionInputV1()
        obj.load_dict(src_dict)
        return obj

class CatalogSortColumnV1(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

class SearchSortColumnV1(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

class PublicationSortColumnV1(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

QueryConditionV1Type = TypeVar("QueryConditionV1Type", bound="QueryConditionV1")

@attr.s(auto_attribs=True)
class QueryConditionV1(DataContract):
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
    def from_dict(cls: QueryConditionV1Type, src_dict: Dict[str, Any]) -> QueryConditionV1Type:
        obj = QueryConditionV1()
        obj.load_dict(src_dict)
        return obj

FullTextQueryConditionV1Type = TypeVar("FullTextQueryConditionV1Type", bound="FullTextQueryConditionV1")

@attr.s(auto_attribs=True)
class FullTextQueryConditionV1(QueryConditionV1):
    searchString: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FullTextQueryConditionV1Type, src_dict: Dict[str, Any]) -> FullTextQueryConditionV1Type:
        obj = FullTextQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

DatasetTypeQueryConditionV1Type = TypeVar("DatasetTypeQueryConditionV1Type", bound="DatasetTypeQueryConditionV1")

@attr.s(auto_attribs=True)
class DatasetTypeQueryConditionV1(QueryConditionV1):
    datasetType: DatasetTypeV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DatasetTypeQueryConditionV1Type, src_dict: Dict[str, Any]) -> DatasetTypeQueryConditionV1Type:
        obj = DatasetTypeQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

SpatialQueryConditionV1Type = TypeVar("SpatialQueryConditionV1Type", bound="SpatialQueryConditionV1")

@attr.s(auto_attribs=True)
class SpatialQueryConditionV1(QueryConditionV1):
    geometry: str = None
    operator: SpatialOperatorV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SpatialQueryConditionV1Type, src_dict: Dict[str, Any]) -> SpatialQueryConditionV1Type:
        obj = SpatialQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

CreatedAtQueryConditionV1Type = TypeVar("CreatedAtQueryConditionV1Type", bound="CreatedAtQueryConditionV1")

@attr.s(auto_attribs=True)
class CreatedAtQueryConditionV1(QueryConditionV1):
    createdAt: str = None
    operator: ComparisonOperatorV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CreatedAtQueryConditionV1Type, src_dict: Dict[str, Any]) -> CreatedAtQueryConditionV1Type:
        obj = CreatedAtQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

IdsQueryConditionV1Type = TypeVar("IdsQueryConditionV1Type", bound="IdsQueryConditionV1")

@attr.s(auto_attribs=True)
class IdsQueryConditionV1(QueryConditionV1):
    ids: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IdsQueryConditionV1Type, src_dict: Dict[str, Any]) -> IdsQueryConditionV1Type:
        obj = IdsQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

CatalogIdQueryConditionV1Type = TypeVar("CatalogIdQueryConditionV1Type", bound="CatalogIdQueryConditionV1")

@attr.s(auto_attribs=True)
class CatalogIdQueryConditionV1(QueryConditionV1):
    catalogId: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CatalogIdQueryConditionV1Type, src_dict: Dict[str, Any]) -> CatalogIdQueryConditionV1Type:
        obj = CatalogIdQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

SearchInputV1Type = TypeVar("SearchInputV1Type", bound="SearchInputV1")

@attr.s(auto_attribs=True)
class SearchInputV1(DataContract):
    query: List[QueryConditionV1] = None
    sortBy: SearchSortColumnV1 = None
    sortOrder: SortOrderV1 = None
    cursor: str = None
    limit: int = None
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
    def from_dict(cls: SearchInputV1Type, src_dict: Dict[str, Any]) -> SearchInputV1Type:
        obj = SearchInputV1()
        obj.load_dict(src_dict)
        return obj

class SubscriptionModeV1(str, Enum):
    OPEN = "Open"
    ONAPPROVAL = "OnApproval"
    def __str__(self) -> str:
        return str(self.value)

PublicationOutputV1Type = TypeVar("PublicationOutputV1Type", bound="PublicationOutputV1")

@attr.s(auto_attribs=True)
class PublicationOutputV1(DataContract):
    id: str = None
    catalogId: str = None
    name: str = None
    description: str = None
    location: str = None
    metadata: str = None
    properties: str = None
    resourceId: str = None
    resourceType: ResourceTypeV1 = None
    discoverable: str = None
    subscriptionMode: SubscriptionModeV1 = None
    publishedUntil: str = None
    createdBy: str = None
    createdAt: str = None
    rowVersion: str = None
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
    def from_dict(cls: PublicationOutputV1Type, src_dict: Dict[str, Any]) -> PublicationOutputV1Type:
        obj = PublicationOutputV1()
        obj.load_dict(src_dict)
        return obj

PublicationOutputCursorResponseV1Type = TypeVar("PublicationOutputCursorResponseV1Type", bound="PublicationOutputCursorResponseV1")

@attr.s(auto_attribs=True)
class PublicationOutputCursorResponseV1(DataContract):
    cursor: str = None
    data: List[PublicationOutputV1] = None
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
    def from_dict(cls: PublicationOutputCursorResponseV1Type, src_dict: Dict[str, Any]) -> PublicationOutputCursorResponseV1Type:
        obj = PublicationOutputCursorResponseV1()
        obj.load_dict(src_dict)
        return obj

CreatePublicationInputV1Type = TypeVar("CreatePublicationInputV1Type", bound="CreatePublicationInputV1")

@attr.s(auto_attribs=True)
class CreatePublicationInputV1(DataContract):
    name: str = None
    description: str = None
    location: str = None
    metadata: str = None
    properties: str = None
    resourceId: str = None
    catalogId: str = None
    resourceType: ResourceTypeV1 = None
    discoverable: str = None
    subscriptionMode: SubscriptionModeV1 = None
    publishedUntil: str = None
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
    def from_dict(cls: CreatePublicationInputV1Type, src_dict: Dict[str, Any]) -> CreatePublicationInputV1Type:
        obj = CreatePublicationInputV1()
        obj.load_dict(src_dict)
        return obj

class SubscriptionStateV1(str, Enum):
    APPROVALPENDING = "ApprovalPending"
    APPROVED = "Approved"
    REVOKED = "Revoked"
    def __str__(self) -> str:
        return str(self.value)

SubscriptionOutputV1Type = TypeVar("SubscriptionOutputV1Type", bound="SubscriptionOutputV1")

@attr.s(auto_attribs=True)
class SubscriptionOutputV1(DataContract):
    id: str = None
    reference: str = None
    publicationId: str = None
    publicationName: str = None
    endDate: str = None
    subscriptionState: SubscriptionStateV1 = None
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
    def from_dict(cls: SubscriptionOutputV1Type, src_dict: Dict[str, Any]) -> SubscriptionOutputV1Type:
        obj = SubscriptionOutputV1()
        obj.load_dict(src_dict)
        return obj

SubscriptionOutputCursorResponseV1Type = TypeVar("SubscriptionOutputCursorResponseV1Type", bound="SubscriptionOutputCursorResponseV1")

@attr.s(auto_attribs=True)
class SubscriptionOutputCursorResponseV1(DataContract):
    cursor: str = None
    data: List[SubscriptionOutputV1] = None
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
    def from_dict(cls: SubscriptionOutputCursorResponseV1Type, src_dict: Dict[str, Any]) -> SubscriptionOutputCursorResponseV1Type:
        obj = SubscriptionOutputCursorResponseV1()
        obj.load_dict(src_dict)
        return obj

AttributeQueryConditionV1Type = TypeVar("AttributeQueryConditionV1Type", bound="AttributeQueryConditionV1")

@attr.s(auto_attribs=True)
class AttributeQueryConditionV1(QueryConditionV1):
    name: str = None
    operator: AttributeOperatorV1 = None
    value: None = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = QueryConditionV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AttributeQueryConditionV1Type, src_dict: Dict[str, Any]) -> AttributeQueryConditionV1Type:
        obj = AttributeQueryConditionV1()
        obj.load_dict(src_dict)
        return obj

SearchOutputV1Type = TypeVar("SearchOutputV1Type", bound="SearchOutputV1")

@attr.s(auto_attribs=True)
class SearchOutputV1(DataContract):
    id: str = None
    name: str = None
    location: str = None
    resourceId: str = None
    resourceType: ResourceTypeV1 = None
    catalogId: str = None
    catalogName: str = None
    subscriptionMode: SubscriptionModeV1 = None
    publishedUntil: str = None
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
    def from_dict(cls: SearchOutputV1Type, src_dict: Dict[str, Any]) -> SearchOutputV1Type:
        obj = SearchOutputV1()
        obj.load_dict(src_dict)
        return obj

SearchOutputCursorResponseV1Type = TypeVar("SearchOutputCursorResponseV1Type", bound="SearchOutputCursorResponseV1")

@attr.s(auto_attribs=True)
class SearchOutputCursorResponseV1(DataContract):
    cursor: str = None
    data: List[SearchOutputV1] = None
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
    def from_dict(cls: SearchOutputCursorResponseV1Type, src_dict: Dict[str, Any]) -> SearchOutputCursorResponseV1Type:
        obj = SearchOutputCursorResponseV1()
        obj.load_dict(src_dict)
        return obj

class SubscriptionSortColumnV1(str, Enum):
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

class SharingGenClientV1(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("sharing"), **kwargs)

    def CreateCatalog(self, projectid, body) -> Response:
        """Catalog

        POST /api/sharing/catalog
        """
        return self.PostRequest("/api/sharing/catalog", body, None, api_version="1", projectid=projectid)

    def GetCatalogList(self, projectid, sortby=None, sortorder=None, cursor=None, limit=None) -> Response:
        """Catalog

        GET /api/sharing/catalog/list
        """
        queryparams = self.GetQueryParams(SortBy=sortby, SortOrder=sortorder, Cursor=cursor, Limit=limit)
        return self.GetRequest("/api/sharing/catalog/list", queryparams, api_version="1", projectid=projectid)

    def CreatePublication(self, projectid, body) -> Response:
        """Publication

        POST /api/sharing/publication
        """
        resource_id = body.get('resourceId', None)
        return self.PostRequest("/api/sharing/publication", body, None, api_version="1", projectid=projectid, datasetid=resource_id)

    def UpdatePublication(self, projectid, body) -> Response:
        """Publication

        PUT /api/sharing/publication
        """
        resource_id = body.get('resourceId', None)
        return self.PutRequest("/api/sharing/publication", body, None, api_version="1", projectid=projectid, datasetid=resource_id)

    def GetPublicationList(self, projectid, resourceid=None, catalogid=None, sortby=None, sortorder=None, cursor=None, limit=None) -> Response:
        """Publication

        GET /api/sharing/publication/list
        """
        queryparams = self.GetQueryParams(ResourceId=resourceid, CatalogId=catalogid, SortBy=sortby, SortOrder=sortorder, Cursor=cursor, Limit=limit)
        return self.GetRequest("/api/sharing/publication/list", queryparams, api_version="1", projectid=projectid)

    def DeletePublication(self, projectid, id, resourceid) -> Response:
        """Publication

        DELETE /api/sharing/publication/{id}
        """
        return self.DeleteRequest(f"/api/sharing/publication/{id}", None, api_version="1", projectid=projectid, datasetid=resourceid)

    def GetPublication(self, projectid, id) -> Response:
        """Publication

        GET /api/sharing/publication/{id}
        """
        return self.GetRequest(f"/api/sharing/publication/{id}", None, api_version="1", projectid=projectid)

    def GetPublicationSubscriptionList(self, projectid, id, sortby=None, sortorder=None, cursor=None, limit=None) -> Response:
        """Publication

        GET /api/sharing/publication/{id}/subscription/list
        """
        queryparams = self.GetQueryParams(SortBy=sortby, SortOrder=sortorder, Cursor=cursor, Limit=limit)
        return self.GetRequest(f"/api/sharing/publication/{id}/subscription/list", queryparams, api_version="1", projectid=projectid)

    def GetResourceDetail(self, projectid, subscriptionid) -> Response:
        """Publication

        GET /api/sharing/publication/{subscriptionId}/resourcedetail
        """
        return self.GetRequest(f"/api/sharing/publication/{subscriptionid}/resourcedetail", None, api_version="1", projectid=projectid)

    def Search(self, projectid, body) -> Response:
        """Search

        POST /api/sharing/search
        """
        return self.PostRequest("/api/sharing/search", body, None, api_version="1", projectid=projectid)

    def CreateSubscription(self, projectid, body) -> Response:
        """Subscription

        POST /api/sharing/subscription
        """
        return self.PostRequest("/api/sharing/subscription", body, None, api_version="1", projectid=projectid)

    def GetSubscriptionList(self, projectid, cursor=None, limit=None) -> Response:
        """Subscription

        GET /api/sharing/subscription/list
        """
        queryparams = self.GetQueryParams(Cursor=cursor, Limit=limit)
        return self.GetRequest("/api/sharing/subscription/list", queryparams, api_version="1", projectid=projectid)
