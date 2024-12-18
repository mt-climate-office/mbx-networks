from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx
from dataclasses import dataclass, field
from enum import Enum
from textwrap import dedent
from instruments import Variable
import re

from typing import NewType

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
    # "ApplyandRestartSequence", # This is a directive
    # "EndApplyandRestartSequence",
    "ArgosData",
    "ArgosDataRepeat",
    "ArgosError",
    "ArgosSetup",
    "ArgosTransmit",
    "ArrayLength",
    "AVW200",
    "ArrayIndex",
    "Battery",
    # "BeginBurstTrigger",
    "BrFull",
    "BrFull6W",
    "BrHalf",
    "BrHalf3W",
    "BrHalf4W",
    "Broadcast",
    "CalFile",
    "Calibrate",
    "CHR",
    # "CPIAddModule",
    # "CPIFileSend",
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
    # "SemaphoreGet",
    # "SemaphoreRelease",
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
    # "ShutDownBegin", This is a directive
    # "ShutDownEnd",
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
    "TGA",
    "Therm109",
    "Therm108",
    "Therm107",
    # "Thermistor",
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
    # "Until",
    "UpperCase",
    "PakBusClock",
    "VaporPressure",
    # "VibratingWire",
    # "VoiceSetup",
    # "VoiceSpeak",
    # "VoiceBeg",
    # "EndVoice",
    # "VoiceKey",
    # "VoiceNumber",
    # "VoicePhrases",
    # "VoiceHangup",
    "VoltSE",
    "VoltDiff",
    "WaitDigTrig",
    # "WaitTriggerSequence",
    # "TriggerSequence",
    # "WebPageBegin",
    # "WebPageEnd",
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

URL = "https://help.campbellsci.com/crbasic/cr1000x"
Constant = NewType("Constant", int)
Expression = NewType("Expression", str)
Array = NewType("Array", Variable)
Integer = NewType("Integer", int)
ConstantInteger = NewType("ConstantInteger", int)


TYPES = ["Variable", "Constant", "Expression", "Array", "Integer", "ConstantInteger"]

class ArgEnum(Enum):
    pass


@dataclass
class ArgOptions:
    choices: str | int
    description: str


def parse_table(table_soup: BeautifulSoup) -> list[ArgOptions]:
    rows = table_soup.find_all("tr")[1:]  

    if len(rows) == 0:
        return None
    
    options = []

    for row in rows:
        cols = row.find_all("td")  
        if len(cols) > 0:

            options.append(ArgOptions(
                cols[0].text.strip().split(" ")[0],
                cols[1].text.strip()
            ))

    return options


@dataclass
class FunctionArgument:
    name: str
    short_name: str
    description: str
    type: list[str] = None
    options: list[ArgOptions] | None = None

    def __post_init__(self):
        if self.type is None:
            self.type = ["Constant"]


def clean_string(s: str):
    s = s.replace('\xa0', ' ')
    s = s.replace('\r', '')
    s = s.replace('\n', '')
    return s

class CSIFunction:
    def __init__(self, *args: FunctionArgument, name: str, source: str, remarks: str):
        self.name = name
        self.source = source
        self.remarks = remarks
        self.args = args
    
    def __str__(self):

        args = ", ".join(
            f"{obj.short_name}: {'Literal[' + ', '.join(f'"{x.choices}"' for x in obj.options) + ']' if obj.options is not None else ' | '.join(obj.type)}" 
            if hasattr(obj, 'type') else obj.short_name 
            for obj in self.args
        )
        return_args = f"{','.join([f'{{{x.short_name}}}' for x in self.args])}"
        arg_descriptions = "\n\t\t".join(
            f"{obj.short_name} ({' | '.join(obj.type)}): {obj.description}" + 
            (f"\n\t\t  Must be one of following options: {', '.join(f'{x.choices} ({x.description})' for x in obj.options)}\n" if obj.options is not None else "\n")
            for obj in self.args
        )
        return dedent(f'''
        def {self.name}({args}) -> str:
            """For a full description of this function, visit [{self.source}]({self.source}).
            
            {self.remarks}
            
            Args:
                {arg_descriptions}
            Returns:
                str: A string of the CRBasic function call.
            """
            return f"{self.name}({return_args})"
        ''')


