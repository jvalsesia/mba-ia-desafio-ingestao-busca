# Busca Semântica em PDF via CLI com LangChain

## 1. Resumo Executivo

Este produto é uma ferramenta Python de linha de comando que ingere um documento PDF em um banco de dados vetorial PostgreSQL e permite perguntas e respostas em linguagem natural estritamente baseadas no conteúdo do documento. Desenvolvido como parte de um desafio do MBA em Engenharia de Software com IA da FullCycle, demonstra um pipeline completo de Geração Aumentada por Recuperação (RAG) usando LangChain, pgVector e OpenAI ou Google Gemini como provedor de IA.

A ferramenta serve a profissionais técnicos que precisam extrair conhecimento estruturado de documentos PDF sem depender do conhecimento geral de treinamento de um LLM. O valor central é a imposição estrita de contexto: o sistema nunca fabrica respostas — se a informação não estiver explicitamente presente no PDF, retorna uma mensagem de recusa padrão, tornando-o confiável para documentos financeiros e empresariais.

Em alto nível, o sistema opera em duas fases sequenciais: uma fase de ingestão, onde o PDF é dividido em blocos de 1.000 caracteres, convertido em embeddings vetoriais e armazenado no pgVector; e uma fase de consulta, onde a pergunta do usuário é vetorizada, os 10 blocos semanticamente mais similares são recuperados e um prompt LLM restrito gera uma resposta limitada exclusivamente a esses blocos.

## 2. Problema e Oportunidade

**O Problema**

**Conhecimento não estruturado preso em PDFs**
- Relatórios empresariais e financeiros existem apenas como arquivos de texto, tornando impossível consultá-los com linguagem natural
- Varrer manualmente um documento para encontrar receitas específicas, datas ou dados de empresas pode levar horas
- Não existe forma programática de perguntar "Qual foi a receita da Empresa X?" e obter uma resposta precisa e com fonte

**Alucinação de LLMs em conteúdo de domínio específico**
- LLMs de uso geral respondem perguntas financeiras ou específicas de empresas usando seus dados de treinamento, não o documento real
- Valores de receita fabricados, nomes de empresas inventados ou datas erradas podem parecer plausíveis, mas são completamente incorretos
- Nenhum limite embutido impede um LLM de inventar com confiança informações que nunca estiveram no documento

**Complexidade na configuração de pipeline RAG**
- Conectar um banco de dados vetorial, API de embeddings e LLM em um pipeline coerente requer expertise em múltiplas bibliotecas
- Desenvolvedores devem configurar corretamente estratégias de chunking, modelos de embedding, templates de prompt e clientes de banco de dados — qualquer configuração errada degrada silenciosamente a qualidade das respostas
- Nenhum projeto inicial existente cobre todos esses componentes com as restrições específicas (tamanho de chunk, overlap, k=10, prompt restrito) em um único pacote implantável

**Risco de lock-in de provedor**
- Depender de um único provedor de IA cria risco de custo e disponibilidade tanto para projetos de estudantes quanto de produção
- Migrar do OpenAI para o Gemini tipicamente requer mudanças no código em múltiplos arquivos

**A Oportunidade**

O produto resolve cada problema diretamente:
- O pipeline de ingestão via pgVector transforma PDFs não estruturados em uma base de conhecimento consultável, retornando respostas em menos de 10 segundos
- O template de prompt cuidadosamente projetado impõe limites de conteúdo para que o LLM só possa responder a partir dos blocos recuperados — a alucinação é estruturalmente prevenida, não apenas desencorajada
- Docker Compose + scripts pré-configurados eliminam a complexidade de configuração do RAG: três comandos entregam um sistema funcionando
- Uma única variável de ambiente `PROVIDER` alterna todo o pipeline entre OpenAI e Gemini sem nenhuma alteração no código

## 3. Público-Alvo

### Usuários Primários

