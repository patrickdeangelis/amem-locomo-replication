# Analise dos resultados da Etapa 2

Relatorio gerado por `analysis/summarize_results.py` a partir dos 3 arquivos de resultado listados. As medias por categoria e por pergunta sao calculadas sobre 199 perguntas em 1 sample(s): 0 de locomo10.json com --ratio 0.1. Elas descrevem a execucao planejada desta Entrega 2 e nao devem ser extrapoladas para todo o LoCoMo.

## Visao geral

Metricas agregadas (media) por arquivo, com intervalo de confianca bootstrap de 95% para a media (10.000 reamostragens, seed=0).

| arquivo | k | perguntas | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|---|
| results_amem_gpt4omini_ratio01_k3.json | 3 | 199 | 0.1005 [0.0603, 0.1457] | 0.2567 [0.2086, 0.3054] | 0.2244 [0.1802, 0.2700] | 0.2643 [0.2163, 0.3131] | 0.1924 [0.1489, 0.2364] | 0.4235 [0.3767, 0.4685] |
| results_amem_gpt4omini_ratio01_k5.json | 5 | 199 | 0.1206 [0.0754, 0.1658] | 0.3026 [0.2509, 0.3536] | 0.2640 [0.2166, 0.3116] | 0.3124 [0.2605, 0.3636] | 0.2281 [0.1821, 0.2758] | 0.4733 [0.4257, 0.5190] |
| results_amem_gpt4omini_ratio01_k10.json | 10 | 199 | 0.1357 [0.0905, 0.1859] | 0.3248 [0.2733, 0.3767] | 0.2844 [0.2353, 0.3335] | 0.3330 [0.2811, 0.3853] | 0.2451 [0.1970, 0.2951] | 0.4912 [0.4446, 0.5374] |

## Analise por categoria

Cada categoria do LoCoMo tem poucas perguntas nesta execucao, entao as medias por categoria tem alta variancia. Use como indicador qualitativo, nao como estimativa robusta.

### k=3 (`results_amem_gpt4omini_ratio01_k3.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 32 | 0.0000 | 0.0729 | 0.0648 | 0.0734 | 0.0369 | 0.2727 |
| 2 (temporal) | 37 | 0.0270 | 0.3633 | 0.2686 | 0.3633 | 0.1276 | 0.6314 |
| 3 (multi-hop) | 13 | 0.0000 | 0.0973 | 0.1046 | 0.1276 | 0.0882 | 0.4303 |
| 4 (open-ended) | 70 | 0.0571 | 0.2609 | 0.2205 | 0.2767 | 0.2297 | 0.4119 |
| 5 (adversarial / unanswerable) | 47 | 0.3191 | 0.3360 | 0.3370 | 0.3358 | 0.3225 | 0.3780 |

### k=5 (`results_amem_gpt4omini_ratio01_k5.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 32 | 0.0000 | 0.0957 | 0.0820 | 0.0970 | 0.0548 | 0.3020 |
| 2 (temporal) | 37 | 0.0270 | 0.3991 | 0.2850 | 0.3991 | 0.1194 | 0.6701 |
| 3 (multi-hop) | 13 | 0.0000 | 0.1360 | 0.1326 | 0.1582 | 0.1024 | 0.4581 |
| 4 (open-ended) | 70 | 0.0714 | 0.2922 | 0.2527 | 0.3150 | 0.2671 | 0.4502 |
| 5 (adversarial / unanswerable) | 47 | 0.3830 | 0.4292 | 0.4245 | 0.4295 | 0.4083 | 0.4734 |

### k=10 (`results_amem_gpt4omini_ratio01_k10.json`)

