# projeto.py — leitura robusta + gráfico simples
from pathlib import Path
import re, pandas as pd, streamlit as st
import plotly.express as px

st.set_page_config(page_title="Projetos de Desenvolvimento Tecnológico", layout="wide")
st.title("📊 Projetos de Desenvolvimento Tecnológico")

# 1) Caminho automático para o CSV (baseado neste arquivo)
BASE = Path(__file__).resolve().parent
CSV_PATH = (BASE / "../Projeto de Desenvolvimento Tecnologico/output/dados_tratados.csv").resolve()

#Onde esta localizado o arquivo
st.caption(f"CSV: {CSV_PATH}") 

# 2) Utilitário: 'R$ 10.000,00' -> 10000.00
def br_to_float(x):
    if pd.isna(x): return 0.0
    if isinstance(x, (int, float)): return float(x)
    s = re.sub(r"[^\d,.-]", "", str(x)).replace(".", "").replace(",", ".")
    try: return float(s)
    except: return 0.0

# 3) Leitura
if not CSV_PATH.exists():
    st.error("❌ CSV não encontrado nesse caminho acima.")
    st.stop()

df = pd.read_csv(CSV_PATH, encoding="utf-8")
st.subheader("👀 Amostra dos dados")
st.dataframe(df.head(), use_container_width=True)

# 4) Detecta colunas de valor e converte
val_cols_candidatas = ["Valor IA-UPE", "Valor agência", "Valor unidade"]
val_cols = [c for c in val_cols_candidatas if c in df.columns]
for c in val_cols:
    df[c] = df[c].apply(br_to_float)























