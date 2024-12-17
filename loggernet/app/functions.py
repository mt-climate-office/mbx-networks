from bs4 import BeautifulSoup
import httpx
from dataclasses import dataclass
from enum import Enum

all_functions = [
    "ACPower",
    "AddPrecise",
    "AM25T",
    "Average",
    "AvgRun",
    "AvgSpa",
    "ABS",
    "AcceptDataRecords",
    "ACos",
    "ASCII",
    "ASin",
    "Atn",
    "Atn2",
    "AngleDegrees",
    "ApplyandRestartSequence",
    "EndApplyandRestartSequence",
    "ArgosData",
    "ArgosDataRepeat",
    "ArgosError",
    "ArgosSetup",
    "ArgosTransmit",
    "ArrayLength",
    "AVW200",
    "ArrayIndex",
    "Battery",
    "BeginBurstTrigger",
    "BrFull",
    "BrFull6W",
    "BrHalf",
    "BrHalf3W",
    "BrHalf4W",
    "Broadcast",
    "CalFile",
    "Calibrate",
    "CHR",
    "CPIAddModule",
    "CPIFileSend",
    "CDM_ACPower",
    "CDM_Battery",
    "CDM_BrFull",
    "CDM_BrFull6W",
    "CDM_BrHalf",
    "CDM_BrHalf3W",
    "CDM_BrHalf4W",
    "CDM_Delay",
    "CDM_ExciteI",
    "CDM_ExciteV",
    "CDM_MuxSelect",
    "CDM_PanelTemp",
    "CDM_PeriodAvg",
    "CDM_PulsePort",
    "CDM_Resistance",
    "CDM_Resistance3W",
    "CDM_SW12",
    "CDM_SW5",
    "CDM_SWPower",
    "CDM_TCDiff",
    "CDM_TCSe",
    "CDM_Therm107",
    "CDM_Therm108",
    "CDM_Therm109",
    "CDM_VoltSE",
    "CDM_VoltDiff",
    "CDM_CurrentDiff",
    "CDM_VW300Config",
    "CDM_VW300Dynamic",
    "CDM_VW300Static",
    "CDM_VW300Rainflow",
    "CDM_TCComp",
    "CheckSum",
    "ClockChange",
    "ClockReport",
    "ComPortIsActive",
    "Cos",
    "CPISpeed",
    "Csgn",
    "Cosh",
    "CSAT3",
    "CSAT3B",
    "CSAT3BMonitor",
    "CS616",
    "CS7500",
    "CheckPort",
    "ClockSet",
    "Covariance",
    "CovSpa",
    "CardFlush",
    "CardOut",
    "CTYPE",
    "CWB100",
    "CWB100Diagnostics",
    "CWB100RSSI",
    "CWB100Routes",
    "Data",
    "DataLong",
    "DataGram",
    "DaylightSavingUS",
    "DaylightSaving",
    "DataTime",
    "DialVoice",
    "DataEvent",
    "DataInterval",
    "Delay",
    "DewPoint",
    "DHCPRenew",
    "DialModem",
    "DialSequence",
    "DNP",
    "DNPUpdate",
    "DNPVariable",
    "EC100",
    "EC100Configure",
    "Eqv",
    "EncryptExempt",
    "EmailSend",
    "EmailRelay",
    "EMailRecv",
    "Encryption",
    "Erase",
    "ESSInitialize",
    "ESSVariables",
    "EndDialSequence",
    "DisplayValue",
    "DisplayLine",
    "ExciteV",
    "EndBurstTrigger",
    "ExciteI",
    "ExciteCAO",
    "Exp",
    "EthernetPower",
    "I2COpen",
    "I2CRead",
    "I2CWrite",
    "SPIOpen",
    "SPIRead",
    "SPIWrite",
    "IPNetPower",
    "ETsz",
    "FFT",
    "FFTSpa",
    "FileManage",
    "FileMark",
    "FillStop",
    "FindSpa",
    "Fix",
    "FieldNames",
    "LoadFieldCal",
    "LoggerType",
    "IIF",
    "SampleFieldCal",
    "NewFieldCal",
    "NewFieldNames",
    "FieldCal",
    "FieldCalStrain",
    "FileOpen",
    "FileClose",
    "FileCopy",
    "FileEncrypt",
    "FileWrite",
    "FileRead",
    "FileReadLine",
    "FileRename",
    "FileTime",
    "FileSize",
    "FileList",
    "Frac",
    "FormatFloat",
    "FormatLong",
    "FormatLongLong",
    "FTPClient",
    "GetRecord",
    "GetDataRecord",
    "GetFile",
    "GetVariables",
    "GOESData",
    "GOESStatus",
    "GOESSetup",
    "GOESGPS",
    "GOESTable",
    "GOESField",
    "GPS",
    "Hex",
    "HexToDec",
    "Histogram",
    "Histogram4D",
    "HydraProbe",
    "HTTPGet",
    "HTTPPost",
    "HTTPPut",
    "HTTPOut",
    "TimeIntoInterval",
    "IfTime",
    "INSATSetup",
    "INSATStatus",
    "INSATData",
    "Int",
    "INTDV",
    "InStr",
    "InstructionTimes",
    "IPInfo",
    "IPRoute",
    "IPTrace",
    "IMP",
    "Len",
    "LevelCrossing",
    "LI7200",
    "LI7700",
    "LineNum",
    "Log",
    "LN",
    "Log10",
    "LowerCase",
    "Maximum",
    "MaxSpa",
    "Median",
    "MemoryTest",
    "MenuItem",
    "MenuPick",
    "MenuRecompile",
    "Mid",
    "Minimum",
    "MinSpa",
    "ModemCallback",
    "ModemHangup",
    "EndModemHangup",
    "Moment",
    "MonitorComms",
    "Move",
    "MoveBytes",
    "MovePrecise",
    "Mod",
    "ModbusMaster",
    "ModbusSlave",
    "MuxSelect",
    "NewFile",
    "Not",
    "OmniSatData",
    "OmniSatSTSetup",
    "OmniSatRandomSetup",
    "OmniSatStatus",
    "OpenInterval",
    "Optional",
    "PanelTemp",
    "PeakValley",
    "PeriodAvg",
    "PingIP",
    "PipeLineMode",
    "PreserveVariables",
    "PPPOpen",
    "PPPClose",
    "PortBridge",
    "PortGet",
    "PortSet",
    "PortsConfig",
    "PortPairConfig",
    "PRT",
    "PRTCalc",
    "PulseCount",
    "PulseCountReset",
    "PulsePort",
    "Public",
    "PWM",
    "PWR",
    "RainFlow",
    "RainFlowSample",
    "Randomize",
    "Resistance",
    "Resistance3W",
    "Read",
    "ReadIO",
    "ReadOnly",
    "RealTime",
    "RectPolar",
    "ResetTable",
    "Restore",
    "Replace",
    "Right",
    "Left",
    "RMSSpa",
    "RND",
    "Route",
    "Routes",
    "RoutersNeighbors",
    "Round",
    "Floor",
    "Ceiling",
    "RunProgram",
    "Sample",
    "SampleMaxMin",
    "SatVP",
    "SDI12Recorder",
    "SDI12SensorSetup",
    "SDI12SensorResponse",
    "SDMAO4",
    "SDMAO4A",
    "SDMBeginPort",
    "SDMCAN",
    "SDMCD16AC",
    "SDMCD16Mask",
    "SDMCVO4",
    "SDMGeneric",
    "SDMINT8",
    "SDMSpeed",
    "SDMSW8A",
    "SDMTrigger",
    "SDMX50",
    "SecsSince1990",
    "SemaphoreGet",
    "SemaphoreRelease",
    "SendData",
    "SendFile",
    "SendTableDef",
    "SendGetVariables",
    "SendVariables",
    "SerialOpen",
    "SerialClose",
    "SerialFlush",
    "SerialIn",
    "SerialInBlock",
    "SerialInChk",
    "SerialInRecord",
    "SerialOut",
    "SerialOutBlock",
    "SerialBrk",
    "SetSettings",
    "SetSecurity",
    "SetStatus",
    "SetSetting",
    "ShutDownBegin",
    "ShutDownEnd",
    "Signature",
    "SNMPVariable",
    "StaticRoute",
    "StdDev",
    "StdDevSpa",
    "Sgn",
    "Sin",
    "Sinh",
    "SDMSIO4",
    "SDMIO16",
    "SplitStr",
    "Sprintf",
    "SolarPosition",
    "SortSpa",
    "Sqr",
    "StrainCalc",
    "StrComp",
    "SW12",
    "TCSe",
    "TCDiff",
    "TCPClose",
    "TCPOpen",
    "TCPsyc",
    "TGA",
    "Therm109",
    "Therm108",
    "Therm107",
    "Thermistor",
    "TimedControl",
    "TimeIsBetween",
    "Timer",
    "Totalize",
    "TableFile",
    "TableHide",
    "Tan",
    "Tanh",
    "TDR100",
    "TDR200",
    "TimerInput",
    "TimeUntilTransmit",
    "TotalRun",
    "MinRun",
    "MaxRun",
    "Trim",
    "LTrim",
    "RTrim",
    "UDPDataGram",
    "UDPOpen",
    "Until",
    "UpperCase",
    "PakBusClock",
    "VaporPressure",
    "VibratingWire",
    "VoiceSetup",
    "VoiceSpeak",
    "VoiceBeg",
    "EndVoice",
    "VoiceKey",
    "VoiceNumber",
    "VoicePhrases",
    "VoiceHangup",
    "VoltSE",
    "VoltDiff",
    "WaitDigTrig",
    "WaitTriggerSequence",
    "TriggerSequence",
    "WebPageBegin",
    "WebPageEnd",
    "WetDryBulb",
    "WorstCase",
    "WriteIO",
    "WindVector",
    "Network",
    "NetworkTimeProtocol",
    "XMLParse",
    "TypeOf",
    "CurrentSE",
    "Matrix",
    "Gzip",
    "GOESCommand",
    "GOESCommand",
    "StructureType",
    "Quadrature",
    "SMSRecv",
    "SMSSend",
    "TCPActiveConnections",
    "WatchdogTimer",
    "MQTTConnect",
    "MQTTPublishTable",
    "MQTTPublishConstTable",
]

