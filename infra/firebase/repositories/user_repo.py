from infra.firebase.client import get_firestore_client


def upsert_user(uid: str, email: str):
    db = get_firestore_client()
    ref = db.collection("users").document(uid)
    ref.set({"email": email}, merge=True)


def save_analysis(uid: str, symbol: str, payload: dict):
    db = get_firestore_client()
    db.collection("users").document(uid).collection("analyses").add({
        "symbol": symbol,
        "payload": payload,
    })
