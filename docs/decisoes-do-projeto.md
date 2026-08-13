# Decisões do projeto

## Por que usar dados reais

O Inep disponibiliza as Taxas de Rendimento Escolar com período, território e recortes suficientes para uma análise reproduzível. Como a fonte é pública e rastreável, não havia necessidade de criar uma base sintética.

## Por que não prever abandono

Uma previsão responsável exigiria observações compatíveis com o fenômeno previsto e variáveis explicativas adequadas. Esta base contém taxas agregadas por território. Ela não contém histórico individual de estudantes nem fatores de contexto suficientes para estimar risco individual.

Aplicar um classificador nessa base produziria uma demonstração tecnicamente fraca e difícil de defender. O projeto foi direcionado para análise exploratória, comparação territorial e monitoramento descritivo.

## Por que não imputar valores ausentes

Preencher uma taxa oficial ausente com média ou zero criaria um valor que não foi publicado. O painel trabalha somente com linhas completas para cada visualização e informa a cobertura da base.

## Por que separar abandono e evasão

O nome do repositório foi preservado para manter seu histórico, mas o painel usa o nome do indicador oficial. Essa escolha evita apresentar uma medida anual como se fosse acompanhamento longitudinal.

## Por que usar uma matriz simples

A matriz de monitoramento foi construída com duas variáveis fáceis de explicar:

1. taxa atual comparada com o Brasil;
2. mudança desde o ano-base.

Não há peso oculto nem nota composta. O objetivo é organizar perguntas, não emitir diagnóstico automático.

## Por que não usar um mapa

O ranking completo das 27 UFs preserva os valores e permite comparação mais precisa. Um mapa seria visualmente atraente, mas exigiria uma camada geográfica adicional e poderia dificultar a leitura de diferenças pequenas. Para este problema, barras ordenadas comunicam melhor a magnitude.

## Como o projeto demonstra Ciência de Dados

- aquisição de dados públicos;
- transformação reproduzível;
- validação de esquema e qualidade;
- análise temporal e territorial;
- construção de indicadores interpretáveis;
- visualização interativa;
- comunicação de incertezas e limites;
- testes automatizados.

