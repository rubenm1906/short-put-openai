# Short Put Screener (short-put-openai)

Este proyecto permite analizar oportunidades para vender opciones PUT (short puts) de forma sistemática, filtrando oportunidades rentables y con riesgo controlado. Soporta múltiples grupos, configuración por YAML y notificaciones a Discord.

---

## 🚀 Características

- Análisis automático de puts OTM
- Rentabilidad anual compuesta
- Filtros configurables por grupo
- Margen de seguridad, IV, HV (volatilidad histórica) y volumen
- Notificación a Discord solo si se cumplen condiciones estrictas
- Multiusuario/multigrupo por configuración YAML

---

## 📦 Requisitos

- Python 3.9+
- `yfinance`, `numpy`, `pandas`, `requests`, `tabulate`, `pyyaml`

Instalar dependencias:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Estructura del proyecto

```
short-put-openai/
├── core/                  # Lógica principal
│   ├── analyzer.py
│   ├── data_loader.py
│   └── volatility.py
├── config/                # Configuraciones de grupos
│   └── groups_config.yaml
├── notifications/         # Notificación a Discord
│   └── discord.py
├── storage/               # Resultados exportados
├── main.py                # Punto de entrada principal
├── requirements.txt       # Librerías necesarias
├── .gitignore             # Exclusiones Git
└── README.md              # Este archivo
```

---

## 🧪 Ejecución

```bash
python main.py
```

---

## 📋 Ejemplo de configuración (`config/groups_config.yaml`)

```yaml
shortlist_ruben:
  description: "Mi short list personal"
  webhook: "https://discord.com/api/webhooks/xxxxx"
  tickers: ["AAPL", "AMZN", "ASML", "EPAM"]
  filters:
    min_rentabilidad_anual: 45
    min_volatilidad_implícita: 35
    max_días_vencimiento: 45
    min_diferencia_porcentual: 5
    min_bid: 1.00
    min_volume: 100
    min_open_interest: 500
    max_precio_activo: 150
  alert_thresholds:
    rentabilidad_anual: 50
    margen_seguridad: 8
    bid: 1.00
    precio_activo: 150
    volumen: 100
    open_interest: 500
    notificar_discord: true
```

---

## 📤 Resultados
- `mejores_contratos.csv`: contratos destacados
- `resultados.txt`: resumen del análisis
- `Mejores_Contratos.txt`: contratos notificados
- Cada contrato incluye ahora la **volatilidad histórica (HV)** además de la IV

---

## 📈 Uso de Volatilidad Histórica (HV)

Cada contrato analizado ahora contiene un campo `historical_volatility`. Esto permite:

- Comparar IV vs HV
- Filtrar opciones donde **IV sea significativamente mayor que HV** (buena señal para vender puts)

Ejemplo de integración futura:
```python
if contract["implied_volatility"] > contract["historical_volatility"] + 10:
    # buena oportunidad
```

---

## 🧠 Autor
Rubén Marín

---

## 📝 Licencia
MIT (o personalizable)
