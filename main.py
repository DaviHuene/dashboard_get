import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
from datetime import datetime

# 🔧 Configuração da página
st.set_page_config(page_title="Painel Inventário", layout="wide")

# 🎨 Tema customizado
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
    



</style>
""", unsafe_allow_html=True)

# 🔸 Menu lateral
st.sidebar.title("Menu")
pagina = st.sidebar.selectbox("Escolha a página", ["Dashboard", "Tabela Completa"])
    
# 🔸 Dados da API
API_URL = "http://192.168.0.214/inventario-api/api/v1/dash"
try:
    response = requests.get(API_URL, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"⚠️ Nenhum dado foi carregado. A API pode estar fora do ar ou sem dados disponíveis.")
    data = []
    grupo = []
# 🔸 Transformar em DataFrame
registros = []
for lote in data:
    for caixa in lote.get("caixas", []):
        for bipado in caixa.get("bipagem", []):
            registros.append({
                "lote_id": lote["id"],
                "status_lote": lote["status"],
                "grupo": lote["group_user"],
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


# 🔍 Filtros globais
st.sidebar.markdown("### Filtros")

# Valores únicos dos filtros
grupos = sorted(df["grupo"].dropna().unique().tolist())
status = sorted(df["status_lote"].dropna().unique().tolist())

# Checkboxes de "Selecionar todos"
selecionar_todos_grupos = st.sidebar.checkbox("Selecionar todos os Grupos (PA)", value=True)
selecionar_todos_status = st.sidebar.checkbox("Selecionar todos os Status de Lote", value=True)

# Multiselects com base nos checkboxes
filtro_grupo = st.sidebar.multiselect(
    "🔍 Filtrar por Grupo (PA)",
    options=grupos,
    default=grupos if selecionar_todos_grupos else [],
    key="filtro_grupo"
)

filtro_status = st.sidebar.multiselect(
    "🔍 Filtrar por Status do Lote",
    options=status,
    default=status if selecionar_todos_status else [],
    key="filtro_status"
)

# 🧪 Aplicar os filtros ao DataFrame base
df_filtrado = df[
    (df["grupo"].isin(filtro_grupo)) & 
    (df["status_lote"].isin(filtro_status))
].copy()         


# ======================
# 📊 DASHBOARD
# ======================
if pagina == "Dashboard":
    st.title("Painel Analítico de Seriais Bipados")
    
    total_lotes = df_filtrado["lote_id"].nunique()
    total_seriais = df_filtrado.shape[0]
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
    <div style="display:flex;gap:40px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:#fff3f3;padding:15px;border-radius:10px;border:1px solid #C4271C;min-width: 150px;">
            <h3 style="margin:0;color:#C4271C;">🔢 Total de Lotes</h3>
            <p style="font-size:22px;margin:5px 0;color:#C4271C;"><strong>{total_lotes}</strong></p>
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

    # 📌 Contadores e Última Atualização
        # 🎯 Aplicar os contadores baseados nos dados filtrados
    

        # Mapeamento de rótulos para status
        # Mapeamento de status para rótulo legível
    status_label_map = {
        "fechado": "Fechado",
        "aberto": "Aberto",
        "aguardando_validação": "Aguardando Validação",
        "em_andamento": "Em Andamento",
        "pendente": "Pendente"
    }

    # Lista de cores em tons de vermelho
    tons_vermelho = ["#c70303", "#5a000b", "#ad4646", "#C4271C", "#ef9a9a", "#f44336"]

    # Gera o mapa de cores com base nas labels de status
    legenda_cores = {
        label: tons_vermelho[i % len(tons_vermelho)]
        for i, label in enumerate(status_label_map.values())
    }
    

    # 1️⃣ Seriais por Grupo (Fechados)
    # st.header("Total de Seriais por PA (Lotes Fechados por Status)")

    df_fechado = df_filtrado[df_filtrado["status_lote"].str.lower() == "fechado"].copy()
    df_fechado["status_lote"] = df_fechado["status_lote"].str.lower().str.replace(" ", "_")
    df_fechado["status_lote_label"] = df_fechado["status_lote"].map(status_label_map)

    df_seriais_status = df_fechado.groupby(["grupo", "status_lote_label"]).size().reset_index(name="total_seriais")

    fig1 = px.bar(df_seriais_status, x="grupo", y="total_seriais", color="status_lote_label",
                barmode="group", text_auto=True,
                labels={"grupo": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status"},
                title="Total de Seriais por PA (Lotes Fechados por Status)",
                color_discrete_map=legenda_cores)
    fig1.update_traces(textposition="inside", textfont_color="white")
    fig1.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=16), legend_title="Status")
    st.plotly_chart(fig1, use_container_width=False, config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})


    # 2️⃣ Seriais por Grupo e Status (Exceto Fechados)
    #st.header("Seriais por PA (Todos os Status Diferentes de Fechado)")
    df_abertos = df_filtrado[df_filtrado["status_lote"].str.lower() != "fechado"].copy()
    df_abertos["status_lote"] = df_abertos["status_lote"].str.lower().str.replace(" ", "_")
    df_abertos["status_lote_label"] = df_abertos["status_lote"].map(status_label_map)

    df_grouped = df_abertos.groupby(["grupo", "status_lote_label"]).size().reset_index(name="quantidade")

    fig2 = px.bar(
        df_grouped,
        x="grupo",
        y="quantidade",
        color="status_lote_label",
        color_discrete_map=legenda_cores,
        barmode="group",
        text_auto=True,
        labels={"grupo": "PA", "quantidade": "Qtd. de Seriais", "status_lote_label": "Status"},
        title="Quantidade de Seriais por PA (Status ≠ Fechado)"
    )
    fig2.update_traces(textposition="inside", textfont_color="white")
    fig2.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=16), legend_title="Status")
    st.plotly_chart(fig2, use_container_width=False, config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

    # 4️⃣ Lotes por Grupo e Status (Todos)
    # st.header("Lotes por PA (Todos os Status)")
    df_unico = df_filtrado[["grupo", "lote_id", "status_lote"]].drop_duplicates()
    df_unico["status_lote"] = df_unico["status_lote"].str.lower().str.replace(" ", "_")
    df_unico["status_lote_label"] = df_unico["status_lote"].map(status_label_map)

    df_grouped = df_unico.groupby(["grupo", "status_lote_label"]).size().reset_index(name="quantidade")

    fig3 = px.bar(df_grouped, x="grupo", y="quantidade", color="status_lote_label",
                color_discrete_map=legenda_cores, barmode="group", text_auto=True,
                labels={"grupo": "PA", "quantidade": "Qtd. de Lotes", "status_lote_label": "Status"},
                title="Quantidade de Lotes por PA (Todos os Status)")
    fig3.update_traces(textposition="inside", textfont_color="white")
    fig3.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=16), legend_title="Status")
    st.plotly_chart(fig3, use_container_width=False, config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})



    # 5️⃣ NOVO: Seriais por Grupo (Todos os Status, incluindo Fechado)
    #st.header("Seriais por PA (Todos os Status)")
    df_all = df_filtrado.copy()
    df_all["status_lote"] = df_all["status_lote"].str.lower().str.replace(" ", "_")
    df_all["status_lote_label"] = df_all["status_lote"].map(status_label_map)

    df_total = df_all.groupby(["grupo", "status_lote_label"]).size().reset_index(name="quantidade")

    fig4 = px.bar(df_total, x="grupo", y="quantidade", color="status_lote_label",
                color_discrete_map=legenda_cores, barmode="group", text_auto=True,
                labels={"grupo": "PA", "quantidade": "Qtd. de Seriais", "status_lote_label": "Status"},
                title="Quantidade Total de Seriais por PA (Todos os Status)")
    fig4.update_traces(textposition="inside", textfont_color="white")
    fig4.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=16), legend_title="Status")
    st.plotly_chart(fig4, use_container_width=False, config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

# ======================
# 📄 TABELA COMPLETA
# ======================

elif pagina == "Tabela Completa":
    st.title(" Tabela de Seriais Bipados")

    # Ocultar a primeira coluna
    df_sem_primeira = df.iloc[:, 0:]

    # CSS para ocultar índice e scroll lateral
    st.markdown("""
        <style>
        .row-heading.level0 {display:none !important;}
        .blank {display:none !important;}
        div[data-testid="stDataFrameScrollable"] > div:nth-child(1) {
            overflow-x: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    # Exibe tabela
    st.dataframe(df_sem_primeira, use_container_width=True, height=500, hide_index=True)

    def to_csv(dataframe):
        output = StringIO()
        dataframe.to_csv(output, index=False, sep=";")  # usa ; como separador, comum no Brasil
        return output.getvalue().encode("utf-8")  #
    # Gera CSV e botão
    csv_bytes = to_csv(df_sem_primeira)

    st.download_button(
        label="📥 Baixar CSV",
        data=csv_bytes,
        file_name="seriais_bipados.csv",
        mime="text/csv"
    )
