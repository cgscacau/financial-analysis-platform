import os
import streamlit as st
from core.data.providers.yfinance_provider import normalize_symbol


DEFAULT_PERIOD = "5y"


def get_default_rf() -> float:
    try:
        return float(os.getenv("DEFAULT_RF_ANNUAL", "0.0"))
    except Exception:
        return 0.0


def ensure_global_state():
    if "global_symbol" not in st.session_state:
        st.session_state["global_symbol"] = "AAPL"
    if "global_period" not in st.session_state:
        st.session_state["global_period"] = DEFAULT_PERIOD
    if "global_rf" not in st.session_state:
        st.session_state["global_rf"] = get_default_rf()


def get_global_inputs():
    ensure_global_state()
    return (
        st.session_state["global_symbol"],
        st.session_state["global_period"],
        float(st.session_state["global_rf"]),
    )


def set_global_inputs(symbol: str, period: str, rf: float):
    ensure_global_state()
    symbol = normalize_symbol((symbol or "").strip())
    st.session_state["global_symbol"] = symbol or "AAPL"
    st.session_state["global_period"] = period or DEFAULT_PERIOD
    st.session_state["global_rf"] = float(rf if rf is not None else get_default_rf())