**Profissional Técnico / Estudante de MBA**
- Desenvolvedor Python completando um desafio de curso de engenharia de IA focado em LangChain e bancos de dados vetoriais
- Familiarizado com Docker e ferramentas de linha de comando; tem acesso a pelo menos uma chave de API de provedor de IA (OpenAI ou Google)
- Objetivo: demonstrar um pipeline RAG completo de ponta a ponta que recupera corretamente respostas baseadas no documento e rejeita perguntas fora de contexto

## 4. Objetivos

**Habilitar busca semântica** sobre conteúdo de PDF para que perguntas em linguagem natural retornem respostas precisas e baseadas no documento
- Métrica: ≥ 90% das perguntas sobre conteúdo presente no documento retornam uma resposta relevante e não vazia em menos de 10 segundos por consulta

**Impor limites de conteúdo** para que perguntas fora do contexto do PDF nunca produzam respostas alucinadas
- Métrica: 100% das perguntas fora de contexto retornam a mensagem de recusa padrão: "Não tenho informações necessárias para responder sua pergunta."

**Suportar dois provedores de LLM** para que desenvolvedores possam alternar entre OpenAI e Gemini sem alterações no código
- Métrica: Ambos os provedores completam um ciclo completo de ingestão + consulta sem erros quando corretamente configurados no `.env`

**Entregar uma CLI completa e executável** para que o pipeline de três scripts esteja pronto para execução com instruções claras de configuração
- Métrica: Todos os três scripts (`ingest.py`, `search.py`, `chat.py`) executam sem erros em sequência a partir de um ambiente limpo seguindo o README

## 5. Histórias de Usuário

### F01. Configuração de Ambiente e Infraestrutura
- Como desenvolvedor, quero executar `docker compose up -d` para iniciar o banco de dados para que o pgVector esteja disponível antes que qualquer script seja executado
- Como desenvolvedor, quero configurar meu provedor de LLM e chave de API em um arquivo `.env` para que os scripts saibam qual modelo de embedding e LLM usar
- Como sistema, quero habilitar automaticamente a extensão pgVector após o banco de dados iniciar para que operações vetoriais estejam disponíveis sem etapas manuais de SQL
- Como desenvolvedor, quero mensagens de erro claras quando variáveis de ambiente obrigatórias estiverem ausentes para que eu possa corrigir problemas de configuração rapidamente

### F02. Ingestão de PDF
- Como desenvolvedor, quero executar `python src/ingest.py` uma vez para carregar o PDF para que o conteúdo do documento seja indexado e pronto para consulta
- Como sistema, quero dividir o PDF em blocos de 1.000 caracteres com overlap de 150 caracteres para que o contexto semântico seja preservado entre os limites dos blocos
- Como sistema, quero que cada bloco seja convertido em um embedding vetorial usando o provedor configurado para que a busca por similaridade possa recuperar trechos semanticamente relevantes
- Como desenvolvedor, quero que re-executar o `ingest.py` substitua os vetores existentes para que eu possa re-indexar após alterar o PDF sem duplicar dados

### F03. Busca Semântica e Resposta do LLM
- Como sistema, quero vetorizar a pergunta do usuário e recuperar os 10 blocos mais relevantes do pgVector para que o LLM tenha contexto suficiente para responder
- Como sistema, quero aplicar o template de prompt restrito com CONTEXTO, REGRAS e EXEMPLOS para que o LLM seja restrito apenas ao conteúdo recuperado
- Como sistema, quero retornar a mensagem de recusa padrão quando nenhum contexto relevante for encontrado para que os usuários sempre recebam uma resposta honesta e fundamentada
- Como desenvolvedor, quero que o mesmo modelo de embedding usado durante a ingestão seja usado durante a busca para que a consistência do espaço vetorial seja garantida

### F04. Interface de Chat via CLI
- Como usuário, quero digitar perguntas no terminal sob um prompt "PERGUNTA:" para que eu possa consultar o documento naturalmente
- Como usuário, quero ver a resposta prefixada com "RESPOSTA:" para que a interação seja claramente estruturada
- Como usuário, quero fazer múltiplas perguntas em sequência para que eu possa explorar o documento iterativamente sem reiniciar o script
- Como usuário, quero sair do chat com Ctrl+C para que eu possa encerrar a sessão de forma limpa a qualquer momento

