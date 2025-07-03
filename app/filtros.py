import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

def aplicar_filtros(data):
    registros = []

    for lote in data:
        try:
            if not lote.get("caixas"):
                registros.append({
                    "lote_id": lote.get("id"),
                    "status_lote": lote.get("status", "").strip().lower(),
                    "username": lote.get("username", ""),
                    "group_user": lote.get("group_user", ""),
                    "caixa_id": None,
                    "nr_caixa": None,
                    "identificador": None,
                    "unidade": None,
                    "modelo": None,
                    "nrserie": None
                })
            else:
                for caixa in lote.get("caixas", []):
                    try:
                        if not caixa.get("bipagem"):
                            registros.append({
                                "lote_id": lote.get("id"),
                                "status_lote": lote.get("status", "").strip().lower(),
                                "username": lote.get("username", ""),
                                "group_user": lote.get("group_user", ""),
                                "caixa_id": caixa.get("id"),
                                "nr_caixa": caixa.get("nr_caixa"),
                                "identificador": caixa.get("identificador"),
                                "unidade": None,
                                "modelo": None,
                                "nrserie": None
                            })
                        else:
                            for bipado in caixa.get("bipagem", []):
                                registros.append({
                                    "lote_id": lote.get("id"),
                                    "status_lote": lote.get("status", "").strip().lower(),
                                    "username": lote.get("username", ""),
                                    "group_user": lote.get("group_user", ""),
                                    "caixa_id": caixa.get("id"),
                                    "nr_caixa": caixa.get("nr_caixa"),
                                    "identificador": caixa.get("identificador"),
                                    "unidade": bipado.get("unidade"),
                                    "modelo": bipado.get("modelo"),
                                    "nrserie": bipado.get("nrserie")
                                })
                    except:
                        pass
        except:
            pass

    df = pd.DataFrame(registros)

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível no momento. Os gráficos aparecerão vazios.")
    elif df["status_lote"].str.lower().eq("aberto").sum() == 0:
        st.warning("⚠️ Nenhum lote com status 'aberto' encontrado.")

    return df



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
