import yfinance as yf
import pandas as pd


class DataNotAvailableError(RuntimeError):
    pass


def fetch_price_history(symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(symbol)
    df = t.history(period=period, interval=interval, auto_adjust=False)

    if df is None or df.empty:
        raise DataNotAvailableError(
            f"Sem dados de preço para '{symbol}'. Verifique o ticker (ex.: PETR4.SA) e o período."
        )

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
        "Dividends": "dividends",
    })
    df.index = pd.to_datetime(df.index)

    if "close" not in df.columns:
        raise DataNotAvailableError(f"Dados inválidos para '{symbol}': coluna close ausente.")

    # padroniza colunas mínimas
    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]
    if "dividends" not in df.columns:
        df["dividends"] = 0.0

    df = df.dropna(subset=["close"])
    if df.empty:
        raise DataNotAvailableError(
            f"Dados vazios após limpeza para '{symbol}'. Tente outro período/intervalo."
        )

    return df
