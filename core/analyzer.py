# core/analyzer.py

import os
import pandas as pd
from core.volatility import calculate_volatility_metrics
from notifications.discord import send_discord_notification
from datetime import datetime

debug = True  # activa trazabilidad por consola

def ra_dinamico_minimo(dias):
    if dias <= 2:
        return 70
    elif dias <= 5:
        return 55
    elif dias <= 10:
        return 45
    else:
        return 35

def rank_top_contracts(contracts, top_n=3):
    def compute_score(c):
        iv = c.get("implied_volatility", 0)
        hv = c.get("historical_volatility", 0)
        spread_bonus = 5 if (iv - hv) > 10 else 0

        return (
            c["rentabilidad_anual"] * 0.6 +
            c["percent_diff"] * 0.3 +
            (iv - hv) * 0.1 +
            spread_bonus
        )

    return sorted(contracts, key=compute_score, reverse=True)[:top_n]

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
            contract["alerta_excluida_por"] = excluido_por

            print("[VALIDO]", ticker, f"Strike: {contract['strike']}",
                  f"Bid: {contract['bid']}",
                  f"RA: {contract['rentabilidad_anual']:.1f}%",
                  f"Días: {contract['days_to_expiration']}",
                  f"Alerta: {'✅' if not excluido_por else '❌'}")

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

    # RA dinámica por días restantes
    if "min_rentabilidad_anual" in filters:
        ra_min = ra_dinamico_minimo(contract["days_to_expiration"])
        if contract["rentabilidad_anual"] < ra_min:
            razones.append(f"RA < mínimo dinámico ({ra_min}%)")

    if "min_volatilidad_implícita" in filters and contract["implied_volatility"] < filters["min_volatilidad_implícita"]:
        razones.append("IV < mínimo")

    if "max_días_vencimiento" in filters and contract["days_to_expiration"] > filters["max_días_vencimiento"]:
        razones.append("días > máximo")

    if "min_diferencia_porcentual" in filters and contract["percent_diff"] < filters["min_diferencia_porcentual"]:
        razones.append("margen < mínimo")

    if "min_bid" in filters and contract["bid"] < filters["min_bid"]:
        razones.append("bid < mínimo")

    if "min_volume" in filters and contract["volume"] < filters["min_volume"]:
        razones.append("volumen < mínimo")

    if "min_open_interest" in filters and contract["open_interest"] < filters["min_open_interest"]:
        razones.append("OI < mínimo")

    if "precio_activo" in filters and filters["precio_activo"] is not None:
        if contract["underlying_price"] > filters["precio_activo"]:
            razones.append("precio subyacente > máximo")

    return len(razones) == 0, razones

def motivos_exclusion_alerta(contract, thresholds):
    razones = []

    if "rentabilidad_anual" in thresholds and contract["rentabilidad_anual"] < thresholds["rentabilidad_anual"]:
        razones.append("RA < umbral")

    if "margen_seguridad" in thresholds and contract["percent_diff"] < thresholds["margen_seguridad"]:
        razones.append("margen < umbral")

    if "bid" in thresholds and contract["bid"] < thresholds["bid"]:
        razones.append("bid < umbral")

    if "precio_activo" in thresholds and thresholds["precio_activo"] is not None:
        if contract["underlying_price"] > thresholds["precio_activo"]:
            razones.append("precio > umbral")

    if "volumen" in thresholds and contract["volume"] < thresholds["volumen"]:
        razones.append("volumen < umbral")

    if "open_interest" in thresholds and contract["open_interest"] < thresholds["open_interest"]:
        razones.append("OI < umbral")

    return ", ".join(razones)
