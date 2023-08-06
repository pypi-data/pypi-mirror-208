# Generated using openapi2py.py
# openapi2py.py "--classname" "MetadataGenClientV" "-t" "PathAction:type:str:PathAction,PathActionDelete:type:str:PathActionDelete,PathActionCreate:type:str:PathActionCreate,PathActionCreateIfNotExists:type:str:PathActionCreateIfNotExists" "-d" "GetServiceIds" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\metadatagen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v1" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v2" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v3"
# 2022-01-13 15:05:56.936055Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v1
# DHI Water Data Metadata API - Version 1
# API for managing projects and datasets inside projects
# 1

class ConverterFilterV1(str, Enum):
    ALL = "All"
    FILE = "File"
    DEDICATED = "Dedicated"
    def __str__(self) -> str:
        return str(self.value)

DatasetTransferInputV1Type = TypeVar("DatasetTransferInputV1Type", bound="DatasetTransferInputV1")

@attr.s(auto_attribs=True)
class DatasetTransferInputV1(DataContract):
    name: str = None
    description: str = None
    metadata: str = None
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
    def from_dict(cls: DatasetTransferInputV1Type, src_dict: Dict[str, Any]) -> DatasetTransferInputV1Type:
        obj = DatasetTransferInputV1()
        obj.load_dict(src_dict)
        return obj

class UnitIdV1(str, Enum):
    EUMUMETER = "eumUmeter"
    EUMUKILOMETER = "eumUkilometer"
    EUMUMILLIMETER = "eumUmillimeter"
    EUMUINCH = "eumUinch"
    EUMUFEET = "eumUfeet"
    EUMUYARD = "eumUyard"
    EUMUMILE = "eumUmile"
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
    EUMUPERCENTPERMINUTE = "eumUpercentPerMinute"
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
    EUMUUNITUNDEFINED = "eumUUnitUndefined"
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

SpatialFilterV1Type = TypeVar("SpatialFilterV1Type", bound="SpatialFilterV1")

@attr.s(auto_attribs=True)
class SpatialFilterV1(DataContract):
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
    def from_dict(cls: SpatialFilterV1Type, src_dict: Dict[str, Any]) -> SpatialFilterV1Type:
        obj = SpatialFilterV1()
        obj.load_dict(src_dict)
        return obj

class ImportDestinationV1(str, Enum):
    DEDICATED = "Dedicated"
    PROJECT = "Project"
    def __str__(self) -> str:
        return str(self.value)

UploadInputV1Type = TypeVar("UploadInputV1Type", bound="UploadInputV1")

@attr.s(auto_attribs=True)
class UploadInputV1(DataContract):
    format: str = None
    projectId: str = None
    appendDatasetId: str = None
    uploadUrl: str = None
    fileName: str = None
    srid: int = None
    arguments: str = None
    destinations: List[ImportDestinationV1] = None
    datasetImportData: DatasetTransferInputV1 = None
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
    def from_dict(cls: UploadInputV1Type, src_dict: Dict[str, Any]) -> UploadInputV1Type:
        obj = UploadInputV1()
        obj.load_dict(src_dict)
        return obj

StorageUsageOutputV1Type = TypeVar("StorageUsageOutputV1Type", bound="StorageUsageOutputV1")

@attr.s(auto_attribs=True)
class StorageUsageOutputV1(DataContract):
    blobStorageUsedKB: int = None
    parsedStorageUsedKB: int = None
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
    def from_dict(cls: StorageUsageOutputV1Type, src_dict: Dict[str, Any]) -> StorageUsageOutputV1Type:
        obj = StorageUsageOutputV1()
        obj.load_dict(src_dict)
        return obj

GetCustomerStorageUsageOutputV1Type = TypeVar("GetCustomerStorageUsageOutputV1Type", bound="GetCustomerStorageUsageOutputV1")

@attr.s(auto_attribs=True)
class GetCustomerStorageUsageOutputV1(DataContract):
    customerId: str = None
    totalUsage: StorageUsageOutputV1 = None
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
    def from_dict(cls: GetCustomerStorageUsageOutputV1Type, src_dict: Dict[str, Any]) -> GetCustomerStorageUsageOutputV1Type:
        obj = GetCustomerStorageUsageOutputV1()
        obj.load_dict(src_dict)
        return obj

GetCustomerStorageUsageOutputCollectionResponseV1Type = TypeVar("GetCustomerStorageUsageOutputCollectionResponseV1Type", bound="GetCustomerStorageUsageOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class GetCustomerStorageUsageOutputCollectionResponseV1(DataContract):
    data: List[GetCustomerStorageUsageOutputV1] = None
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
    def from_dict(cls: GetCustomerStorageUsageOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> GetCustomerStorageUsageOutputCollectionResponseV1Type:
        obj = GetCustomerStorageUsageOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

class ItemIdV1(str, Enum):
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
    EUMIITEMUNDEFINED = "eumIItemUndefined"
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

ItemRedefinitionV1Type = TypeVar("ItemRedefinitionV1Type", bound="ItemRedefinitionV1")

@attr.s(auto_attribs=True)
class ItemRedefinitionV1(DataContract):
    originalName: str = None
    newName: str = None
    newItemId: ItemIdV1 = None
    newUnitId: UnitIdV1 = None
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
    def from_dict(cls: ItemRedefinitionV1Type, src_dict: Dict[str, Any]) -> ItemRedefinitionV1Type:
        obj = ItemRedefinitionV1()
        obj.load_dict(src_dict)
        return obj

ExportParametersV1Type = TypeVar("ExportParametersV1Type", bound="ExportParametersV1")

@attr.s(auto_attribs=True)
class ExportParametersV1(DataContract):
    datasetId: str = None
    outputFileName: str = None
    srid: int = None
    arguments: str = None
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
    def from_dict(cls: ExportParametersV1Type, src_dict: Dict[str, Any]) -> ExportParametersV1Type:
        obj = ExportParametersV1()
        obj.load_dict(src_dict)
        return obj

class SearchDatasetsSortColumnTypeV1(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

ParameterDefinitionOutputV1Type = TypeVar("ParameterDefinitionOutputV1Type", bound="ParameterDefinitionOutputV1")

@attr.s(auto_attribs=True)
class ParameterDefinitionOutputV1(DataContract):
    name: str = None
    description: str = None
    dataType: str = None
    required: str = None
    defaultValue: None = None
    allowedValues: List[None] = None
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
    def from_dict(cls: ParameterDefinitionOutputV1Type, src_dict: Dict[str, Any]) -> ParameterDefinitionOutputV1Type:
        obj = ParameterDefinitionOutputV1()
        obj.load_dict(src_dict)
        return obj

StringResponseV1Type = TypeVar("StringResponseV1Type", bound="StringResponseV1")

@attr.s(auto_attribs=True)
class StringResponseV1(DataContract):
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
    def from_dict(cls: StringResponseV1Type, src_dict: Dict[str, Any]) -> StringResponseV1Type:
        obj = StringResponseV1()
        obj.load_dict(src_dict)
        return obj

ImportParametersV1Type = TypeVar("ImportParametersV1Type", bound="ImportParametersV1")

@attr.s(auto_attribs=True)
class ImportParametersV1(DataContract):
    appendDatasetId: str = None
    uploadUrl: str = None
    fileName: str = None
    srid: int = None
    arguments: str = None
    destinations: List[ImportDestinationV1] = None
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
    def from_dict(cls: ImportParametersV1Type, src_dict: Dict[str, Any]) -> ImportParametersV1Type:
        obj = ImportParametersV1()
        obj.load_dict(src_dict)
        return obj

TransformationParameterV1Type = TypeVar("TransformationParameterV1Type", bound="TransformationParameterV1")

@attr.s(auto_attribs=True)
class TransformationParameterV1(DataContract):
    name: str = None
    dataType: str = None
    displayName: str = None
    required: str = None
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
    def from_dict(cls: TransformationParameterV1Type, src_dict: Dict[str, Any]) -> TransformationParameterV1Type:
        obj = TransformationParameterV1()
        obj.load_dict(src_dict)
        return obj

class SpatialOperatorV1(str, Enum):
    INTERSECTS = "Intersects"
    WITHIN = "Within"
    def __str__(self) -> str:
        return str(self.value)

class TransferStatusV1(str, Enum):
    NONE = "None"
    PENDING = "Pending"
    INPROGRESS = "InProgress"
    COMPLETED = "Completed"
    ERROR = "Error"
    def __str__(self) -> str:
        return str(self.value)

class ComparisonOperatorV1(str, Enum):
    EQUAL = "Equal"
    NOTEQUAL = "NotEqual"
    GREATERTHAN = "GreaterThan"
    LESSTHAN = "LessThan"
    GREATERTHANOREQUAL = "GreaterThanOrEqual"
    LESSTHANOREQUAL = "LessThanOrEqual"
    def __str__(self) -> str:
        return str(self.value)

ItemFilterV1Type = TypeVar("ItemFilterV1Type", bound="ItemFilterV1")

@attr.s(auto_attribs=True)
class ItemFilterV1(DataContract):
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
    def from_dict(cls: ItemFilterV1Type, src_dict: Dict[str, Any]) -> ItemFilterV1Type:
        obj = ItemFilterV1()
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

ProjectCapabilitiesV1Type = TypeVar("ProjectCapabilitiesV1Type", bound="ProjectCapabilitiesV1")

@attr.s(auto_attribs=True)
class ProjectCapabilitiesV1(DataContract):
    canEdit: str = None
    canEditAccessLevel: str = None
    canDelete: str = None
    canGrantAccess: str = None
    canCreateContent: str = None
    canListContent: str = None
    canUpdateContent: str = None
    canDeleteContent: str = None
    canReadContent: str = None
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
    def from_dict(cls: ProjectCapabilitiesV1Type, src_dict: Dict[str, Any]) -> ProjectCapabilitiesV1Type:
        obj = ProjectCapabilitiesV1()
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

ProjectMemberOutputV1Type = TypeVar("ProjectMemberOutputV1Type", bound="ProjectMemberOutputV1")

@attr.s(auto_attribs=True)
class ProjectMemberOutputV1(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberOutputV1Type, src_dict: Dict[str, Any]) -> ProjectMemberOutputV1Type:
        obj = ProjectMemberOutputV1()
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

SubscriptionResourceAccessV1Type = TypeVar("SubscriptionResourceAccessV1Type", bound="SubscriptionResourceAccessV1")

@attr.s(auto_attribs=True)
class SubscriptionResourceAccessV1(DataContract):
    resourceId: str = None
    projectId: str = None
    sasToken: str = None
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
    def from_dict(cls: SubscriptionResourceAccessV1Type, src_dict: Dict[str, Any]) -> SubscriptionResourceAccessV1Type:
        obj = SubscriptionResourceAccessV1()
        obj.load_dict(src_dict)
        return obj

RestoreToProjectInputV1Type = TypeVar("RestoreToProjectInputV1Type", bound="RestoreToProjectInputV1")

@attr.s(auto_attribs=True)
class RestoreToProjectInputV1(DataContract):
    targetProjectId: str = None
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
    def from_dict(cls: RestoreToProjectInputV1Type, src_dict: Dict[str, Any]) -> RestoreToProjectInputV1Type:
        obj = RestoreToProjectInputV1()
        obj.load_dict(src_dict)
        return obj

ProjectStorageUsageOutputV1Type = TypeVar("ProjectStorageUsageOutputV1Type", bound="ProjectStorageUsageOutputV1")

@attr.s(auto_attribs=True)
class ProjectStorageUsageOutputV1(StorageUsageOutputV1):
    projectId: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = StorageUsageOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectStorageUsageOutputV1Type, src_dict: Dict[str, Any]) -> ProjectStorageUsageOutputV1Type:
        obj = ProjectStorageUsageOutputV1()
        obj.load_dict(src_dict)
        return obj

GetCustomerProjectUsageOutputV1Type = TypeVar("GetCustomerProjectUsageOutputV1Type", bound="GetCustomerProjectUsageOutputV1")

@attr.s(auto_attribs=True)
class GetCustomerProjectUsageOutputV1(GetCustomerStorageUsageOutputV1):
    projectUsage: List[ProjectStorageUsageOutputV1] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GetCustomerStorageUsageOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: GetCustomerProjectUsageOutputV1Type, src_dict: Dict[str, Any]) -> GetCustomerProjectUsageOutputV1Type:
        obj = GetCustomerProjectUsageOutputV1()
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

class AggregationTypeV1(str, Enum):
    MAX = "Max"
    MIN = "Min"
    AVG = "Avg"
    WEIGHTEDSUM = "WeightedSum"
    def __str__(self) -> str:
        return str(self.value)

ItemsFilterV1Type = TypeVar("ItemsFilterV1Type", bound="ItemsFilterV1")

@attr.s(auto_attribs=True)
class ItemsFilterV1(DataContract):
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
    def from_dict(cls: ItemsFilterV1Type, src_dict: Dict[str, Any]) -> ItemsFilterV1Type:
        obj = ItemsFilterV1()
        obj.load_dict(src_dict)
        return obj

ItemNameFilterV1Type = TypeVar("ItemNameFilterV1Type", bound="ItemNameFilterV1")

@attr.s(auto_attribs=True)
class ItemNameFilterV1(ItemsFilterV1):
    names: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemNameFilterV1Type, src_dict: Dict[str, Any]) -> ItemNameFilterV1Type:
        obj = ItemNameFilterV1()
        obj.load_dict(src_dict)
        return obj

class DatasetTypeV1(str, Enum):
    FILE = "file"
    MULTIDIMENSIONAL = "multidimensional"
    TIMESERIES = "timeseries"
    GISVECTORDATA = "gisvectordata"
    TILES = "tiles"
    def __str__(self) -> str:
        return str(self.value)

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

EditThumbnailInputV1Type = TypeVar("EditThumbnailInputV1Type", bound="EditThumbnailInputV1")

@attr.s(auto_attribs=True)
class EditThumbnailInputV1(DataContract):
    thumbnailBase64: str = None
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
    def from_dict(cls: EditThumbnailInputV1Type, src_dict: Dict[str, Any]) -> EditThumbnailInputV1Type:
        obj = EditThumbnailInputV1()
        obj.load_dict(src_dict)
        return obj

ItemIndexFilterV1Type = TypeVar("ItemIndexFilterV1Type", bound="ItemIndexFilterV1")

@attr.s(auto_attribs=True)
class ItemIndexFilterV1(ItemsFilterV1):
    itemIndices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemIndexFilterV1Type, src_dict: Dict[str, Any]) -> ItemIndexFilterV1Type:
        obj = ItemIndexFilterV1()
        obj.load_dict(src_dict)
        return obj

StringCollectionResponseV1Type = TypeVar("StringCollectionResponseV1Type", bound="StringCollectionResponseV1")

@attr.s(auto_attribs=True)
class StringCollectionResponseV1(DataContract):
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
    def from_dict(cls: StringCollectionResponseV1Type, src_dict: Dict[str, Any]) -> StringCollectionResponseV1Type:
        obj = StringCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

RecycleBinItemV1Type = TypeVar("RecycleBinItemV1Type", bound="RecycleBinItemV1")

@attr.s(auto_attribs=True)
class RecycleBinItemV1(DataContract):
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
    def from_dict(cls: RecycleBinItemV1Type, src_dict: Dict[str, Any]) -> RecycleBinItemV1Type:
        obj = RecycleBinItemV1()
        obj.load_dict(src_dict)
        return obj

RecycleBinItemPagedCollectionResponseV1Type = TypeVar("RecycleBinItemPagedCollectionResponseV1Type", bound="RecycleBinItemPagedCollectionResponseV1")

@attr.s(auto_attribs=True)
class RecycleBinItemPagedCollectionResponseV1(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[RecycleBinItemV1] = None
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
    def from_dict(cls: RecycleBinItemPagedCollectionResponseV1Type, src_dict: Dict[str, Any]) -> RecycleBinItemPagedCollectionResponseV1Type:
        obj = RecycleBinItemPagedCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

ParameterInputV1Type = TypeVar("ParameterInputV1Type", bound="ParameterInputV1")

@attr.s(auto_attribs=True)
class ParameterInputV1(DataContract):
    name: str = None
    value: None = None
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
    def from_dict(cls: ParameterInputV1Type, src_dict: Dict[str, Any]) -> ParameterInputV1Type:
        obj = ParameterInputV1()
        obj.load_dict(src_dict)
        return obj

MoveInputV1Type = TypeVar("MoveInputV1Type", bound="MoveInputV1")

@attr.s(auto_attribs=True)
class MoveInputV1(DataContract):
    targetProjectId: str = None
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
    def from_dict(cls: MoveInputV1Type, src_dict: Dict[str, Any]) -> MoveInputV1Type:
        obj = MoveInputV1()
        obj.load_dict(src_dict)
        return obj

class TransferTypeV1(str, Enum):
    IMPORT = "Import"
    EXPORT = "Export"
    CONVERSION = "Conversion"
    APPEND = "Append"
    UPDATE = "Update"
    def __str__(self) -> str:
        return str(self.value)

TransferInfoV1Type = TypeVar("TransferInfoV1Type", bound="TransferInfoV1")

@attr.s(auto_attribs=True)
class TransferInfoV1(DataContract):
    format: str = None
    name: str = None
    type: TransferTypeV1 = None
    description: str = None
    package: str = None
    datasetTypes: List[DatasetTypeV1] = None
    canAppend: str = None
    readerName: str = None
    writerName: str = None
    parameters: List[TransformationParameterV1] = None
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
    def from_dict(cls: TransferInfoV1Type, src_dict: Dict[str, Any]) -> TransferInfoV1Type:
        obj = TransferInfoV1()
        obj.load_dict(src_dict)
        return obj

TransferInfoCollectionResponseV1Type = TypeVar("TransferInfoCollectionResponseV1Type", bound="TransferInfoCollectionResponseV1")

@attr.s(auto_attribs=True)
class TransferInfoCollectionResponseV1(DataContract):
    data: List[TransferInfoV1] = None
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
    def from_dict(cls: TransferInfoCollectionResponseV1Type, src_dict: Dict[str, Any]) -> TransferInfoCollectionResponseV1Type:
        obj = TransferInfoCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

class RecycleBinItemTypeV1(str, Enum):
    PROJECT = "Project"
    DATASET = "Dataset"
    def __str__(self) -> str:
        return str(self.value)

RecycleBinItemDatasetV1Type = TypeVar("RecycleBinItemDatasetV1Type", bound="RecycleBinItemDatasetV1")

@attr.s(auto_attribs=True)
class RecycleBinItemDatasetV1(RecycleBinItemV1):
    id: str = None
    name: str = None
    itemType: RecycleBinItemTypeV1 = None
    datasetType: DatasetTypeV1 = None
    datasetFormat: str = None
    sizeKB: int = None
    deletedBy: str = None
    deletedAt: str = None
    projectId: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = RecycleBinItemV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: RecycleBinItemDatasetV1Type, src_dict: Dict[str, Any]) -> RecycleBinItemDatasetV1Type:
        obj = RecycleBinItemDatasetV1()
        obj.load_dict(src_dict)
        return obj

class RecycleBinItemSortPropertyV1(str, Enum):
    NAME = "Name"
    DELETEDAT = "DeletedAt"
    STORAGESIZE = "StorageSize"
    def __str__(self) -> str:
        return str(self.value)

