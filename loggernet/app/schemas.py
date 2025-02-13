from app.instruments import INSTRUMENTS
from enum import Enum

ValidInstruments = Enum("ValidInstruments", dict((key, key) for key in INSTRUMENTS.keys()))