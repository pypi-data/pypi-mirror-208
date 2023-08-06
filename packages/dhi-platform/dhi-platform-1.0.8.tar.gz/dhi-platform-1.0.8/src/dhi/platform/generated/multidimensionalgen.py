# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "md" "--classname" "MultidimensionalGenClientV" "-n" "2" "-r" "projectid" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\multidimensionalgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/multidimensional/v2" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/multidimensional/v3"
# 2022-01-13 19:02:53.687189Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/multidimensional/v2
# DHI Multidimensional API - Version 2
# API for managing multidimensional data like gridded and meshed time series
# 2

class GridTypeV2(str, Enum):
    UNKNOWN = "Unknown"
    NODEALIGNED = "NodeAligned"
    CENTERALIGNED = "CenterAligned"
    BOTTOMLEFTALIGNED = "BottomLeftAligned"
    def __str__(self) -> str:
        return str(self.value)

TemporalFilterV2Type = TypeVar("TemporalFilterV2Type", bound="TemporalFilterV2")

@attr.s(auto_attribs=True)
class TemporalFilterV2(DataContract):
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
    def from_dict(cls: TemporalFilterV2Type, src_dict: Dict[str, Any]) -> TemporalFilterV2Type:
        obj = TemporalFilterV2()
        obj.load_dict(src_dict)
        return obj

class VerticalOrientationV2(str, Enum):
    UP = "Up"
    DOWN = "Down"
    def __str__(self) -> str:
        return str(self.value)

SpatialFilterV2Type = TypeVar("SpatialFilterV2Type", bound="SpatialFilterV2")

@attr.s(auto_attribs=True)
class SpatialFilterV2(DataContract):
    geometry: str = None
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
    def from_dict(cls: SpatialFilterV2Type, src_dict: Dict[str, Any]) -> SpatialFilterV2Type:
        obj = SpatialFilterV2()
        obj.load_dict(src_dict)
        return obj

class TemporalDomainTypeV2(str, Enum):
    UNDEFINED = "Undefined"
    REGULAR = "Regular"
    IRREGULAR = "Irregular"
    def __str__(self) -> str:
        return str(self.value)

TemporalElementV2Type = TypeVar("TemporalElementV2Type", bound="TemporalElementV2")

@attr.s(auto_attribs=True)
class TemporalElementV2(DataContract):
    i: int = None
    v: str = None
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
    def from_dict(cls: TemporalElementV2Type, src_dict: Dict[str, Any]) -> TemporalElementV2Type:
        obj = TemporalElementV2()
        obj.load_dict(src_dict)
        return obj

class UnitIdV2(str, Enum):
    EUMUUNITUNDEFINED = "eumUUnitUndefined"
    EUMUMETER = "eumUmeter"
    EUMUKILOMETER = "eumUkilometer"
    EUMUMILLIMETER = "eumUmillimeter"
    EUMUFEET = "eumUfeet"
    EUMUINCH = "eumUinch"
    EUMUMILE = "eumUmile"
    EUMUYARD = "eumUyard"
    EUMUCENTIMETER = "eumUcentimeter"
    EUMUMICROMETER = "eumUmicrometer"
    EUMUNAUTICALMILE = "eumUnauticalmile"
    EUMUMILLIFEET = "eumUmillifeet"
    EUMULITERPERM2 = "eumULiterPerM2"
    EUMUMILLIMETERD50 = "eumUMilliMeterD50"
    EUMUINCHUS = "eumUinchUS"
    EUMUFEETUS = "eumUfeetUS"
    EUMUYARDUS = "eumUyardUS"
    EUMUMILEUS = "eumUmileUS"
    EUMUKILOGRAM = "eumUkilogram"
    EUMUGRAM = "eumUgram"
    EUMUMILLIGRAM = "eumUmilligram"
    EUMUMICROGRAM = "eumUmicrogram"
    EUMUTON = "eumUton"
    EUMUKILOTON = "eumUkiloton"
    EUMUMEGATON = "eumUmegaton"
    EUMUPOUND = "eumUPound"
    EUMUTONUS = "eumUtonUS"
    EUMUPERKILOGRAM = "eumUperKilogram"
    EUMUPERGRAM = "eumUperGram"
    EUMUPERMILLIGRAM = "eumUperMilligram"
    EUMUPERMICROGRAM = "eumUperMicrogram"
    EUMUPERTON = "eumUperTon"
    EUMUPERKILOTON = "eumUperKiloton"
    EUMUPERMEGATON = "eumUperMegaton"
    EUMUPERPOUND = "eumUperPound"
    EUMUPERTONUS = "eumUperTonUS"
    EUMUSEC = "eumUsec"
    EUMUMINUTE = "eumUminute"
    EUMUHOUR = "eumUhour"
    EUMUDAY = "eumUday"
    EUMUYEAR = "eumUyear"
    EUMUMONTH = "eumUmonth"
    EUMUMILLISEC = "eumUmillisec"
    EUMUM3 = "eumUm3"
    EUMULITER = "eumUliter"
    EUMUMILLILITER = "eumUmilliliter"
    EUMUFT3 = "eumUft3"
    EUMUGAL = "eumUgal"
    EUMUMGAL = "eumUmgal"
    EUMUKM3 = "eumUkm3"
    EUMUACFT = "eumUacft"
    EUMUMEGAGAL = "eumUMegaGal"
    EUMUMEGALITER = "eumUMegaLiter"
    EUMUTENTO6M3 = "eumUTenTo6m3"
    EUMUM3PERCURRENCY = "eumUm3PerCurrency"
    EUMUGALUK = "eumUgalUK"
    EUMUMEGAGALUK = "eumUMegagalUK"
    EUMUYDUS3 = "eumUydUS3"
    EUMUYARD3 = "eumUYard3"
    EUMUM3PERSEC = "eumUm3PerSec"
    EUMUFT3PERSEC = "eumUft3PerSec"
    EUMUMLPERDAY = "eumUMlPerDay"
    EUMUMGALPERDAY = "eumUMgalPerDay"
    EUMUACFTPERDAY = "eumUacftPerDay"
    EUMUM3PERYEAR = "eumUm3PerYear"
    EUMUGALPERDAYPERHEAD = "eumUGalPerDayPerHead"
    EUMULITERPERDAYPERHEAD = "eumULiterPerDayPerHead"
    EUMUM3PERSECPERHEAD = "eumUm3PerSecPerHead"
    EUMULITERPERPERSONPERDAY = "eumUliterPerPersonPerDay"
    EUMUM3PERDAY = "eumUm3PerDay"
    EUMUGALPERSEC = "eumUGalPerSec"
    EUMUGALPERDAY = "eumUGalPerDay"
    EUMUGALPERYEAR = "eumUGalPerYear"
    EUMUFT3PERDAY = "eumUft3PerDay"
    EUMUFT3PERYEAR = "eumUft3PerYear"
    EUMUM3PERMINUTE = "eumUm3PerMinute"
    EUMUFT3PERMIN = "eumUft3PerMin"
    EUMUGALPERMIN = "eumUGalPerMin"
    EUMULITERPERSEC = "eumUliterPerSec"
    EUMULITERPERMIN = "eumUliterPerMin"
    EUMUM3PERHOUR = "eumUm3PerHour"
    EUMUGALUKPERDAY = "eumUgalUKPerDay"
    EUMUMGALUKPERDAY = "eumUMgalUKPerDay"
    EUMUFT3PERDAYPERHEAD = "eumUft3PerDayPerHead"
    EUMUM3PERDAYPERHEAD = "eumUm3PerDayPerHead"
    EUMUGALUKPERSEC = "eumUGalUKPerSec"
    EUMUGALUKPERYEAR = "eumUGalUKPerYear"
    EUMUGALUKPERDAYPERHEAD = "eumUGalUKPerDayPerHead"
    EUMUYDUS3PERSEC = "eumUydUS3PerSec"
    EUMUYARD3PERSEC = "eumUyard3PerSec"
    EUMUFTUS3PERSEC = "eumUftUS3PerSec"
    EUMUFTUS3PERMIN = "eumUftUS3PerMin"
    EUMUFTUS3PERDAY = "eumUftUS3PerDay"
    EUMUFTUS3PERYEAR = "eumUftUS3PerYear"
    EUMUYARDUS3PERSEC = "eumUyardUS3PerSec"
    EUMULITERPERDAY = "eumUliterPerDay"
    EUMUMETERPERSEC = "eumUmeterPerSec"
    EUMUMILLIMETERPERHOUR = "eumUmillimeterPerHour"
    EUMUFEETPERSEC = "eumUfeetPerSec"
    EUMULITERPERSECPERKM2 = "eumUliterPerSecPerKm2"
    EUMUMILLIMETERPERDAY = "eumUmillimeterPerDay"
    EUMUACFTPERSECPERACRE = "eumUacftPerSecPerAcre"
    EUMUMETERPERDAY = "eumUmeterPerDay"
    EUMUFT3PERSECPERMI2 = "eumUft3PerSecPerMi2"
    EUMUMETERPERHOUR = "eumUmeterPerHour"
    EUMUFEETPERDAY = "eumUfeetPerDay"
    EUMUMILLIMETERPERMONTH = "eumUmillimeterPerMonth"
    EUMUINCHPERSEC = "eumUinchPerSec"
    EUMUMETERPERMINUTE = "eumUmeterPerMinute"
    EUMUFEETPERMINUTE = "eumUfeetPerMinute"
    EUMUINCHPERMINUTE = "eumUinchPerMinute"
    EUMUFEETPERHOUR = "eumUfeetPerHour"
    EUMUINCHPERHOUR = "eumUinchPerHour"
    EUMUMILLIMETERPERSECOND = "eumUmillimeterPerSecond"
    EUMUCMPERHOUR = "eumUcmPerHour"
    EUMUKNOT = "eumUknot"
    EUMUMILEPERHOUR = "eumUmilePerHour"
    EUMUKILOMETERPERHOUR = "eumUkilometerPerHour"
    EUMUACREFEETPERDAYPERACRE = "eumUAcreFeetPerDayPerAcre"
    EUMUCENTIMETERPERSECOND = "eumUCentiMeterPerSecond"
    EUMUCUBICFEETPERSECONDPERACRE = "eumUCubicFeetPerSecondPerAcre"
    EUMUCUBICMETERPERDAYPERHECTAR = "eumUCubicMeterPerDayPerHectar"
    EUMUCUBICMETERPERHOURPERHECTAR = "eumUCubicMeterPerHourPerHectar"
    EUMUCUBICMETERPERSECONDPERHECTAR = "eumUCubicMeterPerSecondPerHectar"
    EUMUGALLONPERMINUTEPERACRE = "eumUGallonPerMinutePerAcre"
    EUMULITERPERMINUTEPERHECTAR = "eumULiterPerMinutePerHectar"
    EUMULITERPERSECONDPERHECTAR = "eumULiterPerSecondPerHectar"
    EUMUMICROMETERPERSECOND = "eumUMicroMeterPerSecond"
    EUMUMILLIONGALPERDAYPERACRE = "eumUMillionGalPerDayPerAcre"
    EUMUMILLIONGALUKPERDAYPERACRE = "eumUMillionGalUKPerDayPerAcre"
    EUMUMILLIONLITERPERDAYPERHECTAR = "eumUMillionLiterPerDayPerHectar"
    EUMUINCHUSPERSECOND = "eumUinchUSPerSecond"
    EUMUFEETUSPERSECOND = "eumUfeetUSPerSecond"
    EUMUFEETUSPERDAY = "eumUfeetUSPerDay"
    EUMUINCHUSPERHOUR = "eumUinchUSPerHour"
    EUMUINCHUSPERMINUTE = "eumUinchUSPerMinute"
    EUMUMILLIMETERPERYEAR = "eumUmillimeterPerYear"
    EUMUCUBICFEETPERHOURPERACRE = "eumUCubicFeetPerHourPerAcre"
    EUMUCUBICFEETPERDAYPERACRE = "eumUCubicFeetPerDayPerAcre"
    EUMULITERPERHOURPERHECTAR = "eumULiterPerHourPerHectar"
    EUMULITERPERDAYPERHECTAR = "eumULiterPerDayPerHectar"
    EUMUMETERPERSECONDPERSECOND = "eumUMeterPerSecondPerSecond"
    EUMUFEETPERSECONDPERSECOND = "eumUFeetPerSecondPerSecond"
    EUMUKILOGRAMPERM3 = "eumUkiloGramPerM3"
    EUMUMICROGRAMPERM3 = "eumUmicroGramPerM3"
    EUMUMILLIGRAMPERM3 = "eumUmilliGramPerM3"
    EUMUGRAMPERM3 = "eumUgramPerM3"
    EUMUMICROGRAMPERL = "eumUmicroGramPerL"
    EUMUMILLIGRAMPERL = "eumUmilliGramPerL"
    EUMUGRAMPERL = "eumUgramPerL"
    EUMUPOUNDPERCUBICFEET = "eumUPoundPerCubicFeet"
    EUMUTONPERM3 = "eumUtonPerM3"
    EUMUPOUNDPERSQUAREFEET = "eumUPoundPerSquareFeet"
    EUMUTONPERM2 = "eumUtonPerM2"
    EUMUMICROGRAMPERM2 = "eumUmicroGramPerM2"
    EUMUPOUNDPERYDUS3 = "eumUPoundPerydUS3"
    EUMUPOUNDPERYARD3 = "eumUPoundPeryard3"
    EUMUPOUNDPERCUBICFEETUS = "eumUPoundPerCubicFeetUS"
    EUMUPOUNDPERSQUAREFEETUS = "eumUPoundPerSquareFeetUS"
    EUMUKILOGRAMPERMETERPERSECOND = "eumUKiloGramPerMeterPerSecond"
    EUMUPASCALSECOND = "eumUPascalSecond"
    EUMURADIAN = "eumUradian"
    EUMUDEGREE = "eumUdegree"
    EUMUDEGREENORTH50 = "eumUDegreeNorth50"
    EUMUDEGREESQUARED = "eumUdegreesquared"
    EUMUDEGREEPERMETER = "eumUdegreePerMeter"
    EUMURADIANPERMETER = "eumUradianPerMeter"
    EUMUDEGREEPERSECOND = "eumUdegreePerSecond"
    EUMURADIANPERSECOND = "eumUradianPerSecond"
    EUMUPERDAY = "eumUperDay"
    EUMUPERCENTPERDAY = "eumUpercentPerDay"
    EUMUHERTZ = "eumUhertz"
    EUMUPERHOUR = "eumUperHour"
    EUMUCURRENCYPERYEAR = "eumUcurrencyPerYear"
    EUMUPERSEC = "eumUperSec"
    EUMUBILLIONPERDAY = "eumUbillionPerDay"
    EUMUTRILLIONPERYEAR = "eumUtrillionPerYear"
    EUMUSQUAREMETERPERSECONDPERHECTAR = "eumUSquareMeterPerSecondPerHectar"
    EUMUSQUAREFEETPERSECONDPERACRE = "eumUSquareFeetPerSecondPerAcre"
    EUMUREVOLUTIONPERMINUTE = "eumURevolutionPerMinute"
    EUMUPERCENTPERHOUR = "eumUpercentPerHour"
    EUMUPERCENTPERMINUTE = "eumUpercentPerMinute"
    EUMUPERCENTPERSECOND = "eumUpercentPerSecond"
    EUMUREVOLUTIONPERSECOND = "eumURevolutionPerSecond"
    EUMUREVOLUTIONPERHOUR = "eumURevolutionPerHour"
    EUMUDEGREECELSIUS = "eumUdegreeCelsius"
    EUMUDEGREEFAHRENHEIT = "eumUdegreeFahrenheit"
    EUMUDEGREEKELVIN = "eumUdegreeKelvin"
    EUMUPERDEGREECELSIUS = "eumUperDegreeCelsius"
    EUMUPERDEGREEFAHRENHEIT = "eumUperDegreeFahrenheit"
    EUMUDELTADEGREECELSIUS = "eumUdeltaDegreeCelsius"
    EUMUDELTADEGREEFAHRENHEIT = "eumUdeltaDegreeFahrenheit"
    EUMUMILLPER100ML = "eumUmillPer100ml"
    EUMUPER100ML = "eumUPer100ml"
    EUMUPERLITER = "eumUperLiter"
    EUMUPERM3 = "eumUperM3"
    EUMUPERMILLILITER = "eumUperMilliliter"
    EUMUPERFT3 = "eumUperFt3"
    EUMUPERGALLON = "eumUperGallon"
    EUMUPERMILLIGALLON = "eumUperMilligallon"
    EUMUPERKM3 = "eumUperKm3"
    EUMUPERACFT = "eumUperAcft"
    EUMUPERMEGAGALLON = "eumUperMegagallon"
    EUMUPERMEGALITER = "eumUperMegaliter"
    EUMUPERGALLONUK = "eumUperGallonUK"
    EUMUPERMEGAGALLONUK = "eumUperMegagallonUK"
    EUMUPERYARDUS3 = "eumUperYardUS3"
    EUMUPERYARD3 = "eumUperYard3"
    EUMUSECPERMETER = "eumUSecPerMeter"
    EUMUM2 = "eumUm2"
    EUMUM3PERM = "eumUm3PerM"
    EUMUACRE = "eumUacre"
    EUMUFT2 = "eumUft2"
    EUMUHA = "eumUha"
    EUMUKM2 = "eumUkm2"
    EUMUMI2 = "eumUmi2"
    EUMUFT3PERFT = "eumUft3PerFt"
    EUMUFTUS2 = "eumUftUS2"
    EUMUYDUS2 = "eumUydUS2"
    EUMUMIUS2 = "eumUmiUS2"
    EUMUACREUS = "eumUacreUS"
    EUMUYDUS3PERYARDUS = "eumUydUS3PeryardUS"
    EUMUYARD3PERYARD = "eumUYard3PerYard"
    EUMUFTUS3PERFTUS = "eumUftUS3PerftUS"
    EUMULITERPERMETER = "eumUliterPerMeter"
    EUMUEPERM2PERDAY = "eumUEPerM2PerDay"
    EUMUTHOUSANDPERM2PERDAY = "eumUThousandPerM2PerDay"
    EUMUPERM2PERSEC = "eumUPerM2PerSec"
    EUMUMETER2ONE3RDPERSEC = "eumUMeter2One3rdPerSec"
    EUMUFEET2ONE3RDPERSEC = "eumUFeet2One3rdPerSec"
    EUMUSECPERMETER2ONE3RD = "eumUSecPerMeter2One3rd"
    EUMUSECPERFEET2ONE3RD = "eumUSecPerFeet2One3rd"
    EUMUMETER2ONEHALFPERSEC = "eumUMeter2OneHalfPerSec"
    EUMUFEET2ONEHALFPERSEC = "eumUFeet2OneHalfPerSec"
    EUMUFEETUS2ONEHALFPERSEC = "eumUFeetUS2OneHalfPerSec"
    EUMUKILOGRAMPERSEC = "eumUkilogramPerSec"
    EUMUMICROGRAMPERSEC = "eumUmicrogramPerSec"
    EUMUMILLIGRAMPERSEC = "eumUmilligramPerSec"
    EUMUGRAMPERSEC = "eumUgramPerSec"
    EUMUKILOGRAMPERHOUR = "eumUkilogramPerHour"
    EUMUKILOGRAMPERDAY = "eumUkilogramPerDay"
    EUMUGRAMPERDAY = "eumUgramPerDay"
    EUMUKILOGRAMPERYEAR = "eumUkilogramPerYear"
    EUMUGRAMPERMINUTE = "eumUGramPerMinute"
    EUMUKILOGRAMPERPERSONPERDAY = "eumUKiloGramPerPersonPerDay"
    EUMUKILOGRAMPERMINUTE = "eumUKilogramPerMinute"
    EUMUPOUNDPERDAY = "eumUPoundPerDay"
    EUMUPOUNDPERHOUR = "eumUPoundPerHour"
    EUMUPOUNDPERMINUTE = "eumUPoundPerMinute"
    EUMUPOUNDPERSECOND = "eumUPoundPerSecond"
    EUMUPOUNDPERPERSONPERDAY = "eumUPoundPerPersonPerDay"
    EUMUPOUNDPERYEAR = "eumUPoundPerYear"
    EUMUTONPERYEAR = "eumUTonPerYear"
    EUMUTONPERDAY = "eumUTonPerDay"
    EUMUTONPERSEC = "eumUTonPerSec"
    EUMUGRAMPERM2 = "eumUgramPerM2"
    EUMUKILOGRAMPERM = "eumUkilogramPerM"
    EUMUKILOGRAMPERM2 = "eumUkilogramPerM2"
    EUMUKILOGRAMPERHA = "eumUkilogramPerHa"
    EUMUMILLIGRAMPERM2 = "eumUmilligramPerM2"
    EUMUPOUNDPERACRE = "eumUPoundPerAcre"
    EUMUKILOGRAMPERKM2 = "eumUkilogramPerKm2"
    EUMUTONPERKM2 = "eumUtonPerKm2"
    EUMUGRAMPERKM2 = "eumUgramPerKm2"
    EUMUTONPERHA = "eumUtonPerHa"
    EUMUGRAMPERHA = "eumUgramPerHa"
    EUMUPOUNDPERMI2 = "eumUPoundPerMi2"
    EUMUKILOGRAMPERACRE = "eumUkilogramPerAcre"
    EUMUKILOGRAMPERSQUAREFEET = "eumUkilogramPerSquareFeet"
    EUMUKILOGRAMPERMI2 = "eumUkilogramPerMi2"
    EUMUTONPERACRE = "eumUtonPerAcre"
    EUMUTONPERSQUAREFEET = "eumUtonPerSquareFeet"
    EUMUTONPERMI2 = "eumUtonPerMi2"
    EUMUGRAMPERACRE = "eumUgramPerAcre"
    EUMUGRAMPERSQUAREFEET = "eumUgramPerSquareFeet"
    EUMUGRAMPERMI2 = "eumUgramPerMi2"
    EUMUPOUNDPERHA = "eumUPoundPerHa"
    EUMUPOUNDPERM2 = "eumUPoundPerM2"
    EUMUPOUNDPERKM2 = "eumUPoundPerKm2"
    EUMUMILLIGRAMPERHA = "eumUmilligramPerHa"
    EUMUMILLIGRAMPERKM2 = "eumUmilligramPerKm2"
    EUMUMILLIGRAMPERACRE = "eumUmilligramPerAcre"
    EUMUMILLIGRAMPERSQUAREFEET = "eumUmilligramPerSquareFeet"
    EUMUMILLIGRAMPERMI2 = "eumUmilligramPerMi2"
    EUMUPOUNDPERMETER = "eumUPoundPerMeter"
    EUMUTONPERMETER = "eumUtonPerMeter"
    EUMUGRAMPERM2PERDAY = "eumUgramPerM2PerDay"
    EUMUGRAMPERM2PERSEC = "eumUgramPerM2PerSec"
    EUMUKILOGRAMPERHAPERHOUR = "eumUkilogramPerHaPerHour"
    EUMUKILOGRAMPERM2PERSEC = "eumUkilogramPerM2PerSec"
    EUMUKILOGRAMPERHECTARPERDAY = "eumUKiloGramPerHectarPerDay"
    EUMUPOUNDPERACREPERDAY = "eumUPoundPerAcrePerDay"
    EUMUKILOGRAMPERM2PERDAY = "eumUkilogramPerM2PerDay"
    EUMUPOUNDPERFT2PERSEC = "eumUPoundPerFt2PerSec"
    EUMUGRAMPERM3PERHOUR = "eumUgramPerM3PerHour"
    EUMUGRAMPERM3PERDAY = "eumUgramPerM3PerDay"
    EUMUGRAMPERM3PERSEC = "eumUgramPerM3PerSec"
    EUMUMILLIGRAMPERLITERPERDAY = "eumUMilliGramPerLiterPerDay"
    EUMUM3PERSECPERM = "eumUm3PerSecPerM"
    EUMUM3PERYEARPERM = "eumUm3PerYearPerM"
    EUMUM2PERSEC = "eumUm2PerSec"
    EUMUFT2PERSEC = "eumUft2PerSec"
    EUMUM3PERSECPER10MM = "eumUm3PerSecPer10mm"
    EUMUFT3PERSECPERINCH = "eumUft3PerSecPerInch"
    EUMUM2PERHOUR = "eumUm2PerHour"
    EUMUM2PERDAY = "eumUm2PerDay"
    EUMUFT2PERHOUR = "eumUft2PerHour"
    EUMUFT2PERDAY = "eumUft2PerDay"
    EUMUGALUKPERDAYPERFEET = "eumUGalUKPerDayPerFeet"
    EUMUGALPERDAYPERFEET = "eumUGalPerDayPerFeet"
    EUMUGALPERMINUTEPERFEET = "eumUGalPerMinutePerFeet"
    EUMULITERPERDAYPERMETER = "eumULiterPerDayPerMeter"
    EUMULITERPERMINUTEPERMETER = "eumULiterPerMinutePerMeter"
    EUMULITERPERSECONDPERMETER = "eumULiterPerSecondPerMeter"
    EUMUFT3PERSECPERFT = "eumUft3PerSecPerFt"
    EUMUFT3PERHOURPERFT = "eumUft3PerHourPerFt"
    EUMUFT2PERSEC2 = "eumUft2PerSec2"
    EUMUCM3PERSECPERCM = "eumUcm3PerSecPerCm"
    EUMUMM3PERSECPERMM = "eumUmm3PerSecPerMm"
    EUMUFTUS3PERSECPERFTUS = "eumUftUS3PerSecPerFtUS"
    EUMUIN3PERSECPERIN = "eumUin3PerSecPerIn"
    EUMUINUS3PERSECPERINUS = "eumUinUS3PerSecPerInUS"
    EUMUYDUS3PERSECPERYDUS = "eumUydUS3PerSecPerydUS"
    EUMUYARD3PERSECPERYARD = "eumUyard3PerSecPeryard"
    EUMUYARD3PERYEARPERYARD = "eumUyard3PerYearPeryard"
    EUMUYDUS3PERYEARPERYDUS = "eumUydUS3PerYearPerydUS"
    EUMUM3PERHOURPERM = "eumUm3PerHourPerM"
    EUMUM3PERDAYPERM = "eumUm3PerDayPerM"
    EUMUFT3PERDAYPERFT = "eumUft3PerDayPerFt"
    EUMUMMPERDAY = "eumUmmPerDay"
    EUMUINPERDAY = "eumUinPerDay"
    EUMUM3PERKM2PERDAY = "eumUm3PerKm2PerDay"
    EUMUWATT = "eumUwatt"
    EUMUKWATT = "eumUkwatt"
    EUMUMWATT = "eumUmwatt"
    EUMUGWATT = "eumUgwatt"
    EUMUHORSEPOWER = "eumUHorsePower"
    EUMUPERMETER = "eumUperMeter"
    EUMUPERCENTPER100METER = "eumUpercentPer100meter"
    EUMUPERCENTPER100FEET = "eumUpercentPer100feet"
    EUMUPERFEET = "eumUperFeet"
    EUMUPERINCH = "eumUperInch"
    EUMUPERFEETUS = "eumUperFeetUS"
    EUMUPERINCHUS = "eumUperInchUS"
    EUMUM3PERS2 = "eumUm3PerS2"
    EUMUM2SECPERRAD = "eumUm2SecPerRad"
    EUMUM2PERRAD = "eumUm2PerRad"
    EUMUM2SEC = "eumUm2Sec"
    EUMUM2PERDEGREE = "eumUm2PerDegree"
    EUMUM2SEC2PERRAD = "eumUm2Sec2PerRad"
    EUMUM2PERSECPERRAD = "eumUm2PerSecPerRad"
    EUMUM2SECPERDEGREE = "eumUm2SecPerDegree"
    EUMUM2SEC2PERDEGREE = "eumUm2Sec2PerDegree"
    EUMUM2PERSECPERDEGREE = "eumUm2PerSecPerDegree"
    EUMUFT2PERSECPERRAD = "eumUft2PerSecPerRad"
    EUMUFT2PERSECPERDEGREE = "eumUft2PerSecPerDegree"
    EUMUFT2SEC2PERRAD = "eumUft2Sec2PerRad"
    EUMUFT2SEC2PERDEGREE = "eumUft2Sec2PerDegree"
    EUMUFT2SECPERRAD = "eumUft2SecPerRad"
    EUMUFT2SECPERDEGREE = "eumUft2SecPerDegree"
    EUMUFT2PERRAD = "eumUft2PerRad"
    EUMUFT2PERDEGREE = "eumUft2PerDegree"
    EUMUFT2SEC = "eumUft2Sec"
    EUMUMILLIGRAMPERL2ONEHALFPERDAY = "eumUmilliGramPerL2OneHalfPerDay"
    EUMUMILLIGRAMPERL2ONEHALFPERHOUR = "eumUmilliGramPerL2OneHalfPerHour"
    EUMUNEWTONPERSQRMETER = "eumUNewtonPerSqrMeter"
    EUMUKILONEWTONPERSQRMETER = "eumUkiloNewtonPerSqrMeter"
    EUMUPOUNDPERFEETPERSEC2 = "eumUPoundPerFeetPerSec2"
    EUMUNEWTONPERM3 = "eumUNewtonPerM3"
    EUMUKILONEWTONPERM3 = "eumUkiloNewtonPerM3"
    EUMUKILOGRAMM2 = "eumUkilogramM2"
    EUMUPOUNDSQRFEET = "eumUPoundSqrFeet"
    EUMUJOULE = "eumUJoule"
    EUMUKILOJOULE = "eumUkiloJoule"
    EUMUMEGAJOULE = "eumUmegaJoule"
    EUMUGIGAJOULE = "eumUgigaJoule"
    EUMUTERAJOULE = "eumUteraJoule"
    EUMUKILOWATTHOUR = "eumUKiloWattHour"
    EUMUWATTSECOND = "eumUWattSecond"
    EUMUPETAJOULE = "eumUpetaJoule"
    EUMUEXAJOULE = "eumUexaJoule"
    EUMUMEGAWATTHOUR = "eumUmegaWattHour"
    EUMUGIGAWATTHOUR = "eumUgigaWattHour"
    EUMUPERJOULE = "eumUperJoule"
    EUMUPERKILOJOULE = "eumUperKiloJoule"
    EUMUPERMEGAJOULE = "eumUperMegaJoule"
    EUMUPERGIGAJOULE = "eumUperGigaJoule"
    EUMUPERTERAJOULE = "eumUperTeraJoule"
    EUMUPERPETAJOULE = "eumUperPetaJoule"
    EUMUPEREXAJOULE = "eumUperExaJoule"
    EUMUPERKILOWATTHOUR = "eumUperKiloWattHour"
    EUMUPERWATTSECOND = "eumUperWattSecond"
    EUMUPERMEGAWATTHOUR = "eumUperMegaWattHour"
    EUMUPERGIGAWATTHOUR = "eumUperGigaWattHour"
    EUMUKILOJOULEPERM2PERHOUR = "eumUkiloJoulePerM2PerHour"
    EUMUKILOJOULEPERM2PERDAY = "eumUkiloJoulePerM2PerDay"
    EUMUMEGAJOULEPERM2PERDAY = "eumUmegaJoulePerM2PerDay"
    EUMUJOULEPERM2PERDAY = "eumUJoulePerM2PerDay"
    EUMUM2MMPERKILOJOULE = "eumUm2mmPerKiloJoule"
    EUMUM2MMPERMEGAJOULE = "eumUm2mmPerMegaJoule"
    EUMUMILLIMETERPERDEGREECELSIUSPERDAY = "eumUMilliMeterPerDegreeCelsiusPerDay"
    EUMUMILLIMETERPERDEGREECELSIUSPERHOUR = "eumUMilliMeterPerDegreeCelsiusPerHour"
    EUMUINCHPERDEGREEFAHRENHEITPERDAY = "eumUInchPerDegreeFahrenheitPerDay"
    EUMUINCHPERDEGREEFAHRENHEITPERHOUR = "eumUInchPerDegreeFahrenheitPerHour"
    EUMUPERDEGREECELSIUSPERDAY = "eumUPerDegreeCelsiusPerDay"
    EUMUPERDEGREECELSIUSPERHOUR = "eumUPerDegreeCelsiusPerHour"
    EUMUPERDEGREEFAHRENHEITPERDAY = "eumUPerDegreeFahrenheitPerDay"
    EUMUPERDEGREEFAHRENHEITPERHOUR = "eumUPerDegreeFahrenheitPerHour"
    EUMUDEGREECELSIUSPER100METER = "eumUDegreeCelsiusPer100meter"
    EUMUDEGREECELSIUSPER100FEET = "eumUDegreeCelsiusPer100feet"
    EUMUDEGREEFAHRENHEITPER100METER = "eumUDegreeFahrenheitPer100meter"
    EUMUDEGREEFAHRENHEITPER100FEET = "eumUDegreeFahrenheitPer100feet"
    EUMUPASCAL = "eumUPascal"
    EUMUHECTOPASCAL = "eumUhectoPascal"
    EUMUKILOPASCAL = "eumUkiloPascal"
    EUMUPSI = "eumUpsi"
    EUMUMEGAPASCAL = "eumUMegaPascal"
    EUMUMETRESOFWATER = "eumUMetresOfWater"
    EUMUFEETOFWATER = "eumUFeetOfWater"
    EUMUBAR = "eumUBar"
    EUMUMILLIBAR = "eumUmilliBar"
    EUMUMICROPASCAL = "eumUmicroPascal"
    EUMUDECIBAR = "eumUdeciBar"
    EUMUDB_RE_1MUPA2SECOND = "eumUdB_re_1muPa2second"
    EUMUDBPERLAMBDA = "eumUdBperLambda"
    EUMUPSU = "eumUPSU"
    EUMUPSUM3PERSEC = "eumUPSUM3PerSec"
    EUMUDEGREECELSIUSM3PERSEC = "eumUDegreeCelsiusM3PerSec"
    EUMUCONCNONDIMM3PERSEC = "eumUConcNonDimM3PerSec"
    EUMUPSUFT3PERSEC = "eumUPSUft3PerSec"
    EUMUDEGREEFAHRENHEITFT3PERSEC = "eumUDegreeFahrenheitFt3PerSec"
    EUMUM2PERSEC2 = "eumUm2PerSec2"
    EUMUM2PERSEC3 = "eumUm2PerSec3"
    EUMUFT2PERSEC3 = "eumUft2PerSec3"
    EUMUM2PERSEC3PERRAD = "eumUm2PerSec3PerRad"
    EUMUFT2PERSEC3PERRAD = "eumUft2PerSec3PerRad"
    EUMUJOULEPERKILOGRAM = "eumUJoulePerKilogram"
    EUMUWATTPERM2 = "eumUWattPerM2"
    EUMUJOULEKILOGRAMPERKELVIN = "eumUJouleKilogramPerKelvin"
    EUMUM3PERSEC2 = "eumUm3PerSec2"
    EUMUFT3PERSEC2 = "eumUft3PerSec2"
    EUMUACREFEETPERDAYPERSECOND = "eumUAcreFeetPerDayPerSecond"
    EUMUMILLIONGALUKPERDAYPERSECOND = "eumUMillionGalUKPerDayPerSecond"
    EUMUMILLIONGALPERDAYPERSECOND = "eumUMillionGalPerDayPerSecond"
    EUMUGALPERMINUTEPERSECOND = "eumUGalPerMinutePerSecond"
    EUMUCUBICMETERPERDAYPERSECOND = "eumUCubicMeterPerDayPerSecond"
    EUMUCUBICMETERPERHOURPERSECOND = "eumUCubicMeterPerHourPerSecond"
    EUMUMILLIONLITERPERDAYPERSECOND = "eumUMillionLiterPerDayPerSecond"
    EUMULITERPERMINUTEPERSECOND = "eumULiterPerMinutePerSecond"
    EUMULITERPERSECONDSQUARE = "eumULiterPerSecondSquare"
    EUMUM3PERGRAM = "eumUm3Pergram"
    EUMULITERPERGRAM = "eumULiterPergram"
    EUMUM3PERMILLIGRAM = "eumUm3PerMilligram"
    EUMUM3PERMICROGRAM = "eumUm3PerMicrogram"
    EUMUNEWTON = "eumUNewton"
    EUMUKILONEWTON = "eumUkiloNewton"
    EUMUMEGANEWTON = "eumUmegaNewton"
    EUMUMILLINEWTON = "eumUmilliNewton"
    EUMUKILOGRAMMETER = "eumUkilogramMeter"
    EUMUKILOGRAMMETER2 = "eumUkilogramMeter2"
    EUMUKILOGRAMMETERPERSECOND = "eumUkilogramMeterPerSecond"
    EUMUKILOGRAMMETER2PERSECOND = "eumUkilogramMeter2PerSecond"
    EUMUM2PERHERTZ = "eumUm2PerHertz"
    EUMUM2PERHERTZPERDEGREE = "eumUm2PerHertzPerDegree"
    EUMUM2PERHERTZPERRADIAN = "eumUm2PerHertzPerRadian"
    EUMUFT2PERHERTZ = "eumUft2PerHertz"
    EUMUFT2PERHERTZPERDEGREE = "eumUft2PerHertzPerDegree"
    EUMUFT2PERHERTZPERRADIAN = "eumUft2PerHertzPerRadian"
    EUMUM2PERHERTZ2 = "eumUm2PerHertz2"
    EUMUM2PERHERTZ2PERDEGREE = "eumUm2PerHertz2PerDegree"
    EUMUM2PERHERTZ2PERRADIAN = "eumUm2PerHertz2PerRadian"
    EUMULITERPERSECPERMETER = "eumUliterPerSecPerMeter"
    EUMULITERPERMINPERMETER = "eumUliterPerMinPerMeter"
    EUMUMEGALITERPERDAYPERMETER = "eumUMegaLiterPerDayPerMeter"
    EUMUM3PERHOURPERMETER = "eumUm3PerHourPerMeter"
    EUMUM3PERDAYPERMETER = "eumUm3PerDayPerMeter"
    EUMUFT3PERSECPERPSI = "eumUft3PerSecPerPsi"
    EUMUGALLONPERMINPERPSI = "eumUgallonPerMinPerPsi"
    EUMUMGALPERDAYPERPSI = "eumUMgalPerDayPerPsi"
    EUMUMGALUKPERDAYPERPSI = "eumUMgalUKPerDayPerPsi"
    EUMUACFTPERDAYPERPSI = "eumUacftPerDayPerPsi"
    EUMUM3PERHOURPERBAR = "eumUm3PerHourPerBar"
    EUMUKILOGRAMPERS2 = "eumUKilogramPerS2"
    EUMUM2PERKILOGRAM = "eumUm2Perkilogram"
    EUMUPERMETERPERSECOND = "eumUPerMeterPerSecond"
    EUMUMETERPERSECONDPERHECTAR = "eumUMeterPerSecondPerHectar"
    EUMUFEETPERSECONDPERACRE = "eumUFeetPerSecondPerAcre"
    EUMUPERSQUAREMETER = "eumUPerSquareMeter"
    EUMUPERACRE = "eumUPerAcre"
    EUMUPERHECTAR = "eumUPerHectar"
    EUMUPERKM2 = "eumUperKm2"
    EUMUPERCUBICMETER = "eumUPerCubicMeter"
    EUMUCURRENCYPERCUBICMETER = "eumUCurrencyPerCubicMeter"
    EUMUCURRENCYPERCUBICFEET = "eumUCurrencyPerCubicFeet"
    EUMUSQUAREMETERPERSECOND = "eumUSquareMeterPerSecond"
    EUMUSQUAREFEETPERSECOND = "eumUSquareFeetPerSecond"
    EUMUPERWATT = "eumUPerWatt"
    EUMUNEWTONMETER = "eumUNewtonMeter"
    EUMUKILONEWTONMETER = "eumUkiloNewtonMeter"
    EUMUMEGANEWTONMETER = "eumUmegaNewtonMeter"
    EUMUNEWTONMILLIMETER = "eumUNewtonMillimeter"
    EUMUNEWTONMETERSECOND = "eumUNewtonMeterSecond"
    EUMUNEWTONPERMETERPERSECOND = "eumUNewtonPerMeterPerSecond"
    EUMUMOLE = "eumUmole"
    EUMUMILLIMOLE = "eumUmillimole"
    EUMUMICROMOLE = "eumUmicromole"
    EUMUNANOMOLE = "eumUnanomole"
    EUMUMOLEPERLITER = "eumUmolePerLiter"
    EUMUMILLIMOLEPERLITER = "eumUmillimolePerLiter"
    EUMUMICROMOLEPERLITER = "eumUmicromolePerLiter"
    EUMUNANOMOLEPERLITER = "eumUnanomolePerLiter"
    EUMUMOLEPERM3 = "eumUmolePerM3"
    EUMUMILLIMOLEPERM3 = "eumUmillimolePerM3"
    EUMUMICROMOLEPERM3 = "eumUmicromolePerM3"
    EUMUMOLEPERKILOGRAM = "eumUmolePerKilogram"
    EUMUMILLIMOLEPERKILOGRAM = "eumUmillimolePerKilogram"
    EUMUMICROMOLEPERKILOGRAM = "eumUmicromolePerKilogram"
    EUMUNANOMOLEPERKILOGRAM = "eumUnanomolePerKilogram"
    EUMUONEPERONE = "eumUOnePerOne"
    EUMUPERCENT = "eumUPerCent"
    EUMUPERTHOUSAND = "eumUPerThousand"
    EUMUHOURSPERDAY = "eumUHoursPerDay"
    EUMUPERSON = "eumUPerson"
    EUMUGRAMPERGRAM = "eumUGramPerGram"
    EUMUGRAMPERKILOGRAM = "eumUGramPerKilogram"
    EUMUMILLIGRAMPERGRAM = "eumUMilligramPerGram"
    EUMUMILLIGRAMPERKILOGRAM = "eumUMilligramPerKilogram"
    EUMUMICROGRAMPERGRAM = "eumUMicrogramPerGram"
    EUMUKILOGRAMPERKILOGRAM = "eumUKilogramPerKilogram"
    EUMUM3PERM3 = "eumUM3PerM3"
    EUMULITERPERM3 = "eumULiterPerM3"
    EUMUINTCODE = "eumUintCode"
    EUMUMETERPERMETER = "eumUMeterPerMeter"
    EUMUPERMINUTE = "eumUperminute"
    EUMUPERMONTH = "eumUpermonth"
    EUMUPERYEAR = "eumUperyear"
    EUMUMILLILITERPERLITER = "eumUMilliliterPerLiter"
    EUMUMICROLITERPERLITER = "eumUMicroliterPerLiter"
    EUMUPERMILLION = "eumUPerMillion"
    EUMUGACCELERATION = "eumUgAcceleration"
    EUMUAMPERE = "eumUampere"
    EUMUMILLIAMPERE = "eumUMilliAmpere"
    EUMUMICROAMPERE = "eumUmicroAmpere"
    EUMUKILOAMPERE = "eumUkiloAmpere"
    EUMUMEGAAMPERE = "eumUmegaAmpere"
    EUMUVOLT = "eumUvolt"
    EUMUMILLIVOLT = "eumUmilliVolt"
    EUMUMICROVOLT = "eumUmicroVolt"
    EUMUKILOVOLT = "eumUkiloVolt"
    EUMUMEGAVOLT = "eumUmegaVolt"
    EUMUOHM = "eumUohm"
    EUMUKILOOHM = "eumUkiloOhm"
    EUMUMEGAOHM = "eumUmegaOhm"
    EUMUWATTPERMETER = "eumUWattPerMeter"
    EUMUKILOWATTPERMETER = "eumUkiloWattPerMeter"
    EUMUMEGAWATTPERMETER = "eumUmegaWattPerMeter"
    EUMUGIGAWATTPERMETER = "eumUgigaWattPerMeter"
    EUMUKILOWATTPERFEET = "eumUkiloWattPerFeet"
    EUMUSIEMENS = "eumUsiemens"
    EUMUMILLISIEMENS = "eumUmilliSiemens"
    EUMUMICROSIEMENS = "eumUmicroSiemens"
    EUMUSIEMENSPERMETER = "eumUsiemensPerMeter"
    EUMUMILLISIEMENSPERCENTIMETER = "eumUmilliSiemensPerCentimeter"
    EUMUMICROSIEMENSPERCENTIMETER = "eumUmicroSiemensPerCentimeter"
    EUMUKILOGRAMPERSECPERM = "eumUkilogramPerSecPerM"
    EUMUCENTIPOISE = "eumUCentipoise"
    EUMUPOUNDFORCESECPERSQRFT = "eumUPoundforceSecPerSqrFt"
    EUMUPOUNDFEETPERSEC = "eumUPoundFeetPerSec"
    def __str__(self) -> str:
        return str(self.value)

