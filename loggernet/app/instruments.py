from __future__ import annotations

from dataclasses import dataclass, field
import functions
from functions import Variable, VarType, DataType
from typing import Literal
from abc import ABC
from enum import Enum
import operators as op

field()
@dataclass
class TableItem:
    func: str
    field_names: list[str] | list[Variable]


@dataclass
class CardOut:
    StopRing: Literal[0, 1] = 0
    Size: int = -1

    def __eq__(self, other: CardOut):
        return self.StopRing == other.StopRing and self.Size == other.Size


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
        s = f"DataTable({self.name},self.trig_var)\n"
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


class WireOptions(Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"
    C6 = "C6"
    C7 = "C7"
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
    AG = "AG"
    RG2 = "RG2"
    G = "G"
    _12V = "12V"


@dataclass
class Wire:
    wire: str
    port: WireOptions
    description: str | None

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
                return item

        raise KeyError(f"No wire with color {item} found.")


@dataclass
class Instrument(ABC):
    manufacturer: str = field(init=False)
    model: str = field(init=False)
    type: str = field(init=False)
    wires: WiringDiagram = field(init=False, default=None)
    variables: list[Variable] | dict[str, Variable] = field(init=False, default=None)

    elevation: int | None = None
    sdi12_address: str | None = None

    def __post_init__(self):
        if isinstance(self.variables, list):
            self.variables = {x.name: x for x in self.variables}

    def update_var_names(self):
        raise NotImplementedError("Method not implemented...")

    @property
    def tables(self):
        raise NotImplementedError("Method not implemented...")

    @property
    def pre_scan(self):
        raise NotImplementedError("Method not implemented...")

    @property
    def funcs(self):
        raise NotImplementedError("Method not implemented...")

    @property
    def program(self):
        raise NotImplementedError("Method not implemented...")

    @property
    def slow_sequence(self):
        raise NotImplementedError("Method not implemented...")


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
            Variable("WS_offset", VarType.CONST, 0),
            Variable("WS_multiplier", VarType.CONST, 0.1666),
            Variable("wind_spd", VarType.PUBLIC, units="m s-1"),
            Variable("wind_dir", VarType.PUBLIC, units="arcdeg"),
            Variable("wind_timer", VarType.PUBLIC, units="sec"),
            Variable("wind_dir_sd", table_only=True),
            Variable("windgust", table_only=True),
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
                        self.variables["wind_dir_sd"],
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
                    field_names=[self.variables["wind_timer"]],
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
                op.If(
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
            WireOptions("Green", WireOptions.C2, "Control")
        )
        self.variables = [
            Variable("bp", VarType.PUBLIC, units="kPa")
        ]
        return super().__post_init__()

    @property
    def tables(self) -> list[Table]:
        return [
            Table(
                "FiveMin",
                TableItem(
                    functions.Average(1, self.variables["bp"], "IEEE4", False)
                )
            )
        ]

    @property 
    def program(self) -> str:
        "\n".join(
        [
            functions.PortSet(self.wires["Green"], "1"),
            functions.VoltSE(self.variables["bp"], 1, "mV5000", self.wires["Blue"], True, 0, 60, 0.2, 600),
            f"{self.variables["bp"]} = {self.variables["bp"]}*0.1"
        ]
    )
        
class Vaisala_HMP155(Instrument):
    def __post_init__(self):
        self.model = "HMP-155 (RS-485)"
        self.manufacturer = "Vaisala"
        self.type = "RH/T"

        self.wires = WiringDiagram(
            Wire("Brown", WireOptions.C7, "RS485 B"),
            Wire("Pink", WireOptions.C8, "RS485 A"),
            Wire("Red", WireOptions.RG2),
            Wire("Blue", WireOptions._12V, "12V Power"),
            Wire("Black/Clear", WireOptions.AG)
        )

        self.variables = [
            Variable("rhtemp(2)", VarType.PUBLIC, DataType.FLOAT)
        ]
        return super().__post_init__()