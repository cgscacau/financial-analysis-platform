from datetime import datetime, timezone
from core.domain.models import AssetId, AssetAnalysis, QuantReport, TechnicalReport
from core.data.providers.yfinance_provider import fetch_price_history
from core.engines.quantitative.performance import daily_returns, cagr, vol_annual, sharpe, max_drawdown
from core.engines.technical.scoring import technical_report


def analyze_asset(symbol: str, rf_annual: float = 0.0, period: str = "5y") -> AssetAnalysis:
    df = fetch_price_history(symbol, period=period)
    close = df["close"]
    rets = daily_returns(close)

    q = QuantReport(
        cagr=cagr(close),
        vol_annual=vol_annual(rets),
        sharpe=sharpe(rets, rf_annual=rf_annual),
        max_drawdown=max_drawdown(close),
        explain={
            "cagr": "Produto dos retornos diários, anualizado (252 pregões).",
            "vol_annual": "Desvio padrão dos retornos diários anualizado.",
            "sharpe": "(E[R]-Rf)/sigma anualizado.",
            "max_drawdown": "Pior queda pico→vale no período.",
        },
    )

    t = technical_report(df)
    tr = TechnicalReport(**t)

    market = "BR" if symbol.endswith(".SA") else "US" if symbol.isalpha() else "OTHER"

    return AssetAnalysis(
        asset=AssetId(symbol=symbol, market=market),
        quant=q,
        technical=tr,
        asof=datetime.now(timezone.utc).isoformat(),
        metadata={"period": period, "rows": int(len(df))},
    )
