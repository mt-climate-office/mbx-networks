from pydantic import BaseModel, Field, AliasChoices, ConfigDict
import datetime as dt
from enum import Enum
from typing import Any
import polars as pl


class Networks(Enum):
    LOGGERNET: str = "LoggerNet"
    ZENTRA: str = "Zentra"


class Record(BaseModel):
    datetime: dt.datetime = Field(validation_alias=AliasChoices("@time", "datetime"))
    logger_sn: str = Field(validation_alias=AliasChoices("serial-no", "device_sn", "logger_sn"))
    network: Networks
    element: str = Field(validation_alias=AliasChoices("@name", "element"))
    value: int | float | None
    units: str = Field(validation_alias=AliasChoices("@units", "units"))
    extra_data: dict[str, Any] | None = Field(default_factory=dict)
    model_config = ConfigDict(
        extra="allow",
    )

    def model_post_init(self, __context: Any) -> None:
        if not self.extra_data:
            self.extra_data = self.model_extra
    
    def model_dump(self, **kwargs) -> dict[str, any]:
        to_exclude = {k: True for k in self.model_extra}
        return super().model_dump(exclude=to_exclude, **kwargs)

    def model_dump_json(self, **kwargs) -> dict[str, any]:
        to_exclude = {k: True for k in self.model_extra}
        return super().model_dump_json(to_exclude, **kwargs)
    


def records_to_dataframe(records: list[Record]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            x.model_dump() for x in records
        ]
    )