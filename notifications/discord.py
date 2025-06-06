# notifications/discord.py

import requests

def send_discord_notification(contratos, webhook_url, group_description):
    if not webhook_url or webhook_url == "https://discord.com/api/webhooks/1380659273494691840/O0n-99abTfYqaK31q0fXxBz0--JEN2LkUlzltBFyiHgZ2RM4fIUjochlHkbVMALeOZpG":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    if not contratos:
        print("[INFO] No hay contratos destacados para notificar.")
        return

    lines = [f"**Oportunidades detectadas - {group_description}**\n"]
    for c in contratos:
        lines.append(
            f"🟢 `{c['ticker']}` | Strike: {c['strike']} | Bid: ${c['bid']:.2f} | "
            f"RA: {c['rentabilidad_anual']:.1f}% | Días: {c['days_to_expiration']} | "
            f"IV: {c['implied_volatility']:.1f}% | HV: {c.get('historical_volatility', 0):.1f}%"
        )

    mensaje = "\n".join(lines)
    payload = {"content": mensaje}

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"[INFO] Alerta enviada a Discord ({group_description})")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar a Discord: {e}")


