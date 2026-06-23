# Implementation Plan: F03 — Busca Semântica e Resposta do LLM

**Prerequisites:**
- F01 implementado: `src/config.py` com `get_config()` funcional
- F02 implementado: `python src/ingest.py` executado com sucesso (coleção `pdf_documents` populada)
- Dependências instaladas: `langchain-openai`, `langchain-google-genai`, `langchain-postgres`, `openai`, `google-api-core` (todas presentes em `requirements.txt`)
- Variáveis de ambiente configuradas no `.env` (`OPENAI_API_KEY` ou `GOOGLE_API_KEY`, `DATABASE_URL` ou default)

---

### Stage 1: Integração com pgVector (leitura)

**1. Adicionar importações e instanciação do embedding** - Completar `src/search.py` adicionando as importações necessárias (`ChatOpenAI`, `ChatGoogleGenerativeAI`, `OpenAIEmbeddings`, `GoogleGenerativeAIEmbeddings`, `PGVector`, `openai`, `google.api_core.exceptions`) e instanciando o embedding ciente do provedor seguindo o mesmo padrão já estabelecido em `src/ingest.py`.

**2. Executar similarity search e montar contexto** - Instanciar o PGVector em modo leitura via construtor (não `from_documents`) usando `cfg.connection_string`, `cfg.collection_name` e o embedding criado no passo anterior. Executar `similarity_search_with_score(question, k=10)`, tratar coleção vazia ou exceção retornando a string de "Nenhum documento encontrado", e concatenar os `page_content` dos resultados com `"\n\n"` para montar a string de contexto.

---

### Stage 2: Integração com LLM e retorno da resposta

**3. Instanciar LLM e invocar com prompt** - Formatar o `PROMPT_TEMPLATE` já existente no arquivo com `contexto` e `pergunta`, instanciar o LLM correto para o provedor (ChatOpenAI com `model="gpt-5-nano"` e `timeout=30`, ou ChatGoogleGenerativeAI com `model="gemini-2.5-flash-lite"` e `request_timeout=30`) e invocar com a string de prompt formatada, retornando `response.content`.

**4. Tratar erros de API do LLM** - Envolver a chamada `llm.invoke()` com os blocos de exceção para timeout e erro genérico de API, respeitando a ordem de captura descrita no spec (timeout antes do handler genérico, pois é subclasse). Todos os erros retornam strings para o chamador, sem `sys.exit()`.
