# core/analyzer.py

import os
import pandas as pd
from core.volatility import calculate_volatility_metrics
from notifications.discord import send_discord_notification
from datetime import datetime

# Activa esto si quieres ver motivos de exclusión por consola
debug = True

def rank_top_contracts(contracts, top_n=3):
    def compute_score(c):
        iv = c.get("implied_volatility", 0)
        hv = c.get("historical_volatility", 0)
        return (
            c["rentabilidad_anual"] * 0.6 +
            c["percent_diff"] * 0.3 +
            (iv - hv) * 0.1
        )

    ranked = sorted(contracts, key=compute_score, reverse=True)
    return ranked[:top_n]

def run_group_analysis(group_id, group_data, global_results):
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

    for ticker in tickers:
        print(f"\n[INFO] Analizando {ticker} en grupo {group_id}...")
        raw_data = global_results.get(ticker, [])
        if not raw_data:
            print(f"[WARN] No se encontraron opciones para {ticker}")
            continue

        contratos_filtrados = []
        for contract in raw_data:
            valido, motivos = is_contract_valid(contract, filters)
            if valido:
                contratos_filtrados.append(contract)
            elif debug:
                print(f"[DESCARTADO] {ticker} Strike: {contract['strike']} | Motivos: {', '.join(motivos)}")

        top_contratos = rank_top_contracts(contratos_filtrados, top_n=3)
        for contract in top_contratos:
            contract["ticker"] = ticker
            all_contracts.append(contract)

            excluido_por = motivos_exclusion_alerta(contract, thresholds)
            contract["alerta_excluida_por"] = excluido_por  # nueva columna

            print("[VALIDO]", ticker, f"Strike: {contract['strike']}",
                  f"Bid: {contract['bid']}",
                  f"RA: {contract['rentabilidad_anual']:.1f}%",
                  f"Días: {contract['days_to_expiration']}",
                  f"Alerta: {'❌' if excluido_por else '✅'}")

            if not excluido_por:
                alerted_contracts.append(contract)

    if all_contracts:
        df = pd.DataFrame(all_contracts)
        df.to_csv(f"{storage_path}/{group_id}_resultados.csv", index=False)
        print(f"[INFO] {len(df)} contratos guardados en CSV")

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

    print(f"[INFO] Total válidos: {len(all_contracts)} | Total alertas: {len(alerted_contracts)}")

    if thresholds.get("notificar_discord") and alerted_contracts:
        send_discord_notification(alerted_contracts, webhook, description)

def is_contract_valid(contract, filters):
    razones = []

    if contract["rentabilidad_anual"] < filters.get("min_rentabilidad_anual", 0):
        razones.append("RA < mínimo")

    if contract["implied_volatility"] < filters.get("min_volatilidad_implícita", 0):
        razones.append("IV < mínimo")

    if contract["days_to_expiration"] > filters.get("max_días_vencimiento", 999):
        razones.append("días > máximo")

    if contract["percent_diff"] < filters.get("min_diferencia_porcentual", 0):
        razones.append("margen < mínimo")

    if contract["bid"] < filters.get("min_bid", 0):
        razones.append("bid < mínimo")

    if contract["volume"] < filters.get("min_volume", 0):
        razones.append("volumen < mínimo")

    if contract["open_interest"] < filters.get("min_open_interest", 0):
        razones.append("OI < mínimo")

    if contract["underlying_price"] > filters.get("max_precio_activo", 1e6):
        razones.append("precio subyacente > máximo")

    es_valido = len(razones) == 0
    return es_valido, razones

def motivos_exclusion_alerta(contract, thresholds):
    razones = []

    if contract["rentabilidad_anual"] < thresholds.get("rentabilidad_anual", 999):
        razones.append("RA < umbral")

    if contract["percent_diff"] < thresholds.get("margen_seguridad", 999):
        razones.append("margen < umbral")

    if contract["bid"] < thresholds.get("bid", 999):
        razones.append("bid < umbral")

    if contract["underlying_price"] > thresholds.get("precio_activo", 0):
        razones.append("precio > umbral")

    if contract["volume"] < thresholds.get("volumen", 999):
        razones.append("volumen < umbral")

    if contract["open_interest"] < thresholds.get("open_interest", 999):
        razones.append("OI < umbral")

    return ", ".join(razones)
