import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from app.filtros import aplicar_filtros, criar_menu_filtros
from app.api import carregar_dados_api
def titulo_dashboard(df_filtrado, modo, cor_fundo, cor_texto_menu):
    st.title("Painel Analítico de Seriais Bipados")

def exibir_data_atualizacao(cor_fundo):
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
   

def exibir_indicadores(df, df_filtrado, modo, cor_fundo, cor_primaria, cor_texto_menu):
    tons_vermelho = ["#c70303", "#9b0000", "#c23737", "#d14a4a", "#d80202", "#ef9a9a", "#f44336",
                     "#e53935", "#d32f2f", "#b71c1c", "#ff6f61", "#e57373", "#f28b82", "#a30000", "#ff4d4d", "#cc0000"]

    status_label_map = {
        "fechado": "Fechado",
        "aberto": "Aberto",
        "cancelado": "Cancelado",
        "aguardando_validação": "Aguardando Validação",
        "em_andamento": "Em Andamento",
        "pendente": "Pendente",
        "invalidado": "Invalidado"
    }

    df_lotes = df[["lote_id", "status_lote", "username", "group_user"]].drop_duplicates()
    df_lotes = df[["lote_id", "status_lote"]].drop_duplicates()
    df_lotes["status_lote"] = df_lotes["status_lote"].str.strip().str.lower()

    # Contagens
   
    # Exemplo de gráfico básico:
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
    

    usuarios = sorted(df_filtrado["username"].dropna().unique())
    mapa_cores_username = {user: tons_vermelho[i % len(tons_vermelho)] for i, user in enumerate(usuarios)}

    # Indicadores visuais
    st.markdown(f"""
    <div style="display:flex;gap:40px;margin-top:10px;margin-bottom:20px;flex-wrap:wrap;">
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">🏢 Total de Torres</h3>
            <p style="font-size:22px;margin:5px 0;color:{cor_texto_menu};"><strong>{total_torres}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:15px;border-radius:10px;border:1px solid {cor_primaria};">
            <h3 style="margin:0;color:{cor_texto_menu};">📦  Total de Lotes</h3>
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

        fig1.update_traces(marker_color="#c70101", textposition="inside", textfont_size=14)

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
        fig1.update_traces(textposition='inside', textfont_color='white',textfont_size=50)
        st.plotly_chart(fig1, use_container_width=False,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})


 

    # Gráfico 2 - Torres Abertas/Pendentes
    df_abertos = df_filtrado[df_filtrado["status_lote"] != "fechado"]
    df2 = df_abertos.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig2 = px.bar(df2, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
                title="Torres diferente de fechado por PA", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig2.update_traces(textposition='inside', textfont_color='white',textfont_size=50)
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

    st.plotly_chart(fig2, use_container_width=False,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

    
    # Criar gráfico com colunas separadas para cada status
   

    
    # Gráfico 5 - Invalidado
    df_Invalidado = df_filtrado[df_filtrado["status_lote"] == "invalidado"]
    df_Invalidado_agrupado = df_Invalidado.groupby(["group_user", "username"]).size().reset_index(name="quantidade")
    fig_Invalidado = px.bar(df_Invalidado_agrupado, x="group_user", y="quantidade", color="username", barmode="group",text='quantidade',
     title="Total de Seriais Invalidados por PA e Torre", color_discrete_map=mapa_cores_username,labels={"group_user": "PA", "total_seriais": "Total de Seriais", "status_lote_label": "Status","username":"Torre"})
    fig_Invalidado.update_traces(textposition='inside', textfont_color='white',textfont_size=50)
    fig_Invalidado.update_layout(
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

    st.plotly_chart(fig_Invalidado, use_container_width=False,config={"displaylogo": False, "modeBarButtonsToRemove": ["toggleFullscreen"]})

    
    
    
    
    
    
    
    
    