def get_meta(description: Tag) -> str:
    meta = {
        "table": None,
        "type": None,
        "description": []
    }

    description = arg
    while 'PopupHeadingTopic' not in (description := description.find_next_sibling()).get("class", []):
        if description.name == "h2":
            break
        if description.name == "table":
            table = parse_table(description)
            meta['table'] = table
        elif description.text.startswith("Type:"):
            types = [x for x in TYPES if x in description.text]
            meta['type'] = types
        else:
            meta['description'].append(clean_string(description.text))

        if description.find_next_sibling() is None:
            break
    
    return meta


def get_remarks(soup: BeautifulSoup):
    remarks_tag = soup.find(string="Remarks")
    if remarks_tag is None:
        return ""
    description = remarks_tag.find_parent()
    out = []
    while (description := description.find_next_sibling()).name != "h2":
        if description.find_next_sibling() is None:
            break
        if description.find_previous_sibling().find("img"):
            continue
        if description.name == "p":
            out.append(clean_string(description.text))
        

    if len(out) == 0:
        return ""

    out = [x.strip() for x in out]
    out = [x for x in out if x != '']
    out = [x for x in out if len(x) > 25]
    out = [x.replace ("\n", " ") for x in out]
    return "\n".join(out)

fun_def = []
for function in all_functions:
    if "Therm10" in (url_str := function):
        strs = ["therm107", "therm108", "therm109"]
        if "CDM" in url_str:
            strs = [f"cdm{x}" for x in strs]
        url_str = "".join(strs)
    if url_str in ["SetStatus", "SetSetting", "SetSettings"]:
        url_str = "setstatussetsetting"
    url = f"{URL}/Content/Instructions/{url_str.lower().replace("_", "")}.htm"

    retries = 0
    request = httpx.get(url, follow_redirects=True)
    while request.status_code == 404 and retries < 10:
        new_url = f"{url_str}{retries+1}"
        url =  f"{URL}/Content/Instructions/{new_url.lower().replace("_", "")}.htm"
        retries += 1

    if request.status_code == 404:
        print(f"404 Status Code: {url}")
        continue

    print(url)
    soup = BeautifulSoup(request.text, "html.parser")
    args = soup.find_all(class_="PopupHeadingTopic")
    function_args = []

    for arg in args:
        meta = get_meta(arg)
        name = clean_string(arg.text)
        short_name = re.sub(r' \(.*\)$', '', name)

        if "," in short_name:
            new_args = short_name.split(", ")
            for n in new_args:
                function_args.append(
                    FunctionArgument(
                        name = n,
                        short_name=n,
                        description=" ".join(meta['description']),
                        type=meta['type'],
                        options=meta['table'],
                    )
                )
        else: 
            function_args.append(
                FunctionArgument(
                    name = clean_string(arg.text), 
                    short_name = short_name,
                    description=" ".join(meta['description']),
                    type=meta['type'],
                    options=meta['table'],
                )
            )

    if len(function_args) == 0:
        syntax = soup.find(string="Syntax").find_parent().find_next_sibling().text
        try:
            fun_args = re.findall(r'\((.*?)\)', syntax)[0].replace(" ", "").split(",") 
        except IndexError:
            # This happens when there are no args (it is a declaration rather than a function).
            continue
        for x in fun_args:
            function_args.append(
                FunctionArgument(
                    name = x,
                    short_name = x,
                    description = f"{x} (No description provided)",
                    type = TYPES,
                )
            )

    csi_function = CSIFunction(
        *function_args,
        name=function,
        remarks=get_remarks(soup),
        source=url,
    )

    fun_def.append(csi_function)

# import pickle


# with open("./data.pickle", "rb") as p:
#     test = pickle.load(p)

with open("./all_functions.py", "w") as file:
    for fun in fun_def:
        file.write(str(fun) + '\n')