ProjectMemberOutputCollectionResponseV1Type = TypeVar("ProjectMemberOutputCollectionResponseV1Type", bound="ProjectMemberOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class ProjectMemberOutputCollectionResponseV1(DataContract):
    data: List[ProjectMemberOutputV1] = None
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
    def from_dict(cls: ProjectMemberOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> ProjectMemberOutputCollectionResponseV1Type:
        obj = ProjectMemberOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

SucceededUploadOutputV1Type = TypeVar("SucceededUploadOutputV1Type", bound="SucceededUploadOutputV1")

@attr.s(auto_attribs=True)
class SucceededUploadOutputV1(DataContract):
    fileName: str = None
    datasetId: str = None
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
    def from_dict(cls: SucceededUploadOutputV1Type, src_dict: Dict[str, Any]) -> SucceededUploadOutputV1Type:
        obj = SucceededUploadOutputV1()
        obj.load_dict(src_dict)
        return obj

EditProjectInputV1Type = TypeVar("EditProjectInputV1Type", bound="EditProjectInputV1")

@attr.s(auto_attribs=True)
class EditProjectInputV1(DataContract):
    id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
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
    def from_dict(cls: EditProjectInputV1Type, src_dict: Dict[str, Any]) -> EditProjectInputV1Type:
        obj = EditProjectInputV1()
        obj.load_dict(src_dict)
        return obj

ProjectMemberInputV1Type = TypeVar("ProjectMemberInputV1Type", bound="ProjectMemberInputV1")

@attr.s(auto_attribs=True)
class ProjectMemberInputV1(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberInputV1Type, src_dict: Dict[str, Any]) -> ProjectMemberInputV1Type:
        obj = ProjectMemberInputV1()
        obj.load_dict(src_dict)
        return obj

SetProjectMembersInputV1Type = TypeVar("SetProjectMembersInputV1Type", bound="SetProjectMembersInputV1")

@attr.s(auto_attribs=True)
class SetProjectMembersInputV1(DataContract):
    members: List[ProjectMemberInputV1] = None
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
    def from_dict(cls: SetProjectMembersInputV1Type, src_dict: Dict[str, Any]) -> SetProjectMembersInputV1Type:
        obj = SetProjectMembersInputV1()
        obj.load_dict(src_dict)
        return obj

RecycleBinItemProjectV1Type = TypeVar("RecycleBinItemProjectV1Type", bound="RecycleBinItemProjectV1")

@attr.s(auto_attribs=True)
class RecycleBinItemProjectV1(RecycleBinItemV1):
    id: str = None
    name: str = None
    itemType: RecycleBinItemTypeV1 = None
    deletedBy: str = None
    deletedAt: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = RecycleBinItemV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: RecycleBinItemProjectV1Type, src_dict: Dict[str, Any]) -> RecycleBinItemProjectV1Type:
        obj = RecycleBinItemProjectV1()
        obj.load_dict(src_dict)
        return obj

DatasetRecursiveListOutputV1Type = TypeVar("DatasetRecursiveListOutputV1Type", bound="DatasetRecursiveListOutputV1")

@attr.s(auto_attribs=True)
class DatasetRecursiveListOutputV1(DataContract):
    id: str = None
    projectId: str = None
    name: str = None
    relativePath: str = None
    datasetType: DatasetTypeV1 = None
    datasetUrl: str = None
    sasToken: str = None
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
    def from_dict(cls: DatasetRecursiveListOutputV1Type, src_dict: Dict[str, Any]) -> DatasetRecursiveListOutputV1Type:
        obj = DatasetRecursiveListOutputV1()
        obj.load_dict(src_dict)
        return obj

DatasetRecursiveListOutputPagedCollectionResponseV1Type = TypeVar("DatasetRecursiveListOutputPagedCollectionResponseV1Type", bound="DatasetRecursiveListOutputPagedCollectionResponseV1")

@attr.s(auto_attribs=True)
class DatasetRecursiveListOutputPagedCollectionResponseV1(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[DatasetRecursiveListOutputV1] = None
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
    def from_dict(cls: DatasetRecursiveListOutputPagedCollectionResponseV1Type, src_dict: Dict[str, Any]) -> DatasetRecursiveListOutputPagedCollectionResponseV1Type:
        obj = DatasetRecursiveListOutputPagedCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

class SortOrderV1(str, Enum):
    ASC = "Asc"
    DESC = "Desc"
    def __str__(self) -> str:
        return str(self.value)

SearchSharedDatasetsInputV1Type = TypeVar("SearchSharedDatasetsInputV1Type", bound="SearchSharedDatasetsInputV1")

@attr.s(auto_attribs=True)
class SearchSharedDatasetsInputV1(DataContract):
    query: List[QueryConditionV1] = None
    sortBy: SearchDatasetsSortColumnTypeV1 = None
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
    def from_dict(cls: SearchSharedDatasetsInputV1Type, src_dict: Dict[str, Any]) -> SearchSharedDatasetsInputV1Type:
        obj = SearchSharedDatasetsInputV1()
        obj.load_dict(src_dict)
        return obj

class AccessLevelV1(str, Enum):
    SHARED = "Shared"
    PRIVATE = "Private"
    CONFIDENTIAL = "Confidential"
    def __str__(self) -> str:
        return str(self.value)

DeletedProjectSummaryOutputV1Type = TypeVar("DeletedProjectSummaryOutputV1Type", bound="DeletedProjectSummaryOutputV1")

@attr.s(auto_attribs=True)
class DeletedProjectSummaryOutputV1(DataContract):
    id: str = None
    name: str = None
    description: str = None
    createdAt: str = None
    createdBy: str = None
    updatedAt: str = None
    updatedBy: str = None
    deletedAt: str = None
    deletedBy: str = None
    capabilities: ProjectCapabilitiesV1 = None
    accessLevel: AccessLevelV1 = None
    members: List[ProjectMemberOutputV1] = None
    hasThumbnail: str = None
    thumbnailUrl: str = None
    inheritsMembers: str = None
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
    def from_dict(cls: DeletedProjectSummaryOutputV1Type, src_dict: Dict[str, Any]) -> DeletedProjectSummaryOutputV1Type:
        obj = DeletedProjectSummaryOutputV1()
        obj.load_dict(src_dict)
        return obj

DeletedProjectSummaryOutputCollectionResponseV1Type = TypeVar("DeletedProjectSummaryOutputCollectionResponseV1Type", bound="DeletedProjectSummaryOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class DeletedProjectSummaryOutputCollectionResponseV1(DataContract):
    data: List[DeletedProjectSummaryOutputV1] = None
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
    def from_dict(cls: DeletedProjectSummaryOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> DeletedProjectSummaryOutputCollectionResponseV1Type:
        obj = DeletedProjectSummaryOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

EditProjectAccessLevelInputV1Type = TypeVar("EditProjectAccessLevelInputV1Type", bound="EditProjectAccessLevelInputV1")

@attr.s(auto_attribs=True)
class EditProjectAccessLevelInputV1(DataContract):
    id: str = None
    accessLevel: AccessLevelV1 = None
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
    def from_dict(cls: EditProjectAccessLevelInputV1Type, src_dict: Dict[str, Any]) -> EditProjectAccessLevelInputV1Type:
        obj = EditProjectAccessLevelInputV1()
        obj.load_dict(src_dict)
        return obj

DatasetSummaryOutputV1Type = TypeVar("DatasetSummaryOutputV1Type", bound="DatasetSummaryOutputV1")

@attr.s(auto_attribs=True)
class DatasetSummaryOutputV1(DataContract):
    id: str = None
    name: str = None
    datasetType: DatasetTypeV1 = None
    dataPath: str = None
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
    def from_dict(cls: DatasetSummaryOutputV1Type, src_dict: Dict[str, Any]) -> DatasetSummaryOutputV1Type:
        obj = DatasetSummaryOutputV1()
        obj.load_dict(src_dict)
        return obj

DatasetSummaryOutputCollectionResponseV1Type = TypeVar("DatasetSummaryOutputCollectionResponseV1Type", bound="DatasetSummaryOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class DatasetSummaryOutputCollectionResponseV1(DataContract):
    data: List[DatasetSummaryOutputV1] = None
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
    def from_dict(cls: DatasetSummaryOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> DatasetSummaryOutputCollectionResponseV1Type:
        obj = DatasetSummaryOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

ProjectPathNodeV1Type = TypeVar("ProjectPathNodeV1Type", bound="ProjectPathNodeV1")

@attr.s(auto_attribs=True)
class ProjectPathNodeV1(DataContract):
    id: str = None
    name: str = None
    parentProjectId: str = None
    isDeleted: str = None
    capabilities: ProjectCapabilitiesV1 = None
    accessLevel: AccessLevelV1 = None
    inheritsMembers: str = None
    effectiveUserRole: str = None
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
    def from_dict(cls: ProjectPathNodeV1Type, src_dict: Dict[str, Any]) -> ProjectPathNodeV1Type:
        obj = ProjectPathNodeV1()
        obj.load_dict(src_dict)
        return obj

ProjectPathNodeCollectionResponseV1Type = TypeVar("ProjectPathNodeCollectionResponseV1Type", bound="ProjectPathNodeCollectionResponseV1")

@attr.s(auto_attribs=True)
class ProjectPathNodeCollectionResponseV1(DataContract):
    data: List[ProjectPathNodeV1] = None
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
    def from_dict(cls: ProjectPathNodeCollectionResponseV1Type, src_dict: Dict[str, Any]) -> ProjectPathNodeCollectionResponseV1Type:
        obj = ProjectPathNodeCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

AggregationV1Type = TypeVar("AggregationV1Type", bound="AggregationV1")

@attr.s(auto_attribs=True)
class AggregationV1(DataContract):
    itemsFilter: ItemsFilterV1 = None
    aggregationType: AggregationTypeV1 = None
    expression: str = None
    aggregatedItemName: str = None
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
    def from_dict(cls: AggregationV1Type, src_dict: Dict[str, Any]) -> AggregationV1Type:
        obj = AggregationV1()
        obj.load_dict(src_dict)
        return obj

CreateProjectInputV1Type = TypeVar("CreateProjectInputV1Type", bound="CreateProjectInputV1")

@attr.s(auto_attribs=True)
class CreateProjectInputV1(DataContract):
    name: str = None
    accessLevel: AccessLevelV1 = None
    description: str = None
    thumbnailBase64: str = None
    metadata: str = None
    settings: str = None
    members: List[ProjectMemberInputV1] = None
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
    def from_dict(cls: CreateProjectInputV1Type, src_dict: Dict[str, Any]) -> CreateProjectInputV1Type:
        obj = CreateProjectInputV1()
        obj.load_dict(src_dict)
        return obj

TransformationV1Type = TypeVar("TransformationV1Type", bound="TransformationV1")

@attr.s(auto_attribs=True)
class TransformationV1(DataContract):
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
    def from_dict(cls: TransformationV1Type, src_dict: Dict[str, Any]) -> TransformationV1Type:
        obj = TransformationV1()
        obj.load_dict(src_dict)
        return obj

ItemTransformationV1Type = TypeVar("ItemTransformationV1Type", bound="ItemTransformationV1")

@attr.s(auto_attribs=True)
class ItemTransformationV1(TransformationV1):
    itemRedefinitions: List[ItemRedefinitionV1] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemTransformationV1Type, src_dict: Dict[str, Any]) -> ItemTransformationV1Type:
        obj = ItemTransformationV1()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputV1Type = TypeVar("TransferSummaryOutputV1Type", bound="TransferSummaryOutputV1")

@attr.s(auto_attribs=True)
class TransferSummaryOutputV1(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    type: TransferTypeV1 = None
    format: str = None
    status: TransferStatusV1 = None
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
    def from_dict(cls: TransferSummaryOutputV1Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputV1Type:
        obj = TransferSummaryOutputV1()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputPagedCollectionResponseV1Type = TypeVar("TransferSummaryOutputPagedCollectionResponseV1Type", bound="TransferSummaryOutputPagedCollectionResponseV1")

@attr.s(auto_attribs=True)
class TransferSummaryOutputPagedCollectionResponseV1(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[TransferSummaryOutputV1] = None
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
    def from_dict(cls: TransferSummaryOutputPagedCollectionResponseV1Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputPagedCollectionResponseV1Type:
        obj = TransferSummaryOutputPagedCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

ConvertAppendInputV1Type = TypeVar("ConvertAppendInputV1Type", bound="ConvertAppendInputV1")

@attr.s(auto_attribs=True)
class ConvertAppendInputV1(DataContract):
    uploadUrl: str = None
    readerParameters: List[ParameterInputV1] = None
    writerParameters: List[ParameterInputV1] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV1] = None
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
    def from_dict(cls: ConvertAppendInputV1Type, src_dict: Dict[str, Any]) -> ConvertAppendInputV1Type:
        obj = ConvertAppendInputV1()
        obj.load_dict(src_dict)
        return obj

ItemFilterTransformationV1Type = TypeVar("ItemFilterTransformationV1Type", bound="ItemFilterTransformationV1")

@attr.s(auto_attribs=True)
class ItemFilterTransformationV1(TransformationV1):
    itemFilter: ItemFilterV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemFilterTransformationV1Type, src_dict: Dict[str, Any]) -> ItemFilterTransformationV1Type:
        obj = ItemFilterTransformationV1()
        obj.load_dict(src_dict)
        return obj

SpatialFilterTransformationV1Type = TypeVar("SpatialFilterTransformationV1Type", bound="SpatialFilterTransformationV1")

@attr.s(auto_attribs=True)
class SpatialFilterTransformationV1(TransformationV1):
    spatialFilter: SpatialFilterV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SpatialFilterTransformationV1Type, src_dict: Dict[str, Any]) -> SpatialFilterTransformationV1Type:
        obj = SpatialFilterTransformationV1()
        obj.load_dict(src_dict)
        return obj

ConvertDownloadInputV1Type = TypeVar("ConvertDownloadInputV1Type", bound="ConvertDownloadInputV1")

@attr.s(auto_attribs=True)
class ConvertDownloadInputV1(DataContract):
    readerParameters: List[ParameterInputV1] = None
    writerParameters: List[ParameterInputV1] = None
    readerName: str = None
    writerName: str = None
    targetFileName: str = None
    transformations: List[TransformationV1] = None
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
    def from_dict(cls: ConvertDownloadInputV1Type, src_dict: Dict[str, Any]) -> ConvertDownloadInputV1Type:
        obj = ConvertDownloadInputV1()
        obj.load_dict(src_dict)
        return obj

CsScriptValueTransformationV1Type = TypeVar("CsScriptValueTransformationV1Type", bound="CsScriptValueTransformationV1")

@attr.s(auto_attribs=True)
class CsScriptValueTransformationV1(TransformationV1):
    csScript: str = None
    items: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CsScriptValueTransformationV1Type, src_dict: Dict[str, Any]) -> CsScriptValueTransformationV1Type:
        obj = CsScriptValueTransformationV1()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputCollectionResponseV1Type = TypeVar("TransferSummaryOutputCollectionResponseV1Type", bound="TransferSummaryOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class TransferSummaryOutputCollectionResponseV1(DataContract):
    data: List[TransferSummaryOutputV1] = None
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
    def from_dict(cls: TransferSummaryOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputCollectionResponseV1Type:
        obj = TransferSummaryOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

CrsTransformationV1Type = TypeVar("CrsTransformationV1Type", bound="CrsTransformationV1")

@attr.s(auto_attribs=True)
class CrsTransformationV1(TransformationV1):
    inputSrid: int = None
    outputSrid: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CrsTransformationV1Type, src_dict: Dict[str, Any]) -> CrsTransformationV1Type:
        obj = CrsTransformationV1()
        obj.load_dict(src_dict)
        return obj

AggregationTransformationV1Type = TypeVar("AggregationTransformationV1Type", bound="AggregationTransformationV1")

@attr.s(auto_attribs=True)
class AggregationTransformationV1(TransformationV1):
    aggregations: List[AggregationV1] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AggregationTransformationV1Type, src_dict: Dict[str, Any]) -> AggregationTransformationV1Type:
        obj = AggregationTransformationV1()
        obj.load_dict(src_dict)
        return obj

UnitOutputV1Type = TypeVar("UnitOutputV1Type", bound="UnitOutputV1")

@attr.s(auto_attribs=True)
class UnitOutputV1(DataContract):
    id: str = None
    code: int = None
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
    def from_dict(cls: UnitOutputV1Type, src_dict: Dict[str, Any]) -> UnitOutputV1Type:
        obj = UnitOutputV1()
        obj.load_dict(src_dict)
        return obj

UnitOutputCollectionResponseV1Type = TypeVar("UnitOutputCollectionResponseV1Type", bound="UnitOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class UnitOutputCollectionResponseV1(DataContract):
    data: List[UnitOutputV1] = None
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
    def from_dict(cls: UnitOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> UnitOutputCollectionResponseV1Type:
        obj = UnitOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

ConvertFileUpdateInputV1Type = TypeVar("ConvertFileUpdateInputV1Type", bound="ConvertFileUpdateInputV1")

@attr.s(auto_attribs=True)
class ConvertFileUpdateInputV1(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    readerParameters: List[ParameterInputV1] = None
    writerParameters: List[ParameterInputV1] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV1] = None
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
    def from_dict(cls: ConvertFileUpdateInputV1Type, src_dict: Dict[str, Any]) -> ConvertFileUpdateInputV1Type:
        obj = ConvertFileUpdateInputV1()
        obj.load_dict(src_dict)
        return obj

DatasetSpatialInformationV1Type = TypeVar("DatasetSpatialInformationV1Type", bound="DatasetSpatialInformationV1")

@attr.s(auto_attribs=True)
class DatasetSpatialInformationV1(DataContract):
    location: str = None
    primarySpatialReference: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetSpatialInformationV1Type, src_dict: Dict[str, Any]) -> DatasetSpatialInformationV1Type:
        obj = DatasetSpatialInformationV1()
        obj.load_dict(src_dict)
        return obj

DownloadInputV1Type = TypeVar("DownloadInputV1Type", bound="DownloadInputV1")

@attr.s(auto_attribs=True)
class DownloadInputV1(DataContract):
    format: str = None
    srid: int = None
    arguments: str = None
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
    def from_dict(cls: DownloadInputV1Type, src_dict: Dict[str, Any]) -> DownloadInputV1Type:
        obj = DownloadInputV1()
        obj.load_dict(src_dict)
        return obj

FailedUploadOutputV1Type = TypeVar("FailedUploadOutputV1Type", bound="FailedUploadOutputV1")

@attr.s(auto_attribs=True)
class FailedUploadOutputV1(DataContract):
    fileName: str = None
    message: str = None
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
    def from_dict(cls: FailedUploadOutputV1Type, src_dict: Dict[str, Any]) -> FailedUploadOutputV1Type:
        obj = FailedUploadOutputV1()
        obj.load_dict(src_dict)
        return obj

StagedFilesUploadOutputV1Type = TypeVar("StagedFilesUploadOutputV1Type", bound="StagedFilesUploadOutputV1")

@attr.s(auto_attribs=True)
class StagedFilesUploadOutputV1(DataContract):
    datasets: List[SucceededUploadOutputV1] = None
    failures: List[FailedUploadOutputV1] = None
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
    def from_dict(cls: StagedFilesUploadOutputV1Type, src_dict: Dict[str, Any]) -> StagedFilesUploadOutputV1Type:
        obj = StagedFilesUploadOutputV1()
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

TemporalFilterV1Type = TypeVar("TemporalFilterV1Type", bound="TemporalFilterV1")

@attr.s(auto_attribs=True)
class TemporalFilterV1(DataContract):
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
    def from_dict(cls: TemporalFilterV1Type, src_dict: Dict[str, Any]) -> TemporalFilterV1Type:
        obj = TemporalFilterV1()
        obj.load_dict(src_dict)
        return obj

TemporalIndexFilterV1Type = TypeVar("TemporalIndexFilterV1Type", bound="TemporalIndexFilterV1")

@attr.s(auto_attribs=True)
class TemporalIndexFilterV1(TemporalFilterV1):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexFilterV1Type, src_dict: Dict[str, Any]) -> TemporalIndexFilterV1Type:
        obj = TemporalIndexFilterV1()
        obj.load_dict(src_dict)
        return obj

TemporalValueFilterV1Type = TypeVar("TemporalValueFilterV1Type", bound="TemporalValueFilterV1")

@attr.s(auto_attribs=True)
class TemporalValueFilterV1(TemporalFilterV1):
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
        result = TemporalFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalValueFilterV1Type, src_dict: Dict[str, Any]) -> TemporalValueFilterV1Type:
        obj = TemporalValueFilterV1()
        obj.load_dict(src_dict)
        return obj

StagedFileUploadInputV1Type = TypeVar("StagedFileUploadInputV1Type", bound="StagedFileUploadInputV1")

@attr.s(auto_attribs=True)
class StagedFileUploadInputV1(DataContract):
    url: str = None
    fileName: str = None
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
    def from_dict(cls: StagedFileUploadInputV1Type, src_dict: Dict[str, Any]) -> StagedFileUploadInputV1Type:
        obj = StagedFileUploadInputV1()
        obj.load_dict(src_dict)
        return obj

StagedFilesUploadInputV1Type = TypeVar("StagedFilesUploadInputV1Type", bound="StagedFilesUploadInputV1")

@attr.s(auto_attribs=True)
class StagedFilesUploadInputV1(DataContract):
    files: List[StagedFileUploadInputV1] = None
    destinationPath: str = None
    createDestinationPathIfNotExists: bool = None
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
    def from_dict(cls: StagedFilesUploadInputV1Type, src_dict: Dict[str, Any]) -> StagedFilesUploadInputV1Type:
        obj = StagedFilesUploadInputV1()
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

ConverterOutputV1Type = TypeVar("ConverterOutputV1Type", bound="ConverterOutputV1")

@attr.s(auto_attribs=True)
class ConverterOutputV1(DataContract):
    name: str = None
    description: str = None
    datasetFormat: str = None
    parameters: List[ParameterDefinitionOutputV1] = None
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
    def from_dict(cls: ConverterOutputV1Type, src_dict: Dict[str, Any]) -> ConverterOutputV1Type:
        obj = ConverterOutputV1()
        obj.load_dict(src_dict)
        return obj

ReaderOutputV1Type = TypeVar("ReaderOutputV1Type", bound="ReaderOutputV1")

@attr.s(auto_attribs=True)
class ReaderOutputV1(ConverterOutputV1):
    writers: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ConverterOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ReaderOutputV1Type, src_dict: Dict[str, Any]) -> ReaderOutputV1Type:
        obj = ReaderOutputV1()
        obj.load_dict(src_dict)
        return obj

ReaderOutputCollectionResponseV1Type = TypeVar("ReaderOutputCollectionResponseV1Type", bound="ReaderOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class ReaderOutputCollectionResponseV1(DataContract):
    data: List[ReaderOutputV1] = None
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
    def from_dict(cls: ReaderOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> ReaderOutputCollectionResponseV1Type:
        obj = ReaderOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

ConvertExistingInputV1Type = TypeVar("ConvertExistingInputV1Type", bound="ConvertExistingInputV1")

@attr.s(auto_attribs=True)
class ConvertExistingInputV1(DataContract):
    outputDatasetData: DatasetTransferInputV1 = None
    outputProjectId: str = None
    readerParameters: List[ParameterInputV1] = None
    writerParameters: List[ParameterInputV1] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV1] = None
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
    def from_dict(cls: ConvertExistingInputV1Type, src_dict: Dict[str, Any]) -> ConvertExistingInputV1Type:
        obj = ConvertExistingInputV1()
        obj.load_dict(src_dict)
        return obj

TemporalFilterTransformationV1Type = TypeVar("TemporalFilterTransformationV1Type", bound="TemporalFilterTransformationV1")

@attr.s(auto_attribs=True)
class TemporalFilterTransformationV1(TransformationV1):
    temporalFilter: TemporalFilterV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalFilterTransformationV1Type, src_dict: Dict[str, Any]) -> TemporalFilterTransformationV1Type:
        obj = TemporalFilterTransformationV1()
        obj.load_dict(src_dict)
        return obj

VerticalFilterV1Type = TypeVar("VerticalFilterV1Type", bound="VerticalFilterV1")

@attr.s(auto_attribs=True)
class VerticalFilterV1(DataContract):
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
    def from_dict(cls: VerticalFilterV1Type, src_dict: Dict[str, Any]) -> VerticalFilterV1Type:
        obj = VerticalFilterV1()
        obj.load_dict(src_dict)
        return obj

VerticalIndexFilterV1Type = TypeVar("VerticalIndexFilterV1Type", bound="VerticalIndexFilterV1")

@attr.s(auto_attribs=True)
class VerticalIndexFilterV1(VerticalFilterV1):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalIndexFilterV1Type, src_dict: Dict[str, Any]) -> VerticalIndexFilterV1Type:
        obj = VerticalIndexFilterV1()
        obj.load_dict(src_dict)
        return obj

TemporalIndexListFilterV1Type = TypeVar("TemporalIndexListFilterV1Type", bound="TemporalIndexListFilterV1")

@attr.s(auto_attribs=True)
class TemporalIndexListFilterV1(TemporalFilterV1):
    indices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexListFilterV1Type, src_dict: Dict[str, Any]) -> TemporalIndexListFilterV1Type:
        obj = TemporalIndexListFilterV1()
        obj.load_dict(src_dict)
        return obj

ConvertUploadInputV1Type = TypeVar("ConvertUploadInputV1Type", bound="ConvertUploadInputV1")

@attr.s(auto_attribs=True)
class ConvertUploadInputV1(DataContract):
    uploadUrl: str = None
    outputDatasetData: DatasetTransferInputV1 = None
    projectId: str = None
    readerParameters: List[ParameterInputV1] = None
    writerParameters: List[ParameterInputV1] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV1] = None
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
    def from_dict(cls: ConvertUploadInputV1Type, src_dict: Dict[str, Any]) -> ConvertUploadInputV1Type:
        obj = ConvertUploadInputV1()
        obj.load_dict(src_dict)
        return obj

