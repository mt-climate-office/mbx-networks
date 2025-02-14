from app.instruments import INSTRUMENTS
from pydantic import BaseModel, Field
from enum import Enum
from fastapi import Query

ValidInstruments = Enum("ValidInstruments", dict((key, key) for key in INSTRUMENTS.keys()))

class NamesOnly(BaseModel):
    names_only: bool = Field(False, description="Whether a list of only names should be returned. By default, a json object with detailed instrument information is returned.")