# notifications/discord.py

import requests

def send_discord_notification(tickers, webhook_url, group_description):
    if not webhook_url or webhook_url == "https://discord.com/api/webhooks/1380659273494691840/O0n-99abTfYqaK31q0fXxBz0--JEN2LkUlzltBFyiHgZ2RM4fIUjochlHkbVMALeOZpG":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    tickers_str = ", ".join(tickers)
    mensaje = (
        f"**Oportunidades detectadas - {group_description}**\n"
        f"Se identificaron contratos destacados para los siguientes tickers:\n"
        f"{tickers_str}"
    )

    payload = {"content": mensaje}

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"[INFO] Alerta enviada a Discord ({group_description})")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar a Discord: {e}")

