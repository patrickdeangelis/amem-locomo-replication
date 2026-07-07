# Projeto da Etapa 2

## Objetivo

Executar os experimentos planejados na Etapa 1 para a replicacao parcial do A-Mem em dialogos longos.

Artigo base: A-Mem: Agentic Memory for LLM Agents.

Repositorio usado: `A-mem`, clonado de `https://github.com/WujiangXu/A-mem.git`.

Commit clonado em 2026-07-07: `0c8039f28fdcc08189a23c07a3437d9d2482f9c2`.

## Protocolo experimental

Dataset: `amem/data/locomo10.json`.

Script principal: `amem/test_advanced_robust.py`.

Backend: OpenAI API.

Modelo principal: `gpt-4o-mini`.

Variavel independente: `retrieve_k`.

Configuracoes planejadas:

- `retrieve_k=3`
- `retrieve_k=5`
- `retrieve_k=10`

Fases:

1. Preparar ambiente local e dependencias.
2. Executar smoke test minimo com `data/locomo_smoke_min.json` e `retrieve_k=10`.
3. Se o smoke test minimo produzir saida valida, executar a amostra final para `retrieve_k=3`, `retrieve_k=5` e `retrieve_k=10`.
4. Consolidar metricas agregadas e por categoria.
5. Registrar custo, tempo, divergencias e ameacas a validade.

## Estado em 2026-07-07

O escopo considerado como planejado para esta Entrega 2 e a execucao `--ratio 0.1` sobre `data/locomo10.json`, com `retrieve_k=3,5,10`. As rodadas anteriores ficam documentadas como historico de smoke, depuracao e comparacao de reprodutibilidade.

### Planejado

- Replicacao parcial do A-Mem sobre o LoCoMo com backend OpenAI e `gpt-4o-mini`.
- Varredura de `retrieve_k` em `3`, `5` e `10`.
- Dataset alvo: `data/locomo10.json` com `--ratio 0.1` (sample 0 inteiro, 199 perguntas).
- Metricas: exact match, F1, BLEU-1, ROUGE-1, METEOR, SBERT.
- Analise agregada, por categoria, por pergunta, deltas pareados e IC bootstrap.

### Executado

- Repositorio oficial clonado em `amem`, commit `0c8039f28fdcc08189a23c07a3437d9d2482f9c2`.
- Python 3.11 usado para criar `.venv`.
- Dependencias de `requirements.txt` instaladas.
- Recursos auxiliares em cache local: NLTK `punkt`, `punkt_tab`, `wordnet` e SentenceTransformer `all-MiniLM-L6-v2`.
- Diretorios criados: `results`, `logs`, `commands`, `analysis` e `.cache`.
- Smoke minimo deterministico preservado em `amem/data/locomo_smoke_min.json`: 1 sample, 1 sessao, 8 turnos, 3 perguntas, executado com `retrieve_k=10`.
- Subamostra experimental reduzida preservada em `amem/data/locomo_etapa2_reduced_s2.json`: 1 sample, 2 sessoes, 35 turnos, 20 perguntas, com evidencia restrita as sessoes preservadas.
- A varredura `retrieve_k=3,5,10` sobre a subamostra reduzida foi preservada em duas versoes: antes da correcao, sem seed, temperatura 0.7 e sem metadados, em `amem/results/before-correction/`; e pos-correcao, com seed=0, temperatura 0.0 e bloco `metadata`, em `amem/results/`.
- A execucao principal planejada usou `--ratio 0.1` sobre `data/locomo10.json`, mantendo a rodada reduzida intacta. O recorte selecionou o sample 0 inteiro, com 19 sessoes, 419 turnos e 199 perguntas. Os resultados estao em `amem/results/results_amem_gpt4omini_ratio01_k{3,5,10}.json`, e o relatorio correspondente esta em `resultados-etapa-2-ratio01.md` e `amem/analysis/relatorio-etapa-2-ratio01.md`.
- Na reexecucao `--ratio 0.1` com `caffeinate`, `k=3`, `k=5` e `k=10` reutilizaram o cache existente de 419 memorias.
- Resultados principais consolidados em `resultados-etapa-2-ratio01.md` e `amem/analysis/relatorio-etapa-2-ratio01.md`. A rodada reduzida permanece em `resultados-etapa-2.md`, `resultados-antes-pos-correcao.md` e `amem/analysis/relatorio-etapa-2.md` apenas como historico.
- Uso/custo medido pela OpenAI API para o projeto no dia da execucao: 4.228 chamadas, 5.789.342 tokens de entrada, 106.885 tokens de saida e US$ 0.9153483 em 2026-07-07. A granularidade do export e diaria, portanto o valor pode incluir tentativas e smoke tests do mesmo dia.
- Manifest auditavel em `manifest-etapa-2.json` com hashes sha256 dos artefatos publicados, incluindo JSONs `ratio01`, relatorios, scripts, comandos, parametros e tempos observados. Logs e caches ficaram fora do repositorio publico.

Decisao atual:

- Usar somente OpenAI API.
- Nao usar Ollama como contingencia.

### Fora do escopo atual

