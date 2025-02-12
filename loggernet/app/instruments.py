from __future__ import annotations

from dataclasses import dataclass, field
from app import functions
from app.functions import Variable, VarType, DataType
from typing import Literal, Optional, Callable
from abc import ABC
from enum import Enum
from app.operators import If, For
from textwrap import indent


@dataclass
class TableItem:
    func: str
    field_names: list[str] | list[Variable] | None = None

    def __str__(self):
        if self.field_names:
            return (
                self.func
                + ":"
                + f'FieldNames("{",".join(str(x) for x in self.field_names)}")'
            )
        return self.func


@dataclass
class CardOut:
    StopRing: Literal[0, 1] = 0
    Size: int = -1

    def __eq__(self, other: CardOut):
        return self.StopRing == other.StopRing and self.Size == other.Size

    def __str__(self):
        return f"CardOut({self.StopRing},{self.Size})"


@dataclass
class DataInterval:
    TIntoInt: int = 0
    Interval: int = 5
    Units: str = "min"
    Lapses: int = 10

    def __eq__(self, other: DataInterval):
        return (
            self.TIntoInt == other.TIntoInt
            and self.Interval == other.Interval
            and self.Units == other.Units
            and self.Lapses == other.Lapses
        )

    def __str__(self):
        return (
            f"DataInterval({self.TIntoInt},{self.Interval},{self.Units},{self.Lapses})"
        )


class Table:
    def __init__(
        self,
        name: str,
        *args: TableItem,
        trig_var: str = True,
        size: int = -1,
        data_interval: DataInterval = DataInterval(),
        card_out: CardOut | None = CardOut(),
    ):
        self.name = name
        self.trig_var = trig_var
        self.size = size
        self.args = args
        self.data_interval = data_interval
        self.card_out = card_out

    def __str__(self):
        s = f"DataTable({self.name},{self.trig_var})\n"
        s += f"    {str(self.data_interval)}\n"
        if self.card_out:
            s += f"    {str(self.card_out)}\n"

        for item in self.args:
            s += f"\n    {str(item)}"

        s += "\nEndTable"

        return s

    def __eq__(self, other: Table):
        return (
            self.name == other.name
            and self.trig_var == other.trig_var
            and self.size == other.size
            and self.data_interval == other.data_interval
            and self.card_out == other.card_out
        )


@dataclass
class Scan:
    ScanInterval: int
    ScanUnit: Literal["uSec", "mSec", "Sec", "Min", "Hr", "Day"]
    BufferOption: Literal[0, 1, 2, 3]
    Count: int

    def __str__(self):
        return f"Scan({self.ScanInterval},{self.ScanUnit},{self.BufferOption},{self.Count})"


@dataclass
class SlowSequence:
    id: int | str
    scan: Scan
    logic: str | list[str]

    def __post_init__(self):
        if isinstance(self.logic, list):
            self.logic = "\n".join(self.logic)

    def __str__(self) -> str:
        return "\n".join(
            [
                f"SlowSequence '{self.id}",
                str(self.scan),
                indent(str(self.logic), "    "),
                "NextScan",
            ]
        )


class WireOptions(Enum):
    COM1 = "ComC1"
    C1 = "C1"
    C2 = "C2"
    COM3 = "ComC3"
    C3 = "C3"
    C4 = "C4"
    COM5 = "ComC5"
    C5 = "C5"
    C6 = "C6"
    COM7 = "ComC7"
    C7 = "C7"
    C8 = "C8"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"
    P7 = "P7"
    VX1 = "Vx1"
    VX2 = "Vx2"
    SE1 = "1"
    SE2 = "2"
    SE3 = "3"
    SE4 = "4"
    SE5 = "5"
    SE6 = "6"
    SE7 = "7"
    SE8 = "8"
    SE9 = "9"
    SE10 = "10"
    SE11 = "11"
    SE12 = "12"
    SE13 = "13"
    SE14 = "14"
    SW12_1 = "SW12_1"
    SW12_2 = "SW12_2"
    AG = "AG"
    RG2 = "RG2"
    G = "G"
    _12V = "12V"
    _5V = "5V"
    DIFF_1_H = "1"
    DIFF_1_L = "1"
    DIFF_2_H = "2"
    DIFF_2_L = "2"
    DIFF_3_H = "3"
    DIFF_3_L = "3"
    DIFF_4_H = "4"
    DIFF_4_L = "4"
    DIFF_5_H = "5"
    DIFF_5_L = "5"
    DIFF_6_H = "6"
    DIFF_6_L = "6"
    DIFF_7_H = "7"
    DIFF_7_L = "7"
    DIFF_8_H = "8"
    DIFF_8_L = "8"


    def __str__(self):
        return self.value


@dataclass
class Wire:
    wire: str
    port: WireOptions | None
    description: Optional[str] = ""

    def __str__(self):
        return f"{self.wire + ':':<8} {self.port.value:<8} {self.description:<10}"


class WiringDiagram:
    def __init__(self, *args: Wire, description: str | None = None):
        self.args = args
        self.description = description

    def __str__(self):
        out = "'" + "\n'".join(str(x) for x in self.args)
        if self.description is not None:
            out += f"\n'{self.description}\n"
        return out

    def __getitem__(self, item: str) -> str:
        for wire in self.args:
            if wire.wire.lower() == item.lower():
                return str(wire.port)

        raise KeyError(f"No wire with color {item} found.")


