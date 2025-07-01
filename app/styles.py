# app/styles.py
import streamlit as st

def aplicar_tema():
    st.sidebar.title("Menu")
    modo = st.sidebar.radio("🌗 Tema", ["Claro", "Escuro"], horizontal=True)

    if modo == "Claro":
        cores = {
            "menu": "#fcdddd",
            "texto_menu": "#000000",
            "fundo": "#ffffff",
            "primaria": "#c70101",
            "input": "#ffffff"
        }
    else:
        cores = {
            "menu": "#272727",
            "texto_menu": "#FFFFFF",
            "fundo": "#121212",
            "primaria": "#c70101",
            "input": "#202020"
        }

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background:{cores['fundo']}; color: {cores['texto_menu']}; }}
        [data-testid="stSidebar"] {{ background-color: {cores['menu']}; color: {cores['texto_menu']}; border-right: 3px solid {cores['primaria']}; }}
        [data-testid="stMarkdownContainer"] *, .stText, .stMarkdown, .stDataFrame, label,
        h1, h2, h3, h4, h5, h6, p, div, span, td{{ color: {cores['texto_menu']} !important; }}
        div[data-baseweb="select"] > div {{ border: 2px solid {cores['primaria']} !important; border-radius: 10px !important; background-color: {cores['input']} !important; }}
        div[data-baseweb="select"] span {{ color: {cores['menu']} !important; font-weight: bold; }}
        .stButton > button {{ background-color: {cores['primaria']}; color: white; border: none; border-radius: 6px; }}
        .stMultiSelect,.stDateInput {{ color: {cores['primaria']} !important; }}
        .selectbox[data-baseweb="menu"] .selectbox[role="option"]:hover {{ color: {cores['primaria']} !important; background-color: {cores['input']} !important; }}
        .selectbox{{ color: {cores['primaria']} !important; background-color: {cores['input']} !important; }}
        .stTabs [role="tab"] {{ color: {cores['input']} !important; background-color: {cores['input']} !important; }}
        </style>
    """, unsafe_allow_html=True)

    return modo, cores
