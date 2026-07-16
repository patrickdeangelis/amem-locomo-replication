# Dados do experimento

## LoCoMo

O experimento usa `locomo10.json`, o conjunto de dez conversas publicado pelo
projeto oficial LoCoMo para o trabalho *Evaluating Very Long-Term Conversational
Memory of LLM Agents* (ACL 2024):

- projeto e documentação: https://github.com/snap-research/locomo
- arquivo oficial: https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json
- licença do repositório de origem: Creative Commons Attribution-NonCommercial
  4.0 International (CC BY-NC 4.0), em
  https://github.com/snap-research/locomo/blob/main/LICENSE.txt

O arquivo local foi herdado do repositório-base A-Mem e não foi alterado neste
projeto. Sua identidade local esperada é:

```text
arquivo: data/locomo10.json
tamanho: 2805274 bytes
sha256: 79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4
```

Para obter novamente o dado da fonte oficial:

```bash
curl -L \
  https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json \
  -o data/locomo10.json
shasum -a 256 data/locomo10.json
```

Interrompa a reprodução se o hash diferir do valor acima e registre a versão
obtida: o arquivo oficial pode mudar após o congelamento desta entrega.

## Recorte usado

A Etapa 3 utiliza somente o primeiro diálogo (`sample 0`) do arquivo, com 19
sessões, 419 turnos e 199 perguntas. O arquivo completo é mantido para preservar
a entrada original e permitir a verificação pelo hash; o estudo não afirma
representatividade dos dez diálogos.

Os arquivos `locomo_smoke_min.json` e `locomo_etapa2_reduced_s2.json` são
derivações locais usadas apenas para smoke e histórico da Etapa 2. Eles não
substituem `locomo10.json` na execução principal da Etapa 3.
