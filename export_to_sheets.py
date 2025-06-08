
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configuración de acceso
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Nombre del archivo de credenciales
CREDENTIALS_FILE = "credentials.json"

# Nombre del archivo CSV que quieres subir
CSV_FILE = "storage/shortlist_ruben_resultados.csv"

# Nombre de la hoja de cálculo a crear (o actualizar)
SPREADSHEET_NAME = "Resultados Short Put - Rubén"

def export_to_google_sheets():
    # Verifica existencia de archivo de credenciales
    if not os.path.exists(CREDENTIALS_FILE):
        print("[ERROR] No se encontró 'credentials.json'")
        return

    # Verifica existencia del CSV
    if not os.path.exists(CSV_FILE):
        print(f"[ERROR] No se encontró el archivo CSV: {CSV_FILE}")
        return

    # Autenticación con Google
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)

    # Cargar el CSV
    df = pd.read_csv(CSV_FILE)

    # Crear o abrir Google Sheet
    try:
        sheet = client.open(SPREADSHEET_NAME)
        print(f"[INFO] Hoja existente encontrada: {SPREADSHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SPREADSHEET_NAME)
        print(f"[INFO] Hoja nueva creada: {SPREADSHEET_NAME}")

    worksheet = sheet.get_worksheet(0)
    worksheet.clear()  # Borra el contenido previo
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("[✅] Exportación completada con éxito.")

if __name__ == "__main__":
    export_to_google_sheets()
