# main.py (con caché por ticker)

import yaml
from core.analyzer import run_group_analysis_with_cache

def load_groups():
    with open("config/groups_config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    grupos = load_groups()
    ticker_cache = {}  # Almacena data de cada ticker ya analizado
    for nombre, config in grupos.items():
        run_group_analysis_with_cache(nombre, config, ticker_cache)
