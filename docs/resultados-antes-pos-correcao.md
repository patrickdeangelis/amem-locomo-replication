# Resultados antes e apos a correcao

Este arquivo registra o historico de reprodutibilidade da rodada reduzida. A evidencia principal da Entrega 2 esta em `resultados-etapa-2-ratio01.md`, baseada na execucao planejada `--ratio 0.1`.

Data: 2026-07-07.

Este documento compara a execucao original (sem seed, temperatura 0.7, sem metadados) com a execucao corrigida (seed=0, temperatura 0.0, com metadados), sobre a mesma subamostra reduzida do LoCoMo (sample 0, sessoes 1-2, 35 turnos, 20 perguntas). O objetivo e mostrar o impacto das correcoes de reprodutibilidade nos resultados e na interpretacao.

## O que foi corrigido e por que

A revisao por subagentes identificou seis problemas na execucao original. A tabela abaixo resume cada problema, o impacto na reprodutibilidade e a correcao aplicada.

| # | Problema encontrado (antes) | Impacto | Correcao aplicada (pos) |
| --- | --- | --- | --- |
| 1 | Categoria 5 usava `random.random()` sem seed para ordenar as opcoes de resposta | A ordem das duas opcoes (resposta vs "Not mentioned") variava entre runs, afetando o exact match das 5 perguntas adversariais | `--seed` semeia `random`/`numpy` e a categoria 5 agora usa um `random.Random(seed)` dedicado |
| 2 | Categorias 1-4 usavam temperatura 0.7 hardcoded | A geracao de resposta era nao deterministica; re-executar poderia dar F1 diferente | `--temperature` (default 0.7; use `0.0` para reprodutivel). A execucao pos usa `0.0` |
| 3 | JSONs de resultado sem bloco de metadados | Impossivel auditar seed, temperatura, hash do dataset, commit ou comando a partir do proprio JSON | O script agora grava `metadata` (seed, temperaturas, retrieve_k, sha256 do dataset, commit, comando, timestamps, duracao) |
| 4 | Cache de memorias nomeado apenas por `dataset_stem` | Renomear um dataset mantendo o stem poderia reutilizar cache de conteudo diferente | O script agora valida o cache pelo sha256 do dataset. Na execucao atual, o cache legado foi adotado e marcado com `dataset_hash.txt`; novos caches podem usar o hash no nome do diretorio |
| 5 | Falta analise por categoria, por pergunta, deltas pareados e IC bootstrap | A interpretacao tratava diferencas pequenas como conclusao sem quantificar incerteza | `analysis/summarize_results.py` reescrito com todas as analises e IC bootstrap |
| 6 | Falta manifest auditavel versionavel | Nao havia ponte versionada para rastreabilidade dos resultados e logs brutos | `manifest-etapa-2.json` com sha256 dos artefatos versionados, commit, comandos, parametros e tempos |

## Configuracoes das duas execucoes

| Campo | Antes | Pos |
| --- | --- | --- |
| Backend | OpenAI API | OpenAI API |
| Modelo | `gpt-4o-mini` | `gpt-4o-mini` |
| Dataset | `data/locomo_etapa2_reduced_s2.json` | `data/locomo_etapa2_reduced_s2.json` (mesmo, sha256 `ad2c34ec9ee0`) |
| Seed | nenhuma | `0` |
| Temperatura (categorias 1-4) | `0.7` (hardcoded) | `0.0` (greedy) |
| Temperatura (categoria 5) | `0.5` | `0.5` |
| Cache de memorias | reusado | reusado (mesmo cache, preservado) |
| Bloco `metadata` no JSON | ausente | presente |
| Commit A-mem | `0c8039f28fdc` | `0c8039f28fdc` (nao commitado ainda no A-mem) |

O cache de memorias foi preservado entre as duas execucoes. So o passo de geracao de resposta mudou (seed + temperatura 0). Isso isola o efeito das correcoes de reprodutibilidade no passo de resposta.

