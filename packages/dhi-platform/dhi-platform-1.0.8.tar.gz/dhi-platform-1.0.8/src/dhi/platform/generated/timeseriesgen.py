# Generated using openapi2py.py
# openapi2py.py "--dhiservice" "timeseries" "--classname" "TimeSeriesGenClientV" "-n" "2" "-r" "projectid" "-f" "UploadCsvDataV2:content_type:text/plain" "-i" "datasetid=id" "--out" "C:\work\devops\mike-platform-sdk-py\src\dhi\platform\generated\timeseriesgen.py" "https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/timeseries/v2"
# 2022-01-13 19:05:02.525366Z
from typing import Any, Dict, List, NewType, Type, TypeVar, Union
from enum import Enum
import attr
from ..base.client import DataContract, PlatformClient, Response


# https://apispec-mike-platform-dev0.eu.mike-cloud-dev0.com/timeseries/v2
# DHI Water Data TimeSeries API - Version 2
# API for managing time series
# 2

class PropertyDataTypeV2(str, Enum):
    DATETIME = "DateTime"
    LONG = "Long"
    DOUBLE = "Double"
    BOOLEAN = "Boolean"
    TEXT = "Text"
    def __str__(self) -> str:
        return str(self.value)

class SpatialOperatorV2(str, Enum):
    INTERSECTS = "Intersects"
    WITHIN = "Within"
    def __str__(self) -> str:
        return str(self.value)

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

PropertiesInputV2Type = TypeVar("PropertiesInputV2Type", bound="PropertiesInputV2")

@attr.s(auto_attribs=True)
class PropertiesInputV2(DataContract):
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
    def from_dict(cls: PropertiesInputV2Type, src_dict: Dict[str, Any]) -> PropertiesInputV2Type:
        obj = PropertiesInputV2()
        obj.load_dict(src_dict)
        return obj

AnnotatedOutputV2Type = TypeVar("AnnotatedOutputV2Type", bound="AnnotatedOutputV2")

@attr.s(auto_attribs=True)
class AnnotatedOutputV2(DataContract):
    metadata: str = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AnnotatedOutputV2Type, src_dict: Dict[str, Any]) -> AnnotatedOutputV2Type:
        obj = AnnotatedOutputV2()
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

QueryFilterV2Type = TypeVar("QueryFilterV2Type", bound="QueryFilterV2")

@attr.s(auto_attribs=True)
class QueryFilterV2(DataContract):
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
    def from_dict(cls: QueryFilterV2Type, src_dict: Dict[str, Any]) -> QueryFilterV2Type:
        obj = QueryFilterV2()
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

PropertyDefinitionV2Type = TypeVar("PropertyDefinitionV2Type", bound="PropertyDefinitionV2")

@attr.s(auto_attribs=True)
class PropertyDefinitionV2(DataContract):
    name: str = None
    dataType: PropertyDataTypeV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: PropertyDefinitionV2Type, src_dict: Dict[str, Any]) -> PropertyDefinitionV2Type:
        obj = PropertyDefinitionV2()
        obj.load_dict(src_dict)
        return obj

TimeSeriesDatasetSchemaInputV2Type = TypeVar("TimeSeriesDatasetSchemaInputV2Type", bound="TimeSeriesDatasetSchemaInputV2")

@attr.s(auto_attribs=True)
class TimeSeriesDatasetSchemaInputV2(DataContract):
    properties: List[PropertyDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TimeSeriesDatasetSchemaInputV2Type, src_dict: Dict[str, Any]) -> TimeSeriesDatasetSchemaInputV2Type:
        obj = TimeSeriesDatasetSchemaInputV2()
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

PropertyInputV2Type = TypeVar("PropertyInputV2Type", bound="PropertyInputV2")

@attr.s(auto_attribs=True)
class PropertyInputV2(DataContract):
    property: str = None
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
    def from_dict(cls: PropertyInputV2Type, src_dict: Dict[str, Any]) -> PropertyInputV2Type:
        obj = PropertyInputV2()
        obj.load_dict(src_dict)
        return obj

ObjectResponseV2Type = TypeVar("ObjectResponseV2Type", bound="ObjectResponseV2")

