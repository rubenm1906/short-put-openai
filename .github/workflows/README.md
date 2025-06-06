📘 Guía rápida: ejecutar manualmente el screener desde GitHub
Puedes ejecutar el screener en cualquier momento usando GitHub Actions con estos pasos:

▶️ Cómo lanzar manualmente el workflow
Ve a tu repositorio en GitHub

Haz clic en la pestaña "Actions"

Selecciona el workflow "Run Short Put Screener Daily and On Demand"

Presiona el botón "Run workflow" (arriba a la derecha)

¡Listo! GitHub ejecutará main.py con tu configuración actual.

🕒 Horarios automáticos configurados
El script también se ejecuta automáticamente cada día a:

15:30 CET

18:00 CET

21:00 CET

📝 Resultado
Los resultados se guardan en la carpeta storage/ y se suben automáticamente al repositorio si hay cambios.
