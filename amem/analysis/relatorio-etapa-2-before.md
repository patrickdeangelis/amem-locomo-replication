# Analise dos resultados da Etapa 2

Relatorio gerado por `analysis/summarize_results.py` a partir dos 3 arquivos de resultado listados. As medias por categoria e por pergunta sao calculadas sobre 20 perguntas em 1 sample(s): 0 de locomo_etapa2_reduced_s2.json. Elas descrevem a execucao planejada desta Entrega 2 e nao devem ser extrapoladas para todo o LoCoMo.

## Visao geral

Metricas agregadas (media) por arquivo, com intervalo de confianca bootstrap de 95% para a media (10.000 reamostragens, seed=0).

| arquivo | k | perguntas | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|---|
| results_amem_gpt4omini_reduced_s2_k3.json | 3 | 20 | 0.2000 [0.0500, 0.4000] | 0.4521 [0.2934, 0.6214] | 0.3896 [0.2367, 0.5613] | 0.4579 [0.2960, 0.6293] | 0.3784 [0.2236, 0.5476] | 0.6265 [0.4867, 0.7604] |
| results_amem_gpt4omini_reduced_s2_k5.json | 5 | 20 | 0.2000 [0.0500, 0.4000] | 0.4537 [0.2943, 0.6264] | 0.3966 [0.2397, 0.5671] | 0.4653 [0.3084, 0.6341] | 0.3716 [0.2158, 0.5414] | 0.6508 [0.5058, 0.7856] |
| results_amem_gpt4omini_reduced_s2_k10.json | 10 | 20 | 0.2000 [0.0500, 0.4000] | 0.4788 [0.3219, 0.6447] | 0.4037 [0.2502, 0.5713] | 0.4825 [0.3240, 0.6501] | 0.4074 [0.2506, 0.5742] | 0.6753 [0.5360, 0.8021] |

## Analise por categoria

Cada categoria do LoCoMo tem poucas perguntas nesta execucao, entao as medias por categoria tem alta variancia. Use como indicador qualitativo, nao como estimativa robusta.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.3333 | 0.2000 | 0.3333 | 0.1136 | 0.5280 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.1964 | 0.2576 | 0.0629 | 0.6539 |
| 3 (multi-hop) | 1 | 0.0000 | 0.2222 | 0.1667 | 0.2222 | 0.1515 | 0.6808 |
| 4 (open-ended) | 8 | 0.1250 | 0.5154 | 0.4300 | 0.5298 | 0.5024 | 0.6535 |
| 5 (adversarial / unanswerable) | 5 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 0.5837 | 0.5899 |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.3333 | 0.2000 | 0.3333 | 0.1136 | 0.5600 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.1964 | 0.2576 | 0.0629 | 0.6539 |
| 3 (multi-hop) | 1 | 0.0000 | 0.2222 | 0.1429 | 0.2222 | 0.1515 | 0.6238 |
| 4 (open-ended) | 8 | 0.1250 | 0.5195 | 0.4503 | 0.5484 | 0.4854 | 0.7151 |
| 5 (adversarial / unanswerable) | 5 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 0.5837 | 0.5874 |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 2 | 0.0000 | 0.4000 | 0.2500 | 0.4000 | 0.1190 | 0.6332 |
| 2 (temporal) | 4 | 0.0000 | 0.2576 | 0.1964 | 0.2576 | 0.0629 | 0.6492 |
| 3 (multi-hop) | 1 | 0.0000 | 0.2222 | 0.1429 | 0.2222 | 0.1515 | 0.6238 |
| 4 (open-ended) | 8 | 0.1250 | 0.5653 | 0.4556 | 0.5747 | 0.5735 | 0.7602 |
| 5 (adversarial / unanswerable) | 5 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 0.5837 | 0.5874 |

## Analise por pergunta (piores e melhores)