WriterOutputV1Type = TypeVar("WriterOutputV1Type", bound="WriterOutputV1")

@attr.s(auto_attribs=True)
class WriterOutputV1(ConverterOutputV1):
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ConverterOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: WriterOutputV1Type, src_dict: Dict[str, Any]) -> WriterOutputV1Type:
        obj = WriterOutputV1()
        obj.load_dict(src_dict)
        return obj

WriterOutputCollectionResponseV1Type = TypeVar("WriterOutputCollectionResponseV1Type", bound="WriterOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class WriterOutputCollectionResponseV1(DataContract):
    data: List[WriterOutputV1] = None
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
    def from_dict(cls: WriterOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> WriterOutputCollectionResponseV1Type:
        obj = WriterOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

BaseEntityOutputV1Type = TypeVar("BaseEntityOutputV1Type", bound="BaseEntityOutputV1")

@attr.s(auto_attribs=True)
class BaseEntityOutputV1(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    updatedAt: str = None
    updatedBy: str = None
    deletedAt: str = None
    deletedBy: str = None
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
    def from_dict(cls: BaseEntityOutputV1Type, src_dict: Dict[str, Any]) -> BaseEntityOutputV1Type:
        obj = BaseEntityOutputV1()
        obj.load_dict(src_dict)
        return obj

ProjectOutputV1Type = TypeVar("ProjectOutputV1Type", bound="ProjectOutputV1")

@attr.s(auto_attribs=True)
class ProjectOutputV1(BaseEntityOutputV1):
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
    accessLevel: AccessLevelV1 = None
    members: List[ProjectMemberOutputV1] = None
    capabilities: ProjectCapabilitiesV1 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    inheritsMembers: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectOutputV1Type, src_dict: Dict[str, Any]) -> ProjectOutputV1Type:
        obj = ProjectOutputV1()
        obj.load_dict(src_dict)
        return obj

ProjectOutputCollectionResponseV1Type = TypeVar("ProjectOutputCollectionResponseV1Type", bound="ProjectOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class ProjectOutputCollectionResponseV1(DataContract):
    data: List[ProjectOutputV1] = None
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
    def from_dict(cls: ProjectOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> ProjectOutputCollectionResponseV1Type:
        obj = ProjectOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

DeletedDatasetSummaryOutputV1Type = TypeVar("DeletedDatasetSummaryOutputV1Type", bound="DeletedDatasetSummaryOutputV1")

@attr.s(auto_attribs=True)
class DeletedDatasetSummaryOutputV1(BaseEntityOutputV1):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV1 = None
    projectId: str = None
    dataPath: str = None
    tags: List[str] = None
    storageSize: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DeletedDatasetSummaryOutputV1Type, src_dict: Dict[str, Any]) -> DeletedDatasetSummaryOutputV1Type:
        obj = DeletedDatasetSummaryOutputV1()
        obj.load_dict(src_dict)
        return obj

DeletedDatasetSummaryOutputCollectionResponseV1Type = TypeVar("DeletedDatasetSummaryOutputCollectionResponseV1Type", bound="DeletedDatasetSummaryOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class DeletedDatasetSummaryOutputCollectionResponseV1(DataContract):
    data: List[DeletedDatasetSummaryOutputV1] = None
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
    def from_dict(cls: DeletedDatasetSummaryOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> DeletedDatasetSummaryOutputCollectionResponseV1Type:
        obj = DeletedDatasetSummaryOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

DatasetTemporalInformationV1Type = TypeVar("DatasetTemporalInformationV1Type", bound="DatasetTemporalInformationV1")

@attr.s(auto_attribs=True)
class DatasetTemporalInformationV1(DataContract):
    startTime: str = None
    endTime: str = None
    interval: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetTemporalInformationV1Type, src_dict: Dict[str, Any]) -> DatasetTemporalInformationV1Type:
        obj = DatasetTemporalInformationV1()
        obj.load_dict(src_dict)
        return obj

EditDatasetInputV1Type = TypeVar("EditDatasetInputV1Type", bound="EditDatasetInputV1")

@attr.s(auto_attribs=True)
class EditDatasetInputV1(DataContract):
    id: str = None
    name: str = None
    description: str = None
    datasetType: DatasetTypeV1 = None
    temporalInformation: DatasetTemporalInformationV1 = None
    spatialInformation: DatasetSpatialInformationV1 = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
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
    def from_dict(cls: EditDatasetInputV1Type, src_dict: Dict[str, Any]) -> EditDatasetInputV1Type:
        obj = EditDatasetInputV1()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputV1Type = TypeVar("ProjectListOutputV1Type", bound="ProjectListOutputV1")

@attr.s(auto_attribs=True)
class ProjectListOutputV1(BaseEntityOutputV1):
    name: str = None
    description: str = None
    accessLevel: AccessLevelV1 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectListOutputV1Type, src_dict: Dict[str, Any]) -> ProjectListOutputV1Type:
        obj = ProjectListOutputV1()
        obj.load_dict(src_dict)
        return obj

VerticalFilterTransformationV1Type = TypeVar("VerticalFilterTransformationV1Type", bound="VerticalFilterTransformationV1")

@attr.s(auto_attribs=True)
class VerticalFilterTransformationV1(TransformationV1):
    verticalFilter: VerticalFilterV1 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalFilterTransformationV1Type, src_dict: Dict[str, Any]) -> VerticalFilterTransformationV1Type:
        obj = VerticalFilterTransformationV1()
        obj.load_dict(src_dict)
        return obj

VerticalValueFilterV1Type = TypeVar("VerticalValueFilterV1Type", bound="VerticalValueFilterV1")

@attr.s(auto_attribs=True)
class VerticalValueFilterV1(VerticalFilterV1):
    from_: float = None
    to: float = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalValueFilterV1Type, src_dict: Dict[str, Any]) -> VerticalValueFilterV1Type:
        obj = VerticalValueFilterV1()
        obj.load_dict(src_dict)
        return obj

DatasetOutputV1Type = TypeVar("DatasetOutputV1Type", bound="DatasetOutputV1")

@attr.s(auto_attribs=True)
class DatasetOutputV1(BaseEntityOutputV1):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV1 = None
    projectId: str = None
    dataPath: str = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
    temporalInformation: DatasetTemporalInformationV1 = None
    spatialInformation: DatasetSpatialInformationV1 = None
    storageSize: int = None
    datasetFormat: str = None
    rowVersion: str = None
    sasToken: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DatasetOutputV1Type, src_dict: Dict[str, Any]) -> DatasetOutputV1Type:
        obj = DatasetOutputV1()
        obj.load_dict(src_dict)
        return obj

DatasetOutputCollectionResponseV1Type = TypeVar("DatasetOutputCollectionResponseV1Type", bound="DatasetOutputCollectionResponseV1")

@attr.s(auto_attribs=True)
class DatasetOutputCollectionResponseV1(DataContract):
    data: List[DatasetOutputV1] = None
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
    def from_dict(cls: DatasetOutputCollectionResponseV1Type, src_dict: Dict[str, Any]) -> DatasetOutputCollectionResponseV1Type:
        obj = DatasetOutputCollectionResponseV1()
        obj.load_dict(src_dict)
        return obj

DatasetOutputCursorResponseV1Type = TypeVar("DatasetOutputCursorResponseV1Type", bound="DatasetOutputCursorResponseV1")

@attr.s(auto_attribs=True)
class DatasetOutputCursorResponseV1(DataContract):
    cursor: str = None
    data: List[DatasetOutputV1] = None
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
    def from_dict(cls: DatasetOutputCursorResponseV1Type, src_dict: Dict[str, Any]) -> DatasetOutputCursorResponseV1Type:
        obj = DatasetOutputCursorResponseV1()
        obj.load_dict(src_dict)
        return obj

ImportResultV1Type = TypeVar("ImportResultV1Type", bound="ImportResultV1")

@attr.s(auto_attribs=True)
class ImportResultV1(DataContract):
    projectId: str = None
    datasetId: str = None
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
    def from_dict(cls: ImportResultV1Type, src_dict: Dict[str, Any]) -> ImportResultV1Type:
        obj = ImportResultV1()
        obj.load_dict(src_dict)
        return obj

TransferOutputV1Type = TypeVar("TransferOutputV1Type", bound="TransferOutputV1")

@attr.s(auto_attribs=True)
class TransferOutputV1(BaseEntityOutputV1):
    type: TransferTypeV1 = None
    status: TransferStatusV1 = None
    format: str = None
    projectId: str = None
    importParameters: ImportParametersV1 = None
    exportParameters: ExportParametersV1 = None
    datasetImportData: DatasetTransferInputV1 = None
    downloadPath: str = None
    errorMessage: str = None
    importResults: List[ImportResultV1] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV1.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TransferOutputV1Type, src_dict: Dict[str, Any]) -> TransferOutputV1Type:
        obj = TransferOutputV1()
        obj.load_dict(src_dict)
        return obj

class MetadataGenClientV1(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)

    def GetServiceIds(self) -> Response:
        """List available Service IDs

        Gateway
        GET /api/data/services
        """
        return self.GetRequest("/api/data/services", None)

    def GetAllDeletedItems(self, sortby=None, sortorder=None, offset=None, limit=None) -> Response:
        """RecycleBin

        GET /api/recycle-bin/all-deleted-items
        """
        queryparams = self.GetQueryParams(SortBy=sortby, SortOrder=sortorder, Offset=offset, Limit=limit)
        return self.GetRequest("/api/recycle-bin/all-deleted-items", queryparams, api_version="1")

    def GetMyDeletedItems(self, sortby=None, sortorder=None, offset=None, limit=None) -> Response:
        """RecycleBin

        GET /api/recycle-bin/my-deleted-items
        """
        queryparams = self.GetQueryParams(SortBy=sortby, SortOrder=sortorder, Offset=offset, Limit=limit)
        return self.GetRequest("/api/recycle-bin/my-deleted-items", queryparams, api_version="1")


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v2
# DHI Water Data Metadata API - Version 2
# API for managing projects and datasets inside projects
# 2

class TransferTypeV2(str, Enum):
    IMPORT = "Import"
    EXPORT = "Export"
    CONVERSION = "Conversion"
    APPEND = "Append"
    UPDATE = "Update"
    def __str__(self) -> str:
        return str(self.value)

class SortOrderV2(str, Enum):
    ASC = "Asc"
    DESC = "Desc"
    def __str__(self) -> str:
        return str(self.value)

TransformationParameterV2Type = TypeVar("TransformationParameterV2Type", bound="TransformationParameterV2")

@attr.s(auto_attribs=True)
class TransformationParameterV2(DataContract):
    name: str = None
    dataType: str = None
    displayName: str = None
    required: str = None
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
    def from_dict(cls: TransformationParameterV2Type, src_dict: Dict[str, Any]) -> TransformationParameterV2Type:
        obj = TransformationParameterV2()
        obj.load_dict(src_dict)
        return obj

DatasetSpatialInformationV2Type = TypeVar("DatasetSpatialInformationV2Type", bound="DatasetSpatialInformationV2")

@attr.s(auto_attribs=True)
class DatasetSpatialInformationV2(DataContract):
    location: str = None
    primarySpatialReference: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetSpatialInformationV2Type, src_dict: Dict[str, Any]) -> DatasetSpatialInformationV2Type:
        obj = DatasetSpatialInformationV2()
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

class AccessLevelV2(str, Enum):
    SHARED = "Shared"
    PRIVATE = "Private"
    CONFIDENTIAL = "Confidential"
    def __str__(self) -> str:
        return str(self.value)

SubscriptionResourceAccessV2Type = TypeVar("SubscriptionResourceAccessV2Type", bound="SubscriptionResourceAccessV2")

@attr.s(auto_attribs=True)
class SubscriptionResourceAccessV2(DataContract):
    resourceId: str = None
    projectId: str = None
    sasToken: str = None
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
    def from_dict(cls: SubscriptionResourceAccessV2Type, src_dict: Dict[str, Any]) -> SubscriptionResourceAccessV2Type:
        obj = SubscriptionResourceAccessV2()
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

ImportResultV2Type = TypeVar("ImportResultV2Type", bound="ImportResultV2")

@attr.s(auto_attribs=True)
class ImportResultV2(DataContract):
    projectId: str = None
    datasetId: str = None
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
    def from_dict(cls: ImportResultV2Type, src_dict: Dict[str, Any]) -> ImportResultV2Type:
        obj = ImportResultV2()
        obj.load_dict(src_dict)
        return obj

BaseEntityOutputV2Type = TypeVar("BaseEntityOutputV2Type", bound="BaseEntityOutputV2")

@attr.s(auto_attribs=True)
class BaseEntityOutputV2(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    updatedAt: str = None
    updatedBy: str = None
    deletedAt: str = None
    deletedBy: str = None
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
    def from_dict(cls: BaseEntityOutputV2Type, src_dict: Dict[str, Any]) -> BaseEntityOutputV2Type:
        obj = BaseEntityOutputV2()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputV2Type = TypeVar("ProjectListOutputV2Type", bound="ProjectListOutputV2")

@attr.s(auto_attribs=True)
class ProjectListOutputV2(BaseEntityOutputV2):
    name: str = None
    description: str = None
    accessLevel: AccessLevelV2 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectListOutputV2Type, src_dict: Dict[str, Any]) -> ProjectListOutputV2Type:
        obj = ProjectListOutputV2()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputPagedCollectionResponseV2Type = TypeVar("ProjectListOutputPagedCollectionResponseV2Type", bound="ProjectListOutputPagedCollectionResponseV2")

