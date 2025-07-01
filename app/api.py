# app/api.py
import requests
import streamlit as st

API_URL = "http://192.168.0.214/inventario-api/api/v1/dash"

@st.cache_data(ttl=300)
def carregar_dados_api():
    try:
        response = requests.get(API_URL, headers={"accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao carregar dados da API: {e}")
        return []
