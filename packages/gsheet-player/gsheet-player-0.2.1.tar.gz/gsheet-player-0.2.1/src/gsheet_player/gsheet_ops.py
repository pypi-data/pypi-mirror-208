# Standard library imports
import json
import logging

# Third party imports
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

log = logging.getLogger(__name__)


def read_json_creds(client):
    try:
        response = client.get_parameter(
            Name="/NJTC/GoogleSheets/service/cred", WithDecryption=True
        )
        return json.loads(response["Parameter"]["Value"])
    except Exception as e:
        log.error(f"Reading Parameter Store {e}")
        raise e


def read_gsheet(client, spreadsheet_id, range_name):
    rows = []
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    # AWS way from Parameter Store
    json_acct_info = read_json_creds(client)
    credentials = service_account.Credentials.from_service_account_info(
        json_acct_info, scopes=scopes
    )

    try:
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        log.info("{0} rows retrieved.".format(len(rows)))
    except HttpError as error:
        log.error(f"An error occurred: {error}")

    return rows


def appendLine(client, spreadsheet_id, values, range_name, range):
    try:
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ]

        # AWS way from Parameter Store
        json_acct_info = read_json_creds(client)
        credentials = service_account.Credentials.from_service_account_info(
            json_acct_info, scopes=scopes
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        data = {"values": values}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            body=data,
            range=range_name,
            valueInputOption="USER_ENTERED",
        ).execute()

    except OSError as e:
        log.info(e)


def sortSheet(client, spreadsheet_id):
    try:
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        # AWS way from Parameter Store
        json_acct_info = read_json_creds(client)
        credentials = service_account.Credentials.from_service_account_info(
            json_acct_info, scopes=scopes
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        body = {
            "requests": [
                {
                    "sortRange": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 1,
                            "endRowIndex": 800,
                            "startColumnIndex": 0,
                            "endColumnIndex": 14,
                        },
                        "sortSpecs": [
                            {"dimensionIndex": 4, "sortOrder": "ASCENDING"},
                            {"dimensionIndex": 1, "sortOrder": "ASCENDING"},
                        ],
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()

    except OSError as e:
        log.info(e)


def updateLine(client, spreadsheet_id, values, index, range):
    try:
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ]

        # AWS way from Parameter Store
        json_acct_info = read_json_creds(client)
        credentials = service_account.Credentials.from_service_account_info(
            json_acct_info, scopes=scopes
        )
        range_name = range + "!A" + str(index) + ":N" + str(index)
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        # log.info(f"Updating spreadsheet with values: {values}")
        data = {"values": values}
        # log.info(f"spreadsheet_id={spreadsheet_id} body={data} range={range_name}")
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            body=data,
            range=range_name,
            valueInputOption="USER_ENTERED",
        ).execute()

    except OSError as e:
        log.info(e)


def updateLineColor(client, gsheet, row, color):
    """Updates Google Sheet line with highlight color

    Args:
        client (boto3_client): Boto3 client descriptor
        gsheet (_type_): dict with all gsheet info, defined in __main__
        row (_type_): gsheet row with person of interest
        color (_type_): highlight color
    """
    try:
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ]

        gid = gsheet["sheetId"]
        # AWS way from Parameter Store
        json_acct_info = read_json_creds(client)
        credentials = service_account.Credentials.from_service_account_info(
            json_acct_info, scopes=scopes
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        if "white" in color:
            bg_color = {"red": 1, "green": 1, "blue": 1}
        elif "red" in color:
            bg_color = {"red": 1, "green": 0, "blue": 0}
        elif "yellow" in color:
            bg_color = {"red": 1, "green": 1, "blue": 0}
        else:
            bg_color = {"red": 1, "green": 1, "blue": 1}

        # TODO make the sheetID (GID) for this api call
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": gid,
                            "startRowIndex": row - 1,
                            "endRowIndex": row,
                            "startColumnIndex": 0,
                            "endColumnIndex": 14,
                        },
                        "cell": {"userEnteredFormat": {"backgroundColor": bg_color}},
                        "fields": "userEnteredFormat.backgroundColor",
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=gsheet["spreadsheetId"], body=body
        ).execute()

    except OSError as e:
        log.info(e)