@dataclass
class Instrument(ABC):
    manufacturer: str = field(init=False)
    model: str = field(init=False)
    type: str = field(init=False)
    wires: WiringDiagram = field(init=False, default=None)
    variables: list[Variable] | dict[str, Variable] = field(init=False, default=None)
    _slow_sequence: SlowSequence | str | None = field(init=False, default="initial")

    elevation: int | None = None
    sdi12_address: str | None = None
    transform: Callable[["Instrument"], "Instrument"] | None = None

    def __post_init__(self):
        if isinstance(self.variables, list):
            self.variables = {x.name: x for x in self.variables}
        if self.transform is not None:
            self._transform()
        self.check_unique_names()

    def _transform(self):
        self.transform(self)

    def check_unique_names(self):
        exists = []
        is_list = isinstance(self.variables, list)
        iterator = self.variables if is_list else self.variables.keys()

        for v in iterator:
            v = v.name if is_list else v
            if v in exists:
                raise ValueError(
                    f"Variable named {v} is duplicated... Please make all names unique."
                )
            exists.append(v)

    @property
    def tables(self) -> list[Table]:
        raise NotImplementedError()

    @property
    def pre_scan(self) -> str:
        raise NotImplementedError()

    @property
    def funcs(self) -> list[str]:
        raise NotImplementedError()

    @property
    def program(self) -> str:
        raise NotImplementedError()

    @property
    def post_scan(self) -> str:
        raise NotImplementedError()

    @property
    def slow_sequence(self) -> SlowSequence:
        raise NotImplementedError()

    def __str__(self) -> str:
        table_str = (
            "Defined Tables:\n" + "\n".join(str(x) for x in self.tables)
            if self.tables
            else ""
        )
        pre_scan = f"Pre-Scan Logic:\n{self.pre_scan}\n" if self.pre_scan else ""
        function_str = (
            "User-Defined Functions:\n" + "\n".join(str(x) for x in self.funcs)
            if self.funcs
            else ""
        )
        program = f"Program Logic:\n\n{self.program}\n" if self.program else ""
        slow_seq = (
            f"Slow Sequence:\n\n{self.slow_sequence}\n" if self.slow_sequence else ""
        )
        post_scan = (
            f"Post Table Call Logic:\n{self.post_scan}\n" if self.post_scan else ""
        )

        return "\n".join(
            [
                f"{self.manufacturer} {self.model} ({self.type})",
                "\nWiring Defaults:",
                str(self.wires) or "",
                "\nLoggerNet Variables:",
                "\n".join(x.declaration_str() for x in self.variables.values()),
                "\n",
                table_str,
                function_str,
                pre_scan,
                program,
                post_scan,
                slow_seq,
            ]
        )


class RMYoung_05108_77(Instrument):
    def __post_init__(self):
        self.manufacturer = "RM Young"
        self.model = "05108-74"
        self.type = "Wind"
        self.wires = WiringDiagram(
            Wire("Red", WireOptions.P1, "WS Signal      WS SIG"),
            Wire("White", WireOptions.VX2, "WD Excite      WD EXC"),
            Wire("Green", WireOptions.SE7, "WD Signal      WD SIG"),
            Wire("Black", WireOptions.AG, "Signal G       WD REF"),
            Wire("Brown", WireOptions.G, "Earth G        GND*"),
            description="* NOTE: Ground to EARTH in junction box directly to mast",
        )
        self.variables = [
            Variable("WS_offset", VarType.CONST, value=0),
            Variable("WS_multiplier", VarType.CONST, value=0.1666),
            Variable("wind_spd", VarType.PUBLIC, units="m s-1"),
            Variable("wind_dir", VarType.PUBLIC, units="arcdeg"),
            Variable("wind_timer", VarType.PUBLIC, units="sec"),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.WindVector(
                        1,
                        self.variables["wind_spd"],
                        self.variables["wind_dir"],
                        "FP2",
                        False,
                        0,
                        0,
                        0,
                    ),
                    field_names=[
                        self.variables["wind_spd"],
                        self.variables["wind_dir"],
                        f"{self.variables['wind_dir']}_sd",
                    ],
                ),
                TableItem(
                    functions.Maximum(
                        1,
                        self.variables["wind_spd"],
                        "FP2",
                        False,
                        False,
                    ),
                    field_names=["windgust"],
                ),
                size=-1,
                data_interval=DataInterval(),
                card_out=CardOut(),
            ),
            Table(
                "StatusReport",
                TableItem(
                    functions.Totalize(1, self.variables["wind_timer"], "IEEE4", False),
                    field_names=[self.variables["wind_timer"]],
                ),
                size=-1,
                card_out=CardOut(),
                data_interval=DataInterval(0, 120, "min", 10),
            ),
        ]

    @property
    def program(self) -> str:
        return "\n".join(
            str(x)
            for x in [
                functions.BrHalf(
                    self.variables["wind_dir"],
                    1,
                    "mV5000",
                    self.wires["Green"],
                    self.wires["White"],
                    1,
                    2500,
                    True,
                    0,
                    "60",
                    355,
                    0,
                ),
                functions.PulseCount(
                    self.variables["wind_spd"],
                    1,
                    self.wires["Red"],
                    "5",
                    "1",
                    self.variables["WS_multiplier"],
                    self.variables["WS_offset"],
                ),
                If(
                    self.variables["wind_spd"],
                    "<=",
                    0,
                    logic=[
                        f"{self.variables['wind_dir']} = NAN",
                        f"{self.variables['wind_timer']} = 3",
                    ],
                ).Else(f"{self.variables['wind_timer']} = 0"),
            ]
        )


