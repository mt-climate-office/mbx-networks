from mesonet_networks import parse_zentra_json, parse_loggernet_json, records_to_dataframe
import json

with open("../tests/loggernet.json", "r") as json_file:
    data = json.load(json_file)


with open("../tests/zentra_records.json", "r") as json_file:
    data = json.load(json_file)