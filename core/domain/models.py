from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, Optional

class AssetId(BaseModel):
    symbol: str = Field(..., description="Ticker, ex: AAPL, PETR4.SA")
    market: Literal["BR", "US", "OTHER"] = "OTHER"

class QuantReport(BaseModel):
    cagr: float
    vol_annual: float
    sharpe: float
    max_drawdown: float
    explain: Dict[str, Any]

class TechnicalReport(BaseModel):
    trend_regime: str
    rsi14: float
    explain: Dict[str, Any]

class AssetAnalysis(BaseModel):
    asset: AssetId
    quant: QuantReport
    technical: TechnicalReport
    asof: str
    metadata: Dict[str, Any] = {}