class RMYoung_09106(Instrument):
    def __post_init__(self):
        self.manufacturer = "RM Young"
        self.model = "09106"
        self.type = "Wind"

        self.wires = WiringDiagram(
            Wire("Red", WireOptions._12V, "12v Power"),
            Wire("White", WireOptions.AG, "Signal G"),
            Wire("Clear", WireOptions.AG, "Signal G"),
            Wire("Green", WireOptions.SE13, "WD Signal"),
            Wire("Brown", WireOptions.SE14, "WS Signal"),
            Wire("Black", WireOptions.G, "Power Ground"),
        )
        self.variables = [
            Variable("wind_spd", VarType.PUBLIC, units="m s-1"),
            Variable("wind_dir", VarType.PUBLIC, units="arcdeg"),
            Variable("wind_timer", VarType.PUBLIC, units="sec"),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.WindVector(
                        1,
                        self.variables["wind_spd"],
                        self.variables["wind_dir"],
                        "FP2",
                        False,
                        0,
                        0,
                        0,
                    ),
                    field_names=[
                        self.variables["wind_spd"],
                        self.varaibles["wind_dir"],
                        f"{self.variables['wind_dir']}_sd",
                    ],
                ),
                TableItem(
                    functions.Maximum(
                        1, self.variables["wind_spd", "FP2", False, False]
                    ),
                    ["windgust"],
                ),
            )
        ]

    @property
    def program(self) -> str:
        "\n".join(
            [
                functions.VoltSE(
                    self.variables["wind_spd"],
                    1,
                    "mv5000",
                    self.wires["Green"],
                    0,
                    0,
                    15000,
                    0.020,
                    0,
                ),
                functions.VoltSE(
                    self.variables["wind_dir"],
                    1,
                    "mv5000",
                    self.wires["Brown"],
                    0,
                    0,
                    15000,
                    0.108,
                    0,
                ),
                If(
                    self.variable["wind_dir"] > 360,
                    logic=f"{self.variables['wind_dir']}={self.variables['wind_dir']}-360",
                ),
                If(
                    self.variables["wind_spd"],
                    "<=",
                    0,
                    logic=f"{self.variables['wind_dir']} = NAN\n{self.variables['wind_timer']}=3",
                ).Else(f"{self.variables['wind_timer']} = 0"),
            ]
        )


class Setra_CS100(Instrument):
    def __post_init__(self):
        self.manufacturer = "Setra"
        self.model = "CS100"
        self.type = "Barometer"

        self.wires = WiringDiagram(
            Wire("Blue", WireOptions.SE2, "Signal H"),
            Wire("Yellow", WireOptions.AG, "Signal G"),
            Wire("Clear", WireOptions.AG, "Signal G"),
            Wire("Red", WireOptions._12V, "12v Power"),
            Wire("Black", WireOptions.G, "Power Ground"),
            Wire("Green", WireOptions.C2, "Control"),
        )
        self.variables = [Variable("bp", VarType.PUBLIC, units="kPa")]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(functions.Average(1, self.variables["bp"], "IEEE4", False)),
            )
        ]

    @property
    def program(self) -> str:
        "\n".join(
            [
                functions.PortSet(self.wires["Green"], "1"),
                functions.VoltSE(
                    self.variables["bp"],
                    1,
                    "mV5000",
                    self.wires["Blue"],
                    True,
                    0,
                    60,
                    0.2,
                    600,
                ),
                f"{self.variables['bp']} = {self.variables['bp']}*0.1",
            ]
        )


class Vaisala_HMP155(Instrument):
    def __post_init__(self):
        self.model = "HMP-155 (RS-485)"
        self.manufacturer = "Vaisala"
        self.type = "RH/T"

        self.wires = WiringDiagram(
            Wire("Brown", WireOptions.COM7, "RS485 B"),
            Wire("Pink", WireOptions.C8, "RS485 A"),
            Wire("Red", WireOptions.RG2),
            Wire("Blue", WireOptions._12V, "12V Power"),
            Wire("Black/Clear", WireOptions.AG),
        )

        self.variables = [
            Variable("rhtemp(2)", VarType.PUBLIC, DataType.FLOAT),
            Variable("rhtemp(1)", VarType.ALIAS, value="rh", units="%"),
            Variable("rhtemp(2)", VarType.ALIAS, value="air_temp", units="deg C"),
            Variable("reset_hmp155", VarType.PUBLIC, DataType.BOOLEAN),
            Variable("NBytesReturned", VarType.DIM, DataType.LONG),
            Variable("SerialIngest", VarType.DIM, DataType("String26")),
            Variable("String_1", VarType.DIM, DataType.STRING),
            Variable("String_2", VarType.DIM, DataType.STRING),
            Variable("CRLF", VarType.CONST, value="CHR(13)+CHR(10)"),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Average(1, self.variables["air_temp"], "FP2", False),
                    [self.variables["air_temp"]],
                ),
                TableItem(
                    functions.Maximum(1, self.variables["air_temp"], "FP2", 0, 1),
                    [f"{self.variables['air_temp']}_max"],
                ),
                TableItem(
                    functions.Minimum(1, self.variables["air_temp"], "FP2", 0, 1),
                    [f"{self.variables['air_temp']}_min"],
                ),
                TableItem(
                    functions.Average(1, self.variables["rh"], "FP2", False),
                    [self.variables["rh"]],
                ),
            )
        ]

    @property
    def pre_scan(self) -> str:
        return f"{self.variables['reset_hmp155']} = True"

    @property
    def program(self) -> str:
        "\n".join(
            [
                str(
                    If(
                        self.variables["reset_hmp155"],
                        logic=[
                            functions.SerialOpen(
                                self.wires["Brown"], 4800, "10", 0, 53, "4"
                            ),
                            f'{self.variables["String_1"]} =  "SMODE RUN"+{self.variables["CRLF"]}',
                            f'{self.variables["String_2"]} = "R"+{self.variables["CRLF"]}',
                            functions.SerialOut(
                                self.wires["Brown"],
                                self.variables["String_1"],
                                '"RUN"',
                                3,
                                100,
                            ),
                            functions.Delay(0, 500, 1),
                            functions.SerialOut(
                                self.wires["Brown"],
                                self.variables["String_2"],
                                '"RH"',
                                3,
                                100,
                            ),
                            f"{self.variables['reset_hmp155']} = False",
                        ],
                    )
                ),
                functions.SerialInRecord(
                    self.wires["Brown"],
                    self.variables["SerialIngest"],
                    "00",
                    25,
                    "&H0D0A",
                    self.variables["NBytesReturned"],
                    "01",
                ),
                # TODO: see if I can do this instead of rhtemp(1). Test on datalogger.
                functions.SplitStr(
                    self.variables["rh"], self.variables["SerialIngest"], '"="', 2, 0
                ),
                functions.SerialFlush(self.wires["Brown"]),
            ]
        )


