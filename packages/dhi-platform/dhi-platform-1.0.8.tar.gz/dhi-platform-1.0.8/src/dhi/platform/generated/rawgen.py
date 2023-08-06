# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "raw" "--classname" "RawGenClientV" "-n" "2" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\rawgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/raw/v2"
# 2022-01-13 19:04:07.997380Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/raw/v2
#  - Version 2
# 
# 2

GetFileChecksumOutputV2Type = TypeVar("GetFileChecksumOutputV2Type", bound="GetFileChecksumOutputV2")

@attr.s(auto_attribs=True)
class GetFileChecksumOutputV2(DataContract):
    id: str = None
    name: str = None
    checksum: str = None
    alg: str = None
    lastModified: str = None
    size: int = None
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
    def from_dict(cls: GetFileChecksumOutputV2Type, src_dict: Dict[str, Any]) -> GetFileChecksumOutputV2Type:
        obj = GetFileChecksumOutputV2()
        obj.load_dict(src_dict)
        return obj

UploadBulkFileInputV2Type = TypeVar("UploadBulkFileInputV2Type", bound="UploadBulkFileInputV2")

@attr.s(auto_attribs=True)
class UploadBulkFileInputV2(DataContract):
    id: str = None
    sasToken: str = None
    name: str = None
    url: str = None
    lastModified: str = None
    size: int = None
    forceCopy: str = None
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
    def from_dict(cls: UploadBulkFileInputV2Type, src_dict: Dict[str, Any]) -> UploadBulkFileInputV2Type:
        obj = UploadBulkFileInputV2()
        obj.load_dict(src_dict)
        return obj

GetCopyFileStatusInputV2Type = TypeVar("GetCopyFileStatusInputV2Type", bound="GetCopyFileStatusInputV2")

@attr.s(auto_attribs=True)
class GetCopyFileStatusInputV2(DataContract):
    id: str = None
    copyOperationId: str = None
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
    def from_dict(cls: GetCopyFileStatusInputV2Type, src_dict: Dict[str, Any]) -> GetCopyFileStatusInputV2Type:
        obj = GetCopyFileStatusInputV2()
        obj.load_dict(src_dict)
        return obj

GetCopyFilesStatusInputV2Type = TypeVar("GetCopyFilesStatusInputV2Type", bound="GetCopyFilesStatusInputV2")

@attr.s(auto_attribs=True)
class GetCopyFilesStatusInputV2(DataContract):
    datasets: List[GetCopyFileStatusInputV2] = None
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
    def from_dict(cls: GetCopyFilesStatusInputV2Type, src_dict: Dict[str, Any]) -> GetCopyFilesStatusInputV2Type:
        obj = GetCopyFilesStatusInputV2()
        obj.load_dict(src_dict)
        return obj

GetDownloadDatasetOutputV2Type = TypeVar("GetDownloadDatasetOutputV2Type", bound="GetDownloadDatasetOutputV2")

@attr.s(auto_attribs=True)
class GetDownloadDatasetOutputV2(DataContract):
    id: str = None
    name: str = None
    url: str = None
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
    def from_dict(cls: GetDownloadDatasetOutputV2Type, src_dict: Dict[str, Any]) -> GetDownloadDatasetOutputV2Type:
        obj = GetDownloadDatasetOutputV2()
        obj.load_dict(src_dict)
        return obj

