import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Projetos de Desenvolvimento Tecnológico", layout="wide")
st.title("📊 Projetos de Desenvolvimento Tecnológico")

# Caminho do CSV --> Ficar atento ao caminho do arquivo caso aja problemas
BASE = Path(__file__).resolve().parent
CSV_PATH = (BASE / "../Projeto de Desenvolvimento Tecnologico/output/dados_tratados.csv").resolve()
st.caption(f"CSV: {CSV_PATH}")

# Leitura  -> Para o Streamlit Ler o que tem no arquivo csv
df = pd.read_csv(CSV_PATH, sep=None, engine="python", encoding="utf-8-sig")

# Mostrando a Tabela CSV Completa --> OBS: Alem de df.head() (mostras as 5 primeiras linhas). Deve-se usar so df.
st.subheader("👀 Amostra dos dados")
st.dataframe(df, use_container_width=True)  

# Colunas exatas com acentos
COL_DATA = "Data publicação"
COLS_VAL = ["Valor agência", "Valor unidade", "Valor IA-UPE"]

#  Tratamento de datas/valores 
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)
df = df.dropna(subset=[COL_DATA]).copy()

for c in COLS_VAL:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

df["_ano"] = df[COL_DATA].dt.year.astype(int)
df["_mes"] = df[COL_DATA].dt.to_period("M")
df["_mes_label"] = df["_mes"].dt.strftime("%b-%y").str.capitalize()

#  Seleciona ano 
anos = sorted(df["_ano"].unique().tolist())
ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos)-1)

#  Agrega por mês 
df_ano = df[df["_ano"] == int(ano_sel)]
mensal = (
    df_ano.groupby("_mes")[COLS_VAL].sum()
    .reset_index()
    .sort_values("_mes")
)
mensal["_mes_label"] = mensal["_mes"].dt.strftime("%b-%y").str.capitalize()

#  Deixando em Formato longo 
mensal_long = mensal.melt(
    id_vars=["_mes", "_mes_label"],
    value_vars=COLS_VAL,
    var_name="Tipo",
    value_name="Valor (R$)"
)

#  Gráfico 
st.subheader(f"Comparativo mensal: Agência x Unidade x IAUPE — {ano_sel}")
fig = px.line(mensal_long, x="_mes_label", y="Valor (R$)", color="Tipo", markers=True)
fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ===== Resumo em cards (logo após o gráfico) =====
def fmt_brl(x: float) -> str:
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown("### 📌 Resumo do ano")

# médias mensais por tipo (usa a tabela mensal agregada)
medias = mensal[["Valor agência", "Valor unidade", "Valor IA-UPE"]].mean()

# mês de maior repasse total (somando Agência + Unidade + IA-UPE)
totais_mes = mensal[["Valor agência", "Valor unidade", "Valor IA-UPE"]].sum(axis=1)
i_pico = int(totais_mes.idxmax())
mes_pico_label = mensal.loc[i_pico, "_mes_label"]
valor_pico = float(totais_mes.loc[i_pico])

# cards ---> Utilize essa Nomenclatura
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Média mensal — Agência", fmt_brl(medias["Valor agência"]))
with c2:
    st.metric("Média mensal — Unidade", fmt_brl(medias["Valor unidade"]))
with c3:
    st.metric("Média mensal — IA-UPE", fmt_brl(medias["Valor IA-UPE"]))
with c4:
    st.metric(f"Pico do ano — {mes_pico_label}", fmt_brl(valor_pico))















