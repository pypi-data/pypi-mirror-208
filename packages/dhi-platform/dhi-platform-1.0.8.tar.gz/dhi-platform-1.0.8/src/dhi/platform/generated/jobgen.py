# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "job" "--classname" "JobGenClientV" "-r" "projectid" "--out" "C:\Users\fikr\Source\Repos\mike-platform-sdk-py\src\dhi\platform\generated/jobgen.py" "https://develop.mike-cloud.com/job/v3"
# 2023-03-28 18:45:34.512512Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://develop.mike-cloud.com/job/v3
# job - Version 3
# 
# 3

ClusterOutputV1Type = TypeVar("ClusterOutputV1Type", bound="ClusterOutputV1")

@attr.s(auto_attribs=True)
class ClusterOutputV1(DataContract):
    properties: str = None
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
    def from_dict(cls: ClusterOutputV1Type, src_dict: Dict[str, Any]) -> ClusterOutputV1Type:
        obj = ClusterOutputV1()
        obj.load_dict(src_dict)
        return obj

ContainerInfoOutputV1Type = TypeVar("ContainerInfoOutputV1Type", bound="ContainerInfoOutputV1")

@attr.s(auto_attribs=True)
class ContainerInfoOutputV1(DataContract):
    image: str = None
    command: List[str] = None
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
    def from_dict(cls: ContainerInfoOutputV1Type, src_dict: Dict[str, Any]) -> ContainerInfoOutputV1Type:
        obj = ContainerInfoOutputV1()
        obj.load_dict(src_dict)
        return obj

CronJobOutputV1Type = TypeVar("CronJobOutputV1Type", bound="CronJobOutputV1")

@attr.s(auto_attribs=True)
class CronJobOutputV1(DataContract):
    cronJobId: str = None
    projectId: str = None
    schedule: str = None
    relatedJobIds: List[str] = None
    containerInfos: List[ContainerInfoOutputV1] = None
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
    def from_dict(cls: CronJobOutputV1Type, src_dict: Dict[str, Any]) -> CronJobOutputV1Type:
        obj = CronJobOutputV1()
        obj.load_dict(src_dict)
        return obj