@attr.s(auto_attribs=True)
class ProjectListOutputPagedCollectionResponseV2(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[ProjectListOutputV2] = None
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
    def from_dict(cls: ProjectListOutputPagedCollectionResponseV2Type, src_dict: Dict[str, Any]) -> ProjectListOutputPagedCollectionResponseV2Type:
        obj = ProjectListOutputPagedCollectionResponseV2()
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

DeletedDatasetSummaryOutputV2Type = TypeVar("DeletedDatasetSummaryOutputV2Type", bound="DeletedDatasetSummaryOutputV2")

@attr.s(auto_attribs=True)
class DeletedDatasetSummaryOutputV2(BaseEntityOutputV2):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV2 = None
    projectId: str = None
    dataPath: str = None
    tags: List[str] = None
    storageSize: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DeletedDatasetSummaryOutputV2Type, src_dict: Dict[str, Any]) -> DeletedDatasetSummaryOutputV2Type:
        obj = DeletedDatasetSummaryOutputV2()
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

StorageUsageOutputV2Type = TypeVar("StorageUsageOutputV2Type", bound="StorageUsageOutputV2")

@attr.s(auto_attribs=True)
class StorageUsageOutputV2(DataContract):
    blobStorageUsedKB: int = None
    parsedStorageUsedKB: int = None
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
    def from_dict(cls: StorageUsageOutputV2Type, src_dict: Dict[str, Any]) -> StorageUsageOutputV2Type:
        obj = StorageUsageOutputV2()
        obj.load_dict(src_dict)
        return obj

ProjectStorageUsageOutputV2Type = TypeVar("ProjectStorageUsageOutputV2Type", bound="ProjectStorageUsageOutputV2")

@attr.s(auto_attribs=True)
class ProjectStorageUsageOutputV2(StorageUsageOutputV2):
    projectId: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = StorageUsageOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectStorageUsageOutputV2Type, src_dict: Dict[str, Any]) -> ProjectStorageUsageOutputV2Type:
        obj = ProjectStorageUsageOutputV2()
        obj.load_dict(src_dict)
        return obj

ExportParametersV2Type = TypeVar("ExportParametersV2Type", bound="ExportParametersV2")

@attr.s(auto_attribs=True)
class ExportParametersV2(DataContract):
    datasetId: str = None
    outputFileName: str = None
    srid: int = None
    arguments: str = None
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
    def from_dict(cls: ExportParametersV2Type, src_dict: Dict[str, Any]) -> ExportParametersV2Type:
        obj = ExportParametersV2()
        obj.load_dict(src_dict)
        return obj

GetCustomerStorageUsageOutputV2Type = TypeVar("GetCustomerStorageUsageOutputV2Type", bound="GetCustomerStorageUsageOutputV2")

@attr.s(auto_attribs=True)
class GetCustomerStorageUsageOutputV2(DataContract):
    customerId: str = None
    totalUsage: StorageUsageOutputV2 = None
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
    def from_dict(cls: GetCustomerStorageUsageOutputV2Type, src_dict: Dict[str, Any]) -> GetCustomerStorageUsageOutputV2Type:
        obj = GetCustomerStorageUsageOutputV2()
        obj.load_dict(src_dict)
        return obj

GetCustomerStorageUsageOutputCollectionResponseV2Type = TypeVar("GetCustomerStorageUsageOutputCollectionResponseV2Type", bound="GetCustomerStorageUsageOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class GetCustomerStorageUsageOutputCollectionResponseV2(DataContract):
    data: List[GetCustomerStorageUsageOutputV2] = None
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
    def from_dict(cls: GetCustomerStorageUsageOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> GetCustomerStorageUsageOutputCollectionResponseV2Type:
        obj = GetCustomerStorageUsageOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

DatasetTemporalInformationV2Type = TypeVar("DatasetTemporalInformationV2Type", bound="DatasetTemporalInformationV2")

@attr.s(auto_attribs=True)
class DatasetTemporalInformationV2(DataContract):
    startTime: str = None
    endTime: str = None
    interval: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetTemporalInformationV2Type, src_dict: Dict[str, Any]) -> DatasetTemporalInformationV2Type:
        obj = DatasetTemporalInformationV2()
        obj.load_dict(src_dict)
        return obj

DatasetOutputV2Type = TypeVar("DatasetOutputV2Type", bound="DatasetOutputV2")

@attr.s(auto_attribs=True)
class DatasetOutputV2(BaseEntityOutputV2):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV2 = None
    projectId: str = None
    dataPath: str = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
    temporalInformation: DatasetTemporalInformationV2 = None
    spatialInformation: DatasetSpatialInformationV2 = None
    storageSize: int = None
    datasetFormat: str = None
    rowVersion: str = None
    sasToken: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DatasetOutputV2Type, src_dict: Dict[str, Any]) -> DatasetOutputV2Type:
        obj = DatasetOutputV2()
        obj.load_dict(src_dict)
        return obj

DatasetOutputCursorResponseV2Type = TypeVar("DatasetOutputCursorResponseV2Type", bound="DatasetOutputCursorResponseV2")

@attr.s(auto_attribs=True)
class DatasetOutputCursorResponseV2(DataContract):
    cursor: str = None
    data: List[DatasetOutputV2] = None
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
    def from_dict(cls: DatasetOutputCursorResponseV2Type, src_dict: Dict[str, Any]) -> DatasetOutputCursorResponseV2Type:
        obj = DatasetOutputCursorResponseV2()
        obj.load_dict(src_dict)
        return obj

GetCustomerProjectUsageOutputV2Type = TypeVar("GetCustomerProjectUsageOutputV2Type", bound="GetCustomerProjectUsageOutputV2")

@attr.s(auto_attribs=True)
class GetCustomerProjectUsageOutputV2(GetCustomerStorageUsageOutputV2):
    projectUsage: List[ProjectStorageUsageOutputV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = GetCustomerStorageUsageOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: GetCustomerProjectUsageOutputV2Type, src_dict: Dict[str, Any]) -> GetCustomerProjectUsageOutputV2Type:
        obj = GetCustomerProjectUsageOutputV2()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputCursorResponseV2Type = TypeVar("ProjectListOutputCursorResponseV2Type", bound="ProjectListOutputCursorResponseV2")

@attr.s(auto_attribs=True)
class ProjectListOutputCursorResponseV2(DataContract):
    cursor: str = None
    data: List[ProjectListOutputV2] = None
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
    def from_dict(cls: ProjectListOutputCursorResponseV2Type, src_dict: Dict[str, Any]) -> ProjectListOutputCursorResponseV2Type:
        obj = ProjectListOutputCursorResponseV2()
        obj.load_dict(src_dict)
        return obj

DeletedDatasetSummaryOutputCollectionResponseV2Type = TypeVar("DeletedDatasetSummaryOutputCollectionResponseV2Type", bound="DeletedDatasetSummaryOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class DeletedDatasetSummaryOutputCollectionResponseV2(DataContract):
    data: List[DeletedDatasetSummaryOutputV2] = None
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
    def from_dict(cls: DeletedDatasetSummaryOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> DeletedDatasetSummaryOutputCollectionResponseV2Type:
        obj = DeletedDatasetSummaryOutputCollectionResponseV2()
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

class ProjectSortPropertyV2(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    UPDATEDAT = "UpdatedAt"
    ACCESSLEVEL = "AccessLevel"
    def __str__(self) -> str:
        return str(self.value)

ProjectMemberInputV2Type = TypeVar("ProjectMemberInputV2Type", bound="ProjectMemberInputV2")

@attr.s(auto_attribs=True)
class ProjectMemberInputV2(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberInputV2Type, src_dict: Dict[str, Any]) -> ProjectMemberInputV2Type:
        obj = ProjectMemberInputV2()
        obj.load_dict(src_dict)
        return obj

SetProjectMembersInputV2Type = TypeVar("SetProjectMembersInputV2Type", bound="SetProjectMembersInputV2")

@attr.s(auto_attribs=True)
class SetProjectMembersInputV2(DataContract):
    members: List[ProjectMemberInputV2] = None
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
    def from_dict(cls: SetProjectMembersInputV2Type, src_dict: Dict[str, Any]) -> SetProjectMembersInputV2Type:
        obj = SetProjectMembersInputV2()
        obj.load_dict(src_dict)
        return obj

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

ParameterDefinitionOutputV2Type = TypeVar("ParameterDefinitionOutputV2Type", bound="ParameterDefinitionOutputV2")

@attr.s(auto_attribs=True)
class ParameterDefinitionOutputV2(DataContract):
    name: str = None
    description: str = None
    dataType: str = None
    required: str = None
    defaultValue: None = None
    allowedValues: List[None] = None
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
    def from_dict(cls: ParameterDefinitionOutputV2Type, src_dict: Dict[str, Any]) -> ParameterDefinitionOutputV2Type:
        obj = ParameterDefinitionOutputV2()
        obj.load_dict(src_dict)
        return obj

class SearchDatasetsSortColumnTypeV2(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    def __str__(self) -> str:
        return str(self.value)

SearchSharedDatasetsInputV2Type = TypeVar("SearchSharedDatasetsInputV2Type", bound="SearchSharedDatasetsInputV2")

@attr.s(auto_attribs=True)
class SearchSharedDatasetsInputV2(DataContract):
    query: List[QueryConditionV2] = None
    sortBy: SearchDatasetsSortColumnTypeV2 = None
    sortOrder: SortOrderV2 = None
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
    def from_dict(cls: SearchSharedDatasetsInputV2Type, src_dict: Dict[str, Any]) -> SearchSharedDatasetsInputV2Type:
        obj = SearchSharedDatasetsInputV2()
        obj.load_dict(src_dict)
        return obj

RowVersionInputV2Type = TypeVar("RowVersionInputV2Type", bound="RowVersionInputV2")

@attr.s(auto_attribs=True)
class RowVersionInputV2(DataContract):
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
    def from_dict(cls: RowVersionInputV2Type, src_dict: Dict[str, Any]) -> RowVersionInputV2Type:
        obj = RowVersionInputV2()
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

class ConverterFilterV2(str, Enum):
    ALL = "All"
    FILE = "File"
    DEDICATED = "Dedicated"
    def __str__(self) -> str:
        return str(self.value)

RowVersionOutputV2Type = TypeVar("RowVersionOutputV2Type", bound="RowVersionOutputV2")

@attr.s(auto_attribs=True)
class RowVersionOutputV2(DataContract):
    id: str = None
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
    def from_dict(cls: RowVersionOutputV2Type, src_dict: Dict[str, Any]) -> RowVersionOutputV2Type:
        obj = RowVersionOutputV2()
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

EditProjectInputV2Type = TypeVar("EditProjectInputV2Type", bound="EditProjectInputV2")

@attr.s(auto_attribs=True)
class EditProjectInputV2(DataContract):
    id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
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
    def from_dict(cls: EditProjectInputV2Type, src_dict: Dict[str, Any]) -> EditProjectInputV2Type:
        obj = EditProjectInputV2()
        obj.load_dict(src_dict)
        return obj

EditProjectAccessLevelInputV2Type = TypeVar("EditProjectAccessLevelInputV2Type", bound="EditProjectAccessLevelInputV2")

@attr.s(auto_attribs=True)
class EditProjectAccessLevelInputV2(DataContract):
    id: str = None
    accessLevel: AccessLevelV2 = None
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
    def from_dict(cls: EditProjectAccessLevelInputV2Type, src_dict: Dict[str, Any]) -> EditProjectAccessLevelInputV2Type:
        obj = EditProjectAccessLevelInputV2()
        obj.load_dict(src_dict)
        return obj

RestoreToProjectInputV2Type = TypeVar("RestoreToProjectInputV2Type", bound="RestoreToProjectInputV2")

@attr.s(auto_attribs=True)
class RestoreToProjectInputV2(DataContract):
    targetProjectId: str = None
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
    def from_dict(cls: RestoreToProjectInputV2Type, src_dict: Dict[str, Any]) -> RestoreToProjectInputV2Type:
        obj = RestoreToProjectInputV2()
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

FailedUploadOutputV2Type = TypeVar("FailedUploadOutputV2Type", bound="FailedUploadOutputV2")

@attr.s(auto_attribs=True)
class FailedUploadOutputV2(DataContract):
    fileName: str = None
    message: str = None
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
    def from_dict(cls: FailedUploadOutputV2Type, src_dict: Dict[str, Any]) -> FailedUploadOutputV2Type:
        obj = FailedUploadOutputV2()
        obj.load_dict(src_dict)
        return obj

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

class ComparisonOperatorV2(str, Enum):
    EQUAL = "Equal"
    NOTEQUAL = "NotEqual"
    GREATERTHAN = "GreaterThan"
    LESSTHAN = "LessThan"
    GREATERTHANOREQUAL = "GreaterThanOrEqual"
    LESSTHANOREQUAL = "LessThanOrEqual"
    def __str__(self) -> str:
        return str(self.value)

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

DatasetTransferInputV2Type = TypeVar("DatasetTransferInputV2Type", bound="DatasetTransferInputV2")

@attr.s(auto_attribs=True)
class DatasetTransferInputV2(DataContract):
    name: str = None
    description: str = None
    metadata: str = None
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
    def from_dict(cls: DatasetTransferInputV2Type, src_dict: Dict[str, Any]) -> DatasetTransferInputV2Type:
        obj = DatasetTransferInputV2()
        obj.load_dict(src_dict)
        return obj

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

class UnitIdV2(str, Enum):
    EUMUMETER = "eumUmeter"
    EUMUKILOMETER = "eumUkilometer"
    EUMUMILLIMETER = "eumUmillimeter"
    EUMUINCH = "eumUinch"
    EUMUFEET = "eumUfeet"
    EUMUYARD = "eumUyard"
    EUMUMILE = "eumUmile"
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
    EUMUPERCENTPERMINUTE = "eumUpercentPerMinute"
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
    EUMUUNITUNDEFINED = "eumUUnitUndefined"
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

class ImportDestinationV2(str, Enum):
    DEDICATED = "Dedicated"
    PROJECT = "Project"
    def __str__(self) -> str:
        return str(self.value)

ImportParametersV2Type = TypeVar("ImportParametersV2Type", bound="ImportParametersV2")

@attr.s(auto_attribs=True)
class ImportParametersV2(DataContract):
    appendDatasetId: str = None
    uploadUrl: str = None
    fileName: str = None
    srid: int = None
    arguments: str = None
    destinations: List[ImportDestinationV2] = None
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
    def from_dict(cls: ImportParametersV2Type, src_dict: Dict[str, Any]) -> ImportParametersV2Type:
        obj = ImportParametersV2()
        obj.load_dict(src_dict)
        return obj

TransformationV2Type = TypeVar("TransformationV2Type", bound="TransformationV2")

@attr.s(auto_attribs=True)
class TransformationV2(DataContract):
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
    def from_dict(cls: TransformationV2Type, src_dict: Dict[str, Any]) -> TransformationV2Type:
        obj = TransformationV2()
        obj.load_dict(src_dict)
        return obj

SpatialFilterTransformationV2Type = TypeVar("SpatialFilterTransformationV2Type", bound="SpatialFilterTransformationV2")

@attr.s(auto_attribs=True)
class SpatialFilterTransformationV2(TransformationV2):
    spatialFilter: SpatialFilterV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SpatialFilterTransformationV2Type, src_dict: Dict[str, Any]) -> SpatialFilterTransformationV2Type:
        obj = SpatialFilterTransformationV2()
        obj.load_dict(src_dict)
        return obj

CrsTransformationV2Type = TypeVar("CrsTransformationV2Type", bound="CrsTransformationV2")

@attr.s(auto_attribs=True)
class CrsTransformationV2(TransformationV2):
    inputSrid: int = None
    outputSrid: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CrsTransformationV2Type, src_dict: Dict[str, Any]) -> CrsTransformationV2Type:
        obj = CrsTransformationV2()
        obj.load_dict(src_dict)
        return obj

VerticalFilterTransformationV2Type = TypeVar("VerticalFilterTransformationV2Type", bound="VerticalFilterTransformationV2")

@attr.s(auto_attribs=True)
class VerticalFilterTransformationV2(TransformationV2):
    verticalFilter: VerticalFilterV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalFilterTransformationV2Type, src_dict: Dict[str, Any]) -> VerticalFilterTransformationV2Type:
        obj = VerticalFilterTransformationV2()
        obj.load_dict(src_dict)
        return obj

UnitOutputV2Type = TypeVar("UnitOutputV2Type", bound="UnitOutputV2")

@attr.s(auto_attribs=True)
class UnitOutputV2(DataContract):
    id: str = None
    code: int = None
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
    def from_dict(cls: UnitOutputV2Type, src_dict: Dict[str, Any]) -> UnitOutputV2Type:
        obj = UnitOutputV2()
        obj.load_dict(src_dict)
        return obj

UnitOutputCollectionResponseV2Type = TypeVar("UnitOutputCollectionResponseV2Type", bound="UnitOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class UnitOutputCollectionResponseV2(DataContract):
    data: List[UnitOutputV2] = None
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
    def from_dict(cls: UnitOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> UnitOutputCollectionResponseV2Type:
        obj = UnitOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

TemporalFilterTransformationV2Type = TypeVar("TemporalFilterTransformationV2Type", bound="TemporalFilterTransformationV2")

@attr.s(auto_attribs=True)
class TemporalFilterTransformationV2(TransformationV2):
    temporalFilter: TemporalFilterV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalFilterTransformationV2Type, src_dict: Dict[str, Any]) -> TemporalFilterTransformationV2Type:
        obj = TemporalFilterTransformationV2()
        obj.load_dict(src_dict)
        return obj

SucceededUploadOutputV2Type = TypeVar("SucceededUploadOutputV2Type", bound="SucceededUploadOutputV2")

@attr.s(auto_attribs=True)
class SucceededUploadOutputV2(DataContract):
    fileName: str = None
    datasetId: str = None
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
    def from_dict(cls: SucceededUploadOutputV2Type, src_dict: Dict[str, Any]) -> SucceededUploadOutputV2Type:
        obj = SucceededUploadOutputV2()
        obj.load_dict(src_dict)
        return obj

StagedFilesUploadOutputV2Type = TypeVar("StagedFilesUploadOutputV2Type", bound="StagedFilesUploadOutputV2")

@attr.s(auto_attribs=True)
class StagedFilesUploadOutputV2(DataContract):
    datasets: List[SucceededUploadOutputV2] = None
    failures: List[FailedUploadOutputV2] = None
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
    def from_dict(cls: StagedFilesUploadOutputV2Type, src_dict: Dict[str, Any]) -> StagedFilesUploadOutputV2Type:
        obj = StagedFilesUploadOutputV2()
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

ItemFilterTransformationV2Type = TypeVar("ItemFilterTransformationV2Type", bound="ItemFilterTransformationV2")

@attr.s(auto_attribs=True)
class ItemFilterTransformationV2(TransformationV2):
    itemFilter: ItemFilterV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemFilterTransformationV2Type, src_dict: Dict[str, Any]) -> ItemFilterTransformationV2Type:
        obj = ItemFilterTransformationV2()
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

ItemsFilterV2Type = TypeVar("ItemsFilterV2Type", bound="ItemsFilterV2")

@attr.s(auto_attribs=True)
class ItemsFilterV2(DataContract):
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
    def from_dict(cls: ItemsFilterV2Type, src_dict: Dict[str, Any]) -> ItemsFilterV2Type:
        obj = ItemsFilterV2()
        obj.load_dict(src_dict)
        return obj

ItemIndexFilterV2Type = TypeVar("ItemIndexFilterV2Type", bound="ItemIndexFilterV2")

@attr.s(auto_attribs=True)
class ItemIndexFilterV2(ItemsFilterV2):
    itemIndices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemIndexFilterV2Type, src_dict: Dict[str, Any]) -> ItemIndexFilterV2Type:
        obj = ItemIndexFilterV2()
        obj.load_dict(src_dict)
        return obj

ProjectMemberOutputV2Type = TypeVar("ProjectMemberOutputV2Type", bound="ProjectMemberOutputV2")

