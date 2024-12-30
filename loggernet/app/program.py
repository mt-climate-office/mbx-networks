from dataclasses import dataclass, field
from datetime import date

from instruments import (
    Instrument,
    Table,
    Vaisala_HMP155,
    Acclima_TDR310N,
    RMYoung_05108_77,
)
from typing import Literal


@dataclass
class Program:
    name: str
    instruments: list[Instrument]
    mode: Literal["SequentialMode", "PipelineMode"] = "SequentialMode"
    preserve_variables: bool = True
    tables: list[Table] = field(init=False)

    def __post_init__(self):
        self.__find_tables()
        self.__check_unique_names()

    def __find_tables(self):
        tables = {}
        for instrument in self.instruments:
            for table in instrument.tables:
                if table.name in tables and tables[table.name] != table:
                    raise AttributeError(
                        f"More than one table named {table.name} exist, but have settings that don't match. Make sure that all tables named {table.name} share the same settings."
                    )
                if table.name in tables:
                    tables[table.name].args += table.args
                else:
                    tables[table.name] = table

        self.tables = list(tables.values())

    def __check_unique_names(self):
        keys = []
        for instrument in self.instruments:
            for key in instrument.variables.keys():
                if key in keys:
                    raise ValueError(
                        f"Variable name {key} is duplicated. Please define a name transform function or change in the instrument's configuration."
                    )
                else:
                    keys.append(key)

    def construct(self):
        s = f"'{self.name}\n'Program Created on: {date.today()}\n\n"
        s += "'SYSTEM CONFIGURATION\n"
        s += "\n".join(
            f"'{x.type}: {x.manufacturer} {x.model}" for x in self.instruments
        )
        s += "\n\nWiring Diagram\n"
        for i in self.instruments:
            s += f"####{i.model} Wiring####\n"
            s += str(i.wires) + "\n\n"

        for i in self.instruments:
            for v in i.variables.values():
                s += v.declaration_str() + "\n"

        s += "\n"
        if self.preserve_variables:
            s += "PreserveVariables\n"

        for table in self.tables:
            s += str(table) + "\n\n"

        return s


def rename_soil(i: Instrument) -> None:
    for v in i.variables:
        if "(" in v.name:
            v.name = v.name.replace("soil", f"soil_{i}")


my_sensors = [
    Vaisala_HMP155(200),
    Acclima_TDR310N(5, "1"),
    Acclima_TDR310N(5, "a"),
    Acclima_TDR310N(10, "2"),
    Acclima_TDR310N(10, "b"),
    RMYoung_05108_77(1000),
]

program = Program("test program", my_sensors, "SequentialMode", True)

print(program.construct())
