
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

# Nombre del archivo CSV que quieres subir
CSV_FILE = "storage/shortlist_ruben_resultados.csv"

# Nombre del Google Sheet a actualizar
SPREADSHEET_NAME = "Resultados Short Put - Rubén"

def export_to_google_sheets():
    # Verificar existencia de archivo CSV
    if not os.path.exists(CSV_FILE):
        print(f"[ERROR] No se encontró el archivo CSV: {CSV_FILE}")
        return

    # Leer las credenciales desde variable de entorno (secreto en GitHub)
    creds_content = os.environ.get("GOOGLE_SHEETS_CREDS")
    if not creds_content:
        print("[ERROR] No se encontró la variable GOOGLE_SHEETS_CREDS.")
        return

    # Guardar las credenciales en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(creds_content.encode())
        creds_path = tmp.name

    # Autenticación con Google
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
    client = gspread.authorize(creds)

    # Leer datos del CSV
    df = pd.read_csv(CSV_FILE)

    # Abrir o crear el Google Sheet
    try:
        sheet = client.open(SPREADSHEET_NAME)
        print(f"[INFO] Hoja encontrada: {SPREADSHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SPREADSHEET_NAME)
        print(f"[INFO] Hoja nueva creada: {SPREADSHEET_NAME}")

    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("[✅] Exportación completada correctamente.")

if __name__ == "__main__":
    export_to_google_sheets()
