from pathlib import Path

import pytest

from src.analysis import (
    calcular_kpis_nacionais,
    comparar_anos_ufs,
    lacuna_rural_urbana_ufs,
    ranking_ufs,
    serie_unidade,
)
from src.data import carregar_dados


ARQUIVO = Path(__file__).parents[1] / "data" / "taxas_rendimento_ensino_medio_2019_2025.csv"


@pytest.fixture(scope="module")
def dados():
    return carregar_dados(ARQUIVO)


def test_taxas_nacionais_somam_cem(dados):
    brasil = serie_unidade(dados, "Brasil")
    soma = brasil[["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]].sum(axis=1)
    assert soma.tolist() == pytest.approx([100] * len(soma), abs=0.2)


def test_ranking_de_2025_tem_as_27_ufs(dados):
    ranking = ranking_ufs(dados, 2025)
    assert len(ranking) == 27
    assert ranking.iloc[0]["unidade_geografica"] == "Amapá"
    assert ranking.iloc[-1]["unidade_geografica"] == "Mato Grosso"


def test_kpis_nacionais_de_2025(dados):
    kpis = calcular_kpis_nacionais(dados, 2025)
    assert kpis["taxa_abandono"] == pytest.approx(2.2)
    assert kpis["delta_anual_pp"] == pytest.approx(-1.0)
    assert kpis["amplitude_ufs_pp"] == pytest.approx(4.3)


def test_comparacao_de_ufs_cria_as_quatro_leituras(dados):
    comparacao = comparar_anos_ufs(dados, 2025, 2019)
    assert len(comparacao) == 27
    assert set(comparacao["situacao"]).issubset(
        {
            "Acima do Brasil e piorou",
            "Acima do Brasil, mas melhorou",
            "Até o Brasil, porém piorou",
            "Até o Brasil e melhorou",
        }
    )


def test_lacuna_rural_urbana_usa_apenas_pares_completos(dados):
    lacunas = lacuna_rural_urbana_ufs(dados, 2025)
    assert not lacunas.empty
    assert lacunas[["Rural", "Urbana", "diferenca_rural_urbana_pp"]].notna().all().all()

