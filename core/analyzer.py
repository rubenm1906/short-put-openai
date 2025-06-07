# core/analyzer.py (con ruta absoluta de los CSV)

import os
import pandas as pd
from core.data_loader import get_option_data_yahoo
from core.volatility import calculate_volatility_metrics
from notifications.discord import send_discord_notification
from datetime import datetime

def run_group_analysis(group_id, group_data):
    description = group_data.get("description", group_id)
    webhook = group_data.get("webhook")
    tickers = group_data.get("tickers", [])
    filters = group_data.get("filters", {})
    thresholds = group_data.get("alert_thresholds", {})

    all_contracts = []
    alerted_contracts = []

    storage_path = "storage"
    if os.path.exists(storage_path) and not os.path.isdir(storage_path):
        os.remove(storage_path)
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    print(f"[INFO] Iniciando análisis del grupo: {group_id}")
    for ticker in tickers:
        print(f"[INFO] Descargando opciones para {ticker}...")
        option_data = get_option_data_yahoo(ticker, filters)
        if not option_data:
            print(f"[WARN] No se encontraron opciones para {ticker}")
            continue

        print(f"[INFO] {len(option_data)} contratos recibidos para {ticker}")
        for contract in option_data:
            if not is_contract_valid(contract, filters):
                print(f"[DEBUG] ✖️ Rechazado por filtros: {contract}")
                continue
            contract["ticker"] = ticker
            all_contracts.append(contract)

            print("[VALIDO]", ticker, f"Strike: {contract['strike']}",
                  f"Bid: {contract['bid']}",
                  f"RA: {contract['rentabilidad_anual']:.1f}%",
                  f"Días: {contract['days_to_expiration']}")

            if is_contract_alert_worthy(contract, thresholds):
                contract["score"] = calculate_contract_score(contract)
                alerted_contracts.append(contract)
                print("[ALERTA DETECTADA]", ticker, f"Score: {contract['score']}")

    if all_contracts:
        df = pd.DataFrame(all_contracts)
        csv_path = f"{storage_path}/{group_id}_resultados.csv"
        df.to_csv(csv_path, index=False)
        print(f"[INFO] {len(df)} contratos guardados en CSV")
        print(f"[DEBUG] Archivo generado: {os.path.abspath(csv_path)}")

    if alerted_contracts:
        df_alerts = pd.DataFrame(alerted_contracts)
        alert_csv_path = f"{storage_path}/alertados_{group_id}.csv"
        df_alerts.to_csv(alert_csv_path, index=False)
        print(f"[INFO] {len(df_alerts)} alertas guardadas en alertados_{group_id}.csv")
        print(f"[DEBUG] Archivo generado: {os.path.abspath(alert_csv_path)}")

    resumen_path = f"{storage_path}/resumen_{group_id}.txt"
    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write(f"=== Grupo: {group_id} ===\n")
        f.write(f"Descripción: {description}\n")
        f.write(f"Tickers analizados: {', '.join(tickers)}\n")
        f.write(f"Contratos válidos encontrados: {len(all_contracts)}\n")
        f.write(f"Contratos que cumplen umbrales de alerta: {len(alerted_contracts)}\n")
        f.write(f"Última ejecución: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        if len(all_contracts) == 0:
            f.write("\nSin oportunidades detectadas en esta ejecución.\n")

    if len(all_contracts) == 0:
        print("[INFO] Sin oportunidades detectadas en esta ejecución.")

    print(f"[INFO] Total válidos: {len(all_contracts)} | Total alertas: {len(alerted_contracts)}")

    if thresholds.get("notificar_discord") and alerted_contracts:
        send_discord_notification(alerted_contracts, webhook, description)

def is_contract_valid(contract, filters):
    return (
        contract["rentabilidad_anual"] >= filters.get("min_rentabilidad_anual", 0) and
        contract["implied_volatility"] >= filters.get("min_volatilidad_implícita", 0) and
        contract["days_to_expiration"] <= filters.get("max_días_vencimiento", 999) and
        contract["percent_diff"] >= filters.get("min_diferencia_porcentual", 0) and
        contract["bid"] >= filters.get("min_bid", 0) and
        contract["volume"] >= filters.get("min_volume", 0) and
        contract["open_interest"] >= filters.get("min_open_interest", 0) and
        contract["underlying_price"] <= filters.get("max_precio_activo", 1e6)
    )

def is_contract_alert_worthy(contract, thresholds):
    return (
        contract["rentabilidad_anual"] >= thresholds.get("rentabilidad_anual", 999) and
        contract["percent_diff"] >= thresholds.get("margen_seguridad", 999) and
        contract["bid"] >= thresholds.get("bid", 999) and
        contract["underlying_price"] <= thresholds.get("precio_activo", 0) and
        contract["volume"] >= thresholds.get("volumen", 999) and
        contract["open_interest"] >= thresholds.get("open_interest", 999)
    )

def calculate_contract_score(c):
    exp_score = max(0, (45 - c["days_to_expiration"]) / 45)
    liq_score = min((c["volume"] + c["open_interest"]) / 2000, 1)
    iv_hv_diff = max(c["implied_volatility"] - c["historical_volatility"], 0)

    score = (
        c["rentabilidad_anual"] * 0.35 +
        c["percent_diff"] * 0.25 +
        iv_hv_diff * 0.2 +
        exp_score * 0.1 +
        liq_score * 0.1
    )
    return round(score, 2)
