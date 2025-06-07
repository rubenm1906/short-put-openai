import yfinance as yf
from datetime import datetime
from core.volatility import calculate_volatility_metrics

def get_option_data_yahoo(ticker, config):
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        current_price = stock.info.get("regularMarketPrice", stock.info.get("previousClose", 0))

        if not expirations or current_price <= 0:
            return []

        hv = calculate_volatility_metrics(ticker)

        all_contracts = []

        for expiration in expirations:
            exp_date = datetime.strptime(expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days

            if days_to_exp <= 0 or days_to_exp > config.get("max_días_vencimiento", 45):
                continue

            options_chain = stock.option_chain(expiration)
            for _, row in options_chain.puts.iterrows():
                strike = row["strike"]
                bid = row.get("bid", 0)
                iv = row.get("impliedVolatility", 0) * 100
                last_price = row.get("lastPrice", 0)
                volume = row.get("volume", 0) or 0
                oi = row.get("openInterest", 0) or 0

                if strike >= current_price:
                    continue  # solo OTM

                break_even = strike - last_price
                percent_diff = ((current_price - break_even) / current_price) * 100
                rentabilidad_diaria = (last_price * 100) / current_price
                rentabilidad_anual = ((1 + rentabilidad_diaria / 100) ** (365 / days_to_exp) - 1) * 100

                contract = {
                    "strike": strike,
                    "bid": bid,
                    "implied_volatility": iv,
                    "last_price": last_price,
                    "volume": volume,
                    "open_interest": oi,
                    "expiration": expiration,
                    "days_to_expiration": days_to_exp,
                    "rentabilidad_diaria": rentabilidad_diaria,
                    "rentabilidad_anual": rentabilidad_anual,
                    "break_even": break_even,
                    "percent_diff": percent_diff,
                    "underlying_price": current_price,
                    "historical_volatility": hv
                }
                all_contracts.append(contract)

        return all_contracts

    except Exception as e:
        print(f"[ERROR] Error procesando {ticker}: {e}")
        return []
