# core/analyzer.py

import os
import pandas as pd
from core.data_loader import get_option_data_yahoo
from core.volatility import calculate_volatility_metrics
from notifications.discord import send_discord_notification


def run_group_analysis(group_id, group_data):
    description = group_data.get("description", group_id)
    webhook = group_data.get("webhook")
    tickers = group_data.get("tickers", [])
    filters = group_data.get("filters", {})
    thresholds = group_data.get("alert_thresholds", {})

    all_contracts = []
    notified_tickers = []

    for ticker in tickers:
        print(f"\n[INFO] Analizando {ticker}...")
        option_data = get_option_data_yahoo(ticker, filters)
        if not option_data:
            print(f"[WARN] No se encontraron opciones para {ticker}")
            continue

        for contract in option_data:
            if not is_contract_valid(contract, filters):
                continue
            contract["ticker"] = ticker
            all_contracts.append(contract)

            if is_contract_alert_worthy(contract, thresholds):
                notified_tickers.append(ticker)

    if all_contracts:
        df = pd.DataFrame(all_contracts)
        os.makedirs("storage", exist_ok=True)
        df.to_csv(f"storage/{group_id}_resultados.csv", index=False)
        print(f"[INFO] {len(df)} contratos guardados en CSV")

    if thresholds.get("notificar_discord") and notified_tickers:
        send_discord_notification(notified_tickers, webhook, description)



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