class Acclima_TDR310N(Instrument):
    def __post_init__(self):
        self.model = "Acclima"
        self.manufacturer = "TDR-310N"
        self.type = "Soil"

        if self.sdi12_address is None:
            raise AttributeError(
                "This is an SDI12 device and an SDI12 address must be assigned."
            )

        if self.elevation is None:
            raise AttributeError(
                "This device is deployed at depth. An elevation must be assigned."
            )

        self.wires = WiringDiagram(
            Wire("Blue", WireOptions.C3, "SDI-12 data  SDI_ADD: 1-5"),
            Wire("Red", WireOptions._12V, "12v Power"),
            Wire("White", WireOptions.G, "Ground"),
        )

        self.variables = [
            Variable(f"soil_{self.sdi12_address}(5)", VarType.PUBLIC),
            Variable(
                f"soil_{self.sdi12_address}(1)",
                VarType.ALIAS,
                value="soil_vwc",
                units="m3 m-3",
            ),
            Variable(
                f"soil_{self.sdi12_address}(2)",
                VarType.ALIAS,
                value="soil_temp",
                units="deg C",
            ),
            Variable(f"soil_{self.sdi12_address}(3)", VarType.ALIAS, value="soil_perm"),
            Variable(
                f"soil_{self.sdi12_address}(4)",
                VarType.ALIAS,
                value="soil_ec_blk",
                units="uS cm-1",
            ),
            Variable(
                f"soil_{self.sdi12_address}(5)",
                VarType.ALIAS,
                value="soil_ec_por",
                units="uS cm-1",
            ),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_vwc']}*.01", "FP2"),
                    [self.variables["soil_vwc"]],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_temp']}", "FP2"),
                    [self.variables["soil_temp"]],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_ec_blk']}", "FP2"),
                    [self.variables["soil_ec_blk"]],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_ec_por']}", "FP2"),
                    [self.variables["soil_ec_por"]],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_perm']}", "FP2"),
                    [self.variables["soil_perm"]],
                ),
            ),
            Table(
                "Soils",
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_vwc']}*.01", "FP2"),
                    [f"vwc_{self.sdi12_address}"],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_temp']}", "FP2"),
                    [f"temp_{self.sdi12_address}"],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_ec_blk']}", "FP2"),
                    [f"blk_{self.sdi12_address}"],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_ec_por']}", "FP2"),
                    [f"por_{self.sdi12_address}"],
                ),
                TableItem(
                    functions.Sample(1, f"{self.variables['soil_perm']}", "FP2"),
                    [f"perm_{self.sdi12_address}"],
                ),
                card_out=None,
            ),
        ]

    @property
    def slow_sequence(self) -> SlowSequence | None | str:
        if self._slow_sequence == "initial":
            self._slow_sequence = SlowSequence(
                "soil",
                Scan(1, "Min", 0, 0),
                If(
                    functions.IfTime(4, 5, "min"),
                    logic=functions.SDI12Recorder(
                        self.variables[f"soil_{self.sdi12_address}(5)"],
                        self.wires["Blue"],
                        self.sdi12_address,
                        "M1!",
                        1,
                        0,
                        -1,
                    ),
                ),
            )

        return self._slow_sequence

    @slow_sequence.setter
    def slow_sequence(self, value: SlowSequence | None):
        self._slow_sequence = value


