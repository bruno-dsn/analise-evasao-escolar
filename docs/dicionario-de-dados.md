# Dicionário de dados

Arquivo: `data/taxas_rendimento_ensino_medio_2019_2025.csv`

| Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `ano` | inteiro | Ano de referência do indicador | `2025` |
| `unidade_geografica` | texto | Brasil, região ou unidade da federação | `Amapá` |
| `nivel_geografico` | texto | Nível territorial do registro | `UF` |
| `localizacao` | texto | Total, urbana ou rural | `Rural` |
| `dependencia` | texto | Recorte da dependência administrativa | `Estadual` |
| `taxa_aprovacao` | decimal | Percentual de aprovação | `94.8` |
| `taxa_reprovacao` | decimal | Percentual de reprovação | `3.0` |
| `taxa_abandono` | decimal | Percentual de abandono | `2.2` |

## Chave do recorte

Uma linha é identificada pela combinação de:

`ano + unidade_geografica + nivel_geografico + localizacao + dependencia`

## Valores ausentes

Alguns cruzamentos não possuem as três taxas publicadas. Eles permanecem vazios no CSV e são excluídos somente da visualização que exige aquele valor. O projeto não preenche dados ausentes com média, zero ou estimativa.

## Unidade das taxas

As taxas estão armazenadas como percentuais, não como proporções. Portanto, `2.2` significa 2,2%, e não 220%.

