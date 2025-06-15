import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import tempfile
from datetime import datetime

# Configuración de acceso
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

CSV_FILE = "storage/consolidado_validados.csv"
SPREADSHEET_NAME = "Short Put Screener Consolidado"

def export_to_google_sheets():
    print("🔍 Iniciando exportación a Google Sheets...")

    if not os.path.exists(CSV_FILE):
        print(f"[❌ ERROR] No se encontró el archivo CSV: {CSV_FILE}")
        return

    creds_content = os.environ.get("GOOGLE_SHEETS_CREDS")
    if not creds_content:
        print("[❌ ERROR] No se encontró la variable GOOGLE_SHEETS_CREDS.")
        return

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(creds_content.encode())
            creds_path = tmp.name

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
        client = gspread.authorize(creds)
        print("✅ Autenticación con Google Sheets exitosa.")

        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        print(f"📄 Archivo CSV cargado con {len(df)} filas y {len(df.columns)} columnas.")

        try:
            sheet = client.open(SPREADSHEET_NAME)
            print(f"[INFO] Hoja encontrada: {SPREADSHEET_NAME}")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(SPREADSHEET_NAME)
            print(f"[INFO] Hoja nueva creada: {SPREADSHEET_NAME}")
            sheet.share("rubenmarin19@gmail.com", perm_type="user", role="writer")
            print(f"📤 Hoja creada y compartida con rubenmarin19@gmail.com")

        worksheet = sheet.get_worksheet(0)

        # Limpieza robusta
        df_clean = df.replace([float("inf"), float("-inf")], pd.NA)
        df_clean = df_clean.fillna("")
        df_clean = df_clean.astype(str)

        worksheet.clear()
        worksheet.update([df_clean.columns.values.tolist()] + df_clean.values.tolist())
        print("✅ Exportación completada sin errores de JSON.")
        print(f"🔗 Link directo: https://docs.google.com/spreadsheets/d/{sheet.id}")

    except Exception as e:
        print("[❌ ERROR] Fallo inesperado:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_to_google_sheets()
