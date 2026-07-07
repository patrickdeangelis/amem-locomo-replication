# Resultados da Etapa 2

Este arquivo registra a rodada reduzida de depuracao. A evidencia principal da Entrega 2 esta em `resultados-etapa-2-ratio01.md`, baseada na execucao planejada `--ratio 0.1`.

Data da execucao: 2026-07-07.

## Escopo executado

Foi executada uma replicacao reduzida do A-Mem usando OpenAI API com `gpt-4o-mini`.

O dataset completo `data/locomo10.json` tem 10 samples e 1986 perguntas. A tentativa inicial com `--ratio 0.1` selecionou o sample 0 inteiro, com 419 turnos e 199 perguntas, e foi interrompida apos 333.71s por ser grande demais para smoke inicial.

Para executar a Etapa 2 com custo controlado, foi criada uma subamostra deterministica:

- arquivo: `amem/data/locomo_etapa2_reduced_s2.json`;
- origem: sample 0 do `locomo10.json`;
- sessoes preservadas: sessoes 1 e 2;
- turnos: 35;
- perguntas: 20;
- criterio das perguntas: manter apenas perguntas cuja evidencia pertence as sessoes preservadas;
- distribuicao por categoria: categoria 1 = 2, categoria 2 = 4, categoria 3 = 1, categoria 4 = 8, categoria 5 = 5.

Estes resultados documentam uma execucao experimental reduzida. Eles nao estimam o desempenho geral do A-Mem no LoCoMo.

## Configuracoes

Estes resultados referem-se a execucao pos-correcao, com parametros de reproducao registrados. A execucao anterior, sem seed e com temperatura 0.7, esta preservada em `amem/results/before-correction/` e comparada em `resultados-antes-pos-correcao.md`.

| Campo | Valor |
| --- | --- |
| Backend | OpenAI API |
| Modelo | `gpt-4o-mini` |
| Script | `test_advanced_robust.py` |
| Dataset | `data/locomo_etapa2_reduced_s2.json` |
| Variavel independente | `retrieve_k` |
| Valores testados | 3, 5, 10 |
| Cache de memorias | Separado por backend, modelo e dataset; reusado entre os tres k |
| Seed | `0` |
| Temperatura (categorias 1-4) | `0.0` (greedy, reprodutivel) |
| Temperatura (categoria 5) | `0.5` |
| Bloco `metadata` no JSON | presente (seed, temperaturas, hash do dataset, commit, comando, timestamps) |
| Reprodutibilidade | Sim para o passo de resposta; cache de memorias preservado |

## Resultados agregados

| retrieve_k | perguntas | exact match | F1 medio | BLEU-1 medio | ROUGE-1 F medio | METEOR medio | SBERT medio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 20 | 0.100000 | 0.290785 | 0.257781 | 0.304200 | 0.236831 | 0.488474 |
| 5 | 20 | 0.200000 | 0.439225 | 0.369001 | 0.443436 | 0.363921 | 0.640610 |
| 10 | 20 | 0.150000 | 0.482200 | 0.411441 | 0.484881 | 0.452196 | 0.677841 |

### Interacao da interpretacao com a incerteza

Nesta subamostra, `retrieve_k=10` apresentou os maiores valores agregados de F1, BLEU-1, ROUGE-1 F, METEOR e similaridade SBERT (o exact match ficou em 0.15, abaixo de k=5 que teve 0.20).

Com a execucao reprodutivel (seed=0, temp=0.0), a diferenca entre k=3 e k=10 torna-se (fracamente) significante:

- O delta de F1 medio entre `k=3` e `k=10` e de `0.191` (de `0.291` para `0.482`).
- O IC bootstrap de 95% para a media de F1 em `k=3` e [0.144, 0.454]; em `k=10` e [0.326, 0.650]. A sobreposicao existe, mas e menor do que na execucao anterior.
- O delta pareado entre `k=3` e `k=10` em F1 tem IC 95% de [0.059, 0.352], que nao cruza zero. Isso indica evidencia fraca, dado n=20, de que k=10 supera k=3.