## Resultados agregados antes e apos a correcao

| retrieve_k | metrica | antes | pos | diff |
| ---: | --- | ---: | ---: | ---: |
| 3 | F1 | 0.452115 | 0.290785 | -0.161330 |
| 3 | BLEU-1 | 0.389622 | 0.257781 | -0.131841 |
| 3 | exact match | 0.200000 | 0.100000 | -0.100000 |
| 3 | ROUGE-1 | 0.457889 | 0.304200 | -0.153689 |
| 3 | METEOR | 0.378371 | 0.236831 | -0.141540 |
| 3 | SBERT | 0.626459 | 0.488474 | -0.137985 |
| 5 | F1 | 0.453748 | 0.439225 | -0.014523 |
| 5 | BLEU-1 | 0.396560 | 0.369001 | -0.027559 |
| 5 | exact match | 0.200000 | 0.200000 | 0.000000 |
| 5 | ROUGE-1 | 0.465305 | 0.443436 | -0.021869 |
| 5 | METEOR | 0.371582 | 0.363921 | -0.007661 |
| 5 | SBERT | 0.650829 | 0.640610 | -0.010219 |
| 10 | F1 | 0.478754 | 0.482200 | +0.003446 |
| 10 | BLEU-1 | 0.403669 | 0.411441 | +0.007772 |
| 10 | exact match | 0.200000 | 0.150000 | -0.050000 |
| 10 | ROUGE-1 | 0.482520 | 0.484881 | +0.002361 |
| 10 | METEOR | 0.407350 | 0.452196 | +0.044846 |
| 10 | SBERT | 0.675285 | 0.677841 | +0.002556 |

Observacoes:

- k=3 caiu com a decodificacao greedy (F1 0.452 para 0.291, delta -0.161). A execucao original com temperatura 0.7 gerou respostas melhores em varias perguntas; sem essa aleatoriedade, o k=3 revela-se mais fraco.
- k=5 ficou estavel (F1 0.454 para 0.439, delta -0.015).
- k=10 ficou estavel ou subiu levemente (F1 0.479 para 0.482, delta +0.003; METEOR subiu +0.045). Com mais memorias recuperadas, a decodificacao greedy nao degrada.

## Resultados por categoria antes e apos a correcao

| categoria | descricao | n | k=3 antes | k=3 pos | k=5 antes | k=5 pos | k=10 antes | k=10 pos |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | single-hop | 2 | 0.3333 | 0.0000 | 0.3333 | 0.4000 | 0.4000 | 0.4000 |
| 2 | temporal | 4 | 0.2576 | 0.2576 | 0.2576 | 0.2576 | 0.2576 | 0.2576 |
| 3 | multi-hop | 1 | 0.2222 | 0.0000 | 0.2222 | 0.2222 | 0.2222 | 0.2222 |
| 4 | open-ended | 8 | 0.5154 | 0.4732 | 0.5195 | 0.4665 | 0.5653 | 0.5739 |
| 5 | adversarial | 5 | 0.6000 | 0.2000 | 0.6000 | 0.6000 | 0.6000 | 0.6000 |

Observacoes:

- Categoria 5 em k=3 caiu de 0.6 para 0.2. A unica mudanca relevante nessa categoria foi a ordenacao das opcoes, agora semeada. Isso mostra que o exact match da categoria 5 e sensivel a ordem das opcoes. A seed expoe o problema de design experimental, mas nao o resolve.
- Categoria 1 (single-hop) em k=3 foi a zero. Com poucas memorias e decodificacao greedy, o modelo deu respostas degeneradas para as 2 perguntas single-hop.
- Categorias 2 e 3 em k=3 tambem degradaram. A categoria multi-hop foi a zero. Nesta subamostra, decodificacao greedy com k baixo foi pior.
- k=10 foi menos sensivel a mudanca de temperatura, mantendo ou melhorando quase todas as categorias.

