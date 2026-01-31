import streamlit as st
import sys
from pathlib import Path
# Ensure project root is on PYTHONPATH (Streamlit Cloud compatibility)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from infra.firebase.auth import sign_in_email_password, sign_up_email_password
from infra.firebase.repositories.user_repo import upsert_user, save_analysis

from core.use_cases.analyze_asset import analyze_asset
from core.data.providers.yfinance_provider import fetch_price_history
from core.engines.technical.indicators import sma, rsi

from app.ui.components import kpi_row
from app.ui.charts import price_with_sma, rsi_chart

st.set_page_config(page_title="Financial Analytics Platform", layout="wide")

# ------------------ Auth UI ------------------

def ensure_auth():
    if "user" not in st.session_state:
        st.session_state.user = None

    with st.sidebar:
        st.header("Login")
        mode = st.radio("Modo", ["Entrar", "Criar conta"], horizontal=True, label_visibility="collapsed")
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")

        if mode == "Entrar":
            if st.button("Entrar"):
                try:
                    user = sign_in_email_password(email, password)
                    st.session_state.user = user
                    upsert_user(uid=user["localId"], email=email)
                    st.success("Autenticado.")
                except Exception as e:
                    st.error("Falha no login. Verifique credenciais e se Auth Email/Senha está habilitado.")
                    st.caption(str(e))
        else:
            if st.button("Criar conta"):
                try:
                    user = sign_up_email_password(email, password)
                    st.session_state.user = user
                    upsert_user(uid=user["localId"], email=email)
                    st.success("Conta criada e autenticada.")
                except Exception as e:
                    st.error("Falha ao criar conta.")
                    st.caption(str(e))

    if not st.session_state.user:
        st.title("Financial Analytics Platform")
        st.info("Faça login no menu lateral para acessar a plataforma.")
        st.stop()

ensure_auth()

# ------------------ App ------------------
st.title("Análise de Ativo (MVP)")

colA, colB, colC = st.columns([2,1,1])
with colA:
    symbol = st.text_input("Ticker", value="AAPL", help="Ex: AAPL, MSFT, PETR4.SA, KNRI11.SA")
with colB:
    rf = st.number_input("Taxa livre de risco (anual)", value=0.0, step=0.01)
with colC:
    period = st.selectbox("Período", ["1y","3y","5y","10y"], index=2)

if st.button("Analisar"):
    with st.spinner("Baixando dados e calculando..."):
        analysis = analyze_asset(symbol, rf_annual=rf, period=period)

        # para gráficos com indicadores
        df = fetch_price_history(symbol, period=period)
        df["sma20"] = sma(df["close"], 20)
        df["sma50"] = sma(df["close"], 50)
        df["sma200"] = sma(df["close"], 200)
        df["rsi14"] = rsi(df["close"], 14)

    kpis = {
        "CAGR": analysis.quant.cagr,
        "Vol anual": analysis.quant.vol_annual,
        "Sharpe": analysis.quant.sharpe,
        "Max Drawdown": analysis.quant.max_drawdown,
        "Regime": analysis.technical.trend_regime,
        "RSI(14)": analysis.technical.rsi14,
    }
    kpi_row(kpis)

    st.plotly_chart(price_with_sma(df), use_container_width=True)
    st.plotly_chart(rsi_chart(df), use_container_width=True)

    with st.expander("Sistema explicável"):
        st.subheader("Quant")
        st.json(analysis.quant.explain)
        st.subheader("Técnico")
        st.json(analysis.technical.explain)

    # Persistência
    uid = st.session_state.user.get("localId") or st.session_state.user.get("user_id")
    if st.toggle("Salvar esta análise no Firestore", value=False):
        save_analysis(uid=uid, symbol=symbol, payload=analysis.model_dump())
        st.success("Análise salva.")

