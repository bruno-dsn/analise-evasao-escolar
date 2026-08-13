from __future__ import annotations

from pathlib import Path
from typing import IO

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "ano",
    "unidade_geografica",
    "nivel_geografico",
    "localizacao",
    "dependencia",
    "taxa_aprovacao",
    "taxa_reprovacao",
    "taxa_abandono",
}

COLUNAS_TAXA = ["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]

COLUNAS_CHAVE = [
    "ano",
    "unidade_geografica",
    "nivel_geografico",
    "localizacao",
    "dependencia",
]


def carregar_dados(origem: str | Path | IO[bytes]) -> pd.DataFrame:
    """Carrega e valida o CSV processado das taxas de rendimento escolar."""
    dados = pd.read_csv(origem)
    faltantes = COLUNAS_OBRIGATORIAS - set(dados.columns)
    if faltantes:
        nomes = ", ".join(sorted(faltantes))
        raise ValueError(f"O arquivo não contém as colunas obrigatórias: {nomes}.")

    dados = dados[list(COLUNAS_CHAVE) + COLUNAS_TAXA].copy()
    dados["ano"] = pd.to_numeric(dados["ano"], errors="coerce")
    if dados["ano"].isna().any():
        raise ValueError("A coluna ano contém valores que não são numéricos.")
    dados["ano"] = dados["ano"].astype(int)

    for coluna in ["unidade_geografica", "nivel_geografico", "localizacao", "dependencia"]:
        dados[coluna] = dados[coluna].astype("string").str.strip()

    for coluna in COLUNAS_TAXA:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    valores_validos = dados[COLUNAS_TAXA].stack().dropna().between(0, 100)
    if not valores_validos.all():
        raise ValueError("As taxas precisam estar entre 0 e 100.")

    if dados.duplicated(COLUNAS_CHAVE).any():
        raise ValueError("O arquivo contém recortes geográficos duplicados.")

    if dados[COLUNAS_TAXA].notna().all(axis=1).sum() == 0:
        raise ValueError("O arquivo não contém linhas completas para análise.")

    return dados.sort_values(COLUNAS_CHAVE).reset_index(drop=True)


def somente_linhas_completas(dados: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas linhas com as três taxas publicadas."""
    return dados.dropna(subset=COLUNAS_TAXA).copy()


def resumo_qualidade(dados: pd.DataFrame) -> dict[str, int | float]:
    """Resume cobertura, ausências e consistência aritmética da base."""
    completas = dados[COLUNAS_TAXA].notna().all(axis=1)
    soma_taxas = dados.loc[completas, COLUNAS_TAXA].sum(axis=1)
    inconsistentes = (soma_taxas.sub(100).abs() > 0.2).sum()

    return {
        "linhas": int(len(dados)),
        "linhas_completas": int(completas.sum()),
        "cobertura_pct": float(completas.mean() * 100),
        "celulas_ausentes": int(dados[COLUNAS_TAXA].isna().sum().sum()),
        "linhas_inconsistentes": int(inconsistentes),
        "duplicidades": int(dados.duplicated(COLUNAS_CHAVE).sum()),
    }
