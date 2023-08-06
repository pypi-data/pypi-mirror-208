# Google Sheet Tennis Player

gsheet-player is a Python library for dealing with a Google Sheet of tennis
player information.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install gsheet-player.

```bash
pip install gsheet-player
```

## Usage

```python
import gsheet-player

# Given information about a Google Sheet in this dictionary
gsheet = {
        "spreadsheetId": "1eUR2RpS-yvA8cb-IlwHqmfphHgaKb2SXXREaYEPJrMU",
        "sheetId": "1088338784",
        "sheetName": "Members",
    }
# read_gsheet returns all rows in a list of lists
all_rows = read_gsheet(ssm_client, gsheet["spreadsheetId"], gsheet["sheetName"] + "!A1:N800")

# read_gsheets returns a dictionary with one value as key and the gsheetPlayer object as value
gsheetPlayers = read_gsheets(gsheet, all_rows)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
