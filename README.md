# Busca Semântica em PDF via CLI com LangChain

Ferramenta de linha de comando que ingere um documento PDF em um banco de dados vetorial PostgreSQL e responde perguntas em linguagem natural estritamente baseadas no conteúdo do documento. Implementa um pipeline RAG completo usando LangChain, pgVector e OpenAI ou Google Gemini.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.12+
- Chave de API da OpenAI **ou** do Google Gemini

## Configuração

### 1. Suba o banco de dados

```bash
docker compose up -d
```

O serviço `bootstrap_vector_ext` habilita automaticamente a extensão pgVector após o PostgreSQL ficar saudável (~60 segundos).

### 2. Configure o ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha a chave de API do provedor desejado:

| Variável | Descrição | Padrão |
|---|---|---|
| `OPENAI_API_KEY` | Chave da API OpenAI (define o provedor como OpenAI) | — |
| `GOOGLE_API_KEY` | Chave da API Google Gemini (define o provedor como Gemini) | — |
| `PDF_PATH` | Caminho para o arquivo PDF a ser ingerido | `document.pdf` |
| `DATABASE_URL` | String de conexão PostgreSQL | `postgresql+psycopg://postgres:postgres@localhost:5432/rag` |

O provedor é determinado automaticamente pela chave presente: `OPENAI_API_KEY` ativa OpenAI; `GOOGLE_API_KEY` ativa Gemini. Se ambas estiverem definidas, OpenAI tem precedência.

### 3. Instale as dependências Python

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

Todos os scripts são executados a partir da **raiz do projeto**.

### Passo 1 — Ingestão do PDF

Processa o PDF, divide em chunks e armazena os vetores no pgVector:

```bash
python src/ingest.py
```

Saída esperada:
```
Ingestão concluída: 142 chunks armazenados na coleção 'pdf_documents'.
```

Re-executar o script substitui os vetores existentes (sem duplicatas).

### Passo 2 — Chat interativo

Inicia o loop de perguntas e respostas baseado no conteúdo do PDF:

```bash
python src/chat.py
```

```
Chat iniciado. Digite sua pergunta ou Ctrl+C para sair.

PERGUNTA: Qual foi o faturamento do ano passado?
RESPOSTA: Segundo o documento, o faturamento foi de R$ 2,4 bilhões...

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

PERGUNTA: ^C
Encerrando o chat. Até logo!
```

Pressione **Ctrl+C** ou **Ctrl+D** para encerrar.

## Modelos utilizados

| Provedor | Embedding | LLM |
|---|---|---|
| OpenAI | `text-embedding-3-small` | `gpt-5-nano` |
| Gemini | `models/embedding-001` | `gemini-2.5-flash-lite` |

## Testes

```bash
pytest tests/
```

## Estrutura do projeto

```
.
├── docker-compose.yml      # PostgreSQL + pgVector
├── .env.example            # Template de configuração
├── document.pdf            # PDF de exemplo
├── requirements.txt        # Dependências Python
├── src/
│   ├── config.py           # Carrega e valida variáveis de ambiente
│   ├── ingest.py           # Pipeline de ingestão do PDF
│   ├── search.py           # Busca semântica e resposta do LLM
│   └── chat.py             # Loop interativo de CLI
└── tests/
    ├── test_config.py
    ├── test_ingest.py
    ├── test_search.py
    └── test_chat.py
```
