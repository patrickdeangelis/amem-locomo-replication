# Estudos experimentais do A-Mem no LoCoMo

Este repositório público reúne código, dados, resultados e documentação de
estudos experimentais sobre o A-Mem no benchmark LoCoMo.

O projeto é um arquivo evolutivo de reprodutibilidade. Novas atividades podem
acrescentar protocolos, análises e publicações sem apagar o histórico das
execuções anteriores.

## Objetivo

O objetivo é investigar como configurações do A-Mem afetam a qualidade das
respostas, o custo e o comportamento operacional em conversas longas.

O estudo mais recente é uma replicação parcial do método e dos artefatos do
A-Mem, com uma análise de sensibilidade de `retrieve_k`. Os níveis comparados
são 3, 5 e 10 memórias recuperadas por consulta.

## Escopo atual

O experimento usa o `sample 0` do LoCoMo: 19 sessões, 419 turnos e 199
perguntas, com OpenAI API e `gpt-4o-mini`.

O recorte foi adotado por restrição de custo. Os resultados descrevem o diálogo
avaliado e não estimam o desempenho médio no LoCoMo completo.

Foram executados cinco blocos de repetição. Cada bloco avaliou os três níveis de
`retrieve_k`, totalizando quinze resultados completos.

## Estrutura

- `amem/`: implementação, dados, dependências e scripts de execução.
- `amem/results/entrega3/`: quinze resultados brutos do estudo de cinco blocos.
- `amem/analysis/`: análise estatística, exportadores e validadores.
- `amem/tests/`: testes offline da instrumentação e da análise.
- `article-assets/entrega3/`: tabelas e figuras derivadas dos JSONs.
- `docs/experimento-cinco-blocos/`: protocolo, ambiente, plano e inventário.
- `docs/`: artigos e registros das atividades.
- `entrega_3_reprodutibilidade_patrick_santos.tex`: fonte LaTeX do artigo atual.

Os resultados históricos são preservados para auditoria. Arquivos anteriores a
correções metodológicas ficam separados e não substituem os resultados atuais.

## Reprodução offline

A análise publicada pode ser regenerada sem chave da OpenAI e sem novas
chamadas pagas.

Recomenda-se Python 3.11.

```bash
cd amem
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock.txt
python -m pytest tests -q
```

Regere a análise a partir dos quinze JSONs:

```bash
python analysis/analyze_entrega3.py results/entrega3/*.json \
  --json-output analysis/entrega3-analysis.json \
  --markdown-output analysis/entrega3-analysis.md

python analysis/export_entrega3_assets.py \
  analysis/entrega3-analysis.json \
  --output-dir ../article-assets/entrega3
```

Os resultados regenerados podem ser comparados com
`amem/analysis/entrega3-analysis.json` e com os derivados publicados.

## Reexecução do experimento

Copie o modelo de configuração antes de qualquer chamada à API:

```bash
cd amem
cp .env.example .env.local
```

Defina `OPENAI_API_KEY` em `.env.local`. Esse arquivo é local e não deve ser
versionado.

O runner não chama a API no modo padrão. Ele apenas confere ou gera a agenda:

```bash
python run_entrega3.py
```

A repetição paga exige uma decisão explícita:

```bash
python run_entrega3.py --execute
```

Chamadas futuras podem gerar custo e não precisam produzir respostas idênticas
bit a bit, pois o backend é hospedado. O custo total observado foi estimado em
US$ 2,52.

## Resultados principais

As médias de F1 entre os cinco blocos foram 0,2676 para `k=3`, 0,2943 para
`k=5` e 0,3636 para `k=10`.

O contraste primário `k=10 - k=3` apresentou ganho médio de 0,0960. Os cinco
deltas foram positivos, com teste exato de sinais unilateral
`p=0,03125`.

As conclusões são condicionadas ao diálogo estudado. Elas não demonstram
superioridade geral do A-Mem nem substituem uma avaliação no LoCoMo completo.

## Documentação

- [Artigo científico atual](docs/entrega_3_reprodutibilidade_patrick_santos.pdf)
- [Fonte LaTeX do artigo](entrega_3_reprodutibilidade_patrick_santos.tex)
- [Protocolo do estudo de cinco blocos](docs/experimento-cinco-blocos/protocolo.md)
- [Inventário do Kit de Reprodução](docs/experimento-cinco-blocos/kit-reproducao.md)
- [Ambiente de execução](docs/experimento-cinco-blocos/ambiente.md)
- [Manifesto de hashes](manifest-artifacts.json)
- [Documentação das atividades anteriores](docs/README.md)
- [Resultados históricos do primeiro recorte](docs/resultados-etapa-2-ratio01.md)

O artigo é publicado em PDF e em fonte LaTeX, permitindo sua inspeção e
recompilação.

Para recompilar o manuscrito a partir da raiz do repositório:

```bash
tectonic entrega_3_reprodutibilidade_patrick_santos.tex
```

## Segurança, dados e licenças

O repositório não deve conter chaves de API, `.env.local`, ambientes virtuais,
caches de modelos, caches de memórias ou logs locais brutos.

A origem, licença, URL e hash do dataset estão em
[`amem/data/README.md`](amem/data/README.md).

O código-base deriva do
[A-Mem](https://github.com/WujiangXu/A-mem), no commit
`0c8039f28fdcc08189a23c07a3437d9d2482f9c2`.

Consulte [`amem/LICENSE`](amem/LICENSE) para o código-base e
[`LICENSE-ARTIFACTS.md`](LICENSE-ARTIFACTS.md) para dados, documentação,
resultados e derivados.