@attr.s(auto_attribs=True)
class ObjectResponseV2(DataContract):
    data: None = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: ObjectResponseV2Type, src_dict: Dict[str, Any]) -> ObjectResponseV2Type:
        obj = ObjectResponseV2()
        obj.load_dict(src_dict)
        return obj

FlagDefinitionV2Type = TypeVar("FlagDefinitionV2Type", bound="FlagDefinitionV2")

@attr.s(auto_attribs=True)
class FlagDefinitionV2(DataContract):
    id: int = None
    name: str = None
    description: str = None
    level: int = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: FlagDefinitionV2Type, src_dict: Dict[str, Any]) -> FlagDefinitionV2Type:
        obj = FlagDefinitionV2()
        obj.load_dict(src_dict)
        return obj

class TimeSeriesDataTypeV2(str, Enum):
    INSTANTANEOUS = "Instantaneous"
    ACCUMULATED = "Accumulated"
    STEPACCUMULATED = "StepAccumulated"
    MEANSTEPBACKWARD = "MeanStepBackward"
    MEANSTEPFORWARD = "MeanStepForward"
    def __str__(self) -> str:
        return str(self.value)

AddDatasetSchemaPropertiesInputV2Type = TypeVar("AddDatasetSchemaPropertiesInputV2Type", bound="AddDatasetSchemaPropertiesInputV2")

@attr.s(auto_attribs=True)
class AddDatasetSchemaPropertiesInputV2(DataContract):
    properties: List[PropertyDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: AddDatasetSchemaPropertiesInputV2Type, src_dict: Dict[str, Any]) -> AddDatasetSchemaPropertiesInputV2Type:
        obj = AddDatasetSchemaPropertiesInputV2()
        obj.load_dict(src_dict)
        return obj

DatasetPropertiesInputV2Type = TypeVar("DatasetPropertiesInputV2Type", bound="DatasetPropertiesInputV2")

@attr.s(auto_attribs=True)
class DatasetPropertiesInputV2(DataContract):
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
    def from_dict(cls: DatasetPropertiesInputV2Type, src_dict: Dict[str, Any]) -> DatasetPropertiesInputV2Type:
        obj = DatasetPropertiesInputV2()
        obj.load_dict(src_dict)
        return obj

CreateTimeSeriesDatasetInputV2Type = TypeVar("CreateTimeSeriesDatasetInputV2Type", bound="CreateTimeSeriesDatasetInputV2")

@attr.s(auto_attribs=True)
class CreateTimeSeriesDatasetInputV2(DataContract):
    timeSeriesSchema: TimeSeriesDatasetSchemaInputV2 = None
    datasetProperties: DatasetPropertiesInputV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: CreateTimeSeriesDatasetInputV2Type, src_dict: Dict[str, Any]) -> CreateTimeSeriesDatasetInputV2Type:
        obj = CreateTimeSeriesDatasetInputV2()
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

class DataFieldDataTypeV2(str, Enum):
    DATETIME = "DateTime"
    SINGLE = "Single"
    DOUBLE = "Double"
    FLAG = "Flag"
    TEXT = "Text"
    def __str__(self) -> str:
        return str(self.value)

DataFieldDefinitionV2Type = TypeVar("DataFieldDefinitionV2Type", bound="DataFieldDefinitionV2")

@attr.s(auto_attribs=True)
class DataFieldDefinitionV2(DataContract):
    name: str = None
    dataType: DataFieldDataTypeV2 = None
    flags: List[FlagDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: DataFieldDefinitionV2Type, src_dict: Dict[str, Any]) -> DataFieldDefinitionV2Type:
        obj = DataFieldDefinitionV2()
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

ItemDefinitionV2Type = TypeVar("ItemDefinitionV2Type", bound="ItemDefinitionV2")

@attr.s(auto_attribs=True)
class ItemDefinitionV2(DataContract):
    name: str = None
    unit: UnitIdV2 = None
    item: ItemIdV2 = None
    dataType: AttributeDataTypeV2 = None
    timeSeriesType: TimeSeriesDataTypeV2 = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
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

TimeSeriesDefinitionV2Type = TypeVar("TimeSeriesDefinitionV2Type", bound="TimeSeriesDefinitionV2")