CronJobOutputCollectionResponseV1Type = TypeVar("CronJobOutputCollectionResponseV1Type", bound="CronJobOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class CronJobOutputCollectionResponseV1(DataContract):
    data: List[CronJobOutputV1] = None
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
    def from_dict(cls: CronJobOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> CronJobOutputCollectionResponseV1Type:
        obj = CronJobOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

SecretLinkV1Type = TypeVar("SecretLinkV1Type", bound="SecretLinkV1")

@attr.s(auto_attribs=True)
class SecretLinkV1(DataContract):
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
    def from_dict(cls: SecretLinkV1Type, src_dict: Dict[str, Any]) -> SecretLinkV1Type:
        obj = SecretLinkV1()
        obj.load_dict(src_dict)
        return obj

JobLogOutputV1Type = TypeVar("JobLogOutputV1Type", bound="JobLogOutputV1")

@attr.s(auto_attribs=True)
class JobLogOutputV1(DataContract):
    containerName: str = None
    log: str = None
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
    def from_dict(cls: JobLogOutputV1Type, src_dict: Dict[str, Any]) -> JobLogOutputV1Type:
        obj = JobLogOutputV1()
        obj.load_dict(src_dict)
        return obj

InputLocationSpecV1Type = TypeVar("InputLocationSpecV1Type", bound="InputLocationSpecV1")

@attr.s(auto_attribs=True)
class InputLocationSpecV1(DataContract):
    localPath: str = None
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
    def from_dict(cls: InputLocationSpecV1Type, src_dict: Dict[str, Any]) -> InputLocationSpecV1Type:
        obj = InputLocationSpecV1()
        obj.load_dict(src_dict)
        return obj

InputDataSpecV1Type = TypeVar("InputDataSpecV1Type", bound="InputDataSpecV1")

@attr.s(auto_attribs=True)
class InputDataSpecV1(DataContract):
    locations: List[InputLocationSpecV1] = None
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
    def from_dict(cls: InputDataSpecV1Type, src_dict: Dict[str, Any]) -> InputDataSpecV1Type:
        obj = InputDataSpecV1()
        obj.load_dict(src_dict)
        return obj

EnvironmentVariableSecretV1Type = TypeVar("EnvironmentVariableSecretV1Type", bound="EnvironmentVariableSecretV1")

@attr.s(auto_attribs=True)
class EnvironmentVariableSecretV1(SecretLinkV1):
    environmentVariableName: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretLinkV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: EnvironmentVariableSecretV1Type, src_dict: Dict[str, Any]) -> EnvironmentVariableSecretV1Type:
        obj = EnvironmentVariableSecretV1()
        obj.load_dict(src_dict)
        return obj

ClusterOutputCollectionResponseV1Type = TypeVar("ClusterOutputCollectionResponseV1Type", bound="ClusterOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class ClusterOutputCollectionResponseV1(DataContract):
    data: List[ClusterOutputV1] = None
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
    def from_dict(cls: ClusterOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> ClusterOutputCollectionResponseV1Type:
        obj = ClusterOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

OutputLocationSpecV1Type = TypeVar("OutputLocationSpecV1Type", bound="OutputLocationSpecV1")

@attr.s(auto_attribs=True)
class OutputLocationSpecV1(DataContract):
    localPath: str = None
    uploadContainerLogs: str = None
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
    def from_dict(cls: OutputLocationSpecV1Type, src_dict: Dict[str, Any]) -> OutputLocationSpecV1Type:
        obj = OutputLocationSpecV1()
        obj.load_dict(src_dict)
        return obj

OutputDataSpecV1Type = TypeVar("OutputDataSpecV1Type", bound="OutputDataSpecV1")

@attr.s(auto_attribs=True)
class OutputDataSpecV1(DataContract):
    locations: List[OutputLocationSpecV1] = None
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
    def from_dict(cls: OutputDataSpecV1Type, src_dict: Dict[str, Any]) -> OutputDataSpecV1Type:
        obj = OutputDataSpecV1()
        obj.load_dict(src_dict)
        return obj

ReportingChannelSpecV1Type = TypeVar("ReportingChannelSpecV1Type", bound="ReportingChannelSpecV1")

@attr.s(auto_attribs=True)
class ReportingChannelSpecV1(DataContract):
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
    def from_dict(cls: ReportingChannelSpecV1Type, src_dict: Dict[str, Any]) -> ReportingChannelSpecV1Type:
        obj = ReportingChannelSpecV1()
        obj.load_dict(src_dict)
        return obj

FileReportingChannelV1Type = TypeVar("FileReportingChannelV1Type", bound="FileReportingChannelV1")

@attr.s(auto_attribs=True)
class FileReportingChannelV1(ReportingChannelSpecV1):
    filePath: str = None
    format: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ReportingChannelSpecV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FileReportingChannelV1Type, src_dict: Dict[str, Any]) -> FileReportingChannelV1Type:
        obj = FileReportingChannelV1()
        obj.load_dict(src_dict)
        return obj

PlatformOutputLocationV1Type = TypeVar("PlatformOutputLocationV1Type", bound="PlatformOutputLocationV1")

@attr.s(auto_attribs=True)
class PlatformOutputLocationV1(OutputLocationSpecV1):
    relativePlatformPath: str = None
    type: str = "PlatformOutputLocation"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = OutputLocationSpecV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PlatformOutputLocationV1Type, src_dict: Dict[str, Any]) -> PlatformOutputLocationV1Type:
        obj = PlatformOutputLocationV1()
        obj.load_dict(src_dict)
        return obj

PlatformInputLocationV1Type = TypeVar("PlatformInputLocationV1Type", bound="PlatformInputLocationV1")

@attr.s(auto_attribs=True)
class PlatformInputLocationV1(InputLocationSpecV1):
    projectId: str = None
    excludedFiles: List[str] = None
    type: str = "PlatformInputLocation"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = InputLocationSpecV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PlatformInputLocationV1Type, src_dict: Dict[str, Any]) -> PlatformInputLocationV1Type:
        obj = PlatformInputLocationV1()
        obj.load_dict(src_dict)
        return obj

