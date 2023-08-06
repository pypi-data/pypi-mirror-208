# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "tiles" "--classname" "TilesGenClientV" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\tilesgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/tiles/v1"
# 2022-01-13 19:04:40.570778Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/tiles/v1
# DHI Tiles API - Version 1
# API for getting raster map tiles
# 1

class TilingSchemeTypeV1(str, Enum):
    WMTS = "WMTS"
    XYZ = "XYZ"
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

class RenderOutOfRangeTransparentV1(str, Enum):
    NONE = "None"
    ABOVE = "Above"
    BELOW = "Below"
    ABOVEANDBELOW = "AboveAndBelow"
    def __str__(self) -> str:
        return str(self.value)

class TilingAggregationMethodV1(str, Enum):
    MEAN = "Mean"
    MAX = "Max"
    def __str__(self) -> str:
        return str(self.value)

ItemToBandMappingV1Type = TypeVar("ItemToBandMappingV1Type", bound="ItemToBandMappingV1")

@attr.s(auto_attribs=True)
class ItemToBandMappingV1(DataContract):
    itemName: str = None
    minValue: float = None
    maxValue: float = None
    bandIndex: int = None
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
    def from_dict(cls: ItemToBandMappingV1Type, src_dict: Dict[str, Any]) -> ItemToBandMappingV1Type:
        obj = ItemToBandMappingV1()
        obj.load_dict(src_dict)
        return obj

class ETilingOutputTypeV1(str, Enum):
    RAWDATA = "RawData"
    BINNEDDATA256 = "BinnedData256"
    PNG = "PNG"
    WEBP = "WEBP"
    def __str__(self) -> str:
        return str(self.value)

TilingSchemeV1Type = TypeVar("TilingSchemeV1Type", bound="TilingSchemeV1")

@attr.s(auto_attribs=True)
class TilingSchemeV1(DataContract):
    schemeType: TilingSchemeTypeV1 = None
    itemName: str = None
    itemBandMapping: List[ItemToBandMappingV1] = None
    schemeId: str = None
    outputType: ETilingOutputTypeV1 = None
    aggregationMethod: TilingAggregationMethodV1 = None
    tileWidth: int = None
    tileHeight: int = None
    zoomLevels: List[int] = None
    minValue: float = None
    maxValue: float = None
    renderValuesOutOfRangeAsTransparent: RenderOutOfRangeTransparentV1 = None
    colors: List[str] = None
    maxRasterWidth: int = None
    layerIdx: int = None
    compressionLevel: int = None
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
    def from_dict(cls: TilingSchemeV1Type, src_dict: Dict[str, Any]) -> TilingSchemeV1Type:
        obj = TilingSchemeV1()
        obj.load_dict(src_dict)
        return obj

GeneratedTilingSchemeV1Type = TypeVar("GeneratedTilingSchemeV1Type", bound="GeneratedTilingSchemeV1")

@attr.s(auto_attribs=True)
class GeneratedTilingSchemeV1(TilingSchemeV1):
    resolutions: List[float] = None
    scaleDenominators: List[float] = None
    matrixWidths: List[int] = None
    matrixHeights: List[int] = None
    srid: int = None
    sridAuthName: str = None
    hasLayers: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TilingSchemeV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: GeneratedTilingSchemeV1Type, src_dict: Dict[str, Any]) -> GeneratedTilingSchemeV1Type:
        obj = GeneratedTilingSchemeV1()
        obj.load_dict(src_dict)
        return obj

DatasetTilingMetadataV1Type = TypeVar("DatasetTilingMetadataV1Type", bound="DatasetTilingMetadataV1")

@attr.s(auto_attribs=True)
class DatasetTilingMetadataV1(DataContract):
    nativeExtent: str = None
    wgS84Extent: str = None
    tilingSchemes: List[GeneratedTilingSchemeV1] = None
    tileStorageSizeKB: int = None
    timeStamps: List[str] = None
    layerIds: List[int] = None
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
    def from_dict(cls: DatasetTilingMetadataV1Type, src_dict: Dict[str, Any]) -> DatasetTilingMetadataV1Type:
        obj = DatasetTilingMetadataV1()
        obj.load_dict(src_dict)
        return obj

class TilesGenClientV1(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("tiles"), **kwargs)

    def GetDatasetMetadata(self, projectid, id) -> Response:
        """Tile

        GET /api/tiles/dataset/{id}/metadata
        """
        return self.GetRequest(f"/api/tiles/dataset/{id}/metadata", None, api_version="1", projectid=projectid, datasetid=id)

    def GetEmptyTile(self, projectid, id, schemeid) -> Response:
        """Tile

        GET /api/tiles/dataset/{id}/scheme/{schemeId}/empty-tile
        """
        return self.GetRequest(f"/api/tiles/dataset/{id}/scheme/{schemeid}/empty-tile", None, api_version="1", projectid=projectid, datasetid=id)

    def GetTile(self, projectid, id, schemeid, tilematrix, tilerow, tilecol, layer=None, timestep=None) -> Response:
        """Tile

        GET /api/tiles/dataset/{id}/scheme/{schemeId}/{tileMatrix}/{tileRow}/{tileCol}
        """
        queryparams = self.GetQueryParams(layer=layer, timeStep=timestep)
        return self.GetRequest(f"/api/tiles/dataset/{id}/scheme/{schemeid}/{tilematrix}/{tilerow}/{tilecol}", queryparams, api_version="1", projectid=projectid, datasetid=id)

    def GetWmtsRequest(self, projectid, id, service=None, request=None) -> Response:
        """Tile

        GET /api/tiles/dataset/{id}/wmts
        """
        queryparams = self.GetQueryParams(service=service, request=request)
        return self.GetRequest(f"/api/tiles/dataset/{id}/wmts", queryparams, api_version="1", projectid=projectid, datasetid=id)

    def GetVectorTile(self, projectid, id, zoom, tilecol, tilerow) -> Response:
        """VectorTiles

        GET /api/vectortiles/dataset/{id}/{zoom}/{tileCol}/{tileRow}.vector.pbf
        """
        return self.GetRequest(f"/api/vectortiles/dataset/{id}/{zoom}/{tilecol}/{tilerow}.vector.pbf", None, api_version="1", projectid=projectid, datasetid=id)
