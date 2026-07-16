# Entrega 3 — análise estatística

**Escopo:** Results are conditioned on LoCoMo sample 0 and do not generalize to the full dataset.

## Médias de F1 por execução

| bloco | k | perguntas | F1 médio |
|---:|---:|---:|---:|
| R1 | 3 | 199 | 0.285782 |
| R1 | 5 | 199 | 0.298375 |
| R1 | 10 | 199 | 0.368572 |
| R2 | 3 | 199 | 0.268918 |
| R2 | 5 | 199 | 0.295452 |
| R2 | 10 | 199 | 0.344494 |
| R3 | 3 | 199 | 0.259816 |
| R3 | 5 | 199 | 0.281994 |
| R3 | 10 | 199 | 0.384708 |
| R4 | 3 | 199 | 0.259900 |
| R4 | 5 | 199 | 0.276743 |
| R4 | 10 | 199 | 0.346144 |
| R5 | 3 | 199 | 0.263734 |
| R5 | 5 | 199 | 0.318922 |
| R5 | 10 | 199 | 0.374236 |

## Comparações pareadas por bloco

| comparação | média | mediana | DP | IQR | mín. | máx. | dif. relativa | IC bootstrap 95% | dz | Shapiro-Wilk p |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 3 → 5 | 0.026667 | 0.022178 | 0.016794 | 0.009692 | 0.012593 | 0.055188 | 0.099642 | [0.016210, 0.040938] | 1.5878 | 0.145553 |
| 3 → 10 | 0.096001 | 0.086244 | 0.020808 | 0.027712 | 0.075576 | 0.124892 | 0.358707 | [0.080595, 0.113593] | 4.6137 | 0.406272 |
| 5 → 10 | 0.069334 | 0.069402 | 0.020756 | 0.014883 | 0.049042 | 0.102714 | 0.235591 | [0.055623, 0.086731] | 3.3404 | 0.380896 |

Diferença relativa = média do delta / média de F1 do cenário-base (lado esquerdo do contraste); é n/a quando a média-base é zero.

## Métricas por cenário

| k | exact match | F1 | ROUGE-1 F | METEOR | BERT F1 | SBERT |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 0.093467 | 0.267630 | 0.279333 | 0.199038 | 0.894286 | 0.438117 |
| 5 | 0.110553 | 0.294297 | 0.305085 | 0.221730 | 0.897298 | 0.460274 |
| 10 | 0.145729 | 0.363631 | 0.374413 | 0.273141 | 0.907042 | 0.527424 |

## Métricas operacionais da avaliação por cenário

| k | duração média (s) | DP duração | tokens médios | DP tokens | custo médio (US$) | DP custo |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1034.447 | 737.325 | 370800.4 | 3873.9 | 0.054881 | 0.002277 |
| 5 | 1316.178 | 840.797 | 652938.6 | 14768.8 | 0.096971 | 0.002309 |
| 10 | 1313.490 | 771.536 | 1278731.2 | 34550.6 | 0.189183 | 0.006004 |

## Inferência

O teste exato de sinais unilateral para 3 → 10, com H0: P(delta > 0) <= 0.5, produziu p = 0.031250.

Os testes secundários são bilaterais e seus p-valores foram ajustados por Holm.

| comparação | p bruto | p ajustado por Holm |
|---|---:|---:|
| 3 → 5 | 0.062500 | 0.125000 |
| 5 → 10 | 0.062500 | 0.125000 |

O teste de Shapiro-Wilk é apresentado somente como diagnóstico; com cinco blocos, ele não substitui a inferência exata não paramétrica.
