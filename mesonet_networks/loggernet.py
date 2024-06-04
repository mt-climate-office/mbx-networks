from pydantic import ValidationError
from typing import Any
from .record import Networks, Record


def parse_loggernet_json(data: dict[str, Any]) -> list[Record]:
    if "csixml" not in data:
        raise KeyError(
            "LoggerNet record does not have 'csixml' key. JSON is not formatted correctly."
        )
    else:
        data = data["csixml"]

    metadata = data["head"]["environment"]

    fields = data["head"]["fields"]["field"]

    record_sets = data["data"]["r"]

    records = []
    for record in record_sets:
        observations = [
            {"value": v, "@time": record["@time"]}
            for k, v in record.items()
            if k.startswith("v")
        ]
        assert len(observations) == len(
            fields
        ), "Observations and field headers are not the same length."

        for x, y in zip(fields, observations):
            try:
                r = Record(**x, **y, **metadata, network=Networks.LOGGERNET)
                records.append(r)
            except ValidationError:
                ...

    return records
