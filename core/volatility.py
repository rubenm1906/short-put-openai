import yfinance as yf
import numpy as np
import pandas as pd

def calculate_volatility_metrics(ticker, days=30):
    try:
        data = yf.download(ticker, period=f"{days + 10}d", interval="1d")
        if data.empty or "Close" not in data:
            return None

        data = data[-days:]
        data["log_return"] = np.log(data["Close"] / data["Close"].shift(1))
        data.dropna(inplace=True)

        std_daily = data["log_return"].std()
        hv_annual = std_daily * np.sqrt(252) * 100

        return round(hv_annual, 2)
    except Exception as e:
        print(f"[ERROR] Fallo al calcular HV para {ticker}: {e}")
        return None