class ProStar_EMC1(Instrument):
    def __post_init__(self):
        self.model = "ProStar"
        self.manufacturer = "EMC-1"
        self.type = "Charge Data"

        self.variables = [
            Variable("ModbusSocker", VarType.PUBLIC, DataType.FLOAT),
            Variable("ModbusResult", VarType.PUBLIC),
            Variable("ChgCntDat(82)", VarType.DIM, DataType.LONG),
            Variable("i", VarType.DIM),
            Variable("batt_volt", VarType.PUBLIC, units="v"),
            Variable("shutoff_voltage", VarType.Public, units="v"),
            Variable("ChgCntDat(17)", VarType.ALIAS, value="charge_current"),
            Variable("ChgCntDat(18)", VarType.ALIAS, value="array_current"),
            Variable("ChgCntDat(19)", VarType.ALIAS, value="battery_terminal_voltage"),
            Variable("ChgCntDat(21)", VarType.ALIAS, value="load_voltage"),
            Variable("ChgCntDat(22)", VarType.ALIAS, value="net_battery_current"),
            Variable("ChgCntDat(23)", VarType.ALIAS, value="load_current"),
            Variable("ChgCntDat(27)", VarType.ALIAS, value="heatsink_temp"),
            Variable("ChgCntDat(28)", VarType.ALIAS, value="battery_temp"),
            Variable("ChgCntDat(29)", VarType.ALIAS, value="ambient_temp"),
            Variable("ChgCntDat(34)", VarType.ALIAS, value="charge_state"),
            Variable("ChgCntDat(41)", VarType.ALIAS, value="total_ah_charge_hi"),
            Variable("ChgCntDat(42)", VarType.ALIAS, value="total_ah_charge_lo"),
            Variable("ChgCntDat(47)", VarType.ALIAS, value="load_state"),
            Variable("ChgCntDat(53)", VarType.ALIAS, value="total_ah_load_hi"),
            Variable("ChgCntDat(54)", VarType.ALIAS, value="total_ah_load_lo"),
            Variable("ChgCntDat(74)", VarType.ALIAS, value="daily_absorption_time"),
            Variable("ChgCntDat(75)", VarType.ALIAS, value="daily_equalization_time"),
            Variable("ChgCntDat(76)", VarType.ALIAS, value="daily_float_time"),
        ]
        return super().__post_init__()

    @property
    def pre_scan(self):
        return f"{self.variables['shutoff_voltage']} = 22"

    @property
    def functions(self):
        return "\n".join(
            [
                "Function ScaleToF16(value)",
                "  Dim out",
                "  Dim exponent",
                "  out = value",
                '  out = out AND HexToDec("3ff")',
                "  out = out / 1024.0",
                "  out = out + 1",
                "  value = value >> 10",
                "",
                '  exponent = value AND HexToDec("1f")',
                "  exponent = exponent - 15",
                "  out = out * PWR(2, exponent)",
                "",
                "  Return out",
                "EndFunction",
            ]
        )

    @property
    def tables(self):
        return [
            Table(
                "FiveMin",
                functions.Sample(1, self.variables["batt_volt"], "FP2", False),
                functions.Minimum(1, self.variables["batt_volt"], "FP2", False, False),
            ),
            Table(
                "ChargeData",
                functions.Sample(1, self.variables["charge_current"], "Long", False),
                functions.Sample(1, self.variables["array_current"], "Long", False),
                functions.Sample(
                    1, self.variables["battery_terminal_voltage"], "Long", False
                ),
                functions.Sample(1, self.variables["load_voltage"], "Long", False),
                functions.Sample(
                    1, self.variables["net_battery_current"], "Long", False
                ),
                functions.Sample(1, self.variables["load_current"], "Long", False),
                functions.Sample(1, self.variables["heatsink_temp"], "Long", False),
                functions.Sample(1, self.variables["battery_temp"], "Long", False),
                functions.Sample(1, self.variables["ambient_temp"], "Long", False),
                functions.Sample(1, self.variables["charge_state"], "Long", False),
                functions.Sample(
                    1, self.variables["total_ah_charge_hi"], "Long", False
                ),
                functions.Sample(
                    1, self.variables["total_ah_charge_lo"], "Long", False
                ),
                functions.Sample(1, self.variables["load_state"], "Long", False),
                functions.Sample(1, self.variables["total_ah_load_hi"], "Long", False),
                functions.Sample(1, self.variables["total_ah_load_lo"], "Long", False),
                functions.Sample(
                    1, self.variables["daily_absorption_time"], "Long", False
                ),
                functions.Sample(
                    1, self.variables["daily_equalization_time"], "Long", False
                ),
                functions.Sample(1, self.variables["daily_float_time"], "Long", False),
            ),
        ]

    @property
    def slow_sequence(self):
        SlowSequence(
            "Charge",
            Scan(1, "Min", 0, 0),
            code_string="\n".join(
                [
                    f"{self.variables['ModbusSocket']}={functions.TCPOpen('192.168.1.253', 502, 1)}",
                    f"{functions.ModbusClient(self.variables['ModbusResult'], self.variables['ModbusSocket'], 9600, 1, 3, {str(self.variable['ChgCntDat(82)']).replace('(82)', ''), 1, 82, 3, 1500, 3})}"
                    f" {self.variables['batt_volt']} = ScaleToF16({str(self.variable['ChgCntDat(82)']).replace('(82)', '(25)')})\n",
                    If(
                        self.variables["ModbusSocket"],
                        "=",
                        0,
                        logic=For(
                            logic=f"{str(self.variables['ChgCntDat'].replace('82', 'i'))} = NAN",
                            v=self.variables["i"],
                            start=1,
                            end=82,
                        ),
                    ),
                ]
            ),
        )


# TODO: Implement these as defaults for if no instruments are selected.
class CR1000X_Battery(Instrument): ...


class CR1000X_PanelTemp(Instrument): ...


class Generic_IPCamera(Instrument):
    voltage: CR1000X_Battery | ProStar_EMC1

    def __post_init__(self):
        self.wires = WiringDiagram(
            [
                Wire("Black", WireOptions.G, "#4 Black to Ground"),
                Wire(
                    "Red",
                    WireOptions.SW12_1,
                    "CR1000X SW1 and #2 red to fuse block (6.2A fuse)",
                ),
            ],
            description="Red from camera to #1 and white to ground (yellow cable)",
        )

        self.variables = [
            Variable("Camera_Power", VarType.PUBLIC, DataType.BOOLEAN),
            Variable("Camera_Power_Manual", VarType.PUBLIC, DataType.BOOLEAN),
        ]

        return super().__post_init__()

    @property
    def pre_scan(self):
        "\n".join(
            [
                f"{self.variables['Camera_Power']}=true",
                f"{self.variables['Camera_Power_Manual']}=true",
            ]
        )

    @property
    def program(self):
        "\n".join(
            If(
                self.variables["Camera_Power_Manual"],
                logic=functions.SW12(self.wires["Red"], self.variables["Camera_Power"]),
            ).Else(
                "\n".join(
                    str(
                        If(
                            functions.TimeIsBetween(2, 3, 1400, "min"),
                            logic=f"{self.variables['Camera_Power']}=False",
                        ).Else(f"{self.variables['Camera_Power']}=True")
                    ),
                    str(
                        If(
                            self.voltage.variables["batt_volt"],
                            "<",
                            self.voltage.variables["shutoff_voltage"],
                            logic=f"{self.variables['Camera_Power']}=false",
                        )
                    ),
                    str(
                        functions.SW12(
                            self.wires["Red"], self.variables["Camera_Power"]
                        )
                    ),
                )
            )
        )


