# app/tabela.py
import streamlit as st
from io import StringIO
import pandas as pd
from app.api import carregar_dados_api
from  app.filtros import aplicar_filtros

def exibir_tabela_completa(df_filtrado, modo, cores):
    df_tabela = df_filtrado.rename(columns={
        "username": "Torre",
        "group_user": "PA",
        "nrserie": "Nr Série"
    }).drop(columns=["patrimonio"], errors="ignore")

    cor_botao = "#000000" if modo == "Escuro" else cores["primaria"]
    cor_texto_botao = "#000000" if modo == "Escuro" else "#ffffff"

    st.markdown(f"""
    <style>
    .stDownloadButton > button {{
        background-color: {cor_texto_botao} !important;
        color: {cor_texto_botao} !important;
        border: 1px solid {cor_texto_botao};
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    .stDownloadButton > button:hover {{
        background-color: {cor_texto_botao} !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.title("Tabela de Seriais Bipados")
    st.dataframe(df_tabela, use_container_width=True, height=500, hide_index=True)

    def to_csv(dataframe):
        output = StringIO()
        dataframe.to_csv(output, index=False, sep=";")
        return output.getvalue().encode("utf-8")

    csv_bytes = to_csv(df_tabela)
    st.download_button(
        label="📥 Baixar CSV",
        data=csv_bytes,
        file_name="seriais_bipados.csv",
        mime="text/csv"
    )
