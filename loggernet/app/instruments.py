from dataclasses import dataclass, field
import functions
from functions import Variable
from typing import Literal
from abc import abstractmethod, ABC
from types import SimpleNamespace
from enum import Enum
import operators as op

@dataclass
class TableItem:
    func: str
    field_names: list[str] | list[Variable]


@dataclass
class CardOut:
    StopRing: Literal[0, 1] = 0
    Size: int = -1


@dataclass
class DataInterval:
    TIntoInt: int = 0
    Interval: int = 5
    Units: str = "min"
    Lapses: int = 10


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
            s += f"\n{str(item)}"


class WireOptions(Enum):
    P1="P1"
    P2="P2"
    P3="P3"
    P4="P4"
    P5="P5"
    P6="P6"
    P7="P7"
    VX1="Vx1"
    VX2="Vx2",
    SE1="1"
    SE2="2"
    SE3="3"
    SE4="4"
    SE5="5"
    SE6="6"
    SE7="7"
    SE8="8"
    SE9="9"
    AG="AG"
    G="G"


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
    
    def __getitem__(self, item) -> str:
        # TODO: Make this based on the port rather than name.
        out = [x for x in self.args if x.wire == item]
        assert len(out) == 1, f"Error: More than one wire named {item}."
        out = out[1]
        return out.port.value

@dataclass
class Instrument(ABC):
    manufacturer: str = field(init=False)
    model: str = field(init=False)
    type: str = field(init=False)
    wires: WiringDiagram = field(init=False, default=None)
    variables: SimpleNamespace | dict[str, Variable] | list[Variable] = field(init=False)

    elevation: int | None = None
    sdi12_address: str | None = None

    def __post_init__(self):
        if isinstance(self.variables, dict):
            self.variables = SimpleNamespace(**self.variables)
        if isinstance(self.variables, list):
            self.variables = SimpleNamespace(
                **{
                    x.name: x for x in self.variables
                }
            )
    @abstractmethod
    def update_var_names(self):
        raise NotImplementedError("Method not implemented...")

    @property 
    @abstractmethod
    def tables(self):
        raise NotImplementedError("Method not implemented...")
    
    @property 
    @abstractmethod
    def pre_scan(self):
        raise NotImplementedError("Method not implemented...")
    
    @property 
    @abstractmethod
    def funcs(self):
        raise NotImplementedError("Method not implemented...")
    
    @property 
    @abstractmethod
    def program(self):
        raise NotImplementedError("Method not implemented...")
    
    @property 
    @abstractmethod
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
            Wire("Green", "SE7", "WD Signal      WD SIG"),
            Wire("Black", "AG", "Signal G       WD REF"),
            Wire("Brown", "G", "Earth G        GND*"),
            description="* NOTE: Ground to EARTH in junction box directly to mast",
        )
        self.variables =list(
            Variable("WS_offset", "Const", 0),
            Variable("WS_multiplier", "Const", 0.1666),
            Variable("wind_spd", "Public", units="m s-1"),
            Variable("wind_dir", "Public", units="arcdeg"),
            Variable("wind_timer", "Public", units="sec"),
            Variable("wind_dir_sd", table_only=True),
            Variable("windgust", table_only=True)
        ), 
        return super().__post_init__()

    def tables(self) -> list[Table]:
        return list(
            Table(
                "FiveMin",
                TableItem(
                    functions.WindVector(
                        1,
                        self.variables.wind_spd,
                        self.variables.wind_dir,
                        "FP2",
                        False,
                        0,
                        0,
                        0
                    ),
                    field_names=list(self.variables.wind_spd, self.variables.wind_dir, self.variables.wind_dir_sd)
                ),
                TableItem(
                    functions.Maximum(
                        1, self.variables.wind_spd, "FP2", False, False,
                    ),
                    field_names=list(self.variables.wind_timer)
                ),
                size=-1,
                data_interval=DataInterval(),
                card_out=CardOut(),
            ),
            Table(
                "StatusReport",
                TableItem(
                    functions.Totalize(
                        1, self.variables.wind_timer, "IEEE4", False 
                    ),
                    field_names=list(self.variables.wind_timer)
                )
            )
        )

    def program(self):
        return list(
            functions.BrHalf(self.variables.wind_dir, 1, 'mV5000', self.wires["Green"], self.wires["White"],1, 2500, True, 0, "60", 355, 0),
            # TODO: Pulsecount
            op.If(self.variables.wind_spd, "<=", logic="")
        )