class EnviroCams_iPatrol(Generic_IPCamera):
    def __post_init__(self):
        self.manufacturer = "EnviroCams"
        self.model = "iPatrol PTZ"
        self.type = "IP Camera"

        return super().__post_init__()


class EnviroCams_Scout(Generic_IPCamera):
    def __post_init__(self):
        self.manufacturer = "EnviroCams"
        self.model = "Scout PTZ"
        self.type = "IP Camera"

        return super().__post_init__()


class SparkFun_Door_Switch(Instrument):
    def __post_init__(self):
        self.manufacturer = "SparkFun"
        self.model = "Door Switch"
        self.type = "Door"

        self.wires = WiringDiagram(
            Wire("Red", WireOptions._5V, "5v Power"),
            Wire("Black", WireOptions.C4, "Open/Closed Status"),
        )

        self.variables = [
            Variable("door", VarType.PUBLIC),
            Variable("door_timer", VarType.PUBLIC, DataType.LONG, units="sec"),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Maximum(1, self.variables["door"], "FP2", False, False),
                    [self.variables["door"]],
                ),
            ),
            Table(
                "StatusReport",
                TableItem(
                    functions.Maximum(
                        1, self.variables["door_timer"], "UINT4", False, False
                    ),
                    [self.variables["door_timer"]],
                ),
            ),
        ]

    @property
    def program(self) -> str:
        return "\n".join(
            [
                If(
                    functions.CheckPort(self.wires["Black"]),
                    logic="\n".join(
                        [
                            f"{self.variables['door']} = 0",
                            f"{self.variables['door_timer']} = 0",
                            functions.Timer(1, "2", "3"),
                        ]
                    ),
                ).Else(
                    "\n".join(
                        [
                            functions.Timer(1, "2", "0"),
                            f"{self.variables['door_timer']} = {functions.Timer(1, '2', '4')}",
                            If(
                                self.variables["door_timer"],
                                ">",
                                14400,
                                logic=f"{self.variables['door']} = 0",
                            ).Else(f"{self.variables['door']} = 1"),
                        ]
                    )
                )
            ]
        )


class OTT_PLS500(Instrument):
    def __post_init__(self):
        self.manufacturer = "OTT"
        self.model = "PLS 500"
        self.type = "Pressure Probe"
        assert self.sdi12_address is not None, (
            "An SDI12 Address must be specified for this device."
        )

        self.wires = WiringDiagram(
            Wire("Blue", WireOptions.G),
            Wire("Red", WireOptions._12V, "(on CR1000X)"),
            Wire("Grey", WireOptions.C5),
        )

        self.variables = [
            Variable("Transducer(3)", var_type=VarType.PUBLIC),
            Variable("Transducer(1)", VarType.ALIAS, value="well_lvl", units="m"),
            Variable("Transducer(2)", VarType.ALIAS, value="well_tmp", units="deg C"),
            Variable("Transducer(3)", VarType.ALIAS, value="well_status"),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Average(1, self.variables["well_lvl"], "FP2", False),
                    [self.variables["well_lvl"]],
                ),
                TableItem(
                    functions.Average(1, self.variables["well_tmp"], "FP2", False),
                    [self.variables["well_tmp"]],
                ),
                TableItem(
                    functions.Sample(1, self.variables["well_status"], "FP2", False),
                    [self.variables["well_status"]],
                ),
            ),
        ]

    @property
    def slow_sequence(self) -> SlowSequence:
        SlowSequence(
            "Transducer",
            Scan(1, "Min", 0, 0),
            functions.SDI12Recorder(
                self.variables["Transducer(3)"].replace("(3)", ""),
                self.wires["Grey"],
                self.sdi12_address,
                "M!",
                1,
                0,
                -1,
                1,
            ),
        )


class OTT_Pluvio(Instrument):
    def __post_init__(self):
        self.manufacturer = "OTT"
        self.model = "Pluvio2_L_400"
        self.type = "Precipitation"

        self.wires = WiringDiagram(
            Wire("Black", None, "DC Converter blac (out) (#1 not used)"),
            Wire("Green", WireOptions.C5, "SDI-12 data SDI_ADD: 2"),
            Wire("White", WireOptions.G, "Data Ground"),
            Wire("Red", None, "24V DC Converter Out (Yellow)"),
            Wire("Yellow", WireOptions._12V, "12v Power"),
            Wire("Brown", WireOptions.G, "Power Ground"),
        )

        self.variables = [
            Variable("Pluvio(9)", VarType.PUBLIC),
            Variable("Pluvio(1)", VarType.ALIAS, value="ppt_max_rate", units="mm hr-1"),
            Variable("Pluvio(2)", VarType.ALIAS, value="ppt", units="mm"),
            Variable("Pluvio(3)", VarType.ALIAS, value="pluv_accuNRT", units="mm"),
            Variable("Pluvio(4)", VarType.ALIAS, value="pluv_accuTtlNRT", units="mm"),
            Variable("Pluvio(5)", VarType.ALIAS, value="pluv_fill", units="mm"),
            Variable("Pluvio(6)", VarType.ALIAS, value="pluv_bucketNRT", units="mm"),
            Variable("Pluvio(7)", VarType.ALIAS, value="pluv_temp", units="deg C"),
            Variable("Pluvio(8)", VarType.ALIAS, value="pluv_heater", units="code"),
            Variable("Pluvio(9)", VarType.ALIAS, value="pluv_gagestat", units="code"),
            Variable("pluv_flag", VarType.PUBLIC, value = 1)
        ]

        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin", 
                TableItem(functions.Totalize(1, self.variables["ppt"], "IEEE4", self.variables["pluv_flag"]), ["ppt"]),
                TableItem(functions.Maximum(1, self.variable["ppt_max_rate"], "IEEE4", False, False), ["ppt_max_rate"]),
                TableItem(functions.Sample(1, self.variables["pluv_fill"], "IEEE4", False), ["pluv_fill"]),
                TableItem(functions.Sample(1, self.variables["pluv_heater"], "FP2", False), ["pluv_heater"])
            ),
            Table(
                "StatusReport",
                TableItem(functions.Sample(1, self.variables["pluv_gagestat"], "FP2", False)),
                TableItem(functions.Sample(1, self.variables["pluv_temp"], "FP2", False)),
                data_interval=DataInterval(0, 120, "min", 10)
            )
        ]


    @property
    def end_scan(self) -> str:
        return f"{self.variables["pluv_flag"]} = 1"
    
    @property
    def slow_sequence(self) -> SlowSequence:
        return SlowSequence(
            "pluvio",
            Scan(1, "Min", 0, 0),
            logic = "\n".join([
                functions.SDI12Recorder(
                    self.variables["Pluvio(9)"].name.replace("9", ""),
                    self.wires["Green"],
                    self.sdi12_address,
                    "C!",
                    1,
                    0
                    -1,
                    1
                ),
                f"{self.variables["pluv_flag"]} = 0"
            ])
        )

