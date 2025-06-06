# main.py

from core.analyzer import run_group_analysis
import yaml
import os

CONFIG_PATH = "config/groups_config.yaml"

def load_groups():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    grupos = load_groups()
    for group_id, group_data in grupos.items():
        print(f"\n🚀 Ejecutando análisis para: {group_id} - {group_data.get('description', '')}")
        run_group_analysis(group_id, group_data)
    print("\n✅ Proceso finalizado.")

