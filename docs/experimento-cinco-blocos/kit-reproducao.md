# Kit de Reprodução do experimento de cinco blocos

Este documento descreve os artefatos necessários para compreender, auditar e
regenerar a análise do experimento sem repetir chamadas à OpenAI API.

## Conteúdo

- `amem/data/locomo10.json`: dataset avaliado.
- `amem/data/README.md`: origem, licença, URL, hash e recorte dos dados.
- `amem/results/entrega3/`: quinze resultados brutos em JSON.
- `amem/commands/entrega3_schedule.json`: agenda dos blocos e cenários.
- `amem/run_entrega3.py`: runner com retomada e execução paga explícita.
- `amem/analysis/`: validação, análise estatística e exportação de derivados.
- `amem/tests/`: testes offline da instrumentação e da análise.
- `amem/requirements.lock.txt`: versões diretas e transitivas do ambiente.
- `article-assets/entrega3/`: tabelas e figuras regeneráveis.
- `docs/experimento-cinco-blocos/`: protocolo, ambiente e planejamento.
- `docs/entrega_3_reprodutibilidade_patrick_santos.pdf`: artigo científico.
- `entrega_3_reprodutibilidade_patrick_santos.tex`: fonte LaTeX do artigo.

O artigo integra o pacote público em PDF e em fonte LaTeX, o que permite
inspecionar e recompilar o manuscrito.

## Reprodução offline

```bash
cd amem
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock.txt
python -m pytest tests -q

python analysis/analyze_entrega3.py results/entrega3/*.json \
  --json-output analysis/entrega3-analysis.json \
  --markdown-output analysis/entrega3-analysis.md

python analysis/export_entrega3_assets.py \
  analysis/entrega3-analysis.json \
  --output-dir ../article-assets/entrega3
```

Esses passos não exigem chave da OpenAI nem geram custo de API.

## Reexecução paga

```bash
cd amem
cp .env.example .env.local
# Defina OPENAI_API_KEY em .env.local
python run_entrega3.py
python run_entrega3.py --execute
```

O modo padrão não chama a API. A opção `--execute` deve ser usada somente após
conferência da agenda, do custo e da credencial.

Novas respostas podem se aproximar dos resultados publicados sem coincidir bit
a bit, pois o backend é hospedado.

## Evidências preservadas

O experimento contém cinco blocos, três cenários por bloco e 199 perguntas por
resultado. A matriz completa possui quinze JSONs válidos.

A auditoria local confirmou:

- identidade e ordem das perguntas entre execuções;
- dataset, modelo, temperaturas, agenda e caches coerentes;
- análise regenerável a partir dos JSONs;
- 31 testes offline públicos aprovados;
- instalação nova com Python 3.11.15;
- ausência de chamadas pagas na regeneração da análise.

## Segurança e limpeza

Não devem ser publicados:

- `.env.local` ou chaves de API;
- `.venv`;
- caches de modelos ou memórias;
- logs locais;
- `__pycache__`;
- arquivos temporários.

O arquivo `.gitignore` exclui esses itens. Antes de uma release, o pacote deve
ser validado novamente a partir de um clone limpo.

## Proveniência e limitações

O commit `0c8039f28fdc...` registrado nos JSONs identifica o código-base
upstream. As modificações locais usadas na coleta ainda não estavam em um
commit; essa limitação retrospectiva não pode ser eliminada.

A agenda foi gerada antes da coleta e confirmada pelos metadados dos quinze
resultados, mas não estava comprovadamente versionada naquele momento.

Os resultados são condicionados ao `sample 0` do LoCoMo. As 199 perguntas
compartilham memória e contexto e não são tratadas como réplicas independentes.

## Publicação

O repositório oficial é:

https://github.com/patrickdeangelis/amem-locomo-replication

O código, os dados, os quinze resultados e os derivados foram publicados no
commit `5b28c7a5c1b9`. A atualização seguinte acrescenta o PDF final, o fonte
LaTeX do artigo e o manifesto de hashes.

Antes da submissão final ainda é necessário:

1. criar tag ou release;
2. testar os links sem autenticação;
3. depositar o kit em plataforma arquivística, quando viável;
4. registrar DOI, quando oferecido pela plataforma;
5. enviar o formulário da disciplina.

As licenças do código, dos dados e dos artefatos locais estão descritas em
`amem/LICENSE`, `amem/data/README.md` e `LICENSE-ARTIFACTS.md`.
