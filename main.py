import yaml
from core.analyzer import run_group_analysis
from core.data_loader import get_option_data_yahoo

def load_groups():
    with open("config/groups_config.yaml", "r") as f:
        return yaml.safe_load(f)

def collect_unique_tickers(groups):
    tickers_set = set()
    for group in groups.values():
        tickers_set.update(group.get("tickers", []))
    return sorted(tickers_set)

if __name__ == "__main__":
    grupos = load_groups()
    tickers_unicos = collect_unique_tickers(grupos)

    print("[INFO] Obteniendo contratos para todos los tickers...")
    config_default = {
        "max_días_vencimiento": 45  # Precarga máxima para todos los contratos
    }
    ticker_data = {
        ticker: get_option_data_yahoo(ticker, config_default) for ticker in tickers_unicos
    }

    for nombre, config in grupos.items():
        run_group_analysis(nombre, config, ticker_data)
