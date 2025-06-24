import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Painel por Torre", layout="wide")

# Tema customizado
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background:#fffff; }
[data-testid="stAppViewBlockContainer"] { background: transparent; }
h1, h2, h3 { color: #7a2e2e; }
thead tr th {
    background-color: #ef9a9a !important;
    color: #aa2d3d !important;
    font-weight: bold;
}
tbody tr td { color: #b74d4d !important; }
.stButton > button {
    background-color:#C4271C;
    color: white;
    border: 1.5px solid #ef9a9a;
    display: none;
}
.stButton > button:hover {
    background-color: #e53935;
}
section[data-testid="stSidebar"] {
    background: #fbe6e6;
    border-right: 4px solid #C4271C;
    color: #C4271C;
}
</style>
""", unsafe_allow_html=True)

# Menu lateral
st.sidebar.title("Menu")
pagina = st.sidebar.selectbox("Escolha a página", ["Dashboard", "Tabela Completa"])

# Dados da API
API_URL = "http://192.168.0.214/inventario-api/api/v1/dash"
try:
    response = requests.get(API_URL, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()
except Exception:
    st.error("⚠️ Nenhum dado foi carregado. A API pode estar fora do ar ou sem dados disponíveis.")
    data = []

# Transformar dados em DataFrame
registros = []
for torre in data:
    for caixa in torre.get("caixas", []):
        for bipado in caixa.get("bipagem", []):
            registros.append({
                "torre_id": torre["id"],
                "status_torre": torre["status"],
                "grupo": torre["group_user"],
                "caixa_id": caixa["id"],
                "nr_caixa": caixa["nr_caixa"],
                "identificador": caixa["identificador"],
                "unidade": bipado["unidade"],
                "modelo": bipado["modelo"],
                "patrimonio": bipado["patrimonio"]
            })

# Cria DataFrame com colunas definidas, mesmo se vazio
colunas_esperadas = [
    "lote_id", "status_lote", "grupo", "caixa_id", "nr_caixa", "identificador",
    "unidade", "modelo", "patrimonio"
]
df = pd.DataFrame(registros, columns=colunas_esperadas)

# Filtros
st.sidebar.markdown("### Filtros")
grupos = sorted(df["grupo"].dropna().unique().tolist())
status = sorted(df["status_torre"].dropna().unique().tolist())

selecionar_todos_grupos = st.sidebar.checkbox("Selecionar todos os Grupos (PA)", value=True)
selecionar_todos_status = st.sidebar.checkbox("Selecionar todos os Status das Torres", value=True)

filtro_grupo = st.sidebar.multiselect("🔍 Filtrar por Grupo (PA)", options=grupos, default=grupos if selecionar_todos_grupos else [], key="filtro_grupo")
filtro_status = st.sidebar.multiselect("🔍 Filtrar por Status da Torre", options=status, default=status if selecionar_todos_status else [], key="filtro_status")

# Aplicar filtros
df_filtrado = df[(df["grupo"].isin(filtro_grupo)) & (df["status_torre"].isin(filtro_status))].copy()

# Dashboard
if pagina == "Dashboard":
    st.title("Painel por Torre")

    total_torres = df_filtrado["torre_id"].nunique()
    total_seriais = df_filtrado.shape[0]
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
    <div style="display:flex;gap:40px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:#fff3f3;padding:15px;border-radius:10px;border:1px solid #C4271C;min-width: 150px;">
            <h3 style="margin:0;color:#C4271C;"> Total de Torres</h3>
            <p style="font-size:22px;margin:5px 0;color:#C4271C;"><strong>{total_torres}</strong></p>
        </div>
        <div style="background:#fff3f3;padding:15px;border-radius:10px;border:1px solid #C4271C;min-width: 150px;">
            <h3 style="margin:0;color:#C4271C;">📦 Total de Seriais</h3>
            <p style="font-size:22px;margin:5px 0;color:#C4271C;"><strong>{total_seriais}</strong></p>
        </div>
        <div style="background:#fff3f3;padding:15px;border-radius:10px;border:1px solid #C4271C;min-width: 150px;">
            <h3 style="margin:0;color:#C4271C;">🕒 Atualizado em</h3>
            <p style="font-size:18px;margin:5px 0;color:#C4271C;">{data_atualizacao}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    status_label_map = {
        "fechado": "Fechado",
        "aberto": "Aberto",
        "aguardando_validação": "Aguardando Validação",
        "em_andamento": "Em Andamento",
        "pendente": "Pendente"
    }
    tons_vermelho = ["#c70303", "#5a000b", "#ad4646", "#C4271C", "#ef9a9a", "#f44336"]
    legenda_cores = {label: tons_vermelho[i % len(tons_vermelho)] for i, label in enumerate(status_label_map.values())}

    # Seriais por Torre
    df_seriais_torre = df_filtrado.groupby("torre_id").size().reset_index(name="total_seriais")
    fig1 = px.bar(df_seriais_torre, x="torre_id", y="total_seriais", title="Quantidade de Seriais por Torre",
                  labels={"torre_id": "Torre", "total_seriais": "Total de Seriais"})
    st.plotly_chart(fig1, use_container_width=True)

    # Torres por PA
    df_torres_por_grupo = df_filtrado[["torre_id", "grupo"]].drop_duplicates().groupby("grupo").size().reset_index(name="total_torres")
    fig2 = px.bar(df_torres_por_grupo, x="grupo", y="total_torres", title="Quantidade de Torres por PA",
                  labels={"grupo": "PA", "total_torres": "Total de Torres"})
    st.plotly_chart(fig2, use_container_width=True)

    # Torres por Status e PA
    df_torres_status = df_filtrado[["torre_id", "grupo", "status_torre"]].drop_duplicates()
    df_torres_status["status_label"] = df_torres_status["status_torre"].map(status_label_map)
    df_grouped = df_torres_status.groupby(["grupo", "status_label"]).size().reset_index(name="quantidade")
    fig3 = px.bar(df_grouped, x="grupo", y="quantidade", color="status_label", barmode="group",
                  color_discrete_map=legenda_cores,
                  labels={"grupo": "PA", "quantidade": "Qtd. de Torres", "status_label": "Status"},
                  title="Torres por Status e PA")
    st.plotly_chart(fig3, use_container_width=True)

# Tabela Completa
elif pagina == "Tabela Completa":
    st.title("Tabela de Seriais por Torre")
    st.dataframe(df, use_container_width=True, height=500)

    def to_csv(dataframe):
        output = StringIO()
        dataframe.to_csv(output, index=False, sep=";")
        return output.getvalue().encode("utf-8")

    csv_bytes = to_csv(df)
    st.download_button("📥 Baixar CSV", data=csv_bytes, file_name="seriais_por_torre.csv", mime="text/csv")