| categoria | n | exact_match | f1 | bleu1 | rouge1_f | meteor | sbert_similarity |
|---|---|---|---|---|---|---|---|
| 1 (single-hop) | 32 | 0.0000 | 0.1524 | 0.1323 | 0.1465 | 0.0759 | 0.3376 |
| 2 (temporal) | 37 | 0.0000 | 0.3587 | 0.2549 | 0.3587 | 0.0944 | 0.6347 |
| 3 (multi-hop) | 13 | 0.0000 | 0.1347 | 0.1152 | 0.1545 | 0.1090 | 0.4647 |
| 4 (open-ended) | 70 | 0.0714 | 0.2977 | 0.2534 | 0.3197 | 0.2544 | 0.4510 |
| 5 (adversarial / unanswerable) | 47 | 0.4681 | 0.5086 | 0.5041 | 0.5089 | 0.5027 | 0.5502 |

## Analise por pergunta (piores e melhores)

Para cada arquivo, as 5 perguntas com menor F1 e as 5 com maior F1. Util para inspecao qualitativa de erros.

### k=3 (`results_amem_gpt4omini_ratio01_k3.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 2 | 3 | 0.0000 | 0 | Career options | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 3 | 1 | 0.0000 | 0 | Caroline attended a LGBTQ support group. | Adoption agencies | What did Caroline research? |
| 4 | 2 | 0.0000 | 0 | next month | June 2023 | When is Melanie planning on going camping? |
| 5 | 1 | 0.0000 | 0 | The context does not provide information about Caroline's re | Single | What is Caroline's relationship status? |
| 6 | 5 | 1.0000 | 1 | Being present and bonding with her family | Being present and bonding with her family | What does Caroline love most about camping with her family? |
| 7 | 5 | 1.0000 | 1 | A sign stating that someone is not being able to leave | A sign stating that someone is not being able to leave | What precautionary sign did Caroline see at the café? |
| 8 | 5 | 1.0000 | 1 | Ed Sheeran | Ed Sheeran | Who is Caroline a fan of in terms of modern music? |
| 9 | 5 | 1.0000 | 1 | In Melanie's slipper | In Melanie's slipper | Where did Oscar hide his bone once? |
| 10 | 5 | 1.0000 | 1 | once or twice a year | once or twice a year | How often does Caroline go to the beach with her kids? |

### k=5 (`results_amem_gpt4omini_ratio01_k5.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | 8 May, 2023 | 2022 | When did Melanie paint a sunrise? |
| 2 | 1 | 0.0000 | 0 | Caroline researched "transgender stories." | Adoption agencies | What did Caroline research? |
| 3 | 1 | 0.0000 | 0 | Caroline's identity includes being part of the LGBTQ communi | Transgender woman | What is Caroline's identity? |
| 4 | 2 | 0.0000 | 0 | next month | June 2023 | When is Melanie planning on going camping? |
| 5 | 1 | 0.0000 | 0 | The context does not provide specific information about Caro | Single | What is Caroline's relationship status? |
| 6 | 5 | 1.0000 | 1 | Being present and bonding with her family | Being present and bonding with her family | What does Caroline love most about camping with her family? |
| 7 | 5 | 1.0000 | 0 | He got into an accident. | He got into an accident | What happened to Caroline's son on their road trip? |
| 8 | 5 | 1.0000 | 1 | It was a transgender poetry reading where transgender people | It was a transgender poetry reading where transgender people | What was the poetry reading that Melanie attended about? |
| 9 | 5 | 1.0000 | 1 | A sign stating that someone is not being able to leave | A sign stating that someone is not being able to leave | What precautionary sign did Caroline see at the café? |
| 10 | 5 | 1.0000 | 1 | Ed Sheeran | Ed Sheeran | Who is Caroline a fan of in terms of modern music? |

### k=10 (`results_amem_gpt4omini_ratio01_k10.json`)