@attr.s(auto_attribs=True)
class ProjectMemberOutputV2(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberOutputV2Type, src_dict: Dict[str, Any]) -> ProjectMemberOutputV2Type:
        obj = ProjectMemberOutputV2()
        obj.load_dict(src_dict)
        return obj

EditDatasetInputV2Type = TypeVar("EditDatasetInputV2Type", bound="EditDatasetInputV2")

@attr.s(auto_attribs=True)
class EditDatasetInputV2(DataContract):
    id: str = None
    name: str = None
    description: str = None
    datasetType: DatasetTypeV2 = None
    temporalInformation: DatasetTemporalInformationV2 = None
    spatialInformation: DatasetSpatialInformationV2 = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
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
    def from_dict(cls: EditDatasetInputV2Type, src_dict: Dict[str, Any]) -> EditDatasetInputV2Type:
        obj = EditDatasetInputV2()
        obj.load_dict(src_dict)
        return obj

TransferInfoV2Type = TypeVar("TransferInfoV2Type", bound="TransferInfoV2")

@attr.s(auto_attribs=True)
class TransferInfoV2(DataContract):
    format: str = None
    name: str = None
    type: TransferTypeV2 = None
    description: str = None
    package: str = None
    datasetTypes: List[DatasetTypeV2] = None
    canAppend: str = None
    readerName: str = None
    writerName: str = None
    parameters: List[TransformationParameterV2] = None
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
    def from_dict(cls: TransferInfoV2Type, src_dict: Dict[str, Any]) -> TransferInfoV2Type:
        obj = TransferInfoV2()
        obj.load_dict(src_dict)
        return obj

TransferInfoCollectionResponseV2Type = TypeVar("TransferInfoCollectionResponseV2Type", bound="TransferInfoCollectionResponseV2")

@attr.s(auto_attribs=True)
class TransferInfoCollectionResponseV2(DataContract):
    data: List[TransferInfoV2] = None
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
    def from_dict(cls: TransferInfoCollectionResponseV2Type, src_dict: Dict[str, Any]) -> TransferInfoCollectionResponseV2Type:
        obj = TransferInfoCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

CsScriptValueTransformationV2Type = TypeVar("CsScriptValueTransformationV2Type", bound="CsScriptValueTransformationV2")

@attr.s(auto_attribs=True)
class CsScriptValueTransformationV2(TransformationV2):
    csScript: str = None
    items: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CsScriptValueTransformationV2Type, src_dict: Dict[str, Any]) -> CsScriptValueTransformationV2Type:
        obj = CsScriptValueTransformationV2()
        obj.load_dict(src_dict)
        return obj

class TransferStatusV2(str, Enum):
    NONE = "None"
    PENDING = "Pending"
    INPROGRESS = "InProgress"
    COMPLETED = "Completed"
    ERROR = "Error"
    def __str__(self) -> str:
        return str(self.value)

TransferOutputV2Type = TypeVar("TransferOutputV2Type", bound="TransferOutputV2")

@attr.s(auto_attribs=True)
class TransferOutputV2(BaseEntityOutputV2):
    type: TransferTypeV2 = None
    status: TransferStatusV2 = None
    format: str = None
    projectId: str = None
    importParameters: ImportParametersV2 = None
    exportParameters: ExportParametersV2 = None
    datasetImportData: DatasetTransferInputV2 = None
    downloadPath: str = None
    errorMessage: str = None
    importResults: List[ImportResultV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TransferOutputV2Type, src_dict: Dict[str, Any]) -> TransferOutputV2Type:
        obj = TransferOutputV2()
        obj.load_dict(src_dict)
        return obj

class ItemIdV2(str, Enum):
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
    EUMIITEMUNDEFINED = "eumIItemUndefined"
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

ItemRedefinitionV2Type = TypeVar("ItemRedefinitionV2Type", bound="ItemRedefinitionV2")

@attr.s(auto_attribs=True)
class ItemRedefinitionV2(DataContract):
    originalName: str = None
    newName: str = None
    newItemId: ItemIdV2 = None
    newUnitId: UnitIdV2 = None
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
    def from_dict(cls: ItemRedefinitionV2Type, src_dict: Dict[str, Any]) -> ItemRedefinitionV2Type:
        obj = ItemRedefinitionV2()
        obj.load_dict(src_dict)
        return obj

ItemTransformationV2Type = TypeVar("ItemTransformationV2Type", bound="ItemTransformationV2")

@attr.s(auto_attribs=True)
class ItemTransformationV2(TransformationV2):
    itemRedefinitions: List[ItemRedefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemTransformationV2Type, src_dict: Dict[str, Any]) -> ItemTransformationV2Type:
        obj = ItemTransformationV2()
        obj.load_dict(src_dict)
        return obj

class AggregationTypeV2(str, Enum):
    MAX = "Max"
    MIN = "Min"
    AVG = "Avg"
    WEIGHTEDSUM = "WeightedSum"
    def __str__(self) -> str:
        return str(self.value)

AggregationV2Type = TypeVar("AggregationV2Type", bound="AggregationV2")

@attr.s(auto_attribs=True)
class AggregationV2(DataContract):
    itemsFilter: ItemsFilterV2 = None
    aggregationType: AggregationTypeV2 = None
    expression: str = None
    aggregatedItemName: str = None
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
    def from_dict(cls: AggregationV2Type, src_dict: Dict[str, Any]) -> AggregationV2Type:
        obj = AggregationV2()
        obj.load_dict(src_dict)
        return obj

AggregationTransformationV2Type = TypeVar("AggregationTransformationV2Type", bound="AggregationTransformationV2")

@attr.s(auto_attribs=True)
class AggregationTransformationV2(TransformationV2):
    aggregations: List[AggregationV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AggregationTransformationV2Type, src_dict: Dict[str, Any]) -> AggregationTransformationV2Type:
        obj = AggregationTransformationV2()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputV2Type = TypeVar("TransferSummaryOutputV2Type", bound="TransferSummaryOutputV2")

@attr.s(auto_attribs=True)
class TransferSummaryOutputV2(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    type: TransferTypeV2 = None
    format: str = None
    status: TransferStatusV2 = None
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
    def from_dict(cls: TransferSummaryOutputV2Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputV2Type:
        obj = TransferSummaryOutputV2()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputCollectionResponseV2Type = TypeVar("TransferSummaryOutputCollectionResponseV2Type", bound="TransferSummaryOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class TransferSummaryOutputCollectionResponseV2(DataContract):
    data: List[TransferSummaryOutputV2] = None
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
    def from_dict(cls: TransferSummaryOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputCollectionResponseV2Type:
        obj = TransferSummaryOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

ItemNameFilterV2Type = TypeVar("ItemNameFilterV2Type", bound="ItemNameFilterV2")

@attr.s(auto_attribs=True)
class ItemNameFilterV2(ItemsFilterV2):
    names: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemNameFilterV2Type, src_dict: Dict[str, Any]) -> ItemNameFilterV2Type:
        obj = ItemNameFilterV2()
        obj.load_dict(src_dict)
        return obj

ParameterInputV2Type = TypeVar("ParameterInputV2Type", bound="ParameterInputV2")

@attr.s(auto_attribs=True)
class ParameterInputV2(DataContract):
    name: str = None
    value: None = None
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
    def from_dict(cls: ParameterInputV2Type, src_dict: Dict[str, Any]) -> ParameterInputV2Type:
        obj = ParameterInputV2()
        obj.load_dict(src_dict)
        return obj

ConvertAppendInputV2Type = TypeVar("ConvertAppendInputV2Type", bound="ConvertAppendInputV2")

@attr.s(auto_attribs=True)
class ConvertAppendInputV2(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    readerParameters: List[ParameterInputV2] = None
    writerParameters: List[ParameterInputV2] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV2] = None
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
    def from_dict(cls: ConvertAppendInputV2Type, src_dict: Dict[str, Any]) -> ConvertAppendInputV2Type:
        obj = ConvertAppendInputV2()
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

ProjectCapabilitiesV2Type = TypeVar("ProjectCapabilitiesV2Type", bound="ProjectCapabilitiesV2")

@attr.s(auto_attribs=True)
class ProjectCapabilitiesV2(DataContract):
    canEdit: str = None
    canEditAccessLevel: str = None
    canDelete: str = None
    canGrantAccess: str = None
    canCreateContent: str = None
    canListContent: str = None
    canUpdateContent: str = None
    canDeleteContent: str = None
    canReadContent: str = None
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
    def from_dict(cls: ProjectCapabilitiesV2Type, src_dict: Dict[str, Any]) -> ProjectCapabilitiesV2Type:
        obj = ProjectCapabilitiesV2()
        obj.load_dict(src_dict)
        return obj

ProjectOutputV2Type = TypeVar("ProjectOutputV2Type", bound="ProjectOutputV2")

@attr.s(auto_attribs=True)
class ProjectOutputV2(BaseEntityOutputV2):
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
    accessLevel: AccessLevelV2 = None
    members: List[ProjectMemberOutputV2] = None
    capabilities: ProjectCapabilitiesV2 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    inheritsMembers: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectOutputV2Type, src_dict: Dict[str, Any]) -> ProjectOutputV2Type:
        obj = ProjectOutputV2()
        obj.load_dict(src_dict)
        return obj

ConvertUploadInputV2Type = TypeVar("ConvertUploadInputV2Type", bound="ConvertUploadInputV2")

@attr.s(auto_attribs=True)
class ConvertUploadInputV2(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    outputDatasetData: DatasetTransferInputV2 = None
    projectId: str = None
    readerParameters: List[ParameterInputV2] = None
    writerParameters: List[ParameterInputV2] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV2] = None
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
    def from_dict(cls: ConvertUploadInputV2Type, src_dict: Dict[str, Any]) -> ConvertUploadInputV2Type:
        obj = ConvertUploadInputV2()
        obj.load_dict(src_dict)
        return obj

ConverterOutputV2Type = TypeVar("ConverterOutputV2Type", bound="ConverterOutputV2")

@attr.s(auto_attribs=True)
class ConverterOutputV2(DataContract):
    name: str = None
    description: str = None
    datasetFormat: str = None
    parameters: List[ParameterDefinitionOutputV2] = None
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
    def from_dict(cls: ConverterOutputV2Type, src_dict: Dict[str, Any]) -> ConverterOutputV2Type:
        obj = ConverterOutputV2()
        obj.load_dict(src_dict)
        return obj

WriterOutputV2Type = TypeVar("WriterOutputV2Type", bound="WriterOutputV2")

@attr.s(auto_attribs=True)
class WriterOutputV2(ConverterOutputV2):
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ConverterOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: WriterOutputV2Type, src_dict: Dict[str, Any]) -> WriterOutputV2Type:
        obj = WriterOutputV2()
        obj.load_dict(src_dict)
        return obj

StagedFileUploadInputV2Type = TypeVar("StagedFileUploadInputV2Type", bound="StagedFileUploadInputV2")

@attr.s(auto_attribs=True)
class StagedFileUploadInputV2(DataContract):
    url: str = None
    fileName: str = None
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
    def from_dict(cls: StagedFileUploadInputV2Type, src_dict: Dict[str, Any]) -> StagedFileUploadInputV2Type:
        obj = StagedFileUploadInputV2()
        obj.load_dict(src_dict)
        return obj

StagedFilesUploadInputV2Type = TypeVar("StagedFilesUploadInputV2Type", bound="StagedFilesUploadInputV2")

@attr.s(auto_attribs=True)
class StagedFilesUploadInputV2(DataContract):
    files: List[StagedFileUploadInputV2] = None
    destinationPath: str = None
    createDestinationPathIfNotExists: str = None
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
    def from_dict(cls: StagedFilesUploadInputV2Type, src_dict: Dict[str, Any]) -> StagedFilesUploadInputV2Type:
        obj = StagedFilesUploadInputV2()
        obj.load_dict(src_dict)
        return obj

TransferSummaryOutputPagedCollectionResponseV2Type = TypeVar("TransferSummaryOutputPagedCollectionResponseV2Type", bound="TransferSummaryOutputPagedCollectionResponseV2")

@attr.s(auto_attribs=True)
class TransferSummaryOutputPagedCollectionResponseV2(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[TransferSummaryOutputV2] = None
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
    def from_dict(cls: TransferSummaryOutputPagedCollectionResponseV2Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputPagedCollectionResponseV2Type:
        obj = TransferSummaryOutputPagedCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

WriterOutputCollectionResponseV2Type = TypeVar("WriterOutputCollectionResponseV2Type", bound="WriterOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class WriterOutputCollectionResponseV2(DataContract):
    data: List[WriterOutputV2] = None
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
    def from_dict(cls: WriterOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> WriterOutputCollectionResponseV2Type:
        obj = WriterOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

DeletedProjectSummaryOutputV2Type = TypeVar("DeletedProjectSummaryOutputV2Type", bound="DeletedProjectSummaryOutputV2")

@attr.s(auto_attribs=True)
class DeletedProjectSummaryOutputV2(DataContract):
    id: str = None
    name: str = None
    description: str = None
    createdAt: str = None
    createdBy: str = None
    updatedAt: str = None
    updatedBy: str = None
    deletedAt: str = None
    deletedBy: str = None
    capabilities: ProjectCapabilitiesV2 = None
    accessLevel: AccessLevelV2 = None
    members: List[ProjectMemberOutputV2] = None
    hasThumbnail: str = None
    thumbnailUrl: str = None
    inheritsMembers: str = None
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
    def from_dict(cls: DeletedProjectSummaryOutputV2Type, src_dict: Dict[str, Any]) -> DeletedProjectSummaryOutputV2Type:
        obj = DeletedProjectSummaryOutputV2()
        obj.load_dict(src_dict)
        return obj

DeletedProjectSummaryOutputCollectionResponseV2Type = TypeVar("DeletedProjectSummaryOutputCollectionResponseV2Type", bound="DeletedProjectSummaryOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class DeletedProjectSummaryOutputCollectionResponseV2(DataContract):
    data: List[DeletedProjectSummaryOutputV2] = None
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
    def from_dict(cls: DeletedProjectSummaryOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> DeletedProjectSummaryOutputCollectionResponseV2Type:
        obj = DeletedProjectSummaryOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

ReaderOutputV2Type = TypeVar("ReaderOutputV2Type", bound="ReaderOutputV2")

@attr.s(auto_attribs=True)
class ReaderOutputV2(ConverterOutputV2):
    writers: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ConverterOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ReaderOutputV2Type, src_dict: Dict[str, Any]) -> ReaderOutputV2Type:
        obj = ReaderOutputV2()
        obj.load_dict(src_dict)
        return obj

ReaderOutputCollectionResponseV2Type = TypeVar("ReaderOutputCollectionResponseV2Type", bound="ReaderOutputCollectionResponseV2")

@attr.s(auto_attribs=True)
class ReaderOutputCollectionResponseV2(DataContract):
    data: List[ReaderOutputV2] = None
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
    def from_dict(cls: ReaderOutputCollectionResponseV2Type, src_dict: Dict[str, Any]) -> ReaderOutputCollectionResponseV2Type:
        obj = ReaderOutputCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

class MetadataGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)

    def GetExporterInfoV2(self, format) -> Response:
        """Get details of a particular Exporter

        Exporter
        GET /api/conversion/exporter/{format}
        """
        return self.GetRequest(f"/api/conversion/exporter/{format}", None, api_version="2")

    def GetExporterListV2(self) -> Response:
        """Get available exporters

        Exporter
        GET /api/conversion/exporter/list
        """
        return self.GetRequest("/api/conversion/exporter/list", None, api_version="2")

    def GetImporterInfoV2(self, format) -> Response:
        """Get details of a particular Importer

        Importer
        GET /api/conversion/importer/{format}
        """
        return self.GetRequest(f"/api/conversion/importer/{format}", None, api_version="2")

    def GetImporterListV2(self) -> Response:
        """Get available importers

        Importer
        GET /api/conversion/importer/list
        """
        return self.GetRequest("/api/conversion/importer/list", None, api_version="2")

    def UploadStagedFilesV2(self, body, id) -> Response:
        """FileUpload

        POST /api/conversion/project/{id}/file/import-staged
        """
        return self.PostRequest(f"/api/conversion/project/{id}/file/import-staged", body, None, api_version="2")

    def UploadFileStreamV2(self, body, id) -> Response:
        """FileUpload

        POST /api/conversion/project/{id}/file/upload
        """
        return self.PostRequest(f"/api/conversion/project/{id}/file/upload", body, None, api_version="2")

    def GetReaderV2(self, name) -> Response:
        """Conversion

        GET /api/conversion/reader/{name}
        """
        return self.GetRequest(f"/api/conversion/reader/{name}", None, api_version="2")

    def GetReadersListV2(self, filter=None) -> Response:
        """Conversion

        GET /api/conversion/reader/list
        """
        queryparams = self.GetQueryParams(filter=filter)
        return self.GetRequest("/api/conversion/reader/list", queryparams, api_version="2")

    def GetTransferV2(self, id) -> Response:
        """Get specified transfer

        Transfer
        GET /api/conversion/transfer/{id}
        """
        return self.GetRequest(f"/api/conversion/transfer/{id}", None, api_version="2")

    def GetProjectTransferListV2(self, projectid=None, from_=None, to=None, status=None, offset=None, limit=None, datasetid=None) -> Response:
        """Get transfers for project

        Transfer
        GET /api/conversion/transfer/list
        """
        kw = {"from": from_}
        queryparams = self.GetQueryParams(projectId=projectid, to=to, status=status, offset=offset, limit=limit, datasetId=datasetid, **kw)
        return self.GetRequest("/api/conversion/transfer/list", queryparams, api_version="2")

    def GetTransferListV2(self, from_=None, to=None, status=None) -> Response:
        """Get all transfers

        Transfer
        GET /api/conversion/transfer/list-summaries
        """
        kw = {"from": from_}
        queryparams = self.GetQueryParams(to=to, status=status, **kw)
        return self.GetRequest("/api/conversion/transfer/list-summaries", queryparams, api_version="2")

    def GetUploadUrlV2(self) -> Response:
        """Transfer

        GET /api/conversion/transfer/upload-url
        """
        return self.GetRequest("/api/conversion/transfer/upload-url", None, api_version="2")

    def GetWriterV2(self, name) -> Response:
        """Conversion

        GET /api/conversion/writer/{name}
        """
        return self.GetRequest(f"/api/conversion/writer/{name}", None, api_version="2")

    def GetWritersListV2(self, filter=None) -> Response:
        """Conversion

        GET /api/conversion/writer/list
        """
        queryparams = self.GetQueryParams(filter=filter)
        return self.GetRequest("/api/conversion/writer/list", queryparams, api_version="2")

    def GetServiceIds(self) -> Response:
        """List available Service IDs

        Gateway
        GET /api/data/services
        """
        return self.GetRequest("/api/data/services", None)

    def GetItemsV2(self) -> Response:
        """Get measures items

        Unit
        GET /api/metadata/item/list
        """
        return self.GetRequest("/api/metadata/item/list", None, api_version="2")

    def SearchSharedDatasetsV2(self, body) -> Response:
        """Searches the datasets that are shared within the user's customer. Shared means placed in a project with AccessLevel == Shared

        Search
        POST /api/metadata/search
        """
        return self.PostRequest("/api/metadata/search", body, None, api_version="2")

    def GetUnitsV2(self) -> Response:
        """Get measures units

        Unit
        GET /api/metadata/unit/list
        """
        return self.GetRequest("/api/metadata/unit/list", None, api_version="2")

    def GetRecyclableDatasetV2(self, id) -> Response:
        """DatasetRecycleBin

        GET /api/recycle-bin/dataset/{id}
        """
        return self.GetRequest(f"/api/recycle-bin/dataset/{id}", None, api_version="2")

    def DestroyDatasetV2(self, id) -> Response:
        """DatasetRecycleBin

        DELETE /api/recycle-bin/dataset/{id}
        """
        return self.DeleteRequest(f"/api/recycle-bin/dataset/{id}", None, api_version="2")

    def RestoreDatasetV2(self, id) -> Response:
        """DatasetRecycleBin

        PUT /api/recycle-bin/dataset/{id}/restore
        """
        return self.PutRequest(f"/api/recycle-bin/dataset/{id}/restore", None, None, api_version="2")

    def RestoreDatasetToLocationV2(self, body, id) -> Response:
        """Restore the project into a different location

        DatasetRecycleBin
        POST /api/recycle-bin/dataset/{id}/restore
        """
        return self.PostRequest(f"/api/recycle-bin/dataset/{id}/restore", body, None, api_version="2")

    def GetRecyclablesFromAllProjectsV2(self) -> Response:
        """Returns all recycled datasets from all projects (that the user can see)

        DatasetRecycleBin
        GET /api/recycle-bin/dataset/list
        """
        return self.GetRequest("/api/recycle-bin/dataset/list", None, api_version="2")

    def GetRecyclableProjectV2(self, id) -> Response:
        """ProjectRecycleBin

        GET /api/recycle-bin/project/{id}
        """
        return self.GetRequest(f"/api/recycle-bin/project/{id}", None, api_version="2")

    def DestroyProjectV2(self, id) -> Response:
        """ProjectRecycleBin

        DELETE /api/recycle-bin/project/{id}
        """
        return self.DeleteRequest(f"/api/recycle-bin/project/{id}", None, api_version="2")

    def GetRecyclableDatasetListV2(self, id) -> Response:
        """DatasetRecycleBin

        GET /api/recycle-bin/project/{id}/dataset/list
        """
        return self.GetRequest(f"/api/recycle-bin/project/{id}/dataset/list", None, api_version="2")

    def RestoreProjectV2(self, id) -> Response:
        """ProjectRecycleBin

        PUT /api/recycle-bin/project/{id}/restore
        """
        return self.PutRequest(f"/api/recycle-bin/project/{id}/restore", None, None, api_version="2")

    def RestoreProjectToLocationV2(self, body, id) -> Response:
        """Restore the project into a different location

        ProjectRecycleBin
        POST /api/recycle-bin/project/{id}/restore
        """
        return self.PostRequest(f"/api/recycle-bin/project/{id}/restore", body, None, api_version="2")

    def GetRecyclableSubProjectListV2(self, id) -> Response:
        """ProjectRecycleBin

        GET /api/recycle-bin/project/{id}/subprojects
        """
        return self.GetRequest(f"/api/recycle-bin/project/{id}/subprojects", None, api_version="2")

    def GetRecyclableProjectListV2(self) -> Response:
        """ProjectRecycleBin

        GET /api/recycle-bin/project/list
        """
        return self.GetRequest("/api/recycle-bin/project/list", None, api_version="2")

    def GetRecursiveSasTokenV2(self, projectid=None, expiration=None) -> Response:
        """Generate sas url for data access

        ServiceAccess
        GET /api/security/recursivesastoken
        """
        queryparams = self.GetQueryParams(projectId=projectid, expiration=expiration)
        return self.GetRequest("/api/security/recursivesastoken", queryparams, api_version="2")

    def GetSasTokenV2(self, projectid=None, resourceid=None, expiration=None) -> Response:
        """Generate sas url for data access

        ServiceAccess
        GET /api/security/sastoken
        """
        queryparams = self.GetQueryParams(projectId=projectid, resourceId=resourceid, expiration=expiration)
        return self.GetRequest("/api/security/sastoken", queryparams, api_version="2")

    def GetSubscriptionSasTokenV2(self, subscriptionid=None, expiration=None) -> Response:
        """Generate sas url for data access

        ServiceAccess
        GET /api/security/subscriptionsastoken
        """
        queryparams = self.GetQueryParams(subscriptionId=subscriptionid, expiration=expiration)
        return self.GetRequest("/api/security/subscriptionsastoken", queryparams, api_version="2")


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/metadata/v3
# DHI Water Data Metadata API - Version 3
# API for managing projects and datasets inside projects
# 3

class ImportDestinationV3(str, Enum):
    DEDICATED = "Dedicated"
    PROJECT = "Project"
    def __str__(self) -> str:
        return str(self.value)

ImportResultV3Type = TypeVar("ImportResultV3Type", bound="ImportResultV3")

@attr.s(auto_attribs=True)
class ImportResultV3(DataContract):
    projectId: str = None
    datasetId: str = None
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
    def from_dict(cls: ImportResultV3Type, src_dict: Dict[str, Any]) -> ImportResultV3Type:
        obj = ImportResultV3()
        obj.load_dict(src_dict)
        return obj

TemporalFilterV3Type = TypeVar("TemporalFilterV3Type", bound="TemporalFilterV3")

@attr.s(auto_attribs=True)
class TemporalFilterV3(DataContract):
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
    def from_dict(cls: TemporalFilterV3Type, src_dict: Dict[str, Any]) -> TemporalFilterV3Type:
        obj = TemporalFilterV3()
        obj.load_dict(src_dict)
        return obj

TemporalValueFilterV3Type = TypeVar("TemporalValueFilterV3Type", bound="TemporalValueFilterV3")

@attr.s(auto_attribs=True)
class TemporalValueFilterV3(TemporalFilterV3):
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
        result = TemporalFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalValueFilterV3Type, src_dict: Dict[str, Any]) -> TemporalValueFilterV3Type:
        obj = TemporalValueFilterV3()
        obj.load_dict(src_dict)
        return obj

BaseEntityOutputV3Type = TypeVar("BaseEntityOutputV3Type", bound="BaseEntityOutputV3")

@attr.s(auto_attribs=True)
class BaseEntityOutputV3(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    updatedAt: str = None
    updatedBy: str = None
    deletedAt: str = None
    deletedBy: str = None
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
    def from_dict(cls: BaseEntityOutputV3Type, src_dict: Dict[str, Any]) -> BaseEntityOutputV3Type:
        obj = BaseEntityOutputV3()
        obj.load_dict(src_dict)
        return obj

ExportParametersV3Type = TypeVar("ExportParametersV3Type", bound="ExportParametersV3")

@attr.s(auto_attribs=True)
class ExportParametersV3(DataContract):
    datasetId: str = None
    outputFileName: str = None
    srid: int = None
    arguments: str = None
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
    def from_dict(cls: ExportParametersV3Type, src_dict: Dict[str, Any]) -> ExportParametersV3Type:
        obj = ExportParametersV3()
        obj.load_dict(src_dict)
        return obj

PathActionV3Type = TypeVar("PathActionV3Type", bound="PathActionV3")

@attr.s(auto_attribs=True)
class PathActionV3(DataContract):
    type: str = "PathAction"
    path: str = None
    isFolder: str = None
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
    def from_dict(cls: PathActionV3Type, src_dict: Dict[str, Any]) -> PathActionV3Type:
        obj = PathActionV3()
        obj.load_dict(src_dict)
        return obj

class AccessLevelV3(str, Enum):
    SHARED = "Shared"
    PRIVATE = "Private"
    CONFIDENTIAL = "Confidential"
    def __str__(self) -> str:
        return str(self.value)

PrepareHierarchyInputV3Type = TypeVar("PrepareHierarchyInputV3Type", bound="PrepareHierarchyInputV3")

@attr.s(auto_attribs=True)
class PrepareHierarchyInputV3(DataContract):
    actions: List[PathActionV3] = None
    defaultAccessLevel: AccessLevelV3 = None
    sasTokenExpiration: str = None
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
    def from_dict(cls: PrepareHierarchyInputV3Type, src_dict: Dict[str, Any]) -> PrepareHierarchyInputV3Type:
        obj = PrepareHierarchyInputV3()
        obj.load_dict(src_dict)
        return obj

TemporalIndexListFilterV3Type = TypeVar("TemporalIndexListFilterV3Type", bound="TemporalIndexListFilterV3")

@attr.s(auto_attribs=True)
class TemporalIndexListFilterV3(TemporalFilterV3):
    indices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexListFilterV3Type, src_dict: Dict[str, Any]) -> TemporalIndexListFilterV3Type:
        obj = TemporalIndexListFilterV3()
        obj.load_dict(src_dict)
        return obj

DatasetTemporalInformationV3Type = TypeVar("DatasetTemporalInformationV3Type", bound="DatasetTemporalInformationV3")

@attr.s(auto_attribs=True)
class DatasetTemporalInformationV3(DataContract):
    startTime: str = None
    endTime: str = None
    interval: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetTemporalInformationV3Type, src_dict: Dict[str, Any]) -> DatasetTemporalInformationV3Type:
        obj = DatasetTemporalInformationV3()
        obj.load_dict(src_dict)
        return obj

TemporalIndexFilterV3Type = TypeVar("TemporalIndexFilterV3Type", bound="TemporalIndexFilterV3")

@attr.s(auto_attribs=True)
class TemporalIndexFilterV3(TemporalFilterV3):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TemporalFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalIndexFilterV3Type, src_dict: Dict[str, Any]) -> TemporalIndexFilterV3Type:
        obj = TemporalIndexFilterV3()
        obj.load_dict(src_dict)
        return obj

class ItemIdV3(str, Enum):
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
    EUMIITEMUNDEFINED = "eumIItemUndefined"
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

ProjectCapabilitiesV3Type = TypeVar("ProjectCapabilitiesV3Type", bound="ProjectCapabilitiesV3")

@attr.s(auto_attribs=True)
class ProjectCapabilitiesV3(DataContract):
    canEdit: str = None
    canEditAccessLevel: str = None
    canDelete: str = None
    canGrantAccess: str = None
    canCreateContent: str = None
    canListContent: str = None
    canUpdateContent: str = None
    canDeleteContent: str = None
    canReadContent: str = None
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
    def from_dict(cls: ProjectCapabilitiesV3Type, src_dict: Dict[str, Any]) -> ProjectCapabilitiesV3Type:
        obj = ProjectCapabilitiesV3()
        obj.load_dict(src_dict)
        return obj

ProjectPathNodeV3Type = TypeVar("ProjectPathNodeV3Type", bound="ProjectPathNodeV3")

@attr.s(auto_attribs=True)
class ProjectPathNodeV3(DataContract):
    id: str = None
    name: str = None
    parentProjectId: str = None
    isDeleted: str = None
    capabilities: ProjectCapabilitiesV3 = None
    accessLevel: AccessLevelV3 = None
    inheritsMembers: str = None
    effectiveUserRole: str = None
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
    def from_dict(cls: ProjectPathNodeV3Type, src_dict: Dict[str, Any]) -> ProjectPathNodeV3Type:
        obj = ProjectPathNodeV3()
        obj.load_dict(src_dict)
        return obj

ProjectPathNodeCollectionResponseV3Type = TypeVar("ProjectPathNodeCollectionResponseV3Type", bound="ProjectPathNodeCollectionResponseV3")

@attr.s(auto_attribs=True)
class ProjectPathNodeCollectionResponseV3(DataContract):
    data: List[ProjectPathNodeV3] = None
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
    def from_dict(cls: ProjectPathNodeCollectionResponseV3Type, src_dict: Dict[str, Any]) -> ProjectPathNodeCollectionResponseV3Type:
        obj = ProjectPathNodeCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

DatasetSpatialInformationV3Type = TypeVar("DatasetSpatialInformationV3Type", bound="DatasetSpatialInformationV3")

@attr.s(auto_attribs=True)
class DatasetSpatialInformationV3(DataContract):
    location: str = None
    primarySpatialReference: str = None
    resolution: str = None
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
    def from_dict(cls: DatasetSpatialInformationV3Type, src_dict: Dict[str, Any]) -> DatasetSpatialInformationV3Type:
        obj = DatasetSpatialInformationV3()
        obj.load_dict(src_dict)
        return obj

class DatasetTypeV3(str, Enum):
    FILE = "file"
    MULTIDIMENSIONAL = "multidimensional"
    TIMESERIES = "timeseries"
    GISVECTORDATA = "gisvectordata"
    TILES = "tiles"
    def __str__(self) -> str:
        return str(self.value)

DatasetOutputV3Type = TypeVar("DatasetOutputV3Type", bound="DatasetOutputV3")

@attr.s(auto_attribs=True)
class DatasetOutputV3(BaseEntityOutputV3):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV3 = None
    projectId: str = None
    dataPath: str = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
    temporalInformation: DatasetTemporalInformationV3 = None
    spatialInformation: DatasetSpatialInformationV3 = None
    storageSize: int = None
    datasetFormat: str = None
    rowVersion: str = None
    sasToken: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DatasetOutputV3Type, src_dict: Dict[str, Any]) -> DatasetOutputV3Type:
        obj = DatasetOutputV3()
        obj.load_dict(src_dict)
        return obj

ProjectMemberOutputV3Type = TypeVar("ProjectMemberOutputV3Type", bound="ProjectMemberOutputV3")

@attr.s(auto_attribs=True)
class ProjectMemberOutputV3(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberOutputV3Type, src_dict: Dict[str, Any]) -> ProjectMemberOutputV3Type:
        obj = ProjectMemberOutputV3()
        obj.load_dict(src_dict)
        return obj

ProjectOutputV3Type = TypeVar("ProjectOutputV3Type", bound="ProjectOutputV3")

@attr.s(auto_attribs=True)
class ProjectOutputV3(BaseEntityOutputV3):
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
    accessLevel: AccessLevelV3 = None
    members: List[ProjectMemberOutputV3] = None
    capabilities: ProjectCapabilitiesV3 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    inheritsMembers: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectOutputV3Type, src_dict: Dict[str, Any]) -> ProjectOutputV3Type:
        obj = ProjectOutputV3()
        obj.load_dict(src_dict)
        return obj

