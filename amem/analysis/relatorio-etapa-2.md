# Analise dos resultados da Etapa 2

Relatorio gerado por `analysis/summarize_results.py` a partir dos 3 arquivos de resultado listados. As medias por categoria e por pergunta sao calculadas sobre 20 perguntas em 1 sample(s): 0 de locomo_etapa2_reduced_s2.json com --ratio 1.0. Elas descrevem a execucao planejada desta Entrega 2 e nao devem ser extrapoladas para todo o LoCoMo.

## Visao geral

Metricas agregadas (media) por arquivo, com intervalo de confianca bootstrap de 95% para a media (10.000 reamostragens, seed=0).

| arquivo | k | perguntas | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|---|
| results_amem_gpt4omini_reduced_s2_k3.json | 3 | 20 | 0.1000 [0.0000, 0.2500] | 0.2908 [0.1438, 0.4541] | 0.2578 [0.1206, 0.4144] | 0.3042 [0.1520, 0.4729] | 0.2368 [0.1032, 0.3930] | 0.4885 [0.3427, 0.6379] |
| results_amem_gpt4omini_reduced_s2_k5.json | 5 | 20 | 0.2000 [0.0500, 0.4000] | 0.4392 [0.2831, 0.6079] | 0.3690 [0.2201, 0.5372] | 0.4434 [0.2853, 0.6134] | 0.3639 [0.2173, 0.5267] | 0.6406 [0.5007, 0.7706] |
| results_amem_gpt4omini_reduced_s2_k10.json | 10 | 20 | 0.1500 [0.0000, 0.3000] | 0.4822 [0.3256, 0.6502] | 0.4114 [0.2611, 0.5776] | 0.4849 [0.3262, 0.6544] | 0.4522 [0.2935, 0.6166] | 0.6778 [0.5388, 0.8041] |

## Analise por categoria

Cada categoria do LoCoMo tem poucas perguntas nesta execucao, entao as medias por categoria tem alta variancia. Use como indicador qualitativo, nao como estimativa robusta.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2477 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.1964 | 0.2576 | 0.0629 | 0.6539 |
| 3 (multi-hop) | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3446 |
| 4 (open-ended) | 8 | 0.1250 | 0.4732 | 0.4212 | 0.5067 | 0.4435 | 0.6438 |
| 5 (adversarial / unanswerable) | 5 | 0.2000 | 0.2000 | 0.2000 | 0.2000 | 0.1875 | 0.2328 |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.4000 | 0.2500 | 0.4000 | 0.1190 | 0.6927 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.1964 | 0.2576 | 0.0629 | 0.6539 |
| 3 (multi-hop) | 1 | 0.0000 | 0.2222 | 0.1667 | 0.2222 | 0.1515 | 0.6808 |
| 4 (open-ended) | 8 | 0.1250 | 0.4665 | 0.3660 | 0.4770 | 0.4649 | 0.6477 |
| 5 (adversarial / unanswerable) | 5 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 0.5837 | 0.5899 |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.4000 | 0.3333 | 0.4000 | 0.4464 | 0.6594 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.2083 | 0.2576 | 0.1211 | 0.6579 |
| 3 (multi-hop) | 1 | 0.0000 | 0.2222 | 0.1429 | 0.2222 | 0.1515 | 0.6238 |
| 4 (open-ended) | 8 | 0.1250 | 0.5739 | 0.4607 | 0.5806 | 0.5885 | 0.7574 |
| 5 (adversarial / unanswerable) | 5 | 0.4000 | 0.6000 | 0.5800 | 0.6000 | 0.5614 | 0.5847 |

## Analise por pergunta (piores e melhores)

