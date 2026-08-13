# Fontes e metodologia

## Fonte oficial

Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira, Inep.

Página das Taxas de Rendimento Escolar:

https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar

Período usado: 2019 a 2025.

Data de preparação do arquivo incluído no projeto: 12 de agosto de 2026.

## O que a fonte publica

As Taxas de Rendimento Escolar apresentam três resultados anuais:

1. aprovação;
2. reprovação;
3. abandono.

Este projeto seleciona as colunas totais do ensino médio para Brasil, regiões e unidades da federação. Os filtros de localização e dependência administrativa foram preservados.

## Fluxo de preparação

O script `scripts/preparar_dados.py` executa as etapas abaixo:

1. baixa os arquivos anuais disponibilizados pelo Inep;
2. localiza a planilha XLSX de cada pacote;
3. seleciona ano, território, localização, dependência e as três taxas do ensino médio;
4. converte as taxas para valores numéricos;
5. classifica o nível geográfico em Brasil, região ou UF;
6. combina os anos;
7. ordena e salva o CSV processado.

As planilhas brutas não foram duplicadas no repositório. O CSV processado foi mantido para permitir que o aplicativo funcione sem novo download.

## Validações

O carregamento da base verifica:

- presença das oito colunas obrigatórias;
- ano numérico;
- taxas entre 0 e 100;
- ausência de duplicidades na chave do recorte;
- existência de linhas completas;
- soma de aprovação, reprovação e abandono próxima de 100, considerando arredondamento.

O arquivo possui 4.105 linhas. Há 3.783 linhas completas e 966 células ausentes entre as três taxas. Os valores ausentes foram mantidos, sem imputação. As linhas completas representam 92,2% do total.

## Recorte principal

Os resultados destacados no README utilizam:

- localização: Total;
- dependência administrativa: Total;
- nível de ensino: ensino médio;
- anos: 2019 a 2025.

## Matriz de monitoramento

A matriz usa dois eixos:

- eixo horizontal: mudança da taxa de abandono entre o ano-base e o ano atual;
- eixo vertical: taxa de abandono no ano atual.

O resultado brasileiro no ano atual funciona como referência horizontal. A variação zero funciona como referência vertical.

As quatro leituras são:

| Leitura | Regra |
|---|---|
| Acima do Brasil e piorou | Taxa acima do Brasil e variação positiva |
| Acima do Brasil, mas melhorou | Taxa acima do Brasil e variação nula ou negativa |
| Até o Brasil, porém piorou | Taxa até o Brasil e variação positiva |
| Até o Brasil e melhorou | Taxa até o Brasil e variação nula ou negativa |

Essa regra ajuda a organizar perguntas. Ela não estima probabilidade, não prevê abandono e não substitui análise técnica local.

## Limitações metodológicas

As taxas são agregadas. Elas não incluem, neste projeto, características individuais, frequência, renda, transporte, trabalho ou outros fatores que poderiam ajudar a estudar mecanismos associados ao abandono.

Por esse motivo, o painel não afirma causalidade e não cria um modelo preditivo. Os resultados de 2020 e 2021 também exigem cautela por causa das condições excepcionais de funcionamento das escolas durante a pandemia.