TemporalDomainOutputV2Type = TypeVar("TemporalDomainOutputV2Type", bound="TemporalDomainOutputV2")

@attr.s(auto_attribs=True)
class TemporalDomainOutputV2(DataContract):
    temporalDomainType: TemporalDomainTypeV2 = None
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
    def from_dict(cls: TemporalDomainOutputV2Type, src_dict: Dict[str, Any]) -> TemporalDomainOutputV2Type:
        obj = TemporalDomainOutputV2()
        obj.load_dict(src_dict)
        return obj

RegularTemporalDomainOutputV2Type = TypeVar("RegularTemporalDomainOutputV2Type", bound="RegularTemporalDomainOutputV2")

@attr.s(auto_attribs=True)
class RegularTemporalDomainOutputV2(TemporalDomainOutputV2):
    step: str = None
    start: str = None
    count: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalDomainOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: RegularTemporalDomainOutputV2Type, src_dict: Dict[str, Any]) -> RegularTemporalDomainOutputV2Type:
        obj = RegularTemporalDomainOutputV2()
        obj.load_dict(src_dict)
        return obj

TemporalIndexListFilterV2Type = TypeVar("TemporalIndexListFilterV2Type", bound="TemporalIndexListFilterV2")

@attr.s(auto_attribs=True)
class TemporalIndexListFilterV2(TemporalFilterV2):
    indices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexListFilterV2Type, src_dict: Dict[str, Any]) -> TemporalIndexListFilterV2Type:
        obj = TemporalIndexListFilterV2()
        obj.load_dict(src_dict)
        return obj

VerticalDatumV2Type = TypeVar("VerticalDatumV2Type", bound="VerticalDatumV2")

@attr.s(auto_attribs=True)
class VerticalDatumV2(DataContract):
    origin: float = None
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
    def from_dict(cls: VerticalDatumV2Type, src_dict: Dict[str, Any]) -> VerticalDatumV2Type:
        obj = VerticalDatumV2()
        obj.load_dict(src_dict)
        return obj

IrregularTemporalDomainOutputV2Type = TypeVar("IrregularTemporalDomainOutputV2Type", bound="IrregularTemporalDomainOutputV2")

@attr.s(auto_attribs=True)
class IrregularTemporalDomainOutputV2(TemporalDomainOutputV2):
    times: List[TemporalElementV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalDomainOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IrregularTemporalDomainOutputV2Type, src_dict: Dict[str, Any]) -> IrregularTemporalDomainOutputV2Type:
        obj = IrregularTemporalDomainOutputV2()
        obj.load_dict(src_dict)
        return obj

VerticalFilterV2Type = TypeVar("VerticalFilterV2Type", bound="VerticalFilterV2")

@attr.s(auto_attribs=True)
class VerticalFilterV2(DataContract):
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
    def from_dict(cls: VerticalFilterV2Type, src_dict: Dict[str, Any]) -> VerticalFilterV2Type:
        obj = VerticalFilterV2()
        obj.load_dict(src_dict)
        return obj

VerticalValueFilterV2Type = TypeVar("VerticalValueFilterV2Type", bound="VerticalValueFilterV2")

@attr.s(auto_attribs=True)
class VerticalValueFilterV2(VerticalFilterV2):
    from_: float = None
    to: float = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalValueFilterV2Type, src_dict: Dict[str, Any]) -> VerticalValueFilterV2Type:
        obj = VerticalValueFilterV2()
        obj.load_dict(src_dict)
        return obj

TemporalValueFilterV2Type = TypeVar("TemporalValueFilterV2Type", bound="TemporalValueFilterV2")

@attr.s(auto_attribs=True)
class TemporalValueFilterV2(TemporalFilterV2):
    from_: str = None
    to: str = None
    at: str = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalValueFilterV2Type, src_dict: Dict[str, Any]) -> TemporalValueFilterV2Type:
        obj = TemporalValueFilterV2()
        obj.load_dict(src_dict)
        return obj

VerticalIndexFilterV2Type = TypeVar("VerticalIndexFilterV2Type", bound="VerticalIndexFilterV2")

@attr.s(auto_attribs=True)
class VerticalIndexFilterV2(VerticalFilterV2):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalIndexFilterV2Type, src_dict: Dict[str, Any]) -> VerticalIndexFilterV2Type:
        obj = VerticalIndexFilterV2()
        obj.load_dict(src_dict)
        return obj

class SpatialDomainTypeV2(str, Enum):
    UNDEFINED = "Undefined"
    MESH = "Mesh"
    EQUIDISTANTGRID2D = "EquidistantGrid2D"
    EQUIDISTANTGRID0D = "EquidistantGrid0D"
    EQUIDISTANTGRID1D = "EquidistantGrid1D"
    EQUIDISTANTGRID3D = "EquidistantGrid3D"
    NONEQUIDISTANTGRID2D = "NonequidistantGrid2D"
    NONEQUIDISTANTGRID1D = "NonequidistantGrid1D"
    NONEQUIDISTANTGRID3D = "NonequidistantGrid3D"
    CURVELINEARGRID2D = "CurveLinearGrid2D"
    CURVELINEARGRID1D = "CurveLinearGrid1D"
    CURVELINEARGRID3D = "CurveLinearGrid3D"
    def __str__(self) -> str:
        return str(self.value)

