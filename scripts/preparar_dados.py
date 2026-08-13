from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd


URL_ARQUIVO = (
    "https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/"
    "{ano}/tx_rend_brasil_regioes_ufs_{ano}.zip"
)

UFS = {
    "Acre", "Alagoas", "Amapa", "Amazonas", "Bahia", "Ceara", "Distrito Federal",
    "Espirito Santo", "Goias", "Maranhao", "Mato Grosso", "Mato Grosso do Sul",
    "Minas Gerais", "Para", "Paraiba", "Parana", "Pernambuco", "Piaui",
    "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondonia",
    "Roraima", "Santa Catarina", "Sao Paulo", "Sergipe", "Tocantins",
}

REGIOES = {"Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}


def normalizar_nome(nome: str) -> str:
    tabela = str.maketrans(
        "áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ",
        "aaaaeeioooucAAAAEEIOOOUC",
    )
    return str(nome).translate(tabela)


def classificar_nivel(nome: str) -> str:
    nome_normalizado = normalizar_nome(nome)
    if nome_normalizado == "Brasil":
        return "Brasil"
    if nome_normalizado in REGIOES:
        return "Regiao"
    if nome_normalizado in UFS:
        return "UF"
    return "Outro"


def baixar_zip(ano: int) -> bytes:
    requisicao = Request(
        URL_ARQUIVO.format(ano=ano),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urlopen(requisicao, timeout=120) as resposta:
        return resposta.read()


def ler_zip(conteudo: bytes) -> pd.DataFrame:
    with ZipFile(BytesIO(conteudo)) as arquivo_zip:
        nomes_excel = [nome for nome in arquivo_zip.namelist() if nome.lower().endswith(".xlsx")]
        if not nomes_excel:
            raise ValueError("O arquivo do Inep não contém planilha XLSX.")

        with arquivo_zip.open(nomes_excel[0]) as arquivo_excel:
            dados = pd.read_excel(
                arquivo_excel,
                header=None,
                skiprows=9,
                usecols=[0, 1, 2, 3, 16, 34, 52],
                names=[
                    "ano",
                    "unidade_geografica",
                    "localizacao",
                    "dependencia",
                    "taxa_aprovacao",
                    "taxa_reprovacao",
                    "taxa_abandono",
                ],
            )

    dados["ano"] = pd.to_numeric(dados["ano"], errors="coerce")
    dados = dados.dropna(subset=["ano", "unidade_geografica"]).copy()
    dados["ano"] = dados["ano"].astype(int)

    for coluna in ["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    dados["nivel_geografico"] = dados["unidade_geografica"].map(classificar_nivel)
    return dados


def preparar(destino: Path, ano_inicial: int, ano_final: int) -> pd.DataFrame:
    tabelas = []
    for ano in range(ano_inicial, ano_final + 1):
        print(f"Baixando dados de {ano}")
        tabelas.append(ler_zip(baixar_zip(ano)))

    resultado = pd.concat(tabelas, ignore_index=True)
    resultado = resultado[
        [
            "ano",
            "unidade_geografica",
            "nivel_geografico",
            "localizacao",
            "dependencia",
            "taxa_aprovacao",
            "taxa_reprovacao",
            "taxa_abandono",
        ]
    ].sort_values(
        ["ano", "nivel_geografico", "unidade_geografica", "localizacao", "dependencia"]
    )

    destino.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(destino, index=False)
    print(f"Arquivo criado com {len(resultado)} linhas: {destino}")
    return resultado


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa e prepara as taxas de rendimento do ensino médio publicadas pelo Inep."
    )
    parser.add_argument("--inicio", type=int, default=2019)
    parser.add_argument("--fim", type=int, default=2025)
    parser.add_argument(
        "--destino",
        type=Path,
        default=Path("data/taxas_rendimento_ensino_medio_2019_2025.csv"),
    )
    argumentos = parser.parse_args()
    if argumentos.inicio > argumentos.fim:
        parser.error("O ano inicial não pode ser maior que o ano final.")
    preparar(argumentos.destino, argumentos.inicio, argumentos.fim)


if __name__ == "__main__":
    main()