## 6. Funcionalidades

### F01. Configuração de Ambiente e Infraestrutura

**Fornece:**
- String de conexão ao PostgreSQL, seleção de provedor (openai|gemini), chaves de API, caminho do arquivo PDF (usados por F02, F03)

**Capacidades:**
- `docker-compose.yml` executa a imagem `pgvector/pgvector:pg17` com nome de banco de dados `rag`, usuário `postgres`, senha `postgres`, porta 5432
- O serviço `bootstrap_vector_ext` executa `CREATE EXTENSION IF NOT EXISTS vector` via psql após a verificação de saúde do postgres passar (5 tentativas × intervalo de 10s, timeout de 5s)
- O arquivo `.env` deve definir: `PROVIDER` (valor: `openai` ou `gemini`), `OPENAI_API_KEY` ou `GOOGLE_API_KEY` (dependendo do provedor), `PDF_PATH` (padrão: `document.pdf`), `CONNECTION_STRING` (padrão: `postgresql+psycopg://postgres:postgres@localhost:5432/rag`)
- O valor de `PROVIDER` controla quais classes de embedding e LLM são instanciadas em todos os scripts — nenhuma alteração de código é necessária para trocar de provedor

**Experiência:**
1. Desenvolvedor executa `docker compose up -d`
2. Docker baixa `pgvector/pgvector:pg17` se não estiver em cache
3. Container do Postgres inicia; verificação de saúde executa `pg_isready -U postgres -d rag` a cada 10 segundos
4. Após a verificação de saúde passar, `bootstrap_vector_ext` executa e cria a extensão vetorial
5. Banco de dados fica pronto em ~60 segundos
6. Desenvolvedor copia `.env.example` para `.env`, define `PROVIDER`, preenche a chave de API correspondente e opcionalmente substitui `PDF_PATH` ou `CONNECTION_STRING`

**Tratamento de Erros:**
- Docker daemon não está rodando: todos os comandos `docker compose` falham com "Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?"
- Postgres não saudável após 5 tentativas: container reporta `unhealthy`; desenvolvedor deve inspecionar com `docker logs postgres_rag`
- Variável `.env` obrigatória ausente: script imprime "Variável de ambiente [NOME] não encontrada. Copie .env.example para .env e preencha os valores obrigatórios." e sai com código 1
- Valor inválido de `PROVIDER`: script imprime "Valor inválido para PROVIDER: '[value]'. Use 'openai' ou 'gemini'." e sai com código 1

### F02. Ingestão de PDF

**Consome:**
- F01: String de conexão ao PostgreSQL, seleção de provedor, chaves de API, caminho do arquivo PDF

**Fornece:**
- Blocos do documento vetorizados armazenados na coleção `pdf_documents` do pgVector com conteúdo da página e metadados de origem (usados por F03)

**Capacidades:**
- Carrega o PDF usando `langchain_community.document_loaders.PyPDFLoader` a partir do caminho em `PDF_PATH`
- Divide usando `langchain_text_splitters.RecursiveCharacterTextSplitter` com `chunk_size=1000`, `chunk_overlap=150`
- Provedor OpenAI: `langchain_openai.OpenAIEmbeddings(model="text-embedding-3-small")`
- Provedor Gemini: `langchain_google_genai.GoogleGenerativeAIEmbeddings(model="models/embedding-001")`
- Armazena todos os vetores via `langchain_postgres.PGVector` com `collection_name="pdf_documents"` e `pre_delete_collection=True` (re-ingestão idempotente)
- Nenhum contagem mínima ou máxima de blocos é imposta; a contagem depende do tamanho do documento

**Experiência:**
1. Desenvolvedor executa `python src/ingest.py`
2. Script carrega `.env` e valida variáveis
3. Script abre o PDF de `PDF_PATH` e lê todas as páginas
4. `RecursiveCharacterTextSplitter` gera os blocos
5. A API de embeddings é chamada para converter blocos em vetores (em lotes automaticamente pela biblioteca)
6. `PGVector` exclui a coleção existente e grava todos os novos vetores atomicamente
7. Script imprime: `"Ingestão concluída: [N] chunks armazenados na coleção 'pdf_documents'."`