@attr.s(auto_attribs=True)
class TimeSeriesDefinitionV2(DataContract):
    id: str = None
    item: ItemDefinitionV2 = None
    properties: str = None
    dataFields: List[DataFieldDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TimeSeriesDefinitionV2Type, src_dict: Dict[str, Any]) -> TimeSeriesDefinitionV2Type:
        obj = TimeSeriesDefinitionV2()
        obj.load_dict(src_dict)
        return obj

TimeSeriesDefinitionCollectionResponseV2Type = TypeVar("TimeSeriesDefinitionCollectionResponseV2Type", bound="TimeSeriesDefinitionCollectionResponseV2")

@attr.s(auto_attribs=True)
class TimeSeriesDefinitionCollectionResponseV2(DataContract):
    data: List[TimeSeriesDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = DataContract.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TimeSeriesDefinitionCollectionResponseV2Type, src_dict: Dict[str, Any]) -> TimeSeriesDefinitionCollectionResponseV2Type:
        obj = TimeSeriesDefinitionCollectionResponseV2()
        obj.load_dict(src_dict)
        return obj

TimeSeriesDatasetOutputV2Type = TypeVar("TimeSeriesDatasetOutputV2Type", bound="TimeSeriesDatasetOutputV2")

@attr.s(auto_attribs=True)
class TimeSeriesDatasetOutputV2(AnnotatedOutputV2):
    id: str = None
    items: List[ItemDefinitionV2] = None
    timeSeriesProperties: List[PropertyDefinitionV2] = None
    __renamed = {  }
    def to_dict(self) -> Dict[str, Any]:
        return self.get_dictionary(self.get_renamed())
    def load_dict(self, src_dict: Dict[str, Any]) -> None:
        DataContract.load_from_directory(self, src_dict, self.get_renamed())
    @classmethod
    def get_renamed(cls) -> Dict[str, str]:
        result = AnnotatedOutputV2.get_renamed().copy()
        result.update(cls.__renamed)
        return result
    @classmethod
    def from_dict(cls: TimeSeriesDatasetOutputV2Type, src_dict: Dict[str, Any]) -> TimeSeriesDatasetOutputV2Type:
        obj = TimeSeriesDatasetOutputV2()
        obj.load_dict(src_dict)
        return obj

