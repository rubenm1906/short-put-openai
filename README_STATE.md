storage/resumen_<grupo>.txt: resumen de análisis, incluyendo cuántos contratos válidos y alertas hubo.

[VALIDO] y [ALERTA DETECTADA] se imprimen en los logs para trazabilidad.

⏱️ Automatización
GitHub Actions ejecuta el script automáticamente a las:

15:30 CET (13:30 UTC)

18:00 CET (16:00 UTC)

21:00 CET (19:00 UTC)

También se puede ejecutar manualmente desde la pestaña Actions en GitHub.

📂 Estructura actual
bash
Copy
Edit
.
├── core/
│   ├── analyzer.py         # Lógica de análisis por grupo
│   ├── data_loader.py      # Carga de contratos vía yfinance
│   ├── volatility.py       # Cálculo IV/HV
├── notifications/
│   └── discord.py          # Envío a Discord (si hay alertas)
├── config/
│   └── groups_config.yaml  # Configuración de grupos y filtros
├── storage/                # Resultados exportados
├── main.py                 # Punto de entrada
└── .github/workflows/run-daily.yml
⚠️ Pendientes o próximos pasos sugeridos
Ajuste dinámico de fechas de vencimiento (vencimientos semanales).

Score para priorizar contratos (RA ponderada, IV-HV spread, delta).

Interface de configuración simple para nuevos usuarios/grupos.

Alerta visual (embed en Discord) o exportación a Google Sheets.
