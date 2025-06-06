# notifications/discord.py

import requests

def send_discord_notification(contratos, webhook_url, group_description):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    if not contratos:
        print("[INFO] No hay contratos destacados para notificar.")
        return

    lines = [f"**Oportunidades detectadas - {group_description}**\n"]
    for c in contratos:
        contract_line = (
            f"🟢 `{c['ticker']}` | Strike: {c['strike']} | Bid: ${c['bid']:.2f} | "
            f"RA: {c['rentabilidad_anual']:.1f}% | Días: {c['days_to_expiration']} | "
            f"IV: {c['implied_volatility']:.1f}% | HV: {c.get('historical_volatility', 0):.1f}%"
        )
        print("[ALERTA DETECTADA]", contract_line)
        lines.append(contract_line)

    mensaje = "\n".join(lines)
    payload = {"content": mensaje}

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"[INFO] Alerta enviada a Discord ({group_description}) con {len(contratos)} contrato(s).")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar a Discord: {e}")
