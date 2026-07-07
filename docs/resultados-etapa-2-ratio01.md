# Resultados da Etapa 2 com `--ratio 0.1`

Data da execucao: 2026-07-07. Reexecutado com `caffeinate` em 2026-07-07 para evitar sleep do computador.

Esta execucao manteve a rodada reduzida anterior intacta e executou o protocolo planejado para a Entrega 2 com `--ratio 0.1` sobre `amem/data/locomo10.json`.

## Escopo

O `--ratio 0.1` selecionou 1 dos 10 samples do LoCoMo:

| campo | valor |
| --- | ---: |
| samples | 1 |
| sessoes | 19 |
| turnos | 419 |
| perguntas | 199 |

Distribuicao por categoria:

| categoria | n |
| ---: | ---: |
| 1 | 32 |
| 2 | 37 |
| 3 | 13 |
| 4 | 70 |
| 5 | 47 |

Configuracao comum: OpenAI API, `gpt-4o-mini`, `seed=0`, `temperature_answer=0.0`, `temperature_c5=0.5`, dataset sha256 `79fa87e90f04`.

## Arquivos

- `amem/results/results_amem_gpt4omini_ratio01_k3.json`
- `amem/results/results_amem_gpt4omini_ratio01_k5.json`
- `amem/results/results_amem_gpt4omini_ratio01_k10.json`
- `amem/analysis/relatorio-etapa-2-ratio01.md`

O cache usado na execucao foi preservado no vault local, mas nao foi incluido neste repositorio publico.

## Tempos

| retrieve_k | duracao registrada |
| ---: | ---: |
| 3 | 755.474s (12.6min) |
| 5 | 810.171s (13.5min) |
| 10 | 899.266s (15.0min) |
| total | 2464.911s (41.1min) |

A reexecucao com `caffeinate` reutilizou o cache existente de 419 memorias para `k=3`, `k=5` e `k=10`.

## Uso e custo medidos via OpenAI API

Exports consultados:

- `cost_2026-06-07_2026-07-07.csv`
- `completions_usage_2026-06-07_2026-07-07.csv`

Os exports cobrem 2026-06-07 a 2026-07-07 e possuem apenas uma linha nao vazia, referente ao dia 2026-07-07. Esse bucket diario coincide com o dia da execucao `--ratio 0.1`, mas nao permite isolar a janela de 15:43:03 UTC a 16:24:43 UTC minuto a minuto.

| janela UTC | modelo | chamadas | input tokens | cached input tokens | uncached input tokens | output tokens | custo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-07-07T00:00:00 a 2026-07-08T00:00:00 | `gpt-4o-mini-2024-07-18` | 4,228 | 5,789,342 | 229,120 | 5,560,222 | 106,885 | US$ 0.9153483 |

Interpretacao: o custo real do projeto no dia da execucao foi medido pela API como US$ 0.9153483. Como a granularidade exportada e diaria, esse valor pode incluir tentativas, smoke tests ou outros usos do mesmo projeto em 2026-07-07; por isso, ele e reportado como custo diario medido associado ao dia da execucao, nao como atribuicao exclusiva por minuto da rodada final.

## Resultados agregados

| retrieve_k | perguntas | exact match | F1 medio | BLEU-1 medio | ROUGE-1 F medio | METEOR medio | SBERT medio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 199 | 0.1005 | 0.2567 | 0.2244 | 0.2643 | 0.1924 | 0.4235 |
| 5 | 199 | 0.1206 | 0.3026 | 0.2640 | 0.3124 | 0.2281 | 0.4733 |
| 10 | 199 | 0.1357 | 0.3248 | 0.2844 | 0.3330 | 0.2451 | 0.4912 |

## Deltas pareados em F1

| par | diff medio | IC 95% | melhorou | piorou | igual |
| --- | ---: | --- | ---: | ---: | ---: |
| k=3 para k=5 | 0.0459 | [0.0142, 0.0796] | 33 | 24 | 142 |
| k=3 para k=10 | 0.0681 | [0.0294, 0.1085] | 44 | 22 | 133 |
| k=5 para k=10 | 0.0222 | [-0.0143, 0.0596] | 34 | 25 | 140 |

Nesta execucao, `k=10` tem melhor desempenho agregado em F1, BLEU-1, ROUGE-1 F, METEOR e SBERT. A conclusao ainda deve ser limitada ao sample 0: ha mais perguntas que na subamostra customizada, mas ainda apenas um dialogo.

## Limitacoes

- `--ratio 0.1` nao representa 10% estratificado por pergunta; ele seleciona 1 sample inteiro.
- Todas as 199 perguntas pertencem ao mesmo dialogo, entao os intervalos bootstrap por pergunta podem subestimar incerteza.
- O custo foi medido por export da API apenas em granularidade diaria; nao ha atribuicao intradiaria exclusiva para a janela da reexecucao final.
- Reexecucao fria pode divergir se o cache de memorias for recriado no futuro com uma versao diferente do modelo/API.
