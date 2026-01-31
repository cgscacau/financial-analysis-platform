import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st


def get_firestore_client():
    if not firebase_admin._apps:
        raw = st.secrets["firebase_admin"]["service_account_json"]
        cred = credentials.Certificate(json.loads(raw))
        firebase_admin.initialize_app(cred)
    return firestore.client()