Para cada arquivo, as 5 perguntas com menor F1 e as 5 com maior F1. Util para inspecao qualitativa de erros.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | last year | 2022 | When did Melanie paint a sunrise? |
| 2 | 3 | 0.0000 | 0 | education and career options | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 3 | 1 | 0.0000 | 0 | Caroline researched "career options." | Adoption agencies | What did Caroline research? |
| 4 | 1 | 0.0000 | 0 | Caroline's identity includes being someone who is pursuing a | Transgender woman | What is Caroline's identity? |
| 5 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 6 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 7 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 8 | 4 | 0.8571 | 0 | self-care is really important | self-care is important | What did Melanie realize after the charity race? |
| 9 | 4 | 0.6667 | 0 | Melanie carves out some me-time each day - running, reading, | by carving out some me-time each day for activities like run | How does Melanie prioritize self-care? |
| 10 | 2 | 0.6667 | 0 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | last year | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | LGBTQ+ | Transgender woman | What is Caroline's identity? |
| 3 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 4 | 0.0000 | 0 | Caroline's plans for the summer include taking in kids in ne | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 5 | 0.0000 | 0 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 6 | 5 | 1.0000 | 1 | because of their inclusivity and support for LGBTQ+ individu | because of their inclusivity and support for LGBTQ+ individu | Why did Melanie choose the adoption agency? |
| 7 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 8 | 5 | 1.0000 | 1 | self-care is important | self-care is important | What did Caroline realize after her charity race? |
| 9 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 10 | 1 | 0.8000 | 0 | Researching adoption agencies. | Adoption agencies | What did Caroline research? |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | last year | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | Caroline is an LGBTQ+ individual. | Transgender woman | What is Caroline's identity? |
| 3 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 5 | 0.0000 | 0 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 5 | 0.0000 | 0 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 6 | 5 | 1.0000 | 0 | Because of their inclusivity and support for LGBTQ+ individu | because of their inclusivity and support for LGBTQ+ individu | Why did Melanie choose the adoption agency? |
| 7 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 8 | 5 | 1.0000 | 1 | self-care is important | self-care is important | What did Caroline realize after her charity race? |
| 9 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 10 | 4 | 0.8571 | 0 | self-care is really important | self-care is important | What did Melanie realize after the charity race? |

## Analise qualitativa de erros

Falhas de exact match por arquivo, com a predicao e a referencia. Para categoria 5 (adversarial), uma predicao 'Not mentioned in the conversation' conta como acerto quando a referencia tambem e essa.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

- total de perguntas: 20
- falhas de exact match: 18

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | last year | 2022 | When did Melanie paint a sunrise? |
| 3 | 0.0000 | education and career options | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 1 | 0.0000 | Caroline researched "career options." | Adoption agencies | What did Caroline research? |
| 1 | 0.0000 | Caroline's identity includes being someone who is  | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 0.0000 | Caroline's plans for the summer include "taking in | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 0.0000 | Not mentioned in the conversation | self-care is important | What did Caroline realize after her charity race? |
| 5 | 0.0000 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation. | because of their inclusivity and support for LGBTQ | Why did Melanie choose the adoption agency? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 4 | 0.2353 | Caroline is excited to give kids a loving home. | creating a family for kids who need one | What is Caroline excited about in the adoption process? |
| 4 | 0.3226 | Melanie thinks Caroline is "doing something amazin | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 4 | 0.3333 | LGBTQ+ folks with adoption. | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 2 | 0.3636 | Last Saturday, 20 May 2023. | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 4 | 0.3704 | I chose them 'cause they help LGBTQ+ folks with ad | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

- total de perguntas: 20
- falhas de exact match: 16

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | last year | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | LGBTQ+ | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 0.0000 | Caroline's plans for the summer include taking in  | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 0.0000 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 3 | 0.2222 | counseling or working in mental health | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 4 | 0.3125 | Melanie thinks Caroline is "so kind" and that "her | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 4 | 0.3333 | LGBTQ+ folks with adoption. | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 4 | 0.3571 | "I chose them 'cause they help LGBTQ+ folks with a | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |
| 2 | 0.3636 | Last Saturday, 20 May 2023. | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 4 | 0.3704 | Researching adoption agencies — it's been a dream  | creating a family for kids who need one | What is Caroline excited about in the adoption process? |
| 4 | 0.6000 | Melanie realized that self-care is really importan | self-care is important | What did Melanie realize after the charity race? |
| 2 | 0.6667 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |
| 4 | 0.7586 | Carving out some me-time each day - running, readi | by carving out some me-time each day for activitie | How does Melanie prioritize self-care? |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

- total de perguntas: 20
- falhas de exact match: 17

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | last year | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | Caroline is an LGBTQ+ individual. | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 5 | 0.0000 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 3 | 0.2222 | Counseling or working in mental health. | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 4 | 0.2727 | Researching adoption agencies — it's been a dream  | researching adoption agencies | What are Caroline's plans for the summer? |
| 4 | 0.3125 | Melanie thinks Caroline is "so kind" and that her  | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 4 | 0.3333 | LGBTQ+ folks with adoption. | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 4 | 0.3571 | "I chose them 'cause they help LGBTQ+ folks with a | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |
| 2 | 0.3636 | last Saturday, 20 May 2023 | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 2 | 0.6667 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |
| 4 | 0.7000 | "I'm thrilled to make a family for kids who need o | creating a family for kids who need one | What is Caroline excited about in the adoption process? |
| 4 | 0.7586 | Carving out some me-time each day - running, readi | by carving out some me-time each day for activitie | How does Melanie prioritize self-care? |
| 1 | 0.8000 | Researching adoption agencies | Adoption agencies | What did Caroline research? |

