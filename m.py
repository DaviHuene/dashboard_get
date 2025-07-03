import streamlit as st
from app.styles import aplicar_tema
from app.api import carregar_dados_api
from app.graficos import exibir_indicadores, exibir_data_atualizacao, titulo_dashboard
from app.tabela import exibir_tabela_completa
from app.filtros import aplicar_filtros, criar_menu_filtros

def main():
    st.set_page_config(page_title="Painel Inventário", layout="wide")

    modo, cores = aplicar_tema()

    pagina = st.sidebar.selectbox("Escolha a página", ["Dashboard", "Tabela Completa"])

    data = carregar_dados_api()
    if not data:
        st.error("⚠️ Nenhum dado foi carregado. A API pode estar fora do ar ou sem dados disponíveis.")
        return

    df = aplicar_filtros(data)
    df_filtrado = criar_menu_filtros(df)

    if pagina == "Dashboard":
        exibir_data_atualizacao(cores["fundo"])
        titulo_dashboard(df_filtrado, modo, cores["fundo"], cores["texto_menu"])
        exibir_indicadores(df, df_filtrado, modo, cores["fundo"], cores["primaria"], cores["texto_menu"])
    else:
        exibir_tabela_completa(df_filtrado, modo, cores)

if __name__ == "__main__":
    main()