RuntimeSpecV1Type = TypeVar("RuntimeSpecV1Type", bound="RuntimeSpecV1")

@attr.s(auto_attribs=True)
class RuntimeSpecV1(DataContract):
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
    def from_dict(cls: RuntimeSpecV1Type, src_dict: Dict[str, Any]) -> RuntimeSpecV1Type:
        obj = RuntimeSpecV1()
        obj.load_dict(src_dict)
        return obj

SecretRefV1Type = TypeVar("SecretRefV1Type", bound="SecretRefV1")

@attr.s(auto_attribs=True)
class SecretRefV1(DataContract):
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
    def from_dict(cls: SecretRefV1Type, src_dict: Dict[str, Any]) -> SecretRefV1Type:
        obj = SecretRefV1()
        obj.load_dict(src_dict)
        return obj

SecretSpecV1Type = TypeVar("SecretSpecV1Type", bound="SecretSpecV1")

@attr.s(auto_attribs=True)
class SecretSpecV1(DataContract):
    secretSource: SecretRefV1 = None
    secretLink: SecretLinkV1 = None
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
    def from_dict(cls: SecretSpecV1Type, src_dict: Dict[str, Any]) -> SecretSpecV1Type:
        obj = SecretSpecV1()
        obj.load_dict(src_dict)
        return obj

AdHocInternalSecretV1Type = TypeVar("AdHocInternalSecretV1Type", bound="AdHocInternalSecretV1")

@attr.s(auto_attribs=True)
class AdHocInternalSecretV1(SecretRefV1):
    item: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretRefV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AdHocInternalSecretV1Type, src_dict: Dict[str, Any]) -> AdHocInternalSecretV1Type:
        obj = AdHocInternalSecretV1()
        obj.load_dict(src_dict)
        return obj

JobLogsOutputV1Type = TypeVar("JobLogsOutputV1Type", bound="JobLogsOutputV1")

@attr.s(auto_attribs=True)
class JobLogsOutputV1(DataContract):
    jobId: str = None
    logs: List[JobLogOutputV1] = None
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
    def from_dict(cls: JobLogsOutputV1Type, src_dict: Dict[str, Any]) -> JobLogsOutputV1Type:
        obj = JobLogsOutputV1()
        obj.load_dict(src_dict)
        return obj

class JobStateTypeV1(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    FINISHED = "Finished"
    def __str__(self) -> str:
        return str(self.value)

AdHocSecretV1Type = TypeVar("AdHocSecretV1Type", bound="AdHocSecretV1")

@attr.s(auto_attribs=True)
class AdHocSecretV1(SecretRefV1):
    sourceKey: str = None
    backendType: str = None
    sourceName: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretRefV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AdHocSecretV1Type, src_dict: Dict[str, Any]) -> AdHocSecretV1Type:
        obj = AdHocSecretV1()
        obj.load_dict(src_dict)
        return obj

ExistingSecretV1Type = TypeVar("ExistingSecretV1Type", bound="ExistingSecretV1")

@attr.s(auto_attribs=True)
class ExistingSecretV1(SecretRefV1):
    secretName: str = None
    item: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretRefV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ExistingSecretV1Type, src_dict: Dict[str, Any]) -> ExistingSecretV1Type:
        obj = ExistingSecretV1()
        obj.load_dict(src_dict)
        return obj

JobOutputV1Type = TypeVar("JobOutputV1Type", bound="JobOutputV1")

@attr.s(auto_attribs=True)
class JobOutputV1(DataContract):
    jobId: str = None
    projectId: str = None
    jobState: JobStateTypeV1 = None
    hasError: bool = False
    statusMessage: str = None
    containerInfos: List[str] = None
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
    def from_dict(cls: JobOutputV1Type, src_dict: Dict[str, Any]) -> JobOutputV1Type:
        obj = JobOutputV1()
        obj.load_dict(src_dict)
        return obj

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