### Padroes de erro por categoria (consolidado)

| categoria | descricao | n total | media F1 (min-max entre arquivos) |
|---|---|---|---|
| 1 | 1 (single-hop) | 2 | 0.0000 a 0.4000 |
| 2 | 2 (temporal) | 4 | 0.2576 a 0.2576 |
| 3 | 3 (multi-hop) | 1 | 0.0000 a 0.2222 |
| 4 | 4 (open-ended) | 8 | 0.4665 a 0.5739 |
| 5 | 5 (adversarial / unanswerable) | 5 | 0.2000 a 0.6000 |

## Deltas pareados por pergunta

Para cada par (A para B), o diff corresponde a metrica(B) menos metrica(A) em cada pergunta emparelhada por texto. IC bootstrap de 95% para a media do diff (10.000 reamostragens, seed=0). Como a execucao cobre apenas uma amostra do LoCoMo, os IC devem ser lidos como direcao, nao como teste formal.

### k=3 para k=5 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.1000 | [0.0000, 0.2500] | 2 | 0 | 18 |
| f1 | 0.1484 | [0.0116, 0.3131] | 6 | 3 | 11 |
| bleu1 | 0.1112 | [-0.0204, 0.2703] | 6 | 3 | 11 |
| rouge1_f | 0.1392 | [0.0013, 0.3064] | 6 | 2 | 12 |
| meteor | 0.1271 | [0.0060, 0.2781] | 7 | 2 | 11 |
| sbert_similarity | 0.1521 | [0.0209, 0.3023] | 8 | 3 | 9 |

### k=3 para k=10 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0500 | [0.0000, 0.1500] | 1 | 0 | 19 |
| f1 | 0.1914 | [0.0585, 0.3521] | 7 | 2 | 11 |
| bleu1 | 0.1537 | [0.0325, 0.3037] | 8 | 2 | 10 |
| rouge1_f | 0.1807 | [0.0456, 0.3444] | 7 | 1 | 12 |
| meteor | 0.2154 | [0.0736, 0.3784] | 8 | 1 | 11 |
| sbert_similarity | 0.1894 | [0.0655, 0.3337] | 9 | 2 | 9 |

### k=5 para k=10 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | -0.0500 | [-0.1500, 0.0000] | 0 | 1 | 19 |
| f1 | 0.0430 | [0.0000, 0.0924] | 3 | 0 | 17 |
| bleu1 | 0.0424 | [0.0010, 0.0941] | 5 | 2 | 13 |
| rouge1_f | 0.0414 | [0.0000, 0.0901] | 3 | 0 | 17 |
| meteor | 0.0883 | [0.0149, 0.1766] | 5 | 1 | 14 |
| sbert_similarity | 0.0372 | [-0.0100, 0.1042] | 4 | 5 | 11 |

## Rastreabilidade

Todos os arquivos possuem bloco de metadados registrado no proprio JSON (seed, temperaturas, retrieve_k, hash do dataset, commit, comando, timestamps e duracao).

| arquivo | seed | temp. (cat 1-4) | temp_c5 | retrieve_k | commit | dataset_sha256 |
|---|---|---|---|---|---|---|
| results_amem_gpt4omini_reduced_s2_k3.json | 0 | 0.0 | 0.5 | 3 | 0c8039f28fdc | ad2c34ec9ee0 |
| results_amem_gpt4omini_reduced_s2_k5.json | 0 | 0.0 | 0.5 | 5 | 0c8039f28fdc | ad2c34ec9ee0 |
| results_amem_gpt4omini_reduced_s2_k10.json | 0 | 0.0 | 0.5 | 10 | 0c8039f28fdc | ad2c34ec9ee0 |


## Ameacas a validade

- A execucao cobre 1 sample(s) (0) selecionada por `--ratio 1.0`; portanto, nao estima o desempenho geral do A-Mem em todos os dialogos do LoCoMo.
- 20 perguntas produzem IC bootstrap informativos para esta amostra, mas perguntas do mesmo sample/dialogo nao sao independentes; os IC podem subestimar a incerteza entre dialogos.
- A avaliacao usou `temperature_answer=0.0` e `temperature_c5=0.5`. Mesmo com seed registrada, chamadas a API hospedada podem variar em reexecucoes futuras.
- O cache de memorias `cached_memories_robust_openai_gpt-4o-mini_locomo_etapa2_reduced_s2` foi reutilizado entre valores de k; isso isola a variacao de `retrieve_k`, mas uma reexecucao fria pode divergir se modelo/API/dependencias mudarem.