# URL to scrape
URL = "https://help.campbellsci.com/crbasic/cr1000x"

class TableEnum(Enum):
    pass

def parse_table(table_soup: BeautifulSoup):

    table_data = {}  # Dictionary to store data in the form {Enum: [column2, column3, ...]}

    rows = table_soup.find_all("tr")[1:]  # Exclude the header row (first <tr>)

    if len(rows) == 0:
        return None
    
    for row in rows:
        cols = row.find_all("td")  # Find all cells in the row
        if len(cols) > 0:
            option = cols[0].text.strip()  # First column: Option (Enum key)
            other_data = [col.decode_contents().strip() for col in cols[1:]]  # Other columns
            
            # Create an Enum entry dynamically
            enum_name = f"OPTION_{option}"  # Enum names like OPTION_1, OPTION_2, etc.
            setattr(TableEnum, enum_name, int(option))  # Add to the Enum
            
            # Store other column data in the dictionary
            table_data[getattr(TableEnum, enum_name)] = other_data

    return table_data


class ArgEnum(Enum):
    ...

class FunctionArgument:
    def __init__(self, name: str, description: str, options: ArgEnum | None = None, option_meta: list[str] | None = None):
        self.name = name
        self.description = description
        self.options = options
        self.option_meta = option_meta

class CSIFunction:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

function = "BrFull"
for function in all_functions:
    url = f"{URL}/Content/Instructions/{function.lower()}.htm"
    request = httpx.get(url, follow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")
    args = soup.find_all(class_="PopupHeadingTopic")
    function_args = []

    for arg in args:
        description = arg.find_next_sibling()
        table_soup = description.find_next_sibling()
        FunctionArgument(name = arg.text, description=description)
        

    csi_function = CSIFunction(
        function
    )
    