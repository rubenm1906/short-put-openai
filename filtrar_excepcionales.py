import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import tempfile

# Parámetros de filtro
FILTROS = {
    "rentabilidad_anual": 55,
    "percent_diff": 8,
    "bid": 1.00,
    "days_to_expiration": 25,
    "implied_volatility": 40,
    "iv_minus_hv": 10,
    "volume": 50,
    "open_interest": 100,
    "underlying_price": 150
}

# Archivos
INPUT_CSV = "storage/consolidado_validados.csv"
OUTPUT_CSV = "storage/consolidado_excepcionales.csv"
SHEET_NAME = "Short Put Screener Consolidado"
HOJA_EXCEPCIONALES = "Excepcionales"

# Cargar y filtrar datos
df = pd.read_csv(INPUT_CSV)
df["iv_minus_hv"] = df["implied_volatility"] - df["historical_volatility"]

df_filtrado = df[
    (df["rentabilidad_anual"] >= FILTROS["rentabilidad_anual"]) &
    (df["percent_diff"] >= FILTROS["percent_diff"]) &
    (df["bid"] >= FILTROS["bid"]) &
    (df["days_to_expiration"] <= FILTROS["days_to_expiration"]) &
    (df["implied_volatility"] >= FILTROS["implied_volatility"]) &
    (df["iv_minus_hv"] >= FILTROS["iv_minus_hv"]) &
    (df["volume"] >= FILTROS["volume"]) &
    (df["open_interest"] >= FILTROS["open_interest"]) &
    (df["underlying_price"] <= FILTROS["underlying_price"])
]

print(f"[INFO] Total contratos excepcionales encontrados: {len(df_filtrado)}")
if not df_filtrado.empty:
    print(df_filtrado[["ticker", "strike", "bid", "rentabilidad_anual", "percent_diff"]].head())
    df_filtrado.to_csv(OUTPUT_CSV, index=False)
    print(f"[✅] CSV guardado en {OUTPUT_CSV}")
else:
    print("[⚠️] No se encontraron contratos excepcionales. No se creó el CSV.")

# Subir a Google Sheets
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds_content = os.environ.get("GOOGLE_SHEETS_CREDS")

if creds_content:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(creds_content.encode())
        creds_path = tmp.name

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(SHEET_NAME)
        print(f"[INFO] Hoja encontrada: {SHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SHEET_NAME)
        print(f"[INFO] Hoja nueva creada: {SHEET_NAME}")

    try:
        worksheet = sheet.worksheet(HOJA_EXCEPCIONALES)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=HOJA_EXCEPCIONALES, rows="1000", cols="20")

    df_clean = df_filtrado.replace([float("inf"), float("-inf")], None)
    df_clean = df_clean.where(pd.notnull(df_clean), None)

    worksheet.clear()
    worksheet.update([df_clean.columns.values.tolist()] + df_clean.values.tolist())

    print(f"[✅] {len(df_clean)} contratos excepcionales exportados a Google Sheets.")
else:
    print("[⚠️] GOOGLE_SHEETS_CREDS no está definido. Solo se generó el CSV local.")
