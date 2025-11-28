from __future__ import annotations
from pathlib import Path
import pandas as pd

# Raiz do projeto (pasta onde está este arquivo)
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"

# Nome padrão do JSON (ajuste se necessário)
DEFAULT_JSON_NAME = "Projetos de Desenvolvimento Tecnologico.json"
BRL_COLS = [
    "valorPactuado",       # <--- NOVO: 19/11
    "valorAgencia",
    "valorUnidade",
    "valorIAUPE",
]

def input_path(name: str | Path = DEFAULT_JSON_NAME) -> Path:
    """Retorna o caminho absoluto dentro de input/."""
    p = INPUT_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado em: {p}")
    return p

def carregar_json(path: str | Path | None = None) -> pd.DataFrame:
    """
    Lê o JSON (lista de objetos) e retorna um DataFrame.
    Se path for None, usa input/DEFAULT_JSON_NAME.
    """
    if path is None:
        path = input_path(DEFAULT_JSON_NAME)
    return pd.read_json(path)

def _br_to_float(serie: pd.Series) -> pd.Series:
    """
    Converte '1.234.567,89' -> 1234567.89. Aceita também numérico.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    
    serie = serie.fillna("0").astype(str)
    serie = serie.str.strip() # remove espaços e caracteres invisíveis do início ao fim
    serie = serie.str.replace(r'[^\d\.\,]', '', regex=True) # Remove qualquer coisa que não seja dígito, ponto ou vírgula

    # Cconversão BR -> Float
    serie = (
        serie.str.replace(".", "", regex=False)  # Remove separador de milhar (ponto)
             .str.replace(",", ".", regex=False) # Substitui vírgula por ponto decimal
    )
    
    return pd.to_numeric(serie, errors="coerce").fillna(0.0)

def normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que colunas monetárias estejam em float."""
    for c in BRL_COLS:
        if c in df.columns:
            df[c] = _br_to_float(df[c])
    return df

def preparar_datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte 'dataPublicacao' e cria colunas Ano/Mes/MesNome."""
    df = df.copy()

    # -------------- MODIFICAÇAO 19/11 (INÍCIO) --------------
    # Colunas de data a serem convertidas
    date_cols = ["dataPublicacao", "inicioData", "terminoData"]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    # -------------- MODIFICAÇAO 19/11 (FIM) --------------

    df["dataPublicacao"] = pd.to_datetime(df["dataPublicacao"], errors="coerce") # verificar se não é uma redundância
    df["Ano"] = df["dataPublicacao"].dt.year
    df["Mes"] = df["dataPublicacao"].dt.month
    df["MesNome"] = df["dataPublicacao"].dt.strftime("%m/%b")
    return df

# -------------- MODIFICAÇAO 26/11 (INÍCIO) --------------

"""Extrai o ano do formato 'XXX-AAAA'."""
def _extrair_ano_do_acordo(serie_acordo: pd.Series) -> pd.Series:
    serie = serie_acordo.astype(str).str.split('-').str[-1]
    # Converte para numérico e coerce erros (onde a string não é um ano)
    return pd.to_numeric(serie, errors='coerce')

# Cria uma coluna 'AnoProjeto' usando lógica sequencial (Data Publicação > InícioData > Acordo).
def imputar_data_projeto(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. Trata 'acordoConvenioNumero' para extrair o ano
    # O Ano será preenchido como NaN se a extração falhar.
    df['AnoAcordo'] = _extrair_ano_do_acordo(df['acordoConvenioNumero'])
    
    # 2. Preenche os NaNs em 'Ano' com o 'Ano' de 'InícioData' (se InícioData for válida)
    # df['InícioData'].dt.year obtém o ano do objeto datetime.
    df['Ano'] = df['Ano'].fillna(df['inicioData'].dt.year)
    
    # 3. Preenche os NaNs restantes em 'Ano' com o 'Ano' extraído do acordo
    df['Ano'] = df['Ano'].fillna(df['AnoAcordo'])
    
    # 4. Remove a coluna auxiliar e converte 'Ano' para inteiro (para visualização limpa)
    df = df.drop(columns=['AnoAcordo'], errors='ignore')
    
    # 5. Cria a categoria "Não Definido" para o agrupamento, onde o ano ainda é nulo.
    # Converte o Ano para string para poder usar 'Não Definido' na mesma coluna
    df['Ano'] = df['Ano'].fillna(9999).astype(int).astype(str).replace('9999', 'Não Definido')
    
    return df

# -------------- MODIFICAÇAO 26/11 (FIM) --------------

def agrupar_mensal(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Soma por mês (1..12) os valores da agência, unidade e IA-UPE para o ano dado."""
    df_ano = df[df["Ano"] == ano].copy()
    if df_ano.empty:
        base = pd.DataFrame({"Mes": range(1, 13)})
        base["MesNome"] = base["Mes"].apply(lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b"))
        for c in BRL_COLS:
            base[c] = 0.0
        return base

    grp = (
        df_ano.groupby(["Mes", "MesNome"], as_index=False)[BRL_COLS]
        .sum()
        .sort_values("Mes")
    )
    meses_completos = pd.DataFrame({"Mes": range(1, 13)})
    meses_completos["MesNome"] = meses_completos["Mes"].apply(
        lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b")
    )
    out = meses_completos.merge(grp, on=["Mes", "MesNome"], how="left").fillna(0.0)
    return out

def kpis_anuais(df_mes: pd.DataFrame) -> dict:
    """Totais do ano (soma dos meses) para cards."""
    return {
        "agencia": float(df_mes["valorAgencia"].sum()) if "valorAgencia" in df_mes else 0.0,
        "unidade": float(df_mes["valorUnidade"].sum()) if "valorUnidade" in df_mes else 0.0,
        "ia_upe": float(df_mes["valorIAUPE"].sum()) if "valorIAUPE" in df_mes else 0.0,
    }

def brl(v: float) -> str:
    """Formata float para BRL simples (R$ 1.234,56)."""
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"
    
# -------------- MODIFICAÇAO 19/11 (INÍCIO) --------------
# Função para filtrar, ordenar e retornar os 5 projetos mais recentes
def acordos_recentes(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    # Ordena por InícioData em ordem decrescente (mais recentes primeiro)
    df_ordenado = df_copy.sort_values(by='inicioData', ascending=False)
    
    # Retorna os últimos 5
    return df_ordenado.head(5)
# -------------- MODIFICAÇAO 19/11 (FIM) --------------
