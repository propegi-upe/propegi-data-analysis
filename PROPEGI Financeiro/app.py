import streamlit as st

# Adiciona um título ao app principal
st.set_page_config(page_title="PROPEGI Financeiro", page_icon="../../images/upeLogo.png" ,layout="wide")
st.title("PROPEGI Financeiro: Data Analysis Dashboard")

# Imagem para a barra lateral
# st.sidebar.image("images/upeLogo.png", width=150)
with st.sidebar:
    # 1. Cria três colunas na barra lateral
    # A coluna do meio (col2) será mais larga que as laterais (col1, col3)
    col1, col2, col3 = st.columns([1, 3, 1])

    # 2. Coloca a imagem na coluna do meio (col2)
    with col2:
        st.image("images/upeLogo.png", width=150)

analise1 = st.Page(
    page="pages/01_analise1_comparativa.py",
    title="Análise 1 - Comparativo de Valores das Folhas por Projeto (Mês/Ano)",
    icon=":material/analytics:",
    default=True, # Define esta como a página inicial
)

analise2 = st.Page(
    page="pages/02_analise2_somatorio.py",
    title="Análise 2 - Somatório de Valores das Folhas por Projeto",
    icon=":material/bar_chart:",
)

analise3 = st.Page(
    page="pages/03_analise3_total_mensal.py",
    title="Análise 3 - Total Mensal de Todos os Projetos",
    icon=":material/bar_chart_4_bars:",
)

analise4 = st.Page(
    page="pages/04_analise_mensal_taxa_plano.py",
    title="Análise 4 - Mensal por Taxa/Plano",
    icon=":material/cadence:",
)

analise5 = st.Page(
    page="pages/05_analise_periodo_taxa_plano.py",
    title="Análise 5 - Período por Taxa/Plano",
    icon=":material/finance:",
)

# Cria a navegação com uma lista de páginas
pg = st.navigation(
    {
        "Análises": [analise1, analise2, analise3, analise4, analise5],
    }
)

# Executa a página selecionada
pg.run()
