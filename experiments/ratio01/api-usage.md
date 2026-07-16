# Uso e custo OpenAI API em 2026-07-07

Arquivos consultados para gerar este resumo:

- `cost_2026-06-07_2026-07-07.csv`
- `completions_usage_2026-06-07_2026-07-07.csv`

Os exports cobrem o periodo de 2026-06-07 a 2026-07-07, mas contem apenas um dia com uso/custo nao vazio: 2026-07-07.

## Linha de custo

| janela UTC | projeto | organizacao | moeda | custo |
| --- | --- | --- | --- | ---: |
| 2026-07-07T00:00:00 a 2026-07-08T00:00:00 | Default Project | Personal | USD | 0.9153483 |

## Linha de uso

| janela UTC | modelo | tier | batch | chamadas | input tokens | cached input tokens | uncached input tokens | output tokens |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-07-07T00:00:00+00:00 a 2026-07-08T00:00:00+00:00 | gpt-4o-mini-2024-07-18 | default | False | 4,228 | 5,789,342 | 229,120 | 5,560,222 | 106,885 |

## Interpretacao para a Etapa 2

- A execucao principal `--ratio 0.1` ocorreu em 2026-07-07, entre 15:43:03 UTC e 16:24:43 UTC nos metadados dos JSONs.
- O export da API esta agregado por dia, nao pela janela exata da execucao; portanto, o valor `USD 0.9153483` deve ser tratado como custo medido do projeto no dia da execucao, nao como atribuicao minuto-a-minuto exclusivamente da rodada `ratio 0.1`.
- Como os CSVs nao trazem buckets intradiarios, eles podem incluir tentativas, smoke tests ou outros usos do mesmo projeto no mesmo dia.
- Mesmo com essa limitacao, ha agora uma medicao auditavel de custo e tokens faturados para o dia da execucao.
