from app.instruments import INSTRUMENTS, WireOptions
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal

ValidInstruments = Enum(
    "ValidInstruments", dict((v._id, v._id) for v in INSTRUMENTS.values())
)


class NamesOnly(BaseModel):
    names_only: bool = Field(
        False,
        description="Whether a list of only names should be returned. By default, a json object with detailed instrument information is returned.",
    )


class ProgramInstruments(BaseModel):
    name: str = Field(description="Name of the instrument")
    elevation: int | None = Field(description="The sensor's elevation in cm.")
    sdi12_address: int | str | None = Field(
        "The sensor's SDI12 address (if it is an SDI12 instrument)."
    )
    var_name_inclusion: Literal["sdi12", "elevation", "both", "none"] = Field(
        "Whether to include sensor metadata in the variable name"
    )
    wiring: dict[str, WireOptions | None] = Field(
        "The wiring configuration for the sensor."
    )
    dependencies: dict[str, dict[str, str]] | None = Field(
        "A dictionary defining the variable dependencies of this instrument."
    )
