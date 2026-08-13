from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analysis import (
    calcular_kpis_nacionais,
    comparar_anos_ufs,
    comparar_dependencias,
    comparar_localizacoes,
    filtrar_recorte,
    lacuna_rural_urbana_ufs,
    ranking_ufs,
    serie_unidade,
)
from src.data import carregar_dados, resumo_qualidade, somente_linhas_completas
from src.formatting import percentual, pontos_percentuais


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_DADOS = BASE_DIR / "data" / "taxas_rendimento_ensino_medio_2019_2025.csv"

CORES = {
    "azul": "#3157D5",
    "azul_escuro": "#12263A",
    "verde": "#159A8C",
    "amarelo": "#F2B134",
    "vermelho": "#E25555",
    "roxo": "#7656D8",
    "cinza": "#6B7280",
    "claro": "#EEF2FF",
}


st.set_page_config(
    page_title="Observatório do abandono escolar",
    page_icon=None,
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #F6F8FC; }
    .block-container { max-width: 1480px; padding-top: 1.4rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #ECF1FA; border-right: 1px solid #DCE3F0; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 5px 18px rgba(18, 38, 58, 0.06);
    }
    [data-testid="stMetricLabel"] { color: #526173; }
    .hero {
        background: linear-gradient(118deg, #12263A 0%, #254D8F 58%, #3157D5 100%);
        border-radius: 22px;
        padding: 30px 34px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 14px 38px rgba(18, 38, 58, 0.20);
    }
    .hero h1 { margin: 0 0 8px 0; font-size: 2.15rem; color: white; }
    .hero p { margin: 0; color: #DCE8FF; max-width: 900px; font-size: 1.02rem; }
    .eyebrow { color: #9EC5FF; font-size: 0.78rem; font-weight: 700; letter-spacing: .12em; }
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #3157D5;
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 118px;
        box-shadow: 0 5px 18px rgba(18, 38, 58, 0.05);
    }
    .insight-card strong { color: #12263A; font-size: 1.02rem; }
    .insight-card p { color: #526173; margin: 7px 0 0 0; line-height: 1.45; }
    .small-note { color: #66758A; font-size: .88rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #E9EEF8;
        border-radius: 10px 10px 0 0;
        padding: 10px 15px;
    }
    .stTabs [aria-selected="true"] { background: #FFFFFF; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def obter_dados_padrao() -> pd.DataFrame:
    return carregar_dados(ARQUIVO_DADOS)


def aplicar_layout(fig: go.Figure, altura: int = 430) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=62, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color=CORES["azul_escuro"]),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D9E0EB")
    fig.update_yaxes(gridcolor="#E8EDF5", zeroline=False)
    return fig


def exibir_cartao(titulo: str, texto: str, cor: str = "#3157D5") -> None:
    st.markdown(
        f"""
        <div class="insight-card" style="border-left-color:{cor}">
            <strong>{titulo}</strong>
            <p>{texto}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">DADOS ABERTOS DO INEP, 2019 A 2025</div>
        <h1>Observatório do abandono escolar no ensino médio</h1>
        <p>Uma leitura territorial das taxas de aprovação, reprovação e abandono para apoiar diagnóstico, comparação e monitoramento. O painel descreve padrões, não identifica causas individuais.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Configuração")
arquivo_enviado = st.sidebar.file_uploader(
    "Usar outro CSV processado",
    type="csv",
    help="O arquivo precisa seguir o dicionário de dados deste projeto.",
)

try:
    dados = carregar_dados(arquivo_enviado) if arquivo_enviado else obter_dados_padrao()
except ValueError as erro:
    st.error(str(erro))
    st.stop()

anos = sorted(dados["ano"].unique(), reverse=True)
ano = st.sidebar.selectbox("Ano de referência", anos)

localizacoes = [nome for nome in ["Total", "Urbana", "Rural"] if nome in dados["localizacao"].unique()]
localizacao = st.sidebar.selectbox("Localização", localizacoes)

ordem_dependencias = ["Total", "Pública", "Federal", "Estadual", "Municipal", "Privada"]
dependencias = [nome for nome in ordem_dependencias if nome in dados["dependencia"].unique()]
dependencia = st.sidebar.selectbox("Dependência administrativa", dependencias)

st.sidebar.divider()
st.sidebar.markdown("**Como interpretar**")
st.sidebar.caption(
    "A taxa de abandono faz parte do rendimento escolar anual. Ela não representa, sozinha, toda a trajetória de evasão de um estudante."
)

recorte_global = filtrar_recorte(dados, localizacao, dependencia)
anos_disponiveis = sorted(recorte_global["ano"].unique())
ano_base_padrao = anos_disponiveis[0]

abas = st.tabs(
    [
        "Resumo executivo",
        "Evolução",
        "Territórios",
        "Desigualdades",
        "Matriz de monitoramento",
        "Dados e método",
    ]
)


with abas[0]:
    try:
        kpis = calcular_kpis_nacionais(dados, ano, localizacao, dependencia)
    except ValueError as erro:
        st.warning(str(erro))
    else:
        coluna_1, coluna_2, coluna_3, coluna_4 = st.columns(4)
        coluna_1.metric(
            f"Abandono no Brasil, {ano}",
            percentual(kpis["taxa_abandono"]),
            pontos_percentuais(kpis["delta_anual_pp"]),
            delta_color="inverse",
            help=f"Variação em relação a {kpis['ano_anterior']}.",
        )
        coluna_2.metric("Aprovação", percentual(kpis["taxa_aprovacao"]))
        coluna_3.metric("Reprovação", percentual(kpis["taxa_reprovacao"]))
        coluna_4.metric("Distância entre UFs", pontos_percentuais(kpis["amplitude_ufs_pp"], False))

        st.markdown("#### Leitura rápida")
        cartao_1, cartao_2, cartao_3 = st.columns(3)
        with cartao_1:
            exibir_cartao(
                "Maior taxa entre as UFs",
                f"{kpis['maior_uf']} registrou {percentual(kpis['maior_taxa'])} no recorte selecionado.",
                CORES["vermelho"],
            )
        with cartao_2:
            exibir_cartao(
                "Menor taxa entre as UFs",
                f"{kpis['menor_uf']} registrou {percentual(kpis['menor_taxa'])} no mesmo recorte.",
                CORES["verde"],
            )
        with cartao_3:
            direcao = "redução" if kpis["delta_anual_pp"] < 0 else "aumento"
            exibir_cartao(
                "Mudança nacional",
                f"Houve {direcao} de {pontos_percentuais(abs(kpis['delta_anual_pp']), False)} frente ao ano anterior disponível.",
                CORES["azul"],
            )

        esquerda, direita = st.columns([1.15, 1])
        with esquerda:
            serie_brasil = serie_unidade(dados, "Brasil", localizacao, dependencia)
            figura = px.line(
                serie_brasil,
                x="ano",
                y="taxa_abandono",
                markers=True,
                title="Evolução nacional da taxa de abandono",
                labels={"ano": "Ano", "taxa_abandono": "Abandono"},
            )
            figura.update_traces(line_color=CORES["vermelho"], line_width=4, marker_size=9)
            figura.update_yaxes(ticksuffix="%")
            figura.update_xaxes(dtick=1)
            st.plotly_chart(aplicar_layout(figura), width="stretch")

        with direita:
            ranking = ranking_ufs(dados, ano, localizacao, dependencia).head(8)
            if ranking.empty:
                st.info("Não há ranking disponível para esse recorte.")
            else:
                figura = px.bar(
                    ranking.sort_values("taxa_abandono"),
                    x="taxa_abandono",
                    y="unidade_geografica",
                    orientation="h",
                    text="taxa_abandono",
                    title=f"Oito maiores taxas entre as UFs em {ano}",
                    labels={"taxa_abandono": "Abandono", "unidade_geografica": "UF"},
                )
                figura.update_traces(marker_color=CORES["roxo"], texttemplate="%{text:.1f}%", textposition="outside")
                figura.update_xaxes(ticksuffix="%")
                st.plotly_chart(aplicar_layout(figura), width="stretch")

        st.info(
            "Os resultados de 2020 e 2021 exigem cautela, pois o funcionamento das redes de ensino foi excepcional durante a pandemia."
        )


with abas[1]:
    st.subheader("Compare a trajetória de até seis territórios")
    opcoes = sorted(
        somente_linhas_completas(recorte_global)["unidade_geografica"].dropna().unique()
    )
    padrao = [nome for nome in ["Brasil", "Amapá", "São Paulo"] if nome in opcoes]
    unidades = st.multiselect(
        "Territórios",
        opcoes,
        default=padrao,
        max_selections=6,
    )

    tendencia = somente_linhas_completas(
        recorte_global[recorte_global["unidade_geografica"].isin(unidades)]
    )
    if tendencia.empty:
        st.info("Selecione ao menos um território com dados disponíveis.")
    else:
        figura = px.line(
            tendencia,
            x="ano",
            y="taxa_abandono",
            color="unidade_geografica",
            markers=True,
            title="Taxa de abandono ao longo do período",
            labels={"ano": "Ano", "taxa_abandono": "Abandono", "unidade_geografica": "Território"},
        )
        figura.update_yaxes(ticksuffix="%")
        figura.update_xaxes(dtick=1)
        figura.update_traces(line_width=3, marker_size=7)
        st.plotly_chart(aplicar_layout(figura, 500), width="stretch")

    ano_base = st.selectbox(
        "Ano-base para comparar as UFs",
        sorted([valor for valor in anos_disponiveis if valor < ano], reverse=True),
        index=len([valor for valor in anos_disponiveis if valor < ano]) - 1 if any(valor < ano for valor in anos_disponiveis) else 0,
        disabled=not any(valor < ano for valor in anos_disponiveis),
    ) if any(valor < ano for valor in anos_disponiveis) else ano_base_padrao

    comparacao = comparar_anos_ufs(dados, ano, int(ano_base), localizacao, dependencia)
    if not comparacao.empty:
        melhores = comparacao.nsmallest(5, "variacao_pp")
        piores = comparacao.nlargest(5, "variacao_pp")
        col_1, col_2 = st.columns(2)
        with col_1:
            figura = px.bar(
                melhores.sort_values("variacao_pp", ascending=False),
                x="variacao_pp",
                y="unidade_geografica",
                orientation="h",
                title=f"Maiores reduções entre {ano_base} e {ano}",
                labels={"variacao_pp": "Variação", "unidade_geografica": "UF"},
            )
            figura.update_traces(marker_color=CORES["verde"], texttemplate="%{x:.1f} p.p.", textposition="outside")
            figura.update_xaxes(ticksuffix=" p.p.")
            st.plotly_chart(aplicar_layout(figura), width="stretch")
        with col_2:
            figura = px.bar(
                piores.sort_values("variacao_pp"),
                x="variacao_pp",
                y="unidade_geografica",
                orientation="h",
                title=f"Maiores aumentos entre {ano_base} e {ano}",
                labels={"variacao_pp": "Variação", "unidade_geografica": "UF"},
            )
            figura.update_traces(marker_color=CORES["vermelho"], texttemplate="%{x:.1f} p.p.", textposition="outside")
            figura.update_xaxes(ticksuffix=" p.p.")
            st.plotly_chart(aplicar_layout(figura), width="stretch")


with abas[2]:
    st.subheader(f"Distribuição territorial em {ano}")
    ranking = ranking_ufs(dados, ano, localizacao, dependencia)
    if ranking.empty:
        st.info("Não há dados territoriais completos para esse recorte.")
    else:
        taxa_brasil = float(
            serie_unidade(dados, "Brasil", localizacao, dependencia)
            .query("ano == @ano")
            .iloc[0]["taxa_abandono"]
        )
        ranking["comparacao"] = ranking["diferenca_brasil_pp"].apply(
            lambda valor: "Acima do Brasil" if valor > 0 else "Até a taxa do Brasil"
        )
        figura = px.bar(
            ranking.sort_values("taxa_abandono"),
            x="taxa_abandono",
            y="unidade_geografica",
            color="comparacao",
            orientation="h",
            height=760,
            title="Taxa de abandono nas 27 unidades da federação",
            labels={"taxa_abandono": "Abandono", "unidade_geografica": "UF", "comparacao": "Posição"},
            color_discrete_map={
                "Acima do Brasil": CORES["vermelho"],
                "Até a taxa do Brasil": CORES["azul"],
            },
        )
        figura.add_vline(
            x=taxa_brasil,
            line_dash="dash",
            line_color=CORES["azul_escuro"],
            annotation_text=f"Brasil: {taxa_brasil:.1f}%",
            annotation_position="top",
        )
        figura.update_xaxes(ticksuffix="%")
        st.plotly_chart(aplicar_layout(figura, 790), width="stretch")

        esquerda, direita = st.columns([1, 1.2])
        with esquerda:
            figura = px.box(
                ranking,
                x="regiao",
                y="taxa_abandono",
                color="regiao",
                points="all",
                title="Distribuição das UFs por região",
                labels={"regiao": "Região", "taxa_abandono": "Abandono"},
            )
            figura.update_yaxes(ticksuffix="%")
            st.plotly_chart(aplicar_layout(figura), width="stretch")
        with direita:
            uf_escolhida = st.selectbox("Detalhar uma unidade da federação", ranking["unidade_geografica"].tolist())
            serie_uf = serie_unidade(dados, uf_escolhida, localizacao, dependencia)
            figura = px.line(
                serie_uf,
                x="ano",
                y="taxa_abandono",
                markers=True,
                title=f"Trajetória de {uf_escolhida}",
                labels={"ano": "Ano", "taxa_abandono": "Abandono"},
            )
            figura.update_traces(line_color=CORES["roxo"], line_width=4, marker_size=8)
            figura.update_yaxes(ticksuffix="%")
            figura.update_xaxes(dtick=1)
            st.plotly_chart(aplicar_layout(figura), width="stretch")


with abas[3]:
    st.subheader("Compare localização e rede administrativa")
    unidades_recorte = sorted(dados["unidade_geografica"].dropna().unique())
    unidade_desigualdade = st.selectbox(
        "Território analisado",
        unidades_recorte,
        index=unidades_recorte.index("Brasil") if "Brasil" in unidades_recorte else 0,
        key="territorio_desigualdades",
    )

    col_1, col_2 = st.columns(2)
    with col_1:
        por_localizacao = comparar_localizacoes(dados, unidade_desigualdade, ano, dependencia)
        if por_localizacao.empty:
            st.info("Não há comparação por localização para esse recorte.")
        else:
            figura = px.bar(
                por_localizacao,
                x="localizacao",
                y="taxa_abandono",
                color="localizacao",
                text="taxa_abandono",
                title=f"Abandono por localização em {unidade_desigualdade}",
                labels={"localizacao": "Localização", "taxa_abandono": "Abandono"},
                color_discrete_sequence=[CORES["azul"], CORES["amarelo"], CORES["verde"]],
            )
            figura.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            figura.update_yaxes(ticksuffix="%")
            st.plotly_chart(aplicar_layout(figura), width="stretch")

    with col_2:
        por_dependencia = comparar_dependencias(dados, unidade_desigualdade, ano, localizacao)
        if por_dependencia.empty:
            st.info("Não há comparação por dependência para esse recorte.")
        else:
            figura = px.bar(
                por_dependencia.sort_values("taxa_abandono"),
                x="taxa_abandono",
                y="dependencia",
                orientation="h",
                text="taxa_abandono",
                title=f"Abandono por dependência em {unidade_desigualdade}",
                labels={"dependencia": "Dependência", "taxa_abandono": "Abandono"},
            )
            figura.update_traces(marker_color=CORES["roxo"], texttemplate="%{text:.1f}%", textposition="outside")
            figura.update_xaxes(ticksuffix="%")
            st.plotly_chart(aplicar_layout(figura), width="stretch")

    lacunas = lacuna_rural_urbana_ufs(dados, ano, dependencia)
    if not lacunas.empty:
        maiores_lacunas = lacunas.nlargest(10, "diferenca_rural_urbana_pp")
        figura = px.bar(
            maiores_lacunas.sort_values("diferenca_rural_urbana_pp"),
            x="diferenca_rural_urbana_pp",
            y="unidade_geografica",
            orientation="h",
            color="regiao",
            title="Maiores diferenças entre área rural e urbana",
            labels={
                "diferenca_rural_urbana_pp": "Rural menos urbana",
                "unidade_geografica": "UF",
                "regiao": "Região",
            },
        )
        figura.update_xaxes(ticksuffix=" p.p.")
        st.plotly_chart(aplicar_layout(figura, 500), width="stretch")
        st.caption(
            "Valor positivo significa que a taxa rural foi maior que a urbana. A diferença descreve o recorte e não identifica sua causa."
        )


with abas[4]:
    st.subheader("Matriz simples para orientar perguntas")
    st.caption(
        "A matriz combina a taxa atual com a mudança desde o ano-base. Ela ajuda a organizar o monitoramento, mas não é um modelo de risco nem uma recomendação automática."
    )

    anos_anteriores = [valor for valor in anos_disponiveis if valor < ano]
    ano_base_matriz = st.selectbox(
        "Ano-base",
        sorted(anos_anteriores, reverse=True),
        index=len(anos_anteriores) - 1 if anos_anteriores else 0,
        key="ano_base_matriz",
        disabled=not anos_anteriores,
    ) if anos_anteriores else ano_base_padrao

    matriz = comparar_anos_ufs(dados, ano, int(ano_base_matriz), localizacao, dependencia)
    if matriz.empty:
        st.info("Não há comparação disponível para esse recorte.")
    else:
        taxa_brasil_atual = float(
            serie_unidade(dados, "Brasil", localizacao, dependencia)
            .query("ano == @ano")
            .iloc[0]["taxa_abandono"]
        )
        figura = px.scatter(
            matriz,
            x="variacao_pp",
            y="taxa_abandono_atual",
            color="situacao",
            hover_name="unidade_geografica",
            hover_data={"regiao": True, "variacao_pp": ":.1f", "taxa_abandono_atual": ":.1f"},
            title=f"Taxa em {ano} e variação desde {ano_base_matriz}",
            labels={
                "variacao_pp": "Variação desde o ano-base",
                "taxa_abandono_atual": f"Abandono em {ano}",
                "situacao": "Leitura",
            },
            color_discrete_map={
                "Acima do Brasil e piorou": CORES["vermelho"],
                "Acima do Brasil, mas melhorou": CORES["amarelo"],
                "Até o Brasil, porém piorou": CORES["roxo"],
                "Até o Brasil e melhorou": CORES["verde"],
            },
        )
        figura.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
        figura.add_vline(x=0, line_dash="dash", line_color=CORES["cinza"])
        figura.add_hline(
            y=taxa_brasil_atual,
            line_dash="dash",
            line_color=CORES["azul_escuro"],
            annotation_text=f"Brasil: {taxa_brasil_atual:.1f}%",
        )
        figura.update_xaxes(ticksuffix=" p.p.")
        figura.update_yaxes(ticksuffix="%")
        st.plotly_chart(aplicar_layout(figura, 590), width="stretch")

        contagens = matriz["situacao"].value_counts()
        colunas = st.columns(4)
        ordem = [
            "Acima do Brasil e piorou",
            "Acima do Brasil, mas melhorou",
            "Até o Brasil, porém piorou",
            "Até o Brasil e melhorou",
        ]
        for coluna, situacao in zip(colunas, ordem):
            coluna.metric(situacao, int(contagens.get(situacao, 0)))

        tabela_matriz = matriz.rename(
            columns={
                "unidade_geografica": "UF",
                "regiao": "Região",
                "taxa_abandono_atual": f"Abandono {ano}",
                "taxa_abandono_base": f"Abandono {ano_base_matriz}",
                "variacao_pp": "Variação p.p.",
                "situacao": "Leitura",
            }
        )[["UF", "Região", f"Abandono {ano}", f"Abandono {ano_base_matriz}", "Variação p.p.", "Leitura"]]
        st.dataframe(tabela_matriz, width="stretch", hide_index=True)
        st.download_button(
            "Baixar matriz em CSV",
            tabela_matriz.to_csv(index=False).encode("utf-8"),
            file_name=f"matriz_monitoramento_{ano}.csv",
            mime="text/csv",
        )


with abas[5]:
    qualidade = resumo_qualidade(dados)
    st.subheader("Dados oficiais, análise reproduzível")
    st.markdown(
        """
        A base reúne as **Taxas de Rendimento Escolar** publicadas pelo Inep para Brasil, regiões e unidades da federação. O indicador anual de abandono é analisado no ensino médio e pode ser filtrado por localização e dependência administrativa.

        O nome histórico do repositório usa a palavra evasão. Neste painel, o termo adotado é **abandono**, pois esse é o indicador efetivamente publicado na fonte. Evasão é um conceito mais amplo e pode envolver o acompanhamento da trajetória do estudante por mais tempo.
        """
    )

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Linhas carregadas", f"{qualidade['linhas']:,}".replace(",", "."))
    q2.metric("Linhas completas", f"{qualidade['linhas_completas']:,}".replace(",", "."))
    q3.metric("Cobertura", percentual(qualidade["cobertura_pct"]))
    q4.metric("Duplicidades", qualidade["duplicidades"])

    with st.expander("O que o painel responde"):
        st.markdown(
            """
            - Como a taxa nacional mudou entre 2019 e 2025.
            - Quais UFs ficaram acima ou abaixo do resultado brasileiro em cada recorte.
            - Como os resultados variam entre áreas urbanas e rurais.
            - Como as dependências administrativas se comparam.
            - Quais territórios merecem novas perguntas por combinarem nível atual e mudança histórica.
            """
        )

    with st.expander("O que o painel não responde"):
        st.markdown(
            """
            - Não identifica estudantes individualmente.
            - Não explica as causas do abandono.
            - Não mede impacto de políticas públicas.
            - Não transforma associação em causalidade.
            - Não substitui análises locais com dados de contexto.
            """
        )

    dados_download = somente_linhas_completas(recorte_global).sort_values(
        ["ano", "nivel_geografico", "unidade_geografica"], ascending=[False, True, True]
    )
    st.dataframe(dados_download, width="stretch", hide_index=True)
    st.download_button(
        "Baixar recorte exibido",
        dados_download.to_csv(index=False).encode("utf-8"),
        file_name="taxas_rendimento_recorte.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Fonte: Inep, Taxas de Rendimento Escolar. Projeto de portfólio de Bruno Nunes. Resultados descritivos, sem inferência causal."
)

