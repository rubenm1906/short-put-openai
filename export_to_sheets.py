import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import tempfile

# Configuración de acceso
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

CSV_FILE = "storage/consolidado_validados.csv"
SPREADSHEET_NAME = "Resultados Short Put - Rubén"

def export_to_google_sheets():
    if not os.path.exists(CSV_FILE):
        print(f"[ERROR] No se encontró el archivo CSV: {CSV_FILE}")
        return

    creds_content = os.environ.get("GOOGLE_SHEETS_CREDS")
    if not creds_content:
        print("[ERROR] No se encontró la variable GOOGLE_SHEETS_CREDS.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(creds_content.encode())
        creds_path = tmp.name

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
    client = gspread.authorize(creds)

    df = pd.read_csv(CSV_FILE)

    try:
        sheet = client.open(SPREADSHEET_NAME)
        print(f"[INFO] Hoja encontrada: {SPREADSHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SPREADSHEET_NAME)
        print(f"[INFO] Hoja nueva creada: {SPREADSHEET_NAME}")

    worksheet = sheet.get_worksheet(0)

    # Limpiar datos para que sean compatibles con JSON
    df_clean = df.replace([float("inf"), float("-inf")], None)
    df_clean = df_clean.where(pd.notnull(df_clean), None)

    worksheet.clear()
    worksheet.update([df_clean.columns.values.tolist()] + df_clean.values.tolist())
    print("[✅] Exportación completada sin errores de JSON.")

if __name__ == "__main__":
    export_to_google_sheets()
