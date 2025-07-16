import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
from datetime import datetime
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Painel Inventário", layout="wide")

# === MODO LIGHT / DARK COM MUDANÇA NO MENU E GRÁFICOS ===
st.sidebar.title("Menu")
modo = st.sidebar.radio("🌗 Tema", ["Claro", "Escuro"], horizontal=True)

if modo == "Claro":
    cor_menu = "#fcdddd"
    cor_texto_menu = "#000000"
    cor_fundo = "#ffffff"
    cor_primaria = "#c70101"
    cor_input = "#ffffff"
else:
    cor_menu = "#272727"
    cor_texto_menu = "#FFFFFF"
    cor_fundo = "#121212"
    cor_primaria = "#c70101"
    cor_input = "#202020"

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:{cor_fundo};
        color: {cor_texto_menu};
    }}
    [data-testid="stSidebar"] {{
        background-color: {cor_menu};
        color: {cor_texto_menu};
        border-right: 3px solid {cor_primaria};
    }}
    [data-testid="stMarkdownContainer"] *,
    .stText, .stMarkdown, .stDataFrame, label,
    h1, h2, h3, h4, h5, h6, p, div, span, td {{
        color: {cor_texto_menu} !important;
    }}
    div[data-baseweb="select"] > div {{
        border: 2px solid {cor_primaria} !important;
        border-radius: 10px !important;
        background-color: {cor_input} !important;
    }}
    div[data-baseweb="select"] span {{ 
        color: {cor_menu} !important;
        font-weight: bold;
    }}
    .stButton > button {{
        background-color: {cor_primaria};
        color: white;
        border: none;
        border-radius: 6px;
    }}
    .stMultiSelect,.stDateInput {{
        color: {cor_primaria} !important;
    }}
    </style>
""", unsafe_allow_html=True)

API_URL = "http://192.168.0.216/inventario-api/api/v1/dash/cache/"
API_URL1 = "http://127.0.0.1:8000/inventario-api/api/v1/dash/painel/resumo"

try:
    response = requests.get(API_URL, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()

    # 🔍 Verifica se existe pelo menos um 'status_lote' nos lotes
    if not any("status" in lote for lote in data):
        st.error("⚠️ Nenhum lote encontrado.")
        st.stop()

except Exception:
    st.error("⚠️ Nenhum dado foi carregado. A API pode estar fora do ar ou sem dados disponíveis.")
    st.stop()

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
                "nrserie": None,
                "estado": None,
                "observacao": None,
                "acao": None
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
                            "nrserie": None,
                            "estado": None,
                            "observacao": None,
                            "acao": None
                        })
                    else:
                        for bipado in caixa.get("bipagem", []):
                            try:
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
                                    "nrserie": bipado.get("nrserie"),
                                    "estado": bipado.get("estado"),
                                    "observacao": bipado.get("observacao"),
                                    "acao": bipado.get("acao")
                                })
                            except:
                                pass
                except:
                    pass
    except:
        pass

df = pd.DataFrame(registros)

# Exemplo: detectar se há lote aberto
tem_aberto = not df[df["status_lote"] == "aberto"].empty
if not tem_aberto:
    st.warning("⚠️ Nenhum dado disponível no momento. Os gráficos aparecerão vazios.")
    df = pd.DataFrame(columns=[
        "lote_id", "status_lote", "username", "group_user", "caixa_id", "nr_caixa",
        "identificador", "unidade", "modelo", "estado", "acao", "observacao"
    ])

st.sidebar.markdown("### Filtros")

# Filtros de Torre e Status e PA
pa = sorted(df["group_user"].dropna().unique().tolist())
torres = sorted(df["username"].dropna().unique().tolist())
status = sorted(df["status_lote"].dropna().unique().tolist())
estado = sorted(df["estado"].dropna().unique().tolist())
acao = sorted(df["acao"].dropna().unique().tolist())

selecionar_todas_torres = st.sidebar.checkbox("Selecionar todas as Torres", value=True)
selecionar_todos_status = st.sidebar.checkbox("Selecionar todos os Status", value=True)
selecionar_todas_PA = st.sidebar.checkbox("Selecionar todas as PAs", value=True)
selecionar_todos_estado = st.sidebar.checkbox("Selecionar todos os Status-1", value=True)
selecionar_todas_acao = st.sidebar.checkbox("Selecionar todos os Status-2", value=True)

filtro_PA = st.sidebar.multiselect(
    "🔍 Filtrar por PA", options=pa,
    default=pa if selecionar_todas_PA else []
)
filtro_torres = st.sidebar.multiselect(
    "🔍 Filtrar por Torre", options=torres,
    default=torres if selecionar_todas_torres else []
)
filtro_status = st.sidebar.multiselect(
    "🔍 Filtrar por Status", options=status,
    default=status if selecionar_todos_status else []
)
filtro_estado = st.sidebar.multiselect(
    "🔍 Filtrar por Status-1", options=estado,
    default=estado if selecionar_todos_estado else []
)
filtro_acao = st.sidebar.multiselect(
    "🔍 Filtrar por Status-2", options=acao,
    default=acao if selecionar_todas_acao else []
)

# Aplicar todos os filtros, incluindo PA
df_filtrado = df[
    (df["group_user"].isin(filtro_PA)) &
    (df["username"].isin(filtro_torres)) &
    (df["status_lote"].isin(filtro_status)) &
    (df["estado"].isin(filtro_estado)) &
    (df["acao"].isin(filtro_acao))
].copy()

st.title("Painel Analítico de Seriais Bipados")

# Base completa sem filtro (para contagem real de lotes)
df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

# Contagens
fechados = df_filtrado[df_filtrado["status_lote"] == "fechado"].shape[0]
invalidado = df_filtrado[df_filtrado["status_lote"] == "invalidado"].shape[0]
aberto = df_filtrado[df_filtrado["status_lote"] == "aberto"].shape[0]
total_lotes = df_filtrado.shape[0]

percentual_fechados = round((fechados / total_lotes) * 100, 2) if total_lotes else 0
percentual_invalidado = round((invalidado / total_lotes) * 100, 2) if total_lotes else 0
percentual_aberto = round((aberto / total_lotes) * 100, 2) if total_lotes else 0

# Exibir no Streamlit
# Indicadores adicionais
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
        <h3 style="margin:0;color:{cor_texto_menu};">📦 Total de Lotes</h3>
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
    """, unsafe_allow_html=True)

# Exibe a tabela
st.title("Tabela de Seriais Bipados")
st.dataframe(df_filtrado, use_container_width=True, height=800, hide_index=True)

# Botão para exportar CSV sem 'patrimonio'
def to_csv(dataframe):
    output = StringIO()
    dataframe.to_csv(output, index=False, sep=";")
    return output.getvalue().encode("utf-8")

csv_bytes = to_csv(df_filtrado)
st.download_button(
    label="📥 Baixar CSV",
    data=csv_bytes,
    file_name="seriais_bipados.csv",
    mime="text/csv"
)