ProjectOutputCollectionResponseV3Type = TypeVar("ProjectOutputCollectionResponseV3Type", bound="ProjectOutputCollectionResponseV3")

@attr.s(auto_attribs=True)
class ProjectOutputCollectionResponseV3(DataContract):
    data: List[ProjectOutputV3] = None
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
    def from_dict(cls: ProjectOutputCollectionResponseV3Type, src_dict: Dict[str, Any]) -> ProjectOutputCollectionResponseV3Type:
        obj = ProjectOutputCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

EditProjectAccessLevelInputV3Type = TypeVar("EditProjectAccessLevelInputV3Type", bound="EditProjectAccessLevelInputV3")

@attr.s(auto_attribs=True)
class EditProjectAccessLevelInputV3(DataContract):
    id: str = None
    accessLevel: AccessLevelV3 = None
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
    def from_dict(cls: EditProjectAccessLevelInputV3Type, src_dict: Dict[str, Any]) -> EditProjectAccessLevelInputV3Type:
        obj = EditProjectAccessLevelInputV3()
        obj.load_dict(src_dict)
        return obj

ItemFilterV3Type = TypeVar("ItemFilterV3Type", bound="ItemFilterV3")

@attr.s(auto_attribs=True)
class ItemFilterV3(DataContract):
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
    def from_dict(cls: ItemFilterV3Type, src_dict: Dict[str, Any]) -> ItemFilterV3Type:
        obj = ItemFilterV3()
        obj.load_dict(src_dict)
        return obj

ProjectMemberOutputCollectionResponseV3Type = TypeVar("ProjectMemberOutputCollectionResponseV3Type", bound="ProjectMemberOutputCollectionResponseV3")

@attr.s(auto_attribs=True)
class ProjectMemberOutputCollectionResponseV3(DataContract):
    data: List[ProjectMemberOutputV3] = None
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
    def from_dict(cls: ProjectMemberOutputCollectionResponseV3Type, src_dict: Dict[str, Any]) -> ProjectMemberOutputCollectionResponseV3Type:
        obj = ProjectMemberOutputCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

DatasetRecursiveListOutputV3Type = TypeVar("DatasetRecursiveListOutputV3Type", bound="DatasetRecursiveListOutputV3")

@attr.s(auto_attribs=True)
class DatasetRecursiveListOutputV3(DataContract):
    id: str = None
    projectId: str = None
    name: str = None
    relativePath: str = None
    datasetType: DatasetTypeV3 = None
    datasetUrl: str = None
    sasToken: str = None
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
    def from_dict(cls: DatasetRecursiveListOutputV3Type, src_dict: Dict[str, Any]) -> DatasetRecursiveListOutputV3Type:
        obj = DatasetRecursiveListOutputV3()
        obj.load_dict(src_dict)
        return obj

DatasetRecursiveListOutputPagedCollectionResponseV3Type = TypeVar("DatasetRecursiveListOutputPagedCollectionResponseV3Type", bound="DatasetRecursiveListOutputPagedCollectionResponseV3")

@attr.s(auto_attribs=True)
class DatasetRecursiveListOutputPagedCollectionResponseV3(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[DatasetRecursiveListOutputV3] = None
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
    def from_dict(cls: DatasetRecursiveListOutputPagedCollectionResponseV3Type, src_dict: Dict[str, Any]) -> DatasetRecursiveListOutputPagedCollectionResponseV3Type:
        obj = DatasetRecursiveListOutputPagedCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

EditDatasetInputV3Type = TypeVar("EditDatasetInputV3Type", bound="EditDatasetInputV3")

@attr.s(auto_attribs=True)
class EditDatasetInputV3(DataContract):
    id: str = None
    name: str = None
    description: str = None
    datasetType: DatasetTypeV3 = None
    temporalInformation: DatasetTemporalInformationV3 = None
    spatialInformation: DatasetSpatialInformationV3 = None
    metadata: str = None
    properties: str = None
    tags: List[str] = None
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
    def from_dict(cls: EditDatasetInputV3Type, src_dict: Dict[str, Any]) -> EditDatasetInputV3Type:
        obj = EditDatasetInputV3()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputV3Type = TypeVar("ProjectListOutputV3Type", bound="ProjectListOutputV3")

@attr.s(auto_attribs=True)
class ProjectListOutputV3(BaseEntityOutputV3):
    name: str = None
    description: str = None
    accessLevel: AccessLevelV3 = None
    hasThumbnail: str = None
    parentProjectId: str = None
    thumbnailUrl: str = None
    rowVersion: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ProjectListOutputV3Type, src_dict: Dict[str, Any]) -> ProjectListOutputV3Type:
        obj = ProjectListOutputV3()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputPagedCollectionResponseV3Type = TypeVar("ProjectListOutputPagedCollectionResponseV3Type", bound="ProjectListOutputPagedCollectionResponseV3")

@attr.s(auto_attribs=True)
class ProjectListOutputPagedCollectionResponseV3(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[ProjectListOutputV3] = None
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
    def from_dict(cls: ProjectListOutputPagedCollectionResponseV3Type, src_dict: Dict[str, Any]) -> ProjectListOutputPagedCollectionResponseV3Type:
        obj = ProjectListOutputPagedCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

ItemsFilterV3Type = TypeVar("ItemsFilterV3Type", bound="ItemsFilterV3")

@attr.s(auto_attribs=True)
class ItemsFilterV3(DataContract):
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
    def from_dict(cls: ItemsFilterV3Type, src_dict: Dict[str, Any]) -> ItemsFilterV3Type:
        obj = ItemsFilterV3()
        obj.load_dict(src_dict)
        return obj

ItemIndexFilterV3Type = TypeVar("ItemIndexFilterV3Type", bound="ItemIndexFilterV3")

@attr.s(auto_attribs=True)
class ItemIndexFilterV3(ItemsFilterV3):
    itemIndices: List[int] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemIndexFilterV3Type, src_dict: Dict[str, Any]) -> ItemIndexFilterV3Type:
        obj = ItemIndexFilterV3()
        obj.load_dict(src_dict)
        return obj

ImportParametersV3Type = TypeVar("ImportParametersV3Type", bound="ImportParametersV3")

