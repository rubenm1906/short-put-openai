import requests

def send_discord_notification(contratos, webhook_url, group_description):
    if not webhook_url or webhook_url == "REEMPLAZAR":
        print("[ERROR] Webhook no configurado correctamente.")
        return

    encabezado_base = f"📢 Oportunidades detectadas en: *{group_description}*"
    lineas = []

    for c in contratos:
        linea = (
            f"🟢 {c['ticker']} | Strike: {c['strike']} | Bid: ${c['bid']:.2f} | "
            f"RA: {c['rentabilidad_anual']:.1f}% | Días: {c['days_to_expiration']} | "
            f"Precio: ${c['underlying_price']:.2f} | BE: ${c['break_even']:.2f} | "
            f"Margen: {c['percent_diff']:.1f}% | IV: {c['implied_volatility']:.1f}% | "
            f"HV: {c.get('historical_volatility', 0):.1f}%"
        )
        lineas.append(linea)

    # Fragmentar en mensajes de ≤2000 caracteres incluyendo encabezado
    mensajes = []
    actual = encabezado_base + "\n"
    for linea in lineas:
        if len(actual) + len(linea) + 1 > 2000:
            mensajes.append(actual.strip())
            actual = encabezado_base + "\n" + linea + "\n"
        else:
            actual += linea + "\n"
    if actual:
        mensajes.append(actual.strip())

    # Enviar mensajes numerados
    total = len(mensajes)
    for i, m in enumerate(mensajes, start=1):
        encabezado = f"📢 Oportunidades detectadas en: *{group_description} ({i}/{total})*"
        contenido = m.replace(encabezado_base, encabezado, 1)
        response = requests.post(webhook_url, json={"content": contenido})
        if response.status_code not in [200, 204]:
            print(f"[ERROR] Fallo al enviar a Discord: {response.status_code} - {response.text}")
