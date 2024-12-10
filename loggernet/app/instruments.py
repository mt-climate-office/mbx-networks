from pydantic import BaseModel

class Instrument(BaseModel):
    name: str
    wiring_diagram: list[str]
    variables: list[str]
    tables: dict[str, list[str]]
    pre_scan: list[str] | None = None
    program: list[str]
    slow_sequence: list[str]


class Program(BaseModel):
    # Thinking to not use a template. Each section of the program is a class that just 
    # has a tostring method that can all be joined together.
    pass