# Third party imports
import pytest

# gsheet_player imports
import gsheet_player.gsheetPlayer as gsheetPlayer


@pytest.fixture
def gsheet_indentification():
    gsheet = {
        "spreadsheetId": "1ggnQy5oLlxPYRjrRpP4ihI6sZJhr-SsQ9CfJRJOgF-o",
        "sheetId": "0",
        "sheetName": "Members",
    }
    return gsheet


@pytest.mark.class_test
def test_constructor():
    row = 2
    person = [
        "2023-03-09 01:21:30 UTC",
        "thomas T steves",
        "tom@fastmail.com",
        "(312) 560-3344",
        "3",
        "20189053543",
        "Male",
        "65+",
        "120",
        "no",
        "ch_3MjYAGBaXyCqtgjV0ufo17EF",
        "ch_3MoQWjBaXyCqtgjV1WJxrEZH",
    ]

    # Tests
    p = gsheetPlayer.gsheetPlayer(person, row, gsheet_indentification)
    assert isinstance(p, gsheetPlayer.gsheetPlayer)
    assert p.name == "thomas T steves"
    assert p.name_proper == "Thomas Steves"
    assert p.name_lower == "thomas t steves"
    assert p.ntrp == "3"
    assert p.usta == "20189053543"
    p.league_list = ["team1", "team2"]
    assert p.league_list == ["team1", "team2"]


@pytest.mark.class_test
def test_limits():
    row = 3
    person = []
    p = gsheetPlayer.gsheetPlayer(person, row, gsheet_indentification)
    assert p.name is None
    with pytest.raises(ValueError):
        p.league_list = "not a list"
    with pytest.raises(ValueError):
        p.league_count = -1
    with pytest.raises(ValueError):
        p.league_count = ""