@attr.s(auto_attribs=True)
class ImportParametersV3(DataContract):
    appendDatasetId: str = None
    uploadUrl: str = None
    fileName: str = None
    srid: int = None
    arguments: str = None
    destinations: List[ImportDestinationV3] = None
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
    def from_dict(cls: ImportParametersV3Type, src_dict: Dict[str, Any]) -> ImportParametersV3Type:
        obj = ImportParametersV3()
        obj.load_dict(src_dict)
        return obj

SpatialFilterV3Type = TypeVar("SpatialFilterV3Type", bound="SpatialFilterV3")

@attr.s(auto_attribs=True)
class SpatialFilterV3(DataContract):
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
    def from_dict(cls: SpatialFilterV3Type, src_dict: Dict[str, Any]) -> SpatialFilterV3Type:
        obj = SpatialFilterV3()
        obj.load_dict(src_dict)
        return obj

DeletedDatasetSummaryOutputV3Type = TypeVar("DeletedDatasetSummaryOutputV3Type", bound="DeletedDatasetSummaryOutputV3")

@attr.s(auto_attribs=True)
class DeletedDatasetSummaryOutputV3(BaseEntityOutputV3):
    name: str = None
    description: str = None
    datasetType: DatasetTypeV3 = None
    projectId: str = None
    dataPath: str = None
    tags: List[str] = None
    storageSize: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DeletedDatasetSummaryOutputV3Type, src_dict: Dict[str, Any]) -> DeletedDatasetSummaryOutputV3Type:
        obj = DeletedDatasetSummaryOutputV3()
        obj.load_dict(src_dict)
        return obj

ItemNameFilterV3Type = TypeVar("ItemNameFilterV3Type", bound="ItemNameFilterV3")

@attr.s(auto_attribs=True)
class ItemNameFilterV3(ItemsFilterV3):
    names: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = ItemsFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemNameFilterV3Type, src_dict: Dict[str, Any]) -> ItemNameFilterV3Type:
        obj = ItemNameFilterV3()
        obj.load_dict(src_dict)
        return obj

StringResponseV3Type = TypeVar("StringResponseV3Type", bound="StringResponseV3")

@attr.s(auto_attribs=True)
class StringResponseV3(DataContract):
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
    def from_dict(cls: StringResponseV3Type, src_dict: Dict[str, Any]) -> StringResponseV3Type:
        obj = StringResponseV3()
        obj.load_dict(src_dict)
        return obj

PathActionOutputV3Type = TypeVar("PathActionOutputV3Type", bound="PathActionOutputV3")

@attr.s(auto_attribs=True)
class PathActionOutputV3(DataContract):
    projectId: str = None
    datasetId: str = None
    path: str = None
    sasToken: str = None
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
    def from_dict(cls: PathActionOutputV3Type, src_dict: Dict[str, Any]) -> PathActionOutputV3Type:
        obj = PathActionOutputV3()
        obj.load_dict(src_dict)
        return obj

PrepareHierarchyOutputV3Type = TypeVar("PrepareHierarchyOutputV3Type", bound="PrepareHierarchyOutputV3")

@attr.s(auto_attribs=True)
class PrepareHierarchyOutputV3(DataContract):
    results: List[PathActionOutputV3] = None
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
    def from_dict(cls: PrepareHierarchyOutputV3Type, src_dict: Dict[str, Any]) -> PrepareHierarchyOutputV3Type:
        obj = PrepareHierarchyOutputV3()
        obj.load_dict(src_dict)
        return obj

class TransferStatusV3(str, Enum):
    NONE = "None"
    PENDING = "Pending"
    INPROGRESS = "InProgress"
    COMPLETED = "Completed"
    ERROR = "Error"
    def __str__(self) -> str:
        return str(self.value)

class SortOrderV3(str, Enum):
    ASC = "Asc"
    DESC = "Desc"
    def __str__(self) -> str:
        return str(self.value)

DatasetTransferInputV3Type = TypeVar("DatasetTransferInputV3Type", bound="DatasetTransferInputV3")

@attr.s(auto_attribs=True)
class DatasetTransferInputV3(DataContract):
    name: str = None
    description: str = None
    metadata: str = None
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
    def from_dict(cls: DatasetTransferInputV3Type, src_dict: Dict[str, Any]) -> DatasetTransferInputV3Type:
        obj = DatasetTransferInputV3()
        obj.load_dict(src_dict)
        return obj

UploadInputV3Type = TypeVar("UploadInputV3Type", bound="UploadInputV3")

@attr.s(auto_attribs=True)
class UploadInputV3(DataContract):
    format: str = None
    projectId: str = None
    appendDatasetId: str = None
    uploadUrl: str = None
    fileName: str = None
    srid: int = None
    arguments: str = None
    destinations: List[ImportDestinationV3] = None
    datasetImportData: DatasetTransferInputV3 = None
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
    def from_dict(cls: UploadInputV3Type, src_dict: Dict[str, Any]) -> UploadInputV3Type:
        obj = UploadInputV3()
        obj.load_dict(src_dict)
        return obj

ProjectListOutputCursorResponseV3Type = TypeVar("ProjectListOutputCursorResponseV3Type", bound="ProjectListOutputCursorResponseV3")

@attr.s(auto_attribs=True)
class ProjectListOutputCursorResponseV3(DataContract):
    cursor: str = None
    data: List[ProjectListOutputV3] = None
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
    def from_dict(cls: ProjectListOutputCursorResponseV3Type, src_dict: Dict[str, Any]) -> ProjectListOutputCursorResponseV3Type:
        obj = ProjectListOutputCursorResponseV3()
        obj.load_dict(src_dict)
        return obj

class UnitIdV3(str, Enum):
    EUMUMETER = "eumUmeter"
    EUMUKILOMETER = "eumUkilometer"
    EUMUMILLIMETER = "eumUmillimeter"
    EUMUINCH = "eumUinch"
    EUMUFEET = "eumUfeet"
    EUMUYARD = "eumUyard"
    EUMUMILE = "eumUmile"
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
    EUMUPERCENTPERMINUTE = "eumUpercentPerMinute"
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
    EUMUUNITUNDEFINED = "eumUUnitUndefined"
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

ItemRedefinitionV3Type = TypeVar("ItemRedefinitionV3Type", bound="ItemRedefinitionV3")

@attr.s(auto_attribs=True)
class ItemRedefinitionV3(DataContract):
    originalName: str = None
    newName: str = None
    newItemId: ItemIdV3 = None
    newUnitId: UnitIdV3 = None
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
    def from_dict(cls: ItemRedefinitionV3Type, src_dict: Dict[str, Any]) -> ItemRedefinitionV3Type:
        obj = ItemRedefinitionV3()
        obj.load_dict(src_dict)
        return obj

PathActionDeleteV3Type = TypeVar("PathActionDeleteV3Type", bound="PathActionDeleteV3")

@attr.s(auto_attribs=True)
class PathActionDeleteV3(PathActionV3):
    type: str = "PathActionDelete"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = PathActionV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PathActionDeleteV3Type, src_dict: Dict[str, Any]) -> PathActionDeleteV3Type:
        obj = PathActionDeleteV3()
        obj.load_dict(src_dict)
        return obj

ProjectRecursiveListOutputV3Type = TypeVar("ProjectRecursiveListOutputV3Type", bound="ProjectRecursiveListOutputV3")

@attr.s(auto_attribs=True)
class ProjectRecursiveListOutputV3(DataContract):
    id: str = None
    parentProjectId: str = None
    name: str = None
    relativePath: str = None
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
    def from_dict(cls: ProjectRecursiveListOutputV3Type, src_dict: Dict[str, Any]) -> ProjectRecursiveListOutputV3Type:
        obj = ProjectRecursiveListOutputV3()
        obj.load_dict(src_dict)
        return obj

ProjectRecursiveListOutputPagedCollectionResponseV3Type = TypeVar("ProjectRecursiveListOutputPagedCollectionResponseV3Type", bound="ProjectRecursiveListOutputPagedCollectionResponseV3")

@attr.s(auto_attribs=True)
class ProjectRecursiveListOutputPagedCollectionResponseV3(DataContract):
    totalCount: int = None
    offset: int = None
    limit: int = None
    data: List[ProjectRecursiveListOutputV3] = None
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
    def from_dict(cls: ProjectRecursiveListOutputPagedCollectionResponseV3Type, src_dict: Dict[str, Any]) -> ProjectRecursiveListOutputPagedCollectionResponseV3Type:
        obj = ProjectRecursiveListOutputPagedCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

PathActionCreateV3Type = TypeVar("PathActionCreateV3Type", bound="PathActionCreateV3")

@attr.s(auto_attribs=True)
class PathActionCreateV3(PathActionV3):
    type: str = "PathActionCreate"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = PathActionV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PathActionCreateV3Type, src_dict: Dict[str, Any]) -> PathActionCreateV3Type:
        obj = PathActionCreateV3()
        obj.load_dict(src_dict)
        return obj

StringCollectionResponseV3Type = TypeVar("StringCollectionResponseV3Type", bound="StringCollectionResponseV3")

@attr.s(auto_attribs=True)
class StringCollectionResponseV3(DataContract):
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
    def from_dict(cls: StringCollectionResponseV3Type, src_dict: Dict[str, Any]) -> StringCollectionResponseV3Type:
        obj = StringCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

RowVersionInputV3Type = TypeVar("RowVersionInputV3Type", bound="RowVersionInputV3")

@attr.s(auto_attribs=True)
class RowVersionInputV3(DataContract):
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
    def from_dict(cls: RowVersionInputV3Type, src_dict: Dict[str, Any]) -> RowVersionInputV3Type:
        obj = RowVersionInputV3()
        obj.load_dict(src_dict)
        return obj

class AggregationTypeV3(str, Enum):
    MAX = "Max"
    MIN = "Min"
    AVG = "Avg"
    WEIGHTEDSUM = "WeightedSum"
    def __str__(self) -> str:
        return str(self.value)

AggregationV3Type = TypeVar("AggregationV3Type", bound="AggregationV3")

@attr.s(auto_attribs=True)
class AggregationV3(DataContract):
    itemsFilter: ItemsFilterV3 = None
    aggregationType: AggregationTypeV3 = None
    expression: str = None
    aggregatedItemName: str = None
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
    def from_dict(cls: AggregationV3Type, src_dict: Dict[str, Any]) -> AggregationV3Type:
        obj = AggregationV3()
        obj.load_dict(src_dict)
        return obj

class ProjectSortPropertyV3(str, Enum):
    NAME = "Name"
    CREATEDAT = "CreatedAt"
    UPDATEDAT = "UpdatedAt"
    ACCESSLEVEL = "AccessLevel"
    def __str__(self) -> str:
        return str(self.value)

DatasetOutputCollectionResponseV3Type = TypeVar("DatasetOutputCollectionResponseV3Type", bound="DatasetOutputCollectionResponseV3")

@attr.s(auto_attribs=True)
class DatasetOutputCollectionResponseV3(DataContract):
    data: List[DatasetOutputV3] = None
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
    def from_dict(cls: DatasetOutputCollectionResponseV3Type, src_dict: Dict[str, Any]) -> DatasetOutputCollectionResponseV3Type:
        obj = DatasetOutputCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

PathActionCreateIfNotExistsV3Type = TypeVar("PathActionCreateIfNotExistsV3Type", bound="PathActionCreateIfNotExistsV3")

@attr.s(auto_attribs=True)
class PathActionCreateIfNotExistsV3(PathActionV3):
    type: str = "PathActionCreateIfNotExists"
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = PathActionV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PathActionCreateIfNotExistsV3Type, src_dict: Dict[str, Any]) -> PathActionCreateIfNotExistsV3Type:
        obj = PathActionCreateIfNotExistsV3()
        obj.load_dict(src_dict)
        return obj

ParameterInputV3Type = TypeVar("ParameterInputV3Type", bound="ParameterInputV3")

@attr.s(auto_attribs=True)
class ParameterInputV3(DataContract):
    name: str = None
    value: None = None
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
    def from_dict(cls: ParameterInputV3Type, src_dict: Dict[str, Any]) -> ParameterInputV3Type:
        obj = ParameterInputV3()
        obj.load_dict(src_dict)
        return obj

EditThumbnailInputV3Type = TypeVar("EditThumbnailInputV3Type", bound="EditThumbnailInputV3")

@attr.s(auto_attribs=True)
class EditThumbnailInputV3(DataContract):
    thumbnailBase64: str = None
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
    def from_dict(cls: EditThumbnailInputV3Type, src_dict: Dict[str, Any]) -> EditThumbnailInputV3Type:
        obj = EditThumbnailInputV3()
        obj.load_dict(src_dict)
        return obj

class TransferTypeV3(str, Enum):
    IMPORT = "Import"
    EXPORT = "Export"
    CONVERSION = "Conversion"
    APPEND = "Append"
    UPDATE = "Update"
    def __str__(self) -> str:
        return str(self.value)

TransferSummaryOutputV3Type = TypeVar("TransferSummaryOutputV3Type", bound="TransferSummaryOutputV3")

@attr.s(auto_attribs=True)
class TransferSummaryOutputV3(DataContract):
    id: str = None
    createdAt: str = None
    createdBy: str = None
    type: TransferTypeV3 = None
    format: str = None
    status: TransferStatusV3 = None
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
    def from_dict(cls: TransferSummaryOutputV3Type, src_dict: Dict[str, Any]) -> TransferSummaryOutputV3Type:
        obj = TransferSummaryOutputV3()
        obj.load_dict(src_dict)
        return obj

UserDetailsBaseV3Type = TypeVar("UserDetailsBaseV3Type", bound="UserDetailsBaseV3")

@attr.s(auto_attribs=True)
class UserDetailsBaseV3(DataContract):
    userId: str = None
    displayName: str = None
    email: str = None
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
    def from_dict(cls: UserDetailsBaseV3Type, src_dict: Dict[str, Any]) -> UserDetailsBaseV3Type:
        obj = UserDetailsBaseV3()
        obj.load_dict(src_dict)
        return obj

UserDetailsV3Type = TypeVar("UserDetailsV3Type", bound="UserDetailsV3")

@attr.s(auto_attribs=True)
class UserDetailsV3(UserDetailsBaseV3):
    isAdmin: str = None
    customerId: str = None
    customerName: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = UserDetailsBaseV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: UserDetailsV3Type, src_dict: Dict[str, Any]) -> UserDetailsV3Type:
        obj = UserDetailsV3()
        obj.load_dict(src_dict)
        return obj

UserDetailsCollectionResponseV3Type = TypeVar("UserDetailsCollectionResponseV3Type", bound="UserDetailsCollectionResponseV3")

@attr.s(auto_attribs=True)
class UserDetailsCollectionResponseV3(DataContract):
    data: List[UserDetailsV3] = None
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
    def from_dict(cls: UserDetailsCollectionResponseV3Type, src_dict: Dict[str, Any]) -> UserDetailsCollectionResponseV3Type:
        obj = UserDetailsCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

TransferOutputV3Type = TypeVar("TransferOutputV3Type", bound="TransferOutputV3")

@attr.s(auto_attribs=True)
class TransferOutputV3(BaseEntityOutputV3):
    type: TransferTypeV3 = None
    status: TransferStatusV3 = None
    format: str = None
    projectId: str = None
    importParameters: ImportParametersV3 = None
    exportParameters: ExportParametersV3 = None
    datasetImportData: DatasetTransferInputV3 = None
    downloadPath: str = None
    errorMessage: str = None
    importResults: List[ImportResultV3] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = BaseEntityOutputV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TransferOutputV3Type, src_dict: Dict[str, Any]) -> TransferOutputV3Type:
        obj = TransferOutputV3()
        obj.load_dict(src_dict)
        return obj

RowVersionOutputV3Type = TypeVar("RowVersionOutputV3Type", bound="RowVersionOutputV3")

@attr.s(auto_attribs=True)
class RowVersionOutputV3(DataContract):
    id: str = None
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
    def from_dict(cls: RowVersionOutputV3Type, src_dict: Dict[str, Any]) -> RowVersionOutputV3Type:
        obj = RowVersionOutputV3()
        obj.load_dict(src_dict)
        return obj

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

DatasetSummaryOutputV3Type = TypeVar("DatasetSummaryOutputV3Type", bound="DatasetSummaryOutputV3")

@attr.s(auto_attribs=True)
class DatasetSummaryOutputV3(DataContract):
    id: str = None
    name: str = None
    datasetType: DatasetTypeV3 = None
    dataPath: str = None
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
    def from_dict(cls: DatasetSummaryOutputV3Type, src_dict: Dict[str, Any]) -> DatasetSummaryOutputV3Type:
        obj = DatasetSummaryOutputV3()
        obj.load_dict(src_dict)
        return obj

DatasetSummaryOutputCollectionResponseV3Type = TypeVar("DatasetSummaryOutputCollectionResponseV3Type", bound="DatasetSummaryOutputCollectionResponseV3")

@attr.s(auto_attribs=True)
class DatasetSummaryOutputCollectionResponseV3(DataContract):
    data: List[DatasetSummaryOutputV3] = None
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
    def from_dict(cls: DatasetSummaryOutputCollectionResponseV3Type, src_dict: Dict[str, Any]) -> DatasetSummaryOutputCollectionResponseV3Type:
        obj = DatasetSummaryOutputCollectionResponseV3()
        obj.load_dict(src_dict)
        return obj

TransformationV3Type = TypeVar("TransformationV3Type", bound="TransformationV3")

@attr.s(auto_attribs=True)
class TransformationV3(DataContract):
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
    def from_dict(cls: TransformationV3Type, src_dict: Dict[str, Any]) -> TransformationV3Type:
        obj = TransformationV3()
        obj.load_dict(src_dict)
        return obj

TemporalFilterTransformationV3Type = TypeVar("TemporalFilterTransformationV3Type", bound="TemporalFilterTransformationV3")

@attr.s(auto_attribs=True)
class TemporalFilterTransformationV3(TransformationV3):
    temporalFilter: TemporalFilterV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TemporalFilterTransformationV3Type, src_dict: Dict[str, Any]) -> TemporalFilterTransformationV3Type:
        obj = TemporalFilterTransformationV3()
        obj.load_dict(src_dict)
        return obj

AggregationTransformationV3Type = TypeVar("AggregationTransformationV3Type", bound="AggregationTransformationV3")

@attr.s(auto_attribs=True)
class AggregationTransformationV3(TransformationV3):
    aggregations: List[AggregationV3] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AggregationTransformationV3Type, src_dict: Dict[str, Any]) -> AggregationTransformationV3Type:
        obj = AggregationTransformationV3()
        obj.load_dict(src_dict)
        return obj

ConvertAppendInputV3Type = TypeVar("ConvertAppendInputV3Type", bound="ConvertAppendInputV3")

@attr.s(auto_attribs=True)
class ConvertAppendInputV3(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertAppendInputV3Type, src_dict: Dict[str, Any]) -> ConvertAppendInputV3Type:
        obj = ConvertAppendInputV3()
        obj.load_dict(src_dict)
        return obj

MoveInputV3Type = TypeVar("MoveInputV3Type", bound="MoveInputV3")

@attr.s(auto_attribs=True)
class MoveInputV3(DataContract):
    targetProjectId: str = None
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
    def from_dict(cls: MoveInputV3Type, src_dict: Dict[str, Any]) -> MoveInputV3Type:
        obj = MoveInputV3()
        obj.load_dict(src_dict)
        return obj

ItemTransformationV3Type = TypeVar("ItemTransformationV3Type", bound="ItemTransformationV3")

@attr.s(auto_attribs=True)
class ItemTransformationV3(TransformationV3):
    itemRedefinitions: List[ItemRedefinitionV3] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemTransformationV3Type, src_dict: Dict[str, Any]) -> ItemTransformationV3Type:
        obj = ItemTransformationV3()
        obj.load_dict(src_dict)
        return obj