| rank | categoria | F1 | exact | predicao | referencia | pergunta |
|---|---|---|---|---|---|---|
| 1 | 2 | 0.0000 | 0 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 2 | 2 | 0.0000 | 0 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 3 | 1 | 0.0000 | 0 | The context does not provide specific information about Caro | Single | What is Caroline's relationship status? |
| 4 | 2 | 0.0000 | 0 | Not specified. | 4 years | How long has Caroline had her current group of friends for? |
| 5 | 1 | 0.0000 | 0 | The context does not provide information about where Carolin | Sweden | Where did Caroline move from 4 years ago? |
| 6 | 5 | 1.0000 | 1 | Being present and bonding with her family | Being present and bonding with her family | What does Caroline love most about camping with her family? |
| 7 | 5 | 1.0000 | 0 | They are important and mean the world to her. | They are important and mean the world to her | How did Caroline feel about her family after the accident? |
| 8 | 5 | 1.0000 | 1 | He got into an accident | He got into an accident | What happened to Caroline's son on their road trip? |
| 9 | 5 | 1.0000 | 1 | It was a transgender poetry reading where transgender people | It was a transgender poetry reading where transgender people | What was the poetry reading that Melanie attended about? |
| 10 | 5 | 1.0000 | 1 | A sign stating that someone is not being able to leave | A sign stating that someone is not being able to leave | What precautionary sign did Caroline see at the café? |

## Analise qualitativa de erros

Falhas de exact match por arquivo, com a predicao e a referencia. Para categoria 5 (adversarial), uma predicao 'Not mentioned in the conversation' conta como acerto quando a referencia tambem e essa.

### k=3 (`results_amem_gpt4omini_ratio01_k3.json`)

- total de perguntas: 199
- falhas de exact match: 179

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 3 | 0.0000 | Career options | Psychology, counseling certification | What fields would Caroline be likely to pursue in her educaton? |
| 1 | 0.0000 | Caroline attended a LGBTQ support group. | Adoption agencies | What did Caroline research? |
| 2 | 0.0000 | next month | June 2023 | When is Melanie planning on going camping? |
| 1 | 0.0000 | The context does not provide information about Car | Single | What is Caroline's relationship status? |
| 2 | 0.0000 | Not specified. | 4 years | How long has Caroline had her current group of friends for? |
| 1 | 0.0000 | The context does not provide information about whe | Sweden | Where did Caroline move from 4 years ago? |
| 1 | 0.0000 | Gonna continue my edu and check out career options | counseling or mental health for Transgender people | What career path has Caroline decided to persue? |
| 3 | 0.0000 | The context does not provide a definitive answer t | Likely no | Would Caroline still want to pursue counseling as a career if she hadn |
| 1 | 0.0000 | swamped with the kids & work | pottery, camping, painting, swimming | What activities does Melanie partake in? |
| 1 | 0.0000 | The context does not provide specific information  | dinosaurs, nature | What do Melanie's kids like? |
| 2 | 0.0000 | Not mentioned. | 5 July 2023 | When did Melanie go to the museum? |
| 2 | 0.0000 | No mention of a picnic. | The week before 6 July 2023 | When did Caroline have a picnic? |
| 2 | 0.0000 | Not mentioned. | 2022 | When did Melanie read the book "nothing is impossible"? |
| 1 | 0.0000 | Caroline has participated in a LGBTQ support group | Mentoring program, school speech | What events has Caroline participated in to help children? |

### k=5 (`results_amem_gpt4omini_ratio01_k5.json`)

