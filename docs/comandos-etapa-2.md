# Comandos da Etapa 2

Data da preparacao: 2026-07-07.

Diretorio base:

```bash
cd /Users/patrick/obsidian-notes/mestrado/disciplinas/reprodutibilidade-em-pesquisa/projeto-etapa-2/A-mem
```

## Preparacao executada

Clone do repositorio oficial:

```bash
git clone https://github.com/WujiangXu/A-mem.git mestrado/disciplinas/reprodutibilidade-em-pesquisa/projeto-etapa-2/A-mem
```

Commit verificado:

```bash
git rev-parse HEAD
```

Resultado:

```text
0c8039f28fdcc08189a23c07a3437d9d2482f9c2
```

Ambiente Python:

```bash
/Users/patrick/.local/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Caches locais e diretorios de artefatos:

```bash
mkdir -p .cache/huggingface .cache/matplotlib .cache/nltk results logs commands analysis
```

Recursos auxiliares:

```bash
HF_HOME=.cache/huggingface \
MPLCONFIGDIR=.cache/matplotlib \
NLTK_DATA=.cache/nltk \
.venv/bin/python -c "import nltk; nltk.download('punkt', download_dir='.cache/nltk'); nltk.download('punkt_tab', download_dir='.cache/nltk'); nltk.download('wordnet', download_dir='.cache/nltk'); from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('resources ready')"
```

## Smoke test `--ratio 0.1` tentado

```bash
HF_HOME=.cache/huggingface \
MPLCONFIGDIR=.cache/matplotlib \
NLTK_DATA=.cache/nltk \
/usr/bin/time -p .venv/bin/python test_advanced_robust.py \
  --backend openai \
  --model gpt-4o-mini \
  --dataset data/locomo10.json \
  --ratio 0.1 \
  --retrieve_k 10 \
  --output results/results_amem_gpt4omini_smoke_ratio01_k10.json
```

Resultado observado:

```text
Loaded 10 samples
Using 1 samples (10.0% of dataset)
ValueError: OpenAI API key not found. Set OPENAI_API_KEY environment variable.
```

Tempo da tentativa com recursos ja carregados:

```text
real 22.11
user 5.60
sys 1.94
```

Conclusao inicial: a etapa de preparacao e leitura do dataset foi validada. A execucao experimental ficou inicialmente bloqueada por ausencia de `OPENAI_API_KEY`; apos a chave ser configurada em `.env.local` (ignorado pelo git), as execucoes seguintes prosseguiram normalmente.

Depois da chave ficar disponivel, uma nova tentativa com `--ratio 0.1` foi iniciada. Ela acessou a OpenAI API e entrou na fase `Creating new memories`, mas foi interrompida manualmente apos varios minutos sem cache intermediario. O motivo operacional e que `--ratio 0.1` ainda seleciona o sample 0 inteiro, com 419 turnos e 199 perguntas.

Para validar o pipeline com custo controlado antes da execucao final, foi criado um smoke minimo deterministico:

```bash
.venv/bin/python analysis/make_smoke_dataset.py
```

Esse comando gera `data/locomo_smoke_min.json` com 1 sample, 1 sessao, 8 turnos e 3 perguntas.

Primeira execucao do smoke minimo:

- cache de 8 memorias criado com sucesso;
- primeira pergunta respondida;
- falha no calculo de metricas por ausencia do recurso NLTK `punkt_tab`.

Correcao aplicada:

```bash
HF_HOME=.cache/huggingface \
MPLCONFIGDIR=.cache/matplotlib \
NLTK_DATA=.cache/nltk \
.venv/bin/python -c "import nltk; nltk.download('punkt_tab', download_dir='.cache/nltk'); print('punkt_tab ready')"
```

Segunda execucao do smoke minimo:

- cache de memorias reutilizado;
- 3 perguntas respondidas;
- metricas calculadas;
- arquivo produzido: `results/results_amem_gpt4omini_smoke_min_k10.json`;
- tempo observado: `real 74.46`, `user 10.75`, `sys 5.23`.

Correcao adicional de reproducibilidade:

- O script original nomeava cache apenas por backend/modelo.
- Isso poderia reutilizar cache de um dataset em outro dataset.
- Foi ajustado para incluir o nome do dataset no diretorio de cache.

## Decisao de backend

Em 2026-07-07 foi decidido usar somente OpenAI API para a Etapa 2. Ollama nao sera usado como contingencia experimental.

## Comando para retomar

A chave `OPENAI_API_KEY` foi configurada localmente em `amem/.env.local` durante a execucao original. Esse arquivo nao faz parte do repositorio publico. Os scripts `run_etapa2_*.sh` carregam `.env.local` automaticamente quando o arquivo existe.

Executar smoke test:

```bash
./run_etapa2_smoke.sh
```

Executar experimento reduzido:

```bash
.venv/bin/python analysis/make_reduced_dataset.py
./run_etapa2_reduced.sh
```

Executar experimento completo (estimar custo antes):

```bash
.venv/bin/python analysis/estimate_cost.py
./run_etapa2_final.sh
```

Gerar relatorio de analise a partir dos JSONs de resultado:

```bash
.venv/bin/python analysis/summarize_results.py \
  results/results_amem_gpt4omini_reduced_s2_k3.json \
  results/results_amem_gpt4omini_reduced_s2_k5.json \
  results/results_amem_gpt4omini_reduced_s2_k10.json \
  --output analysis/relatorio-etapa-2.md