TemporalIndexFilterV2Type = TypeVar("TemporalIndexFilterV2Type", bound="TemporalIndexFilterV2")

@attr.s(auto_attribs=True)
class TemporalIndexFilterV2(TemporalFilterV2):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexFilterV2Type, src_dict: Dict[str, Any]) -> TemporalIndexFilterV2Type:
        obj = TemporalIndexFilterV2()
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

BinaryOptionsV2Type = TypeVar("BinaryOptionsV2Type", bound="BinaryOptionsV2")

@attr.s(auto_attribs=True)
class BinaryOptionsV2(DataContract):
    majorVersion: int = None
    minorVersion: int = None
    coordinatePrecision: int = None
    includeMeshElementId: str = None
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
    def from_dict(cls: BinaryOptionsV2Type, src_dict: Dict[str, Any]) -> BinaryOptionsV2Type:
        obj = BinaryOptionsV2()
        obj.load_dict(src_dict)
        return obj

DataBlockFloatV2Type = TypeVar("DataBlockFloatV2Type", bound="DataBlockFloatV2")

@attr.s(auto_attribs=True)
class DataBlockFloatV2(DataContract):
    itemIndex: int = None
    timeIndex: int = None
    layerIndex: int = None
    data: List[float] = None
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
    def from_dict(cls: DataBlockFloatV2Type, src_dict: Dict[str, Any]) -> DataBlockFloatV2Type:
        obj = DataBlockFloatV2()
        obj.load_dict(src_dict)
        return obj

TimeseriesDataBlockFloatV2Type = TypeVar("TimeseriesDataBlockFloatV2Type", bound="TimeseriesDataBlockFloatV2")

@attr.s(auto_attribs=True)
class TimeseriesDataBlockFloatV2(DataContract):
    itemIndex: int = None
    elementIndex: int = None
    layerIndex: int = None
    data: List[float] = None
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
    def from_dict(cls: TimeseriesDataBlockFloatV2Type, src_dict: Dict[str, Any]) -> TimeseriesDataBlockFloatV2Type:
        obj = TimeseriesDataBlockFloatV2()
        obj.load_dict(src_dict)
        return obj

SpatialElementV2Type = TypeVar("SpatialElementV2Type", bound="SpatialElementV2")

@attr.s(auto_attribs=True)
class SpatialElementV2(DataContract):
    i: int = None
    v: List[List[float]] = None
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
    def from_dict(cls: SpatialElementV2Type, src_dict: Dict[str, Any]) -> SpatialElementV2Type:
        obj = SpatialElementV2()
        obj.load_dict(src_dict)
        return obj

TimeSeriesQueryOutputV2Type = TypeVar("TimeSeriesQueryOutputV2Type", bound="TimeSeriesQueryOutputV2")

@attr.s(auto_attribs=True)
class TimeSeriesQueryOutputV2(DataContract):
    datasetId: str = None
    elements: List[SpatialElementV2] = None
    timeSteps: List[str] = None
    srid: int = None
    dataBlocks: List[TimeseriesDataBlockFloatV2] = None
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
    def from_dict(cls: TimeSeriesQueryOutputV2Type, src_dict: Dict[str, Any]) -> TimeSeriesQueryOutputV2Type:
        obj = TimeSeriesQueryOutputV2()
        obj.load_dict(src_dict)
        return obj

UnitV2Type = TypeVar("UnitV2Type", bound="UnitV2")

@attr.s(auto_attribs=True)
class UnitV2(DataContract):
    id: UnitIdV2 = None
    description: str = None
    abbreviation: str = None
    expression: str = None
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
    def from_dict(cls: UnitV2Type, src_dict: Dict[str, Any]) -> UnitV2Type:
        obj = UnitV2()
        obj.load_dict(src_dict)
        return obj

VerticalDomainOutputV2Type = TypeVar("VerticalDomainOutputV2Type", bound="VerticalDomainOutputV2")

@attr.s(auto_attribs=True)
class VerticalDomainOutputV2(DataContract):
    datum: VerticalDatumV2 = None
    maxZ: List[float] = None
    name: str = None
    orientation: VerticalOrientationV2 = None
    unit: UnitV2 = None
    layerCount: int = None
    layerDepths: List[float] = None
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
    def from_dict(cls: VerticalDomainOutputV2Type, src_dict: Dict[str, Any]) -> VerticalDomainOutputV2Type:
        obj = VerticalDomainOutputV2()
        obj.load_dict(src_dict)
        return obj

SpatialDomainOutputV2Type = TypeVar("SpatialDomainOutputV2Type", bound="SpatialDomainOutputV2")

@attr.s(auto_attribs=True)
class SpatialDomainOutputV2(DataContract):
    spatialDomainType: SpatialDomainTypeV2 = None
    verticalDomain: VerticalDomainOutputV2 = None
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
    def from_dict(cls: SpatialDomainOutputV2Type, src_dict: Dict[str, Any]) -> SpatialDomainOutputV2Type:
        obj = SpatialDomainOutputV2()
        obj.load_dict(src_dict)
        return obj

GridOutputV2Type = TypeVar("GridOutputV2Type", bound="GridOutputV2")

@attr.s(auto_attribs=True)
class GridOutputV2(SpatialDomainOutputV2):
    latitude: float = None
    longitude: float = None
    rotation: float = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SpatialDomainOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: GridOutputV2Type, src_dict: Dict[str, Any]) -> GridOutputV2Type:
        obj = GridOutputV2()
        obj.load_dict(src_dict)
        return obj

EquidistantGrid2DOutputV2Type = TypeVar("EquidistantGrid2DOutputV2Type", bound="EquidistantGrid2DOutputV2")

@attr.s(auto_attribs=True)
class EquidistantGrid2DOutputV2(GridOutputV2):
    x0: float = None
    dx: float = None
    nx: int = None
    y0: float = None
    dy: float = None
    ny: int = None
    gridType: GridTypeV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GridOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: EquidistantGrid2DOutputV2Type, src_dict: Dict[str, Any]) -> EquidistantGrid2DOutputV2Type:
        obj = EquidistantGrid2DOutputV2()
        obj.load_dict(src_dict)
        return obj

QueryOutputV2Type = TypeVar("QueryOutputV2Type", bound="QueryOutputV2")

@attr.s(auto_attribs=True)
class QueryOutputV2(DataContract):
    datasetId: str = None
    elements: List[SpatialElementV2] = None
    srid: int = None
    dataBlocks: List[DataBlockFloatV2] = None
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
    def from_dict(cls: QueryOutputV2Type, src_dict: Dict[str, Any]) -> QueryOutputV2Type:
        obj = QueryOutputV2()
        obj.load_dict(src_dict)
        return obj

ItemFilterV2Type = TypeVar("ItemFilterV2Type", bound="ItemFilterV2")

@attr.s(auto_attribs=True)
class ItemFilterV2(DataContract):
    itemIndices: List[int] = None
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
    def from_dict(cls: ItemFilterV2Type, src_dict: Dict[str, Any]) -> ItemFilterV2Type:
        obj = ItemFilterV2()
        obj.load_dict(src_dict)
        return obj

QueryInputV2Type = TypeVar("QueryInputV2Type", bound="QueryInputV2")

@attr.s(auto_attribs=True)
class QueryInputV2(DataContract):
    itemFilter: ItemFilterV2 = None
    spatialFilter: SpatialFilterV2 = None
    temporalFilter: TemporalFilterV2 = None
    verticalFilter: VerticalFilterV2 = None
    includeGeometries: str = None
    includeValues: str = None
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
    def from_dict(cls: QueryInputV2Type, src_dict: Dict[str, Any]) -> QueryInputV2Type:
        obj = QueryInputV2()
        obj.load_dict(src_dict)
        return obj

BinaryQueryInputV2Type = TypeVar("BinaryQueryInputV2Type", bound="BinaryQueryInputV2")

@attr.s(auto_attribs=True)
class BinaryQueryInputV2(DataContract):
    query: QueryInputV2 = None
    options: BinaryOptionsV2 = None
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
    def from_dict(cls: BinaryQueryInputV2Type, src_dict: Dict[str, Any]) -> BinaryQueryInputV2Type:
        obj = BinaryQueryInputV2()
        obj.load_dict(src_dict)
        return obj

NonequidistantGrid2DOutputV2Type = TypeVar("NonequidistantGrid2DOutputV2Type", bound="NonequidistantGrid2DOutputV2")

@attr.s(auto_attribs=True)
class NonequidistantGrid2DOutputV2(GridOutputV2):
    xCoordinates: List[float] = None
    yCoordinates: List[float] = None
    gridType: GridTypeV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GridOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: NonequidistantGrid2DOutputV2Type, src_dict: Dict[str, Any]) -> NonequidistantGrid2DOutputV2Type:
        obj = NonequidistantGrid2DOutputV2()
        obj.load_dict(src_dict)
        return obj

