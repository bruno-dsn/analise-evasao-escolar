from pathlib import Path

import pandas as pd
import pytest

from src.data import carregar_dados, resumo_qualidade


ARQUIVO = Path(__file__).parents[1] / "data" / "taxas_rendimento_ensino_medio_2019_2025.csv"


def test_base_tem_periodo_e_niveis_esperados():
    dados = carregar_dados(ARQUIVO)
    assert set(dados["ano"].unique()) == set(range(2019, 2026))
    assert {"Brasil", "Regiao", "UF"} == set(dados["nivel_geografico"].unique())


def test_qualidade_da_base_processada():
    qualidade = resumo_qualidade(carregar_dados(ARQUIVO))
    assert qualidade["linhas"] == 4105
    assert qualidade["linhas_completas"] == 3783
    assert qualidade["duplicidades"] == 0
    assert qualidade["linhas_inconsistentes"] == 0


def test_coluna_obrigatoria_ausente_gera_erro(tmp_path):
    arquivo = tmp_path / "incompleto.csv"
    pd.DataFrame({"ano": [2025]}).to_csv(arquivo, index=False)
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        carregar_dados(arquivo)


def test_duplicidade_gera_erro(tmp_path):
    dados = pd.read_csv(ARQUIVO).head(1)
    arquivo = tmp_path / "duplicado.csv"
    pd.concat([dados, dados], ignore_index=True).to_csv(arquivo, index=False)
    with pytest.raises(ValueError, match="duplicados"):
        carregar_dados(arquivo)