**Tratamento de Erros:**
- Arquivo PDF não encontrado: `"Arquivo PDF não encontrado: [path]. Verifique a variável PDF_PATH no .env."` sai com código 1
- Conexão com banco de dados recusada: `"Falha ao conectar ao banco de dados. Verifique se o Docker está rodando: docker compose up -d"` sai com código 1
- Chave de API inválida ou cota excedida: `"Falha de autenticação com [OpenAI|Gemini]: [error message]."` sai com código 1
- PDF não contém texto extraível (imagem digitalizada sem OCR): `"O PDF não contém texto legível. Verifique se o arquivo possui camada de texto."` sai com código 1

### F03. Busca Semântica e Resposta do LLM

**Consome:**
- F01: String de conexão ao PostgreSQL, seleção de provedor, chaves de API
- F02: Blocos vetorizados da coleção `pdf_documents` do pgVector

**Fornece:**
- Texto de resposta gerado pelo LLM (usado por F04)

**Capacidades:**
- Aceita uma string de pergunta como entrada via função `search_prompt(question)`
- Vetoriza a pergunta usando o mesmo modelo de embedding da ingestão (consciente do provedor)
- Executa `similarity_search_with_score(query, k=10)` contra a coleção `pdf_documents`
- Concatena o `page_content` de todos os 10 resultados separados por `"\n\n"` em uma única string de contexto
- Constrói o prompt usando o template exato: bloco CONTEXTO com os blocos concatenados, bloco REGRAS com 4 regras, bloco EXEMPLOS com 3 exemplos de recusa, bloco PERGUNTA DO USUÁRIO com a pergunta
- Provedor OpenAI: LLM é `gpt-5-nano` via `langchain_openai.ChatOpenAI`
- Provedor Gemini: LLM é `gemini-2.5-flash-lite` via `langchain_google_genai.ChatGoogleGenerativeAI`
- Retorna o conteúdo da resposta do LLM como uma string simples

**Experiência:**
1. `search_prompt(question)` é chamada com a string de pergunta do usuário
2. O embedding da pergunta é gerado usando o provedor configurado
3. `similarity_search_with_score(question, k=10)` retorna 10 blocos de documentos ordenados por similaridade de cosseno
4. Os 10 valores de `page_content` são unidos no bloco CONTEXTO
5. O prompt completo é montado e enviado ao LLM configurado
6. O LLM aplica as REGRAS: se a resposta estiver no contexto, retorna-a; caso contrário, retorna "Não tenho informações necessárias para responder sua pergunta."
7. A string de resposta é retornada ao chamador

**Tratamento de Erros:**
- Coleção `pdf_documents` não existe ou está vazia: `"Nenhum documento encontrado no banco. Execute python src/ingest.py primeiro."` retorna essa string como resposta
- Timeout da API do LLM (resposta excede 30 segundos): `"Tempo limite excedido ao chamar a LLM. Tente novamente."` retornado como resposta
- Erro da API do LLM (limite de taxa, erro de servidor): `"Erro ao obter resposta da LLM: [error message]."` retornado como resposta

### F04. Interface de Chat via CLI

**Consome:**
- F03: Texto de resposta gerado pelo LLM

**Capacidades:**
- Loop interativo de terminal: lê uma pergunta por iteração, imprime a resposta e então repete
- Entrada vazia (usuário pressiona Enter sem digitar) é tratada como no-op — o prompt "PERGUNTA:" é exibido novamente
- Encerra de forma limpa com Ctrl+C (SIGINT) ou EOF (Ctrl+D no Linux/macOS)
- Sem histórico de conversa — cada pergunta é processada independentemente com apenas o contexto do PDF
- Nenhum parsing de argumentos necessário; o script executa com `python src/chat.py` e lê toda a configuração do `.env`

