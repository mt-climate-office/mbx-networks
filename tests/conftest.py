import pytest
import json
from typing import Any


@pytest.fixture(scope="session")
def loggernet() -> dict[str, Any]:
    with open("./tests/loggernet.json", "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture(scope="session")
def zentra() -> dict[str, Any]:
    with open("./tests/zentra.json", "r") as json_file:
        data = json.load(json_file)
    return data
