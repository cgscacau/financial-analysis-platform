import streamlit as st
import pyrebase


def _pyrebase_app():
    cfg = dict(st.secrets["firebase"])
    return pyrebase.initialize_app(cfg)


def sign_in_email_password(email: str, password: str):
    auth = _pyrebase_app().auth()
    return auth.sign_in_with_email_and_password(email, password)


def sign_up_email_password(email: str, password: str):
    auth = _pyrebase_app().auth()
    return auth.create_user_with_email_and_password(email, password)
