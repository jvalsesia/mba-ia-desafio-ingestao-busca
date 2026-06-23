import sys
import pytest
from unittest.mock import patch, MagicMock

import openai
import google.api_core.exceptions

sys.path.insert(0, "src")
from search import search_prompt


OPENAI_ENV = {"OPENAI_API_KEY": "sk-test"}
GEMINI_ENV = {"GOOGLE_API_KEY": "AIza-test"}

MOCK_DOCS = [(MagicMock(page_content=f"chunk {i}"), 0.9) for i in range(10)]


def _apply_base_mocks(monkeypatch, search_results=None, llm_side_effect=None, llm_content="Resposta mockada"):
    if search_results is None:
        search_results = MOCK_DOCS

    embedding_mock = MagicMock()
    monkeypatch.setattr("search.OpenAIEmbeddings", lambda model: embedding_mock)

    vectorstore_mock = MagicMock()
    vectorstore_mock.similarity_search_with_score.return_value = search_results
    monkeypatch.setattr("search.PGVector", lambda **kwargs: vectorstore_mock)

    llm_mock = MagicMock()
    if llm_side_effect:
        llm_mock.invoke.side_effect = llm_side_effect
    else:
        llm_mock.invoke.return_value = MagicMock(content=llm_content)
    monkeypatch.setattr("search.ChatOpenAI", lambda **kwargs: llm_mock)

    return vectorstore_mock, llm_mock


class TestEmptyCollection:
    def test_empty_results_returns_no_docs_message(self, monkeypatch):
        _apply_base_mocks(monkeypatch, search_results=[])

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            result = search_prompt("qualquer pergunta")

        assert result == "Nenhum documento encontrado no banco. Execute python src/ingest.py primeiro."

    def test_vectorstore_exception_returns_no_docs_message(self, monkeypatch):
        embedding_mock = MagicMock()
        monkeypatch.setattr("search.OpenAIEmbeddings", lambda model: embedding_mock)

        vectorstore_mock = MagicMock()
        vectorstore_mock.similarity_search_with_score.side_effect = Exception("relation does not exist")
        monkeypatch.setattr("search.PGVector", lambda **kwargs: vectorstore_mock)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            result = search_prompt("qualquer pergunta")

        assert result == "Nenhum documento encontrado no banco. Execute python src/ingest.py primeiro."


class TestLlmErrors:
    def test_llm_timeout_returns_timeout_message(self, monkeypatch):
        timeout_error = openai.APITimeoutError(request=MagicMock())
        _apply_base_mocks(monkeypatch, llm_side_effect=timeout_error)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            result = search_prompt("pergunta")

        assert result == "Tempo limite excedido ao chamar a LLM. Tente novamente."

    def test_llm_api_error_returns_error_message(self, monkeypatch):
        api_error = openai.APIError(
            message="rate limit exceeded",
            request=MagicMock(),
            body=None,
        )
        _apply_base_mocks(monkeypatch, llm_side_effect=api_error)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            result = search_prompt("pergunta")

        assert result.startswith("Erro ao obter resposta da LLM:")


class TestSuccessfulSearch:
    def test_returns_llm_response_content(self, monkeypatch):
        _apply_base_mocks(monkeypatch, llm_content="Resposta do LLM")

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            result = search_prompt("pergunta dentro do contexto")

        assert result == "Resposta do LLM"

    def test_context_joined_with_double_newline(self, monkeypatch):
        docs = [
            (MagicMock(page_content="a"), 0.9),
            (MagicMock(page_content="b"), 0.8),
            (MagicMock(page_content="c"), 0.7),
        ]

        embedding_mock = MagicMock()
        monkeypatch.setattr("search.OpenAIEmbeddings", lambda model: embedding_mock)

        vectorstore_mock = MagicMock()
        vectorstore_mock.similarity_search_with_score.return_value = docs
        monkeypatch.setattr("search.PGVector", lambda **kwargs: vectorstore_mock)

        captured_prompts = []
        llm_mock = MagicMock()
        llm_mock.invoke.side_effect = lambda p: (captured_prompts.append(p), MagicMock(content="ok"))[1]
        monkeypatch.setattr("search.ChatOpenAI", lambda **kwargs: llm_mock)

        with patch.dict("os.environ", OPENAI_ENV, clear=True):
            search_prompt("test")

        assert len(captured_prompts) == 1
        assert "a\n\nb\n\nc" in captured_prompts[0]

    def test_gemini_provider_uses_gemini_classes(self, monkeypatch):
        gemini_embedding_mock = MagicMock()
        monkeypatch.setattr("search.GoogleGenerativeAIEmbeddings", lambda model: gemini_embedding_mock)

        vectorstore_mock = MagicMock()
        vectorstore_mock.similarity_search_with_score.return_value = MOCK_DOCS
        monkeypatch.setattr("search.PGVector", lambda **kwargs: vectorstore_mock)

        gemini_llm_mock = MagicMock()
        gemini_llm_mock.invoke.return_value = MagicMock(content="Gemini response")
        monkeypatch.setattr("search.ChatGoogleGenerativeAI", lambda **kwargs: gemini_llm_mock)

        openai_llm_mock = MagicMock()
        monkeypatch.setattr("search.ChatOpenAI", lambda **kwargs: openai_llm_mock)

        with patch.dict("os.environ", GEMINI_ENV, clear=True):
            result = search_prompt("pergunta")

        assert result == "Gemini response"
        openai_llm_mock.invoke.assert_not_called()
