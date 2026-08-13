from src.formatting import percentual, pontos_percentuais


def test_formatacao_em_portugues():
    assert percentual(2.2) == "2,2%"
    assert pontos_percentuais(-1.0) == "-1,0 p.p."
    assert pontos_percentuais(4.3, False) == "4,3 p.p."

