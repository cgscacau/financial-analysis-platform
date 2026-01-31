import pandas as pd
from core.engines.technical.indicators import sma, rsi


def technical_report(df: pd.DataFrame) -> dict:
    if df is None or df.empty or "close" not in df.columns:
        return {
            "trend_regime": "unknown",
            "rsi14": float("nan"),
            "explain": {
                "error": "Sem dados suficientes para análise técnica.",
            },
        }

    close = df["close"].dropna()
    if close.empty:
        return {
            "trend_regime": "unknown",
            "rsi14": float("nan"),
            "explain": {
                "error": "Série de fechamento vazia após remoção de NaNs.",
            },
        }

    sma50 = sma(close, 50)
    sma200 = sma(close, 200)

    last_close = float(close.iloc[-1])
    last_sma50 = float(sma50.iloc[-1]) if sma50.notna().iloc[-1] else float("nan")
    last_sma200 = float(sma200.iloc[-1]) if sma200.notna().iloc[-1] else float("nan")
    last_rsi = float(rsi(close, 14).iloc[-1])

    regime = "unknown"
    if pd.notna(last_sma200):
        regime = "bull" if last_close > last_sma200 else "bear"

    return {
        "trend_regime": regime,
        "rsi14": last_rsi,
        "explain": {
            "trend_regime": "bull se close > SMA200, bear caso contrário.",
            "rsi14": "RSI(14) clássico (0-100).",
            "last_close": last_close,
            "last_sma50": last_sma50,
            "last_sma200": last_sma200,
            "notes": "Se SMA200 for NaN (poucos dados), regime fica 'unknown'.",
        },
    }
