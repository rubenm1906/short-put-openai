# notifications/discord.py

import requests
from collections import defaultdict

def send_discord_notification(contratos, webhook_url, group_description, top_n_per_ticker=3, max_chars=1800):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    # Agrupar por ticker y ordenar top-N por score
    por_ticker = defaultdict(list)
    for c in contratos:
        por_ticker[c["ticker"]].append(c)

    mensajes = []
    mensaje_actual = f"**📢 Oportunidades detectadas en:** *{group_description}*\n"

    for ticker in sorted(por_ticker.keys()):
        contratos_ticker = sorted(por_ticker[ticker], key=lambda x: x.get("score", 0), reverse=True)[:top_n_per_ticker]
        bloque = ""
        for c in contratos_ticker:
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
            bloque += fila

        if len(mensaje_actual) + len(bloque) > max_chars:
            mensajes.append(mensaje_actual)
            mensaje_actual = f"**📢 Oportunidades detectadas en:** *{group_description}*\n"

        mensaje_actual += bloque

    if mensaje_actual:
        mensajes.append(mensaje_actual)

    # Enviar todos los bloques
    for msg in mensajes:
        response = requests.post(webhook_url, json={"content": msg})
        if response.status_code != 204:
            print(f"[ERROR] Fallo al enviar a Discord: {response.status_code} - {response.text}")
