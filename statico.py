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






modo = st.radio("🌗 Tema",  ["Claro", "Escuro"], horizontal=True)


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
 /* Container do radio */
[data-testid="stRadio"] {{
    display: flex;
    justify-content:first baseline
    padding: 10px;
    margin-bottom: 40px;
    background-color:  {cor_menu} ;
    border-radius: 12px;
    border: 2px solid {cor_primaria}
   
}}


    .selectbox[data-baseweb="menu"] .selectbox[role="option"]:hover {{
   color: {cor_primaria} !important;
    background-color: {cor_input} !important;
        }}
    .selectbox{{
       color: {cor_primaria} !important;
    background-color: {cor_input} !important;
    }}
    .stTabs [role="tab"] {{
        color: {cor_input} !important;
        background-color: {cor_input} !important;
    }}
    </style>
""", unsafe_allow_html=True)

API_URL = "http://192.168.0.214/inventario-api/api/v1/dash"
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
                                    "acao":None
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

else:
    tem_aberto = False

   


# Filtros de Torre e Status e PA
pa = sorted(df["group_user"].dropna().unique().tolist())
torres = sorted(df["username"].dropna().unique().tolist())
status = sorted(df["status_lote"].dropna().unique().tolist())

# Aplicar todos os filtros, incluindo PA
# Filtragem automática: remover registros com campos vazios críticos
df_filtrado = df[
    df["group_user"].notna() &
    df["username"].notna() &
    df["status_lote"].notna()
].copy()


if  "Dashboard":
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
           <div style="background:{cor_fundo};">
            <h3>🕒 Atualizado em: {data_atualizacao}</h3>
        </div>""",unsafe_allow_html=True)
    st.title("Painel Analítico de Seriais Bipados")
    
    # Base completa sem filtro (para contagem real de lotes)
    df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
    df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

    # Contagens
    config = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d",
        "hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines", "sendDataToCloud", "toggleHover"
    ]
}

 
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
    <div style="display:flex;gap:60px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🏢 Total de Torres</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_torres}</strong></p>
        </div>
         <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦 Total de Lotes</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_caixas}</strong></p>
        </div>
          <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
             <h3 style="margin:0;color:{cor_texto_menu};">📦 Total de Seriais</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_seriais}</strong></p>
        </div>
          <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📈 Lotes Fechados</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_fechados}%</strong></p>
        </div>
             <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
        <h3 style="margin:0;color:{cor_texto_menu};">🟡 Lotes Abertos</h3>
        <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{percentual_aberto}%</strong></p>
    </div>
         <div style="background:{cor_fundo};padding:30px;border-radius:10px;border:1px solid {cor_primaria};">
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
    @st.cache_data(ttl=300)
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

    # 📊 Filtrar os status desejados
    df_status = df_lotes[df_lotes["status_lote"].isin(["fechado", "aberto", "invalidado"])]

    # 🔀 Criar coluna combinada: PA + Torre
    df_status["torre_pa"] = df_status["group_user"] + " - " + df_status["username"]

    # 🧮 Agrupar por torre_pa e status
    df_agrupado = df_status.groupby(["torre_pa", "status_lote"]).size().reset_index(name="quantidade")
    df_totais = df_status.groupby("torre_pa").size().reset_index(name="total_lotes")

    # ➗ Calcular percentual
    df_percentual = pd.merge(df_agrupado, df_totais, on="torre_pa")
    df_percentual["percentual"] = round((df_percentual["quantidade"] / df_percentual["total_lotes"]) * 100, 2)
    df_percentual["status_lote"] = df_percentual["status_lote"].str.capitalize()
    df_percentual["percentual"] = df_percentual["percentual"].astype(str) + "%"
        
    fig = px.bar(
        df_percentual,
        x="torre_pa",
        y="percentual",
        color="status_lote",
        text="percentual",
        barmode="stack",
        title=" Percentual de Lotes por Status, Torre e PA",
        labels={"torre_pa": "Torre - PA", "percentual": "%", "status_lote": "Status"},
        color_discrete_map={
            "Fechado": "#dd1d1d",
            "Aberto": "#7a0101",
            "Invalidado": "#4b0b04"
        }
    )

    fig.update_layout(
        yaxis_title="Percentual (%)",
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=cor_texto_menu),
        legend=dict(font=dict(color=cor_texto_menu)),
        xaxis=dict(color=cor_texto_menu),
        yaxis=dict(color=cor_texto_menu, gridcolor="#444" if modo == "Escuro" else "#ccc")
    )

    fig.update_traces(textposition="inside", textfont_size=18)
    fig.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
    # ▶️ Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True, config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })

        # 📦 Garantir colunas necessárias
    colunas_necessarias = ["caixa_id", "username", "group_user", "status_lote"]
    faltando = [col for col in colunas_necessarias if col not in df_filtrado.columns]

    if faltando:
        st.warning(f"⚠️ Colunas faltando no DataFrame: {', '.join(faltando)}")
    else:
        # 🔄 Remover duplicatas por caixa única
        df_caixas = df_filtrado.drop_duplicates(subset=["caixa_id", "username", "group_user", "status_lote"])

        # ✅ Filtrar apenas caixas de lotes fechados
        df_fechadas = df_caixas[df_caixas["status_lote"] == "fechado"]

        # 🏷️ Criar coluna combinada "Torre - PA"
        df_fechadas["torre_pa"] = df_fechadas["username"] + " - " + df_fechadas["group_user"]

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

        fig1.update_traces(marker_color="#c70101", textposition="inside", textfont_size=18)

        fig1.update_layout(
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
        fig1.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)

        fig1.update_traces(textposition='inside', textfont_color='white',textfont_size=18)
        st.plotly_chart(fig1, use_container_width=False,config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })


 
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
        title="Total de Seriais por Estado ",
        labels={"value": "Quantidade", "variable": "Estado"}, text_auto=True  ,#
        barmode="group"
    )

    #  Aplicar tons de vermelho manualmente por trace
    for trace in fig_estado.data:
        estado_nome = trace.name.lower()
        if estado_nome in custom_colors:
            trace.marker.color = custom_colors[estado_nome]

    # Layout visual
    fig_estado.update_layout(
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
    fig_estado.update_traces(textposition='inside', textfont_color='white', textfont_size=18)
   
    st.plotly_chart(
        fig_estado,
        use_container_width=True,
        config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]}
    )

    # Gráfico 2 - Torres Abertas/Pendentes
    df_abertos = df_filtrado[df_filtrado["status_lote"] != "fechado"]
    df2 = df_abertos.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig2 = px.bar(df2, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
                title="Torres diferente de fechado por PA", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig2.update_traces(textposition='inside', textfont_color='white',textfont_size=18)
    fig2.update_layout(
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
   
    fig2.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
    st.plotly_chart(fig2, use_container_width=False,config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })

    # Gráfico 3 - Seriais por Torre (Fechados)
    df_fechado = df_filtrado[df_filtrado["status_lote"].str.lower() == "fechado"].copy()
    df_fechado["status_lote"] = df_fechado["status_lote"].str.lower().str.replace(" ", "_")
    df_fechado["status_lote_label"] = df_fechado["status_lote"].map(status_label_map)
    df3 = df_fechado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig3 = px.bar(df3, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
                title="Total de Seriais por PA e Torre (Fechados)", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig3.update_traces(textposition='inside', textfont_color='white',textfont_size=18)
    fig3.update_layout(
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
    fig3.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
  
    st.plotly_chart(fig3, use_container_width=False)
    
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
    fig4.update_traces(textposition='inside', textfont_color='white', textfont_size=18)
    fig4.update_layout(
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
    fig4.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
  
    st.plotly_chart(fig4, use_container_width=True, config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })


    # Gráfico 5 - Invalidado
    df_Invalidado = df_filtrado[df_filtrado["status_lote"] == "invalidado"]
    df_Invalidado_agrupado = df_Invalidado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig_Invalidado = px.bar(df_Invalidado_agrupado, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
     title="Total de Seriais Invalidados por PA e Torre", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig_Invalidado.update_traces(textposition='inside', textfont_color='white',textfont_size=18)
    fig_Invalidado.update_layout(
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
    fig_Invalidado.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
  
    st.plotly_chart(fig_Invalidado, use_container_width=False,config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })

    # Gráfico de Pizza
    col_p1, col_p2 = st.columns(2)
    df_pizza = df_filtrado.groupby("username").size().reset_index(name="total_seriais")
    df_pizza_group = df_filtrado.groupby(["group_user", "username"]).size().reset_index(name="total_seriais")

    # Preencher com valores fictícios se estiver vazio
    if df_pizza.empty:
        df_pizza = pd.DataFrame({
            "username": ["Sem Dados"],
            "total_seriais": [1]
            
        })

    if df_pizza_group.empty:
        df_pizza_group = pd.DataFrame({
            "group_user": ["Sem Dados"],
            "username": ["Sem Dados"],
            "total_seriais": [1]
        })

    with col_p1:
        fig_pizza = px.pie(
        df_pizza, names="username", values="total_seriais",
            title="Seriais por Torre (Total)", hole=0.3,
            color="username", color_discrete_map=mapa_cores_username,
            labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status", "username": "Torre"})
        fig_pizza.update_traces(textinfo='percent+label')
        fig_pizza.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=18), legend_title="Status")
        fig_pizza.update_layout(
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
        fig_pizza.update_layout(
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)
   
        st.plotly_chart(fig_pizza, use_container_width=False,config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })
        
    with col_p2:
        fig_pizza2 = px.sunburst(
        df_pizza_group, path=["group_user", "username"], values="total_seriais",
        title="Distribuição de Seriais por PA e Torre",
        color="username", color_discrete_map=mapa_cores_username,
        labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status", "username": "Torre"})
        fig_pizza2.update_layout(width=1000, height=400, xaxis_tickfont=dict(size=18), legend_title="Status")
        fig_pizza2.update_layout(
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
       
        fig_pizza2.update_traces(marker=dict(colors=tons_vermelho),  hoverinfo='label+value+percent entry',
    insidetextorientation='radial')
        fig_pizza2.update_layout(uirevision='static',
    dragmode=False,                     # desativa pan/zoom via mouse
    xaxis_fixedrange=True,             # desativa zoom eixo X
   yaxis_fixedrange=True   ,legend_itemclick=False,
    legend_itemdoubleclick=False          # desativa zoom eixo Y
)# força o uso do seu mapa
        st.plotly_chart(fig_pizza2, use_container_width=False,config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["toggleFullscreen"],"displayModeBar": False
    })

else:
    st.warning("⚠️ Coluna 'status' não encontrada para o gráfico de Status por Torre.")