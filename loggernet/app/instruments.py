from abc import ABC, abstractmethod
from pydantic import BaseModel

class Instrument(BaseModel):
    name: str
    wiring_diagram: list[str] | None = None
    variables: list[str]
    tables: dict[str, list[str]]
    pre_scan: list[str] | None = None
    program: list[str] | None = None
    slow_sequence: list[str] | None = None

# define each sensor here