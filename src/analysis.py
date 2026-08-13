from __future__ import annotations

import pandas as pd

from src.data import somente_linhas_completas


UF_REGIAO = {
    "Acre": "Norte",
    "Amapá": "Norte",
    "Amazonas": "Norte",
    "Pará": "Norte",
    "Rondônia": "Norte",
    "Roraima": "Norte",
    "Tocantins": "Norte",
    "Alagoas": "Nordeste",
    "Bahia": "Nordeste",
    "Ceará": "Nordeste",
    "Maranhão": "Nordeste",
    "Paraíba": "Nordeste",
    "Pernambuco": "Nordeste",
    "Piauí": "Nordeste",
    "Rio Grande do Norte": "Nordeste",
    "Sergipe": "Nordeste",
    "Distrito Federal": "Centro-Oeste",
    "Goiás": "Centro-Oeste",
    "Mato Grosso": "Centro-Oeste",
    "Mato Grosso do Sul": "Centro-Oeste",
    "Espírito Santo": "Sudeste",
    "Minas Gerais": "Sudeste",
    "Rio de Janeiro": "Sudeste",
    "São Paulo": "Sudeste",
    "Paraná": "Sul",
    "Rio Grande do Sul": "Sul",
    "Santa Catarina": "Sul",
}


def filtrar_recorte(
    dados: pd.DataFrame,
    localizacao: str = "Total",
    dependencia: str = "Total",
) -> pd.DataFrame:
    """Seleciona localização e dependência sem alterar o DataFrame original."""
    return dados[
        dados["localizacao"].eq(localizacao)
        & dados["dependencia"].eq(dependencia)
    ].copy()


def serie_unidade(
    dados: pd.DataFrame,
    unidade: str,
    localizacao: str = "Total",
    dependencia: str = "Total",
) -> pd.DataFrame:
    recorte = filtrar_recorte(dados, localizacao, dependencia)
    return (
        somente_linhas_completas(recorte[recorte["unidade_geografica"].eq(unidade)])
        .sort_values("ano")
        .reset_index(drop=True)
    )


def ranking_ufs(
    dados: pd.DataFrame,
    ano: int,
    localizacao: str = "Total",
    dependencia: str = "Total",
) -> pd.DataFrame:
    """Cria ranking das UFs e a distância para a taxa nacional do mesmo recorte."""
    recorte = somente_linhas_completas(filtrar_recorte(dados, localizacao, dependencia))
    ano_dados = recorte[recorte["ano"].eq(ano)]
    brasil = ano_dados[ano_dados["unidade_geografica"].eq("Brasil")]
    ufs = ano_dados[ano_dados["nivel_geografico"].eq("UF")].copy()

    if brasil.empty or ufs.empty:
        return pd.DataFrame()

    taxa_brasil = float(brasil.iloc[0]["taxa_abandono"])
    ufs["regiao"] = ufs["unidade_geografica"].map(UF_REGIAO)
    ufs["diferenca_brasil_pp"] = ufs["taxa_abandono"] - taxa_brasil
    ufs = ufs.sort_values(["taxa_abandono", "unidade_geografica"], ascending=[False, True])
    ufs["posicao"] = range(1, len(ufs) + 1)
    return ufs.reset_index(drop=True)


def calcular_kpis_nacionais(
    dados: pd.DataFrame,
    ano: int,
    localizacao: str = "Total",
    dependencia: str = "Total",
) -> dict[str, float | str | int]:
    """Calcula os indicadores do Brasil e a dispersão entre UFs."""
    serie = serie_unidade(dados, "Brasil", localizacao, dependencia)
    atual = serie[serie["ano"].eq(ano)]
    if atual.empty:
        raise ValueError("Não há total nacional para o recorte selecionado.")

    linha = atual.iloc[0]
    anteriores = serie[serie["ano"].lt(ano)]
    delta_anual = float("nan")
    ano_anterior = ano
    if not anteriores.empty:
        anterior = anteriores.iloc[-1]
        delta_anual = float(linha["taxa_abandono"] - anterior["taxa_abandono"])
        ano_anterior = int(anterior["ano"])

    ranking = ranking_ufs(dados, ano, localizacao, dependencia)
    if ranking.empty:
        maior_uf = menor_uf = "Sem dados"
        maior_taxa = menor_taxa = distancia = float("nan")
    else:
        maior = ranking.iloc[0]
        menor = ranking.iloc[-1]
        maior_uf = str(maior["unidade_geografica"])
        menor_uf = str(menor["unidade_geografica"])
        maior_taxa = float(maior["taxa_abandono"])
        menor_taxa = float(menor["taxa_abandono"])
        distancia = maior_taxa - menor_taxa

    return {
        "ano": int(ano),
        "taxa_abandono": float(linha["taxa_abandono"]),
        "taxa_aprovacao": float(linha["taxa_aprovacao"]),
        "taxa_reprovacao": float(linha["taxa_reprovacao"]),
        "delta_anual_pp": delta_anual,
        "ano_anterior": ano_anterior,
        "maior_uf": maior_uf,
        "maior_taxa": maior_taxa,
        "menor_uf": menor_uf,
        "menor_taxa": menor_taxa,
        "amplitude_ufs_pp": float(distancia),
    }


