# F02 — Plano de Implementação: Ingestão de PDF

## Pré-requisitos

- F01 implementado: `src/config.py` com `get_config()` funcionando e todos os testes passando
- Docker rodando e banco de dados healthy (`docker compose up -d`)
- `document.pdf` presente na raiz do projeto (para validação manual)
- `spec.md` desta feature lido

---

## Fase 1: Implementar Pipeline de Ingestão

**1. Completar `src/ingest.py`** — Implementar o corpo de `ingest_pdf()` integrando PyPDFLoader, RecursiveCharacterTextSplitter e PGVector.from_documents conforme a estrutura de função descrita na spec. Cobrir os quatro caminhos de erro (arquivo ausente, PDF sem texto, banco offline, API inválida) com as mensagens exatas definidas na tabela de Error Handling da spec, impressas em stderr antes de `sys.exit(1)`.

---

## Fase 2: Testar e Validar

**2. Criar `tests/test_ingest.py`** — Implementar os testes unitários seguindo o padrão class-based de `tests/test_config.py`, mockando PyPDFLoader, RecursiveCharacterTextSplitter e PGVector.from_documents para cobrir todos os caminhos de erro e o caminho feliz (mensagem de conclusão com contagem correta e verificação de `pre_delete_collection=True`).

**3. Validar manualmente** — Executar `python src/ingest.py` com o banco rodando e confirmar a mensagem de conclusão com contagem de chunks maior que zero. Re-executar imediatamente para confirmar idempotência: a mesma contagem deve ser reportada sem duplicatas no pgVector.
