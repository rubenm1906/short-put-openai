# core/analyzer.py

import os
import pandas as pd
from core.data_loader import get_option_data_yahoo
from notifications.discord import send_discord_notification

def analizar_grupo(nombre_grupo, config):
    print(f"\n🚀 Ejecutando análisis para: {nombre_grupo} - {config.get('description', '')}")
    tickers = config["tickers"]
    filtros = config["filters"]
    umbrales_alerta = config.get("alert_thresholds", {})
    webhook_url = config.get("webhook", "REEMPLAZAR")

    contratos_validos = []

    for ticker in tickers:
        print(f"[INFO] Analizando {ticker}...")
        opciones = get_option_data_yahoo(ticker, filtros)
        if not opciones:
            continue

        for opcion in opciones:
            if not cumple_filtros(opcion, filtros):
                continue

            contrato = {
                "ticker": ticker,
                "strike": opcion["strike"],
                "bid": opcion["bid"],
                "días_vencimiento": opcion["days_to_expiration"],
                "rentabilidad_anual": opcion["rentabilidad_anual"],
                "margen_seguridad": opcion["percent_diff"],
                "volume": opcion["volume"],
                "open_interest": opcion["open_interest"]
            }

            print(f"[VALIDO] {ticker} Strike: {contrato['strike']} Bid: {contrato['bid']} RA: {contrato['rentabilidad_anual']:.1f}% Días: {contrato['días_vencimiento']}")
            contratos_validos.append(contrato)

    alertas = []
    for contrato in contratos_validos:
        if cumple_umbral(contrato, umbrales_alerta):
            alertas.append(contrato)
        else:
            razones = []
            if contrato["rentabilidad_anual"] < umbrales_alerta.get("rentabilidad_anual", 0):
                razones.append(f"RA {contrato['rentabilidad_anual']:.1f}% < {umbrales_alerta['rentabilidad_anual']}%")
            if contrato.get("margen_seguridad") is not None and contrato["margen_seguridad"] < umbrales_alerta.get("margen_seguridad", 0):
                razones.append(f"MS {contrato['margen_seguridad']:.1f}% < {umbrales_alerta['margen_seguridad']}%")
            if contrato["bid"] < umbrales_alerta.get("bid", 0):
                razones.append(f"Bid {contrato['bid']} < {umbrales_alerta['bid']}")
            if contrato["volume"] < umbrales_alerta.get("volumen", 0):
                razones.append(f"Vol {contrato['volume']} < {umbrales_alerta['volumen']}")
            if contrato["open_interest"] < umbrales_alerta.get("open_interest", 0):
                razones.append(f"OI {contrato['open_interest']} < {umbrales_alerta['open_interest']}")
            print(f"[DESCARTADO ALERTA] {contrato['ticker']} Strike {contrato['strike']} - {' | '.join(razones)}")

    guardar_resultados(nombre_grupo, contratos_validos, alertas)

    if umbrales_alerta.get("notificar_discord", False) and alertas:
        send_discord_notification(alertas, webhook_url, config.get("description", ""))

    print(f"[INFO] {len(contratos_validos)} contratos guardados en CSV")
    print(f"[INFO] Total válidos: {len(contratos_validos)} | Total alertas: {len(alertas)}")

def cumple_filtros(opcion, filtros):
    return (
        opcion["rentabilidad_anual"] >= filtros.get("min_rentabilidad_anual", 0) and
        opcion["implied_volatility"] >= filtros.get("min_volatilidad_implícita", 0) and
        opcion["days_to_expiration"] <= filtros.get("max_días_vencimiento", 1000) and
        opcion["percent_diff"] >= filtros.get("min_diferencia_porcentual", 0) and
        opcion["bid"] >= filtros.get("min_bid", 0) and
        opcion["volume"] >= filtros.get("min_volume", 0) and
        opcion["open_interest"] >= filtros.get("min_open_interest", 0) and
        opcion["underlying_price"] <= filtros.get("max_precio_activo", float("inf"))
    )

def cumple_umbral(contrato, umbral):
    return (
        contrato["rentabilidad_anual"] >= umbral.get("rentabilidad_anual", 0) and
        contrato.get("margen_seguridad") is not None and contrato["margen_seguridad"] >= umbral.get("margen_seguridad", 0) and
        contrato["bid"] >= umbral.get("bid", 0) and
        contrato["volume"] >= umbral.get("volumen", 0) and
        contrato["open_interest"] >= umbral.get("open_interest", 0)
    )

def guardar_resultados(nombre_grupo, contratos_validos, alertas):
    os.makedirs("storage", exist_ok=True)
    df_validos = pd.DataFrame(contratos_validos)
    df_validos.to_csv(f"storage/{nombre_grupo}_resultados.csv", index=False)

    with open(f"storage/resumen_{nombre_grupo}.txt", "w") as f:
        f.write(f"Resumen del grupo {nombre_grupo}\n")
        f.write(f"Contratos válidos: {len(contratos_validos)}\n")
        f.write(f"Contratos para alerta: {len(alertas)}\n")
        for a in alertas:
            f.write(f"- {a['ticker']} Strike: {a['strike']} RA: {a['rentabilidad_anual']:.1f}% Bid: {a['bid']}\n")

