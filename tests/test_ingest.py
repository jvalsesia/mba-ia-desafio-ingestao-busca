import sys
import pytest
from unittest.mock import patch, MagicMock

import sqlalchemy.exc
import openai
import google.api_core.exceptions

sys.path.insert(0, "src")
from ingest import ingest_pdf


OPENAI_ENV = {"OPENAI_API_KEY": "sk-test"}

MOCK_CHUNKS = [MagicMock(page_content="chunk") for _ in range(42)]


def _mock_loader_docs():
    doc = MagicMock()
    doc.page_content = "some text"
    return [doc]


def _apply_base_mocks(monkeypatch, chunks=None, pgvector_side_effect=None):
    if chunks is None:
        chunks = MOCK_CHUNKS

    monkeypatch.setattr("ingest.PyPDFLoader", lambda path: MagicMock(load=lambda: _mock_loader_docs()))
    splitter_mock = MagicMock()
    splitter_mock.split_documents.return_value = chunks
    monkeypatch.setattr(
        "ingest.RecursiveCharacterTextSplitter",
        lambda chunk_size, chunk_overlap: splitter_mock,
    )
    monkeypatch.setattr("ingest.OpenAIEmbeddings", lambda model: MagicMock())

    if pgvector_side_effect:
        pgvector_mock = MagicMock(side_effect=pgvector_side_effect)
    else:
        pgvector_mock = MagicMock()

    monkeypatch.setattr("ingest.PGVector.from_documents", pgvector_mock)
    return pgvector_mock


class TestPdfErrors:
    def test_pdf_not_found_exits_with_code_1(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "ingest.PyPDFLoader",
            lambda path: MagicMock(load=MagicMock(side_effect=FileNotFoundError)),
        )

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            with pytest.raises(SystemExit) as exc:
                ingest_pdf()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Arquivo PDF não encontrado" in captured.err

    def test_empty_pdf_exits_with_code_1(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "ingest.PyPDFLoader",
            lambda path: MagicMock(load=lambda: _mock_loader_docs()),
        )
        splitter_mock = MagicMock()
        splitter_mock.split_documents.return_value = []
        monkeypatch.setattr(
            "ingest.RecursiveCharacterTextSplitter",
            lambda chunk_size, chunk_overlap: splitter_mock,
        )

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            with pytest.raises(SystemExit) as exc:
                ingest_pdf()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "O PDF não contém texto legível" in captured.err


class TestDatabaseError:
    def test_db_connection_refused_exits_with_code_1(self, monkeypatch, capsys):
        _apply_base_mocks(
            monkeypatch,
            pgvector_side_effect=sqlalchemy.exc.OperationalError("conn refused", None, None),
        )

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            with pytest.raises(SystemExit) as exc:
                ingest_pdf()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Falha ao conectar ao banco de dados" in captured.err


class TestApiError:
    def test_invalid_api_key_exits_with_code_1(self, monkeypatch, capsys):
        auth_error = openai.AuthenticationError(
            message="Invalid API key",
            response=MagicMock(headers={}, status_code=401),
            body={"error": {"message": "Invalid API key"}},
        )
        _apply_base_mocks(monkeypatch, pgvector_side_effect=auth_error)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            with pytest.raises(SystemExit) as exc:
                ingest_pdf()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Falha de autenticação com" in captured.err

    def test_google_api_error_exits_with_code_1(self, monkeypatch, capsys):
        google_error = google.api_core.exceptions.GoogleAPIError("Quota exceeded")
        _apply_base_mocks(monkeypatch, pgvector_side_effect=google_error)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            with pytest.raises(SystemExit) as exc:
                ingest_pdf()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Falha de autenticação com" in captured.err


class TestSuccessfulIngestion:
    def test_completion_message_contains_chunk_count(self, monkeypatch, capsys):
        _apply_base_mocks(monkeypatch)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            ingest_pdf()

        captured = capsys.readouterr()
        assert "Ingestão concluída: 42 chunks armazenados na coleção 'pdf_documents'." in captured.out

    def test_pre_delete_collection_true_is_passed(self, monkeypatch):
        pgvector_mock = _apply_base_mocks(monkeypatch)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            ingest_pdf()

        call_kwargs = pgvector_mock.call_args.kwargs
        assert call_kwargs.get("pre_delete_collection") is True
