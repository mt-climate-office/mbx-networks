from dataclasses import dataclass

from typing import Literal


@dataclass
class Variable:
    name: str
    type: Literal["Public", "Const", "Dim", "Alias"] | None = None
    value: str | int | float | None = None
    units: str | None = None

    def __post_init__(self):
        if self.type == "Const" and self.value is None:
            raise ValueError("When defining a Const type, value must not be none.")

    def __str__(self):
        if self.type is not None:
            out = f"{self.type} {self.name}"
            if self.type == "Const":
                out = f"{out} = {self.value}"

            if self.units is not None:
                out = f"{out} : Units {self.name} = {self.units}"

            return out
        return self.name


class TableItem:
    def __init__(self, func: str, field_names: list[str] | str, *args: str):
        self.func = func
        self.args = args
        self.field_names = field_names
        if isinstance(self.field_names, str):
            self.field_names = list[self.field_names]

    def __str__(self):
        return f"{self.func}({",".join(self.args)}) : FieldNames(\"{','.join(self.field_names)}\")"


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


@dataclass
class Wire:
    wire: str
    port: str
    description: str | None

    def __str__(self):
        return f"{self.wire + ':':<8} {self.port:<8} {self.description:<10}"


class WiringDiagram:
    def __init__(self, *args: Wire, description: str | None = None):
        self.args = args
        self.description = description

    def __str__(self):
        out = "'" + "\n'".join(str(x) for x in self.args)
        if self.description is not None:
            out += f"\n'{self.description}\n"
        return out


@dataclass
class Instrument:
    manufacturer: str
    model: str
    type: str
    elevation: int | None = None
    sdi12_address: str | None = None
    wiring: str | None = None
    variables: list[Variable] | None = None
    tables: list[Table] | None = None
    pre_scan: str | None = None
    program: str | None = None
    slow_sequence: str | None = None

    def __post_init__(self):
        self._extend_variable_names()
        self._validate_variables()

    def _extend_variable_names(self):
        for v in self.variables:
            if self.elevation is not None:
                v.name += f"_{self.elevation}"
            if self.sdi12_address is not None:
                v.name += f"_id{self.sdi12_address}"

    def _validate_variables(self):
        # TODO: This method will check that all variablese in
        # the tables are defined as variables.
        ...

    def _find_variable_references(self) -> list:
        # TODO: This will happen first. Make a map of where
        # references to each variable is so we can update names.
        ...


RMYoung_05108_74 = Instrument(
    manufacturer="RM Young",
    model=" 05108-74",
    type="Wind",
    wiring=WiringDiagram(
        Wire("Red", "P1", "WS Signal      WS SIG"),
        Wire("White", "VX2", "WD Excite      WD EXC"),
        Wire("Green", "SE7", "WD Signal      WD SIG"),
        Wire("Black", "AG", "Signal G       WD REF"),
        Wire("Brown", "G", "Earth G        GND*"),
        description="* NOTE: Ground to EARTH in junction box directly to mast",
    ),
    variables=list(
        Variable("WS_offset", "Const", 0),
        Variable("WS_multiplier", "Const", 0.1666),
        Variable("wind_spd", "Public", units="m s-1"),
        Variable("wind_dir", "Public", units="arcdeg"),
        Variable("wind_timer", "Public", units="sec"),
    ),
    tables=list(
        Table(
            "FiveMin",
            TableItem(
                "WindVector",
                list(
                    Variable("wind_spd"), Variable("wind_dir"), Variable("wind_dir_sd")
                ),
                1,
                Variable("wind_spd"),
                Variable("wind_dir"),
                "FP2",
                False,
                0,
                0,
                0,
            ),
            TableItem("Maximum", "windgust", 1, "wind_spd", "FP2", False, False),
            trig_var=True,
            size=-1,
            data_interval=DataInterval(),
            card_out=CardOut(),
        ),
        Table("StatusReport", TableItem()),
    ),
)
# Maximum(1,wind_spd_{elevation},FP2,False,False):FieldNames ("windgust_{elevation}")
