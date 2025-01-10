from dataclasses import dataclass, field
from datetime import date
import re

from instruments import (
    Instrument,
    Table,
    Vaisala_HMP155,
    Acclima_TDR310N,
    RMYoung_05108_77,
    Scan,
    SlowSequence,
)
from typing import Literal
from textwrap import indent


@dataclass
class Program:
    name: str
    instruments: list[Instrument]
    mode: Literal["SequentialMode", "PipelineMode"] = "SequentialMode"
    preserve_variables: bool = True
    include_batt: bool = False
    scan: Scan = field(default_factory=lambda: Scan(3, "Sec", 1, 0))
    tables: list[Table] = field(init=False)
    functions: list[str] = field(init=False)
    slow_sequence: list[SlowSequence] = field(init=False)

    def __post_init__(self):
        self.__find_tables()
        self.__find_functions()
        self.__group_slow_sequence()
        self.__check_unique_names()
        self.__validate_dependencies()

    def __find_functions(self):
        functions = set()
        for instrument in self.instruments:
            try:
                if f := instrument.funcs:
                    functions.add(f)
            except NotImplementedError:
                continue

        self.functions = list(functions)

    # TODO: Implement logic to make sure if an instruemnt has a dependency,
    # that the dependency indeed exists.
    def __validate_dependencies(self): ...

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

    def __group_slow_sequence(self):
        ss: dict[str, SlowSequence] = {}

        for instrument in self.instruments:
            if i := instrument.slow_sequence:
                if i.id in ss:
                    target = ss[i.id]
                    target.logic = f"{target.logic}\n{i.logic}"
                else:
                    ss[i.id] = i

        self.slow_sequence = "\n\n".join(str(x) for x in ss.values())

    def __check_unique_names(self):
        keys = []
        for instrument in self.instruments:
            for k, v in instrument.variables.items():
                val = v.rename_to or k
                if val in keys:
                    raise ValueError(
                        f"Variable name {val} is duplicated. Please define a name transform function or change in the instrument's configuration."
                    )
                else:
                    keys.append(val)

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

        if self.functions:
            s += "\n".join(self.functions)
            s += "\n"

        s += "BeginProg\n"

        for i in self.instruments:
            if ps := i.pre_scan:
                s += indent(ps, "    ")
                s += "\n\n"

        s += f"    {str(self.scan)}\n\n"

        for i in self.instruments:
            if pr := i.program:
                s += indent(pr, "    ")
                s += "\n\n"

        s += "\n    NextScan\n\n"

        calltable = "\n".join([f"CallTable {x.name}" for x in self.tables])

        s += indent(calltable, "    ")
        s += "\n\n"

        for i in self.instruments:
            if ps := i.post_scan:
                s += indent(ps, "    ")
                s += "\n\n"

        s += "NextScan\n\n"

        s += indent(self.slow_sequence, "    ")

        s += "\n\nEndProg"

        return s


def rename_soil(i: Instrument) -> None:
    pattern = r"\(\d+\)"
    for v in i.variables.values():
        # Only match if it is not an array.
        if not re.search(pattern, v.name):
            v.rename_to = f"{v.name}_{i.elevation:04}_id{i.sdi12_address}"


my_sensors = [
    Vaisala_HMP155(200),
    Acclima_TDR310N(5, "1", transform=rename_soil),
    Acclima_TDR310N(5, "a", transform=rename_soil),
    Acclima_TDR310N(10, "2", transform=rename_soil),
    Acclima_TDR310N(10, "b", transform=rename_soil),
    RMYoung_05108_77(1000),
]

program = Program("test program", my_sensors, "SequentialMode", True)

print(program.construct())
