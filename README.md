# 📉 Short Put Screener – Proyecto Modular y Escalable

Este proyecto automatiza el análisis de **opciones PUT OTM (Out of the Money)** para detectar oportunidades con **alta rentabilidad anual, buena prima y margen de seguridad**. El objetivo es construir una solución **modular, escalable y personalizable**, con notificaciones inteligentes y configuración flexible.

---

## 🎯 Objetivo

Detectar y alertar contratos PUT que cumplan condiciones específicas en cuanto a:

- Rentabilidad esperada
- Volatilidad implícita vs histórica
- Seguridad (distancia al strike)
- Liquidez (volumen e interés abierto)
- Requisitos de prima y precio del subyacente

La lógica puede aplicarse sobre cualquier conjunto de tickers, sea de Nasdaq, S&P500 u otros.

---

## 🧱 Estructura del proyecto

```
short-put-screener/
├── core/
│   ├── analyzer.py          # Evaluación de contratos y lógica por grupo
│   ├── data_loader.py       # Carga de opciones desde Yahoo Finance
│   └── volatility.py        # Cálculo de volatilidad histórica (HV)
├── notifications/
│   └── discord.py           # Fragmentación y envío a Discord
├── config/
│   └── groups_config.yaml   # Configuración de múltiples grupos (tickers, filtros, umbrales, webhook)
├── storage/                 # Resultados CSV y TXT generados por grupo
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias de Python
├── .github/workflows/
│   └── run-daily.yml        # Workflow de GitHub Actions para ejecución automática
└── README.md               # Este archivo
```

---

## 👥 Soporte para múltiples grupos

Cada grupo en `groups_config.yaml` puede tener:

- Su propia lista de tickers
- Filtros personalizados (`filters`)
- Umbrales de alerta (`alert_thresholds`)
- Webhook de Discord propio

Esto permite crear grupos como:

- `shortlist_ruben`
- `7_Magnificas`
- `Indices`
- `Fundamentales_SP500`

---

## 🧮 Métricas calculadas por contrato

- **Rentabilidad anual compuesta (RA)**
- **Volatilidad implícita (IV)**
- **Volatilidad histórica (HV, 30 días)**
- **Break-even** y **margen de seguridad (%)**
- **Validez por filtros y alertabilidad por umbrales**

---

## 🧠 Ranking de contratos

Por cada ticker, se seleccionan los **3 mejores contratos**, ordenados por:

```
score = RA * 0.6 + margen_seguridad * 0.3 + (IV - HV) * 0.1
```

Solo contratos válidos entran al ranking. Solo los que además cumplen `alert_thresholds` son notificados.

---

## 🔔 Notificaciones a Discord

- Se notifica solo si `notificar_discord: true` y hay contratos que cumplen los umbrales
- Los mensajes se dividen automáticamente en bloques de hasta 2000 caracteres
- Cada contrato aparece en una sola línea, así:

```
🟢 PLTR | Strike: 120 | Bid: $1.50 | RA: 42.1% | Días: 6 | Precio: $124.2 | BE: $118.5 | Margen: 4.6% | IV: 50.3% | HV: 34.2%
```

---

## ⚙️ Ejemplo de configuración YAML

```yaml
shortlist_ruben:
  description: "Mi lista personal"
  webhook: "https://discord.com/api/webhooks/..."
  tickers: ["PLTR", "EPAM", "NFE"]
  filters:
    min_rentabilidad_anual: 40
    min_volatilidad_implícita: 35
    max_días_vencimiento: 30
    min_diferencia_porcentual: 2.0
    min_bid: 1.00
    min_volume: 100
    min_open_interest: 500
    precio_activo: null
  alert_thresholds:
    rentabilidad_anual: 45
    margen_seguridad: 3
    bid: 1.00
    precio_activo: null
    volumen: 150
    open_interest: 500
    notificar_discord: true
```

---

## ▶️ Ejecución

### Manual

```bash
python main.py
```

### Automática (GitHub Actions)

- El workflow se ejecuta a las **15:30**, **18:00** y **21:00 CET**
- Configura `PAT_TOKEN` como secret para habilitar `git push` al repositorio

---

## 🧪 Resultados generados

- `storage/<grupo>_resultados.csv`: todos los contratos válidos
- `storage/resumen_<grupo>.txt`: resumen de ejecución
- Columna extra en CSV: `alerta_excluida_por` (motivos por los que no se notificó)

---

## 🧭 Roadmap futuro

- [ ] Dashboard interactivo (Flask/Streamlit)
- [ ] Soporte para opciones CALL
- [ ] Conexión a APIs (IBKR, Finnhub, Tradier)
- [ ] Modo backtest / simulación histórica
- [ ] Exportación a Google Sheets
- [ ] Interfaz web para crear grupos

---

## 📝 Licencia

MIT – Uso libre para propósitos educativos y personales. Adaptable para uso comercial con autorización del autor.

---

## 🧠 Autor

**Rubén Marín**  
Proyecto personal de automatización de screening de opciones con base en fundamentos.
