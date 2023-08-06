# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "engine" "--classname" "EngineGenClientV" "-n" "2" "-r" "projectid" "-p" "GetAllConfigurations:projectid,GetAllEngines:projectid,GetEngine:projectid,GetMyExecutions:projectid" "-f" "RunExecutionWithPlatformData:recursivetoken:true" "-a" "GetAllConfigurations,GetAllEngines,GetEngine" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\enginegen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/engine/v2"
# 2023-02-21 10:07:18.820338Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/engine/v2
# engine - Version 2
# API for executing modelling engines
# 2

GetConfigurationOutputV2Type = TypeVar("GetConfigurationOutputV2Type", bound="GetConfigurationOutputV2")

@attr.s(auto_attribs=True)
class GetConfigurationOutputV2(DataContract):
    """Characteristics of a pool type supported by engine/tool execution

    """
    poolType: str = None
    virtualMachineSize: str = None
    nodeLimit: int = None
    gpuCount: int = None
    numberOfCores: int = None
    memoryInMB: int = None
    resourceDiskSizeInMB: int = None
    description: str = None
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
    def from_dict(cls: GetConfigurationOutputV2Type, src_dict: Dict[str, Any]) -> GetConfigurationOutputV2Type:
        obj = GetConfigurationOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineDefinitionV2Type = TypeVar("EngineDefinitionV2Type", bound="EngineDefinitionV2")

@attr.s(auto_attribs=True)
class EngineDefinitionV2(DataContract):
    name: str = None
    version: str = None
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
    def from_dict(cls: EngineDefinitionV2Type, src_dict: Dict[str, Any]) -> EngineDefinitionV2Type:
        obj = EngineDefinitionV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionPeekParametersV2Type = TypeVar("EngineExecutionPeekParametersV2Type", bound="EngineExecutionPeekParametersV2")

@attr.s(auto_attribs=True)
class EngineExecutionPeekParametersV2(DataContract):
    """Describes the parameters used for peeking an execution

    """
    peekFileLocalPaths: List[str] = None
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
    def from_dict(cls: EngineExecutionPeekParametersV2Type, src_dict: Dict[str, Any]) -> EngineExecutionPeekParametersV2Type:
        obj = EngineExecutionPeekParametersV2()
        obj.load_dict(src_dict)
        return obj

