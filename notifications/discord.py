import requests

def send_discord_notification(contratos, webhook_url, group_description):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    mensaje = f"**📢 Oportunidades detectadas en:** *{group_description}*\n"

    for c in contratos:
        mensaje += (
            f"🟢 {c['ticker']} | "
            f"Strike: {c['strike']} | "
            f"Bid: ${c['bid']:.2f} | "
            f"RA: {c['rentabilidad_anual']:.1f}% | "
            f"Días: {c['days_to_expiration']} | "
            f"IV: {c['implied_volatility']:.1f}% | "
            f"HV: {c.get('historical_volatility', 0):.1f}%\n"
        )

    response = requests.post(webhook_url, json={"content": mensaje})
    if response.status_code != 204:
        print(f"[ERROR] Fallo al enviar a Discord: {response.status_code} - {response.text}")
