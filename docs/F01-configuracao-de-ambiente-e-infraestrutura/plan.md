# F01 — Plano de Implementação: Configuração de Ambiente e Infraestrutura

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.x com dependências do `requirements.txt` instaladas (`pip install -r requirements.txt`)
- Arquivo `PRD.md` e `spec.md` desta feature lidos

---

## Fase 1: Verificar e Finalizar Infraestrutura

**1. Verificar `docker-compose.yml`** — Confirmar que o arquivo existente corresponde à especificação do PRD (imagem `pgvector/pgvector:pg17`, serviço `bootstrap_vector_ext`, healthcheck com `pg_isready`, 5 retries × 10s, timeout 5s). Nenhuma alteração deve ser necessária.

**2. Verificar e corrigir `.env.example`** — Confirmar que o arquivo na raiz contém exatamente as 5 variáveis especificadas (`PROVIDER`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `PDF_PATH`, `CONNECTION_STRING`) com os valores padrão corretos. Ajustar se houver divergência em relação à spec.

---

## Fase 2: Implementar Módulo de Configuração

**3. Criar `src/config.py`** — Implementar a função `get_config()` que executa `load_dotenv()`, valida as variáveis na ordem definida na spec (PROVIDER → valor de PROVIDER → API key do provedor → defaults de PDF_PATH e CONNECTION_STRING) e retorna um `SimpleNamespace` com os valores validados.

**4. Implementar tratamento de erros em `get_config()`** — Para cada condição de erro definida na tabela de Error Handling da spec, imprimir a mensagem exata em `stderr` e chamar `sys.exit(1)`. Cobrir: PROVIDER ausente, PROVIDER inválido, API key ausente para o provedor selecionado.

**5. Integrar `get_config()` nos scripts existentes** — Substituir o `load_dotenv()` e os `os.getenv()` avulsos nos stubs `src/ingest.py`, `src/search.py` e `src/chat.py` pela chamada a `from config import get_config` seguida de `cfg = get_config()` no topo de cada módulo.

---

## Fase 3: Validar

**6. Executar a infraestrutura e verificar saúde** — Rodar `docker compose up -d` e confirmar que o container `postgres_rag` atinge status `healthy` dentro de 60 segundos e que a extensão `vector` está ativa no banco via consulta SQL.

**7. Executar os testes de aceitação da spec** — Rodar os testes unitários de `get_config()` cobrindo: variável ausente, PROVIDER inválido, provider correto retornado, defaults aplicados. Confirmar que todos passam antes de avançar para F02.
