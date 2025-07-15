import streamlit as st
from streamlit import session_state as state
import requests


Api_url = "http://127.0.0.1:8000/Template/api/v1/cars/"


st.title ('cadastro de carros')

with st.form(key='form_cadastro_carro'):
    nome = st.text_input("Nome")
    modelo = st.text_input("Modelo")
    cor = st.text_input("Cor")
    marca = st.text_input("Marca")
    versao = st.text_input("Versão")
    ano = st.number_input("Ano", min_value=1900, max_value=2100, step=1)
    
    submitted = st.form_submit_button("Cadastrar")
    
    if submitted:
        dados= {
            "nome": nome,
            "modelo": modelo,
            "cor": cor,
            "marca": marca,
            "versao": versao,
            "ano": ano
        }
        
        try:
            response = requests.post(Api_url, json=dados)
            if response.status_code == 201:
                st.success("Carro cadastrado com sucesso!")
            else:
                st.error(f"Erro ao cadastrar carro: {response.text}")
        except Exception as e:
            st.error(f"Erro ao cadastrar carro: {e}")   