GetDownloadDatasetOutputCollectionResponseV2Type = TypeVar("GetDownloadDatasetOutputCollectionResponseV2Type", bound="GetDownloadDatasetOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class GetDownloadDatasetOutputCollectionResponseV2(DataContract):
    data: List[GetDownloadDatasetOutputV2] = None
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
    def from_dict(cls: GetDownloadDatasetOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> GetDownloadDatasetOutputCollectionResponseV2Type:
        obj = GetDownloadDatasetOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

DownloadOutputV2Type = TypeVar("DownloadOutputV2Type", bound="DownloadOutputV2")

@attr.s(auto_attribs=True)
class DownloadOutputV2(DataContract):
    datasetName: str = None
    url: str = None
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
    def from_dict(cls: DownloadOutputV2Type, src_dict: Dict[str, Any]) -> DownloadOutputV2Type:
        obj = DownloadOutputV2()
        obj.load_dict(src_dict)
        return obj

MoveStagedFileInputV2Type = TypeVar("MoveStagedFileInputV2Type", bound="MoveStagedFileInputV2")

@attr.s(auto_attribs=True)
class MoveStagedFileInputV2(DataContract):
    stagedFileUrl: str = None
    datasetName: str = None
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
    def from_dict(cls: MoveStagedFileInputV2Type, src_dict: Dict[str, Any]) -> MoveStagedFileInputV2Type:
        obj = MoveStagedFileInputV2()
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

UploadBulkFilesInputV2Type = TypeVar("UploadBulkFilesInputV2Type", bound="UploadBulkFilesInputV2")

@attr.s(auto_attribs=True)
class UploadBulkFilesInputV2(DataContract):
    datasets: List[UploadBulkFileInputV2] = None
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
    def from_dict(cls: UploadBulkFilesInputV2Type, src_dict: Dict[str, Any]) -> UploadBulkFilesInputV2Type:
        obj = UploadBulkFilesInputV2()
        obj.load_dict(src_dict)
        return obj

GetFileChecksumOutputCollectionResponseV2Type = TypeVar("GetFileChecksumOutputCollectionResponseV2Type", bound="GetFileChecksumOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class GetFileChecksumOutputCollectionResponseV2(DataContract):
    data: List[GetFileChecksumOutputV2] = None
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
    def from_dict(cls: GetFileChecksumOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> GetFileChecksumOutputCollectionResponseV2Type:
        obj = GetFileChecksumOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

UploadOutputV2Type = TypeVar("UploadOutputV2Type", bound="UploadOutputV2")

@attr.s(auto_attribs=True)
class UploadOutputV2(DataContract):
    id: str = None
    url: str = None
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
    def from_dict(cls: UploadOutputV2Type, src_dict: Dict[str, Any]) -> UploadOutputV2Type:
        obj = UploadOutputV2()
        obj.load_dict(src_dict)
        return obj

IsStagingUrlInputV2Type = TypeVar("IsStagingUrlInputV2Type", bound="IsStagingUrlInputV2")

@attr.s(auto_attribs=True)
class IsStagingUrlInputV2(DataContract):
    url: str = None
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
    def from_dict(cls: IsStagingUrlInputV2Type, src_dict: Dict[str, Any]) -> IsStagingUrlInputV2Type:
        obj = IsStagingUrlInputV2()
        obj.load_dict(src_dict)
        return obj

CopyOperationOutputV2Type = TypeVar("CopyOperationOutputV2Type", bound="CopyOperationOutputV2")

@attr.s(auto_attribs=True)
class CopyOperationOutputV2(DataContract):
    id: str = None
    hasCompleted: str = None
    copiedBytes: int = None
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
    def from_dict(cls: CopyOperationOutputV2Type, src_dict: Dict[str, Any]) -> CopyOperationOutputV2Type:
        obj = CopyOperationOutputV2()
        obj.load_dict(src_dict)
        return obj

GetCopyFilesStatusOutputV2Type = TypeVar("GetCopyFilesStatusOutputV2Type", bound="GetCopyFilesStatusOutputV2")

@attr.s(auto_attribs=True)
class GetCopyFilesStatusOutputV2(DataContract):
    id: str = None
    name: str = None
    copyOperation: CopyOperationOutputV2 = None
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
    def from_dict(cls: GetCopyFilesStatusOutputV2Type, src_dict: Dict[str, Any]) -> GetCopyFilesStatusOutputV2Type:
        obj = GetCopyFilesStatusOutputV2()
        obj.load_dict(src_dict)
        return obj

GetCopyFilesStatusOutputCollectionResponseV2Type = TypeVar("GetCopyFilesStatusOutputCollectionResponseV2Type", bound="GetCopyFilesStatusOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class GetCopyFilesStatusOutputCollectionResponseV2(DataContract):
    data: List[GetCopyFilesStatusOutputV2] = None
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
    def from_dict(cls: GetCopyFilesStatusOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> GetCopyFilesStatusOutputCollectionResponseV2Type:
        obj = GetCopyFilesStatusOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

StagingUrlOutputV2Type = TypeVar("StagingUrlOutputV2Type", bound="StagingUrlOutputV2")

@attr.s(auto_attribs=True)
class StagingUrlOutputV2(DataContract):
    url: str = None
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
    def from_dict(cls: StagingUrlOutputV2Type, src_dict: Dict[str, Any]) -> StagingUrlOutputV2Type:
        obj = StagingUrlOutputV2()
        obj.load_dict(src_dict)
        return obj

StagingUrlOutputCollectionResponseV2Type = TypeVar("StagingUrlOutputCollectionResponseV2Type", bound="StagingUrlOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class StagingUrlOutputCollectionResponseV2(DataContract):
    data: List[StagingUrlOutputV2] = None
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
    def from_dict(cls: StagingUrlOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> StagingUrlOutputCollectionResponseV2Type:
        obj = StagingUrlOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

UploadBulkFileOutputV2Type = TypeVar("UploadBulkFileOutputV2Type", bound="UploadBulkFileOutputV2")

@attr.s(auto_attribs=True)
class UploadBulkFileOutputV2(DataContract):
    id: str = None
    name: str = None
    size: int = None
    copyOperation: CopyOperationOutputV2 = None
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
    def from_dict(cls: UploadBulkFileOutputV2Type, src_dict: Dict[str, Any]) -> UploadBulkFileOutputV2Type:
        obj = UploadBulkFileOutputV2()
        obj.load_dict(src_dict)
        return obj

UploadBulkFileOutputCollectionResponseV2Type = TypeVar("UploadBulkFileOutputCollectionResponseV2Type", bound="UploadBulkFileOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class UploadBulkFileOutputCollectionResponseV2(DataContract):
    data: List[UploadBulkFileOutputV2] = None
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
    def from_dict(cls: UploadBulkFileOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> UploadBulkFileOutputCollectionResponseV2Type:
        obj = UploadBulkFileOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

StringResponseV2Type = TypeVar("StringResponseV2Type", bound="StringResponseV2")

@attr.s(auto_attribs=True)
class StringResponseV2(DataContract):
    data: str = None
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
    def from_dict(cls: StringResponseV2Type, src_dict: Dict[str, Any]) -> StringResponseV2Type:
        obj = StringResponseV2()
        obj.load_dict(src_dict)
        return obj

IsStagingUrlOutputV2Type = TypeVar("IsStagingUrlOutputV2Type", bound="IsStagingUrlOutputV2")

@attr.s(auto_attribs=True)
class IsStagingUrlOutputV2(DataContract):
    result: str = None
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
    def from_dict(cls: IsStagingUrlOutputV2Type, src_dict: Dict[str, Any]) -> IsStagingUrlOutputV2Type:
        obj = IsStagingUrlOutputV2()
        obj.load_dict(src_dict)
        return obj

GetDatasetBlockChecksumOutputV2Type = TypeVar("GetDatasetBlockChecksumOutputV2Type", bound="GetDatasetBlockChecksumOutputV2")

@attr.s(auto_attribs=True)
class GetDatasetBlockChecksumOutputV2(DataContract):
    checksum: str = None
    size: int = None
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
    def from_dict(cls: GetDatasetBlockChecksumOutputV2Type, src_dict: Dict[str, Any]) -> GetDatasetBlockChecksumOutputV2Type:
        obj = GetDatasetBlockChecksumOutputV2()
        obj.load_dict(src_dict)
        return obj

GetDatasetBlocksChecksumsOutputV2Type = TypeVar("GetDatasetBlocksChecksumsOutputV2Type", bound="GetDatasetBlocksChecksumsOutputV2")

@attr.s(auto_attribs=True)
class GetDatasetBlocksChecksumsOutputV2(DataContract):
    datasetId: str = None
    blocks: List[GetDatasetBlockChecksumOutputV2] = None
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
    def from_dict(cls: GetDatasetBlocksChecksumsOutputV2Type, src_dict: Dict[str, Any]) -> GetDatasetBlocksChecksumsOutputV2Type:
        obj = GetDatasetBlocksChecksumsOutputV2()
        obj.load_dict(src_dict)
        return obj

class RawGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("raw"), **kwargs)

    def GetFilesChecksums(self, projectid, id=None) -> Response:
        """Get checksums for selected or all files in a folder.

        FileSync
        GET /api/filesync/checksums
        """
        queryparams = self.GetQueryParams(id=id)
        return self.GetRequest("/api/filesync/checksums", queryparams, api_version="2", projectid=projectid)

    def GetDownloadDatasets(self, projectid, id=None) -> Response:
        """Get download info for selected or all files in a folder.

        FileSync
        GET /api/filesync/prepare-download
        """
        queryparams = self.GetQueryParams(id=id)
        return self.GetRequest("/api/filesync/prepare-download", queryparams, api_version="2", projectid=projectid)

    def UploadBulkFiles(self, projectid, body) -> Response:
        """Upload file datasets from the staging area or another storage.
        Files in the staging area moved, all other files are copied.
        Check the copy operations with "POST /api/filesync/upload/status".

        FileSync
        PUT /api/filesync/upload
        """
        return self.PutRequest("/api/filesync/upload", body, None, api_version="2", projectid=projectid)

    def GetCopyFilesStatus(self, projectid, body) -> Response:
        """Get upload copy operations status, copy operations started in "PUT /api/filesync/upload".

        FileSync
        POST /api/filesync/upload/status
        """
        return self.PostRequest("/api/filesync/upload/status", body, None, api_version="2", projectid=projectid)

    def GetDatasetBlocksChecksums(self, projectid, id) -> Response:
        """Get file blocks with checksums.

        FileSync
        GET /api/filesync/{id}/blocks
        """
        return self.GetRequest(f"/api/filesync/{id}/blocks", None, api_version="2", projectid=projectid, datasetid=id)

    def GetFileSasUrlV2(self, projectid, id, downloadfilename=None) -> Response:
        """Prepare download of data for dataset. When you call this service directly you need to provide a SAS token
        for the given dataset with read privilege to download data for a dataset.

        Raw
        GET /api/raw/dataset/{id}
        """
        queryparams = self.GetQueryParams(downloadFileName=downloadfilename)
        return self.GetRequest(f"/api/raw/dataset/{id}", queryparams, api_version="2", projectid=projectid, datasetid=id)

    def MoveStagedFileToDataset(self, projectid, body) -> Response:
        """Move data from staging storage to dataset.

        Staging
        POST /api/raw/move-staged-url
        """
        return self.PostRequest("/api/raw/move-staged-url", body, None, api_version="2", projectid=projectid)

    def GetDatasetDownloadUrl(self, projectid, datasetid, downloadfilename=None) -> Response:
        """Prepare download of data for dataset.

        Dataset
        GET /api/raw/prepare-download/{datasetId}
        """
        queryparams = self.GetQueryParams(downloadFileName=downloadfilename)
        return self.GetRequest(f"/api/raw/prepare-download/{datasetid}", queryparams, api_version="2", projectid=projectid)

    def GetDatasetUploadUrl(self, projectid, datasetname) -> Response:
        """Prepare upload of data for dataset.

        Dataset
        GET /api/raw/prepare-upload/{datasetName}
        """
        return self.GetRequest(f"/api/raw/prepare-upload/{datasetname}", None, api_version="2", projectid=projectid)

    def GetStagingUrlV2(self, projectid) -> Response:
        """Prepare staging blob storage for data upload.

        Staging
        GET /api/raw/staging-url
        """
        return self.GetRequest("/api/raw/staging-url", None, api_version="2", projectid=projectid)

    def IsStagingUrlV2(self, projectid, body) -> Response:
        """Check if given url is a staging url

        Staging
        POST /api/raw/staging-url
        """
        return self.PostRequest("/api/raw/staging-url", body, None, api_version="2", projectid=projectid)

    def GetStagingUrls(self, projectid, count) -> Response:
        """Prepare staging blob storages for data upload.

        Staging
        GET /api/raw/staging-urls
        """
        queryparams = self.GetQueryParams(count=count)
        return self.GetRequest("/api/raw/staging-urls", queryparams, api_version="2", projectid=projectid)
