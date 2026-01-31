"""Firebase Authentication (Email/Password) via REST API.

Why: Pyrebase4 pulls legacy deps (gcloud/pkg_resources) and is brittle on newer runtimes.
This module uses the official Identity Toolkit REST endpoints.
"""

from __future__ import annotations
import requests
import streamlit as st


class FirebaseAuthError(RuntimeError):
    pass


def _api_key() -> str:
    return st.secrets["firebase"]["apiKey"]


def _post(url: str, payload: dict) -> dict:
    r = requests.post(url, json=payload, timeout=30)
    data = r.json() if r.content else {}
    if not r.ok:
        msg = data.get("error", {}).get("message", "AUTH_ERROR")
        raise FirebaseAuthError(msg)
    return data


def sign_in_email_password(email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={_api_key()}"
    return _post(url, {"email": email, "password": password, "returnSecureToken": True})


def sign_up_email_password(email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_api_key()}"
    return _post(url, {"email": email, "password": password, "returnSecureToken": True})
