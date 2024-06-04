from mesonet_networks import (
    parse_zentra_json,
    parse_loggernet_json,
    records_to_dataframe,
)
import polars as pl


def test_zentra_valid(zentra):
    data = parse_zentra_json(zentra)

    assert len(data) > 0, "Zentra records not parsed correctly."


def test_loggernet_valid(loggernet):
    data = parse_loggernet_json(loggernet)

    assert len(data) > 0, "Loggernet records not parsed correctly."


def test_to_df(loggernet):
    data = parse_loggernet_json(loggernet)
    df = records_to_dataframe(data)

    assert isinstance(df, pl.DataFrame), "DataFrame isn't correct type."
    assert len(df) == len(data), "Records dropped in df conversion"
