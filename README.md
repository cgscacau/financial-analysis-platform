# Financial Analytics Platform (Streamlit + Firebase)

Plataforma web de análise de ativos (BR/US) com arquitetura modular (core engines) e backend Firebase (Auth + Firestore).

## Stack
- Python + Streamlit
- Firebase Auth (Email/Senha) + Firestore
- yfinance (dados de mercado)
- pandas/numpy/scipy/cvxpy (próximas fases)
- plotly

## 1) Como rodar localmente

### 1.1 Pré-requisitos
- Python 3.11+

### 1.2 Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 1.3 Firebase (obrigatório para login)
Este repositório usa:
- **Cliente**: Pyrebase4 (login email/senha) via `st.secrets`
- **Admin**: firebase-admin (Firestore) via Service Account JSON

#### Passo a passo (Vou criar)
1. Crie um projeto em: https://console.firebase.google.com/
2. No projeto, ative **Authentication** → **Sign-in method** → habilite **Email/Password**.
3. Crie um app Web: **Project settings** → **Your apps** → **Web**.
4. Crie o Firestore: **Build** → **Firestore Database** → **Create database** (modo production ou test).
5. Gere Service Account:
   - **Project settings** → **Service accounts** → **Generate new private key**

#### Secrets do Streamlit
Crie o arquivo `.streamlit/secrets.toml` (NÃO commitar) com:
```toml
[firebase]
apiKey = "..."
authDomain = "..."
projectId = "..."
storageBucket = "..."
messagingSenderId = "..."
appId = "..."

[firebase_admin]
# cole o JSON da service account como string (uma linha)
service_account_json = "{...}"
```

> No Streamlit Cloud, configure essas mesmas chaves em **App settings → Secrets**.

### 1.4 Rodar
```bash
streamlit run app/Home.py
```

## 2) Deploy no Streamlit Cloud
1. Suba este repo no GitHub
2. Aponte o Streamlit Cloud para o arquivo `app/Home.py`
3. Configure os Secrets do Firebase

## 3) Estrutura
- `app/`: UI Streamlit
- `core/`: engines e use_cases (testável, sem Streamlit)
- `infra/`: Firebase (auth + firestore)

## 4) Roadmap (alto nível)
- Fundamentalista (scores configuráveis)
- Dividend engine
- Otimização de carteiras (cvxpy)
- Backtests e Monte Carlo