class ItemIdV2(str, Enum):
    EUMIITEMUNDEFINED = "eumIItemUndefined"
    EUMIWATERLEVEL = "eumIWaterLevel"
    EUMIDISCHARGE = "eumIDischarge"
    EUMIWINDVELOCITY = "eumIWindVelocity"
    EUMIWINDDIRECTION = "eumIWindDirection"
    EUMIRAINFALL = "eumIRainfall"
    EUMIEVAPORATION = "eumIEvaporation"
    EUMITEMPERATURE = "eumITemperature"
    EUMICONCENTRATION = "eumIConcentration"
    EUMIBACTERIACONC = "eumIBacteriaConc"
    EUMIRESISTFACTOR = "eumIResistFactor"
    EUMISEDIMENTTRANSPORT = "eumISedimentTransport"
    EUMIBOTTOMLEVEL = "eumIBottomLevel"
    EUMIBOTTOMLEVELCHANGE = "eumIBottomLevelChange"
    EUMISEDIMENTFRACTION = "eumISedimentFraction"
    EUMISEDIMENTFRACTIONCHANGE = "eumISedimentFractionChange"
    EUMIGATELEVEL = "eumIGateLevel"
    EUMIFLOWVELOCITY = "eumIFlowVelocity"
    EUMIDENSITY = "eumIDensity"
    EUMIDAMBREACHLEVEL = "eumIDamBreachLevel"
    EUMIDAMBREACHWIDTH = "eumIDamBreachWidth"
    EUMIDAMBREACHSLOPE = "eumIDamBreachSlope"
    EUMISUNSHINE = "eumISunShine"
    EUMISUNRADIATION = "eumISunRadiation"
    EUMIRELATIVEHUMIDITY = "eumIRelativeHumidity"
    EUMISALINITY = "eumISalinity"
    EUMISURFACESLOPE = "eumISurfaceSlope"
    EUMIFLOWAREA = "eumIFlowArea"
    EUMIFLOWWIDTH = "eumIFlowWidth"
    EUMIHYDRAULICRADIUS = "eumIHydraulicRadius"
    EUMIRESISTANCERADIUS = "eumIResistanceRadius"
    EUMIMANNINGSM = "eumIManningsM"
    EUMIMANNINGSN = "eumIManningsn"
    EUMICHEZYNO = "eumIChezyNo"
    EUMICONVEYANCE = "eumIConveyance"
    EUMIFROUDENO = "eumIFroudeNo"
    EUMIWATERVOLUME = "eumIWaterVolume"
    EUMIFLOODEDAREA = "eumIFloodedArea"
    EUMIWATERVOLUMEERROR = "eumIWaterVolumeError"
    EUMIACCWATERVOLUMEERROR = "eumIAccWaterVolumeError"
    EUMICOMPMASS = "eumICompMass"
    EUMICOMPMASSERROR = "eumICompMassError"
    EUMIACCCOMPMASSERROR = "eumIAccCompMassError"
    EUMIRELCOMPMASSERROR = "eumIRelCompMassError"
    EUMIRELACCCOMPMASSERROR = "eumIRelAccCompMassError"
    EUMICOMPDECAY = "eumICompDecay"
    EUMIACCCOMPDECAY = "eumIAccCompDecay"
    EUMICOMPTRANSP = "eumICompTransp"
    EUMIACCCOMPTRANSP = "eumIAccCompTransp"
    EUMICOMPDISPTRANSP = "eumICompDispTransp"
    EUMIACCCOMPDISPTRANSP = "eumIAccCompDispTransp"
    EUMICOMPCONVTRANSP = "eumICompConvTransp"
    EUMIACCCOMPCONVTRANSP = "eumIAccCompConvTransp"
    EUMIACCSEDIMENTTRANSPORT = "eumIAccSedimentTransport"
    EUMIDUNELENGTH = "eumIDuneLength"
    EUMIDUNEHEIGHT = "eumIDuneHeight"
    EUMIBEDSEDIMENTLOAD = "eumIBedSedimentLoad"
    EUMISUSPSEDIMENTLOAD = "eumISuspSedimentLoad"
    EUMIIRRIGATION = "eumIIrrigation"
    EUMIRELMOISTURECONT = "eumIRelMoistureCont"
    EUMIGROUNDWATERDEPTH = "eumIGroundWaterDepth"
    EUMISNOWCOVER = "eumISnowCover"
    EUMIINFILTRATION = "eumIInfiltration"
    EUMIRECHARGE = "eumIRecharge"
    EUMIOF1_FLOW = "eumIOF1_Flow"
    EUMIIF1_FLOW = "eumIIF1_Flow"
    EUMICAPILLARYFLUX = "eumICapillaryFlux"
    EUMISURFSTORAGE_OF1 = "eumISurfStorage_OF1"
    EUMISURFSTORAGE_OF0 = "eumISurfStorage_OF0"
    EUMISEDIMENTLAYER = "eumISedimentLayer"
    EUMIBEDLEVEL = "eumIBedLevel"
    EUMIRAINFALLINTENSITY = "eumIRainfallIntensity"
    EUMIPRODUCTIONRATE = "eumIproductionRate"
    EUMISEDIMENTMASS = "eumIsedimentMass"
    EUMIPRIMARYPRODUCTION = "eumIprimaryProduction"
    EUMIPRODPERVOLUME = "eumIprodPerVolume"
    EUMISECCHIDEPTH = "eumIsecchiDepth"
    EUMIACCSEDIMENTMASS = "eumIAccSedimentMass"
    EUMISEDIMENTMASSPERM = "eumISedimentMassPerM"
    EUMISURFACEELEVATION = "eumISurfaceElevation"
    EUMIBATHYMETRY = "eumIBathymetry"
    EUMIFLOWFLUX = "eumIFlowFlux"
    EUMIBEDLOADPERM = "eumIBedLoadPerM"
    EUMISUSPLOADPERM = "eumISuspLoadPerM"
    EUMISEDITRANSPORTPERM = "eumISediTransportPerM"
    EUMIWAVEHEIGHT = "eumIWaveHeight"
    EUMIWAVEPERIOD = "eumIWavePeriod"
    EUMIWAVEFREQUENCY = "eumIWaveFrequency"
    EUMIPOTENTIALEVAPRATE = "eumIPotentialEvapRate"
    EUMIRAINFALLRATE = "eumIRainfallRate"
    EUMIWATERDEMAND = "eumIWaterDemand"
    EUMIRETURNFLOWFRACTION = "eumIReturnFlowFraction"
    EUMILINEARROUTINGCOEF = "eumILinearRoutingCoef"
    EUMISPECIFICRUNOFF = "eumISpecificRunoff"
    EUMIMACHINEEFFICIENCY = "eumIMachineEfficiency"
    EUMITARGETPOWER = "eumITargetPower"
    EUMIWAVEDIRECTION = "eumIWaveDirection"
    EUMIACCSEDITRANSPORTPERM = "eumIAccSediTransportPerM"
    EUMISIGNIFICANTWAVEHEIGHT = "eumISignificantWaveHeight"
    EUMISHIELDSPARAMETER = "eumIShieldsParameter"
    EUMIANGLEBEDVELOCITY = "eumIAngleBedVelocity"
    EUMIPROFILENUMBER = "eumIProfileNumber"
    EUMICLIMATENUMBER = "eumIClimateNumber"
    EUMISPECTRALDESCRIPTION = "eumISpectralDescription"
    EUMISPREADINGFACTOR = "eumISpreadingFactor"
    EUMIREFPOINTNUMBER = "eumIRefPointNumber"
    EUMIWINDFRICTIONFACTOR = "eumIWindFrictionFactor"
    EUMIWAVEDISTURBANCECOEFFICIENT = "eumIWaveDisturbanceCoefficient"
    EUMITIMEFIRSTWAVEARRIVAL = "eumITimeFirstWaveArrival"
    EUMISURFACECURVATURE = "eumISurfaceCurvature"
    EUMIRADIATIONSTRESS = "eumIRadiationStress"
    EUMISPECTRALDENSITY = "eumISpectralDensity"
    EUMIFREQINTEGSPECTRALDENSITY = "eumIFreqIntegSpectralDensity"
    EUMIDIRECINTEGSPECTRALDENSITY = "eumIDirecIntegSpectralDensity"
    EUMIVISCOSITY = "eumIViscosity"
    EUMIDSD = "eumIDSD"
    EUMIBEACHPOSITION = "eumIBeachPosition"
    EUMITRENCHPOSITION = "eumITrenchPosition"
    EUMIGRAINDIAMETER = "eumIGrainDiameter"
    EUMIFALLVELOCITY = "eumIFallVelocity"
    EUMIGEODEVIATION = "eumIGeoDeviation"
    EUMIBREAKINGWAVE = "eumIBreakingWave"
    EUMIDUNEPOSITION = "eumIDunePosition"
    EUMICONTOURANGLE = "eumIContourAngle"
    EUMIFLOWDIRECTION = "eumIFlowDirection"
    EUMIBEDSLOPE = "eumIBedSlope"
    EUMISURFACEAREA = "eumISurfaceArea"
    EUMICATCHMENTAREA = "eumICatchmentArea"
    EUMIROUGHNESS = "eumIRoughness"
    EUMIACTIVEDEPTH = "eumIActiveDepth"
    EUMISEDIMENTGRADATION = "eumISedimentGradation"
    EUMIGROUNDWATERRECHARGE = "eumIGroundwaterRecharge"
    EUMISOLUTEFLUX = "eumISoluteFlux"
    EUMIRIVERSTRUCTGEO = "eumIRiverStructGeo"
    EUMIRIVERCHAINAGE = "eumIRiverChainage"
    EUMINONDIMFACTOR = "eumINonDimFactor"
    EUMINONDIMEXP = "eumINonDimExp"
    EUMISTORAGEDEPTH = "eumIStorageDepth"
    EUMIRIVERWIDTH = "eumIRiverWidth"
    EUMIFLOWROUTINGTIMECNST = "eumIFlowRoutingTimeCnst"
    EUMIFSTORDERRATEAD = "eumIFstOrderRateAD"
    EUMIFSTORDERRATEWQ = "eumIFstOrderRateWQ"
    EUMIERODEPOCOEF = "eumIEroDepoCoef"
    EUMISHEARSTRESS = "eumIShearStress"
    EUMIDISPCOEF = "eumIDispCoef"
    EUMIDISPFACT = "eumIDispFact"
    EUMISEDIMENTVOLUMEPERLENGTHUNIT = "eumISedimentVolumePerLengthUnit"
    EUMILATLONG = "eumILatLong"
    EUMISPECIFICGRAVITY = "eumISpecificGravity"
    EUMITRANSMISSIONCOEFFICIENT = "eumITransmissionCoefficient"
    EUMIREFLECTIONCOEFFICIENT = "eumIReflectionCoefficient"
    EUMIFRICTIONFACTOR = "eumIFrictionFactor"
    EUMIRADIATIONINTENSITY = "eumIRadiationIntensity"
    EUMIDURATION = "eumIDuration"
    EUMIRESPPRODPERAREA = "eumIRespProdPerArea"
    EUMIRESPPRODPERVOLUME = "eumIRespProdPerVolume"
    EUMISEDIMENTDEPTH = "eumISedimentDepth"
    EUMIANGLEOFRESPOSE = "eumIAngleOfRespose"
    EUMIHALFORDERRATEWQ = "eumIHalfOrderRateWQ"
    EUMIREARATIONCONSTANT = "eumIRearationConstant"
    EUMIDEPOSITIONRATE = "eumIDepositionRate"
    EUMIBODATRIVERBED = "eumIBODAtRiverBed"
    EUMICROPDEMAND = "eumICropDemand"
    EUMIIRRIGATEDAREA = "eumIIrrigatedArea"
    EUMILIVESTOCKDEMAND = "eumILiveStockDemand"
    EUMINUMBEROFLIVESTOCK = "eumINumberOfLiveStock"
    EUMITOTALGAS = "eumITotalGas"
    EUMIGROUNDWATERABSTRACTION = "eumIGroundWaterAbstraction"
    EUMIMELTINGCOEFFICIENT = "eumIMeltingCoefficient"
    EUMIRAINMELTINGCOEFFICIENT = "eumIRainMeltingCoefficient"
    EUMIELEVATION = "eumIElevation"
    EUMICROSSSECTIONXDATA = "eumICrossSectionXdata"
    EUMIVEGETATIONHEIGHT = "eumIVegetationHeight"
    EUMIGEOGRAPHICALCOORDINATE = "eumIGeographicalCoordinate"
    EUMIANGLE = "eumIAngle"
    EUMIITEMGEOMETRY0D = "eumIItemGeometry0D"
    EUMIITEMGEOMETRY1D = "eumIItemGeometry1D"
    EUMIITEMGEOMETRY2D = "eumIItemGeometry2D"
    EUMIITEMGEOMETRY3D = "eumIItemGeometry3D"
    EUMITEMPERATURELAPSERATE = "eumITemperatureLapseRate"
    EUMICORRECTIONOFPRECIPITATION = "eumICorrectionOfPrecipitation"
    EUMITEMPERATURECORRECTION = "eumITemperatureCorrection"
    EUMIPRECIPITATIONCORRECTION = "eumIPrecipitationCorrection"
    EUMIMAXWATER = "eumIMaxWater"
    EUMILOWERBASEFLOW = "eumILowerBaseflow"
    EUMIMASSFLUX = "eumIMassFlux"
    EUMIPRESSURESI = "eumIPressureSI"
    EUMITURBULENTKINETICENERGY = "eumITurbulentKineticEnergy"
    EUMIDISSIPATIONTKE = "eumIDissipationTKE"
    EUMISALTFLUX = "eumISaltFlux"
    EUMITEMPERATUREFLUX = "eumITemperatureFlux"
    EUMICONCENTRATIONNONDIM = "eumIConcentrationNonDim"
    EUMILATENTHEAT = "eumILatentHeat"
    EUMIHEATFLUX = "eumIHeatFlux"
    EUMISPECIFICHEAT = "eumISpecificHeat"
    EUMIVISIBILITY = "eumIVisibility"
    EUMIICETHICKNESS = "eumIIceThickness"
    EUMISTRUCTUREGEOMETRYPERTIME = "eumIStructureGeometryPerTime"
    EUMIDISCHARGEPERTIME = "eumIDischargePerTime"
    EUMIFETCHLENGTH = "eumIFetchLength"
    EUMIRUBBLEMOUND = "eumIRubbleMound"
    EUMIGRIDSPACING = "eumIGridSpacing"
    EUMITIMESTEP = "eumITimeStep"
    EUMILENGTHSCALE = "eumILengthScale"
    EUMIEROSIONCOEFFICIENTFACTOR = "eumIErosionCoefficientFactor"
    EUMIFRICTIONCOEFFIENT = "eumIFrictionCoeffient"
    EUMITRANSITIONRATE = "eumITransitionRate"
    EUMIDISTANCE = "eumIDistance"
    EUMITIMECORRECTIONATNOON = "eumITimeCorrectionAtNoon"
    EUMICRITICALVELOCITY = "eumICriticalVelocity"
    EUMILIGHTEXTINCTIONBACKGROUND = "eumILightExtinctionBackground"
    EUMIPARTICLEPRODUCTIONRATE = "eumIParticleProductionRate"
    EUMIFIRSTORDERGRAZINGRATEDEPENDANCE = "eumIFirstOrderGrazingRateDependance"
    EUMIRESUSPENSIONRATE = "eumIResuspensionRate"
    EUMIADSORPTIONCOEFFICIENT = "eumIAdsorptionCoefficient"
    EUMIDESORPTIONCOEFFICIENT = "eumIDesorptionCoefficient"
    EUMISEDIMENTATIONVELOCITY = "eumISedimentationVelocity"
    EUMIBOUNDARYLAYERTHICKNESS = "eumIBoundaryLayerThickness"
    EUMIDIFFUSIONCOEFFICIENT = "eumIDiffusionCoefficient"
    EUMIBIOCONCENTRATIONFACTOR = "eumIBioconcentrationFactor"
    EUMIFCOLICONCENTRATION = "eumIFcoliConcentration"
    EUMISPECIFICDISCHARGE = "eumISpecificDischarge"
    EUMIPRECIPITATION = "eumIPrecipitation"
    EUMISPECIFICPRECIPITATION = "eumISpecificPrecipitation"
    EUMIPOWER = "eumIPower"
    EUMICONVEYANCELOSS = "eumIConveyanceLoss"
    EUMIINFILTRATIONFLUX = "eumIInfiltrationFlux"
    EUMIEVAPORATIONFLUX = "eumIEvaporationFlux"
    EUMIGROUNDWATERABSTRACTIONFLUX = "eumIGroundWaterAbstractionFlux"
    EUMIFRACTION = "eumIFraction"
    EUMIYIELDFACTOR = "eumIYieldfactor"
    EUMISPECIFICSOLUTEFLUXPERAREA = "eumISpecificSoluteFluxPerArea"
    EUMICURRENTSPEED = "eumICurrentSpeed"
    EUMICURRENTDIRECTION = "eumICurrentDirection"
    EUMICURRENTMAGNITUDE = "eumICurrentMagnitude"
    EUMIPISTONPOSITION = "eumIPistonPosition"
    EUMISUBPISTONPOSITION = "eumISubPistonPosition"
    EUMISUPPISTONPOSITION = "eumISupPistonPosition"
    EUMIFLAPPOSITION = "eumIFlapPosition"
    EUMISUBFLAPPOSITION = "eumISubFlapPosition"
    EUMISUPFLAPPOSITION = "eumISupFlapPosition"
    EUMILENGTHZEROCROSSING = "eumILengthZeroCrossing"
    EUMITIMEZEROCROSSING = "eumITimeZeroCrossing"
    EUMILENGTHLOGGEDDATA = "eumILengthLoggedData"
    EUMIFORCELOGGEDDATA = "eumIForceLoggedData"
    EUMISPEEDLOGGEDDATA = "eumISpeedLoggedData"
    EUMIVOLUMEFLOWLOGGEDDATA = "eumIVolumeFlowLoggedData"
    EUMI2DSURFACEELEVATIONSPECTRUM = "eumI2DSurfaceElevationSpectrum"
    EUMI3DSURFACEELEVATIONSPECTRUM = "eumI3DSurfaceElevationSpectrum"
    EUMIDIRECTIONALSPREADINGFUNCTION = "eumIDirectionalSpreadingFunction"
    EUMIAUTOSPECTRUM = "eumIAutoSpectrum"
    EUMICROSSSPECTRUM = "eumICrossSpectrum"
    EUMICOHERENCESPECTRUM = "eumICoherenceSpectrum"
    EUMICOHERENTSPECTRUM = "eumICoherentSpectrum"
    EUMIFREQUENCYRESPONSESPECTRUM = "eumIFrequencyResponseSpectrum"
    EUMIPHASESPECTRUM = "eumIPhaseSpectrum"
    EUMIFIRCOEFFICIENT = "eumIFIRCoefficient"
    EUMIFOURIERACOEFFICIENT = "eumIFourierACoefficient"
    EUMIFOURIERBCOEFFICIENT = "eumIFourierBCoefficient"
    EUMIUVELOCITY = "eumIuVelocity"
    EUMIVVELOCITY = "eumIvVelocity"
    EUMIWVELOCITY = "eumIwVelocity"
    EUMIBEDTHICKNESS = "eumIBedThickness"
    EUMIDISPERSIONVELOCITYFACTOR = "eumIDispersionVelocityFactor"
    EUMIWINDSPEED = "eumIWindSpeed"
    EUMISHORECURRENTZONE = "eumIShoreCurrentZone"
    EUMIDEPTHOFWIND = "eumIDepthofWind"
    EUMIEMULSIFICATIONCONSTANTK1 = "eumIEmulsificationConstantK1"
    EUMIEMULSIFICATIONCONSTANTK2 = "eumIEmulsificationConstantK2"
    EUMILIGHTEXTINCTION = "eumILightExtinction"
    EUMIWATERDEPTH = "eumIWaterDepth"
    EUMIREFERENCESETTLINGVELOCITY = "eumIReferenceSettlingVelocity"
    EUMIPHASEERROR = "eumIPhaseError"
    EUMILEVELAMPLITUDEERROR = "eumILevelAmplitudeError"
    EUMIDISCHARGEAMPLITUDEERROR = "eumIDischargeAmplitudeError"
    EUMILEVELCORRECTION = "eumILevelCorrection"
    EUMIDISCHARGECORRECTION = "eumIDischargeCorrection"
    EUMILEVELSIMULATED = "eumILevelSimulated"
    EUMIDISCHARGESIMULATED = "eumIDischargeSimulated"
    EUMISUMMQCORRECTED = "eumISummQCorrected"
    EUMITIMESCALE = "eumITimeScale"
    EUMISPONGECOEFFICIENT = "eumISpongeCoefficient"
    EUMIPOROSITYCOEFFICIENT = "eumIPorosityCoefficient"
    EUMIFILTERCOEFFICIENT = "eumIFilterCoefficient"
    EUMISKEWNESS = "eumISkewness"
    EUMIASYMMETRY = "eumIAsymmetry"
    EUMIATILTNESS = "eumIAtiltness"
    EUMIKURTOSIS = "eumIKurtosis"
    EUMIAUXILIARYVARIABLEW = "eumIAuxiliaryVariableW"
    EUMIROLLERTHICKNESS = "eumIRollerThickness"
    EUMILINETHICKNESS = "eumILineThickness"
    EUMIMARKERSIZE = "eumIMarkerSize"
    EUMIROLLERCELERITY = "eumIRollerCelerity"
    EUMIENCROACHMENTOFFSET = "eumIEncroachmentOffset"
    EUMIENCROACHMENTPOSITION = "eumIEncroachmentPosition"
    EUMIENCROACHMENTWIDTH = "eumIEncroachmentWidth"
    EUMICONVEYANCEREDUCTION = "eumIConveyanceReduction"
    EUMIWATERLEVELCHANGE = "eumIWaterLevelChange"
    EUMIENERGYLEVELCHANGE = "eumIEnergyLevelChange"
    EUMIPARTICLEVELOCITYU = "eumIParticleVelocityU"
    EUMIPARTICLEVELOCITYV = "eumIParticleVelocityV"
    EUMIAREAFRACTION = "eumIAreaFraction"
    EUMICATCHMENTSLOPE = "eumICatchmentSlope"
    EUMIAVERAGELENGTH = "eumIAverageLength"
    EUMIPERSONEQUI = "eumIPersonEqui"
    EUMIINVERSEEXPO = "eumIInverseExpo"
    EUMITIMESHIFT = "eumITimeShift"
    EUMIATTENUATION = "eumIAttenuation"
    EUMIPOPULATION = "eumIPopulation"
    EUMIINDUSTRIALOUTPUT = "eumIIndustrialOutput"
    EUMIAGRICULTURALAREA = "eumIAgriculturalArea"
    EUMIPOPULATIONUSAGE = "eumIPopulationUsage"
    EUMIINDUSTRIALUSE = "eumIIndustrialUse"
    EUMIAGRICULTURALUSAGE = "eumIAgriculturalUsage"
    EUMILAYERTHICKNESS = "eumILayerThickness"
    EUMISNOWDEPTH = "eumISnowDepth"
    EUMISNOWCOVERPERCENTAGE = "eumISnowCoverPercentage"
    EUMIPRESSUREHEAD = "eumIPressureHead"
    EUMIKC = "eumIKC"
    EUMIAROOT = "eumIAroot"
    EUMIC1 = "eumIC1"
    EUMIC2 = "eumIC2"
    EUMIC3 = "eumIC3"
    EUMIIRRIGATIONDEMAND = "eumIIrrigationDemand"
    EUMIHYDRTRANSMISSIVITY = "eumIHydrTransmissivity"
    EUMIDARCYVELOCITY = "eumIDarcyVelocity"
    EUMIHYDRLEAKAGECOEFFICIENT = "eumIHydrLeakageCoefficient"
    EUMIHYDRCONDUCTANCE = "eumIHydrConductance"
    EUMIHEIGHTABOVEGROUND = "eumIHeightAboveGround"
    EUMIPUMPINGRATE = "eumIPumpingRate"
    EUMIDEPTHBELOWGROUND = "eumIDepthBelowGround"
    EUMICELLHEIGHT = "eumICellHeight"
    EUMIHEADGRADIENT = "eumIHeadGradient"
    EUMIGROUNDWATERFLOWVELOCITY = "eumIGroundWaterFlowVelocity"
    EUMIINTEGERCODE = "eumIIntegerCode"
    EUMIDRAINAGETIMECONSTANT = "eumIDrainageTimeConstant"
    EUMIHEADELEVATION = "eumIHeadElevation"
    EUMILENGTHERROR = "eumILengthError"
    EUMIELASTICSTORAGE = "eumIElasticStorage"
    EUMISPECIFICYIELD = "eumISpecificYield"
    EUMIEXCHANGERATE = "eumIExchangeRate"
    EUMIVOLUMETRICWATERCONTENT = "eumIVolumetricWaterContent"
    EUMISTORAGECHANGERATE = "eumIStorageChangeRate"
    EUMISEEPAGE = "eumISeepage"
    EUMIROOTDEPTH = "eumIRootDepth"
    EUMIRILLDEPTH = "eumIRillDepth"
    EUMILOGICAL = "eumILogical"
    EUMILAI = "eumILAI"
    EUMIIRRIGATIONRATE = "eumIIrrigationRate"
    EUMIIRRIGATIONINDEX = "eumIIrrigationIndex"
    EUMIINTERCEPTION = "eumIInterception"
    EUMIETRATE = "eumIETRate"
    EUMIEROSIONSURFACELOAD = "eumIErosionSurfaceLoad"
    EUMIEROSIONCONCENTRATION = "eumIErosionConcentration"
    EUMIEPSILONUZ = "eumIEpsilonUZ"
    EUMIDRAINAGE = "eumIDrainage"
    EUMIDEFICIT = "eumIDeficit"
    EUMICROPYIELD = "eumICropYield"
    EUMICROPTYPE = "eumICropType"
    EUMICROPSTRESS = "eumICropStress"
    EUMICROPSTAGE = "eumICropStage"
    EUMICROPLOSS = "eumICropLoss"
    EUMICROPINDEX = "eumICropIndex"
    EUMIAGE = "eumIAge"
    EUMIHYDRCONDUCTIVITY = "eumIHydrConductivity"
    EUMIPRINTSCALEEQUIVALENCE = "eumIPrintScaleEquivalence"
    EUMICONCENTRATION_1 = "eumIConcentration_1"
    EUMICONCENTRATION_2 = "eumIConcentration_2"
    EUMICONCENTRATION_3 = "eumIConcentration_3"
    EUMICONCENTRATION_4 = "eumIConcentration_4"
    EUMISEDIMENTDIAMETER = "eumISedimentDiameter"
    EUMIMEANWAVEDIRECTION = "eumIMeanWaveDirection"
    EUMIFLOWDIRECTION_1 = "eumIFlowDirection_1"
    EUMIAIRPRESSURE = "eumIAirPressure"
    EUMIDECAYFACTOR = "eumIDecayFactor"
    EUMISEDIMENTBEDDENSITY = "eumISedimentBedDensity"
    EUMIDISPERSIONCOEFFICIENT = "eumIDispersionCoefficient"
    EUMIFLOWVELOCITYPROFILE = "eumIFlowVelocityProfile"
    EUMIHABITATINDEX = "eumIHabitatIndex"
    EUMIANGLE2 = "eumIAngle2"
    EUMIHYDRAULICLENGTH = "eumIHydraulicLength"
    EUMISCSCATCHSLOPE = "eumISCSCatchSlope"
    EUMITURBIDITY_FTU = "eumITurbidity_FTU"
    EUMITURBIDITY_MGPERL = "eumITurbidity_MgPerL"
    EUMIBACTERIAFLOW = "eumIBacteriaFlow"
    EUMIBEDDISTRIBUTION = "eumIBedDistribution"
    EUMISURFACEELEVATIONATPADDLE = "eumISurfaceElevationAtPaddle"
    EUMIUNITHYDROGRAPHORDINATE = "eumIUnitHydrographOrdinate"
    EUMITRANSFERRATE = "eumITransferRate"
    EUMIRETURNPERIOD = "eumIReturnPeriod"
    EUMICONSTFALLVELOCITY = "eumIConstFallVelocity"
    EUMIDEPOSITIONCONCFLUX = "eumIDepositionConcFlux"
    EUMISETTLINGVELOCITYCOEF = "eumISettlingVelocityCoef"
    EUMIEROSIONCOEFFICIENT = "eumIErosionCoefficient"
    EUMIVOLUMEFLUX = "eumIVolumeFlux"
    EUMIPRECIPITATIONRATE = "eumIPrecipitationRate"
    EUMIEVAPORATIONRATE = "eumIEvaporationRate"
    EUMICOSPECTRUM = "eumICoSpectrum"
    EUMIQUADSPECTRUM = "eumIQuadSpectrum"
    EUMIPROPAGATIONDIRECTION = "eumIPropagationDirection"
    EUMIDIRECTIONALSPREADING = "eumIDirectionalSpreading"
    EUMIMASSPERUNITAREA = "eumIMassPerUnitArea"
    EUMIINCIDENTSPECTRUM = "eumIIncidentSpectrum"
    EUMIREFLECTEDSPECTRUM = "eumIReflectedSpectrum"
    EUMIREFLECTIONFUNCTION = "eumIReflectionFunction"
    EUMIBACTERIAFLUX = "eumIBacteriaFlux"
    EUMIHEADDIFFERENCE = "eumIHeadDifference"
    EUMIENERGY = "eumIenergy"
    EUMIDIRSTDDEV = "eumIDirStdDev"
    EUMIRAINFALLDEPTH = "eumIRainfallDepth"
    EUMIGROUNDWATERABSTRACTIONDEPTH = "eumIGroundWaterAbstractionDepth"
    EUMIEVAPORATIONINTESITY = "eumIEvaporationIntesity"
    EUMILONGITUDINALINFILTRATION = "eumILongitudinalInfiltration"
    EUMIPOLLUTANTLOAD = "eumIPollutantLoad"
    EUMIPRESSURE = "eumIPressure"
    EUMICOSTPERTIME = "eumICostPerTime"
    EUMIMASS = "eumIMass"
    EUMIMASSPERTIME = "eumIMassPerTime"
    EUMIMASSPERAREAPERTIME = "eumIMassPerAreaPerTime"
    EUMIKD = "eumIKd"
    EUMIPOROSITY = "eumIPorosity"
    EUMIHALFLIFE = "eumIHalfLife"
    EUMIDISPERSIVITY = "eumIDispersivity"
    EUMIFRICTIONCOEFFIENTCFW = "eumIFrictionCoeffientcfw"
    EUMIWAVEAMPLITUDE = "eumIWaveamplitude"
    EUMISEDIMENTGRAINDIAMETER = "eumISedimentGrainDiameter"
    EUMISEDIMENTSPILL = "eumISedimentSpill"
    EUMINUMBEROFPARTICLES = "eumINumberOfParticles"
    EUMIELLIPSOIDALHEIGHT = "eumIEllipsoidalHeight"
    EUMICLOUDINESS = "eumICloudiness"
    EUMIPROBABILITY = "eumIProbability"
    EUMIDISPERSANTACTIVITY = "eumIDispersantActivity"
    EUMIDREDGERATE = "eumIDredgeRate"
    EUMIDREDGESPILL = "eumIDredgeSpill"
    EUMICLEARNESSCOEFFICIENT = "eumIClearnessCoefficient"
    EUMIPROFILEORIENTATION = "eumIProfileOrientation"
    EUMIREDUCTIONFACTOR = "eumIReductionFactor"
    EUMIACTIVEBEACHHEIGHT = "eumIActiveBeachHeight"
    EUMIUPDATEPERIOD = "eumIUpdatePeriod"
    EUMIACCUMULATEDEROSION = "eumIAccumulatedErosion"
    EUMIEROSIONRATE = "eumIErosionRate"
    EUMINONDIMTRANSPORT = "eumINonDimTransport"
    EUMILOCALCOORDINATE = "eumILocalCoordinate"
    EUMIRADIIOFGYRATION = "eumIRadiiOfGyration"
    EUMIPERCENTAGE = "eumIPercentage"
    EUMILINECAPACITY = "eumILineCapacity"
    EUMIDIVERTEDDISCHARGE = "eumIDiverteddischarge"
    EUMIDEMANDCARRYOVERFRACTION = "eumIDemandcarryoverfraction"
    EUMIGROUNDWATERDEMAND = "eumIGroundwaterdemand"
    EUMIDAMCRESTLEVEL = "eumIDamcrestlevel"
    EUMISEEPAGEFLUX = "eumISeepageflux"
    EUMISEEPAGEFRACTION = "eumISeepagefraction"
    EUMIEVAPORATIONFRACTION = "eumIEvaporationfraction"
    EUMIRESIDENCETIME = "eumIResidencetime"
    EUMIOWNEDFRACTIONOFINFLOW = "eumIOwnedfractionofinflow"
    EUMIOWNEDFRACTIONOFVOLUME = "eumIOwnedfractionofvolume"
    EUMIREDUCTIONLEVEL = "eumIReductionlevel"
    EUMIREDUCTIONTHRESHOLD = "eumIReductionthreshold"
    EUMIREDUCTIONFRACTION = "eumIReductionfraction"
    EUMITOTALLOSSES = "eumITotalLosses"
    EUMICOUNTSPERLITER = "eumICountsPerLiter"
    EUMIASSIMILATIVECAPACITY = "eumIAssimilativeCapacity"
    EUMISTILLWATERDEPTH = "eumIStillWaterDepth"
    EUMITOTALWATERDEPTH = "eumITotalWaterDepth"
    EUMIMAXWAVEHEIGHT = "eumIMaxWaveHeight"
    EUMIICECONCENTRATION = "eumIIceConcentration"
    EUMIWINDFRICTIONSPEED = "eumIWindFrictionSpeed"
    EUMIROUGHNESSLENGTH = "eumIRoughnessLength"
    EUMIWINDDRAGCOEFFICIENT = "eumIWindDragCoefficient"
    EUMICHARNOCKCONSTANT = "eumICharnockConstant"
    EUMIBREAKINGPARAMETERGAMMA = "eumIBreakingParameterGamma"
    EUMITHRESHOLDPERIOD = "eumIThresholdPeriod"
    EUMICOURANTNUMBER = "eumICourantNumber"
    EUMITIMESTEPFACTOR = "eumITimeStepFactor"
    EUMIELEMENTLENGTH = "eumIElementLength"
    EUMIELEMENTAREA = "eumIElementArea"
    EUMIROLLERANGLE = "eumIRollerAngle"
    EUMIRATEBEDLEVELCHANGE = "eumIRateBedLevelChange"
    EUMIBEDLEVELCHANGE = "eumIBedLevelChange"
    EUMISEDIMENTTRANSPORTDIRECTION = "eumISedimentTransportDirection"
    EUMIWAVEACTIONDENSITY = "eumIWaveActionDensity"
    EUMIZEROMOMENTWAVEACTION = "eumIZeroMomentWaveAction"
    EUMIFIRSTMOMENTWAVEACTION = "eumIFirstMomentWaveAction"
    EUMIBEDMASS = "eumIBedMass"
    EUMIEPANETWATERQUALITY = "eumIEPANETWaterQuality"
    EUMIEPANETSTATUS = "eumIEPANETStatus"
    EUMIEPANETSETTING = "eumIEPANETSetting"
    EUMIEPANETREACTIONRATE = "eumIEPANETReactionRate"
    EUMIFRDISCHARGE = "eumIFRDischarge"
    EUMISRDISCHARGE = "eumISRDischarge"
    EUMIAVESEDITRANSPORTPERLENGTHUNIT = "eumIAveSediTransportPerLengthUnit"
    EUMIVALVESETTING = "eumIValveSetting"
    EUMIWAVEENERGYDENSITY = "eumIWaveEnergyDensity"
    EUMIWAVEENERGYDISTRIBUTION = "eumIWaveEnergyDistribution"
    EUMIWAVEENERGY = "eumIWaveEnergy"
    EUMIRADIATIONMELTINGCOEFFICIENT = "eumIRadiationMeltingCoefficient"
    EUMIRAINMELTINGCOEFFICIENTPERDEGREE = "eumIRainMeltingCoefficientPerDegree"
    EUMIEPANETFRICTION = "eumIEPANETFriction"
    EUMIWAVEACTIONDENSITYRATE = "eumIWaveActionDensityRate"
    EUMIELEMENTAREALONGLAT = "eumIElementAreaLongLat"
    EUMIELECTRICCURRENT = "eumIElectricCurrent"
    EUMIHEATFLUXRESISTANCE = "eumIHeatFluxResistance"
    EUMIABSOLUTEHUMIDITY = "eumIAbsoluteHumidity"
    EUMILENGTH = "eumILength"
    EUMIAREA = "eumIArea"
    EUMIVOLUME = "eumIVolume"
    EUMIELEMENTVOLUME = "eumIElementVolume"
    EUMIWAVEPOWER = "eumIWavePower"
    EUMIMOMENTOFINERTIA = "eumIMomentOfInertia"
    EUMITOPOGRAPHY = "eumITopography"
    EUMISCOURDEPTH = "eumIScourDepth"
    EUMISCOURWIDTH = "eumIScourWidth"
    EUMICOSTPERVOLUME = "eumICostPerVolume"
    EUMICOSTPERENERGY = "eumICostPerEnergy"
    EUMICOSTPERMASS = "eumICostPerMass"
    EUMIAPPLICATIONINTENSITY = "eumIApplicationIntensity"
    EUMICOST = "eumICost"
    EUMIVOLTAGE = "eumIVoltage"
    EUMINORMALVELOCITY = "eumINormalVelocity"
    EUMIGRAVITY = "eumIGravity"
    EUMIVESSELDISPLACEMENT = "eumIVesselDisplacement"
    EUMIHYDROSTATICMATRIX = "eumIHydrostaticMatrix"
    EUMIWAVENUMBER = "eumIWaveNumber"
    EUMIRADIATIONPOTENTIAL = "eumIRadiationPotential"
    EUMIADDEDMASSTT = "eumIAddedMassTT"
    EUMIRADIATIONDAMPING = "eumIRadiationDamping"
    EUMIFREQUENCY = "eumIFrequency"
    EUMISOUNDEXPOSURELEVEL = "eumISoundExposureLevel"
    EUMITRANSMISSIONLOSS = "eumITransmissionLoss"
    EUMIPH = "eumIpH"
    EUMIACOUSTICATTENUATION = "eumIAcousticAttenuation"
    EUMISOUNDSPEED = "eumISoundSpeed"
    EUMILEAKAGE = "eumILeakage"
    EUMIHEIGHTABOVEKEEL = "eumIHeightAboveKeel"
    EUMISUBMERGEDMASS = "eumISubmergedMass"
    EUMIDEFLECTION = "eumIDeflection"
    EUMILINEARDAMPINGCOEFFICIENT = "eumILinearDampingCoefficient"
    EUMIQUADRATICDAMPINGCOEFFICIENT = "eumIQuadraticDampingCoefficient"
    EUMIDAMPINGTT = "eumIDampingTT"
    EUMIRAOMOTION = "eumIRAOmotion"
    EUMIRAOROTATION = "eumIRAOrotation"
    EUMIADDEDMASSCOEFFICIENT = "eumIAddedMassCoefficient"
    EUMIELECTRICCONDUCTIVITY = "eumIElectricConductivity"
    EUMIADDEDMASSTR = "eumIAddedMassTR"
    EUMIADDEDMASSRT = "eumIAddedMassRT"
    EUMIADDEDMASSRR = "eumIAddedMassRR"
    EUMIDAMPINGTR = "eumIDampingTR"
    EUMIDAMPINGRT = "eumIDampingRT"
    EUMIDAMPINGRR = "eumIDampingRR"
    EUMIFENDERFORCE = "eumIFenderForce"
    EUMIFORCE = "eumIForce"
    EUMIMOMENT = "eumIMoment"
    EUMIREDUCEDPOLLUTANTLOAD = "eumIReducedPollutantLoad"
    EUMISIZEANDPOSITION = "eumISizeAndPosition"
    EUMIFRAMERATE = "eumIFrameRate"
    EUMIDYNAMICVISCOSITY = "eumIDynamicViscosity"
    EUMIGRIDROTATION = "eumIGridRotation"
    EUMIAGENTDENSITY = "eumIAgentDensity"
    EUMIEMITTERCOEFFICIENT = "eumIEmitterCoefficient"
    EUMIPIPEDIAMETER = "eumIPipeDiameter"
    EUMISPEED = "eumISpeed"
    EUMIVELOCITY = "eumIVelocity"
    EUMIDIRECTION = "eumIDirection"
    EUMIDISPLACEMENT = "eumIDisplacement"
    EUMIPOSITION = "eumIPosition"
    EUMIROTATION = "eumIRotation"
    EUMITORQUE = "eumITorque"
    EUMIOVERTOPPING = "eumIOvertopping"
    EUMIFLOWRATE = "eumIFlowRate"
    EUMIACCELERATION = "eumIAcceleration"
    EUMIDIMENSIONLESSACCELERATION = "eumIDimensionlessAcceleration"
    EUMITIME = "eumITime"
    EUMIRESISTANCE = "eumIResistance"
    EUMIAMOUNTOFSUBSTANCE = "eumIAmountOfSubstance"
    EUMIMOLARCONCENTRATION = "eumIMolarConcentration"
    EUMIMOLALCONCENTRATION = "eumIMolalConcentration"
    EUMISUSPSEDIMENTLOADPERAREA = "eumISuspSedimentLoadPerArea"
    EUMIBOLLARDFORCE = "eumIBollardForce"
    EUMIDISCHARGEPERPRESSURE = "eumIDischargePerPressure"
    EUMIROTATIONALSPEED = "eumIRotationalSpeed"
    EUMIINFILTRATIONPERAREA = "eumIInfiltrationPerArea"
    def __str__(self) -> str:
        return str(self.value)