GetConfigurationOutputCollectionResponseV2Type = TypeVar("GetConfigurationOutputCollectionResponseV2Type", bound="GetConfigurationOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class GetConfigurationOutputCollectionResponseV2(DataContract):
    data: List[GetConfigurationOutputV2] = None
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
    def from_dict(cls: GetConfigurationOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> GetConfigurationOutputCollectionResponseV2Type:
        obj = GetConfigurationOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

EngineRunOutputV2Type = TypeVar("EngineRunOutputV2Type", bound="EngineRunOutputV2")

@attr.s(auto_attribs=True)
class EngineRunOutputV2(DataContract):
    """Describes the output when starting a new execution

    """
    executionId: str = None
    outputLocation: str = None
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
    def from_dict(cls: EngineRunOutputV2Type, src_dict: Dict[str, Any]) -> EngineRunOutputV2Type:
        obj = EngineRunOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineRunParameterV2Type = TypeVar("EngineRunParameterV2Type", bound="EngineRunParameterV2")

@attr.s(auto_attribs=True)
class EngineRunParameterV2(DataContract):
    """Optional, engine/tool-specific parameter, that can be used when starting on execution

    """
    name: str = None
    value: str = None
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
    def from_dict(cls: EngineRunParameterV2Type, src_dict: Dict[str, Any]) -> EngineRunParameterV2Type:
        obj = EngineRunParameterV2()
        obj.load_dict(src_dict)
        return obj

EngineModelItemV2Type = TypeVar("EngineModelItemV2Type", bound="EngineModelItemV2")

@attr.s(auto_attribs=True)
class EngineModelItemV2(DataContract):
    """Describes an execution input from the MIKE Cloud Platform

    """
    subprojectId: str = None
    modelFileName: str = None
    engine: str = None
    version: str = None
    resultsRelativePath: str = None
    overwriteResultsIfExists: str = None
    runParameters: List[EngineRunParameterV2] = None
    reportLogUpdatesLines: int = None
    logFiles: List[str] = None
    terminateOnNoProgressForSec: int = None
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
    def from_dict(cls: EngineModelItemV2Type, src_dict: Dict[str, Any]) -> EngineModelItemV2Type:
        obj = EngineModelItemV2()
        obj.load_dict(src_dict)
        return obj

class SortOrderV2(str, Enum):
    ASC = "Asc"
    DESC = "Desc"
    def __str__(self) -> str:
        return str(self.value)

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

HttpValidationProblemDetailsV2Type = TypeVar("HttpValidationProblemDetailsV2Type", bound="HttpValidationProblemDetailsV2")

@attr.s(auto_attribs=True)
class HttpValidationProblemDetailsV2(ProblemDetailsV2):
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
    def from_dict(cls: HttpValidationProblemDetailsV2Type, src_dict: Dict[str, Any]) -> HttpValidationProblemDetailsV2Type:
        obj = HttpValidationProblemDetailsV2()
        obj.load_dict(src_dict)
        return obj

EngineGetOutputV2Type = TypeVar("EngineGetOutputV2Type", bound="EngineGetOutputV2")

@attr.s(auto_attribs=True)
class EngineGetOutputV2(DataContract):
    """Describes the details related to a supported engine/tool

    """
    name: str = None
    description: str = None
    allowedRunParameters: List[str] = None
    versions: List[str] = None
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
    def from_dict(cls: EngineGetOutputV2Type, src_dict: Dict[str, Any]) -> EngineGetOutputV2Type:
        obj = EngineGetOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineGetOutputCollectionResponseV2Type = TypeVar("EngineGetOutputCollectionResponseV2Type", bound="EngineGetOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class EngineGetOutputCollectionResponseV2(DataContract):
    data: List[EngineGetOutputV2] = None
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
    def from_dict(cls: EngineGetOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> EngineGetOutputCollectionResponseV2Type:
        obj = EngineGetOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionDiagnosticsOutputV2Type = TypeVar("EngineExecutionDiagnosticsOutputV2Type", bound="EngineExecutionDiagnosticsOutputV2")

@attr.s(auto_attribs=True)
class EngineExecutionDiagnosticsOutputV2(DataContract):
    """Describes the execution diagnostics

    """
    executionId: str = None
    diagnosticsLocation: str = None
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
    def from_dict(cls: EngineExecutionDiagnosticsOutputV2Type, src_dict: Dict[str, Any]) -> EngineExecutionDiagnosticsOutputV2Type:
        obj = EngineExecutionDiagnosticsOutputV2()
        obj.load_dict(src_dict)
        return obj

OptionsV2Type = TypeVar("OptionsV2Type", bound="OptionsV2")

@attr.s(auto_attribs=True)
class OptionsV2(DataContract):
    """Setup of the hardware configuration used for the execution

    """
    poolType: str = None
    nodeCount: int = None
    maxExecutionElapsedTimeHours: float = None
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
    def from_dict(cls: OptionsV2Type, src_dict: Dict[str, Any]) -> OptionsV2Type:
        obj = OptionsV2()
        obj.load_dict(src_dict)
        return obj

EngineOutputItemV2Type = TypeVar("EngineOutputItemV2Type", bound="EngineOutputItemV2")

@attr.s(auto_attribs=True)
class EngineOutputItemV2(DataContract):
    """Describes the location in a blob storage where the result files for the execution are stored

    """
    uri: str = None
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
    def from_dict(cls: EngineOutputItemV2Type, src_dict: Dict[str, Any]) -> EngineOutputItemV2Type:
        obj = EngineOutputItemV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionInputParametersV2Type = TypeVar("EngineExecutionInputParametersV2Type", bound="EngineExecutionInputParametersV2")

@attr.s(auto_attribs=True)
class EngineExecutionInputParametersV2(DataContract):
    """Describes the parameters of an execution that uses the MIKE Cloud Platform

    """
    models: List[EngineModelItemV2] = None
    output: EngineOutputItemV2 = None
    options: OptionsV2 = None
    scenarioName: str = None
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
    def from_dict(cls: EngineExecutionInputParametersV2Type, src_dict: Dict[str, Any]) -> EngineExecutionInputParametersV2Type:
        obj = EngineExecutionInputParametersV2()
        obj.load_dict(src_dict)
        return obj

EngineOutputPlatformItemV2Type = TypeVar("EngineOutputPlatformItemV2Type", bound="EngineOutputPlatformItemV2")

@attr.s(auto_attribs=True)
class EngineOutputPlatformItemV2(DataContract):
    """Describes the location in the MIKE Platform Cloud where the result files for an execution associated with a setup file are stored

    """
    modelFileName: str = None
    resultsRelativePath: str = None
    overwriteResultsIfExists: str = None
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
    def from_dict(cls: EngineOutputPlatformItemV2Type, src_dict: Dict[str, Any]) -> EngineOutputPlatformItemV2Type:
        obj = EngineOutputPlatformItemV2()
        obj.load_dict(src_dict)
        return obj

class EngineExecutionStatusV2(str, Enum):
    PENDING = "Pending"
    SETTINGUPCOMPUTERESOURCES = "SettingUpComputeResources"
    EVALUATINGINPUTSIZE = "EvaluatingInputSize"
    DOWNLOADINGINPUTFILES = "DownloadingInputFiles"
    INPROGRESS = "InProgress"
    UPLOADINGRESULTS = "UploadingResults"
    SUCCESS = "Success"
    FAILURE = "Failure"
    CANCELLING = "Cancelling"
    CANCELLED = "Cancelled"
    DELETING = "Deleting"
    def __str__(self) -> str:
        return str(self.value)

EngineExecutionOutputV2Type = TypeVar("EngineExecutionOutputV2Type", bound="EngineExecutionOutputV2")

@attr.s(auto_attribs=True)
class EngineExecutionOutputV2(DataContract):
    """Describes the details related to an execution

    """
    executionId: str = None
    outputLocation: str = None
    status: EngineExecutionStatusV2 = None
    message: str = None
    projectId: str = None
    customerId: str = None
    createdAt: str = None
    startedAt: str = None
    updatedAt: str = None
    finishedAt: str = None
    engines: List[EngineDefinitionV2] = None
    poolType: str = None
    virtualMachineSize: str = None
    nodeCount: int = None
    runningSetupIndex: int = None
    runningSetupProgress: str = None
    totalNumberOfSetups: int = None
    maxRunLimitTimeHours: float = None
    scenarioName: str = None
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
    def from_dict(cls: EngineExecutionOutputV2Type, src_dict: Dict[str, Any]) -> EngineExecutionOutputV2Type:
        obj = EngineExecutionOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineInputItemV2Type = TypeVar("EngineInputItemV2Type", bound="EngineInputItemV2")

@attr.s(auto_attribs=True)
class EngineInputItemV2(DataContract):
    """Describes an execution input from a blob storage

    """
    uri: str = None
    localPath: str = None
    engine: str = None
    version: str = None
    runParameters: List[EngineRunParameterV2] = None
    reportLogUpdatesLines: int = None
    logFiles: List[str] = None
    terminateOnNoProgressForSec: int = None
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
    def from_dict(cls: EngineInputItemV2Type, src_dict: Dict[str, Any]) -> EngineInputItemV2Type:
        obj = EngineInputItemV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionParametersV2Type = TypeVar("EngineExecutionParametersV2Type", bound="EngineExecutionParametersV2")

@attr.s(auto_attribs=True)
class EngineExecutionParametersV2(DataContract):
    """Describes the parameters used for running an execution with inputs from blob storage

    """
    inputs: List[EngineInputItemV2] = None
    output: EngineOutputItemV2 = None
    platformOutput: List[EngineOutputPlatformItemV2] = None
    options: OptionsV2 = None
    scenarioName: str = None
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
    def from_dict(cls: EngineExecutionParametersV2Type, src_dict: Dict[str, Any]) -> EngineExecutionParametersV2Type:
        obj = EngineExecutionParametersV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionInputOutputV2Type = TypeVar("EngineExecutionInputOutputV2Type", bound="EngineExecutionInputOutputV2")

@attr.s(auto_attribs=True)
class EngineExecutionInputOutputV2(DataContract):
    platformInputs: EngineExecutionInputParametersV2 = None
    inputs: EngineExecutionParametersV2 = None
    isPlatformData: str = None
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
    def from_dict(cls: EngineExecutionInputOutputV2Type, src_dict: Dict[str, Any]) -> EngineExecutionInputOutputV2Type:
        obj = EngineExecutionInputOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionSummaryOutputV2Type = TypeVar("EngineExecutionSummaryOutputV2Type", bound="EngineExecutionSummaryOutputV2")

@attr.s(auto_attribs=True)
class EngineExecutionSummaryOutputV2(DataContract):
    """Describes the details shown for an existing execution

    """
    executionId: str = None
    status: EngineExecutionStatusV2 = None
    projectId: str = None
    customerId: str = None
    createdAt: str = None
    startedAt: str = None
    updatedAt: str = None
    finishedAt: str = None
    engines: List[EngineDefinitionV2] = None
    poolType: str = None
    virtualMachineSize: str = None
    nodeCount: int = None
    runningSetupIndex: int = None
    runningSetupProgress: str = None
    totalNumberOfSetups: int = None
    outputLocation: str = None
    maxRunLimitTimeHours: float = None
    scenarioName: str = None
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
    def from_dict(cls: EngineExecutionSummaryOutputV2Type, src_dict: Dict[str, Any]) -> EngineExecutionSummaryOutputV2Type:
        obj = EngineExecutionSummaryOutputV2()
        obj.load_dict(src_dict)
        return obj

EngineExecutionSummaryOutputPagedResultV2Type = TypeVar("EngineExecutionSummaryOutputPagedResultV2Type", bound="EngineExecutionSummaryOutputPagedResultV2")

@attr.s(auto_attribs=True)
class EngineExecutionSummaryOutputPagedResultV2(DataContract):
    _nextLink: str = None
    cursor: str = None
    data: List[EngineExecutionSummaryOutputV2] = None
    __renamed = { "@nextLink": "_nextLink" }
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
    def from_dict(cls: EngineExecutionSummaryOutputPagedResultV2Type, src_dict: Dict[str, Any]) -> EngineExecutionSummaryOutputPagedResultV2Type:
        obj = EngineExecutionSummaryOutputPagedResultV2()
        obj.load_dict(src_dict)
        return obj

class EngineExecutionFieldV2(str, Enum):
    EXECUTIONID = "ExecutionId"
    STATUS = "Status"
    PROJECTID = "ProjectId"
    CREATEDAT = "CreatedAt"
    STARTEDAT = "StartedAt"
    UPDATEDAT = "UpdatedAt"
    FINISHEDAT = "FinishedAt"
    ENGINENAME = "EngineName"
    POOLTYPE = "PoolType"
    NODECOUNT = "NodeCount"
    TOTALNUMBEROFSETUPS = "TotalNumberOfSetups"
    SCENARIONAME = "ScenarioName"
    def __str__(self) -> str:
        return str(self.value)

class EngineGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("engine"), **kwargs)

    def GetAllConfigurations(self) -> Response:
        """Get the list of hardware configurations.

        Configuration
        GET /api/compute/configuration/list
        """
        return self.GetRequest("/api/compute/configuration/list", None, api_version="2", noauthentication=True)

    def GetAllEngines(self) -> Response:
        """Get the list of registered engines/tools.

        Engine
        GET /api/compute/engine/list
        """
        return self.GetRequest("/api/compute/engine/list", None, api_version="2", noauthentication=True)

    def GetEngine(self, name) -> Response:
        """Get the engine/tool information.

        Engine
        GET /api/compute/engine/{name}
        """
        return self.GetRequest(f"/api/compute/engine/{name}", None, api_version="2", noauthentication=True)

    def RunExecution(self, projectid, body) -> Response:
        """Run the engine/tool with input data from any blob storage. Create permission on the project is required.

        Execution
        POST /api/compute/execution
        """
        return self.PostRequest("/api/compute/execution", body, None, api_version="2", projectid=projectid)

    def GetExecutions(self, projectid, starttime=None, endtime=None, cursor=None) -> Response:
        """Get information about executions within a project. Read permission on the project is required.

        Execution
        GET /api/compute/execution/list
        """
        queryparams = self.GetQueryParams(startTime=starttime, endTime=endtime, cursor=cursor)
        return self.GetRequest("/api/compute/execution/list", queryparams, api_version="2", projectid=projectid)

    def GetMyExecutions(self, sortby=None, sortorder=None, starttime=None, endtime=None, scenarioname=None, status=None, project=None, limit=None, cursor=None) -> Response:
        """Get information about executions run by the user.

        Execution
        GET /api/compute/execution/my-list
        """
        queryparams = self.GetQueryParams(sortBy=sortby, sortOrder=sortorder, startTime=starttime, endTime=endtime, scenarioName=scenarioname, status=status, project=project, limit=limit, cursor=cursor)
        return self.GetRequest("/api/compute/execution/my-list", queryparams, api_version="2")

    def RunExecutionWithPlatformData(self, projectid, body) -> Response:
        """Run the engine/tool with input data from MIKE Cloud Platform. Create permission on the project is required.

        Execution
        POST /api/compute/execution/platform
        """
        return self.PostRequest("/api/compute/execution/platform", body, None, api_version="2", projectid=projectid, recursivetoken="true")

    def GetExecution(self, projectid, executionid) -> Response:
        """Get the execution information. Read permission on the project is required.

        Execution
        GET /api/compute/execution/{executionId}
        """
        return self.GetRequest(f"/api/compute/execution/{executionid}", None, api_version="2", projectid=projectid)

    def DeleteExecution(self, projectid, executionid) -> Response:
        """Delete the engine/tool execution. It can delete finished (also failed) and running executions. Delete permission on the project is required.

        Execution
        DELETE /api/compute/execution/{executionId}
        """
        return self.DeleteRequest(f"/api/compute/execution/{executionid}", None, api_version="2", projectid=projectid)

    def CancelExecution(self, projectid, executionid) -> Response:
        """Cancel the engine/tool execution. Create permission on the project is required.

        Execution
        PUT /api/compute/execution/{executionId}/cancel
        """
        return self.PutRequest(f"/api/compute/execution/{executionid}/cancel", None, None, api_version="2", projectid=projectid)

    def GetExecutionDiagnostics(self, projectid, executionid) -> Response:
        """Get the diagnostics collected during the execution. Read permission on the project is required.

        Execution
        GET /api/compute/execution/{executionId}/diagnostics
        """
        return self.GetRequest(f"/api/compute/execution/{executionid}/diagnostics", None, api_version="2", projectid=projectid)

    def GetExecutionInputs(self, projectid, executionid) -> Response:
        """Get the inputs used for starting the execution. Read permission on the project is required.

        Execution
        GET /api/compute/execution/{executionId}/input
        """
        return self.GetRequest(f"/api/compute/execution/{executionid}/input", None, api_version="2", projectid=projectid)

    def PutPeekExecutionRequest(self, projectid, body, executionid) -> Response:
        """Peek the engine/tool execution generated files. Read permission on the project is required.

        Execution
        PUT /api/compute/execution/{executionId}/peek
        """
        return self.PutRequest(f"/api/compute/execution/{executionid}/peek", body, None, api_version="2", projectid=projectid)
