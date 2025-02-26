from dataclasses import dataclass, field
from datetime import date
import re

from app.instruments import (
    Instrument,
    Table,
    Acclima_TDR310N,
    Scan,
    SlowSequence,
)
from app.functions import VarType
from typing import Callable, Literal
from textwrap import indent


@dataclass
class Program:
    name: str
    instruments: list[Instrument]
    mode: Literal["SequentialMode", "PipelineMode"] = "SequentialMode"
    preserve_variables: bool = True
    scan: Scan = field(default_factory=lambda: Scan(3, "Sec", 1, 0))
    tables: list[Table] = field(init=False)
    functions: list[str] = field(init=False)
    slow_sequence: list[SlowSequence] = field(init=False)

    transform: Callable[["Program"], "Program"] | None = None

    def __post_init__(self):
        if self.transform is not None:
            self._transform()

        self.__find_tables()
        self.__find_functions()
        self.__group_slow_sequence()
        self.__check_unique_names()
        self.__validate_dependencies()

    def _transform(self):
        self.transform(self)

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
    def __validate_dependencies(self): 
        ...

    def __find_tables(self):
        tables = {}
        for instrument in self.instruments:
            try: 
                tabs = instrument.tables
            except NotImplementedError:
                continue

            for table in tabs:
                if table.name in tables and tables[table.name] != table:
                    raise AttributeError(
                        f"More than one table named {table.name} exist, but have settings that don't match. Make sure that all tables named {table.name} share the same settings."
                    )
                if table.name in tables:
                    tables[table.name].table_items += table.table_items
                else:
                    tables[table.name] = table

        self.tables = list(tables.values())

    def __group_slow_sequence(self):
        ss: dict[str, SlowSequence] = {}

        for instrument in self.instruments:
            try:
                if i := instrument.slow_sequence:
                    if i.id in ss:
                        target = ss[i.id]
                        target.logic = f"{target.logic}\n{i.logic}"
                    else:
                        ss[i.id] = i
            except NotImplementedError:
                continue

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

    def construct(self) -> str:
        s = f"'{self.name}\n'Program Created on: {date.today()}\n\n"
        s += "'SYSTEM CONFIGURATION\n"
        s += "\n".join(
            f"'{x.type}: {x.manufacturer} {x.model}" for x in self.instruments
        )
        s += "\n\n'Wiring Diagram\n"
        for i in self.instruments:
            if i.wires is not None:
                s += f"'####{i.model} Wiring####\n"
                s += str(i.wires) + "\n\n"

        for i in self.instruments:
            for v in i.variables.values():
                if v.var_type != VarType.FIELD_ONLY:
                    s += v.declaration_str() + "\n"

        s += "\n"
        if self.preserve_variables:
            s += "PreserveVariables\n"

        s += f"{self.mode}\n"

        for table in self.tables:
            s += str(table) + "\n\n"

        if self.functions:
            s += "\n".join(self.functions)
            s += "\n"

        s += "BeginProg\n"

        for i in self.instruments:
            try:
                if ps := i.pre_scan:
                    s += indent(ps, "    ")
                    s += "\n\n"
            except NotImplementedError:
                continue

        s += f"    {str(self.scan)}\n\n"

        for i in self.instruments:
            try:
                if pr := i.program:
                    s += indent(pr, "        ")
                    s += "\n\n"
            except NotImplementedError:
                continue

        calltable = "\n".join([f"CallTable {x.name}" for x in self.tables])

        s += indent(calltable, "        ")
        s += "\n\n"

        for i in self.instruments:
            try:
                if ps := i.post_scan:
                    s += indent(ps, "    ")
                    s += "\n\n"
            except NotImplementedError:
                continue

        s += "    NextScan\n\n"

        s += indent(self.slow_sequence, "    ")

        s += "\n\nEndProg"

        return s


def elev_sdi12_rename(i: Instrument, which: Literal["sdi12", "elevation", "both", "none"]) -> None:
    assert which in ["sdi12", "elevation", "both", "none"], "'which' must be sdi12, elevation, or both."
    if which == "none":
        return i
    pattern = r"\(\d+\)"
    for v in i.variables.values():
        # Only match if it is not an array.
        if which == "both":
            if not re.search(pattern, v.name):
                v.rename_to = f"{v.name}_{i.elevation:04}_id{i.sdi12_address}"
        elif which == "sdi12":
            if not re.search(pattern, v.name):
                v.rename_to = f"{v.name}_id{i.sdi12_address}"
        else: 
            if not re.search(pattern, v.name):
                v.rename_to = f"{v.name}_{i.elevation:04}"


def soil_slow_seq_match(p: Program) -> None:
    probes = []

    for i in p.instruments:
        if i.type == "Soil":
            probes.append(i)

    if probes:
        first: Acclima_TDR310N = probes.pop(0)
        ss_logic = first.slow_sequence.logic
        for probe in probes:
            if ss_logic == (new_logic := probe.slow_sequence.logic):
                ss_logic += new_logic
            probe.slow_sequence = None

