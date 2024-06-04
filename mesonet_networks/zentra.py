from .record import Record, Networks
from typing import Any


def parse_zentra_json(data: dict[str, Any]) -> list[Record]:
    out = []
    for element, records in data.items():
        for record in records:
            metadata = record["metadata"]
            readings = record["readings"]
            if (read_len := len(readings)) > 1:
                raise ValueError(f"Readings has {read_len} items. Should have 1.")

            out.append(
                Record(
                    **metadata, **readings[0], element=element, network=Networks.ZENTRA
                )
            )

    return out
