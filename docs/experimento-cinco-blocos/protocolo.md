# Protocolo experimental da Entrega 3

**Versão original:** 1.0, definida em 14 de julho de 2026 antes da coleta

**Adendo pós-execução:** 1.1, registrado em 15 de julho de 2026

**Estado atual:** cinco blocos e quinze avaliações concluídos. O texto normativo abaixo preserva o plano anterior à coleta; o adendo registra execução, desvios e correções sem reescrever retroativamente o protocolo.

## 0. Adendo pós-execução

- A agenda foi gerada deterministicamente antes da coleta com `schedule_seed=20260714`. Ela ainda não estava em um commit Git; foi preservada nos metadados, conferida contra os 15 JSONs e posteriormente incluída no manifesto.
- A hipótese primária é formalizada como `H0: P(d_r > 0) <= 0,5` contra `H1: P(d_r > 0) > 0,5`. Com cinco deltas positivos, o teste exato de sinais unilateral produz `p=1/32=0,03125`.
- Os contrastes secundários usam testes exatos de sinais bilaterais e correção de Holm. O teste de sinais substitui a formulação imprecisa de inversão de sinais da versão 1.0.
- As seeds controlaram a agenda, Python, NumPy e a ordenação local da categoria adversarial. Elas não foram enviadas à OpenAI API e não tornam as respostas hospedadas determinísticas.
- O commit `0c8039f28fdc...` identifica o código-base upstream, não o estado local exato. O código executado continha mudanças ainda não commitadas; essa limitação de proveniência é preservada no artigo.
- Em R1, a memória foi construída e salva, mas o processo falhou por ausência de `punkt_tab` antes de gravar a telemetria da construção. A avaliação foi retomada com o mesmo cache; custo e tempo dessa construção ficaram ausentes.
- O gráfico Q-Q planejado não foi produzido. Shapiro-Wilk e os cinco deltas brutos foram preservados como diagnóstico, sem selecionar o teste principal por normalidade.
- Métricas secundárias, categorias e métricas operacionais foram incluídas na análise regenerada. A duração total do processo é confundida pela construção da memória na primeira posição de cada bloco e é tratada descritivamente.

## 1. Objetivo e escopo

Este protocolo transforma a reprodução parcial da Etapa 2 em um estudo de caso experimental reproduzível. O objetivo é avaliar, no diálogo `sample 0` do LoCoMo, como o número de memórias recuperadas pelo A-Mem (`retrieve_k`) afeta a qualidade das respostas e o custo operacional.

O recorte é deliberado por restrição de orçamento. O estudo **não** estima o desempenho do A-Mem no LoCoMo completo e **não** generaliza seus resultados para outros diálogos. As conclusões serão condicionadas às 199 perguntas do diálogo selecionado.

## 2. Trabalho de referência e sistema avaliado

- Trabalho reproduzido: *A-Mem: Agentic Memory for LLM Agents*.
- Implementação-base: repositório `amem`, fixado no commit registrado nos metadados do projeto.
- Dataset: `amem/data/locomo10.json`.
- Caso estudado: `sample 0`, selecionado deterministicamente por `--ratio 0.1`, com 19 sessões, 419 turnos e 199 perguntas.
- Backend: OpenAI API.
- Modelo: `gpt-4o-mini`.
- Temperaturas: `0.0` para as categorias 1–4 e valor explicitamente registrado para a categoria 5.
- Seed lógica: registrada em cada execução.

## 3. Desenho experimental

### 3.1 Fator, níveis e variáveis de resposta

A variável independente é `retrieve_k`, com três níveis:

- `k=3`;
- `k=5`;
- `k=10`.

A variável dependente primária é o F1 médio das 199 perguntas. As variáveis dependentes secundárias são exact match, BLEU-1, ROUGE-1 F, METEOR e SBERT. Duração, chamadas, tokens de entrada, tokens em cache, tokens de saída e custo estimado serão tratados como métricas operacionais.

### 3.2 Unidade de repetição e blocos

Serão executados cinco blocos de repetição, identificados como `R1` a `R5`. Cada bloco reconstruirá a memória em um namespace de cache próprio e avaliará os três níveis de `k` sobre as mesmas 199 perguntas. Os blocos são unidades repetidas da execução condicionadas ao mesmo diálogo; não representam amostras independentes da população de diálogos do LoCoMo.

O bloco é a unidade de repetição para a comparação entre cenários. As perguntas são casos fixos e correlacionados dentro de um único diálogo; não serão tratadas como 199 réplicas experimentais independentes.

### 3.3 Controles

Dentro de cada bloco permanecerão constantes o dataset e seu hash, o `sample_id`, o modelo, as temperaturas, a implementação, as instruções ao modelo e o cache de memória usado pelos três níveis de `k`. Assim, a comparação dentro do bloco isola o fator de recuperação. Entre blocos, o cache será reconstruído para incorporar a variabilidade da construção da memória.

## 4. Hipóteses

### 4.1 Contraste primário

Para cada bloco `r`, seja:

`d_r = F1 médio(r, k=10) - F1 médio(r, k=3)`.

- **H0:** a distribuição dos deltas pareados não favorece `k=10`; o efeito central é menor ou igual a zero.
- **H1:** `k=10` apresenta F1 médio maior que `k=3` no diálogo avaliado; o efeito central é positivo.

O contraste é unilateral, com `α=0,05`, e foi escolhido antes das novas execuções.

### 4.2 Contrastes secundários e análises exploratórias