def comparar_anos_ufs(
    dados: pd.DataFrame,
    ano_atual: int,
    ano_base: int,
    localizacao: str = "Total",
    dependencia: str = "Total",
) -> pd.DataFrame:
    """Compara UFs entre dois anos e classifica um sinal simples de monitoramento."""
    atual = ranking_ufs(dados, ano_atual, localizacao, dependencia)
    base = ranking_ufs(dados, ano_base, localizacao, dependencia)
    if atual.empty or base.empty:
        return pd.DataFrame()

    comparacao = atual[
        ["unidade_geografica", "regiao", "taxa_abandono", "diferenca_brasil_pp"]
    ].merge(
        base[["unidade_geografica", "taxa_abandono"]],
        on="unidade_geografica",
        how="inner",
        suffixes=("_atual", "_base"),
    )
    comparacao["variacao_pp"] = (
        comparacao["taxa_abandono_atual"] - comparacao["taxa_abandono_base"]
    )
    comparacao["situacao"] = comparacao.apply(_classificar_situacao, axis=1)
    return comparacao.sort_values(
        ["taxa_abandono_atual", "variacao_pp"], ascending=[False, False]
    ).reset_index(drop=True)


def _classificar_situacao(linha: pd.Series) -> str:
    acima_brasil = linha["diferenca_brasil_pp"] > 0
    piorou = linha["variacao_pp"] > 0
    if acima_brasil and piorou:
        return "Acima do Brasil e piorou"
    if acima_brasil:
        return "Acima do Brasil, mas melhorou"
    if piorou:
        return "Até o Brasil, porém piorou"
    return "Até o Brasil e melhorou"


def comparar_localizacoes(
    dados: pd.DataFrame,
    unidade: str,
    ano: int,
    dependencia: str = "Total",
) -> pd.DataFrame:
    recorte = dados[
        dados["unidade_geografica"].eq(unidade)
        & dados["ano"].eq(ano)
        & dados["dependencia"].eq(dependencia)
    ]
    return somente_linhas_completas(recorte).sort_values("localizacao").reset_index(drop=True)


def comparar_dependencias(
    dados: pd.DataFrame,
    unidade: str,
    ano: int,
    localizacao: str = "Total",
) -> pd.DataFrame:
    recorte = dados[
        dados["unidade_geografica"].eq(unidade)
        & dados["ano"].eq(ano)
        & dados["localizacao"].eq(localizacao)
        & ~dados["dependencia"].eq("Total")
    ]
    return somente_linhas_completas(recorte).sort_values("taxa_abandono", ascending=False).reset_index(drop=True)


def lacuna_rural_urbana_ufs(
    dados: pd.DataFrame,
    ano: int,
    dependencia: str = "Total",
) -> pd.DataFrame:
    """Calcula abandono rural menos urbano para UFs com ambos os recortes."""
    recorte = somente_linhas_completas(
        dados[
            dados["ano"].eq(ano)
            & dados["dependencia"].eq(dependencia)
            & dados["nivel_geografico"].eq("UF")
            & dados["localizacao"].isin(["Urbana", "Rural"])
        ]
    )
    tabela = recorte.pivot_table(
        index="unidade_geografica",
        columns="localizacao",
        values="taxa_abandono",
        aggfunc="first",
    ).dropna(subset=["Urbana", "Rural"])
    tabela["diferenca_rural_urbana_pp"] = tabela["Rural"] - tabela["Urbana"]
    tabela["regiao"] = tabela.index.map(UF_REGIAO)
    return tabela.reset_index().sort_values("diferenca_rural_urbana_pp", ascending=False)