Para cada arquivo, as 5 perguntas com menor F1 e as 5 com maior F1. Util para inspecao qualitativa de erros.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | last year | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | Caroline is part of the LGBTQ+ community. | Transgender woman | What is Caroline's identity? |
| 3 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 4 | 0.0000 | 0 | Caroline's plans for the summer include "taking in kids in n | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 5 | 0.0000 | 0 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 6 | 5 | 1.0000 | 1 | because of their inclusivity and support for LGBTQ+ individu | because of their inclusivity and support for LGBTQ+ individu | Why did Melanie choose the adoption agency? |
| 7 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 8 | 5 | 1.0000 | 1 | self-care is important | self-care is important | What did Caroline realize after her charity race? |
| 9 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 10 | 4 | 0.8571 | 0 | self-care is really important | self-care is important | What did Melanie realize after the charity race? |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | last year | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | Caroline identifies as LGBTQ+. | Transgender woman | What is Caroline's identity? |
| 3 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 4 | 0.0000 | 0 | Caroline is off to go do some research. | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 5 | 0.0000 | 0 | Not mentioned in the conversation. | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 6 | 5 | 1.0000 | 1 | because of their inclusivity and support for LGBTQ+ individu | because of their inclusivity and support for LGBTQ+ individu | Why did Melanie choose the adoption agency? |
| 7 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 8 | 5 | 1.0000 | 1 | self-care is important | self-care is important | What did Caroline realize after her charity race? |
| 9 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 10 | 4 | 0.8571 | 0 | self-care is really important | self-care is important | What did Melanie realize after the charity race? |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | Caroline is a person who helps LGBTQ+ folks with adoption. | Transgender woman | What is Caroline's identity? |
| 3 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 5 | 0.0000 | 0 | Not mentioned in the conversation. | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 5 | 0.0000 | 0 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 6 | 5 | 1.0000 | 1 | because of their inclusivity and support for LGBTQ+ individu | because of their inclusivity and support for LGBTQ+ individu | Why did Melanie choose the adoption agency? |
| 7 | 5 | 1.0000 | 1 | LGBTQ+ individuals | LGBTQ+ individuals | What type of individuals does the adoption agency Melanie is considering support |
| 8 | 5 | 1.0000 | 1 | self-care is important | self-care is important | What did Caroline realize after her charity race? |
| 9 | 4 | 1.0000 | 1 | mental health | mental health | What did the charity race raise awareness for? |
| 10 | 4 | 0.8750 | 0 | Creating a family for kids who need it. | creating a family for kids who need one | What is Caroline excited about in the adoption process? |

## Analise qualitativa de erros

Falhas de exact match por arquivo, com a predicao e a referencia. Para categoria 5 (adversarial), uma predicao 'Not mentioned in the conversation' conta como acerto quando a referencia tambem e essa.

### k=3 (`results_amem_gpt4omini_reduced_s2_k3.json`)

- total de perguntas: 20
- falhas de exact match: 16

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | last year | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | Caroline is part of the LGBTQ+ community. | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 0.0000 | Caroline's plans for the summer include "taking in | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 0.0000 | Not mentioned in the conversation | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 3 | 0.2222 | counseling or working in mental health | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 4 | 0.3333 | LGBTQ+ folks with adoption. | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 4 | 0.3571 | "I chose them 'cause they help LGBTQ+ folks with a | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |
| 2 | 0.3636 | Last Saturday, 20 May 2023. | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 4 | 0.3704 | Researching adoption agencies — it's been a dream  | creating a family for kids who need one | What is Caroline excited about in the adoption process? |
| 4 | 0.5385 | Melanie thinks Caroline is "so kind" and that "you | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 2 | 0.6667 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |
| 1 | 0.6667 | Caroline researched adoption agencies. | Adoption agencies | What did Caroline research? |
| 4 | 0.6667 | Melanie carves out some me-time each day - running | by carving out some me-time each day for activitie | How does Melanie prioritize self-care? |

### k=5 (`results_amem_gpt4omini_reduced_s2_k5.json`)

- total de perguntas: 20
- falhas de exact match: 16

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | last year | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | Caroline identifies as LGBTQ+. | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 4 | 0.0000 | Caroline is off to go do some research. | researching adoption agencies | What are Caroline's plans for the summer? |
| 5 | 0.0000 | Not mentioned in the conversation. | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 3 | 0.2222 | Counseling or working in mental health. | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 4 | 0.3125 | Melanie thinks Caroline is "so kind" and that "you | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 4 | 0.3571 | "I chose them 'cause they help LGBTQ+ folks with a | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |
| 2 | 0.3636 | Last Saturday, 20 May 2023. | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 4 | 0.3704 | Researching adoption agencies — it's been a dream  | creating a family for kids who need one | What is Caroline excited about in the adoption process? |
| 4 | 0.5000 | LGBTQ+ folks | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 2 | 0.6667 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |
| 1 | 0.6667 | Caroline researched adoption agencies. | Adoption agencies | What did Caroline research? |
| 4 | 0.7586 | Carving out some me-time each day - running, readi | by carving out some me-time each day for activitie | How does Melanie prioritize self-care? |

### k=10 (`results_amem_gpt4omini_reduced_s2_k10.json`)

- total de perguntas: 20
- falhas de exact match: 16

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | Caroline is a person who helps LGBTQ+ folks with a | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 5 | 0.0000 | Not mentioned in the conversation. | researching adoption agencies | What are Melanie's plans for the summer with respect to adoption? |
| 5 | 0.0000 | Not mentioned in the conversation | creating a family for kids who need one | What is Melanie excited about in her adoption process? |
| 3 | 0.2222 | Counseling or working in mental health. | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 4 | 0.2727 | Researching adoption agencies — it's been a dream  | researching adoption agencies | What are Caroline's plans for the summer? |
| 4 | 0.3125 | Melanie thinks Caroline is "so kind" and that "you | she thinks Caroline is doing something amazing and | What does Melanie think about Caroline's decision to adopt? |
| 4 | 0.3333 | LGBTQ+ folks with adoption. | LGBTQ+ individuals | What type of individuals does the adoption agency Caroline is consider |
| 2 | 0.3636 | Last Saturday, 20 May 2023. | The sunday before 25 May 2023 | When did Melanie run a charity race? |
| 4 | 0.3704 | I chose them 'cause they help LGBTQ+ folks with ad | because of their inclusivity and support for LGBTQ | Why did Caroline choose the adoption agency? |
| 4 | 0.6000 | Melanie realized that self-care is really importan | self-care is important | What did Melanie realize after the charity race? |
| 2 | 0.6667 | 8 May, 2023 | 7 May 2023 | When did Caroline go to the LGBTQ support group? |
| 4 | 0.7586 | Carving out some me-time each day - running, readi | by carving out some me-time each day for activitie | How does Melanie prioritize self-care? |
| 1 | 0.8000 | Researching adoption agencies. | Adoption agencies | What did Caroline research? |

