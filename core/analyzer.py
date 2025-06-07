# analyzer_score_before_filter.py

import os
import copy
import pandas as pd
from core.data_loader import get_option_data_yahoo
from core.volatility import calculate_volatility_metrics
from notifications.discord import send_discord_notification
from datetime import datetime

def run_group_analysis_with_cache(group_id, group_data, ticker_cache):
    description = group_data.get("description", group_id)
    webhook = group_data.get("webhook")
    tickers = group_data.get("tickers", [])
    filters = group_data.get("filters", {})
    thresholds = group_data.get("alert_thresholds", {})

    all_contracts = []
    scored_contracts = []

    storage_path = "storage"
    if os.path.exists(storage_path) and not os.path.isdir(storage_path):
        os.remove(storage_path)
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    print(f"[INFO] Iniciando análisis del grupo: {group_id}")
    for ticker in tickers:
        if ticker in ticker_cache:
            print(f"[CACHE] Usando datos cacheados para {ticker}")
            option_data_raw = ticker_cache[ticker]
        else:
            print(f"[INFO] Descargando opciones para {ticker}...")
            option_data_raw = get_option_data_yahoo(ticker, filters)
            ticker_cache[ticker] = option_data_raw

        option_data = [copy.deepcopy(c) for c in option_data_raw]

        if not option_data:
            print(f"[WARN] No se encontraron opciones para {ticker}")
            continue

        for contract in option_data:
            contract["ticker"] = ticker

            if is_contract_valid(contract, filters):
                contract["score"] = calculate_contract_score(contract)
                all_contracts.append(contract)

    if all_contracts:
        df = pd.DataFrame(all_contracts)
        csv_path = f"{storage_path}/{group_id}_resultados.csv"
        df.to_csv(csv_path, index=False)
        print(f"[INFO] {len(df)} contratos guardados en CSV")

    # Aplicar alerta solo a los contratos ya puntuados
    alerted_contracts = [
        c for c in all_contracts if is_contract_alert_worthy(c, thresholds)
    ]

    print(f"[INFO] Total válidos: {len(all_contracts)} | Total alertas: {len(alerted_contracts)}")

    if thresholds.get("notificar_discord") and alerted_contracts:
        notificados = send_discord_notification(alerted_contracts, webhook, description)
        if notificados:
            df_alerts = pd.DataFrame(notificados)
            df_alerts.to_csv(f"{storage_path}/alertados_{group_id}.csv", index=False)
            print(f"[INFO] {len(df_alerts)} alertas guardadas en alertados_{group_id}.csv")

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
