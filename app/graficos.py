# Este arquivo conterá todas as funções de visualização com Plotly, separadas da lógica principal do Streamlit

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from app.api import carregar_dados_api


def exibir_indicadores(df, df_filtrado, cor_fundo, cor_primaria, cor_texto_menu):
    # Indicadores principais
    df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
    df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

    fechados = df_lotes[df_lotes["status_lote"] == "fechado"].shape[0]
    invalidado = df_lotes[df_lotes["status_lote"] == "invalidado"].shape[0]
    aberto = df_lotes[df_lotes["status_lote"] == "aberto"].shape[0]
    total_lotes = df_lotes.shape[0]

    percentual_fechados = round((fechados / total_lotes) * 100, 2) if total_lotes else 0
    percentual_invalidado = round((invalidado / total_lotes) * 100, 2) if total_lotes else 0
    percentual_aberto = round((aberto / total_lotes) * 100, 2) if total_lotes else 0

    total_seriais = df_filtrado.shape[0]
    total_torres = df_filtrado["username"].nunique()
    total_caixas = df_filtrado["caixa_id"].nunique()

    st.markdown(f"""
    <div style="display:flex;gap:40px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🏢 Total de Torres</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_torres}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦 Caixas Únicas</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_caixas}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦 Total de Seriais</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_seriais}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📈 Lotes Fechados</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_fechados}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🟡 Lotes Abertos</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_aberto}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">❌ Lotes Invalidados</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_invalidado}%</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def exibir_data_atualizacao(cor_fundo):
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"<div style='background:{cor_fundo};'><h3>🕒 Atualizado em: {data_atualizacao}</h3></div>", unsafe_allow_html=True)
# app/graficos.py

def exibir_indicadores(df, df_filtrado, cor_fundo, cor_primaria, cor_texto_menu):
    # Indicadores principais
    df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
    df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

    fechados = df_lotes[df_lotes["status_lote"] == "fechado"].shape[0]
    invalidado = df_lotes[df_lotes["status_lote"] == "invalidado"].shape[0]
    aberto = df_lotes[df_lotes["status_lote"] == "aberto"].shape[0]
    total_lotes = df_lotes.shape[0]

    percentual_fechados = round((fechados / total_lotes) * 100, 2) if total_lotes else 0
    percentual_invalidado = round((invalidado / total_lotes) * 100, 2) if total_lotes else 0
    percentual_aberto = round((aberto / total_lotes) * 100, 2) if total_lotes else 0

    total_seriais = df_filtrado.shape[0]
    total_torres = df_filtrado["username"].nunique()
    total_caixas = df_filtrado["caixa_id"].nunique()

    st.markdown(f"""
    <div style="display:flex;gap:40px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🏢 Total de Torres</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_torres}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦 Caixas Únicas</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_caixas}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦 Total de Seriais</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_seriais}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📈 Lotes Fechados</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_fechados}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🟡 Lotes Abertos</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_aberto}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">❌ Lotes Invalidados</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_invalidado}%</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def exibir_data_atualizacao(cor_fundo):
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"<div style='background:{cor_fundo};'><h3>🕒 Atualizado em: {data_atualizacao}</h3></div>", unsafe_allow_html=True)

def titulo_dashboard(df_filtrado, modo, cor_fundo, cor_texto_menu):
    st.title("Painel Analítico de Seriais Bipados")

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado disponível para exibir os gráficos.")
        return

    col1, col2 = st.columns(2)

    with col1:
        df_por_torre = df_filtrado.groupby("username").size().reset_index(name="total")
        fig = px.bar(df_por_torre, x="username", y="total", title="Quantidade de Seriais por Torre")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_por_status = df_filtrado.groupby("status_lote").size().reset_index(name="total")
        fig2 = px.pie(df_por_status, names="status_lote", values="total", title="Distribuição por Status do Lote")
        st.plotly_chart(fig2, use_container_width=True)

    # Gráfico adicional: Seriais por PA e Torre
    df_extra = df_filtrado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig3 = px.bar(df_extra, x="group_user", y="quantidade", color="username", barmode="group",
                  title="Total de Seriais por PA e Torre")
    st.plotly_chart(fig3, use_container_width=True)
