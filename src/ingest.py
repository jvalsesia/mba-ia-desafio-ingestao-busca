import sys

import openai
import google.api_core.exceptions
import sqlalchemy.exc
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from config import get_config


def ingest_pdf():
    cfg = get_config()

    try:
        docs = PyPDFLoader(cfg.pdf_path).load()
    except FileNotFoundError:
        print(
            f"Arquivo PDF não encontrado: {cfg.pdf_path}. Verifique a variável PDF_PATH no .env.",
            file=sys.stderr,
        )
        sys.exit(1)

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150
    ).split_documents(docs)

    if len(chunks) == 0:
        print(
            "O PDF não contém texto legível. Verifique se o arquivo possui camada de texto.",
            file=sys.stderr,
        )
        sys.exit(1)

    if cfg.provider == "openai":
        embedding = OpenAIEmbeddings(model=cfg.embedding_model)
    else:
        embedding = GoogleGenerativeAIEmbeddings(model=cfg.embedding_model)

    provider_name = "OpenAI" if cfg.provider == "openai" else "Gemini"

    try:
        PGVector.from_documents(
            documents=chunks,
            embedding=embedding,
            connection=cfg.connection_string,
            collection_name=cfg.collection_name,
            pre_delete_collection=True,
        )
    except sqlalchemy.exc.OperationalError:
        print(
            "Falha ao conectar ao banco de dados. Verifique se o Docker está rodando: docker compose up -d",
            file=sys.stderr,
        )
        sys.exit(1)
    except openai.AuthenticationError as e:
        print(f"Falha de autenticação com {provider_name}: {str(e)}.", file=sys.stderr)
        sys.exit(1)
    except google.api_core.exceptions.GoogleAPIError as e:
        print(f"Falha de autenticação com {provider_name}: {str(e)}.", file=sys.stderr)
        sys.exit(1)

    print(
        f"Ingestão concluída: {len(chunks)} chunks armazenados na coleção 'pdf_documents'."
    )


if __name__ == "__main__":
    ingest_pdf()
