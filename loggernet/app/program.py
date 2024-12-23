from dataclasses import dataclass, field
from datetime import date

from instruments import Instrument, Table
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

    def __find_tables(self):
        # TODO: Here look through instruments and find all shared tables.
        ...
    def construct(self):
        s = f"'{self.name}\n'Program Created on: {date.today()}\n\n"
        s += "'SYSTEM CONFIGURATION\n"
        s += "\n".join(
            f"'{x.type}: {x.manufacturer} {x.model}" for x in self.instruments
        )
        s += "\n\nWiring Diagram\n"
        for i in self.instruments:
            s += f"####{i.model} Wiring####\n"
            s += str(i.wiring)

        s += "\n".join()

        ...
