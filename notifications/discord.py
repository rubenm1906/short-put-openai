# notifications/discord.py

import requests
from collections import defaultdict

def send_discord_notification(contratos, webhook_url, group_description, top_n_per_ticker=3, max_chars=1800):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    # Agrupar y filtrar top por ticker
    por_ticker = defaultdict(list)
    for c in contratos:
        por_ticker[c["ticker"]].append(c)

    top_contratos = []
    for ticker, lista in por_ticker.items():
        ordenados = sorted(lista, key=lambda x: x.get("score", 0), reverse=True)
        top_contratos.extend(ordenados[:top_n_per_ticker])

    # Ordenar globalmente
    top_final = sorted(top_contratos, key=lambda x: x.get("score", 0), reverse=True)

    # Enviar por bloques
    mensaje = f"**📢 Oportunidades detectadas en:** *{group_description}*\n"
    for c in top_final:
        fila = (
            f"🟢 {c['ticker']} | "
            f"Strike: {c['strike']} | "
            f"Bid: ${c['bid']:.2f} | "
            f"RA: {c['rentabilidad_anual']:.1f}% | "
            f"Días: {c['days_to_expiration']} | "
            f"IV: {c['implied_volatility']:.1f}% | "
            f"HV: {c.get('historical_volatility', 0):.1f}% | "
            f"Score: {c.get('score', 0):.1f}\n"
        )

        if len(mensaje) + len(fila) > max_chars:
            requests.post(webhook_url, json={"content": mensaje})
            mensaje = ""

        mensaje += fila

    if mensaje:
        requests.post(webhook_url, json={"content": mensaje})
