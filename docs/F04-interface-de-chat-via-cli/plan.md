# Implementation Plan: F04 — Interface de Chat via CLI

**Prerequisites:**
- F03 implementado: `src/search.py` com `search_prompt(question)` funcional e retornando string em todos os caminhos
- Arquivo `src/chat.py` existente (esqueleto a ser reescrito)
- pytest disponível no ambiente de teste

---

### Stage 1: Implementação do Loop de Chat

**1. Reescrever `src/chat.py`** - Substituir o esqueleto existente pela implementação completa do `main()`: remover as importações e chamadas obsoletas (`get_config`, `chain = search_prompt()`), adicionar `import sys` e `from search import search_prompt`, e implementar o loop `while True` conforme descrito no spec — mensagem de inicialização, leitura de input, tratamento de entrada vazia (no-op via `continue`), chamada de `search_prompt(question)`, impressão de "RESPOSTA:" com linha em branco, e captura de `KeyboardInterrupt`/`EOFError` para encerramento com mensagem e `sys.exit(0)`.

---

### Stage 2: Testes Unitários

**2. Criar `tests/test_chat.py` — testes de comportamento do loop** - Implementar os testes unitários de startup, no-op e resposta seguindo o padrão class-based do projeto: usar `monkeypatch.setattr("builtins.input", side_effect=[...])` para simular sequências de entradas, `monkeypatch.setattr("chat.search_prompt", ...)` para isolar F03, e `capsys.readouterr()` para verificar mensagens no stdout. Cobrir: mensagem de inicialização, entrada vazia (não chama `search_prompt`), entrada com apenas espaços (no-op), formatação "RESPOSTA:", linha em branco após resposta, transmissão verbatim do texto retornado, e múltiplas perguntas em sequência.

**3. Criar `tests/test_chat.py` — testes de terminação** - Adicionar a classe `TestTermination` ao mesmo arquivo de testes, usando `pytest.raises(SystemExit)` para verificar que `sys.exit(0)` é chamado tanto em `KeyboardInterrupt` quanto em `EOFError`, e `capsys.readouterr()` para confirmar que a mensagem "Encerrando o chat. Até logo!" é impressa antes da saída em ambos os casos.