HttpValidationProblemDetailsV1Type = TypeVar("HttpValidationProblemDetailsV1Type", bound="HttpValidationProblemDetailsV1")

@attr.s(auto_attribs=True)
class HttpValidationProblemDetailsV1(ProblemDetailsV1):
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
    def from_dict(cls: HttpValidationProblemDetailsV1Type, src_dict: Dict[str, Any]) -> HttpValidationProblemDetailsV1Type:
        obj = HttpValidationProblemDetailsV1()
        obj.load_dict(src_dict)
        return obj

AdHocExternalSecretV1Type = TypeVar("AdHocExternalSecretV1Type", bound="AdHocExternalSecretV1")

@attr.s(auto_attribs=True)
class AdHocExternalSecretV1(SecretRefV1):
    sourceKey: str = None
    backendType: str = None
    sourceName: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretRefV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AdHocExternalSecretV1Type, src_dict: Dict[str, Any]) -> AdHocExternalSecretV1Type:
        obj = AdHocExternalSecretV1()
        obj.load_dict(src_dict)
        return obj

ContainerInputV1Type = TypeVar("ContainerInputV1Type", bound="ContainerInputV1")

@attr.s(auto_attribs=True)
class ContainerInputV1(DataContract):
    image: str = None
    command: List[str] = None
    cpuCores: float = None
    memoryMB: int = None
    secrets: List[SecretSpecV1] = None
    environmentVariables: str = None
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
    def from_dict(cls: ContainerInputV1Type, src_dict: Dict[str, Any]) -> ContainerInputV1Type:
        obj = ContainerInputV1()
        obj.load_dict(src_dict)
        return obj

ProgressReportingSpecV1Type = TypeVar("ProgressReportingSpecV1Type", bound="ProgressReportingSpecV1")

@attr.s(auto_attribs=True)
class ProgressReportingSpecV1(DataContract):
    channels: List[ReportingChannelSpecV1] = None
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
    def from_dict(cls: ProgressReportingSpecV1Type, src_dict: Dict[str, Any]) -> ProgressReportingSpecV1Type:
        obj = ProgressReportingSpecV1()
        obj.load_dict(src_dict)
        return obj

JobDefinitionInputV1Type = TypeVar("JobDefinitionInputV1Type", bound="JobDefinitionInputV1")

@attr.s(auto_attribs=True)
class JobDefinitionInputV1(DataContract):
    runtime: RuntimeSpecV1 = None
    inputData: InputDataSpecV1 = None
    outputData: OutputDataSpecV1 = None
    progressReporting: ProgressReportingSpecV1 = None
    retryLimit: int = None
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
    def from_dict(cls: JobDefinitionInputV1Type, src_dict: Dict[str, Any]) -> JobDefinitionInputV1Type:
        obj = JobDefinitionInputV1()
        obj.load_dict(src_dict)
        return obj

CronJobDefinitionInputV1Type = TypeVar("CronJobDefinitionInputV1Type", bound="CronJobDefinitionInputV1")

@attr.s(auto_attribs=True)
class CronJobDefinitionInputV1(JobDefinitionInputV1):
    schedule: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = JobDefinitionInputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CronJobDefinitionInputV1Type, src_dict: Dict[str, Any]) -> CronJobDefinitionInputV1Type:
        obj = CronJobDefinitionInputV1()
        obj.load_dict(src_dict)
        return obj

StorageRequestSpecV1Type = TypeVar("StorageRequestSpecV1Type", bound="StorageRequestSpecV1")

@attr.s(auto_attribs=True)
class StorageRequestSpecV1(DataContract):
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
    def from_dict(cls: StorageRequestSpecV1Type, src_dict: Dict[str, Any]) -> StorageRequestSpecV1Type:
        obj = StorageRequestSpecV1()
        obj.load_dict(src_dict)
        return obj

