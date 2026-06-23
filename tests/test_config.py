import sys
import pytest
from unittest.mock import patch


sys.path.insert(0, "src")
from config import get_config


def _env(**kwargs):
    """Returns a minimal valid env dict merged with kwargs."""
    base = {
        "PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test",
        "PDF_PATH": "document.pdf",
        "CONNECTION_STRING": "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
    }
    base.update(kwargs)
    return {k: v for k, v in base.items() if v is not None}


class TestMissingProvider:
    def test_missing_provider_exits_with_code_1(self, capsys):
        env = _env(PROVIDER=None, OPENAI_API_KEY=None)
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "PROVIDER" in captured.err
        assert "não encontrada" in captured.err


class TestInvalidProvider:
    def test_invalid_provider_exits_with_code_1(self, capsys):
        env = _env(PROVIDER="aws")
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "aws" in captured.err
        assert "openai" in captured.err
        assert "gemini" in captured.err

    def test_provider_capitalised_is_invalid(self, capsys):
        env = _env(PROVIDER="OpenAI")
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1


class TestProviderOpenAI:
    def test_valid_openai_config_returns_namespace(self):
        env = _env(PROVIDER="openai", OPENAI_API_KEY="sk-test")
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.provider == "openai"
        assert cfg.api_key == "sk-test"

    def test_missing_openai_api_key_exits_with_code_1(self, capsys):
        env = _env(PROVIDER="openai", OPENAI_API_KEY=None)
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.err


class TestProviderGemini:
    def test_valid_gemini_config_returns_namespace(self):
        env = {"PROVIDER": "gemini", "GOOGLE_API_KEY": "AIza-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.provider == "gemini"
        assert cfg.api_key == "AIza-test"

    def test_missing_google_api_key_exits_with_code_1(self, capsys):
        env = {"PROVIDER": "gemini"}
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(SystemExit) as exc:
                get_config()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "GOOGLE_API_KEY" in captured.err


class TestDefaults:
    def test_pdf_path_defaults_to_document_pdf(self):
        env = {"PROVIDER": "openai", "OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.pdf_path == "document.pdf"

    def test_connection_string_has_default(self):
        env = {"PROVIDER": "openai", "OPENAI_API_KEY": "sk-test"}
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.connection_string == "postgresql+psycopg://postgres:postgres@localhost:5432/rag"

    def test_custom_pdf_path_is_respected(self):
        env = _env(PDF_PATH="/data/my_report.pdf")
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.pdf_path == "/data/my_report.pdf"

    def test_custom_connection_string_is_respected(self):
        env = _env(CONNECTION_STRING="postgresql+psycopg://user:pass@host:5433/mydb")
        with patch.dict("os.environ", env, clear=True):
            cfg = get_config()
        assert cfg.connection_string == "postgresql+psycopg://user:pass@host:5433/mydb"