class Sierra_RV50X(Instrument):
    voltage: CR1000X_Battery | ProStar_EMC1

    def __post_init__(self):
        self.manufacturer = "Sierra Wireless"
        self.model = "RV50X"
        self.type = "Modem"

        self.wires = WiringDiagram(
            Wire("Black", WireOptions.G),
            Wire("Red", WireOptions._12V, "(On CR1000X)"),
            Wire("White", WireOptions.SW12_2),
        )

        self.variables = [Variable("Modem_Power", VarType.PUBLIC, DataType.BOOLEAN)]

        return super().__post_init__()

    @property
    def pre_scan(self) -> str:
        return f"{self.variables['Modem_Power']} = True"

    @property
    def program(self) -> str:
        return "\n".join(
            [
                If(
                    functions.TimeIsBetween(2, 3, 1440, "min"),
                    logic=f"{self.variables['Modem_Power']} = False",
                ).Else(f"{self.variables['Modem_Power']} = True"),
                If(
                    self.voltage.variables["batt_volt"],
                    "<",
                    self.voltage.variables["shutoff_voltage"],
                    logic=If(
                        functions.TimeIsBetween(1, 4, 240, "min"),
                        logic=f"{self.variables['Modem_Power']} = True",
                    ).Else(f"{self.variables['Modem_Power']} = False"),
                ),
                functions.SW12(self.wires["White"], self.variables["Modem_Power"]),
            ]
        )


