import requests

def send_discord_notification(contratos, webhook_url, group_description):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    mensaje = f"📢 *Oportunidades detectadas en:* **{group_description}**\n"
    for c in contratos:
        mensaje += f"- {c['ticker']} Strike: {c['strike']} | Bid: {c['bid']} | RA: {c['rentabilidad_anual']:.1f}%\n"

    data = {"content": mensaje}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"[ERROR] Fallo al enviar a Discord: {response.status_code} - {response.text}")
