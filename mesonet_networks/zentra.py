from record import Record, Networks
import json
from typing import Any

import json

with open("../tests/zentra_records.json", "r") as json_file:
    data = json.load(json_file)


def parse_zentra_records(data: dict[str, Any]) -> list[Record]:
    
    records = []
    for element, record in data.items():
        ...