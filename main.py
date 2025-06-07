import yaml
from core.analyzer import run_group_analysis

def load_groups():
    with open("config/groups_config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    grupos = load_groups()
    for nombre, config in grupos.items():
        run_group_analysis(nombre, config)

