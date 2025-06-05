import os.path

import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
RANGE_NAME = "A1:G20"


def googleLogin():

    creds = None
    

    if os.path.exists("google_utils/token.json"):
        creds = Credentials.from_authorized_user_file("google_utils/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_utils/google-credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8090, open_browser=False)

        # Save the credentials for the next run
        with open("google_utils/token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

def readSpreadsheet(creds,SPREADSHEET_ID):
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Si no hi ha valors o només té una fila (la de títols), salta error
    if not values or len(values) < 2:
        print("No data found. Empty SpreadSheet")
        return []

    # La primera fila son los nombres de las columnas
    columns = values[0]
    data = values[1:]

    # Convertimos a DataFrame para facilitar el manejo de tipos
    df = pd.DataFrame(data, columns=columns)
    for col in ['MIN_PRICE', 'MAX_PRICE', 'LONGITUDE', 'LATITUDE', 'DISTANCE']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.to_dict(orient='records')

if __name__ == "__main__":
    creds = googleLogin()
    busquedas = readSpreadsheet(creds)
    for b in busquedas:
        print(b['MIN_PRICE'])