ItemDefinitionV2Type = TypeVar("ItemDefinitionV2Type", bound="ItemDefinitionV2")

@attr.s(auto_attribs=True)
class ItemDefinitionV2(DataContract):
    i: int = None
    name: str = None
    unit: UnitIdV2 = None
    item: ItemIdV2 = None
    dataType: AttributeDataTypeV2 = None
    noDataValue: float = None
    hasLayers: str = None
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
    def from_dict(cls: ItemDefinitionV2Type, src_dict: Dict[str, Any]) -> ItemDefinitionV2Type:
        obj = ItemDefinitionV2()
        obj.load_dict(src_dict)
        return obj

TemporalDomainOutputGetDatasetOutputV2Type = TypeVar("TemporalDomainOutputGetDatasetOutputV2Type", bound="TemporalDomainOutputGetDatasetOutputV2")

@attr.s(auto_attribs=True)
class TemporalDomainOutputGetDatasetOutputV2(DataContract):
    id: str = None
    name: str = None
    spatialDomain: SpatialDomainOutputV2 = None
    temporalDomain: TemporalDomainOutputV2 = None
    items: List[ItemDefinitionV2] = None
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
    def from_dict(cls: TemporalDomainOutputGetDatasetOutputV2Type, src_dict: Dict[str, Any]) -> TemporalDomainOutputGetDatasetOutputV2Type:
        obj = TemporalDomainOutputGetDatasetOutputV2()
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

class MultidimensionalGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("md"), **kwargs)

    def Timeseries_query_V2(self, projectid, body, id) -> Response:
        """Query TS data

        Query
        POST /api/md/dataset/{id}/query-timeseries
        """
        return self.PostRequest(f"/api/md/dataset/{id}/query-timeseries", body, None, api_version="2", projectid=projectid, datasetid=id)

    def Timesteps_Query_V2(self, projectid, body, id) -> Response:
        """Query multidimensional data

        Query
        POST /api/md/dataset/{id}/query-timesteps
        """
        return self.PostRequest(f"/api/md/dataset/{id}/query-timesteps", body, None, api_version="2", projectid=projectid, datasetid=id)

    def GetQueryTimestepResultAsBinaryStream(self, projectid, body, id) -> Response:
        """Binary

        POST /api/md/dataset/{id}/binary-query-timesteps
        """
        return self.PostRequest(f"/api/md/dataset/{id}/binary-query-timesteps", body, None, projectid=projectid, datasetid=id)

    def GetQueryTimeseriesResultAsBinaryStream(self, projectid, body, id) -> Response:
        """Binary

        POST /api/md/dataset/{id}/binary-query-timeseries
        """
        return self.PostRequest(f"/api/md/dataset/{id}/binary-query-timeseries", body, None, projectid=projectid, datasetid=id)


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/multidimensional/v3
# DHI Multidimensional API - Version 3
# API for managing multidimensional data like gridded and meshed time series
# 3

class GridTypeV3(str, Enum):
    UNKNOWN = "Unknown"
    NODEALIGNED = "NodeAligned"
    CENTERALIGNED = "CenterAligned"
    BOTTOMLEFTALIGNED = "BottomLeftAligned"
    def __str__(self) -> str:
        return str(self.value)

TemporalElementV3Type = TypeVar("TemporalElementV3Type", bound="TemporalElementV3")

@attr.s(auto_attribs=True)
class TemporalElementV3(DataContract):
    i: int = None
    v: str = None
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
    def from_dict(cls: TemporalElementV3Type, src_dict: Dict[str, Any]) -> TemporalElementV3Type:
        obj = TemporalElementV3()
        obj.load_dict(src_dict)
        return obj

class VerticalOrientationV3(str, Enum):
    UP = "Up"
    DOWN = "Down"
    def __str__(self) -> str:
        return str(self.value)

VerticalDatumV3Type = TypeVar("VerticalDatumV3Type", bound="VerticalDatumV3")

@attr.s(auto_attribs=True)
class VerticalDatumV3(DataContract):
    origin: float = None
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
    def from_dict(cls: VerticalDatumV3Type, src_dict: Dict[str, Any]) -> VerticalDatumV3Type:
        obj = VerticalDatumV3()
        obj.load_dict(src_dict)
        return obj

class SpatialDomainTypeV3(str, Enum):
    UNDEFINED = "Undefined"
    MESH = "Mesh"
    EQUIDISTANTGRID2D = "EquidistantGrid2D"
    EQUIDISTANTGRID0D = "EquidistantGrid0D"
    EQUIDISTANTGRID1D = "EquidistantGrid1D"
    EQUIDISTANTGRID3D = "EquidistantGrid3D"
    NONEQUIDISTANTGRID2D = "NonequidistantGrid2D"
    NONEQUIDISTANTGRID1D = "NonequidistantGrid1D"
    NONEQUIDISTANTGRID3D = "NonequidistantGrid3D"
    CURVELINEARGRID2D = "CurveLinearGrid2D"
    CURVELINEARGRID1D = "CurveLinearGrid1D"
    CURVELINEARGRID3D = "CurveLinearGrid3D"
    def __str__(self) -> str:
        return str(self.value)

class AttributeDataTypeV3(str, Enum):
    TEXT = "Text"
    DATE = "Date"
    INT32 = "Int32"
    INT64 = "Int64"
    SINGLE = "Single"
    DOUBLE = "Double"
    INT16 = "Int16"
    def __str__(self) -> str:
        return str(self.value)

ProblemDetailsV3Type = TypeVar("ProblemDetailsV3Type", bound="ProblemDetailsV3")

@attr.s(auto_attribs=True)
class ProblemDetailsV3(DataContract):
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
    def from_dict(cls: ProblemDetailsV3Type, src_dict: Dict[str, Any]) -> ProblemDetailsV3Type:
        obj = ProblemDetailsV3()
        obj.load_dict(src_dict)
        return obj

ValidationProblemDetailsV3Type = TypeVar("ValidationProblemDetailsV3Type", bound="ValidationProblemDetailsV3")

@attr.s(auto_attribs=True)
class ValidationProblemDetailsV3(ProblemDetailsV3):
    errors: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ProblemDetailsV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ValidationProblemDetailsV3Type, src_dict: Dict[str, Any]) -> ValidationProblemDetailsV3Type:
        obj = ValidationProblemDetailsV3()
        obj.load_dict(src_dict)
        return obj