class TimeSeriesGenClientV2(PlatformClient):
    def __init__(self, inspectFnc=PlatformClient.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, includeheaders=PlatformClient.GetServiceHeaders("timeseries"), **kwargs)

    def CreateTimeseriesDatasetV2(self, projectid, body) -> Response:
        """Create a new time series dataset

        TimeSeriesCreate
        POST /api/ts/dataset
        """
        return self.PostRequest("/api/ts/dataset", body, None, api_version="2", projectid=projectid)

    def GetTimeSeriesDatasetV2(self, projectid, id) -> Response:
        """Get details about time series dataset

        TimeSeriesRead
        GET /api/ts/dataset/{id}
        """
        return self.GetRequest(f"/api/ts/dataset/{id}", None, api_version="2", projectid=projectid, datasetid=id)

    def AddDatasetSchemaPropertiesV2(self, projectid, body, id) -> Response:
        """Add new property definitions into time series dataset.

        TimeSeriesCreate
        PUT /api/ts/dataset/{id}/schema/properties
        """
        return self.PutRequest(f"/api/ts/dataset/{id}/schema/properties", body, None, api_version="2", projectid=projectid, datasetid=id)

    def AddTimeSeriesV2(self, projectid, body, id) -> Response:
        """Create a new time series

        TimeSeriesUpdate
        POST /api/ts/dataset/{id}/timeseries
        """
        return self.PostRequest(f"/api/ts/dataset/{id}/timeseries", body, None, api_version="2", projectid=projectid, datasetid=id)

    def GetAllTimeSeriesV2(self, projectid, id) -> Response:
        """Get list of dataset's time series

        TimeSeriesRead
        GET /api/ts/dataset/{id}/timeseries/list
        """
        return self.GetRequest(f"/api/ts/dataset/{id}/timeseries/list", None, api_version="2", projectid=projectid, datasetid=id)

    def GetQueryTimeSeriesV2(self, projectid, body, id) -> Response:
        """Query time series by name or property value(s)

        TimeSeriesRead
        POST /api/ts/dataset/{id}/timeseries/query
        """
        return self.PostRequest(f"/api/ts/dataset/{id}/timeseries/query", body, None, api_version="2", projectid=projectid, datasetid=id)

    def GetMultiTimeSeriesDataV2(self, projectid, body, id, from_=None, to=None) -> Response:
        """Get time series values

        TimeSeriesRead
        POST /api/ts/dataset/{id}/timeseries/values
        """
        kw = {"from": from_}
        queryparams = self.GetQueryParams(to=to, **kw)
        return self.PostRequest(f"/api/ts/dataset/{id}/timeseries/values", body, queryparams, api_version="2", projectid=projectid, datasetid=id)

    def GetTimeSeriesByIdV2(self, projectid, id, timeseriesid) -> Response:
        """Get details about time series

        TimeSeriesRead
        GET /api/ts/dataset/{id}/timeseries/{timeSeriesId}
        """
        return self.GetRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}", None, api_version="2", projectid=projectid, datasetid=id)

    def SetAllTimeSeriesPropertiesV2(self, projectid, body, id, timeseriesid) -> Response:
        """Update all time series properties

        TimeSeriesUpdate
        PUT /api/ts/dataset/{id}/timeseries/{timeSeriesId}
        """
        return self.PutRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}", body, None, api_version="2", projectid=projectid, datasetid=id)

    def DeleteTimeSeriesV2(self, projectid, id, timeseriesid) -> Response:
        """Delete time series from dataset

        TimeSeriesUpdate
        DELETE /api/ts/dataset/{id}/timeseries/{timeSeriesId}
        """
        return self.DeleteRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}", None, api_version="2", projectid=projectid, datasetid=id)

    def SetTimeSeriesPropertyV2(self, projectid, body, id, timeseriesid) -> Response:
        """Update a single time series property

        TimeSeriesUpdate
        PUT /api/ts/dataset/{id}/timeseries/{timeSeriesId}/property
        """
        return self.PutRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}/property", body, None, api_version="2", projectid=projectid, datasetid=id)

    def UploadCsvDataV2(self, projectid, body, id, timeseriesid, datetimeindex, delimiter, decimalseparator, valueindex=None, flagindex=None, **kwargs) -> Response:
        """Append time series data in CSV format

        Upload
        POST /api/ts/dataset/{id}/timeseries/{timeSeriesId}/upload/csv
        """
        queryparams = self.GetQueryParams(datetimeIndex=datetimeindex, delimiter=delimiter, decimalSeparator=decimalseparator, valueIndex=valueindex, flagIndex=flagindex)
        return self.PostRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}/upload/csv", body, queryparams, api_version="2", projectid=projectid, datasetid=id, content_type="text/plain")

    def UploadJsonDataV2(self, projectid, id, timeseriesid) -> Response:
        """Append time series data in JSON format

        Upload
        POST /api/ts/dataset/{id}/timeseries/{timeSeriesId}/upload/json
        """
        return self.PostRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}/upload/json", None, None, api_version="2", projectid=projectid, datasetid=id)

    def GetTimeSeriesDataV2(self, projectid, id, timeseriesid, from_=None, to=None) -> Response:
        """Get time series values

        TimeSeriesRead
        GET /api/ts/dataset/{id}/timeseries/{timeSeriesId}/values
        """
        kw = {"from": from_}
        queryparams = self.GetQueryParams(to=to, **kw)
        return self.GetRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}/values", queryparams, api_version="2", projectid=projectid, datasetid=id)

    def DeleteTimeSeriesValuesV2(self, projectid, id, timeseriesid, from_=None, to=None) -> Response:
        """Delete time series values

        TimeSeriesUpdate
        DELETE /api/ts/dataset/{id}/timeseries/{timeSeriesId}/values
        """
        kw = {"from": from_}
        queryparams = self.GetQueryParams(to=to, **kw)
        return self.DeleteRequest(f"/api/ts/dataset/{id}/timeseries/{timeseriesid}/values", queryparams, api_version="2", projectid=projectid, datasetid=id)
