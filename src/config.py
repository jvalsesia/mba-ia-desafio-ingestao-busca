import os
import sys
from types import SimpleNamespace
from dotenv import load_dotenv


def get_config() -> SimpleNamespace:
    load_dotenv()

    provider = os.getenv("PROVIDER")
    if not provider:
        print(
            "Variável de ambiente PROVIDER não encontrada. "
            "Copie .env.example para .env e preencha os valores obrigatórios.",
            file=sys.stderr,
        )
        sys.exit(1)

    if provider not in ("openai", "gemini"):
        print(
            f"Valor inválido para PROVIDER: '{provider}'. Use 'openai' ou 'gemini'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(
                "Variável de ambiente OPENAI_API_KEY não encontrada. "
                "Copie .env.example para .env e preencha os valores obrigatórios.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(
                "Variável de ambiente GOOGLE_API_KEY não encontrada. "
                "Copie .env.example para .env e preencha os valores obrigatórios.",
                file=sys.stderr,
            )
            sys.exit(1)

    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    connection_string = os.getenv(
        "CONNECTION_STRING",
        "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
    )

    return SimpleNamespace(
        provider=provider,
        api_key=api_key,
        pdf_path=pdf_path,
        connection_string=connection_string,
    )
