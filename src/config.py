import os
import sys
from types import SimpleNamespace
from dotenv import load_dotenv


def get_config() -> SimpleNamespace:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if openai_api_key:
        provider = "openai"
        api_key = openai_api_key
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    elif google_api_key:
        provider = "gemini"
        api_key = google_api_key
        embedding_model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
    else:
        print(
            "Nenhuma chave de API encontrada. "
            "Defina OPENAI_API_KEY ou GOOGLE_API_KEY no .env.",
            file=sys.stderr,
        )
        sys.exit(1)

    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    connection_string = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
    )
    collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_documents")

    return SimpleNamespace(
        provider=provider,
        api_key=api_key,
        embedding_model=embedding_model,
        pdf_path=pdf_path,
        connection_string=connection_string,
        collection_name=collection_name,
    )
