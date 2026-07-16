# Ambiente da Entrega 3

Registro sanitizado do ambiente usado na coleta de 14 e 15 de julho de 2026. Identificadores do equipamento, números de série e credenciais não fazem parte do kit.

| Recurso | Valor |
|---|---|
| Equipamento | MacBook Pro 2021, identificador de modelo `MacBookPro18,1` |
| Processador | Apple M1 Pro, 10 núcleos (8 de desempenho e 2 de eficiência) |
| Memória | 16 GB de memória unificada |
| Arquitetura | arm64 |
| Sistema operacional | macOS 26.4, build 25E246 |
| Python | 3.11.15 |
| Armazenamento | SSD interno; cerca de 20 GiB livres no momento da auditoria final |
| Backend e modelo | OpenAI API, `gpt-4o-mini` |
| Rede | Conexão à internet necessária somente para chamadas à API e instalação inicial |

As versões diretas e transitivas resolvidas estão em `amem/requirements.lock.txt`. O ambiente virtual, caches de modelos e credenciais são deliberadamente excluídos do pacote público.

Em 15 de julho de 2026, o lockfile foi instalado com sucesso em um ambiente virtual temporário criado do zero com Python 3.11.15. A instalação resolveu 90 pacotes e instalou 88 distribuições sem reutilizar a `.venv` do projeto.

Os JSONs registram plataforma, Python, modelo, parâmetros, tokens e duração de cada execução. CPU e RAM não afetam diretamente a inferência hospedada, mas afetam carregamento de métricas, embeddings e tempo local.