- A execucao do dataset completo `data/locomo10.json` (10 samples, 1986 perguntas) NAO foi realizada.
- A tentativa inicial com `--ratio 0.1` selecionou o sample 0 inteiro (419 turnos, 199 perguntas) e foi interrompida manualmente apos 333.71s por ser grande demais para smoke inicial. A execucao `--ratio 0.1` planejada foi realizada depois; a reexecucao com `caffeinate` reutilizou o cache existente para `k=3`, `k=5` e `k=10`.
- Uma execucao futura em escala completa exigiria nova estimativa de custo/tempo com `amem/analysis/estimate_cost.py`. Estimativa central anterior para o dataset completo: ~13h de wall-clock e ~$10 (faixa $7.71-$12.86), com alta incerteza.

## Reprodutibilidade

O script `test_advanced_robust.py` foi corrigido para suportar reprodutibilidade:

- `--seed`: semeia `random` e `numpy`. A categoria 5 (adversarial) usava `random.random()` sem seed para ordenar as opcoes; agora usa um RNG semeado.
- `--temperature`: temperatura para categorias 1-4 (antes hardcoded em `0.7`). Use `0.0` para avaliacao reprodutivel. A categoria 5 continua controlada por `--temperature_c5`.
- O bloco `metadata` agora e gravado dentro de cada JSON de saida: seed, temperaturas, `retrieve_k`, hash sha256 do dataset, commit do repositorio, comando executado, timestamps e duracao.
- O cache de memorias agora e validado pelo hash sha256 do dataset, evitando reutilizacao indevida quando um arquivo e renomeado mantendo o mesmo stem. Na execucao reduzida pos-correcao, o cache legado foi adotado e marcado com `dataset_hash.txt`; na execucao `--ratio 0.1`, o cache novo ficou em `cached_memories_robust_openai_gpt-4o-mini_locomo10_79fa87e90f04`.

Os tres JSONs `results_amem_gpt4omini_ratio01_k*.json` sao a evidencia principal atual da Etapa 2. Os JSONs `results_amem_gpt4omini_reduced_s2_k*.json` preservam a rodada reduzida pos-correcao (seed=0, temp 0.0, com bloco `metadata`), e os JSONs da execucao anterior (sem seed, temp 0.7, sem metadados) estao preservados em `amem/results/before-correction/`. A comparacao entre as duas execucoes reduzidas esta em `resultados-antes-pos-correcao.md`, mas suas conclusoes ficam restritas a subamostra historica de 20 perguntas.

## Artefatos

- `comandos-etapa-2.md`: comandos executados e comandos pendentes.
- `resultados-etapa-2-ratio01.md`: resultados principais da execucao planejada `--ratio 0.1` sobre o sample 0 inteiro do `locomo10.json`.
- `resultados-etapa-2.md`: historico da rodada reduzida pos-correcao, analise por categoria e ameacas a validade.
- `resultados-antes-pos-correcao.md`: comparacao entre a execucao anterior (sem seed, temp 0.7) e a pos-correcao (seed=0, temp 0.0), com problemas encontrados e impacto nas conclusoes.
- `manifest-etapa-2.json`: manifest auditavel com hashes dos artefatos principais, comandos, parametros e tempos.
- `openai-api-usage-2026-07-07.md`: resumo sanitizado dos exports de custo e uso da OpenAI API para o dia da execucao.
- `article-assets/`: tabelas CSV geradas a partir dos JSONs principais para alimentar o artigo da Entrega 2. Os fragmentos LaTeX nao foram incluidos no repositorio publico.
- `figures/`: graficos PDF gerados a partir dos JSONs principais para o artigo da Entrega 2.
- O fonte LaTeX `entrega_2_reprodutibilidade_patrick_santos.tex` foi mantido fora do repositorio publico; o PDF final esta em `paper/`.
- `amem/analysis/relatorio-etapa-2.md`: relatorio de analise pos-correcao gerado por `summarize_results.py`.
- `amem/analysis/relatorio-etapa-2-ratio01.md`: relatorio de analise da execucao `--ratio 0.1`.
- `amem/analysis/relatorio-etapa-2-before.md`: relatorio de analise da execucao anterior (preservado).
- `amem/results/before-correction/`: JSONs da execucao anterior, preservados para auditoria.
- `amem/.env.example`: variaveis esperadas, sem chaves reais.
- `amem/run_etapa2_smoke.sh`: smoke test reproduzivel.
- `amem/run_etapa2_reduced.sh`: execucao reduzida da Etapa 2 para `retrieve_k=3`, `5` e `10`.
- `amem/run_etapa2_ratio01.sh`: execucao `--ratio 0.1` da Etapa 2 para `retrieve_k=3`, `5` e `10`.
- `amem/run_etapa2_final.sh`: script preservado para uma eventual execucao completa futura, fora do escopo atual.
- `amem/analysis/summarize_results.py`: analise agregada, por categoria, por pergunta, deltas pareados e IC bootstrap.
- `amem/analysis/export_article_assets.py`: exporta tabelas CSV e graficos PDF para o artigo a partir dos JSONs `ratio01`.
- `amem/analysis/estimate_cost.py`: estimador de custo/tempo calibrado na execucao reduzida.
- `amem/analysis/make_manifest.py`: gerador do `manifest-etapa-2.json`.