class ItemIdV3(str, Enum):
    EUMIITEMUNDEFINED = "eumIItemUndefined"
    EUMIWATERLEVEL = "eumIWaterLevel"
    EUMIDISCHARGE = "eumIDischarge"
    EUMIWINDVELOCITY = "eumIWindVelocity"
    EUMIWINDDIRECTION = "eumIWindDirection"
    EUMIRAINFALL = "eumIRainfall"
    EUMIEVAPORATION = "eumIEvaporation"
    EUMITEMPERATURE = "eumITemperature"
    EUMICONCENTRATION = "eumIConcentration"
    EUMIBACTERIACONC = "eumIBacteriaConc"
    EUMIRESISTFACTOR = "eumIResistFactor"
    EUMISEDIMENTTRANSPORT = "eumISedimentTransport"
    EUMIBOTTOMLEVEL = "eumIBottomLevel"
    EUMIBOTTOMLEVELCHANGE = "eumIBottomLevelChange"
    EUMISEDIMENTFRACTION = "eumISedimentFraction"
    EUMISEDIMENTFRACTIONCHANGE = "eumISedimentFractionChange"
    EUMIGATELEVEL = "eumIGateLevel"
    EUMIFLOWVELOCITY = "eumIFlowVelocity"
    EUMIDENSITY = "eumIDensity"
    EUMIDAMBREACHLEVEL = "eumIDamBreachLevel"
    EUMIDAMBREACHWIDTH = "eumIDamBreachWidth"
    EUMIDAMBREACHSLOPE = "eumIDamBreachSlope"
    EUMISUNSHINE = "eumISunShine"
    EUMISUNRADIATION = "eumISunRadiation"
    EUMIRELATIVEHUMIDITY = "eumIRelativeHumidity"
    EUMISALINITY = "eumISalinity"
    EUMISURFACESLOPE = "eumISurfaceSlope"
    EUMIFLOWAREA = "eumIFlowArea"
    EUMIFLOWWIDTH = "eumIFlowWidth"
    EUMIHYDRAULICRADIUS = "eumIHydraulicRadius"
    EUMIRESISTANCERADIUS = "eumIResistanceRadius"
    EUMIMANNINGSM = "eumIManningsM"
    EUMIMANNINGSN = "eumIManningsn"
    EUMICHEZYNO = "eumIChezyNo"
    EUMICONVEYANCE = "eumIConveyance"
    EUMIFROUDENO = "eumIFroudeNo"
    EUMIWATERVOLUME = "eumIWaterVolume"
    EUMIFLOODEDAREA = "eumIFloodedArea"
    EUMIWATERVOLUMEERROR = "eumIWaterVolumeError"
    EUMIACCWATERVOLUMEERROR = "eumIAccWaterVolumeError"
    EUMICOMPMASS = "eumICompMass"
    EUMICOMPMASSERROR = "eumICompMassError"
    EUMIACCCOMPMASSERROR = "eumIAccCompMassError"
    EUMIRELCOMPMASSERROR = "eumIRelCompMassError"
    EUMIRELACCCOMPMASSERROR = "eumIRelAccCompMassError"
    EUMICOMPDECAY = "eumICompDecay"
    EUMIACCCOMPDECAY = "eumIAccCompDecay"
    EUMICOMPTRANSP = "eumICompTransp"
    EUMIACCCOMPTRANSP = "eumIAccCompTransp"
    EUMICOMPDISPTRANSP = "eumICompDispTransp"
    EUMIACCCOMPDISPTRANSP = "eumIAccCompDispTransp"
    EUMICOMPCONVTRANSP = "eumICompConvTransp"
    EUMIACCCOMPCONVTRANSP = "eumIAccCompConvTransp"
    EUMIACCSEDIMENTTRANSPORT = "eumIAccSedimentTransport"
    EUMIDUNELENGTH = "eumIDuneLength"
    EUMIDUNEHEIGHT = "eumIDuneHeight"
    EUMIBEDSEDIMENTLOAD = "eumIBedSedimentLoad"
    EUMISUSPSEDIMENTLOAD = "eumISuspSedimentLoad"
    EUMIIRRIGATION = "eumIIrrigation"
    EUMIRELMOISTURECONT = "eumIRelMoistureCont"
    EUMIGROUNDWATERDEPTH = "eumIGroundWaterDepth"
    EUMISNOWCOVER = "eumISnowCover"
    EUMIINFILTRATION = "eumIInfiltration"
    EUMIRECHARGE = "eumIRecharge"
    EUMIOF1_FLOW = "eumIOF1_Flow"
    EUMIIF1_FLOW = "eumIIF1_Flow"
    EUMICAPILLARYFLUX = "eumICapillaryFlux"
    EUMISURFSTORAGE_OF1 = "eumISurfStorage_OF1"
    EUMISURFSTORAGE_OF0 = "eumISurfStorage_OF0"
    EUMISEDIMENTLAYER = "eumISedimentLayer"
    EUMIBEDLEVEL = "eumIBedLevel"
    EUMIRAINFALLINTENSITY = "eumIRainfallIntensity"
    EUMIPRODUCTIONRATE = "eumIproductionRate"
    EUMISEDIMENTMASS = "eumIsedimentMass"
    EUMIPRIMARYPRODUCTION = "eumIprimaryProduction"
    EUMIPRODPERVOLUME = "eumIprodPerVolume"
    EUMISECCHIDEPTH = "eumIsecchiDepth"
    EUMIACCSEDIMENTMASS = "eumIAccSedimentMass"
    EUMISEDIMENTMASSPERM = "eumISedimentMassPerM"
    EUMISURFACEELEVATION = "eumISurfaceElevation"
    EUMIBATHYMETRY = "eumIBathymetry"
    EUMIFLOWFLUX = "eumIFlowFlux"
    EUMIBEDLOADPERM = "eumIBedLoadPerM"
    EUMISUSPLOADPERM = "eumISuspLoadPerM"
    EUMISEDITRANSPORTPERM = "eumISediTransportPerM"
    EUMIWAVEHEIGHT = "eumIWaveHeight"
    EUMIWAVEPERIOD = "eumIWavePeriod"
    EUMIWAVEFREQUENCY = "eumIWaveFrequency"
    EUMIPOTENTIALEVAPRATE = "eumIPotentialEvapRate"
    EUMIRAINFALLRATE = "eumIRainfallRate"
    EUMIWATERDEMAND = "eumIWaterDemand"
    EUMIRETURNFLOWFRACTION = "eumIReturnFlowFraction"
    EUMILINEARROUTINGCOEF = "eumILinearRoutingCoef"
    EUMISPECIFICRUNOFF = "eumISpecificRunoff"
    EUMIMACHINEEFFICIENCY = "eumIMachineEfficiency"
    EUMITARGETPOWER = "eumITargetPower"
    EUMIWAVEDIRECTION = "eumIWaveDirection"
    EUMIACCSEDITRANSPORTPERM = "eumIAccSediTransportPerM"
    EUMISIGNIFICANTWAVEHEIGHT = "eumISignificantWaveHeight"
    EUMISHIELDSPARAMETER = "eumIShieldsParameter"
    EUMIANGLEBEDVELOCITY = "eumIAngleBedVelocity"
    EUMIPROFILENUMBER = "eumIProfileNumber"
    EUMICLIMATENUMBER = "eumIClimateNumber"
    EUMISPECTRALDESCRIPTION = "eumISpectralDescription"
    EUMISPREADINGFACTOR = "eumISpreadingFactor"
    EUMIREFPOINTNUMBER = "eumIRefPointNumber"
    EUMIWINDFRICTIONFACTOR = "eumIWindFrictionFactor"
    EUMIWAVEDISTURBANCECOEFFICIENT = "eumIWaveDisturbanceCoefficient"
    EUMITIMEFIRSTWAVEARRIVAL = "eumITimeFirstWaveArrival"
    EUMISURFACECURVATURE = "eumISurfaceCurvature"
    EUMIRADIATIONSTRESS = "eumIRadiationStress"
    EUMISPECTRALDENSITY = "eumISpectralDensity"
    EUMIFREQINTEGSPECTRALDENSITY = "eumIFreqIntegSpectralDensity"
    EUMIDIRECINTEGSPECTRALDENSITY = "eumIDirecIntegSpectralDensity"
    EUMIVISCOSITY = "eumIViscosity"
    EUMIDSD = "eumIDSD"
    EUMIBEACHPOSITION = "eumIBeachPosition"
    EUMITRENCHPOSITION = "eumITrenchPosition"
    EUMIGRAINDIAMETER = "eumIGrainDiameter"
    EUMIFALLVELOCITY = "eumIFallVelocity"
    EUMIGEODEVIATION = "eumIGeoDeviation"
    EUMIBREAKINGWAVE = "eumIBreakingWave"
    EUMIDUNEPOSITION = "eumIDunePosition"
    EUMICONTOURANGLE = "eumIContourAngle"
    EUMIFLOWDIRECTION = "eumIFlowDirection"
    EUMIBEDSLOPE = "eumIBedSlope"
    EUMISURFACEAREA = "eumISurfaceArea"
    EUMICATCHMENTAREA = "eumICatchmentArea"
    EUMIROUGHNESS = "eumIRoughness"
    EUMIACTIVEDEPTH = "eumIActiveDepth"
    EUMISEDIMENTGRADATION = "eumISedimentGradation"
    EUMIGROUNDWATERRECHARGE = "eumIGroundwaterRecharge"
    EUMISOLUTEFLUX = "eumISoluteFlux"
    EUMIRIVERSTRUCTGEO = "eumIRiverStructGeo"
    EUMIRIVERCHAINAGE = "eumIRiverChainage"
    EUMINONDIMFACTOR = "eumINonDimFactor"
    EUMINONDIMEXP = "eumINonDimExp"
    EUMISTORAGEDEPTH = "eumIStorageDepth"
    EUMIRIVERWIDTH = "eumIRiverWidth"
    EUMIFLOWROUTINGTIMECNST = "eumIFlowRoutingTimeCnst"
    EUMIFSTORDERRATEAD = "eumIFstOrderRateAD"
    EUMIFSTORDERRATEWQ = "eumIFstOrderRateWQ"
    EUMIERODEPOCOEF = "eumIEroDepoCoef"
    EUMISHEARSTRESS = "eumIShearStress"
    EUMIDISPCOEF = "eumIDispCoef"
    EUMIDISPFACT = "eumIDispFact"
    EUMISEDIMENTVOLUMEPERLENGTHUNIT = "eumISedimentVolumePerLengthUnit"
    EUMILATLONG = "eumILatLong"
    EUMISPECIFICGRAVITY = "eumISpecificGravity"
    EUMITRANSMISSIONCOEFFICIENT = "eumITransmissionCoefficient"
    EUMIREFLECTIONCOEFFICIENT = "eumIReflectionCoefficient"
    EUMIFRICTIONFACTOR = "eumIFrictionFactor"
    EUMIRADIATIONINTENSITY = "eumIRadiationIntensity"
    EUMIDURATION = "eumIDuration"
    EUMIRESPPRODPERAREA = "eumIRespProdPerArea"
    EUMIRESPPRODPERVOLUME = "eumIRespProdPerVolume"
    EUMISEDIMENTDEPTH = "eumISedimentDepth"
    EUMIANGLEOFRESPOSE = "eumIAngleOfRespose"
    EUMIHALFORDERRATEWQ = "eumIHalfOrderRateWQ"
    EUMIREARATIONCONSTANT = "eumIRearationConstant"
    EUMIDEPOSITIONRATE = "eumIDepositionRate"
    EUMIBODATRIVERBED = "eumIBODAtRiverBed"
    EUMICROPDEMAND = "eumICropDemand"
    EUMIIRRIGATEDAREA = "eumIIrrigatedArea"
    EUMILIVESTOCKDEMAND = "eumILiveStockDemand"
    EUMINUMBEROFLIVESTOCK = "eumINumberOfLiveStock"
    EUMITOTALGAS = "eumITotalGas"
    EUMIGROUNDWATERABSTRACTION = "eumIGroundWaterAbstraction"
    EUMIMELTINGCOEFFICIENT = "eumIMeltingCoefficient"
    EUMIRAINMELTINGCOEFFICIENT = "eumIRainMeltingCoefficient"
    EUMIELEVATION = "eumIElevation"
    EUMICROSSSECTIONXDATA = "eumICrossSectionXdata"
    EUMIVEGETATIONHEIGHT = "eumIVegetationHeight"
    EUMIGEOGRAPHICALCOORDINATE = "eumIGeographicalCoordinate"
    EUMIANGLE = "eumIAngle"
    EUMIITEMGEOMETRY0D = "eumIItemGeometry0D"
    EUMIITEMGEOMETRY1D = "eumIItemGeometry1D"
    EUMIITEMGEOMETRY2D = "eumIItemGeometry2D"
    EUMIITEMGEOMETRY3D = "eumIItemGeometry3D"
    EUMITEMPERATURELAPSERATE = "eumITemperatureLapseRate"
    EUMICORRECTIONOFPRECIPITATION = "eumICorrectionOfPrecipitation"
    EUMITEMPERATURECORRECTION = "eumITemperatureCorrection"
    EUMIPRECIPITATIONCORRECTION = "eumIPrecipitationCorrection"
    EUMIMAXWATER = "eumIMaxWater"
    EUMILOWERBASEFLOW = "eumILowerBaseflow"
    EUMIMASSFLUX = "eumIMassFlux"
    EUMIPRESSURESI = "eumIPressureSI"
    EUMITURBULENTKINETICENERGY = "eumITurbulentKineticEnergy"
    EUMIDISSIPATIONTKE = "eumIDissipationTKE"
    EUMISALTFLUX = "eumISaltFlux"
    EUMITEMPERATUREFLUX = "eumITemperatureFlux"
    EUMICONCENTRATIONNONDIM = "eumIConcentrationNonDim"
    EUMILATENTHEAT = "eumILatentHeat"
    EUMIHEATFLUX = "eumIHeatFlux"
    EUMISPECIFICHEAT = "eumISpecificHeat"
    EUMIVISIBILITY = "eumIVisibility"
    EUMIICETHICKNESS = "eumIIceThickness"
    EUMISTRUCTUREGEOMETRYPERTIME = "eumIStructureGeometryPerTime"
    EUMIDISCHARGEPERTIME = "eumIDischargePerTime"
    EUMIFETCHLENGTH = "eumIFetchLength"
    EUMIRUBBLEMOUND = "eumIRubbleMound"
    EUMIGRIDSPACING = "eumIGridSpacing"
    EUMITIMESTEP = "eumITimeStep"
    EUMILENGTHSCALE = "eumILengthScale"
    EUMIEROSIONCOEFFICIENTFACTOR = "eumIErosionCoefficientFactor"
    EUMIFRICTIONCOEFFIENT = "eumIFrictionCoeffient"
    EUMITRANSITIONRATE = "eumITransitionRate"
    EUMIDISTANCE = "eumIDistance"
    EUMITIMECORRECTIONATNOON = "eumITimeCorrectionAtNoon"
    EUMICRITICALVELOCITY = "eumICriticalVelocity"
    EUMILIGHTEXTINCTIONBACKGROUND = "eumILightExtinctionBackground"
    EUMIPARTICLEPRODUCTIONRATE = "eumIParticleProductionRate"
    EUMIFIRSTORDERGRAZINGRATEDEPENDANCE = "eumIFirstOrderGrazingRateDependance"
    EUMIRESUSPENSIONRATE = "eumIResuspensionRate"
    EUMIADSORPTIONCOEFFICIENT = "eumIAdsorptionCoefficient"
    EUMIDESORPTIONCOEFFICIENT = "eumIDesorptionCoefficient"
    EUMISEDIMENTATIONVELOCITY = "eumISedimentationVelocity"
    EUMIBOUNDARYLAYERTHICKNESS = "eumIBoundaryLayerThickness"
    EUMIDIFFUSIONCOEFFICIENT = "eumIDiffusionCoefficient"
    EUMIBIOCONCENTRATIONFACTOR = "eumIBioconcentrationFactor"
    EUMIFCOLICONCENTRATION = "eumIFcoliConcentration"
    EUMISPECIFICDISCHARGE = "eumISpecificDischarge"
    EUMIPRECIPITATION = "eumIPrecipitation"
    EUMISPECIFICPRECIPITATION = "eumISpecificPrecipitation"
    EUMIPOWER = "eumIPower"
    EUMICONVEYANCELOSS = "eumIConveyanceLoss"
    EUMIINFILTRATIONFLUX = "eumIInfiltrationFlux"
    EUMIEVAPORATIONFLUX = "eumIEvaporationFlux"
    EUMIGROUNDWATERABSTRACTIONFLUX = "eumIGroundWaterAbstractionFlux"
    EUMIFRACTION = "eumIFraction"
    EUMIYIELDFACTOR = "eumIYieldfactor"
    EUMISPECIFICSOLUTEFLUXPERAREA = "eumISpecificSoluteFluxPerArea"
    EUMICURRENTSPEED = "eumICurrentSpeed"
    EUMICURRENTDIRECTION = "eumICurrentDirection"
    EUMICURRENTMAGNITUDE = "eumICurrentMagnitude"
    EUMIPISTONPOSITION = "eumIPistonPosition"
    EUMISUBPISTONPOSITION = "eumISubPistonPosition"
    EUMISUPPISTONPOSITION = "eumISupPistonPosition"
    EUMIFLAPPOSITION = "eumIFlapPosition"
    EUMISUBFLAPPOSITION = "eumISubFlapPosition"
    EUMISUPFLAPPOSITION = "eumISupFlapPosition"
    EUMILENGTHZEROCROSSING = "eumILengthZeroCrossing"
    EUMITIMEZEROCROSSING = "eumITimeZeroCrossing"
    EUMILENGTHLOGGEDDATA = "eumILengthLoggedData"
    EUMIFORCELOGGEDDATA = "eumIForceLoggedData"
    EUMISPEEDLOGGEDDATA = "eumISpeedLoggedData"
    EUMIVOLUMEFLOWLOGGEDDATA = "eumIVolumeFlowLoggedData"
    EUMI2DSURFACEELEVATIONSPECTRUM = "eumI2DSurfaceElevationSpectrum"
    EUMI3DSURFACEELEVATIONSPECTRUM = "eumI3DSurfaceElevationSpectrum"
    EUMIDIRECTIONALSPREADINGFUNCTION = "eumIDirectionalSpreadingFunction"
    EUMIAUTOSPECTRUM = "eumIAutoSpectrum"
    EUMICROSSSPECTRUM = "eumICrossSpectrum"
    EUMICOHERENCESPECTRUM = "eumICoherenceSpectrum"
    EUMICOHERENTSPECTRUM = "eumICoherentSpectrum"
    EUMIFREQUENCYRESPONSESPECTRUM = "eumIFrequencyResponseSpectrum"
    EUMIPHASESPECTRUM = "eumIPhaseSpectrum"
    EUMIFIRCOEFFICIENT = "eumIFIRCoefficient"
    EUMIFOURIERACOEFFICIENT = "eumIFourierACoefficient"
    EUMIFOURIERBCOEFFICIENT = "eumIFourierBCoefficient"
    EUMIUVELOCITY = "eumIuVelocity"
    EUMIVVELOCITY = "eumIvVelocity"
    EUMIWVELOCITY = "eumIwVelocity"
    EUMIBEDTHICKNESS = "eumIBedThickness"
    EUMIDISPERSIONVELOCITYFACTOR = "eumIDispersionVelocityFactor"
    EUMIWINDSPEED = "eumIWindSpeed"
    EUMISHORECURRENTZONE = "eumIShoreCurrentZone"
    EUMIDEPTHOFWIND = "eumIDepthofWind"
    EUMIEMULSIFICATIONCONSTANTK1 = "eumIEmulsificationConstantK1"
    EUMIEMULSIFICATIONCONSTANTK2 = "eumIEmulsificationConstantK2"
    EUMILIGHTEXTINCTION = "eumILightExtinction"
    EUMIWATERDEPTH = "eumIWaterDepth"
    EUMIREFERENCESETTLINGVELOCITY = "eumIReferenceSettlingVelocity"
    EUMIPHASEERROR = "eumIPhaseError"
    EUMILEVELAMPLITUDEERROR = "eumILevelAmplitudeError"
    EUMIDISCHARGEAMPLITUDEERROR = "eumIDischargeAmplitudeError"
    EUMILEVELCORRECTION = "eumILevelCorrection"
    EUMIDISCHARGECORRECTION = "eumIDischargeCorrection"
    EUMILEVELSIMULATED = "eumILevelSimulated"
    EUMIDISCHARGESIMULATED = "eumIDischargeSimulated"
    EUMISUMMQCORRECTED = "eumISummQCorrected"
    EUMITIMESCALE = "eumITimeScale"
    EUMISPONGECOEFFICIENT = "eumISpongeCoefficient"
    EUMIPOROSITYCOEFFICIENT = "eumIPorosityCoefficient"
    EUMIFILTERCOEFFICIENT = "eumIFilterCoefficient"
    EUMISKEWNESS = "eumISkewness"
    EUMIASYMMETRY = "eumIAsymmetry"
    EUMIATILTNESS = "eumIAtiltness"
    EUMIKURTOSIS = "eumIKurtosis"
    EUMIAUXILIARYVARIABLEW = "eumIAuxiliaryVariableW"
    EUMIROLLERTHICKNESS = "eumIRollerThickness"
    EUMILINETHICKNESS = "eumILineThickness"
    EUMIMARKERSIZE = "eumIMarkerSize"
    EUMIROLLERCELERITY = "eumIRollerCelerity"
    EUMIENCROACHMENTOFFSET = "eumIEncroachmentOffset"
    EUMIENCROACHMENTPOSITION = "eumIEncroachmentPosition"
    EUMIENCROACHMENTWIDTH = "eumIEncroachmentWidth"
    EUMICONVEYANCEREDUCTION = "eumIConveyanceReduction"
    EUMIWATERLEVELCHANGE = "eumIWaterLevelChange"
    EUMIENERGYLEVELCHANGE = "eumIEnergyLevelChange"
    EUMIPARTICLEVELOCITYU = "eumIParticleVelocityU"
    EUMIPARTICLEVELOCITYV = "eumIParticleVelocityV"
    EUMIAREAFRACTION = "eumIAreaFraction"
    EUMICATCHMENTSLOPE = "eumICatchmentSlope"
    EUMIAVERAGELENGTH = "eumIAverageLength"
    EUMIPERSONEQUI = "eumIPersonEqui"
    EUMIINVERSEEXPO = "eumIInverseExpo"
    EUMITIMESHIFT = "eumITimeShift"
    EUMIATTENUATION = "eumIAttenuation"
    EUMIPOPULATION = "eumIPopulation"
    EUMIINDUSTRIALOUTPUT = "eumIIndustrialOutput"
    EUMIAGRICULTURALAREA = "eumIAgriculturalArea"
    EUMIPOPULATIONUSAGE = "eumIPopulationUsage"
    EUMIINDUSTRIALUSE = "eumIIndustrialUse"
    EUMIAGRICULTURALUSAGE = "eumIAgriculturalUsage"
    EUMILAYERTHICKNESS = "eumILayerThickness"
    EUMISNOWDEPTH = "eumISnowDepth"
    EUMISNOWCOVERPERCENTAGE = "eumISnowCoverPercentage"
    EUMIPRESSUREHEAD = "eumIPressureHead"
    EUMIKC = "eumIKC"
    EUMIAROOT = "eumIAroot"
    EUMIC1 = "eumIC1"
    EUMIC2 = "eumIC2"
    EUMIC3 = "eumIC3"
    EUMIIRRIGATIONDEMAND = "eumIIrrigationDemand"
    EUMIHYDRTRANSMISSIVITY = "eumIHydrTransmissivity"
    EUMIDARCYVELOCITY = "eumIDarcyVelocity"
    EUMIHYDRLEAKAGECOEFFICIENT = "eumIHydrLeakageCoefficient"
    EUMIHYDRCONDUCTANCE = "eumIHydrConductance"
    EUMIHEIGHTABOVEGROUND = "eumIHeightAboveGround"
    EUMIPUMPINGRATE = "eumIPumpingRate"
    EUMIDEPTHBELOWGROUND = "eumIDepthBelowGround"
    EUMICELLHEIGHT = "eumICellHeight"
    EUMIHEADGRADIENT = "eumIHeadGradient"
    EUMIGROUNDWATERFLOWVELOCITY = "eumIGroundWaterFlowVelocity"
    EUMIINTEGERCODE = "eumIIntegerCode"
    EUMIDRAINAGETIMECONSTANT = "eumIDrainageTimeConstant"
    EUMIHEADELEVATION = "eumIHeadElevation"
    EUMILENGTHERROR = "eumILengthError"
    EUMIELASTICSTORAGE = "eumIElasticStorage"
    EUMISPECIFICYIELD = "eumISpecificYield"
    EUMIEXCHANGERATE = "eumIExchangeRate"
    EUMIVOLUMETRICWATERCONTENT = "eumIVolumetricWaterContent"
    EUMISTORAGECHANGERATE = "eumIStorageChangeRate"
    EUMISEEPAGE = "eumISeepage"
    EUMIROOTDEPTH = "eumIRootDepth"
    EUMIRILLDEPTH = "eumIRillDepth"
    EUMILOGICAL = "eumILogical"
    EUMILAI = "eumILAI"
    EUMIIRRIGATIONRATE = "eumIIrrigationRate"
    EUMIIRRIGATIONINDEX = "eumIIrrigationIndex"
    EUMIINTERCEPTION = "eumIInterception"
    EUMIETRATE = "eumIETRate"
    EUMIEROSIONSURFACELOAD = "eumIErosionSurfaceLoad"
    EUMIEROSIONCONCENTRATION = "eumIErosionConcentration"
    EUMIEPSILONUZ = "eumIEpsilonUZ"
    EUMIDRAINAGE = "eumIDrainage"
    EUMIDEFICIT = "eumIDeficit"
    EUMICROPYIELD = "eumICropYield"
    EUMICROPTYPE = "eumICropType"
    EUMICROPSTRESS = "eumICropStress"
    EUMICROPSTAGE = "eumICropStage"
    EUMICROPLOSS = "eumICropLoss"
    EUMICROPINDEX = "eumICropIndex"
    EUMIAGE = "eumIAge"
    EUMIHYDRCONDUCTIVITY = "eumIHydrConductivity"
    EUMIPRINTSCALEEQUIVALENCE = "eumIPrintScaleEquivalence"
    EUMICONCENTRATION_1 = "eumIConcentration_1"
    EUMICONCENTRATION_2 = "eumIConcentration_2"
    EUMICONCENTRATION_3 = "eumIConcentration_3"
    EUMICONCENTRATION_4 = "eumIConcentration_4"
    EUMISEDIMENTDIAMETER = "eumISedimentDiameter"
    EUMIMEANWAVEDIRECTION = "eumIMeanWaveDirection"
    EUMIFLOWDIRECTION_1 = "eumIFlowDirection_1"
    EUMIAIRPRESSURE = "eumIAirPressure"
    EUMIDECAYFACTOR = "eumIDecayFactor"
    EUMISEDIMENTBEDDENSITY = "eumISedimentBedDensity"
    EUMIDISPERSIONCOEFFICIENT = "eumIDispersionCoefficient"
    EUMIFLOWVELOCITYPROFILE = "eumIFlowVelocityProfile"
    EUMIHABITATINDEX = "eumIHabitatIndex"
    EUMIANGLE2 = "eumIAngle2"
    EUMIHYDRAULICLENGTH = "eumIHydraulicLength"
    EUMISCSCATCHSLOPE = "eumISCSCatchSlope"
    EUMITURBIDITY_FTU = "eumITurbidity_FTU"
    EUMITURBIDITY_MGPERL = "eumITurbidity_MgPerL"
    EUMIBACTERIAFLOW = "eumIBacteriaFlow"
    EUMIBEDDISTRIBUTION = "eumIBedDistribution"
    EUMISURFACEELEVATIONATPADDLE = "eumISurfaceElevationAtPaddle"
    EUMIUNITHYDROGRAPHORDINATE = "eumIUnitHydrographOrdinate"
    EUMITRANSFERRATE = "eumITransferRate"
    EUMIRETURNPERIOD = "eumIReturnPeriod"
    EUMICONSTFALLVELOCITY = "eumIConstFallVelocity"
    EUMIDEPOSITIONCONCFLUX = "eumIDepositionConcFlux"
    EUMISETTLINGVELOCITYCOEF = "eumISettlingVelocityCoef"
    EUMIEROSIONCOEFFICIENT = "eumIErosionCoefficient"
    EUMIVOLUMEFLUX = "eumIVolumeFlux"
    EUMIPRECIPITATIONRATE = "eumIPrecipitationRate"
    EUMIEVAPORATIONRATE = "eumIEvaporationRate"
    EUMICOSPECTRUM = "eumICoSpectrum"
    EUMIQUADSPECTRUM = "eumIQuadSpectrum"
    EUMIPROPAGATIONDIRECTION = "eumIPropagationDirection"
    EUMIDIRECTIONALSPREADING = "eumIDirectionalSpreading"
    EUMIMASSPERUNITAREA = "eumIMassPerUnitArea"
    EUMIINCIDENTSPECTRUM = "eumIIncidentSpectrum"
    EUMIREFLECTEDSPECTRUM = "eumIReflectedSpectrum"
    EUMIREFLECTIONFUNCTION = "eumIReflectionFunction"
    EUMIBACTERIAFLUX = "eumIBacteriaFlux"
    EUMIHEADDIFFERENCE = "eumIHeadDifference"
    EUMIENERGY = "eumIenergy"
    EUMIDIRSTDDEV = "eumIDirStdDev"
    EUMIRAINFALLDEPTH = "eumIRainfallDepth"
    EUMIGROUNDWATERABSTRACTIONDEPTH = "eumIGroundWaterAbstractionDepth"
    EUMIEVAPORATIONINTESITY = "eumIEvaporationIntesity"
    EUMILONGITUDINALINFILTRATION = "eumILongitudinalInfiltration"
    EUMIPOLLUTANTLOAD = "eumIPollutantLoad"
    EUMIPRESSURE = "eumIPressure"
    EUMICOSTPERTIME = "eumICostPerTime"
    EUMIMASS = "eumIMass"
    EUMIMASSPERTIME = "eumIMassPerTime"
    EUMIMASSPERAREAPERTIME = "eumIMassPerAreaPerTime"
    EUMIKD = "eumIKd"
    EUMIPOROSITY = "eumIPorosity"
    EUMIHALFLIFE = "eumIHalfLife"
    EUMIDISPERSIVITY = "eumIDispersivity"
    EUMIFRICTIONCOEFFIENTCFW = "eumIFrictionCoeffientcfw"
    EUMIWAVEAMPLITUDE = "eumIWaveamplitude"
    EUMISEDIMENTGRAINDIAMETER = "eumISedimentGrainDiameter"
    EUMISEDIMENTSPILL = "eumISedimentSpill"
    EUMINUMBEROFPARTICLES = "eumINumberOfParticles"
    EUMIELLIPSOIDALHEIGHT = "eumIEllipsoidalHeight"
    EUMICLOUDINESS = "eumICloudiness"
    EUMIPROBABILITY = "eumIProbability"
    EUMIDISPERSANTACTIVITY = "eumIDispersantActivity"
    EUMIDREDGERATE = "eumIDredgeRate"
    EUMIDREDGESPILL = "eumIDredgeSpill"
    EUMICLEARNESSCOEFFICIENT = "eumIClearnessCoefficient"
    EUMIPROFILEORIENTATION = "eumIProfileOrientation"
    EUMIREDUCTIONFACTOR = "eumIReductionFactor"
    EUMIACTIVEBEACHHEIGHT = "eumIActiveBeachHeight"
    EUMIUPDATEPERIOD = "eumIUpdatePeriod"
    EUMIACCUMULATEDEROSION = "eumIAccumulatedErosion"
    EUMIEROSIONRATE = "eumIErosionRate"
    EUMINONDIMTRANSPORT = "eumINonDimTransport"
    EUMILOCALCOORDINATE = "eumILocalCoordinate"
    EUMIRADIIOFGYRATION = "eumIRadiiOfGyration"
    EUMIPERCENTAGE = "eumIPercentage"
    EUMILINECAPACITY = "eumILineCapacity"
    EUMIDIVERTEDDISCHARGE = "eumIDiverteddischarge"
    EUMIDEMANDCARRYOVERFRACTION = "eumIDemandcarryoverfraction"
    EUMIGROUNDWATERDEMAND = "eumIGroundwaterdemand"
    EUMIDAMCRESTLEVEL = "eumIDamcrestlevel"
    EUMISEEPAGEFLUX = "eumISeepageflux"
    EUMISEEPAGEFRACTION = "eumISeepagefraction"
    EUMIEVAPORATIONFRACTION = "eumIEvaporationfraction"
    EUMIRESIDENCETIME = "eumIResidencetime"
    EUMIOWNEDFRACTIONOFINFLOW = "eumIOwnedfractionofinflow"
    EUMIOWNEDFRACTIONOFVOLUME = "eumIOwnedfractionofvolume"
    EUMIREDUCTIONLEVEL = "eumIReductionlevel"
    EUMIREDUCTIONTHRESHOLD = "eumIReductionthreshold"
    EUMIREDUCTIONFRACTION = "eumIReductionfraction"
    EUMITOTALLOSSES = "eumITotalLosses"
    EUMICOUNTSPERLITER = "eumICountsPerLiter"
    EUMIASSIMILATIVECAPACITY = "eumIAssimilativeCapacity"
    EUMISTILLWATERDEPTH = "eumIStillWaterDepth"
    EUMITOTALWATERDEPTH = "eumITotalWaterDepth"
    EUMIMAXWAVEHEIGHT = "eumIMaxWaveHeight"
    EUMIICECONCENTRATION = "eumIIceConcentration"
    EUMIWINDFRICTIONSPEED = "eumIWindFrictionSpeed"
    EUMIROUGHNESSLENGTH = "eumIRoughnessLength"
    EUMIWINDDRAGCOEFFICIENT = "eumIWindDragCoefficient"
    EUMICHARNOCKCONSTANT = "eumICharnockConstant"
    EUMIBREAKINGPARAMETERGAMMA = "eumIBreakingParameterGamma"
    EUMITHRESHOLDPERIOD = "eumIThresholdPeriod"
    EUMICOURANTNUMBER = "eumICourantNumber"
    EUMITIMESTEPFACTOR = "eumITimeStepFactor"
    EUMIELEMENTLENGTH = "eumIElementLength"
    EUMIELEMENTAREA = "eumIElementArea"
    EUMIROLLERANGLE = "eumIRollerAngle"
    EUMIRATEBEDLEVELCHANGE = "eumIRateBedLevelChange"
    EUMIBEDLEVELCHANGE = "eumIBedLevelChange"
    EUMISEDIMENTTRANSPORTDIRECTION = "eumISedimentTransportDirection"
    EUMIWAVEACTIONDENSITY = "eumIWaveActionDensity"
    EUMIZEROMOMENTWAVEACTION = "eumIZeroMomentWaveAction"
    EUMIFIRSTMOMENTWAVEACTION = "eumIFirstMomentWaveAction"
    EUMIBEDMASS = "eumIBedMass"
    EUMIEPANETWATERQUALITY = "eumIEPANETWaterQuality"
    EUMIEPANETSTATUS = "eumIEPANETStatus"
    EUMIEPANETSETTING = "eumIEPANETSetting"
    EUMIEPANETREACTIONRATE = "eumIEPANETReactionRate"
    EUMIFRDISCHARGE = "eumIFRDischarge"
    EUMISRDISCHARGE = "eumISRDischarge"
    EUMIAVESEDITRANSPORTPERLENGTHUNIT = "eumIAveSediTransportPerLengthUnit"
    EUMIVALVESETTING = "eumIValveSetting"
    EUMIWAVEENERGYDENSITY = "eumIWaveEnergyDensity"
    EUMIWAVEENERGYDISTRIBUTION = "eumIWaveEnergyDistribution"
    EUMIWAVEENERGY = "eumIWaveEnergy"
    EUMIRADIATIONMELTINGCOEFFICIENT = "eumIRadiationMeltingCoefficient"
    EUMIRAINMELTINGCOEFFICIENTPERDEGREE = "eumIRainMeltingCoefficientPerDegree"
    EUMIEPANETFRICTION = "eumIEPANETFriction"
    EUMIWAVEACTIONDENSITYRATE = "eumIWaveActionDensityRate"
    EUMIELEMENTAREALONGLAT = "eumIElementAreaLongLat"
    EUMIELECTRICCURRENT = "eumIElectricCurrent"
    EUMIHEATFLUXRESISTANCE = "eumIHeatFluxResistance"
    EUMIABSOLUTEHUMIDITY = "eumIAbsoluteHumidity"
    EUMILENGTH = "eumILength"
    EUMIAREA = "eumIArea"
    EUMIVOLUME = "eumIVolume"
    EUMIELEMENTVOLUME = "eumIElementVolume"
    EUMIWAVEPOWER = "eumIWavePower"
    EUMIMOMENTOFINERTIA = "eumIMomentOfInertia"
    EUMITOPOGRAPHY = "eumITopography"
    EUMISCOURDEPTH = "eumIScourDepth"
    EUMISCOURWIDTH = "eumIScourWidth"
    EUMICOSTPERVOLUME = "eumICostPerVolume"
    EUMICOSTPERENERGY = "eumICostPerEnergy"
    EUMICOSTPERMASS = "eumICostPerMass"
    EUMIAPPLICATIONINTENSITY = "eumIApplicationIntensity"
    EUMICOST = "eumICost"
    EUMIVOLTAGE = "eumIVoltage"
    EUMINORMALVELOCITY = "eumINormalVelocity"
    EUMIGRAVITY = "eumIGravity"
    EUMIVESSELDISPLACEMENT = "eumIVesselDisplacement"
    EUMIHYDROSTATICMATRIX = "eumIHydrostaticMatrix"
    EUMIWAVENUMBER = "eumIWaveNumber"
    EUMIRADIATIONPOTENTIAL = "eumIRadiationPotential"
    EUMIADDEDMASSTT = "eumIAddedMassTT"
    EUMIRADIATIONDAMPING = "eumIRadiationDamping"
    EUMIFREQUENCY = "eumIFrequency"
    EUMISOUNDEXPOSURELEVEL = "eumISoundExposureLevel"
    EUMITRANSMISSIONLOSS = "eumITransmissionLoss"
    EUMIPH = "eumIpH"
    EUMIACOUSTICATTENUATION = "eumIAcousticAttenuation"
    EUMISOUNDSPEED = "eumISoundSpeed"
    EUMILEAKAGE = "eumILeakage"
    EUMIHEIGHTABOVEKEEL = "eumIHeightAboveKeel"
    EUMISUBMERGEDMASS = "eumISubmergedMass"
    EUMIDEFLECTION = "eumIDeflection"
    EUMILINEARDAMPINGCOEFFICIENT = "eumILinearDampingCoefficient"
    EUMIQUADRATICDAMPINGCOEFFICIENT = "eumIQuadraticDampingCoefficient"
    EUMIDAMPINGTT = "eumIDampingTT"
    EUMIRAOMOTION = "eumIRAOmotion"
    EUMIRAOROTATION = "eumIRAOrotation"
    EUMIADDEDMASSCOEFFICIENT = "eumIAddedMassCoefficient"
    EUMIELECTRICCONDUCTIVITY = "eumIElectricConductivity"
    EUMIADDEDMASSTR = "eumIAddedMassTR"
    EUMIADDEDMASSRT = "eumIAddedMassRT"
    EUMIADDEDMASSRR = "eumIAddedMassRR"
    EUMIDAMPINGTR = "eumIDampingTR"
    EUMIDAMPINGRT = "eumIDampingRT"
    EUMIDAMPINGRR = "eumIDampingRR"
    EUMIFENDERFORCE = "eumIFenderForce"
    EUMIFORCE = "eumIForce"
    EUMIMOMENT = "eumIMoment"
    EUMIREDUCEDPOLLUTANTLOAD = "eumIReducedPollutantLoad"
    EUMISIZEANDPOSITION = "eumISizeAndPosition"
    EUMIFRAMERATE = "eumIFrameRate"
    EUMIDYNAMICVISCOSITY = "eumIDynamicViscosity"
    EUMIGRIDROTATION = "eumIGridRotation"
    EUMIAGENTDENSITY = "eumIAgentDensity"
    EUMIEMITTERCOEFFICIENT = "eumIEmitterCoefficient"
    EUMIPIPEDIAMETER = "eumIPipeDiameter"
    EUMISPEED = "eumISpeed"
    EUMIVELOCITY = "eumIVelocity"
    EUMIDIRECTION = "eumIDirection"
    EUMIDISPLACEMENT = "eumIDisplacement"
    EUMIPOSITION = "eumIPosition"
    EUMIROTATION = "eumIRotation"
    EUMITORQUE = "eumITorque"
    EUMIOVERTOPPING = "eumIOvertopping"
    EUMIFLOWRATE = "eumIFlowRate"
    EUMIACCELERATION = "eumIAcceleration"
    EUMIDIMENSIONLESSACCELERATION = "eumIDimensionlessAcceleration"
    EUMITIME = "eumITime"
    EUMIRESISTANCE = "eumIResistance"
    EUMIAMOUNTOFSUBSTANCE = "eumIAmountOfSubstance"
    EUMIMOLARCONCENTRATION = "eumIMolarConcentration"
    EUMIMOLALCONCENTRATION = "eumIMolalConcentration"
    EUMISUSPSEDIMENTLOADPERAREA = "eumISuspSedimentLoadPerArea"
    EUMIBOLLARDFORCE = "eumIBollardForce"
    EUMIDISCHARGEPERPRESSURE = "eumIDischargePerPressure"
    EUMIROTATIONALSPEED = "eumIRotationalSpeed"
    EUMIINFILTRATIONPERAREA = "eumIInfiltrationPerArea"
    def __str__(self) -> str:
        return str(self.value)

