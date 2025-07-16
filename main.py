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
    cor_input="#ffffff"
else:
    cor_menu = "#272727"
    cor_texto_menu = "#FFFFFF"
    cor_fundo = "#121212"
    cor_primaria = "#c70101"
    cor_input="#202020"
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
    h1, h2, h3, h4, h5, h6, p, div, span,  td{{
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

pagina = st.sidebar.selectbox("Escolha a página", ["Dashboard", "Tabela Completa"])

API_URL = "http://192.168.0.216/inventario-api/api/v1/dash/cache/"

try:
    response = requests.get(API_URL, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()

    # 🔍 Verifica se existe pelo menos um 'status_lote' nos lotes
    if not any("status" in lote for lote in data):
        st.error("⚠️ Nenhum lote  encontrado.")
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
                "observacao":None,
                "acao":None
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
                            "observacao":None,
                            "acao":None
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
                                    "estado": bipado.get ("estado"),
                                    "observacao":bipado.get ("observacao"),
                                    "acao":bipado.get ("acao")
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
        "identificador", "unidade", "modelo","estado","acao", "observacao"
])

   
st.sidebar.markdown("### Filtros")

# Filtros de Torre e Status e PA
pa = sorted(df["group_user"].dropna().unique().tolist())
torres = sorted(df["username"].dropna().unique().tolist())
status = sorted(df["status_lote"].dropna().unique().tolist())
estado = sorted(df["estado"].dropna().unique().tolist())
acao= sorted(df["acao"].dropna().unique().tolist())

selecionar_todas_torres = st.sidebar.checkbox("Selecionar todas as Torres", value=True)
selecionar_todos_status = st.sidebar.checkbox("Selecionar todos os Status", value=True)
selecionar_todas_PA = st.sidebar.checkbox("Selecionar todas as PAs", value=True)
selecionar_todos_estado = st.sidebar.checkbox("Selecionar todos os Status-1", value=True)
selecionar_todas_acao = st.sidebar.checkbox("Selecionar todos os Status-2", value=True)

filtro_PA =st.sidebar.multiselect(
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
filtro_acao= st.sidebar.multiselect(
     "🔍 Filtrar por Status-2", options=acao,
   default=acao if selecionar_todas_acao else []
)



# Aplicar todos os filtros, incluindo PA
df_filtrado = df[
    (df["group_user"].isin(filtro_PA))&
    (df["username"].isin(filtro_torres))&
    (df["status_lote"].isin(filtro_status))&
    (df["estado"].isin(filtro_estado))&
    (df["acao"].isin(filtro_acao)) 
].copy()
#

if pagina == "Dashboard":
  
    st.title("Painel Analítico de Seriais Bipados")
    
    # Base completa sem filtro (para contagem real de lotes)
    df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
    df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

    # Contagens
   
# Agora suas contagens e percentuais devem usar o df_filtrado 👇
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
        """,unsafe_allow_html=True)
   
 


    status_label_map = {
        "fechado": "Fechado",
        "aberto": "Aberto",
        "cancelado": "Cancelado",
        "aguardando_validação": "Aguardando Validação",
        "em_andamento": "Em Andamento",
        "pendente": "Pendente"
    }
    # Gerar cores vermelhas por torre
    tons_vermelho = [
    "#c70303",  # vermelho puro
    "#9b0000",  # vinho escuro
    "#c23737",
    "#d14a4a",# telha queimado
    "#d80202",  # vermelho tomate
    "#ef9a9a",  # rosa claro avermelhado
    "#f44336",  # vermelho vibrante
    "#e53935",  # cereja intenso
    "#d32f2f",  # rubi escuro
    "#b71c1c",  # vermelho bordô
    "#ff6f61",  # coral avermelhado
    "#e57373",  # salmão queimado
    "#f28b82",  # vermelho pastel
    "#a30000",  # bordô forte
    "#ff4d4d",  # vermelho claro intenso
    "#cc0000"  # vermelho clássico
    ]
    usuarios = sorted(df_filtrado["username"].dropna().unique())
    mapa_cores_username = {user: tons_vermelho[i % len(tons_vermelho)] for i, user in enumerate(usuarios)}
   
    @st.cache_data(ttl=5000)
    def carregar_dados():
        response = requests.get(API_URL, headers={"accept": "application/json"})
        response.raise_for_status()
        return response.json()

    data = carregar_dados()

        # 🔁 Garantir que 'username' e 'group_user' estejam presentes em df_lotes
    if "username" not in df_lotes.columns or "group_user" not in df_lotes.columns:
        df_lotes = df_lotes.merge(
            df_filtrado[["lote_id", "username", "group_user"]].drop_duplicates(),
            on="lote_id", how="left"
        )

        # 📦 Garantir colunas necessárias
    colunas_necessarias = ["caixa_id", "username", "group_user", "status_lote"]
    faltando = [col for col in colunas_necessarias if col not in df_filtrado.columns]

    if faltando:
        st.warning(f"⚠️ Colunas faltando no DataFrame: {', '.join(faltando)}")
    else:
        # 🔄 Remover duplicatas por caixa única
        df_caixas = df_filtrado.drop_duplicates(subset=["caixa_id", "username", "group_user", "status_lote"])

        # ✅ Filtrar apenas caixas de lotes fechados
        df_fechadas = df_caixas[df_caixas["status_lote"] == "fechado"].copy()  # <- ESSENCIAL
        df_fechadas.loc[:, "torre_pa"] = df_fechadas["username"] + " - " + df_fechadas["group_user"]

        # 🧮 Agrupar e contar caixas fechadas por Torre-PA
        df_caixas_fechadas = df_fechadas.groupby("torre_pa")["caixa_id"].nunique().reset_index(name="caixas_fechadas")

        fig1 = px.bar(
        df_caixas_fechadas,
        x="torre_pa",
        y="caixas_fechadas",
        text="caixas_fechadas",
        title="Total de lotes Fechados por Torre e PA",
        labels={"torre_pa": "Torre - PA", "caixas_fechadas": "Caixas Fechadas"}
    )

        fig1.update_traces(marker_color="#c70101", textposition="inside", textfont_size=2500)

        fig1.update_layout(width=2000, height=1000,
        plot_bgcolor='rgba(0,0,0,0)',        # fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)',       # fundo da área externa
        font=dict(color=cor_texto_menu),    # cor dos textos do gráfico
        legend=dict(font=dict(color=cor_texto_menu)),  # legenda
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc",
            zeroline=False
        )
    )
        fig1.update_traces(textposition='inside', textfont_color='white',textfont_size=2500)
        st.plotly_chart(fig1,  use_container_width=True,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

    # Paleta em tons de vermelho para os estados
    custom_colors = {
        "good": "#C40606",
        "triagem": "#8B163D",
        "bad": "#94180A",
        "obsoleto": "#FF2A13"
    }

    # 1. Garantir que a coluna 'estado' está em minúsculo
    df_filtrado["estado"] = df_filtrado["estado"].str.lower()

    # 2. Agrupar por group_user, username e estado
    df_estado = df_filtrado.groupby(["group_user", "username", "estado"]).size().reset_index(name="quantidade")

    # 3. Criar coluna combinada PA_Torre
    df_estado["torre_pa"] = df_estado["group_user"] + " - " + df_estado["username"]

    # 4. Pivotar os dados (linhas em colunas por estado)
    df_pivot = df_estado.pivot_table(
        index="torre_pa",
        columns="estado",
        values="quantidade",
        fill_value=0
    ).reset_index()

    # 5. Gerar gráfico com Plotly
    fig_estado = px.bar(
        df_pivot,
        x="torre_pa",
        y=[col for col in df_pivot.columns if col != "torre_pa"],
        title="Total de Seriais por Status-1 ",
        labels={"value": "Quantidade", "variable": "Status-1"}, text_auto=True  ,#
        barmode="group"
    )

    #  Aplicar tons de vermelho manualmente por trace
    for trace in fig_estado.data:
        estado_nome = trace.name.lower()
        if estado_nome in custom_colors:
            trace.marker.color = custom_colors[estado_nome]

    # Layout visual
    fig_estado.update_layout(width=2000, height=1000,
         plot_bgcolor='rgba(0,0,0,0)',        # fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)',       # fundo da área externa
        font=dict(color=cor_texto_menu),    # cor dos textos do gráfico
        legend=dict(font=dict(color=cor_texto_menu)),  # legenda
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc",
            zeroline=False
        )
    )
    fig_estado.update_traces(textposition='inside', textfont_color='white', textfont_size=2500)
   
    st.plotly_chart(
        fig_estado,
        use_container_width=True,
        config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]}
    )
 # Paleta em tons de vermelho para os estados
    custom_colors1 = {
    "fif": "#C40606",
    "f": "#8B163D",
    "fifo": "#94180A",
    "fff": "#FF2A13"
}

    # 1. Garantir que a coluna 'acao' está em minúsculo
    df_filtrado["acao"] = df_filtrado["acao"].str.lower()

    # 2. Agrupar por group_user, username e acao
    df_acao = df_filtrado.groupby(["group_user", "username", "acao"]).size().reset_index(name="quantidade")

    # 3. Criar coluna combinada PA_Torre
    df_acao["torre_pa"] = df_acao["group_user"] + " - " + df_acao["username"]

    # 4. Pivotar os dados (linhas em colunas por estado)
    df_pivot = df_acao.pivot_table(
        index="torre_pa",
        columns="acao",
        values="quantidade",
        fill_value=0
    ).reset_index()

    # 5. Gerar gráfico com Plotly
    fig_acao = px.bar(
        df_pivot,
        x="torre_pa",
        y=[col for col in df_pivot.columns if col != "torre_pa"],
        title="Total de Seriais por Status-2",
        labels={"value": "Quantidade", "variable": "Status-2"},  # <- Aqui alterado
        text_auto=True,
        barmode="group"
    )

    # 6. Aplicar cores personalizadas por trace
    for trace in fig_acao.data:
        acao_nome = trace.name.lower()
        if acao_nome in custom_colors1:
            trace.marker.color = custom_colors1[acao_nome]

    # 7. Layout visual
    fig_acao.update_layout(width=2000, height=1000,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=cor_texto_menu),
        legend=dict(font=dict(color=cor_texto_menu)),
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc",
            zeroline=False
        )
    )

    fig_acao.update_traces(
        textposition='inside',
        textfont_color='white',
        textfont_size=2500
    )

    # 8. Exibir no Streamlit
    st.plotly_chart(
        fig_acao,
        use_container_width=True,
        config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]}
    )


    # Gráfico 2 - Torres Abertas/Pendentes
    df_abertos = df_filtrado[df_filtrado["status_lote"] != "fechado"]
    df2 = df_abertos.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig2 = px.bar(df2, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
                title="Torres diferente de fechado por PA", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig2.update_traces(textposition='inside', textfont_color='white',textfont_size=2500)
    fig2.update_layout(width=2000, height=1000,
        plot_bgcolor='rgba(0,0,0,0)',        # fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)',       # fundo da área externa
        font=dict(color=cor_texto_menu),    # cor dos textos do gráfico
        legend=dict(font=dict(color=cor_texto_menu)),  # legenda
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc",
            zeroline=False
        )
    )

    st.plotly_chart(fig2,  use_container_width=True,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

    # Gráfico 3 - Seriais por Torre (Fechados)
    df_fechado = df_filtrado[df_filtrado["status_lote"].str.lower() == "fechado"].copy()
    df_fechado["status_lote"] = df_fechado["status_lote"].str.lower().str.replace(" ", "_")
    df_fechado["status_lote_label"] = df_fechado["status_lote"].map(status_label_map)
    df3 = df_fechado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig3 = px.bar(df3, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
                title="Total de Seriais por PA e Torre (Fechados)", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig3.update_traces(textposition='inside', textfont_color='white',textfont_size=2500)
    fig3.update_layout(width=2000, height=1000,
        plot_bgcolor='rgba(0,0,0,0)',        # fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)',       # fundo da área externa
        font=dict(color=cor_texto_menu),    # cor dos textos do gráfico
        legend=dict(font=dict(color=cor_texto_menu)),  # legenda
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc",
            zeroline=False
        )
    )

    st.plotly_chart(fig3,  use_container_width=True)
    
    # 1. Mapeamento de status (legível)
    mapa_status = {
    "aberto": "Aberto",
    "fechado": "Fechado",
    "invalidado": "Invalidado"
    }

    df_filtrado["status_lote"] = df_filtrado["status_lote"].str.lower()
    df_filtrado["status_lote_label"] = df_filtrado["status_lote"].map(mapa_status)
    df_grouped = df_filtrado.groupby(["group_user", "username", "status_lote_label"]).size().reset_index(name="quantidade")


    # 3. Criar coluna combinada PA-Torre para eixo X
    df_grouped["PA_Torre"] = df_grouped["group_user"] + " - " + df_grouped["username"]

    # 4. Mapa de cores por status
    mapa_cores_status = {
        "Aberto": "#C40606",       # Laranja
        "Fechado": "#8B163D",      # Verde
        "Invalidado": "#94180A"    # Vermelho
    }

    # 5. Criar gráfico
    fig4 = px.bar(
        df_grouped,
        x="PA_Torre",
        y="quantidade",
        color="status_lote_label", 
        barmode="group",
        text="quantidade",
        title="Total de Seriais por PA e Torre, Separados por Status",
        labels={
            "quantidade": "Quantidade",
            "PA_Torre": "PA - Torre",
            "status_lote_label": "Status"
        },
        color_discrete_map=mapa_cores_status
    )

    # 6. Estilização
    fig4.update_traces(textposition='inside', textfont_color='white', textfont_size=2500)
    fig4.update_layout(width=2000, height=1000,
        font=dict(color=cor_texto_menu),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color=cor_texto_menu)),
        xaxis=dict(color=cor_texto_menu, showgrid=False),
        yaxis=dict(
            color=cor_texto_menu,
            showgrid=True,
            gridcolor="#444" if modo == "Escuro" else "#ccc"
        )
    )

    st.plotly_chart(fig4, use_container_width=True, config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})


    # Gráfico 5 - Invalidado
    df_Invalidado = df_filtrado[df_filtrado["status_lote"] == "invalidado"]
    df_Invalidado_agrupado = df_Invalidado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig_Invalidado = px.bar(df_Invalidado_agrupado, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
     title="Total de Seriais Invalidados por PA e Torre", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig_Invalidado.update_traces(textposition='inside', textfont_color='white',textfont_size=2500)
    fig_Invalidado.update_layout(width=2000, height=1000,
        plot_bgcolor='rgba(0,0,0,0)',        # fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)',       # fundo da área externa
        font=dict(color=cor_texto_menu),    # cor dos textos do gráfico
        legend=dict(font=dict(color=cor_texto_menu)),  # legenda
        xaxis=dict(
            color=cor_texto_menu,
            showgrid=False,
            zeroline=False
        )
    )

    st.plotly_chart(fig_Invalidado,  use_container_width=True,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

  
elif pagina == "Tabela Completa":
    # CSS para ocultar índice e scroll lateral
    df_sem_primeira = df.iloc[:, 0:]
    # Garante nomes amigáveis na tabela

    # ✅ Prepara os dados (renomeia colunas e remove 'patrimonio')
    df_tabela = df_filtrado.rename(columns={
    "username": "Torre",
    "group_user": "PA",
    "nrserie": "Nr Série",
    "estado": "Status-1",
    "acao":"Status-2"
    }).drop(columns=["patrimonio"], errors="ignore")


    cor_botao = "#000000" if modo == "Escuro" else cor_primaria
    cor_texto_botao = "#000000" if modo == "Escuro" else "#ffffff"

    st.markdown(f"""
    <style>
    .stDownloadButton > button {{
        background-color: { cor_texto_botao} !important;
        color: {cor_texto_botao} !important;
        border: 1px solid { cor_texto_botao};
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    .stDownloadButton > button:hover {{
        background-color: { cor_texto_botao} !important;
        color: white !important;
    }}
    
    
    /* Tabela geral */
    div[data-testid="stDataFrame"] div[role="grid"] {{
        background-color: {cor_texto_botao} !important;
        color: {cor_texto_botao} !important;
        border-radius: 10px;
       
    }}

    /* Cabeçalho */
    div[data-testid="stDataFrame"] thead th {{
        background-color: {cor_texto_botao} !important;
        color: {cor_texto_botao} !important;
        font-weight: bold;
        border-bottom: 1px solid #999;
    }}

    /* Células */
    div[data-testid="stDataFrame"] tbody td {{
        background-color: {cor_texto_botao} !important;
        color: {cor_texto_botao} !important;
    }}

    /* Scroll invisível */
    div[data-testid="stDataFrameScrollable"] > div:nth-child(1) {{
        overflow-x: hidden;
    }}
    </style>
""", unsafe_allow_html=True)


    # ✅ Exibe a tabela
    st.title("Tabela de Seriais Bipados")
    st.dataframe(df_tabela, use_container_width=True, height=550, hide_index=True)
    
    # ✅ Botão para exportar CSV sem 'patrimonio'
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

else:
    st.warning("⚠️ Coluna 'status' não encontrada para o gráfico de Status por Torre.")