- `k=5` versus `k=3` e `k=10` versus `k=5` serão contrastes secundários, com correção de Holm.
- O comportamento por categoria oficial do LoCoMo será exploratório, pois algumas categorias contêm poucas perguntas e existe apenas um diálogo.
- A hipótese operacional é que valores maiores de `k` aumentam duração, tokens e custo. Essa comparação será apresentada com estimativas e variabilidade, sem substituir o desfecho primário.

## 5. Randomização e registro da agenda

Antes da execução principal, um script determinístico deverá gerar uma agenda contendo, para cada bloco, uma permutação de `[3, 5, 10]`. A agenda e a `schedule_seed` serão versionadas antes da coleta.

Regras:

1. cada bloco contém exatamente uma execução de cada nível de `k`;
2. a ordem de `k` é randomizada dentro do bloco;
3. a mesma seed sempre produz a mesma agenda;
4. a ordem efetivamente executada é registrada nos metadados;
5. uma retomada respeita a agenda original e não sobrescreve resultados válidos.

## 6. Instrumentação e proveniência

Cada resultado deverá registrar, no mínimo:

- `replicate_id`, `sample_id`, `retrieve_k` e posição na agenda;
- `schedule_seed`, seed lógica e temperaturas;
- modelo, backend e commit do código;
- hash SHA-256 do dataset e identificador do cache;
- comando, início, fim e duração;
- quantidade de chamadas e tentativas;
- tokens de entrada, tokens em cache e tokens de saída;
- preço de referência e custo estimado;
- status da execução e eventuais desvios do protocolo.

Chaves, prompts com dados sensíveis e o conteúdo de `.env.local` não serão incluídos em logs, resultados ou manifestos públicos.

## 7. Política de falhas, retentativas e exclusões

- Falhas transitórias da API poderão ser repetidas pelo mecanismo automático com limite e espera definidos no código; toda tentativa será contabilizada.
- Se uma unidade `bloco × k` falhar definitivamente, ela será retomada com os mesmos parâmetros, cache e posição lógica da agenda.
- Um arquivo parcial ou que não passe pela validação de esquema não será considerado resultado concluído.
- Um resultado válido nunca será sobrescrito. Reexecuções terão identificador próprio e motivo documentado.
- Não haverá repetição seletiva por desempenho observado nem exclusão de resultados por serem favoráveis ou desfavoráveis às hipóteses.
- Desvios, interrupções, reexecuções e valores operacionais atípicos serão mantidos em um registro de auditoria.
- Se um bloco não puder ser concluído, o conjunto ficará marcado como incompleto. Uma análise com menos de cinco blocos será rotulada exploratória e não será apresentada como confirmação a `α=0,05`.

## 8. Plano de análise

1. Validar completude, hashes, parâmetros, duplicatas, falhas e retentativas antes de observar os contrastes.
2. Gerar uma linha por `replicate_id × k` com métricas agregadas e preservar os resultados por pergunta para auditoria.
3. Para cada bloco, calcular os deltas pareados de F1 entre os cenários.
4. Avaliar o contraste primário com teste exato de sinais unilateral sobre os cinco deltas, sob `H0: P(d_r > 0) <= 0,5`. Com cinco deltas não nulos há resolução mínima unilateral de `p=0,03125`.
5. Aplicar testes exatos de sinais bilaterais aos contrastes secundários e ajustar seus valores de `p` por Holm.
6. Reportar média, mediana, desvio-padrão, IQR, mínimo e máximo por cenário, além de diferença absoluta, diferença relativa, intervalo de confiança de 95% e tamanho de efeito pareado.
7. Inspecionar os cinco deltas com gráfico Q-Q e Shapiro-Wilk apenas como diagnóstico. A decisão primária permanecerá não paramétrica devido ao número reduzido de blocos.
8. Apresentar bootstrap pareado por pergunta somente como análise descritiva condicionada ao diálogo, nunca como inferência para o LoCoMo completo.
9. Apresentar métricas secundárias, categorias e custos separadamente como análises secundárias ou exploratórias.
10. Basear a conclusão no contraste predefinido e explicitar resultados inconclusivos, mesmo quando métricas descritivas sugerirem tendência.

## 9. Limitações e ameaças à validade

- Há um único diálogo; não é possível medir variabilidade entre diálogos nem generalizar para o LoCoMo.
- As 199 perguntas compartilham contexto e memória, portanto não são independentes.
- Cinco blocos oferecem baixa resolução e baixo poder estatístico; ausência de significância não demonstra equivalência.
- A API hospedada, o modelo e a infraestrutura podem mudar ao longo do tempo, apesar do controle de seed e temperatura.
- O custo limita o número de amostras e repetições.
- O estudo compara níveis de `retrieve_k`, não o A-Mem contra todos os baselines do artigo original.
- Exact match, BLEU, ROUGE e métricas semânticas capturam aspectos diferentes e podem discordar.
- Resultados por categoria têm caráter exploratório dentro deste recorte.

## 10. Critérios de conclusão

O protocolo experimental estará cumprido quando:

- a agenda randomizada estiver registrada antes da execução;
- existirem cinco blocos completos e quinze resultados válidos;
- todos os metadados e métricas operacionais estiverem presentes;
- a auditoria não identificar unidades ausentes ou exclusões seletivas;
- a análise for regenerável por comando documentado;
- o artigo restringir suas conclusões ao `sample 0` e registrar qualquer desvio deste protocolo.

Se o orçamento não permitir os cinco blocos, os artefatos e a análise já existentes continuarão válidos como reprodução parcial descritiva, mas o requisito de repetição experimental permanecerá explicitamente não atendido.