### Padroes de erro por categoria (consolidado)

| categoria | descricao | n total | media F1 (min-max entre arquivos) |
|---|---|---|---|
| 1 | 1 (single-hop) | 2 | 0.3333 a 0.4000 |
| 2 | 2 (temporal) | 4 | 0.2576 a 0.2576 |
| 3 | 3 (multi-hop) | 1 | 0.2222 a 0.2222 |
| 4 | 4 (open-ended) | 8 | 0.5154 a 0.5653 |
| 5 | 5 (adversarial / unanswerable) | 5 | 0.6000 a 0.6000 |

## Deltas pareados por pergunta

Para cada par (A para B), o diff corresponde a metrica(B) menos metrica(A) em cada pergunta emparelhada por texto. IC bootstrap de 95% para a media do diff (10.000 reamostragens, seed=0). Como a execucao cobre apenas uma amostra do LoCoMo, os IC devem ser lidos como direcao, nao como teste formal.

### k=3 para k=5 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0000 | [0.0000, 0.0000] | 0 | 0 | 20 |
| f1 | 0.0016 | [-0.0293, 0.0296] | 2 | 1 | 17 |
| bleu1 | 0.0069 | [-0.0258, 0.0464] | 2 | 2 | 16 |
| rouge1_f | 0.0074 | [-0.0248, 0.0382] | 3 | 1 | 16 |
| meteor | -0.0068 | [-0.0242, 0.0034] | 2 | 1 | 17 |
| sbert_similarity | 0.0244 | [-0.0031, 0.0600] | 5 | 2 | 13 |

### k=3 para k=10 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0000 | [0.0000, 0.0000] | 0 | 0 | 20 |
| f1 | 0.0266 | [-0.0347, 0.0970] | 5 | 2 | 13 |
| bleu1 | 0.0140 | [-0.0516, 0.0905] | 5 | 3 | 12 |
| rouge1_f | 0.0246 | [-0.0337, 0.0966] | 4 | 2 | 14 |
| meteor | 0.0290 | [-0.0373, 0.1128] | 4 | 2 | 14 |
| sbert_similarity | 0.0488 | [-0.0198, 0.1268] | 7 | 4 | 9 |

### k=5 para k=10 (20 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0000 | [0.0000, 0.0000] | 0 | 0 | 20 |
| f1 | 0.0250 | [-0.0332, 0.0945] | 4 | 2 | 14 |
| bleu1 | 0.0071 | [-0.0650, 0.0864] | 4 | 2 | 14 |
| rouge1_f | 0.0172 | [-0.0350, 0.0864] | 3 | 2 | 15 |
| meteor | 0.0358 | [-0.0284, 0.1188] | 3 | 2 | 15 |
| sbert_similarity | 0.0245 | [-0.0444, 0.1036] | 4 | 4 | 12 |

## Rastreabilidade

Nenhum dos arquivos possui bloco de metadados: eles foram gerados antes da inclusao desse bloco no script. A rastreabilidade vem do `manifest-etapa-2.json`.

| arquivo | seed | temp. (cat 1-4) | temp_c5 | retrieve_k | commit | dataset_sha256 |
|---|---|---|---|---|---|---|
| results_amem_gpt4omini_reduced_s2_k3.json | n/a | n/a | n/a | 3 | n/a | n/a |
| results_amem_gpt4omini_reduced_s2_k5.json | n/a | n/a | n/a | 5 | n/a | n/a |
| results_amem_gpt4omini_reduced_s2_k10.json | n/a | n/a | n/a | 10 | n/a | n/a |


## Ameacas a validade

- A execucao cobre 1 sample(s) (0); portanto, nao estima o desempenho geral do A-Mem em todos os dialogos do LoCoMo.
- 20 perguntas produzem IC bootstrap informativos para esta amostra, mas perguntas do mesmo sample/dialogo nao sao independentes; os IC podem subestimar a incerteza entre dialogos.
- A avaliacao usou `temperature_answer=n/a` e `temperature_c5=n/a`. Mesmo com seed registrada, chamadas a API hospedada podem variar em reexecucoes futuras.
- O cache de memorias `cache nao registrado` foi reutilizado entre valores de k; isso isola a variacao de `retrieve_k`, mas uma reexecucao fria pode divergir se modelo/API/dependencias mudarem.