- total de perguntas: 199
- falhas de exact match: 175

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | 8 May, 2023 | 2022 | When did Melanie paint a sunrise? |
| 1 | 0.0000 | Caroline researched "transgender stories." | Adoption agencies | What did Caroline research? |
| 1 | 0.0000 | Caroline's identity includes being part of the LGB | Transgender woman | What is Caroline's identity? |
| 2 | 0.0000 | next month | June 2023 | When is Melanie planning on going camping? |
| 1 | 0.0000 | The context does not provide specific information  | Single | What is Caroline's relationship status? |
| 2 | 0.0000 | Not specified. | 4 years | How long has Caroline had her current group of friends for? |
| 1 | 0.0000 | The context does not provide information about whe | Sweden | Where did Caroline move from 4 years ago? |
| 2 | 0.0000 | 14 August, 2023 | 10 years ago | How long ago was Caroline's 18th birthday? |
| 3 | 0.0000 | It's unclear from the context, but Caroline emphas | Likely no | Would Caroline still want to pursue counseling as a career if she hadn |
| 2 | 0.0000 | Not mentioned. | 5 July 2023 | When did Melanie go to the museum? |
| 2 | 0.0000 | No specific date mentioned for a picnic. | The week before 6 July 2023 | When did Caroline have a picnic? |
| 1 | 0.0000 | Melanie is swamped with the kids & work. | Running, pottery | What does Melanie do to destress? |
| 2 | 0.0000 | Not mentioned. | 2022 | When did Melanie read the book "nothing is impossible"? |
| 1 | 0.0000 | Caroline has participated in a LGBTQ support group | Mentoring program, school speech | What events has Caroline participated in to help children? |
| 1 | 0.0000 | a painting of a sunflower on a canvas | sunset | What did Melanie paint recently? |

### k=10 (`results_amem_gpt4omini_ratio01_k10.json`)

- total de perguntas: 199
- falhas de exact match: 172

| cat | F1 | predicao | referencia | pergunta |
|---|---|---|---|---|
| 2 | 0.0000 | Last year. | 2022 | When did Melanie paint a sunrise? |
| 2 | 0.0000 | Next month. | June 2023 | When is Melanie planning on going camping? |
| 1 | 0.0000 | The context does not provide specific information  | Single | What is Caroline's relationship status? |
| 2 | 0.0000 | Not specified. | 4 years | How long has Caroline had her current group of friends for? |
| 1 | 0.0000 | The context does not provide information about whe | Sweden | Where did Caroline move from 4 years ago? |
| 3 | 0.0000 | It's unclear from the context, but Caroline emphas | Likely no | Would Caroline still want to pursue counseling as a career if she hadn |
| 2 | 0.0000 | This month. | July 2023 | When is Caroline going to the transgender conference? |
| 2 | 0.0000 | Not mentioned. | 5 July 2023 | When did Melanie go to the museum? |
| 2 | 0.0000 | No mention of a picnic. | The week before 6 July 2023 | When did Caroline have a picnic? |
| 2 | 0.0000 | 1:56 pm on 8 May, 2023 | 2022 | When did Melanie read the book "nothing is impossible"? |
| 1 | 0.0000 | Caroline has participated in taking in kids in nee | Mentoring program, school speech | What events has Caroline participated in to help children? |
| 1 | 0.0000 | A painting of a lake sunrise. | sunset | What did Melanie paint recently? |
| 1 | 0.0000 | once or twice a year | 2 | How many times has Melanie gone to the beach in 2023? |
| 1 | 0.0000 | Melanie and her kids made their own pots and clay  | bowls, cup | What types of pottery have Melanie and her kids made? |
| 2 | 0.0000 | 17 August, 2023 | 2022 | When did Caroline and Melanie go to a pride fesetival together? |

### Padroes de erro por categoria (consolidado)

| categoria | descricao | n total | media F1 (min-max entre arquivos) |
|---|---|---|---|
| 1 | 1 (single-hop) | 32 | 0.0729 a 0.1524 |
| 2 | 2 (temporal) | 37 | 0.3587 a 0.3991 |
| 3 | 3 (multi-hop) | 13 | 0.0973 a 0.1360 |
| 4 | 4 (open-ended) | 70 | 0.2609 a 0.2977 |
| 5 | 5 (adversarial / unanswerable) | 47 | 0.3360 a 0.5086 |

## Deltas pareados por pergunta

Para cada par (A para B), o diff corresponde a metrica(B) menos metrica(A) em cada pergunta emparelhada por texto. IC bootstrap de 95% para a media do diff (10.000 reamostragens, seed=0). Como a execucao cobre apenas uma amostra do LoCoMo, os IC devem ser lidos como direcao, nao como teste formal.

