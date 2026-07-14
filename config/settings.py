import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Daftar semua environment variable yang dibutuhkan
ENV_KEYS = [
    "OPENAI_API_KEY",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_PROJECT"
]

for key in ENV_KEYS:
    # Ambil dari st.secrets (jika ada), jika tidak fallback ke os.getenv (.env)
    try:
        val = st.secrets.get(key, os.getenv(key))
    except Exception:
        val = os.getenv(key)
        
    # Paksa masuk ke os.environ agar otomatis terbaca oleh modul LangChain
    if val:
        os.environ[key] = str(val)

# Expose variabel utama untuk diimport modul lain
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")