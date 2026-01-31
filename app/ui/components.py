import streamlit as st


def kpi_row(kpis: dict):
    cols = st.columns(len(kpis))
    for col, (k, v) in zip(cols, kpis.items()):
        if isinstance(v, float):
            if "drawdown" in k.lower() or "cagr" in k.lower() or "vol" in k.lower():
                col.metric(k, f"{v:.2%}")
            else:
                col.metric(k, f"{v:.2f}")
        else:
            col.metric(k, str(v))
