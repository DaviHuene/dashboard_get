import streamlit as st
import pandas as pd
import requests
from io import StringIO

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

# Função para obter os dados da API com filtro de PA
def obter_resumo(pa=None):
    try:
        # Se o filtro de PA for fornecido, adicionamos o parâmetro na URL
        if pa:
            response = requests.get(f"https://www.centralretencao.com.br/inventario-api/api/v1/dash/resumo?pa={pa}")
        else:
            response = requests.get("https://www.centralretencao.com.br/inventario-api/api/v1/dash/resumo")
        
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        return response.json()  # Retorna os dados como um dicionário
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Erro ao carregar dados da API: {e}")
        return None

# Filtro de PA na barra lateral
# Lista bruta de PAs (copiada e colada como string multilinha)
lista_pas = """
CD_PAYLOG_BH
CD_PAYTEC
AG_23008_CURITIBA_PR_CORNER
AG_0565_CAMPINAS_SP_CORNER
AG_3396_NITEROI_RJ_CORNER
LAB_TECTOY_MOBYAN
AG_2093_RIO_DE_JANEIRO_RJ_CORNER
AG_4591_FEIRA_DE_SANTANA_BA_CORNER
AG_0336_TABOAO_DA_SERRA_CORNER
AG_3829_SAO_PAULO_SP_CORNER
LAB_GERTEC
AG_3554_SAO_BERNARDO_DO_CAMPO_SP_CORNER
AG_0213_JOAO_PESSOA_PB_CORNER
AG_0019_RIBEIRAO_PRETO_SP_CORNER
AG_3087_CAMPOS_DO_JORDAO_CORNER
AG_0179_JUIZ_DE_FORA_MG_CORNER
AG_0040_JUNDIAI_SP_CORNER
AG_3650_SANTOS_SP_CORNER
40739_AG_0157_INDAIATUBA_SP_CORNER
AG_3294_SANTO_ANDRE_SP_CORNER
AG_4036_JABOATAO_GUARARAPES_PE_CORNER
AG_0215_PETROPOLIS_RJ_CORNER
AG_3524_BELEM_PA_CORNER
AG_0189_CAXIAS_DO_SUL_RS_CORNER
AG_1634_SP_CAPAO_REDONDO_SP_CORNER
19290_AG_2140_CAMPO_GRANDE_MS_CORNER
AG_4279_FORTALEZA_CE_CORNER
AG_3747_SALVADOR_BA_CORNER
19166_AG_0162_LONDRINA_PR_CORNER
AG_2135_SALVADOR_BA_CORNER
AG_3520_UBERABA_MG_CORNER
AG_4375_SANTAREM_PA_CORNER
AG_0186_MACEIO_AL_CORNER
AG_4008__PETROLINA_PE_CORNER
AG_3153_GENERAL_OSORIO_RJ_CORNER
AG_4017_CARUARU_PE_CORNER
AG_3176_JOINVILLE_SC_(CORNER)
AG_3253_PORTO_VELHO_RO_CORNER
AG_2185_RONDONOPOLIS_MT_CORNER
AG_0341_BARUERI_SP_CORNER
AG_3348_GOIANIA_GO_CORNER
AG_3131_FLORIANOPOLIS_SC_CORNER
AG_2132_TAGUATINGANORTE_CORNER
AG_3311_SAO_JOSE_DO_RIO_PRETO_SP_CORNER
AG_3381_RIO_DE_JANEIRO_RJ_CORNER
AG_0080_NATAL_RN_CORNER
AG_3059_BLUMENAU_SC_CORNER
AG_0135_SAO_VICENTE_SP_CORNER
18775_AG_0087_MOGI_DAS_CRUZES_SP_CORNER
AG_0001_CENTRAL_SP_CORNER
AG_4541_MARINGA_PR_CORNER
AG_0090_AMERICANA_SP_CORNER
AG_0787_RIO_DE_JANEIRO_RJ__CORNER
AG_4156_CABO_DE_SANTO_AGOSTINHO_PE_CORNE
AG_3067_BRASILIA_DF_CORNER
AG_3757_RECIFE_PE_CORNER
AG_1064_CANOAS_RS_CORNER
AG_3273_MANAUS_AM_CORNER
AG_3488_CONTAGEM_MG_CORNER
AG_3108_CORONEL_FABRICIANO_MG_CORNER
AG_0566_SOROCABA_SP_CORNER
AG_0201_SAO_PAULO_SP_CORNER
AG_2307__CALHAU_SÃO_LUIS_CORNER
AG_3132_FORTALEZA_CE_CORNER
AG_4281_SAO_PAULO_SP_CORNER
AG_0005_BRAS_SP_CORNER
AG_0142_DIADEMA_SP_CORNER
AG_0013_LIMEIRA_SP_CORNER
AG_0277_COTIA_SP_CORNER
AG_3020_ANGRA_DOS_REIS_RJ_CORNER
AG_3504_MONTES_CLAROS_MG_CORNER
AG_3704_LAURO_DE_FREITAS_BA_CORNER
AG_3412_SAO_PAULO_SP_CORNER
AG_0140_GUARULHOS_SP_CORNER
18596_AG_4254_SAO_PAULO_SP_CORNER
AG_1320_TAUBATE_SP_CORNER
AG_1658_BELO_HORIZONTE_MG_CORNER
AG_3932_PALMAS_TO_CORNER
AG_3346_VILA_VELHA_ES__CORNER
AG_4168_SINOP_MT_CORNER
AG_4619_NOVA_IGUACU_RJ_CORNER
AG_0342_CARAGUATATUBA_SP_CORNER
AG_3015_ANAPOLIS_GO_CORNER
AG_3547_OSASCO_SP_CORNER
AG_3310_SAO_JOSE_DOS_CAMPOS_SP_CORNER
AG_0805_CABO_FRIO_RJ_CORNER
AG_3466_CUIABA_MT_CORNER
AG_3026_ARACAJU_SE_CORNER
AG_3122_DUQUE_DE_CAXIAS_RJ_CORNER
AG_0202_RIO_DE_JANEIRO_RJ_(CORNER)
AG_1522_SAO_JOAO_DE_MERITI_RJ_CORNER
AG_3350_RIO_DE_JANEIRO_RJ_CORNER
AG_3686_RECIFE_PE_CORNER
19360_AG_0008_ARAÇATUBA_SP_CORNER
AG_0010_CAMPINAS_SP_CORNER
AG_3490_DIVINOPOLIS_MG_CORNER
AG_3154_IPATINGA_MG_CORNER
AG_0041_PIRACICABA_SP_CORNER
AG_0044_ARARAQUARA_SP_CORNER
AG_3352_VOLTA_REDONDA_RJ_CORNER
AG_0100_TERESINA_PI_CORNER
AG_3477_BELO_HORIZONTE_MG_CORNER
AG_4039_PAULISTA_PE_CORNER
AG_3121_DOURADOS_MS_CORNER
AG_3240_PELOTAS _RS_CORNER
AG_3270_RIO_BRANCO_AC_CORNER
AG_4182_CAMPINA_GRANDE_PB__CORNER
AG_1290_PONTA_GROSSA_PR_CORNER
AG_3344_VARGINHA_MG_CORNER
AG_3058_BETIM_MG_CORNER
AG_3342_UBERLANDIA_MG_CORNER
AG_3391_SAO_GONCALO_RJ_CORNER
AG_4416_SANTA_LUZIA_MG_CORNER
AG_3436_BOA_VISTA_RR_CORNER
AG_3345_VITÓRIA_ES_CORNER
AG_3601_FOZ_DO_IGUACU_PR_CORNER
""".strip().splitlines()