A execucao anterior, sem seed e com temperatura 0.7, mostrava delta de `0.027` com IC [-0.035, 0.097], cruzando zero. A correcao de reprodutibilidade mudou a leitura estatistica de "indistinguivel" para "fracamente significante". A comparacao completa esta em `resultados-antes-pos-correcao.md`.

## Analise por categoria

Cada categoria do LoCoMo tem poucas perguntas nesta subamostra, entao as medias por categoria tem alta variancia. Use como indicador qualitativo, nao como estimativa robusta. (Valores de F1 medio por categoria, execucao pos-correcao.)

| categoria | descricao | n | k=3 | k=5 | k=10 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | single-hop | 2 | 0.0000 | 0.4000 | 0.4000 |
| 2 | temporal | 4 | 0.2576 | 0.2576 | 0.2576 |
| 3 | multi-hop | 1 | 0.0000 | 0.2222 | 0.2222 |
| 4 | open-ended | 8 | 0.4732 | 0.4665 | 0.5739 |
| 5 | adversarial / unanswerable | 5 | 0.2000 | 0.6000 | 0.6000 |

Observacoes:

- A categoria 5 (adversarial) e a unica com exact match nao nulo (0.6 em k=5 e k=10; 0.2 em k=3), porque boa parte das perguntas adversariais recebe "Not mentioned in the conversation" tanto como predicao quanto como referencia. A sensibilidade de k=3 aqui (0.2 vs 0.6) vem da ordenacao semeada das opcoes.
- A categoria 2 (temporal) e a categoria 3 (multi-hop) tem F1 medio baixo e zero exact match nos tres valores de `k`, indicando dificuldade sistematica com raciocinio temporal e multi-hop nesta subamostra.
- A categoria 4 (open-ended) e a que mais responde ao aumento de `k` (0.4732 em k=3 contra 0.5739 em k=10), possivelmente porque perguntas abertas se beneficiam de mais contexto recuperado.
- A categoria 1 (single-hop) em k=3 foi a zero: com poucas memorias e decodificacao greedy, o modelo deu respostas degeneradas para as 2 perguntas single-hop.
- Como cada categoria tem entre 1 e 8 perguntas, nenhuma diferenca entre `k` e testavel de forma significativa por categoria.

## Analise qualitativa de erros

Foram 16 falhas de exact match em 20 perguntas, em cada valor de `k`. Os padroes recorrentes sao:

- Raciocinio temporal: "When did Melanie paint a sunrise?" recebeu "last year" em todos os `k`, com referencia "2022". "When did Melanie run a charity race?" recebeu "Last Saturday, 20 May 2023" contra referencia "The sunday before 25 May 2023". O modelo recupera a informacao, mas nao normaliza datas.
- Identidade e topicos sensiveis: "What is Caroline's identity?" recebeu variacoes de "LGBTQ+ community" em todos os `k`, contra referencia "Transgender woman". O modelo evita o termo especifico, possivelmente por alinhamento de seguranca.
- Falso negativo em pergunta adversarial: em perguntas cuja resposta existe na conversa mas a categoria 5 sugere "Not mentioned in the conversation" como opcao, o modelo as vezes escolhe a opcao negativa, zerando o exact match. Um exemplo e "What are Melanie's plans for the summer with respect to adoption?".
- Parafrase em pergunta aberta: respostas semanticamente corretas, mas com palavras diferentes da referencia, pontuam baixo em F1/BLEU por limitacao da metrica. Um exemplo e "self-care is really important" contra "self-care is important".

## Deltas pareados por pergunta

Para cada par (A para B), o diff corresponde a metrica(B) menos metrica(A) em cada pergunta emparelhada por texto, com IC bootstrap de 95% (10.000 reamostragens, seed=0). Como a subamostra e pequena, os IC sao largos e devem ser lidos como direcao, nao como teste formal. Valores da execucao pos-correcao.

