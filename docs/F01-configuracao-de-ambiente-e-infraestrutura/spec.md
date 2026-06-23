# F01 — Configuração de Ambiente e Infraestrutura

## Scope

### Included
- `docker-compose.yml` com serviço `postgres` (pgvector/pgvector:pg17) e serviço `bootstrap_vector_ext` que habilita a extensão `vector` automaticamente após o healthcheck passar — **já implementado**
- `.env.example` na raiz do projeto contendo as 4 variáveis obrigatórias/opcionais com valores padrão
- `src/config.py` — módulo compartilhado com a função `get_config()` que carrega o `.env`, valida as variáveis obrigatórias, verifica o valor de `PROVIDER` e retorna um objeto de configuração pronto para uso

### Input Contracts
- Nenhuma dependência de outra feature (F01 é Foundation)

### Output Contracts
Fornece para F02 e F03:
- `CONNECTION_STRING` — string de conexão PostgreSQL com driver psycopg
- `PROVIDER` — valor validado `"openai"` ou `"gemini"`
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY` — chave do provedor selecionado
- `PDF_PATH` — caminho para o arquivo PDF a ser ingerido

---

## Component Overview

| Arquivo | Status | Responsabilidade |
|---|---|---|
| `docker-compose.yml` | Já implementado | Sobe PostgreSQL + pgVector e habilita a extensão `vector` |
| `.env.example` | Já existe (verificar conteúdo) | Template de configuração para o desenvolvedor |
| `src/config.py` | **A criar** | Carrega `.env`, valida variáveis, expõe `get_config()` |

### `src/config.py` — estrutura da função

```
get_config() -> ConfigNamespace
  ├── load_dotenv()
  ├── valida PROVIDER (obrigatório, deve ser "openai" ou "gemini")
  ├── valida chave de API do provedor selecionado (OPENAI_API_KEY ou GOOGLE_API_KEY)
  ├── resolve PDF_PATH (default: "document.pdf")
  ├── resolve CONNECTION_STRING (default: "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
  └── retorna SimpleNamespace com: provider, api_key, pdf_path, connection_string
```

---

## Requirements

### Carregamento de variáveis
- `load_dotenv()` deve ser chamado antes de qualquer `os.getenv()`, permitindo que o `.env` sobrescreva variáveis de ambiente do sistema
- As variáveis são lidas exclusivamente via `os.getenv()`

### Variáveis obrigatórias sem default
- `PROVIDER`: obrigatório, sem default — ausência provoca saída com código 1
- `OPENAI_API_KEY`: obrigatório somente quando `PROVIDER=openai` — ausência provoca saída com código 1
- `GOOGLE_API_KEY`: obrigatório somente quando `PROVIDER=gemini` — ausência provoca saída com código 1

### Variáveis com default
- `PDF_PATH`: default `"document.pdf"` quando não definida
- `CONNECTION_STRING`: default `"postgresql+psycopg://postgres:postgres@localhost:5432/rag"` quando não definida

### Validação de PROVIDER
- Aceita somente os valores literais `"openai"` ou `"gemini"` (case-sensitive)
- Qualquer outro valor (incluindo variações de capitalização como `"OpenAI"`) é inválido

### Ordem de validação em `get_config()`
1. Verificar presença de `PROVIDER`
2. Verificar que o valor de `PROVIDER` é `"openai"` ou `"gemini"`
3. Verificar presença da chave de API do provedor selecionado
4. Resolver `PDF_PATH` (com default)
5. Resolver `CONNECTION_STRING` (com default)

### Uso nos scripts
- `src/ingest.py`, `src/search.py` e `src/chat.py` devem chamar `get_config()` no topo (antes de instanciar qualquer cliente LangChain ou de banco de dados)
- `get_config()` imprime a mensagem de erro e chama `sys.exit(1)` internamente — o script chamador não precisa tratar exceções

### `.env.example`
Deve conter exatamente:
```
PROVIDER=openai
OPENAI_API_KEY=
GOOGLE_API_KEY=
PDF_PATH=document.pdf
CONNECTION_STRING=postgresql+psycopg://postgres:postgres@localhost:5432/rag
```

---

## Error Handling

Derivado do bloco **Error Handling** do PRD F01:

| Condição | Mensagem impressa | Exit code |
|---|---|---|
| `PROVIDER` ausente | `"Variável de ambiente PROVIDER não encontrada. Copie .env.example para .env e preencha os valores obrigatórios."` | 1 |
| `PROVIDER` com valor inválido | `"Valor inválido para PROVIDER: '[valor]'. Use 'openai' ou 'gemini'."` | 1 |
| `OPENAI_API_KEY` ausente (quando `PROVIDER=openai`) | `"Variável de ambiente OPENAI_API_KEY não encontrada. Copie .env.example para .env e preencha os valores obrigatórios."` | 1 |
| `GOOGLE_API_KEY` ausente (quando `PROVIDER=gemini`) | `"Variável de ambiente GOOGLE_API_KEY não encontrada. Copie .env.example para .env e preencha os valores obrigatórios."` | 1 |

Todos os erros são impressos em `stderr` (via `print(..., file=sys.stderr)`) antes do `sys.exit(1)`.

---

## Testing Strategy

### Testes de aceitação (dos critérios de aceitação do PRD Seção 9 — F01)

```
test_missing_provider_exits_with_code_1
  Dado: .env sem PROVIDER
  Quando: get_config() é chamada
  Então: mensagem "Variável de ambiente PROVIDER não encontrada..." impressa em stderr
         sys.exit(1) levantado

test_invalid_provider_exits_with_code_1
  Dado: PROVIDER="aws" (ou qualquer valor inválido)
  Quando: get_config() é chamada
  Então: mensagem "Valor inválido para PROVIDER: 'aws'..." impressa em stderr
         sys.exit(1) levantado

test_provider_openai_returns_correct_config
  Dado: PROVIDER=openai, OPENAI_API_KEY=sk-test
  Quando: get_config() é chamada
  Então: retorna objeto com provider="openai", api_key="sk-test"

test_provider_gemini_returns_correct_config
  Dado: PROVIDER=gemini, GOOGLE_API_KEY=AIza-test
  Quando: get_config() é chamada
  Então: retorna objeto com provider="gemini", api_key="AIza-test"

test_missing_api_key_for_selected_provider_exits_with_code_1
  Dado: PROVIDER=openai, sem OPENAI_API_KEY
  Quando: get_config() é chamada
  Então: mensagem "Variável de ambiente OPENAI_API_KEY não encontrada..." impressa em stderr
         sys.exit(1) levantado

test_pdf_path_defaults_to_document_pdf
  Dado: PROVIDER e API_KEY válidos, sem PDF_PATH
  Quando: get_config() é chamada
  Então: retorna objeto com pdf_path="document.pdf"

test_connection_string_has_default
  Dado: PROVIDER e API_KEY válidos, sem CONNECTION_STRING
  Quando: get_config() é chamada
  Então: retorna objeto com connection_string="postgresql+psycopg://postgres:postgres@localhost:5432/rag"
```

### Testes de integração (dos critérios Cross-Feature do PRD Seção 9)

```
test_config_provider_openai_instantiates_openai_classes
  Dado: PROVIDER=openai, OPENAI_API_KEY válida
  Quando: ingest.py ou search.py importam get_config()
  Então: OpenAIEmbeddings e ChatOpenAI são instanciados (não Google)

test_config_provider_gemini_instantiates_gemini_classes
  Dado: PROVIDER=gemini, GOOGLE_API_KEY válida
  Quando: ingest.py ou search.py importam get_config()
  Então: GoogleGenerativeAIEmbeddings e ChatGoogleGenerativeAI são instanciados (não OpenAI)
```

### Verificação manual de infraestrutura
```
test_docker_compose_postgres_healthy
  Execução: docker compose up -d
  Verificação: docker inspect postgres_rag | grep '"Status": "healthy"'
  Timeout: 60 segundos

test_pgvector_extension_active
  Execução: psql -U postgres -d rag -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
  Verificação: retorna exatamente 1 linha com "vector"
```