## Deltas pareados de F1 entre k=3 e k=10

| execucao | diff medio de F1 | IC 95% bootstrap | melhorou | piorou | igual | cruza zero? |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| antes (sem seed, temp 0.7) | +0.0266 | [-0.035, 0.097] | 5 | 2 | 13 | sim (nao significante) |
| pos (seed 0, temp 0.0) | +0.1914 | [0.059, 0.352] | 7 | 2 | 11 | nao (significante) |

Efeito observado apos a correcao:

- Antes: a diferenca entre k=3 e k=10 em F1 era +0.027, com IC cruzando zero. Nao era possivel afirmar que k=10 fosse melhor; a conclusao correta era "indistinguivel nesta subamostra".
- Apos a correcao: a diferenca e +0.191, com IC [0.059, 0.352] que nao cruza zero. Ha evidencia fraca, dado n=20, de que k=10 supera k=3.

A correcao de reprodutibilidade tornou os resultados auditaveis e mudou a conclusao estatistica: o efeito de `retrieve_k`, que parecia inexistente, aparece quando o ruido da temperatura 0.7 e removido.

## Rastreabilidade pos-correcao

Os tres JSONs pos-correcao contem, no proprio arquivo, o bloco `metadata`:

| arquivo | seed | temp (cat 1-4) | temp_c5 | retrieve_k | commit | dataset_sha256 | duracao (s) |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| results_amem_gpt4omini_reduced_s2_k3.json | 0 | 0.0 | 0.5 | 3 | 0c8039f28fdc | ad2c34ec9ee0 | 91.6 |
| results_amem_gpt4omini_reduced_s2_k5.json | 0 | 0.0 | 0.5 | 5 | 0c8039f28fdc | ad2c34ec9ee0 | 107.8 |
| results_amem_gpt4omini_reduced_s2_k10.json | 0 | 0.0 | 0.5 | 10 | 0c8039f28fdc | ad2c34ec9ee0 | 93.4 |

Os JSONs da execucao anterior foram preservados em `amem/results/before-correction/` para auditoria. O `manifest-etapa-2.json` registra os hashes dos arquivos antes e pos-correcao.

## Licoes de reprodutibilidade

1. **Aleatoriedade nao controlada pode mascarar efeitos reais.** A temperatura 0.7 adicionava ruido que reduzia a diferenca aparente entre k=3 e k=10; removida, o efeito aparece.
2. **Pequenas amostras amplificam o ruido.** Com n=20, a sensibilidade a seed/temperatura e grande. Em escala completa (n=1986) o efeito seria mais facil de isolar.
3. **Detalhes de implementacao importam.** A ordenacao das opcoes na categoria 5 (um `random.random() < 0.5` invisivel) mudou o exact match de 5 perguntas. Isso e ruido experimental, nao efeito do metodo.
4. **Metadados no JSON sao essenciais.** Sem eles, a execucao "antes" nao era auditavel; so a comparacao com a execucao "pos" (que registra seed/temperatura/hash/commit) permite atribuir a diferenca a correcao.
5. **Conclusoes devem acompanhar a incerteza.** A afirmacao "k=10 e melhor" e direcional na execucao antes (IC cruza zero) e (fracamente) significante na execucao pos (IC nao cruza zero). Apresentar uma sem a outra seria enganoso.

## Artefatos

- `amem/results/results_amem_gpt4omini_reduced_s2_k{3,5,10}.json`: execucao pos-correcao, com `metadata`.
- `amem/results/before-correction/results_amem_gpt4omini_reduced_s2_k{3,5,10}.json`: execucao antes, preservada para comparacao.
- `amem/analysis/relatorio-etapa-2.md`: relatorio de analise da execucao pos-correcao.
- `amem/analysis/relatorio-etapa-2-before.md`: relatorio de analise da execucao anterior.
- `docs/manifest-etapa-2.json`: manifest auditavel com hashes pos-correcao.