# Remover espaços e ordenar
lista_pas = sorted([pa.strip() for pa in lista_pas])

# Inserir "Todos" no topo
lista_opcoes = ["Todos"] + lista_pas

# Componente multiselect com Streamlit
filtro_pa = st.sidebar.selectbox(
    "🔍 Selecione o PA",
    options=lista_opcoes,
    index=0  # "Todos" como padrão
)
if filtro_pa == "Todos":
    dados_resumo = obter_resumo()  # dados gerais
else:
    dados_resumo = obter_resumo(pa=filtro_pa)



# Verificar se os dados foram carregados corretamente
if dados_resumo:
    # Extraindo os dados
    total_torres = dados_resumo.get("total_torres", 0)
    total_lotes = dados_resumo.get("total_lotes", 0)
    total_seriais = dados_resumo.get("total_seriais", 0)
    pct_fechados = dados_resumo.get("pct_fechados", 0)
    pct_abertos = dados_resumo.get("pct_abertos", 0)
    pct_invalidados = dados_resumo.get("pct_invalidados", 0)

    # Exibindo os dados no formato de cards
    st.markdown(f"""
    <div style="display:flex;gap:100px;margin-top:20px;margin-bottom:30px;flex-wrap:wrap;justify-content:center;">
         <div style="background:{cor_fundo};padding:20px 40px;border-radius:20px;border:3px solid {cor_primaria};">
            <h2 style="margin:0;color:{cor_texto_menu};font-size:28px;">📦 Total de Lotes</h2>
            <p style="font-size:80px;margin:10px 0;color:{cor_texto_menu};"><strong>{total_lotes}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:20px 40px;border-radius:20px;border:3px solid {cor_primaria};">
            <h2 style="margin:0;color:{cor_texto_menu};font-size:28px;">📦 Total de Seriais</h2>
            <p style="font-size:80px;margin:10px 0;color:{cor_texto_menu};"><strong>{total_seriais}</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:20px 40px;border-radius:20px;border:3px solid {cor_primaria};">
            <h2 style="margin:0;color:{cor_texto_menu};font-size:28px;">📈 Lotes Fechados</h2>
            <p style="font-size:80px;margin:10px 0;color:{cor_texto_menu};"><strong>{pct_fechados}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:20px 40px;border-radius:20px;border:3px solid {cor_primaria};">
            <h2 style="margin:0;color:{cor_texto_menu};font-size:28px;">🟡 Lotes Abertos</h2>
            <p style="font-size:80px;margin:10px 0;color:{cor_texto_menu};"><strong>{pct_abertos}%</strong></p>
        </div>
        <div style="background:{cor_fundo};padding:20px 40px;border-radius:20px;border:3px solid {cor_primaria};">
            <h2 style="margin:0;color:{cor_texto_menu};font-size:28px;">❌ Lotes Invalidados</h2>
            <p style="font-size:80px;margin:10px 0;color:{cor_texto_menu};"><strong>{pct_invalidados}%</strong></p>
        </div>
    </div>
""", unsafe_allow_html=True)

else:
    st.warning("⚠️ Não foi possível carregar os dados do painel.")
# API para obter os lotes
# API para obter os lotes
API_URL2 = "http://192.168.0.216/inventario-api/api/v1/dash/cache/"

# ⚠️ Verificação se nenhum PA foi selecionado
if not filtro_pa:
    st.warning("⚠️ Nenhum PA selecionado. Selecione pelo menos um para continuar.")
    st.stop()

try:
    response = requests.get(API_URL2, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()

    # Verifica se existe pelo menos um 'status_lote' nos lotes
    if not any("status" in lote for lote in data):
        st.error("⚠️ Nenhum lote encontrado.")
        st.stop()

except Exception:
    st.error("⚠️ Nenhum dado foi carregado. A API pode estar fora do ar ou sem dados disponíveis.")
    st.stop()
