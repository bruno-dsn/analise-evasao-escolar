from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch


BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_DADOS = BASE_DIR / "data" / "taxas_rendimento_ensino_medio_2019_2025.csv"
PASTA_ASSETS = BASE_DIR / "assets"

AZUL_ESCURO = "#12263A"
AZUL = "#3157D5"
VERDE = "#159A8C"
AMARELO = "#F2B134"
VERMELHO = "#E25555"
ROXO = "#7656D8"
FUNDO = "#F4F7FC"
TEXTO = "#34445A"


def numero_pt(valor: float, com_sinal: bool = False) -> str:
    formato = "+.1f" if com_sinal else ".1f"
    return format(valor, formato).replace(".", ",")


def dados_principais() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dados = pd.read_csv(ARQUIVO_DADOS)
    base = dados[
        dados["localizacao"].eq("Total")
        & dados["dependencia"].eq("Total")
    ].dropna(subset=["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"])
    brasil = base[base["unidade_geografica"].eq("Brasil")].sort_values("ano")
    ranking = base[
        base["ano"].eq(2025) & base["nivel_geografico"].eq("UF")
    ].sort_values("taxa_abandono", ascending=False)
    localidades = dados[
        dados["ano"].eq(2025)
        & dados["unidade_geografica"].eq("Brasil")
        & dados["dependencia"].eq("Total")
    ].dropna(subset=["taxa_abandono"])
    return brasil, ranking, localidades


def cartao(fig: plt.Figure, x: float, titulo: str, valor: str, detalhe: str, cor: str) -> None:
    fundo = FancyBboxPatch(
        (x, 0.70),
        0.205,
        0.145,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        transform=fig.transFigure,
        facecolor="white",
        edgecolor="#DFE6F0",
        linewidth=1.1,
    )
    fig.patches.append(fundo)
    fig.text(x + 0.016, 0.809, titulo, fontsize=11, color="#66758A", weight="bold")
    fig.text(x + 0.016, 0.755, valor, fontsize=25, color=cor, weight="bold")
    fig.text(x + 0.016, 0.718, detalhe, fontsize=9.5, color=TEXTO)


def gerar_dashboard() -> None:
    brasil, ranking, localidades = dados_principais()
    atual = brasil.iloc[-1]
    anterior = brasil.iloc[-2]
    maior = ranking.iloc[0]
    menor = ranking.iloc[-1]

    fig = plt.figure(figsize=(16, 9), facecolor=FUNDO)
    fig.text(0.06, 0.945, "OBSERVATÓRIO EDUCACIONAL", fontsize=11, color=AZUL, weight="bold")
    fig.text(0.06, 0.895, "Abandono escolar no ensino médio", fontsize=28, color=AZUL_ESCURO, weight="bold")
    fig.text(
        0.06,
        0.858,
        "Taxas de rendimento escolar do Inep, Brasil e unidades da federação, 2019 a 2025",
        fontsize=12,
        color="#617187",
    )

    delta = atual["taxa_abandono"] - anterior["taxa_abandono"]
    cartao(fig, 0.06, "Abandono no Brasil", f"{numero_pt(atual['taxa_abandono'])}%", "resultado de 2025", VERMELHO)
    cartao(fig, 0.285, "Mudança anual", f"{numero_pt(delta, True)} p.p.", "comparação com 2024", VERDE if delta < 0 else VERMELHO)
    cartao(fig, 0.51, "Maior taxa entre UFs", f"{numero_pt(maior['taxa_abandono'])}%", str(maior["unidade_geografica"]), ROXO)
    cartao(fig, 0.735, "Distância entre UFs", f"{numero_pt(maior['taxa_abandono'] - menor['taxa_abandono'])} p.p.", "maior menos menor taxa", AMARELO)

    ax_linha = fig.add_axes([0.06, 0.14, 0.42, 0.48], facecolor="white")
    ax_linha.plot(
        brasil["ano"],
        brasil["taxa_abandono"],
        color=VERMELHO,
        marker="o",
        linewidth=3.2,
        markersize=7,
    )
    for _, linha in brasil.iterrows():
        ax_linha.text(linha["ano"], linha["taxa_abandono"] + 0.22, f"{numero_pt(linha['taxa_abandono'])}%", ha="center", fontsize=9, color=TEXTO)
    ax_linha.set_title("Evolução nacional", loc="left", fontsize=15, color=AZUL_ESCURO, weight="bold", pad=18)
    ax_linha.set_ylabel("Taxa de abandono")
    ax_linha.set_xticks(brasil["ano"])
    ax_linha.set_ylim(0, max(brasil["taxa_abandono"]) + 1.2)
    ax_linha.grid(axis="y", color="#E8EDF5", linewidth=0.8)
    ax_linha.spines[["top", "right", "left"]].set_visible(False)
    ax_linha.spines["bottom"].set_color("#D8E0EB")
    ax_linha.tick_params(colors="#64748B")

    ax_barra = fig.add_axes([0.55, 0.14, 0.39, 0.48], facecolor="white")
    top = ranking.head(8).sort_values("taxa_abandono")
    barras = ax_barra.barh(top["unidade_geografica"], top["taxa_abandono"], color=ROXO)
    ax_barra.bar_label(barras, labels=[f"{numero_pt(valor)}%" for valor in top["taxa_abandono"]], padding=5, fontsize=9, color=TEXTO)
    ax_barra.set_title("Maiores taxas entre as UFs em 2025", loc="left", fontsize=15, color=AZUL_ESCURO, weight="bold", pad=18)
    ax_barra.set_xlabel("Taxa de abandono")
    ax_barra.set_xlim(0, top["taxa_abandono"].max() + 1.2)
    ax_barra.grid(axis="x", color="#E8EDF5", linewidth=0.8)
    ax_barra.spines[["top", "right", "left"]].set_visible(False)
    ax_barra.spines["bottom"].set_color("#D8E0EB")
    ax_barra.tick_params(colors="#64748B")

    fig.text(
        0.06,
        0.065,
        "Leitura: o indicador descreve abandono anual. Não explica causas e não deve ser tratado como evasão longitudinal.",
        fontsize=10,
        color="#617187",
    )
    fig.text(0.94, 0.065, "Fonte: Inep", fontsize=10, color=AZUL, weight="bold", ha="right")

    PASTA_ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PASTA_ASSETS / "dashboard_abandono_escolar.png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)