class UnitIdV3(str, Enum):
    EUMUUNITUNDEFINED = "eumUUnitUndefined"
    EUMUMETER = "eumUmeter"
    EUMUKILOMETER = "eumUkilometer"
    EUMUMILLIMETER = "eumUmillimeter"
    EUMUFEET = "eumUfeet"
    EUMUINCH = "eumUinch"
    EUMUMILE = "eumUmile"
    EUMUYARD = "eumUyard"
    EUMUCENTIMETER = "eumUcentimeter"
    EUMUMICROMETER = "eumUmicrometer"
    EUMUNAUTICALMILE = "eumUnauticalmile"
    EUMUMILLIFEET = "eumUmillifeet"
    EUMULITERPERM2 = "eumULiterPerM2"
    EUMUMILLIMETERD50 = "eumUMilliMeterD50"
    EUMUINCHUS = "eumUinchUS"
    EUMUFEETUS = "eumUfeetUS"
    EUMUYARDUS = "eumUyardUS"
    EUMUMILEUS = "eumUmileUS"
    EUMUKILOGRAM = "eumUkilogram"
    EUMUGRAM = "eumUgram"
    EUMUMILLIGRAM = "eumUmilligram"
    EUMUMICROGRAM = "eumUmicrogram"
    EUMUTON = "eumUton"
    EUMUKILOTON = "eumUkiloton"
    EUMUMEGATON = "eumUmegaton"
    EUMUPOUND = "eumUPound"
    EUMUTONUS = "eumUtonUS"
    EUMUPERKILOGRAM = "eumUperKilogram"
    EUMUPERGRAM = "eumUperGram"
    EUMUPERMILLIGRAM = "eumUperMilligram"
    EUMUPERMICROGRAM = "eumUperMicrogram"
    EUMUPERTON = "eumUperTon"
    EUMUPERKILOTON = "eumUperKiloton"
    EUMUPERMEGATON = "eumUperMegaton"
    EUMUPERPOUND = "eumUperPound"
    EUMUPERTONUS = "eumUperTonUS"
    EUMUSEC = "eumUsec"
    EUMUMINUTE = "eumUminute"
    EUMUHOUR = "eumUhour"
    EUMUDAY = "eumUday"
    EUMUYEAR = "eumUyear"
    EUMUMONTH = "eumUmonth"
    EUMUMILLISEC = "eumUmillisec"
    EUMUM3 = "eumUm3"
    EUMULITER = "eumUliter"
    EUMUMILLILITER = "eumUmilliliter"
    EUMUFT3 = "eumUft3"
    EUMUGAL = "eumUgal"
    EUMUMGAL = "eumUmgal"
    EUMUKM3 = "eumUkm3"
    EUMUACFT = "eumUacft"
    EUMUMEGAGAL = "eumUMegaGal"
    EUMUMEGALITER = "eumUMegaLiter"
    EUMUTENTO6M3 = "eumUTenTo6m3"
    EUMUM3PERCURRENCY = "eumUm3PerCurrency"
    EUMUGALUK = "eumUgalUK"
    EUMUMEGAGALUK = "eumUMegagalUK"
    EUMUYDUS3 = "eumUydUS3"
    EUMUYARD3 = "eumUYard3"
    EUMUM3PERSEC = "eumUm3PerSec"
    EUMUFT3PERSEC = "eumUft3PerSec"
    EUMUMLPERDAY = "eumUMlPerDay"
    EUMUMGALPERDAY = "eumUMgalPerDay"
    EUMUACFTPERDAY = "eumUacftPerDay"
    EUMUM3PERYEAR = "eumUm3PerYear"
    EUMUGALPERDAYPERHEAD = "eumUGalPerDayPerHead"
    EUMULITERPERDAYPERHEAD = "eumULiterPerDayPerHead"
    EUMUM3PERSECPERHEAD = "eumUm3PerSecPerHead"
    EUMULITERPERPERSONPERDAY = "eumUliterPerPersonPerDay"
    EUMUM3PERDAY = "eumUm3PerDay"
    EUMUGALPERSEC = "eumUGalPerSec"
    EUMUGALPERDAY = "eumUGalPerDay"
    EUMUGALPERYEAR = "eumUGalPerYear"
    EUMUFT3PERDAY = "eumUft3PerDay"
    EUMUFT3PERYEAR = "eumUft3PerYear"
    EUMUM3PERMINUTE = "eumUm3PerMinute"
    EUMUFT3PERMIN = "eumUft3PerMin"
    EUMUGALPERMIN = "eumUGalPerMin"
    EUMULITERPERSEC = "eumUliterPerSec"
    EUMULITERPERMIN = "eumUliterPerMin"
    EUMUM3PERHOUR = "eumUm3PerHour"
    EUMUGALUKPERDAY = "eumUgalUKPerDay"
    EUMUMGALUKPERDAY = "eumUMgalUKPerDay"
    EUMUFT3PERDAYPERHEAD = "eumUft3PerDayPerHead"
    EUMUM3PERDAYPERHEAD = "eumUm3PerDayPerHead"
    EUMUGALUKPERSEC = "eumUGalUKPerSec"
    EUMUGALUKPERYEAR = "eumUGalUKPerYear"
    EUMUGALUKPERDAYPERHEAD = "eumUGalUKPerDayPerHead"
    EUMUYDUS3PERSEC = "eumUydUS3PerSec"
    EUMUYARD3PERSEC = "eumUyard3PerSec"
    EUMUFTUS3PERSEC = "eumUftUS3PerSec"
    EUMUFTUS3PERMIN = "eumUftUS3PerMin"
    EUMUFTUS3PERDAY = "eumUftUS3PerDay"
    EUMUFTUS3PERYEAR = "eumUftUS3PerYear"
    EUMUYARDUS3PERSEC = "eumUyardUS3PerSec"
    EUMULITERPERDAY = "eumUliterPerDay"
    EUMUMETERPERSEC = "eumUmeterPerSec"
    EUMUMILLIMETERPERHOUR = "eumUmillimeterPerHour"
    EUMUFEETPERSEC = "eumUfeetPerSec"
    EUMULITERPERSECPERKM2 = "eumUliterPerSecPerKm2"
    EUMUMILLIMETERPERDAY = "eumUmillimeterPerDay"
    EUMUACFTPERSECPERACRE = "eumUacftPerSecPerAcre"
    EUMUMETERPERDAY = "eumUmeterPerDay"
    EUMUFT3PERSECPERMI2 = "eumUft3PerSecPerMi2"
    EUMUMETERPERHOUR = "eumUmeterPerHour"
    EUMUFEETPERDAY = "eumUfeetPerDay"
    EUMUMILLIMETERPERMONTH = "eumUmillimeterPerMonth"
    EUMUINCHPERSEC = "eumUinchPerSec"
    EUMUMETERPERMINUTE = "eumUmeterPerMinute"
    EUMUFEETPERMINUTE = "eumUfeetPerMinute"
    EUMUINCHPERMINUTE = "eumUinchPerMinute"
    EUMUFEETPERHOUR = "eumUfeetPerHour"
    EUMUINCHPERHOUR = "eumUinchPerHour"
    EUMUMILLIMETERPERSECOND = "eumUmillimeterPerSecond"
    EUMUCMPERHOUR = "eumUcmPerHour"
    EUMUKNOT = "eumUknot"
    EUMUMILEPERHOUR = "eumUmilePerHour"
    EUMUKILOMETERPERHOUR = "eumUkilometerPerHour"
    EUMUACREFEETPERDAYPERACRE = "eumUAcreFeetPerDayPerAcre"
    EUMUCENTIMETERPERSECOND = "eumUCentiMeterPerSecond"
    EUMUCUBICFEETPERSECONDPERACRE = "eumUCubicFeetPerSecondPerAcre"
    EUMUCUBICMETERPERDAYPERHECTAR = "eumUCubicMeterPerDayPerHectar"
    EUMUCUBICMETERPERHOURPERHECTAR = "eumUCubicMeterPerHourPerHectar"
    EUMUCUBICMETERPERSECONDPERHECTAR = "eumUCubicMeterPerSecondPerHectar"
    EUMUGALLONPERMINUTEPERACRE = "eumUGallonPerMinutePerAcre"
    EUMULITERPERMINUTEPERHECTAR = "eumULiterPerMinutePerHectar"
    EUMULITERPERSECONDPERHECTAR = "eumULiterPerSecondPerHectar"
    EUMUMICROMETERPERSECOND = "eumUMicroMeterPerSecond"
    EUMUMILLIONGALPERDAYPERACRE = "eumUMillionGalPerDayPerAcre"
    EUMUMILLIONGALUKPERDAYPERACRE = "eumUMillionGalUKPerDayPerAcre"
    EUMUMILLIONLITERPERDAYPERHECTAR = "eumUMillionLiterPerDayPerHectar"
    EUMUINCHUSPERSECOND = "eumUinchUSPerSecond"
    EUMUFEETUSPERSECOND = "eumUfeetUSPerSecond"
    EUMUFEETUSPERDAY = "eumUfeetUSPerDay"
    EUMUINCHUSPERHOUR = "eumUinchUSPerHour"
    EUMUINCHUSPERMINUTE = "eumUinchUSPerMinute"
    EUMUMILLIMETERPERYEAR = "eumUmillimeterPerYear"
    EUMUCUBICFEETPERHOURPERACRE = "eumUCubicFeetPerHourPerAcre"
    EUMUCUBICFEETPERDAYPERACRE = "eumUCubicFeetPerDayPerAcre"
    EUMULITERPERHOURPERHECTAR = "eumULiterPerHourPerHectar"
    EUMULITERPERDAYPERHECTAR = "eumULiterPerDayPerHectar"
    EUMUMETERPERSECONDPERSECOND = "eumUMeterPerSecondPerSecond"
    EUMUFEETPERSECONDPERSECOND = "eumUFeetPerSecondPerSecond"
    EUMUKILOGRAMPERM3 = "eumUkiloGramPerM3"
    EUMUMICROGRAMPERM3 = "eumUmicroGramPerM3"
    EUMUMILLIGRAMPERM3 = "eumUmilliGramPerM3"
    EUMUGRAMPERM3 = "eumUgramPerM3"
    EUMUMICROGRAMPERL = "eumUmicroGramPerL"
    EUMUMILLIGRAMPERL = "eumUmilliGramPerL"
    EUMUGRAMPERL = "eumUgramPerL"
    EUMUPOUNDPERCUBICFEET = "eumUPoundPerCubicFeet"
    EUMUTONPERM3 = "eumUtonPerM3"
    EUMUPOUNDPERSQUAREFEET = "eumUPoundPerSquareFeet"
    EUMUTONPERM2 = "eumUtonPerM2"
    EUMUMICROGRAMPERM2 = "eumUmicroGramPerM2"
    EUMUPOUNDPERYDUS3 = "eumUPoundPerydUS3"
    EUMUPOUNDPERYARD3 = "eumUPoundPeryard3"
    EUMUPOUNDPERCUBICFEETUS = "eumUPoundPerCubicFeetUS"
    EUMUPOUNDPERSQUAREFEETUS = "eumUPoundPerSquareFeetUS"
    EUMUKILOGRAMPERMETERPERSECOND = "eumUKiloGramPerMeterPerSecond"
    EUMUPASCALSECOND = "eumUPascalSecond"
    EUMURADIAN = "eumUradian"
    EUMUDEGREE = "eumUdegree"
    EUMUDEGREENORTH50 = "eumUDegreeNorth50"
    EUMUDEGREESQUARED = "eumUdegreesquared"
    EUMUDEGREEPERMETER = "eumUdegreePerMeter"
    EUMURADIANPERMETER = "eumUradianPerMeter"
    EUMUDEGREEPERSECOND = "eumUdegreePerSecond"
    EUMURADIANPERSECOND = "eumUradianPerSecond"
    EUMUPERDAY = "eumUperDay"
    EUMUPERCENTPERDAY = "eumUpercentPerDay"
    EUMUHERTZ = "eumUhertz"
    EUMUPERHOUR = "eumUperHour"
    EUMUCURRENCYPERYEAR = "eumUcurrencyPerYear"
    EUMUPERSEC = "eumUperSec"
    EUMUBILLIONPERDAY = "eumUbillionPerDay"
    EUMUTRILLIONPERYEAR = "eumUtrillionPerYear"
    EUMUSQUAREMETERPERSECONDPERHECTAR = "eumUSquareMeterPerSecondPerHectar"
    EUMUSQUAREFEETPERSECONDPERACRE = "eumUSquareFeetPerSecondPerAcre"
    EUMUREVOLUTIONPERMINUTE = "eumURevolutionPerMinute"
    EUMUPERCENTPERHOUR = "eumUpercentPerHour"
    EUMUPERCENTPERMINUTE = "eumUpercentPerMinute"
    EUMUPERCENTPERSECOND = "eumUpercentPerSecond"
    EUMUREVOLUTIONPERSECOND = "eumURevolutionPerSecond"
    EUMUREVOLUTIONPERHOUR = "eumURevolutionPerHour"
    EUMUDEGREECELSIUS = "eumUdegreeCelsius"
    EUMUDEGREEFAHRENHEIT = "eumUdegreeFahrenheit"
    EUMUDEGREEKELVIN = "eumUdegreeKelvin"
    EUMUPERDEGREECELSIUS = "eumUperDegreeCelsius"
    EUMUPERDEGREEFAHRENHEIT = "eumUperDegreeFahrenheit"
    EUMUDELTADEGREECELSIUS = "eumUdeltaDegreeCelsius"
    EUMUDELTADEGREEFAHRENHEIT = "eumUdeltaDegreeFahrenheit"
    EUMUMILLPER100ML = "eumUmillPer100ml"
    EUMUPER100ML = "eumUPer100ml"
    EUMUPERLITER = "eumUperLiter"
    EUMUPERM3 = "eumUperM3"
    EUMUPERMILLILITER = "eumUperMilliliter"
    EUMUPERFT3 = "eumUperFt3"
    EUMUPERGALLON = "eumUperGallon"
    EUMUPERMILLIGALLON = "eumUperMilligallon"
    EUMUPERKM3 = "eumUperKm3"
    EUMUPERACFT = "eumUperAcft"
    EUMUPERMEGAGALLON = "eumUperMegagallon"
    EUMUPERMEGALITER = "eumUperMegaliter"
    EUMUPERGALLONUK = "eumUperGallonUK"
    EUMUPERMEGAGALLONUK = "eumUperMegagallonUK"
    EUMUPERYARDUS3 = "eumUperYardUS3"
    EUMUPERYARD3 = "eumUperYard3"
    EUMUSECPERMETER = "eumUSecPerMeter"
    EUMUM2 = "eumUm2"
    EUMUM3PERM = "eumUm3PerM"
    EUMUACRE = "eumUacre"
    EUMUFT2 = "eumUft2"
    EUMUHA = "eumUha"
    EUMUKM2 = "eumUkm2"
    EUMUMI2 = "eumUmi2"
    EUMUFT3PERFT = "eumUft3PerFt"
    EUMUFTUS2 = "eumUftUS2"
    EUMUYDUS2 = "eumUydUS2"
    EUMUMIUS2 = "eumUmiUS2"
    EUMUACREUS = "eumUacreUS"
    EUMUYDUS3PERYARDUS = "eumUydUS3PeryardUS"
    EUMUYARD3PERYARD = "eumUYard3PerYard"
    EUMUFTUS3PERFTUS = "eumUftUS3PerftUS"
    EUMULITERPERMETER = "eumUliterPerMeter"
    EUMUEPERM2PERDAY = "eumUEPerM2PerDay"
    EUMUTHOUSANDPERM2PERDAY = "eumUThousandPerM2PerDay"
    EUMUPERM2PERSEC = "eumUPerM2PerSec"
    EUMUMETER2ONE3RDPERSEC = "eumUMeter2One3rdPerSec"
    EUMUFEET2ONE3RDPERSEC = "eumUFeet2One3rdPerSec"
    EUMUSECPERMETER2ONE3RD = "eumUSecPerMeter2One3rd"
    EUMUSECPERFEET2ONE3RD = "eumUSecPerFeet2One3rd"
    EUMUMETER2ONEHALFPERSEC = "eumUMeter2OneHalfPerSec"
    EUMUFEET2ONEHALFPERSEC = "eumUFeet2OneHalfPerSec"
    EUMUFEETUS2ONEHALFPERSEC = "eumUFeetUS2OneHalfPerSec"
    EUMUKILOGRAMPERSEC = "eumUkilogramPerSec"
    EUMUMICROGRAMPERSEC = "eumUmicrogramPerSec"
    EUMUMILLIGRAMPERSEC = "eumUmilligramPerSec"
    EUMUGRAMPERSEC = "eumUgramPerSec"
    EUMUKILOGRAMPERHOUR = "eumUkilogramPerHour"
    EUMUKILOGRAMPERDAY = "eumUkilogramPerDay"
    EUMUGRAMPERDAY = "eumUgramPerDay"
    EUMUKILOGRAMPERYEAR = "eumUkilogramPerYear"
    EUMUGRAMPERMINUTE = "eumUGramPerMinute"
    EUMUKILOGRAMPERPERSONPERDAY = "eumUKiloGramPerPersonPerDay"
    EUMUKILOGRAMPERMINUTE = "eumUKilogramPerMinute"
    EUMUPOUNDPERDAY = "eumUPoundPerDay"
    EUMUPOUNDPERHOUR = "eumUPoundPerHour"
    EUMUPOUNDPERMINUTE = "eumUPoundPerMinute"
    EUMUPOUNDPERSECOND = "eumUPoundPerSecond"
    EUMUPOUNDPERPERSONPERDAY = "eumUPoundPerPersonPerDay"
    EUMUPOUNDPERYEAR = "eumUPoundPerYear"
    EUMUTONPERYEAR = "eumUTonPerYear"
    EUMUTONPERDAY = "eumUTonPerDay"
    EUMUTONPERSEC = "eumUTonPerSec"
    EUMUGRAMPERM2 = "eumUgramPerM2"
    EUMUKILOGRAMPERM = "eumUkilogramPerM"
    EUMUKILOGRAMPERM2 = "eumUkilogramPerM2"
    EUMUKILOGRAMPERHA = "eumUkilogramPerHa"
    EUMUMILLIGRAMPERM2 = "eumUmilligramPerM2"
    EUMUPOUNDPERACRE = "eumUPoundPerAcre"
    EUMUKILOGRAMPERKM2 = "eumUkilogramPerKm2"
    EUMUTONPERKM2 = "eumUtonPerKm2"
    EUMUGRAMPERKM2 = "eumUgramPerKm2"
    EUMUTONPERHA = "eumUtonPerHa"
    EUMUGRAMPERHA = "eumUgramPerHa"
    EUMUPOUNDPERMI2 = "eumUPoundPerMi2"
    EUMUKILOGRAMPERACRE = "eumUkilogramPerAcre"
    EUMUKILOGRAMPERSQUAREFEET = "eumUkilogramPerSquareFeet"
    EUMUKILOGRAMPERMI2 = "eumUkilogramPerMi2"
    EUMUTONPERACRE = "eumUtonPerAcre"
    EUMUTONPERSQUAREFEET = "eumUtonPerSquareFeet"
    EUMUTONPERMI2 = "eumUtonPerMi2"
    EUMUGRAMPERACRE = "eumUgramPerAcre"
    EUMUGRAMPERSQUAREFEET = "eumUgramPerSquareFeet"
    EUMUGRAMPERMI2 = "eumUgramPerMi2"
    EUMUPOUNDPERHA = "eumUPoundPerHa"
    EUMUPOUNDPERM2 = "eumUPoundPerM2"
    EUMUPOUNDPERKM2 = "eumUPoundPerKm2"
    EUMUMILLIGRAMPERHA = "eumUmilligramPerHa"
    EUMUMILLIGRAMPERKM2 = "eumUmilligramPerKm2"
    EUMUMILLIGRAMPERACRE = "eumUmilligramPerAcre"
    EUMUMILLIGRAMPERSQUAREFEET = "eumUmilligramPerSquareFeet"
    EUMUMILLIGRAMPERMI2 = "eumUmilligramPerMi2"
    EUMUPOUNDPERMETER = "eumUPoundPerMeter"
    EUMUTONPERMETER = "eumUtonPerMeter"
    EUMUGRAMPERM2PERDAY = "eumUgramPerM2PerDay"
    EUMUGRAMPERM2PERSEC = "eumUgramPerM2PerSec"
    EUMUKILOGRAMPERHAPERHOUR = "eumUkilogramPerHaPerHour"
    EUMUKILOGRAMPERM2PERSEC = "eumUkilogramPerM2PerSec"
    EUMUKILOGRAMPERHECTARPERDAY = "eumUKiloGramPerHectarPerDay"
    EUMUPOUNDPERACREPERDAY = "eumUPoundPerAcrePerDay"
    EUMUKILOGRAMPERM2PERDAY = "eumUkilogramPerM2PerDay"
    EUMUPOUNDPERFT2PERSEC = "eumUPoundPerFt2PerSec"
    EUMUGRAMPERM3PERHOUR = "eumUgramPerM3PerHour"
    EUMUGRAMPERM3PERDAY = "eumUgramPerM3PerDay"
    EUMUGRAMPERM3PERSEC = "eumUgramPerM3PerSec"
    EUMUMILLIGRAMPERLITERPERDAY = "eumUMilliGramPerLiterPerDay"
    EUMUM3PERSECPERM = "eumUm3PerSecPerM"
    EUMUM3PERYEARPERM = "eumUm3PerYearPerM"
    EUMUM2PERSEC = "eumUm2PerSec"
    EUMUFT2PERSEC = "eumUft2PerSec"
    EUMUM3PERSECPER10MM = "eumUm3PerSecPer10mm"
    EUMUFT3PERSECPERINCH = "eumUft3PerSecPerInch"
    EUMUM2PERHOUR = "eumUm2PerHour"
    EUMUM2PERDAY = "eumUm2PerDay"
    EUMUFT2PERHOUR = "eumUft2PerHour"
    EUMUFT2PERDAY = "eumUft2PerDay"
    EUMUGALUKPERDAYPERFEET = "eumUGalUKPerDayPerFeet"
    EUMUGALPERDAYPERFEET = "eumUGalPerDayPerFeet"
    EUMUGALPERMINUTEPERFEET = "eumUGalPerMinutePerFeet"
    EUMULITERPERDAYPERMETER = "eumULiterPerDayPerMeter"
    EUMULITERPERMINUTEPERMETER = "eumULiterPerMinutePerMeter"
    EUMULITERPERSECONDPERMETER = "eumULiterPerSecondPerMeter"
    EUMUFT3PERSECPERFT = "eumUft3PerSecPerFt"
    EUMUFT3PERHOURPERFT = "eumUft3PerHourPerFt"
    EUMUFT2PERSEC2 = "eumUft2PerSec2"
    EUMUCM3PERSECPERCM = "eumUcm3PerSecPerCm"
    EUMUMM3PERSECPERMM = "eumUmm3PerSecPerMm"
    EUMUFTUS3PERSECPERFTUS = "eumUftUS3PerSecPerFtUS"
    EUMUIN3PERSECPERIN = "eumUin3PerSecPerIn"
    EUMUINUS3PERSECPERINUS = "eumUinUS3PerSecPerInUS"
    EUMUYDUS3PERSECPERYDUS = "eumUydUS3PerSecPerydUS"
    EUMUYARD3PERSECPERYARD = "eumUyard3PerSecPeryard"
    EUMUYARD3PERYEARPERYARD = "eumUyard3PerYearPeryard"
    EUMUYDUS3PERYEARPERYDUS = "eumUydUS3PerYearPerydUS"
    EUMUM3PERHOURPERM = "eumUm3PerHourPerM"
    EUMUM3PERDAYPERM = "eumUm3PerDayPerM"
    EUMUFT3PERDAYPERFT = "eumUft3PerDayPerFt"
    EUMUMMPERDAY = "eumUmmPerDay"
    EUMUINPERDAY = "eumUinPerDay"
    EUMUM3PERKM2PERDAY = "eumUm3PerKm2PerDay"
    EUMUWATT = "eumUwatt"
    EUMUKWATT = "eumUkwatt"
    EUMUMWATT = "eumUmwatt"
    EUMUGWATT = "eumUgwatt"
    EUMUHORSEPOWER = "eumUHorsePower"
    EUMUPERMETER = "eumUperMeter"
    EUMUPERCENTPER100METER = "eumUpercentPer100meter"
    EUMUPERCENTPER100FEET = "eumUpercentPer100feet"
    EUMUPERFEET = "eumUperFeet"
    EUMUPERINCH = "eumUperInch"
    EUMUPERFEETUS = "eumUperFeetUS"
    EUMUPERINCHUS = "eumUperInchUS"
    EUMUM3PERS2 = "eumUm3PerS2"
    EUMUM2SECPERRAD = "eumUm2SecPerRad"
    EUMUM2PERRAD = "eumUm2PerRad"
    EUMUM2SEC = "eumUm2Sec"
    EUMUM2PERDEGREE = "eumUm2PerDegree"
    EUMUM2SEC2PERRAD = "eumUm2Sec2PerRad"
    EUMUM2PERSECPERRAD = "eumUm2PerSecPerRad"
    EUMUM2SECPERDEGREE = "eumUm2SecPerDegree"
    EUMUM2SEC2PERDEGREE = "eumUm2Sec2PerDegree"
    EUMUM2PERSECPERDEGREE = "eumUm2PerSecPerDegree"
    EUMUFT2PERSECPERRAD = "eumUft2PerSecPerRad"
    EUMUFT2PERSECPERDEGREE = "eumUft2PerSecPerDegree"
    EUMUFT2SEC2PERRAD = "eumUft2Sec2PerRad"
    EUMUFT2SEC2PERDEGREE = "eumUft2Sec2PerDegree"
    EUMUFT2SECPERRAD = "eumUft2SecPerRad"
    EUMUFT2SECPERDEGREE = "eumUft2SecPerDegree"
    EUMUFT2PERRAD = "eumUft2PerRad"
    EUMUFT2PERDEGREE = "eumUft2PerDegree"
    EUMUFT2SEC = "eumUft2Sec"
    EUMUMILLIGRAMPERL2ONEHALFPERDAY = "eumUmilliGramPerL2OneHalfPerDay"
    EUMUMILLIGRAMPERL2ONEHALFPERHOUR = "eumUmilliGramPerL2OneHalfPerHour"
    EUMUNEWTONPERSQRMETER = "eumUNewtonPerSqrMeter"
    EUMUKILONEWTONPERSQRMETER = "eumUkiloNewtonPerSqrMeter"
    EUMUPOUNDPERFEETPERSEC2 = "eumUPoundPerFeetPerSec2"
    EUMUNEWTONPERM3 = "eumUNewtonPerM3"
    EUMUKILONEWTONPERM3 = "eumUkiloNewtonPerM3"
    EUMUKILOGRAMM2 = "eumUkilogramM2"
    EUMUPOUNDSQRFEET = "eumUPoundSqrFeet"
    EUMUJOULE = "eumUJoule"
    EUMUKILOJOULE = "eumUkiloJoule"
    EUMUMEGAJOULE = "eumUmegaJoule"
    EUMUGIGAJOULE = "eumUgigaJoule"
    EUMUTERAJOULE = "eumUteraJoule"
    EUMUKILOWATTHOUR = "eumUKiloWattHour"
    EUMUWATTSECOND = "eumUWattSecond"
    EUMUPETAJOULE = "eumUpetaJoule"
    EUMUEXAJOULE = "eumUexaJoule"
    EUMUMEGAWATTHOUR = "eumUmegaWattHour"
    EUMUGIGAWATTHOUR = "eumUgigaWattHour"
    EUMUPERJOULE = "eumUperJoule"
    EUMUPERKILOJOULE = "eumUperKiloJoule"
    EUMUPERMEGAJOULE = "eumUperMegaJoule"
    EUMUPERGIGAJOULE = "eumUperGigaJoule"
    EUMUPERTERAJOULE = "eumUperTeraJoule"
    EUMUPERPETAJOULE = "eumUperPetaJoule"
    EUMUPEREXAJOULE = "eumUperExaJoule"
    EUMUPERKILOWATTHOUR = "eumUperKiloWattHour"
    EUMUPERWATTSECOND = "eumUperWattSecond"
    EUMUPERMEGAWATTHOUR = "eumUperMegaWattHour"
    EUMUPERGIGAWATTHOUR = "eumUperGigaWattHour"
    EUMUKILOJOULEPERM2PERHOUR = "eumUkiloJoulePerM2PerHour"
    EUMUKILOJOULEPERM2PERDAY = "eumUkiloJoulePerM2PerDay"
    EUMUMEGAJOULEPERM2PERDAY = "eumUmegaJoulePerM2PerDay"
    EUMUJOULEPERM2PERDAY = "eumUJoulePerM2PerDay"
    EUMUM2MMPERKILOJOULE = "eumUm2mmPerKiloJoule"
    EUMUM2MMPERMEGAJOULE = "eumUm2mmPerMegaJoule"
    EUMUMILLIMETERPERDEGREECELSIUSPERDAY = "eumUMilliMeterPerDegreeCelsiusPerDay"
    EUMUMILLIMETERPERDEGREECELSIUSPERHOUR = "eumUMilliMeterPerDegreeCelsiusPerHour"
    EUMUINCHPERDEGREEFAHRENHEITPERDAY = "eumUInchPerDegreeFahrenheitPerDay"
    EUMUINCHPERDEGREEFAHRENHEITPERHOUR = "eumUInchPerDegreeFahrenheitPerHour"
    EUMUPERDEGREECELSIUSPERDAY = "eumUPerDegreeCelsiusPerDay"
    EUMUPERDEGREECELSIUSPERHOUR = "eumUPerDegreeCelsiusPerHour"
    EUMUPERDEGREEFAHRENHEITPERDAY = "eumUPerDegreeFahrenheitPerDay"
    EUMUPERDEGREEFAHRENHEITPERHOUR = "eumUPerDegreeFahrenheitPerHour"
    EUMUDEGREECELSIUSPER100METER = "eumUDegreeCelsiusPer100meter"
    EUMUDEGREECELSIUSPER100FEET = "eumUDegreeCelsiusPer100feet"
    EUMUDEGREEFAHRENHEITPER100METER = "eumUDegreeFahrenheitPer100meter"
    EUMUDEGREEFAHRENHEITPER100FEET = "eumUDegreeFahrenheitPer100feet"
    EUMUPASCAL = "eumUPascal"
    EUMUHECTOPASCAL = "eumUhectoPascal"
    EUMUKILOPASCAL = "eumUkiloPascal"
    EUMUPSI = "eumUpsi"
    EUMUMEGAPASCAL = "eumUMegaPascal"
    EUMUMETRESOFWATER = "eumUMetresOfWater"
    EUMUFEETOFWATER = "eumUFeetOfWater"
    EUMUBAR = "eumUBar"
    EUMUMILLIBAR = "eumUmilliBar"
    EUMUMICROPASCAL = "eumUmicroPascal"
    EUMUDECIBAR = "eumUdeciBar"
    EUMUDB_RE_1MUPA2SECOND = "eumUdB_re_1muPa2second"
    EUMUDBPERLAMBDA = "eumUdBperLambda"
    EUMUPSU = "eumUPSU"
    EUMUPSUM3PERSEC = "eumUPSUM3PerSec"
    EUMUDEGREECELSIUSM3PERSEC = "eumUDegreeCelsiusM3PerSec"
    EUMUCONCNONDIMM3PERSEC = "eumUConcNonDimM3PerSec"
    EUMUPSUFT3PERSEC = "eumUPSUft3PerSec"
    EUMUDEGREEFAHRENHEITFT3PERSEC = "eumUDegreeFahrenheitFt3PerSec"
    EUMUM2PERSEC2 = "eumUm2PerSec2"
    EUMUM2PERSEC3 = "eumUm2PerSec3"
    EUMUFT2PERSEC3 = "eumUft2PerSec3"
    EUMUM2PERSEC3PERRAD = "eumUm2PerSec3PerRad"
    EUMUFT2PERSEC3PERRAD = "eumUft2PerSec3PerRad"
    EUMUJOULEPERKILOGRAM = "eumUJoulePerKilogram"
    EUMUWATTPERM2 = "eumUWattPerM2"
    EUMUJOULEKILOGRAMPERKELVIN = "eumUJouleKilogramPerKelvin"
    EUMUM3PERSEC2 = "eumUm3PerSec2"
    EUMUFT3PERSEC2 = "eumUft3PerSec2"
    EUMUACREFEETPERDAYPERSECOND = "eumUAcreFeetPerDayPerSecond"
    EUMUMILLIONGALUKPERDAYPERSECOND = "eumUMillionGalUKPerDayPerSecond"
    EUMUMILLIONGALPERDAYPERSECOND = "eumUMillionGalPerDayPerSecond"
    EUMUGALPERMINUTEPERSECOND = "eumUGalPerMinutePerSecond"
    EUMUCUBICMETERPERDAYPERSECOND = "eumUCubicMeterPerDayPerSecond"
    EUMUCUBICMETERPERHOURPERSECOND = "eumUCubicMeterPerHourPerSecond"
    EUMUMILLIONLITERPERDAYPERSECOND = "eumUMillionLiterPerDayPerSecond"
    EUMULITERPERMINUTEPERSECOND = "eumULiterPerMinutePerSecond"
    EUMULITERPERSECONDSQUARE = "eumULiterPerSecondSquare"
    EUMUM3PERGRAM = "eumUm3Pergram"
    EUMULITERPERGRAM = "eumULiterPergram"
    EUMUM3PERMILLIGRAM = "eumUm3PerMilligram"
    EUMUM3PERMICROGRAM = "eumUm3PerMicrogram"
    EUMUNEWTON = "eumUNewton"
    EUMUKILONEWTON = "eumUkiloNewton"
    EUMUMEGANEWTON = "eumUmegaNewton"
    EUMUMILLINEWTON = "eumUmilliNewton"
    EUMUKILOGRAMMETER = "eumUkilogramMeter"
    EUMUKILOGRAMMETER2 = "eumUkilogramMeter2"
    EUMUKILOGRAMMETERPERSECOND = "eumUkilogramMeterPerSecond"
    EUMUKILOGRAMMETER2PERSECOND = "eumUkilogramMeter2PerSecond"
    EUMUM2PERHERTZ = "eumUm2PerHertz"
    EUMUM2PERHERTZPERDEGREE = "eumUm2PerHertzPerDegree"
    EUMUM2PERHERTZPERRADIAN = "eumUm2PerHertzPerRadian"
    EUMUFT2PERHERTZ = "eumUft2PerHertz"
    EUMUFT2PERHERTZPERDEGREE = "eumUft2PerHertzPerDegree"
    EUMUFT2PERHERTZPERRADIAN = "eumUft2PerHertzPerRadian"
    EUMUM2PERHERTZ2 = "eumUm2PerHertz2"
    EUMUM2PERHERTZ2PERDEGREE = "eumUm2PerHertz2PerDegree"
    EUMUM2PERHERTZ2PERRADIAN = "eumUm2PerHertz2PerRadian"
    EUMULITERPERSECPERMETER = "eumUliterPerSecPerMeter"
    EUMULITERPERMINPERMETER = "eumUliterPerMinPerMeter"
    EUMUMEGALITERPERDAYPERMETER = "eumUMegaLiterPerDayPerMeter"
    EUMUM3PERHOURPERMETER = "eumUm3PerHourPerMeter"
    EUMUM3PERDAYPERMETER = "eumUm3PerDayPerMeter"
    EUMUFT3PERSECPERPSI = "eumUft3PerSecPerPsi"
    EUMUGALLONPERMINPERPSI = "eumUgallonPerMinPerPsi"
    EUMUMGALPERDAYPERPSI = "eumUMgalPerDayPerPsi"
    EUMUMGALUKPERDAYPERPSI = "eumUMgalUKPerDayPerPsi"
    EUMUACFTPERDAYPERPSI = "eumUacftPerDayPerPsi"
    EUMUM3PERHOURPERBAR = "eumUm3PerHourPerBar"
    EUMUKILOGRAMPERS2 = "eumUKilogramPerS2"
    EUMUM2PERKILOGRAM = "eumUm2Perkilogram"
    EUMUPERMETERPERSECOND = "eumUPerMeterPerSecond"
    EUMUMETERPERSECONDPERHECTAR = "eumUMeterPerSecondPerHectar"
    EUMUFEETPERSECONDPERACRE = "eumUFeetPerSecondPerAcre"
    EUMUPERSQUAREMETER = "eumUPerSquareMeter"
    EUMUPERACRE = "eumUPerAcre"
    EUMUPERHECTAR = "eumUPerHectar"
    EUMUPERKM2 = "eumUperKm2"
    EUMUPERCUBICMETER = "eumUPerCubicMeter"
    EUMUCURRENCYPERCUBICMETER = "eumUCurrencyPerCubicMeter"
    EUMUCURRENCYPERCUBICFEET = "eumUCurrencyPerCubicFeet"
    EUMUSQUAREMETERPERSECOND = "eumUSquareMeterPerSecond"
    EUMUSQUAREFEETPERSECOND = "eumUSquareFeetPerSecond"
    EUMUPERWATT = "eumUPerWatt"
    EUMUNEWTONMETER = "eumUNewtonMeter"
    EUMUKILONEWTONMETER = "eumUkiloNewtonMeter"
    EUMUMEGANEWTONMETER = "eumUmegaNewtonMeter"
    EUMUNEWTONMILLIMETER = "eumUNewtonMillimeter"
    EUMUNEWTONMETERSECOND = "eumUNewtonMeterSecond"
    EUMUNEWTONPERMETERPERSECOND = "eumUNewtonPerMeterPerSecond"
    EUMUMOLE = "eumUmole"
    EUMUMILLIMOLE = "eumUmillimole"
    EUMUMICROMOLE = "eumUmicromole"
    EUMUNANOMOLE = "eumUnanomole"
    EUMUMOLEPERLITER = "eumUmolePerLiter"
    EUMUMILLIMOLEPERLITER = "eumUmillimolePerLiter"
    EUMUMICROMOLEPERLITER = "eumUmicromolePerLiter"
    EUMUNANOMOLEPERLITER = "eumUnanomolePerLiter"
    EUMUMOLEPERM3 = "eumUmolePerM3"
    EUMUMILLIMOLEPERM3 = "eumUmillimolePerM3"
    EUMUMICROMOLEPERM3 = "eumUmicromolePerM3"
    EUMUMOLEPERKILOGRAM = "eumUmolePerKilogram"
    EUMUMILLIMOLEPERKILOGRAM = "eumUmillimolePerKilogram"
    EUMUMICROMOLEPERKILOGRAM = "eumUmicromolePerKilogram"
    EUMUNANOMOLEPERKILOGRAM = "eumUnanomolePerKilogram"
    EUMUONEPERONE = "eumUOnePerOne"
    EUMUPERCENT = "eumUPerCent"
    EUMUPERTHOUSAND = "eumUPerThousand"
    EUMUHOURSPERDAY = "eumUHoursPerDay"
    EUMUPERSON = "eumUPerson"
    EUMUGRAMPERGRAM = "eumUGramPerGram"
    EUMUGRAMPERKILOGRAM = "eumUGramPerKilogram"
    EUMUMILLIGRAMPERGRAM = "eumUMilligramPerGram"
    EUMUMILLIGRAMPERKILOGRAM = "eumUMilligramPerKilogram"
    EUMUMICROGRAMPERGRAM = "eumUMicrogramPerGram"
    EUMUKILOGRAMPERKILOGRAM = "eumUKilogramPerKilogram"
    EUMUM3PERM3 = "eumUM3PerM3"
    EUMULITERPERM3 = "eumULiterPerM3"
    EUMUINTCODE = "eumUintCode"
    EUMUMETERPERMETER = "eumUMeterPerMeter"
    EUMUPERMINUTE = "eumUperminute"
    EUMUPERMONTH = "eumUpermonth"
    EUMUPERYEAR = "eumUperyear"
    EUMUMILLILITERPERLITER = "eumUMilliliterPerLiter"
    EUMUMICROLITERPERLITER = "eumUMicroliterPerLiter"
    EUMUPERMILLION = "eumUPerMillion"
    EUMUGACCELERATION = "eumUgAcceleration"
    EUMUAMPERE = "eumUampere"
    EUMUMILLIAMPERE = "eumUMilliAmpere"
    EUMUMICROAMPERE = "eumUmicroAmpere"
    EUMUKILOAMPERE = "eumUkiloAmpere"
    EUMUMEGAAMPERE = "eumUmegaAmpere"
    EUMUVOLT = "eumUvolt"
    EUMUMILLIVOLT = "eumUmilliVolt"
    EUMUMICROVOLT = "eumUmicroVolt"
    EUMUKILOVOLT = "eumUkiloVolt"
    EUMUMEGAVOLT = "eumUmegaVolt"
    EUMUOHM = "eumUohm"
    EUMUKILOOHM = "eumUkiloOhm"
    EUMUMEGAOHM = "eumUmegaOhm"
    EUMUWATTPERMETER = "eumUWattPerMeter"
    EUMUKILOWATTPERMETER = "eumUkiloWattPerMeter"
    EUMUMEGAWATTPERMETER = "eumUmegaWattPerMeter"
    EUMUGIGAWATTPERMETER = "eumUgigaWattPerMeter"
    EUMUKILOWATTPERFEET = "eumUkiloWattPerFeet"
    EUMUSIEMENS = "eumUsiemens"
    EUMUMILLISIEMENS = "eumUmilliSiemens"
    EUMUMICROSIEMENS = "eumUmicroSiemens"
    EUMUSIEMENSPERMETER = "eumUsiemensPerMeter"
    EUMUMILLISIEMENSPERCENTIMETER = "eumUmilliSiemensPerCentimeter"
    EUMUMICROSIEMENSPERCENTIMETER = "eumUmicroSiemensPerCentimeter"
    EUMUKILOGRAMPERSECPERM = "eumUkilogramPerSecPerM"
    EUMUCENTIPOISE = "eumUCentipoise"
    EUMUPOUNDFORCESECPERSQRFT = "eumUPoundforceSecPerSqrFt"
    EUMUPOUNDFEETPERSEC = "eumUPoundFeetPerSec"
    def __str__(self) -> str:
        return str(self.value)

