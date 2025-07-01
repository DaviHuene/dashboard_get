# app/filtros.py
import streamlit as st
import pandas as pd
from app.api import carregar_dados_api

def aplicar_filtros(data):
    registros = []
    for lote in data:
        status_lote = lote.get("status", "").strip().lower()
        for caixa in lote.get("caixas", []):
            for bipado in caixa.get("bipagem", []):
                registros.append({
                    "lote_id": lote["id"],
                    "status_lote": status_lote,
                    "username": lote["username"],
                    "group_user": lote.get("group_user", ""),
                    "caixa_id": caixa["id"],
                    "nr_caixa": caixa["nr_caixa"],
                    "identificador": caixa["identificador"],
                    "unidade": bipado["unidade"],
                    "modelo": bipado["modelo"],
                    "nrserie": bipado["nrserie"]
                })


    df = pd.DataFrame(registros)

    if df.empty:
        return df, df

    return df, criar_menu_filtros(df)


def criar_menu_filtros(df):
    pa = sorted(df["group_user"].dropna().unique().tolist())
    torres = sorted(df["username"].dropna().unique().tolist())
    status = sorted(df["status_lote"].dropna().unique().tolist())

    selecionar_todas_torres = st.sidebar.checkbox("Selecionar todas as Torres", value=True)
    selecionar_todos_status = st.sidebar.checkbox("Selecionar todos os Status", value=True)
    selecionar_todas_PA = st.sidebar.checkbox("Selecionar todas as PAs", value=True)

    filtro_PA = st.sidebar.multiselect("🔍 Filtrar por PA", options=pa, default=pa if selecionar_todas_PA else [])
    filtro_torres = st.sidebar.multiselect("🔍 Filtrar por Torre", options=torres, default=torres if selecionar_todas_torres else [])
    filtro_status = st.sidebar.multiselect("🔍 Filtrar por Status", options=status, default=status if selecionar_todos_status else [])

    df_filtrado = df[
        (df["group_user"].isin(filtro_PA)) &
        (df["username"].isin(filtro_torres)) &
        (df["status_lote"].isin(filtro_status))
    ].copy()

    return df_filtrado