def gerar_capa_linkedin() -> None:
    brasil, ranking, _ = dados_principais()
    atual = brasil.iloc[-1]
    anterior = brasil.iloc[-2]
    maior = ranking.iloc[0]
    delta = atual["taxa_abandono"] - anterior["taxa_abandono"]

    fig = plt.figure(figsize=(12, 6.27), facecolor=AZUL_ESCURO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.add_patch(plt.Circle((0.91, 0.86), 0.28, color=AZUL, alpha=0.35, transform=ax.transAxes))
    ax.add_patch(plt.Circle((0.80, 0.12), 0.20, color=ROXO, alpha=0.30, transform=ax.transAxes))
    ax.add_patch(plt.Circle((0.05, 0.08), 0.15, color=VERDE, alpha=0.22, transform=ax.transAxes))

    fig.text(0.065, 0.86, "PROJETO DE CIÊNCIA DE DADOS", fontsize=12, color="#9EC5FF", weight="bold")
    fig.text(0.065, 0.69, "Abandono escolar\nno ensino médio", fontsize=34, color="white", weight="bold", linespacing=1.05)
    fig.text(0.065, 0.53, "Dados oficiais do Inep, 2019 a 2025", fontsize=16, color="#DDE8FF")

    caixas = [
        ("Brasil em 2025", f"{numero_pt(atual['taxa_abandono'])}%", VERMELHO),
        ("Variação anual", f"{numero_pt(delta, True)} p.p.", VERDE if delta < 0 else VERMELHO),
        ("Maior taxa entre UFs", f"{numero_pt(maior['taxa_abandono'])}%", AMARELO),
    ]
    for indice, (rotulo, valor, cor) in enumerate(caixas):
        x = 0.065 + indice * 0.29
        caixa = FancyBboxPatch(
            (x, 0.19), 0.245, 0.19,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            transform=fig.transFigure,
            facecolor="#19354D",
            edgecolor="#345069",
        )
        fig.patches.append(caixa)
        fig.text(x + 0.018, 0.32, rotulo, fontsize=10, color="#B9C8D8")
        fig.text(x + 0.018, 0.235, valor, fontsize=24, color=cor, weight="bold")

    fig.text(0.065, 0.08, "Bruno Nunes  |  Ciência de Dados", fontsize=12, color="white", weight="bold")
    fig.text(0.935, 0.08, "Streamlit  |  Python  |  Plotly", fontsize=11, color="#B9C8D8", ha="right")

    fig.savefig(PASTA_ASSETS / "capa_linkedin.png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    gerar_dashboard()
    gerar_capa_linkedin()
    print("Imagens criadas em assets/.")