UnitV3Type = TypeVar("UnitV3Type", bound="UnitV3")

@attr.s(auto_attribs=True)
class UnitV3(DataContract):
    id: UnitIdV3 = None
    description: str = None
    abbreviation: str = None
    expression: str = None
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
    def from_dict(cls: UnitV3Type, src_dict: Dict[str, Any]) -> UnitV3Type:
        obj = UnitV3()
        obj.load_dict(src_dict)
        return obj

VerticalDomainOutputV3Type = TypeVar("VerticalDomainOutputV3Type", bound="VerticalDomainOutputV3")

@attr.s(auto_attribs=True)
class VerticalDomainOutputV3(DataContract):
    datum: VerticalDatumV3 = None
    maxZ: List[float] = None
    name: str = None
    orientation: VerticalOrientationV3 = None
    unit: UnitV3 = None
    layerCount: int = None
    layerDepths: List[float] = None
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
    def from_dict(cls: VerticalDomainOutputV3Type, src_dict: Dict[str, Any]) -> VerticalDomainOutputV3Type:
        obj = VerticalDomainOutputV3()
        obj.load_dict(src_dict)
        return obj

SpatialDomainOutputV3Type = TypeVar("SpatialDomainOutputV3Type", bound="SpatialDomainOutputV3")

@attr.s(auto_attribs=True)
class SpatialDomainOutputV3(DataContract):
    spatialDomainType: SpatialDomainTypeV3 = None
    verticalDomain: VerticalDomainOutputV3 = None
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
    def from_dict(cls: SpatialDomainOutputV3Type, src_dict: Dict[str, Any]) -> SpatialDomainOutputV3Type:
        obj = SpatialDomainOutputV3()
        obj.load_dict(src_dict)
        return obj

GridOutputV3Type = TypeVar("GridOutputV3Type", bound="GridOutputV3")

@attr.s(auto_attribs=True)
class GridOutputV3(SpatialDomainOutputV3):
    latitude: float = None
    longitude: float = None
    rotation: float = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = SpatialDomainOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: GridOutputV3Type, src_dict: Dict[str, Any]) -> GridOutputV3Type:
        obj = GridOutputV3()
        obj.load_dict(src_dict)
        return obj

NonequidistantGrid2DOutputV3Type = TypeVar("NonequidistantGrid2DOutputV3Type", bound="NonequidistantGrid2DOutputV3")

@attr.s(auto_attribs=True)
class NonequidistantGrid2DOutputV3(GridOutputV3):
    xCoordinates: List[float] = None
    yCoordinates: List[float] = None
    gridType: GridTypeV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GridOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: NonequidistantGrid2DOutputV3Type, src_dict: Dict[str, Any]) -> NonequidistantGrid2DOutputV3Type:
        obj = NonequidistantGrid2DOutputV3()
        obj.load_dict(src_dict)
        return obj

class TemporalDomainTypeV3(str, Enum):
    UNDEFINED = "Undefined"
    REGULAR = "Regular"
    IRREGULAR = "Irregular"
    def __str__(self) -> str:
        return str(self.value)

TemporalDomainOutputV3Type = TypeVar("TemporalDomainOutputV3Type", bound="TemporalDomainOutputV3")

@attr.s(auto_attribs=True)
class TemporalDomainOutputV3(DataContract):
    temporalDomainType: TemporalDomainTypeV3 = None
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
    def from_dict(cls: TemporalDomainOutputV3Type, src_dict: Dict[str, Any]) -> TemporalDomainOutputV3Type:
        obj = TemporalDomainOutputV3()
        obj.load_dict(src_dict)
        return obj

RegularTemporalDomainOutputV3Type = TypeVar("RegularTemporalDomainOutputV3Type", bound="RegularTemporalDomainOutputV3")

@attr.s(auto_attribs=True)
class RegularTemporalDomainOutputV3(TemporalDomainOutputV3):
    step: str = None
    start: str = None
    count: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalDomainOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: RegularTemporalDomainOutputV3Type, src_dict: Dict[str, Any]) -> RegularTemporalDomainOutputV3Type:
        obj = RegularTemporalDomainOutputV3()
        obj.load_dict(src_dict)
        return obj

ItemDefinitionV3Type = TypeVar("ItemDefinitionV3Type", bound="ItemDefinitionV3")

@attr.s(auto_attribs=True)
class ItemDefinitionV3(DataContract):
    i: int = None
    name: str = None
    unit: UnitIdV3 = None
    item: ItemIdV3 = None
    dataType: AttributeDataTypeV3 = None
    noDataValue: float = None
    hasLayers: str = None
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
    def from_dict(cls: ItemDefinitionV3Type, src_dict: Dict[str, Any]) -> ItemDefinitionV3Type:
        obj = ItemDefinitionV3()
        obj.load_dict(src_dict)
        return obj

TemporalDomainOutputGetDatasetOutputV3Type = TypeVar("TemporalDomainOutputGetDatasetOutputV3Type", bound="TemporalDomainOutputGetDatasetOutputV3")

@attr.s(auto_attribs=True)
class TemporalDomainOutputGetDatasetOutputV3(DataContract):
    id: str = None
    name: str = None
    spatialDomain: SpatialDomainOutputV3 = None
    temporalDomain: TemporalDomainOutputV3 = None
    items: List[ItemDefinitionV3] = None
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
    def from_dict(cls: TemporalDomainOutputGetDatasetOutputV3Type, src_dict: Dict[str, Any]) -> TemporalDomainOutputGetDatasetOutputV3Type:
        obj = TemporalDomainOutputGetDatasetOutputV3()
        obj.load_dict(src_dict)
        return obj

ItemDefinitionUpdateV3Type = TypeVar("ItemDefinitionUpdateV3Type", bound="ItemDefinitionUpdateV3")

@attr.s(auto_attribs=True)
class ItemDefinitionUpdateV3(DataContract):
    name: str = None
    unit: UnitIdV3 = None
    item: ItemIdV3 = None
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
    def from_dict(cls: ItemDefinitionUpdateV3Type, src_dict: Dict[str, Any]) -> ItemDefinitionUpdateV3Type:
        obj = ItemDefinitionUpdateV3()
        obj.load_dict(src_dict)
        return obj

IrregularTemporalDomainOutputV3Type = TypeVar("IrregularTemporalDomainOutputV3Type", bound="IrregularTemporalDomainOutputV3")

@attr.s(auto_attribs=True)
class IrregularTemporalDomainOutputV3(TemporalDomainOutputV3):
    times: List[TemporalElementV3] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalDomainOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: IrregularTemporalDomainOutputV3Type, src_dict: Dict[str, Any]) -> IrregularTemporalDomainOutputV3Type:
        obj = IrregularTemporalDomainOutputV3()
        obj.load_dict(src_dict)
        return obj

EquidistantGrid2DOutputV3Type = TypeVar("EquidistantGrid2DOutputV3Type", bound="EquidistantGrid2DOutputV3")

@attr.s(auto_attribs=True)
class EquidistantGrid2DOutputV3(GridOutputV3):
    x0: float = None
    dx: float = None
    nx: int = None
    y0: float = None
    dy: float = None
    ny: int = None
    gridType: GridTypeV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GridOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: EquidistantGrid2DOutputV3Type, src_dict: Dict[str, Any]) -> EquidistantGrid2DOutputV3Type:
        obj = EquidistantGrid2DOutputV3()
        obj.load_dict(src_dict)
        return obj

class MultidimensionalGenClientV3(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("md"), **kwargs)

    def GetDatasetV3(self, projectid, id) -> Response:
        """Get dataset details

        DatasetControler
        GET /api/md/dataset/{id}
        """
        return self.GetRequest(f"/api/md/dataset/{id}", None, api_version="3", projectid=projectid, datasetid=id)

    def UpdateItemDefinition(self, projectid, body, id, index) -> Response:
        """DatasetControler

        PATCH /api/md/dataset/{id}/item/{index}
        """
        return self.PatchRequest(f"/api/md/dataset/{id}/item/{index}", body, None, api_version="3", projectid=projectid, datasetid=id)

    def DeleteTimestep(self, projectid, id, timestepindex=None) -> Response:
        """DatasetControler

        DELETE /api/md/dataset/{id}/timestep
        """
        queryparams = self.GetQueryParams(timestepIndex=timestepindex)
        return self.DeleteRequest(f"/api/md/dataset/{id}/timestep", queryparams, api_version="3", projectid=projectid, datasetid=id)
