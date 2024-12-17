from pydantic import BaseModel
from datetime import date

from instruments import Instrument
from typing import Literal


class Program(BaseModel):
    name: str
    instruments: list[Instrument]
    mode: Literal["SequentialMode", "PipelineMode"] = "SequentialMode"
    preserve_variables: bool = True

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
