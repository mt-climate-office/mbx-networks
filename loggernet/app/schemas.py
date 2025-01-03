from instruments import INSTRUMENTS
from enum import Enum

valid_instruments = Enum("ValidInstruments", {key: key for key in INSTRUMENTS.keys()})