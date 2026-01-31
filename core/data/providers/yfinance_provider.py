import yfinance as yf
import pandas as pd


def fetch_price_history(symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(symbol)
    df = t.history(period=period, interval=interval, auto_adjust=False)
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
        "Dividends": "dividends",
    })
    df.index = pd.to_datetime(df.index)
    # padroniza colunas mínimas
    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]
    if "dividends" not in df.columns:
        df["dividends"] = 0.0
    return df.dropna(subset=["close"])