class Campbell_SnowVue10(Instrument):
    temperature: Vaisala_HMP155

    def __post_init__(self):
        self.manufacturer = "Campbell Scientific"
        self.model = "SnowVue10"
        self.type = "Snow"

        self.wires = WiringDiagram(
            Wire("White", WireOptions.C1, "SDI-12 data SDI_ADD: 1"),
            Wire("Brown", WireOptions._12V, "Fuse Block 0.5A fuse power"),
            Wire("Black", WireOptions.G, "Power Ground"),
            Wire("Clear", WireOptions.AG)
        )

        self.variables = [
            Variable("SnowVUE_Go", VarType.PUBLIC, DataType.BOOLEAN),  # When true, runs the SnowVUE10 measurement cycle
            Variable("Set_D2G", VarType.PUBLIC, DataType.BOOLEAN),  # When true, sets the SnowVUE10 distance to ground
            Variable("SnowVUE(2)", VarType.PUBLIC),  # General SnowVUE variable
            Variable("Dist2Gnd", VarType.PUBLIC, units="m"),  # Distance to ground
            Variable("SnowVUE(1)", VarType.ALIAS, value="Dist2Targ", units="m"),  # Distance from the SnowVUE10 to target
            Variable("TCDT", VarType.PUBLIC, units="m"),  # Final temperature-corrected distance
            Variable("snow_depth", VarType.PUBLIC, units="cm"),  # Snow depth
            Variable("snow_min", VarType.PUBLIC, units="cm"),  # Used to store snow_depth < 0
            Variable("SnowVUE(2)", VarType.ALIAS, value="snow_depth_q"),  # Measurement quality number
            Variable("FH", VarType.DIM, DataType.LONG),  # File Handle to use to set distance to ground
            Variable("dummystr", VarType.DIM, DataType.STRING),  # Dummy string variable
            Variable("SnowVUE_Meta(8)", VarType.PUBLIC),  # Metadata calls
            Variable("SnowVUE_Meta(2)", VarType.ALIAS, value="IntTemp", units="deg C"),  # Temperature inside sensor housing
            Variable("SnowVUE_Meta(3)", VarType.ALIAS, value="IntRH", units="%"),  # Relative Humidity inside sensor housing
            Variable("SnowVUE_Meta(4)", VarType.ALIAS, value="Pitch", units="deg"),  # Tilt (degrees) front to back
            Variable("SnowVUE_Meta(5)", VarType.ALIAS, value="Roll", units="deg"),  # Tilt (degrees) side to side
            Variable("SnowVUE_Meta(6)", VarType.ALIAS, value="SupVolt", units="v"),  # Voltage of supply from power source
            Variable("SnowVUE_Meta(7)", VarType.ALIAS, value="ResFreq", units="kHz"),  # Resonate Frequency of Transducer
            Variable("SnowVUE_Meta(8)", VarType.ALIAS, value="Alert", units="unitless"),  # Alert flag if ResFreq is out of tolerance
        ]

        return super().__post_init__()
    

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Sample(1, self.variables["snow_depth"], "FP2"),
                    field_names=["snow_depth"],
                ),
                TableItem(
                    functions.Sample(1, self.variables["snow_depth_q"], "FP2"),
                    field_names=["snow_depth_q"],
                ),
                size=-1,
                data_interval=DataInterval(),
                card_out=CardOut(),
            ),
            Table(
                "StatusReport",
                TableItem(
                    functions.Minimum(
                        1, self.variables["snow_min"], "FP2", False, False
                    ),
                    field_names=["snow_min"],
                ),
                size=-1,
                card_out=CardOut(),
                data_interval=DataInterval(0, 120, "min", 10),
            ),
        ]    
    
    @property
    def pre_scan(self) -> str:
        return "\n".join([
            If(functions.FileSize("USR:Dist2Gnd.txt"), ">", 0, 
               logic = "\n".join([
                   f"{self.variables["FH"]} = {functions.FileOpen("USR:Dist2Gnd.txt", "r", 0)}",
                   functions.FileRead(self.variables["FH"], self.variables["dummystr"],10),
                   functions.SplitStr(self.variables["Dist2Gnd"],self.variables["dummystr"],"",1,0),
                   functions.FileClose(self.variables['FH'])
               ])).Else(
                   f"{self.variables["Dist2Gnd"]} = 1.9"
               )
        ])

    @property
    def program(self) -> str:
        return "\n".join([
            If(functions.IfTime(237, 300, "Sec"), logic=f"{self.variables["SnowVUE_Go"]} = True"),
            If(self.variables["Set_D2G"], logic = f"{self.variables["SnowVUE_Go"]} = True")
        ]) 
    
    @property
    def slow_sequence(self) -> SlowSequence:
        return SlowSequence(
            "Snow",
            Scan(1, "Min", 0, 0),
            logic = "\n".join([If(
                self.variables["SnowVUE_Go"],
                logic = "\n".join([
                    functions.SDI12Recorder(
                        self.variables["SnowVUE(2)"].name.replace("2", ""), self.wires["White"], self.sdi12_address, "M1!", 1, 0, -1
                    ),
                    functions.SDI12Recorder(
                        self.variables["SnowVUE_Meta(8)"].name.replace("8", ""), self.wires["White"], self.sdi12_address, "M9!", 1, 0, -1
                    )
                ])
            ),
            f"{self.variables["SnowVUE_Go"]} = False",
            f"{self.variables["TCDT"]} = {self.variables["Dist2Targ"]}*{functions.Sqr(f"({self.Vaisala_HMP155.variables["air_temp"]}+273.15)/273.15")}",
            f"{self.variables['snow_depth']} = ({self.variables['Dist2Gnd']} - {self.variables['TCDT']}) * 100",
            If(
                self.variables['snow_depth'], "<", "0",
                logic=[
                    f"{self.variables['snow_min']} = {self.variables['snow_depth']}",
                    f"{self.variables['snow_depth']} = 0",
                ],
            ),
            If(
                self.variables['Set_D2G'],
                logic=[
                    f"{self.variables['Dist2Gnd']} = {self.variables['TCDT']}",
                    f'{self.variables["FH"]} = {functions.FileOpen("USR:Dist2Gnd.txt", "w", 0)}',
                    functions.Sprintf(self.variables["dummystr"], r"%f", self.variables["Dist2Gnd"]),
                    functions.FileWrite(self.variables["FH"], self.variables["dummystr"], 0),
                    functions.FileClose(self.variables["FH"]),
                    f"{self.variables['Set_D2G']} = False",
                ],
            )
])
        )


class Apogee_SP510(Instrument):
    pyran_calib: float

    def __post_init__(self):
        self.manufacturer = "Apogee"
        self.model = "SP-510 SS"
        self.type = "Pyranometer"

        self.wires = WiringDiagram(
            Wire("White", WireOptions.DIFF_2_H, "Signal Positive"),
            Wire("Black", WireOptions.DIFF_2_L, "Signal Negative"),
            Wire("Clear", WireOptions.AG, "Shield Ground"),
            Wire("Yellow", WireOptions._12V, "Fuse block 0.5A fuse heater"),
            Wire("Blue", WireOptions.G, "Power ground for heater")
        )

        self.variables = [
            Variable("sol_rad", VarType.PUBLIC, units="W m-2"),
            Variable("sol_min", VarType.PUBLIC, units="W m-2"),
            Variable("pyran_calib", VarType.PUBLIC),
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Average(
                        1,
                        self.variables["sol_rad"],
                        "FP2",
                        False,
                    ),
                    field_names=[self.variables["sol_rad"]],
                ),
                size=-1,
                data_interval=DataInterval(),
                card_out=CardOut(),
            ),
            Table(
                "StatusReport",
                TableItem(
                    functions.Minimum(
                        1,
                        self.variables["sol_min"],
                        "FP2",
                        False,
                        False,
                    ),
                    field_names=[self.variables["sol_min"]],
                ),
                size=-1,
                card_out=CardOut(),
                data_interval=DataInterval(0, 120, "min", 10),
            ),
        ]
    
    @property
    def pre_scan(self) -> str:
        return f"{self.variables["pyran_calib"]} = {self.pyran_calib}"

    @property 
    def program(self) -> str:
        return "\n".join([
            functions.VoltDiff(self.variables["sol_rad"], 1, 'mv200', self.wires["White"], True, 0, "60", self.variables["pyran_calib"], 0),
            If(self.variables["sol_rad"], "<", 0,
               logic = [
                   f"{self.variables["sol_min"]} = {self.variables["sol_rad"]}",
                   f"{self.variables["sol_rad"]} = 0"
               ])
        ])


INSTRUMENTS = {
    "RMYoung_05108_77": RMYoung_05108_77,
    "Setra_CS100": Setra_CS100,
    "Vaisala_HMP155": Vaisala_HMP155,
    "Acclima_TDR310N": Acclima_TDR310N,
}
