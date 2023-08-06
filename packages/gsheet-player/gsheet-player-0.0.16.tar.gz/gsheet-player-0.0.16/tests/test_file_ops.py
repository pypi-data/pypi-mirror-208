# Standard library imports
import csv
import pathlib

# Third party imports
import pytest

# gsheet_player imports
from src.gsheet_player.file_ops import read_gsheets
from src.gsheet_player.gsheetPlayer import gsheetPlayer

# Current directory
HERE = pathlib.Path(__file__).resolve().parent


@pytest.fixture
def gsheet_indentification():
    gsheet = {
        "spreadsheetId": "1ggnQy5oLlxPYRjrRpP4ihI6sZJhr-SsQ9CfJRJOgF-o",
        "sheetId": "0",
        "sheetName": "Members",
    }
    return gsheet


@pytest.fixture
def local_csv():
    """Use local CSV file instead of from Google Sheets."""
    all_rows = []
    with open(HERE / "test_players.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            all_rows.append(row)
    return all_rows


@pytest.mark.file_test
def test_read_local_file(local_csv, gsheet_indentification):
    gsheetPlayers = read_gsheets(gsheet_indentification, local_csv)
    assert len(gsheetPlayers) == 5



@pytest.mark.file_test
def test_player_content(local_csv, gsheet_indentification):
    gsheetPlayers = read_gsheets(gsheet_indentification, local_csv)
    assert isinstance(gsheetPlayers, dict)
    assert len(gsheetPlayers) == 5
    # assert gsheetPlayers.keys() == "this"
    if isinstance(gsheetPlayers, dict):
        p = gsheetPlayers["ch_3MrmtPBaXyCqtgjV1RWmcSJN"]
        assert p.name == "CINDY LORSH"
        assert p.name_proper == "Cindy Lorsh"
        assert p.ntrp == "2.5"
        assert p.usta == "2019444444"
        assert gsheetPlayers["ch_3MfDVwBaXyCqtgjV13SRAn0i"].name == "Bob Smith"
        assert gsheetPlayers['ch_3MXzPSBaXyCqtgjV1brSabct'].name == "Barb James"
        assert gsheetPlayers['ch_3MzgUXBaXyCqtgjV0zvpriil'].name == "Colby Corker"


# TODO Test JSON serializer
@pytest.mark.file_test
def test_serializer():
    pass

    # Read serialized data to file
    # json_filename = "teams_last_read.json"

    # Write serialized data to file
    # json_file_write(gsheetPlayers, json_filename)