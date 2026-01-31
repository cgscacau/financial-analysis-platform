import numpy as np
import pandas as pd


def daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()


def cagr(close: pd.Series, trading_days: int = 252) -> float:
    rets = daily_returns(close)
    if rets.empty:
        return float("nan")
    total = (1 + rets).prod()
    years = len(rets) / trading_days
    return float(total ** (1 / years) - 1)


def vol_annual(rets: pd.Series, trading_days: int = 252) -> float:
    return float(rets.std() * np.sqrt(trading_days))


def sharpe(rets: pd.Series, rf_annual: float = 0.0, trading_days: int = 252) -> float:
    rf_daily = (1 + rf_annual) ** (1 / trading_days) - 1
    ex = rets - rf_daily
    denom = ex.std()
    if denom == 0 or np.isnan(denom):
        return float("nan")
    return float((ex.mean() / denom) * np.sqrt(trading_days))


def max_drawdown(close: pd.Series) -> float:
    peak = close.cummax()
    dd = close / peak - 1.0
    return float(dd.min())
