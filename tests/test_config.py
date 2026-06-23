import sys
import pytest
from unittest.mock import patch


sys.path.insert(0, "src")
from config import get_config


class TestNoApiKey:
    def test_no_api_keys_exits_with_code_1(self, capsys):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.err or "GOOGLE_API_KEY" in captured.err


class TestProviderOpenAI:
    def test_openai_key_selects_openai_provider(self):
        env = {"OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.provider == "openai"
        assert cfg.api_key == "sk-test"

    def test_openai_default_embedding_model(self):
        env = {"OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.embedding_model == "text-embedding-3-small"

    def test_openai_custom_embedding_model(self):
        env = {"OPENAI_API_KEY": "sk-test", "OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.embedding_model == "text-embedding-ada-002"

    def test_openai_takes_priority_when_both_keys_set(self):
        env = {"OPENAI_API_KEY": "sk-test", "GOOGLE_API_KEY": "AIza-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.provider == "openai"


class TestProviderGemini:
    def test_google_key_selects_gemini_provider(self):
        env = {"GOOGLE_API_KEY": "AIza-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.provider == "gemini"
        assert cfg.api_key == "AIza-test"

    def test_gemini_default_embedding_model(self):
        env = {"GOOGLE_API_KEY": "AIza-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.embedding_model == "models/embedding-001"

    def test_gemini_custom_embedding_model(self):
        env = {"GOOGLE_API_KEY": "AIza-test", "GOOGLE_EMBEDDING_MODEL": "models/embedding-002"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.embedding_model == "models/embedding-002"


class TestDefaults:
    def test_pdf_path_defaults_to_document_pdf(self):
        env = {"OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.pdf_path == "document.pdf"

    def test_database_url_has_default(self):
        env = {"OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.connection_string == "postgresql+psycopg://postgres:postgres@localhost:5432/rag"

    def test_collection_name_defaults_to_pdf_documents(self):
        env = {"OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.collection_name == "pdf_documents"

    def test_custom_pdf_path_is_respected(self):
        env = {"OPENAI_API_KEY": "sk-test", "PDF_PATH": "/data/report.pdf"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.pdf_path == "/data/report.pdf"

    def test_custom_database_url_is_respected(self):
        env = {"OPENAI_API_KEY": "sk-test", "DATABASE_URL": "postgresql+psycopg://user:pass@host:5433/mydb"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.connection_string == "postgresql+psycopg://user:pass@host:5433/mydb"

    def test_custom_collection_name_is_respected(self):
        env = {"OPENAI_API_KEY": "sk-test", "PG_VECTOR_COLLECTION_NAME": "my_collection"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.collection_name == "my_collection"