LocalStorageRequestSpecV1Type = TypeVar("LocalStorageRequestSpecV1Type", bound="LocalStorageRequestSpecV1")

@attr.s(auto_attribs=True)
class LocalStorageRequestSpecV1(StorageRequestSpecV1):
    storageSizeGB: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = StorageRequestSpecV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: LocalStorageRequestSpecV1Type, src_dict: Dict[str, Any]) -> LocalStorageRequestSpecV1Type:
        obj = LocalStorageRequestSpecV1()
        obj.load_dict(src_dict)
        return obj

FileSecretV1Type = TypeVar("FileSecretV1Type", bound="FileSecretV1")

@attr.s(auto_attribs=True)
class FileSecretV1(SecretLinkV1):
    fileName: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SecretLinkV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FileSecretV1Type, src_dict: Dict[str, Any]) -> FileSecretV1Type:
        obj = FileSecretV1()
        obj.load_dict(src_dict)
        return obj

ContainerRuntimeSpecV1Type = TypeVar("ContainerRuntimeSpecV1Type", bound="ContainerRuntimeSpecV1")

@attr.s(auto_attribs=True)
class ContainerRuntimeSpecV1(RuntimeSpecV1):
    containers: List[ContainerInputV1] = None
    requiredLabels: List[str] = None
    toleratedTaints: List[str] = None
    runInCallerNamespace: bool = False
    storageRequest: StorageRequestSpecV1 = None
    type: str = "ContainerRuntimeSpec"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = RuntimeSpecV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ContainerRuntimeSpecV1Type, src_dict: Dict[str, Any]) -> ContainerRuntimeSpecV1Type:
        obj = ContainerRuntimeSpecV1()
        obj.load_dict(src_dict)
        return obj

class JobGenClientV1(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("job"), **kwargs)

    def GetClusters(self, projectid) -> Response:
        """Cluster

        GET /api/process/cluster/list
        """
        return self.GetRequest("/api/process/cluster/list", None, api_version="3", projectid=projectid)

    def CreateCronJob(self, projectid, body) -> Response:
        """CronJob

        POST /api/process/cronjob
        """
        return self.PostRequest("/api/process/cronjob", body, None, api_version="3", projectid=projectid)

    def GetCronJob(self, projectid, id) -> Response:
        """CronJob

        GET /api/process/cronjob/{id}
        """
        return self.GetRequest(f"/api/process/cronjob/{id}", None, api_version="3", projectid=projectid)

    def RemoveCronJob(self, projectid, id) -> Response:
        """CronJob

        DELETE /api/process/cronjob/{id}
        """
        return self.DeleteRequest(f"/api/process/cronjob/{id}", None, api_version="3", projectid=projectid)

    def ExecuteJob(self, projectid, body) -> Response:
        """Job

        POST /api/process/job
        """
        return self.PostRequest("/api/process/job", body, None, api_version="3", projectid=projectid)

    def GetJob(self, projectid, id) -> Response:
        """Job

        GET /api/process/job/{id}
        """
        return self.GetRequest(f"/api/process/job/{id}", None, api_version="3", projectid=projectid)

    def CancelJob(self, projectid, id) -> Response:
        """Job

        PUT /api/process/job/{id}/cancel
        """
        return self.PutRequest(f"/api/process/job/{id}/cancel", None, None, api_version="3", projectid=projectid)

    def GetJobLogs(self, projectid, id, taillines=None) -> Response:
        """Job

        GET /api/process/job/{id}/log
        """
        queryparams = self.GetQueryParams(tailLines=taillines)
        return self.GetRequest(f"/api/process/job/{id}/log", queryparams, api_version="3", projectid=projectid)

    def GetCronJobList(self, projectid) -> Response:
        """CronJobList

        GET /api/process/project/{projectId}/cronjob/list
        """
        return self.GetRequest(f"/api/process/project/{projectid}/cronjob/list", None, api_version="3", projectid=projectid)