**Experiência:**
1. Desenvolvedor executa `python src/chat.py`
2. Terminal imprime: `"Chat iniciado. Digite sua pergunta ou Ctrl+C para sair.\n"`
3. Terminal imprime: `"PERGUNTA: "` e aguarda entrada
4. Usuário digita uma pergunta e pressiona Enter
5. Script chama `search_prompt(question)` de `search.py`
6. Terminal imprime: `"RESPOSTA: [texto da resposta]"` seguido de uma linha em branco
7. Loop retorna ao passo 3
8. Com Ctrl+C ou EOF: terminal imprime `"\nEncerrando o chat. Até logo!"` e sai com código 0

## 7. Fora do Escopo

**Interface**
- Interface web ou gráfica
- Endpoint REST API para consumo externo
- Respostas em streaming token a token (SSE ou WebSocket)
- Configuração via argumentos CLI (toda configuração via `.env`)

**Gerenciamento de Documentos**
- Ingestão de múltiplos PDFs simultaneamente na mesma coleção ou em coleções separadas
- Ingestão incremental (acréscimo à coleção existente sem substituição)
- Suporte a tipos de documentos não-PDF (DOCX, TXT, HTML, imagens)
- Re-ingestão automática quando o PDF muda

**Funcionalidades Conversacionais**
- Memória de conversa ou histórico de chat entre múltiplos turnos
- Perguntas de acompanhamento que referenciam respostas anteriores
- Persistência de sessão entre execuções separadas do `chat.py`

**Busca Avançada**
- Re-ranqueamento de resultados além do score de similaridade vetorial top k=10
- Busca híbrida combinando busca por palavras-chave com busca semântica
- Filtragem de resultados por metadados (número de página, seção, data)
- Valor de k ajustável em tempo de execução

**Infraestrutura**
- Implantação em nuvem (AWS, GCP, Azure, Railway)
- Configuração de banco de dados para produção (pool de conexões, SSL, backups)
- Autenticação de usuários ou suporte a múltiplos usuários
- Observabilidade (logging, métricas, rastreamento)

## 8. Grafo de Dependências

| # | Funcionalidade | Prioridade | Dependências |
|---|----------------|------------|--------------|
| F01 | Configuração de Ambiente e Infraestrutura | 1 | Nenhuma |
| F02 | Ingestão de PDF | 1 | F01 |
| F03 | Busca Semântica e Resposta do LLM | 1 | F01, F02 |
| F04 | Interface de Chat via CLI | 1 | F03 |

### Funcionalidades Fundamentais
Essas funcionalidades configuram a infraestrutura compartilhada do projeto. Em um projeto do zero, devem ser implementadas sequencialmente antes ou junto com qualquer funcionalidade que delas dependa:
- **F01 Configuração de Ambiente e Infraestrutura** — inicializa o banco de dados PostgreSQL + pgVector via Docker Compose e estabelece o contrato de configuração `.env` (string de conexão, seleção de provedor, chaves de API, caminho do PDF) que todas as outras funcionalidades consomem na inicialização

### Ondas de Execução
Funcionalidades dentro da mesma onda podem ser construídas em paralelo. Uma onda começa somente após todas as funcionalidades das ondas anteriores estarem completas.

**Nota:** Funcionalidades fundamentais (ver "Funcionalidades Fundamentais" acima) não podem ser executadas em paralelo em um projeto do zero mesmo que apareçam juntas em uma onda — elas compartilham arquivos de scaffolding e devem ser implementadas sequencialmente até que a base esteja no lugar.

- **Onda 1**: F01
- **Onda 2**: F02
- **Onda 3**: F03
- **Onda 4**: F04

### Níveis de Prioridade
- **1** = Essencial — o produto não funciona sem isso
- **2** = Importante — adição significativa de valor
- **3** = Desejável — melhoria incremental

```mermaid
graph TD
  F01[Configuração de Infra] --> F02[Ingestão de PDF]
  F01 --> F03[Busca Semântica]
  F02 --> F03
  F03 --> F04[Chat via CLI]
```

## 9. Critérios de Aceitação

