# Replicacao parcial do A-Mem no LoCoMo

Este repositorio contem os artefatos publicaveis da Entrega 2 de Reprodutibilidade em Pesquisa: uma replicacao parcial do A-Mem no benchmark LoCoMo, usando OpenAI API com `gpt-4o-mini` e varredura de `retrieve_k` em `3`, `5` e `10`.

O experimento principal executado usa `amem/data/locomo10.json` com `--ratio 0.1`, selecionando o sample 0 inteiro: 19 sessoes, 419 turnos e 199 perguntas.

## Estrutura

- `amem/`: codigo do A-Mem usado na execucao, scripts de reproducao, dados e JSONs de resultado.
- `amem/analysis/`: scripts de analise, geracao de relatorios, tabelas, figuras, manifest e estimativa de custo.
- `amem/results/`: resultados brutos em JSON. Os arquivos `results_amem_gpt4omini_ratio01_k*.json` sao a evidencia principal.
- `docs/`: comandos executados, manifest auditavel, relatorios e resumo sanitizado de uso/custo da OpenAI API.

## Execucao principal reproduzida

```bash
cd amem
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader -d .cache/nltk \
  punkt punkt_tab wordnet
cp .env.example .env.local
```

Edite `amem/.env.local` e defina `OPENAI_API_KEY`.

Para reproduzir a execucao principal:

```bash
cd amem
./run_etapa2_ratio01.sh
```


Os resultados esperados sao gravados em:

- `amem/results/results_amem_gpt4omini_ratio01_k3.json`
- `amem/results/results_amem_gpt4omini_ratio01_k5.json`
- `amem/results/results_amem_gpt4omini_ratio01_k10.json`

## Smoke test

Para validar ambiente antes da rodada principal:

```bash
cd amem
./run_etapa2_smoke.sh
```

## Analise

Depois de executar ou alterar resultados:

```bash
cd amem
python analysis/summarize_results.py
python analysis/export_article_assets.py
python analysis/make_manifest.py
```

Os relatorios publicados estao em `docs/`.

## Resultados principais

Na execucao de 2026-07-07:

| retrieve_k | F1 | BLEU-1 | Exact match | Duracao |
|---:|---:|---:|---:|---:|
| 3 | 0.2567 | 0.2244 | 0.1005 | 755.474s |
| 5 | 0.3026 | 0.2640 | 0.1206 | 810.171s |
| 10 | 0.3248 | 0.2844 | 0.1357 | 899.266s |

Duracao total registrada: 2464.911s, cerca de 41.1 min.

Uso/custo medido no bucket diario da OpenAI API em 2026-07-07: US$ 0.9153483. A granularidade do export e diaria, portanto esse custo nao deve ser interpretado como atribuicao isolada por configuracao.

## Segredos e dados locais

Este repositorio nao inclui `.env.local`, chaves de API, ambiente virtual, caches de modelo, caches de memorias ou logs locais brutos. Use `.env.example` como modelo.

## Origem

Codigo base: A-Mem, clonado de `https://github.com/WujiangXu/A-mem.git`.

Commit base usado em 2026-07-07: `0c8039f28fdcc08189a23c07a3437d9d2482f9c2`.

Consulte `amem/LICENSE` para a licenca do codigo A-Mem.
