import streamlit as st

import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH (Streamlit Cloud compatibility)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from infra.firebase.auth import (
    sign_in_email_password,
    sign_up_email_password,
    FirebaseAuthError,
)

# Firestore is optional at runtime (graceful degradation)
try:
    from infra.firebase.repositories.user_repo import upsert_user, save_analysis
except Exception:
    upsert_user = None
    save_analysis = None

from core.use_cases.analyze_asset import analyze_asset
from core.data.providers.yfinance_provider import fetch_price_history, DataNotAvailableError
from core.engines.technical.indicators import sma, rsi
from app.ui.components import kpi_row
from app.ui.charts import price_with_sma, rsi_chart


st.set_page_config(page_title="Financial Analytics Platform", layout="wide")


# ------------------ Helpers ------------------

def secrets_healthcheck() -> dict:
    """
    Validates presence of required secrets keys.
    Does NOT validate correctness (e.g., JSON parse), only existence.
    """
    status = {"firebase_ok": False, "firebase_admin_ok": False, "missing": []}

    try:
        _ = st.secrets["firebase"]["apiKey"]
        status["firebase_ok"] = True
    except Exception:
        status["missing"].append('Missing secrets: [firebase].apiKey')

    try:
        _ = st.secrets["firebase_admin"]["service_account_json"]
        status["firebase_admin_ok"] = True
    except Exception:
        status["missing"].append('Missing secrets: [firebase_admin].service_account_json')

    return status


def logout():
    st.session_state.user = None
    st.session_state.email = None
    st.rerun()


def ensure_auth():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "email" not in st.session_state:
        st.session_state.email = None

    # Sidebar Auth UI
    with st.sidebar:
        st.subheader("Login")

        # Avoid empty label warnings
        mode = st.radio(
            "Modo",
            ["Entrar", "Criar conta"],
            horizontal=True,
            label_visibility="collapsed",
        )

        email = st.text_input("Email", value=st.session_state.email or "")
        password = st.text_input("Senha", type="password")

        # Show minimal secrets status (helps debugging on Cloud)
        s = secrets_healthcheck()
        if not s["firebase_ok"]:
            st.error("Secrets do Firebase (client) não configurados.")
            for m in s["missing"]:
                st.caption(m)
            st.stop()

        # Auth actions
        if mode == "Entrar":
            if st.button("Entrar"):
                try:
                    user = sign_in_email_password(email, password)
                    st.session_state.user = user
                    st.session_state.email = email
                    st.success("Autenticado.")
                    # Best-effort Firestore (won't break login)
                    if upsert_user is not None:
                        try:
                            upsert_user(uid=user["localId"], email=email)
                        except Exception as e:
                            st.warning(
                                "Login OK, mas Firestore indisponível. "
                                "Você pode usar o app; salvar dados ficará desativado."
                            )
                            st.caption(str(e))
                    st.rerun()
                except FirebaseAuthError as e:
                    st.error("Falha no login (Firebase Auth).")
                    st.caption(str(e))
                except Exception as e:
                    st.error("Falha inesperada no login.")
                    st.caption(str(e))

        else:
            if st.button("Criar conta"):
                try:
                    user = sign_up_email_password(email, password)
                    st.session_state.user = user
                    st.session_state.email = email
                    st.success("Conta criada e autenticada.")
                    # Best-effort Firestore (won't break signup)
                    if upsert_user is not None:
                        try:
                            upsert_user(uid=user["localId"], email=email)
                        except Exception as e:
                            st.warning(
                                "Cadastro OK, mas Firestore indisponível. "
                                "Você pode usar o app; salvar dados ficará desativado."
                            )
                            st.caption(str(e))
                    st.rerun()
                except FirebaseAuthError as e:
                    # Common messages: EMAIL_EXISTS, INVALID_PASSWORD, WEAK_PASSWORD
                    st.error("Falha ao criar conta (Firebase Auth).")
                    st.caption(str(e))
                except Exception as e:
                    st.error("Falha inesperada ao criar conta.")
                    st.caption(str(e))

        # Logged-in status + logout
        if st.session_state.user:
            st.divider()
            st.caption("Usuário autenticado:")
            st.code(st.session_state.email or "(email indisponível)")
            st.button("Sair", on_click=logout)

    # Gate
    if not st.session_state.user:
        st.title("Financial Analytics Platform")
        st.info("Faça login no menu lateral para acessar a plataforma.")
        st.stop()


# ------------------ App ------------------

ensure_auth()

st.title("Análise de Ativo (MVP)")

colA, colB, colC = st.columns([2, 1, 1])
with colA:
    symbol = st.text_input("Ticker", value="AAPL", help="Ex: AAPL, MSFT, PETR4.SA, KNRI11.SA")
with colB:
    rf = st.number_input("Taxa livre de risco (anual)", value=0.0, step=0.01)
with colC:
    period = st.selectbox("Período", ["1y", "3y", "5y", "10y"], index=2)

if st.button("Analisar"):
    try:
        with st.spinner("Baixando dados e calculando..."):
            # Use case (quant + technical)
            analysis = analyze_asset(symbol, rf_annual=rf, period=period)

            # Raw prices for charts + indicators
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

        # Persistência (best-effort)
        uid = (st.session_state.user.get("localId")
               or st.session_state.user.get("user_id"))

        if uid and save_analysis is not None:
            if st.toggle("Salvar esta análise no Firestore", value=False):
                try:
                    save_analysis(uid=uid, symbol=symbol, payload=analysis.model_dump())
                    st.success("Análise salva.")
                except Exception as e:
                    st.warning("Não foi possível salvar no Firestore (persistência indisponível).")
                    st.caption(str(e))
        else:
            st.caption("Persistência no Firestore indisponível (UID ou módulo não carregado).")

    except DataNotAvailableError as e:
        st.error("Sem dados de preço para este ticker/período.")
        st.caption(str(e))
        st.info(
            "Dicas: \n"
            "- Brasil: use sufixo .SA (ex.: PETR4.SA, VALE3.SA, KNRI11.SA)\n"
            "- EUA: AAPL, MSFT, SPY\n"
            "- Tente reduzir para 1y ou tentar outro ticker"
        )
    except Exception as e:
        st.error("Erro inesperado ao analisar.")
        st.caption(str(e))