### F01. Configuração de Ambiente e Infraestrutura
- [ ] `docker compose up -d` inicia o container do postgres e ele reporta healthy em até 60 segundos
- [ ] A extensão pgVector está ativa após o bootstrap (confirmado com `SELECT extname FROM pg_extension WHERE extname = 'vector'` retornando uma linha)
- [ ] Executar qualquer script com uma variável `.env` obrigatória ausente imprime a mensagem "Variável de ambiente não encontrada" e sai com código 1
- [ ] Definir `PROVIDER=openai` faz os scripts instanciarem `OpenAIEmbeddings` e `ChatOpenAI`
- [ ] Definir `PROVIDER=gemini` faz os scripts instanciarem `GoogleGenerativeAIEmbeddings` e `ChatGoogleGenerativeAI`
- [ ] Definir `PROVIDER` para qualquer valor diferente de `openai` ou `gemini` imprime a mensagem "Valor inválido para PROVIDER" e sai com código 1

### F02. Ingestão de PDF
- [ ] Executar `python src/ingest.py` com um `.env` válido e banco de dados em execução completa sem erro
- [ ] O script imprime a mensagem de conclusão com uma contagem de blocos maior que zero
- [ ] A coleção `pdf_documents` no pgVector contém o número exato de vetores reportado na mensagem de conclusão
- [ ] Executar `python src/ingest.py` uma segunda vez sem alterar o PDF resulta na mesma contagem de blocos (sem duplicatas)
- [ ] Quando `PDF_PATH` aponta para um arquivo inexistente, o script imprime a mensagem "Arquivo PDF não encontrado" e sai com código 1
- [ ] Quando o banco de dados não está em execução, o script imprime a mensagem "Falha ao conectar ao banco de dados" e sai com código 1

### F03. Busca Semântica e Resposta do LLM
- [ ] `search_prompt("Qual o faturamento da Empresa X?")` retorna uma string não vazia contendo informações presentes no documento
- [ ] `search_prompt("Qual é a capital da França?")` retorna exatamente "Não tenho informações necessárias para responder sua pergunta."
- [ ] `search_prompt("Você acha isso bom ou ruim?")` retorna a mensagem de recusa padrão
- [ ] `search_prompt("Quantos clientes temos em 2024?")` retorna a mensagem de recusa padrão
- [ ] Chamar `search_prompt` antes de o `ingest.py` ter sido executado retorna a mensagem "Nenhum documento encontrado no banco"
- [ ] Tanto `PROVIDER=openai` quanto `PROVIDER=gemini` produzem respostas válidas e não vazias para perguntas dentro do contexto quando as chaves de API estão corretamente definidas

### F04. Interface de Chat via CLI
- [ ] Executar `python src/chat.py` entra no loop interativo e imprime a mensagem de inicialização
- [ ] Cada pergunta submetida pelo usuário produz uma resposta "RESPOSTA:" antes do próximo prompt "PERGUNTA:" aparecer
- [ ] Pressionar Enter sem digitar uma pergunta re-exibe "PERGUNTA:" sem erro ou resposta
- [ ] Múltiplas perguntas na mesma sessão recebem respostas corretas e independentes
- [ ] Ctrl+C sai do loop, imprime "Encerrando o chat. Até logo!" e retorna código de saída 0

### Integração entre Funcionalidades
- [ ] Após o `ingest.py` (F02) concluir, chamar `search_prompt` (F03) recupera com sucesso os blocos da coleção `pdf_documents` gravada pelo F02 — confirmado por um contexto não vazio no prompt do LLM
- [ ] Os valores de `CONNECTION_STRING` e `PROVIDER` do ambiente F01 são lidos de forma idêntica tanto pelo F02 (durante embedding e armazenamento) quanto pelo F03 (durante embedding e recuperação) — trocar de provedor durante a sessão sem re-ingerir produz um erro de incompatibilidade de dimensão, não uma resposta errada silenciosa
- [ ] O texto de resposta gerado pelo LLM retornado por `search_prompt` (F03) é exibido verbatim pelo `chat.py` (F04) sob o prefixo "RESPOSTA:" sem modificação ou truncamento
