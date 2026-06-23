import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, "src")
from chat import main


class TestStartup:
    def test_startup_message_is_printed(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=KeyboardInterrupt))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Chat iniciado. Digite sua pergunta ou Ctrl+C para sair." in captured.out


class TestEmptyInput:
    def test_empty_input_is_no_op(self, monkeypatch, capsys):
        search_mock = MagicMock()
        monkeypatch.setattr("chat.search_prompt", search_mock)
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=["", KeyboardInterrupt()]))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA:" not in captured.out
        assert search_mock.call_count == 0

    def test_whitespace_only_input_is_no_op(self, monkeypatch, capsys):
        search_mock = MagicMock()
        monkeypatch.setattr("chat.search_prompt", search_mock)
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=["   ", KeyboardInterrupt()]))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA:" not in captured.out


class TestResponse:
    def test_question_produces_resposta_prefix(self, monkeypatch, capsys):
        monkeypatch.setattr("chat.search_prompt", MagicMock(return_value="R$ 10 milhões"))
        monkeypatch.setattr(
            "builtins.input", MagicMock(side_effect=["Qual a receita?", KeyboardInterrupt()])
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA: R$ 10 milhões" in captured.out

    def test_response_followed_by_blank_line(self, monkeypatch, capsys):
        monkeypatch.setattr("chat.search_prompt", MagicMock(return_value="qualquer"))
        monkeypatch.setattr(
            "builtins.input", MagicMock(side_effect=["pergunta", KeyboardInterrupt()])
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA: qualquer\n\n" in captured.out

    def test_response_is_verbatim(self, monkeypatch, capsys):
        texto = "Texto exato com acentuação e número 123"
        monkeypatch.setattr("chat.search_prompt", MagicMock(return_value=texto))
        monkeypatch.setattr(
            "builtins.input", MagicMock(side_effect=["pergunta", KeyboardInterrupt()])
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert f"RESPOSTA: {texto}" in captured.out

    def test_multiple_questions_produce_multiple_responses(self, monkeypatch, capsys):
        search_mock = MagicMock(side_effect=["r1", "r2"])
        monkeypatch.setattr("chat.search_prompt", search_mock)
        monkeypatch.setattr(
            "builtins.input", MagicMock(side_effect=["q1", "q2", KeyboardInterrupt()])
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA: r1" in captured.out
        assert "RESPOSTA: r2" in captured.out
        assert search_mock.call_count == 2


class TestTermination:
    def test_keyboard_interrupt_exits_with_code_0(self, monkeypatch):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=KeyboardInterrupt))

        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == 0

    def test_eof_exits_with_code_0(self, monkeypatch):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=EOFError))

        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == 0

    def test_exit_message_printed_on_ctrl_c(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=KeyboardInterrupt))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Encerrando o chat. Até logo!" in captured.out

    def test_exit_message_printed_on_eof(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=EOFError))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Encerrando o chat. Até logo!" in captured.out