### k=3 para k=5 (199 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0201 | [-0.0050, 0.0503] | 6 | 2 | 191 |
| f1 | 0.0459 | [0.0142, 0.0796] | 33 | 24 | 142 |
| bleu1 | 0.0396 | [0.0089, 0.0718] | 39 | 22 | 138 |
| rouge1_f | 0.0481 | [0.0163, 0.0816] | 37 | 23 | 139 |
| meteor | 0.0357 | [0.0052, 0.0682] | 32 | 26 | 141 |
| sbert_similarity | 0.0498 | [0.0180, 0.0828] | 55 | 32 | 112 |

### k=3 para k=10 (199 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0352 | [0.0050, 0.0704] | 9 | 2 | 188 |
| f1 | 0.0681 | [0.0294, 0.1085] | 44 | 22 | 133 |
| bleu1 | 0.0600 | [0.0237, 0.0978] | 47 | 29 | 123 |
| rouge1_f | 0.0687 | [0.0296, 0.1089] | 46 | 25 | 128 |
| meteor | 0.0527 | [0.0167, 0.0909] | 41 | 23 | 135 |
| sbert_similarity | 0.0677 | [0.0324, 0.1053] | 68 | 37 | 94 |

### k=5 para k=10 (199 perguntas emparelhadas)

| metrica | diff medio | IC 95% | melhorou | piorou | igual |
|---|---|---|---|---|---|
| exact_match | 0.0151 | [-0.0151, 0.0452] | 6 | 3 | 190 |
| f1 | 0.0222 | [-0.0143, 0.0596] | 34 | 25 | 140 |
| bleu1 | 0.0204 | [-0.0132, 0.0550] | 36 | 31 | 132 |
| rouge1_f | 0.0206 | [-0.0160, 0.0580] | 34 | 27 | 138 |
| meteor | 0.0170 | [-0.0140, 0.0492] | 31 | 26 | 142 |
| sbert_similarity | 0.0180 | [-0.0151, 0.0525] | 50 | 47 | 102 |

## Rastreabilidade

Todos os arquivos possuem bloco de metadados registrado no proprio JSON (seed, temperaturas, retrieve_k, hash do dataset, commit, comando, timestamps e duracao).

| arquivo | seed | temp. (cat 1-4) | temp_c5 | retrieve_k | commit | dataset_sha256 |
|---|---|---|---|---|---|---|
| results_amem_gpt4omini_ratio01_k3.json | 0 | 0.0 | 0.5 | 3 | 0c8039f28fdc | 79fa87e90f04 |
| results_amem_gpt4omini_ratio01_k5.json | 0 | 0.0 | 0.5 | 5 | 0c8039f28fdc | 79fa87e90f04 |
| results_amem_gpt4omini_ratio01_k10.json | 0 | 0.0 | 0.5 | 10 | 0c8039f28fdc | 79fa87e90f04 |


## Ameacas a validade

- A execucao cobre 1 sample(s) (0) selecionada por `--ratio 0.1`; portanto, nao estima o desempenho geral do A-Mem em todos os dialogos do LoCoMo.
- 199 perguntas produzem IC bootstrap informativos para esta amostra, mas perguntas do mesmo sample/dialogo nao sao independentes; os IC podem subestimar a incerteza entre dialogos.
- A avaliacao usou `temperature_answer=0.0` e `temperature_c5=0.5`. Mesmo com seed registrada, chamadas a API hospedada podem variar em reexecucoes futuras.
- O cache de memorias `cached_memories_robust_openai_gpt-4o-mini_locomo10_79fa87e90f04` foi reutilizado entre valores de k; isso isola a variacao de `retrieve_k`, mas uma reexecucao fria pode divergir se modelo/API/dependencias mudarem.