VerticalFilterV3Type = TypeVar("VerticalFilterV3Type", bound="VerticalFilterV3")

@attr.s(auto_attribs=True)
class VerticalFilterV3(DataContract):
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
    def from_dict(cls: VerticalFilterV3Type, src_dict: Dict[str, Any]) -> VerticalFilterV3Type:
        obj = VerticalFilterV3()
        obj.load_dict(src_dict)
        return obj

VerticalIndexFilterV3Type = TypeVar("VerticalIndexFilterV3Type", bound="VerticalIndexFilterV3")

@attr.s(auto_attribs=True)
class VerticalIndexFilterV3(VerticalFilterV3):
    from_: int = None
    to: int = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalIndexFilterV3Type, src_dict: Dict[str, Any]) -> VerticalIndexFilterV3Type:
        obj = VerticalIndexFilterV3()
        obj.load_dict(src_dict)
        return obj

EditProjectInputV3Type = TypeVar("EditProjectInputV3Type", bound="EditProjectInputV3")

@attr.s(auto_attribs=True)
class EditProjectInputV3(DataContract):
    id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    settings: str = None
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
    def from_dict(cls: EditProjectInputV3Type, src_dict: Dict[str, Any]) -> EditProjectInputV3Type:
        obj = EditProjectInputV3()
        obj.load_dict(src_dict)
        return obj

CsScriptValueTransformationV3Type = TypeVar("CsScriptValueTransformationV3Type", bound="CsScriptValueTransformationV3")

@attr.s(auto_attribs=True)
class CsScriptValueTransformationV3(TransformationV3):
    csScript: str = None
    items: List[str] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CsScriptValueTransformationV3Type, src_dict: Dict[str, Any]) -> CsScriptValueTransformationV3Type:
        obj = CsScriptValueTransformationV3()
        obj.load_dict(src_dict)
        return obj

ProjectMemberInputV3Type = TypeVar("ProjectMemberInputV3Type", bound="ProjectMemberInputV3")

@attr.s(auto_attribs=True)
class ProjectMemberInputV3(DataContract):
    userId: str = None
    role: str = None
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
    def from_dict(cls: ProjectMemberInputV3Type, src_dict: Dict[str, Any]) -> ProjectMemberInputV3Type:
        obj = ProjectMemberInputV3()
        obj.load_dict(src_dict)
        return obj

ConvertFileUpdateInputV3Type = TypeVar("ConvertFileUpdateInputV3Type", bound="ConvertFileUpdateInputV3")

@attr.s(auto_attribs=True)
class ConvertFileUpdateInputV3(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertFileUpdateInputV3Type, src_dict: Dict[str, Any]) -> ConvertFileUpdateInputV3Type:
        obj = ConvertFileUpdateInputV3()
        obj.load_dict(src_dict)
        return obj

CrsTransformationV3Type = TypeVar("CrsTransformationV3Type", bound="CrsTransformationV3")

@attr.s(auto_attribs=True)
class CrsTransformationV3(TransformationV3):
    inputSrid: int = None
    outputSrid: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CrsTransformationV3Type, src_dict: Dict[str, Any]) -> CrsTransformationV3Type:
        obj = CrsTransformationV3()
        obj.load_dict(src_dict)
        return obj

VerticalValueFilterV3Type = TypeVar("VerticalValueFilterV3Type", bound="VerticalValueFilterV3")

@attr.s(auto_attribs=True)
class VerticalValueFilterV3(VerticalFilterV3):
    from_: float = None
    to: float = None
    __renamed = { "from": "from_" }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = VerticalFilterV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalValueFilterV3Type, src_dict: Dict[str, Any]) -> VerticalValueFilterV3Type:
        obj = VerticalValueFilterV3()
        obj.load_dict(src_dict)
        return obj

ConvertUploadInputV3Type = TypeVar("ConvertUploadInputV3Type", bound="ConvertUploadInputV3")

@attr.s(auto_attribs=True)
class ConvertUploadInputV3(DataContract):
    originalFileName: str = None
    uploadUrl: str = None
    outputDatasetData: DatasetTransferInputV3 = None
    projectId: str = None
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertUploadInputV3Type, src_dict: Dict[str, Any]) -> ConvertUploadInputV3Type:
        obj = ConvertUploadInputV3()
        obj.load_dict(src_dict)
        return obj

SetProjectMembersInputV3Type = TypeVar("SetProjectMembersInputV3Type", bound="SetProjectMembersInputV3")

@attr.s(auto_attribs=True)
class SetProjectMembersInputV3(DataContract):
    members: List[ProjectMemberInputV3] = None
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
    def from_dict(cls: SetProjectMembersInputV3Type, src_dict: Dict[str, Any]) -> SetProjectMembersInputV3Type:
        obj = SetProjectMembersInputV3()
        obj.load_dict(src_dict)
        return obj

ItemFilterTransformationV3Type = TypeVar("ItemFilterTransformationV3Type", bound="ItemFilterTransformationV3")

@attr.s(auto_attribs=True)
class ItemFilterTransformationV3(TransformationV3):
    itemFilter: ItemFilterV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ItemFilterTransformationV3Type, src_dict: Dict[str, Any]) -> ItemFilterTransformationV3Type:
        obj = ItemFilterTransformationV3()
        obj.load_dict(src_dict)
        return obj

SpatialFilterTransformationV3Type = TypeVar("SpatialFilterTransformationV3Type", bound="SpatialFilterTransformationV3")

@attr.s(auto_attribs=True)
class SpatialFilterTransformationV3(TransformationV3):
    spatialFilter: SpatialFilterV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: SpatialFilterTransformationV3Type, src_dict: Dict[str, Any]) -> SpatialFilterTransformationV3Type:
        obj = SpatialFilterTransformationV3()
        obj.load_dict(src_dict)
        return obj

VerticalFilterTransformationV3Type = TypeVar("VerticalFilterTransformationV3Type", bound="VerticalFilterTransformationV3")

@attr.s(auto_attribs=True)
class VerticalFilterTransformationV3(TransformationV3):
    verticalFilter: VerticalFilterV3 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = TransformationV3.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: VerticalFilterTransformationV3Type, src_dict: Dict[str, Any]) -> VerticalFilterTransformationV3Type:
        obj = VerticalFilterTransformationV3()
        obj.load_dict(src_dict)
        return obj

ConvertDownloadInputV3Type = TypeVar("ConvertDownloadInputV3Type", bound="ConvertDownloadInputV3")

@attr.s(auto_attribs=True)
class ConvertDownloadInputV3(DataContract):
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    targetFileName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertDownloadInputV3Type, src_dict: Dict[str, Any]) -> ConvertDownloadInputV3Type:
        obj = ConvertDownloadInputV3()
        obj.load_dict(src_dict)
        return obj

ConvertExistingInputV3Type = TypeVar("ConvertExistingInputV3Type", bound="ConvertExistingInputV3")

@attr.s(auto_attribs=True)
class ConvertExistingInputV3(DataContract):
    outputDatasetData: DatasetTransferInputV3 = None
    outputProjectId: str = None
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertExistingInputV3Type, src_dict: Dict[str, Any]) -> ConvertExistingInputV3Type:
        obj = ConvertExistingInputV3()
        obj.load_dict(src_dict)
        return obj

ConvertDatasetUpdateInputV3Type = TypeVar("ConvertDatasetUpdateInputV3Type", bound="ConvertDatasetUpdateInputV3")

@attr.s(auto_attribs=True)
class ConvertDatasetUpdateInputV3(DataContract):
    readerParameters: List[ParameterInputV3] = None
    writerParameters: List[ParameterInputV3] = None
    readerName: str = None
    writerName: str = None
    transformations: List[TransformationV3] = None
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
    def from_dict(cls: ConvertDatasetUpdateInputV3Type, src_dict: Dict[str, Any]) -> ConvertDatasetUpdateInputV3Type:
        obj = ConvertDatasetUpdateInputV3()
        obj.load_dict(src_dict)
        return obj

CreateProjectInputV3Type = TypeVar("CreateProjectInputV3Type", bound="CreateProjectInputV3")

@attr.s(auto_attribs=True)
class CreateProjectInputV3(DataContract):
    name: str = None
    accessLevel: AccessLevelV3 = None
    description: str = None
    thumbnailBase64: str = None
    metadata: str = None
    settings: str = None
    members: List[ProjectMemberInputV3] = None
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
    def from_dict(cls: CreateProjectInputV3Type, src_dict: Dict[str, Any]) -> CreateProjectInputV3Type:
        obj = CreateProjectInputV3()
        obj.load_dict(src_dict)
        return obj

DownloadInputV3Type = TypeVar("DownloadInputV3Type", bound="DownloadInputV3")

@attr.s(auto_attribs=True)
class DownloadInputV3(DataContract):
    format: str = None
    srid: int = None
    arguments: str = None
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
    def from_dict(cls: DownloadInputV3Type, src_dict: Dict[str, Any]) -> DownloadInputV3Type:
        obj = DownloadInputV3()
        obj.load_dict(src_dict)
        return obj

class MetadataGenClientV3(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)

    def UploadV3(self, body) -> Response:
        """Register new upload transfer

        TransferUpload
        POST /api/conversion/upload
        """
        return self.PostRequest("/api/conversion/upload", body, None, api_version="3")

    def UploadConvertV3(self, body) -> Response:
        """Register new upload transfer

        TransferUpload
        POST /api/conversion/upload-convert
        """
        return self.PostRequest("/api/conversion/upload-convert", body, None, api_version="3")

    def GetUserList(self) -> Response:
        """Customer

        GET /api/customer/user/list
        """
        return self.GetRequest("/api/customer/user/list", None, api_version="3")

    def GetServiceIds(self) -> Response:
        """List available Service IDs

        Gateway
        GET /api/data/services
        """
        return self.GetRequest("/api/data/services", None)

    def PrepareHierarchy(self, body, id) -> Response:
        """BulkHierarchy

        POST /api/hierarchy/project/{id}
        """
        return self.PostRequest(f"/api/hierarchy/project/{id}", body, None, api_version="3")

    def GetDatasetV3(self, id) -> Response:
        """Dataset

        GET /api/metadata/dataset/{id}
        """
        return self.GetRequest(f"/api/metadata/dataset/{id}", None, api_version="3")

    def DeleteDatasetV3(self, id) -> Response:
        """Moves the dataset into the recycle-bin

        Dataset
        DELETE /api/metadata/dataset/{id}
        """
        return self.DeleteRequest(f"/api/metadata/dataset/{id}", None, api_version="3")

    def AppendDatasetV3(self, body, id) -> Response:
        """Append data to existing dataset.

        Dataset
        POST /api/metadata/dataset/{id}/append
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/append", body, None, api_version="3")

    def ConvertDatasetV3(self, body, id) -> Response:
        """Dataset

        POST /api/metadata/dataset/{id}/convert
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/convert", body, None, api_version="3")

    def DownloadDatasetV3(self, body, id) -> Response:
        """Download the dataset

        Dataset
        POST /api/metadata/dataset/{id}/download
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/download", body, None, api_version="3")

    def DownloadConvertDatasetV3(self, body, id) -> Response:
        """Download the dataset with conversion

        Dataset
        POST /api/metadata/dataset/{id}/download-convert
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/download-convert", body, None, api_version="3")

    def MoveDatasetV3(self, body, id) -> Response:
        """Move the dataset

        Dataset
        POST /api/metadata/dataset/{id}/move
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/move", body, None, api_version="3")

    def UpdateFromFileV3(self, body, id) -> Response:
        """Update data from existing dataset.

        Dataset
        POST /api/metadata/dataset/{id}/update
        """
        return self.PostRequest(f"/api/metadata/dataset/{id}/update", body, None, api_version="3")

    def UpdateFromDatasetV3(self, body, sourceid, targetid) -> Response:
        """Update data of existing dataset.

        Dataset
        POST /api/metadata/dataset/{sourceId}/update/{targetId}
        """
        return self.PostRequest(f"/api/metadata/dataset/{sourceid}/update/{targetid}", body, None, api_version="3")

    def CreateProjectV3(self, body) -> Response:
        """Project

        POST /api/metadata/project
        """
        return self.PostRequest("/api/metadata/project", body, None, api_version="3")

    def UpdateProjectV3(self, body) -> Response:
        """Project

        PUT /api/metadata/project
        """
        return self.PutRequest("/api/metadata/project", body, None, api_version="3")

    def UpdateProjectAccessLevelV3(self, body) -> Response:
        """Updates the project access level

        Project
        PATCH /api/metadata/project
        """
        return self.PatchRequest("/api/metadata/project", body, None, api_version="3")

    def GetProjectV3(self, id) -> Response:
        """Project

        GET /api/metadata/project/{id}
        """
        return self.GetRequest(f"/api/metadata/project/{id}", None, api_version="3")

    def DeleteProjectV3(self, id) -> Response:
        """Moves the project into the recycle-bin

        Project
        DELETE /api/metadata/project/{id}
        """
        return self.DeleteRequest(f"/api/metadata/project/{id}", None, api_version="3")

    def GetProjectCapabilitiesV3(self, id) -> Response:
        """Project

        GET /api/metadata/project/{id}/capabilities
        """
        return self.GetRequest(f"/api/metadata/project/{id}/capabilities", None, api_version="3")

    def UpdateDatasetV3(self, body, id) -> Response:
        """Dataset

        PUT /api/metadata/project/{id}/dataset
        """
        return self.PutRequest(f"/api/metadata/project/{id}/dataset", body, None, api_version="3")

    def GetDatasetListV3(self, id, includesastokens=None) -> Response:
        """Dataset

        GET /api/metadata/project/{id}/dataset/list
        """
        queryparams = self.GetQueryParams(includeSasTokens=includesastokens)
        return self.GetRequest(f"/api/metadata/project/{id}/dataset/list", queryparams, api_version="3")

    def GetDatasetSummariesListV3(self, id) -> Response:
        """Dataset

        GET /api/metadata/project/{id}/dataset/list-summaries
        """
        return self.GetRequest(f"/api/metadata/project/{id}/dataset/list-summaries", None, api_version="3")

    def GetRecursiveDatasetListV3(self, id, offset=None, limit=None, datasettype=None, includesastokens=None) -> Response:
        """Dataset

        GET /api/metadata/project/{id}/dataset/recursive-list
        """
        queryparams = self.GetQueryParams(Offset=offset, Limit=limit, datasetType=datasettype, includeSasTokens=includesastokens)
        return self.GetRequest(f"/api/metadata/project/{id}/dataset/recursive-list", queryparams, api_version="3")

    def GetProjectMemberV3(self, id) -> Response:
        """ProjectMember

        GET /api/metadata/project/{id}/member
        """
        return self.GetRequest(f"/api/metadata/project/{id}/member", None, api_version="3")

    def CreateProjectMemberV3(self, body, id) -> Response:
        """ProjectMember

        POST /api/metadata/project/{id}/member
        """
        return self.PostRequest(f"/api/metadata/project/{id}/member", body, None, api_version="3")

    def DeleteProjectMemberV3(self, memberid, id) -> Response:
        """ProjectMember

        DELETE /api/metadata/project/{id}/member/{memberId}
        """
        return self.DeleteRequest(f"/api/metadata/project/{id}/member/{memberid}", None, api_version="3")

    def SetProjectMembersV3(self, body, id) -> Response:
        """Replaces the members of the given project with the given input

        ProjectMember
        PUT /api/metadata/project/{id}/members
        """
        return self.PutRequest(f"/api/metadata/project/{id}/members", body, None, api_version="3")

    def SetInheritMembersV3(self, body, id) -> Response:
        """Sets the given project to inherit members

        ProjectMember
        PUT /api/metadata/project/{id}/members/inherit
        """
        return self.PutRequest(f"/api/metadata/project/{id}/members/inherit", body, None, api_version="3")

    def MoveProjectV3(self, body, id) -> Response:
        """Moves project with id:'id' to existing project with id:'input.TargetProjectId'

        Project
        POST /api/metadata/project/{id}/move
        """
        return self.PostRequest(f"/api/metadata/project/{id}/move", body, None, api_version="3")

    def GetRecursiveProjectListV3(self, id, offset=None, limit=None) -> Response:
        """Project

        GET /api/metadata/project/{id}/offset-list-recursive
        """
        queryparams = self.GetQueryParams(offset=offset, limit=limit)
        return self.GetRequest(f"/api/metadata/project/{id}/offset-list-recursive", queryparams, api_version="3")

    def GetProjectPathV3(self, id) -> Response:
        """Project

        GET /api/metadata/project/{id}/path
        """
        return self.GetRequest(f"/api/metadata/project/{id}/path", None, api_version="3")

    def CreateSubProjectV3(self, body, id) -> Response:
        """Project

        POST /api/metadata/project/{id}/subproject
        """
        return self.PostRequest(f"/api/metadata/project/{id}/subproject", body, None, api_version="3")

    def GetSubProjectListV3(self, id, nameprefix=None, role=None, capability=None, sortby=None, sortorder=None, cursor=None, limit=None) -> Response:
        """Get list of direct subprojects of a given project.

        Project
        GET /api/metadata/project/{id}/subproject/list
        """
        queryparams = self.GetQueryParams(NamePrefix=nameprefix, Role=role, Capability=capability, SortBy=sortby, SortOrder=sortorder, Cursor=cursor, Limit=limit)
        return self.GetRequest(f"/api/metadata/project/{id}/subproject/list", queryparams, api_version="3")

    def GetSubProjectListWithOffsetV3(self, id, nameprefix=None, sortby=None, sortorder=None, offset=None, limit=None, role=None, capability=None) -> Response:
        """Get list of direct subprojects of a given project.

        Project
        GET /api/metadata/project/{id}/subproject/offset-list
        """
        queryparams = self.GetQueryParams(namePrefix=nameprefix, sortBy=sortby, sortOrder=sortorder, offset=offset, limit=limit, role=role, capability=capability)
        return self.GetRequest(f"/api/metadata/project/{id}/subproject/offset-list", queryparams, api_version="3")

    def GetSubProjectsV3(self, id) -> Response:
        """Project

        GET /api/metadata/project/{id}/subprojects
        """
        return self.GetRequest(f"/api/metadata/project/{id}/subprojects", None, api_version="3")

    def UpdateProjectThumbnailV3(self, body, id) -> Response:
        """Project

        PUT /api/metadata/project/{id}/thumbnail
        """
        return self.PutRequest(f"/api/metadata/project/{id}/thumbnail", body, None, api_version="3")

    def GetProjectListV3(self, nameprefix=None, role=None, capability=None, sortby=None, sortorder=None, cursor=None, limit=None) -> Response:
        """Get list of root-level projects.

        Project
        GET /api/metadata/project/list
        """
        queryparams = self.GetQueryParams(NamePrefix=nameprefix, Role=role, Capability=capability, SortBy=sortby, SortOrder=sortorder, Cursor=cursor, Limit=limit)
        return self.GetRequest("/api/metadata/project/list", queryparams, api_version="3")

    def GetProjectListWithOffsetV3(self, nameprefix=None, sortby=None, sortorder=None, offset=None, limit=None, role=None, capability=None) -> Response:
        """Get list of root-level projects.

        Project
        GET /api/metadata/project/offset-list
        """
        queryparams = self.GetQueryParams(namePrefix=nameprefix, sortBy=sortby, sortOrder=sortorder, offset=offset, limit=limit, role=role, capability=capability)
        return self.GetRequest("/api/metadata/project/offset-list", queryparams, api_version="3")

    def GetServiceUrlV3(self, servicename) -> Response:
        """Get baseuri for specific service

        ServiceAccess
        GET /api/services/{serviceName}/baseuri
        """
        return self.GetRequest(f"/api/services/{servicename}/baseuri", None, api_version="3")
