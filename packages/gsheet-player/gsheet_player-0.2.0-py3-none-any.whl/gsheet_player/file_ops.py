# Standard library imports
import json
import logging
from collections import namedtuple
from pathlib import Path

# gsheet_player imports
from gsheet_player.gsheetPlayer import gsheetPlayer

log = logging.getLogger(__name__)


def json_file_read(filename):
    player_uids = {}
    local_file = Path(filename)
    if local_file.is_file():
        with open(filename, "r") as read_file:
            log.info(f"Reading JSON file for input: {filename}")
            data = json.load(read_file)

        # Get field names for namedtuple construction from first record
        first = next(iter(data))
        Person = namedtuple("Person", data[first]["field_names"], defaults=["", 0, []])

        for count, (player_uid, player) in enumerate(data.items()):
            log.info(f"player {count}: {player['original']}")

            person = Person(*player["original"])
            player_uids[player_uid] = gsheetPlayer(
                person,
                player["row"],
                player["gsheet"],
            )
            log.warning(
                f"Adding UID: {player_uid} with record {player_uids[player_uid]}"
            )

    return player_uids


def json_file_write(players, filename):
    data = {}
    for player in players:
        data[player] = players[player].dump
    try:
        with open(filename, "w") as write_file:
            json.dump(data, write_file, indent=4)
    except Exception as e:
        log.error(f"Writing JSON file: {e}")


def read_gsheets(gsheet, all_rows, by_email=False):
    """Read list of rows from spreadsheet into namedtuple for easier class entry"""
    players = {}
    emails = {}

    # Create iterator for list of lists
    reader = iter(all_rows)

    # Iterate on first row for header values to name fields
    Person = namedtuple("Person", next(reader), rename=True, defaults=["", 0, [], ""])
    for i, row in enumerate(reader, start=2):
        person = Person(*row)
        curr = gsheetPlayer(person, i, gsheet)
        if curr.cid in players and "FREE" not in curr.cid:
            log.warning(f"DUPLICATE ENTRY: {curr} {curr.cid} row={i}, ignoring...")
        else:
            players[curr.cid] = curr
            if by_email:
                emails[curr.email] = curr

    if by_email:
        return players, emails
    else:
        return players