```

Estimar custo/tempo do dataset completo:

```bash
.venv/bin/python analysis/estimate_cost.py --print-md
```

Regenerar o manifest auditavel (hashes + comandos + parametros):

```bash
.venv/bin/python analysis/make_manifest.py
```

Gerar tabelas CSV e graficos PDF para o artigo da Entrega 2 a partir dos JSONs principais `ratio01`:

```bash
MPLCONFIGDIR=../.cache/matplotlib \
  .venv/bin/python analysis/export_article_assets.py
```

Resultados da execucao reduzida:

```text
arquivo,total_questions,f1_mean,bleu1_mean,exact_match_mean
results_amem_gpt4omini_reduced_s2_k3.json,20,0.452115,0.389622,0.200000
results_amem_gpt4omini_reduced_s2_k5.json,20,0.453748,0.396560,0.200000
results_amem_gpt4omini_reduced_s2_k10.json,20,0.478754,0.403669,0.200000
```

## Execucao planejada `--ratio 0.1` concluida

Comando equivalente executado em 2026-07-07, preservando os resultados reduzidos e usando nomes de saida separados:

```bash
set -a
source .env.local
set +a

for k in 3 5 10; do
  /usr/bin/time -p .venv/bin/python test_advanced_robust.py \
    --backend openai \
    --model gpt-4o-mini \
    --dataset data/locomo10.json \
    --ratio 0.1 \
    --retrieve_k "$k" \
    --seed 0 \
    --temperature 0.0 \
    --output "results/results_amem_gpt4omini_ratio01_k${k}.json"
done
```

O mesmo procedimento ficou encapsulado em `run_etapa2_ratio01.sh`, que carrega `.env.local` quando o arquivo existe.

Reexecucao final feita com `caffeinate` para evitar sleep do computador:

```bash
/usr/bin/caffeinate -dimsu ./run_etapa2_ratio01.sh
```

Escopo efetivo do `--ratio 0.1`: sample 0 inteiro, 19 sessoes, 419 turnos e 199 perguntas.

Arquivos produzidos:

```text
results/results_amem_gpt4omini_ratio01_k3.json
results/results_amem_gpt4omini_ratio01_k5.json
results/results_amem_gpt4omini_ratio01_k10.json
analysis/relatorio-etapa-2-ratio01.md
```

Tempos registrados nos metadados dos JSONs apos a reexecucao com `caffeinate`:

```text
k=3: 755.474s
k=5: 810.171s
k=10: 899.266s
total: 2464.911s
```

Resultados agregados:

```text
arquivo,total_questions,f1_mean,bleu1_mean,exact_match_mean
results_amem_gpt4omini_ratio01_k3.json,199,0.256745,0.224362,0.100503
results_amem_gpt4omini_ratio01_k5.json,199,0.302632,0.264002,0.120603
results_amem_gpt4omini_ratio01_k10.json,199,0.324815,0.284389,0.135678
```

Exports da OpenAI API usados para medir uso/custo do dia da execucao:

```text
/Users/patrick/Downloads/cost_2026-06-07_2026-07-07.csv
/Users/patrick/Downloads/completions_usage_2026-06-07_2026-07-07.csv
```

Resumo do bucket diario `2026-07-07T00:00:00` a `2026-07-08T00:00:00`:

```text
modelo: gpt-4o-mini-2024-07-18
chamadas: 4228
input_tokens: 5789342
input_cached_tokens: 229120
input_uncached_tokens: 5560222
output_tokens: 106885
custo: USD 0.9153483
```

Observacao: os exports estao agregados por dia. O custo e uma medicao real da API para o projeto no dia da execucao, mas nao isola a janela intradiaria da reexecucao `ratio 0.1`.

Script preservado para eventual execucao completa futura, fora do escopo atual:

```bash
./run_etapa2_final.sh
```