| par | metrica | diff medio | IC 95% | melhorou | piorou | igual |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| k=3 para k=5 | F1 | 0.1484 | [0.012, 0.313] | 6 | 3 | 11 |
| k=3 para k=10 | F1 | 0.1914 | [0.059, 0.352] | 7 | 2 | 11 |
| k=5 para k=10 | F1 | 0.0430 | [0.000, 0.092] | 3 | 0 | 17 |

Na execucao pos-correcao, os IC de F1 para k=3 para k=5 e k=3 para k=10 nao cruzam zero, indicando evidencia fraca, dado n=20, de que aumentar k melhora o F1. O delta de k=5 para k=10 toca zero; portanto, o ganho adicional de 5 para 10 e marginal. A comparacao com a execucao anterior esta em `resultados-antes-pos-correcao.md`.

## Artefatos gerados

- `amem/results/results_amem_gpt4omini_reduced_s2_k3.json` (pos-correcao, com `metadata`)
- `amem/results/results_amem_gpt4omini_reduced_s2_k5.json` (pos-correcao, com `metadata`)
- `amem/results/results_amem_gpt4omini_reduced_s2_k10.json` (pos-correcao, com `metadata`)
- `amem/results/before-correction/` (JSONs da execucao anterior, preservados para auditoria)
- `amem/data/locomo_etapa2_reduced_s2.json`
- `amem/analysis/make_reduced_dataset.py`
- `amem/analysis/summarize_results.py`
- `amem/analysis/estimate_cost.py`
- `amem/analysis/make_manifest.py`
- `amem/analysis/relatorio-etapa-2.md` (pos-correcao)
- `amem/analysis/relatorio-etapa-2-before.md` (antes, preservado)
- `amem/run_etapa2_reduced.sh`
- `manifest-etapa-2.json`
- `resultados-antes-pos-correcao.md`

## Observacoes

- A criacao inicial do cache de memoria foi a parte mais demorada (~300s para 35 turns, na execucao antes). As execucoes pos-correcao reutilizaram o mesmo cache e ficaram em ~92-108s para 20 perguntas cada.
- O cache de memorias foi compartilhado entre os tres valores de `k` e entre as execucoes antes e pos correcao; apenas o passo de recuperacao e resposta variou. Isso isola o efeito das correcoes no passo de resposta.
- O script original nomeava o cache apenas por backend/modelo. Foi ajustado para incluir o nome do dataset e, posteriormente, o hash sha256 do dataset, evitando contaminacao entre datasets.
- O log do script e muito verboso porque grava prompts, contextos recuperados e metricas detalhadas.

## Limitacoes e ameacas a validade

- A subamostra reduzida nao substitui uma reproducao completa do LoCoMo.
- A amostra vem de apenas um dialogo e duas sessoes. Nao ha variabilidade entre dialogos nem entre dias.
- 20 perguntas produzem IC bootstrap largos; mesmo o delta entre k=3 e k=10 (IC [0.059, 0.352]) deve ser lido como evidencia fraca, nao conclusao robusta.
- A execucao pos-correcao e reprodutivel no passo de resposta (seed=0, temp 0.0). A execucao anterior nao era, pois nao usava seed e operava com temp 0.7. A sensibilidade dos resultados a essa mudanca tambem e um achado de reprodutibilidade, documentado em `resultados-antes-pos-correcao.md`.
- A categoria 5 (adversarial) tem exact match altamente sensivel a ordenacao das opcoes, que a seed torna deterministica mas nao resolve como problema de design.
- O cache de memorias foi criado sem seed (a criacao de memoria usa temperatura 0.7 no controlador LLM, nao afetada por `--seed`/`--temperature`); ele e deterministico por estar congelado em disco, nao por ser semeado.
- A comparacao entre `retrieve_k` deve ser apresentada como observacao com IC, nao como ranking definitivo.
