import openai
import google.api_core.exceptions
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector

from config import get_config

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
    cfg = get_config()

    if cfg.provider == "openai":
        embedding = OpenAIEmbeddings(model=cfg.embedding_model)
    else:
        embedding = GoogleGenerativeAIEmbeddings(model=cfg.embedding_model)

    vectorstore = PGVector(
        connection=cfg.connection_string,
        collection_name=cfg.collection_name,
        embeddings=embedding,
    )

    try:
        results = vectorstore.similarity_search_with_score(question, k=10)
    except Exception:
        return "Nenhum documento encontrado no banco. Execute python src/ingest.py primeiro."

    if not results:
        return "Nenhum documento encontrado no banco. Execute python src/ingest.py primeiro."

    contexto = "\n\n".join(doc.page_content for doc, _ in results)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)

    if cfg.provider == "openai":
        llm = ChatOpenAI(model="gpt-5-nano", timeout=60)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", request_timeout=60)

    try:
        response = llm.invoke(prompt)
    except (openai.APITimeoutError, google.api_core.exceptions.DeadlineExceeded):
        return "Tempo limite excedido ao chamar a LLM. Tente novamente."
    except (openai.APIError, google.api_core.exceptions.GoogleAPIError) as e:
        return f"Erro ao obter resposta da LLM: {str(e)}."

    return response.content