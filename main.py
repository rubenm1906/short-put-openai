# main.py

import yaml
from core.analyzer import analizar_grupo

def load_groups():
    with open("config/groups_config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    grupos = load_groups()
    for nombre, config in grupos.items():
        analizar_grupo(nombre, config)
