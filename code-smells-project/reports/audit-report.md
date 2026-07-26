================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-166, 174, 188, 192, 220, 224, 279-281, 289-297
Description: Praticamente todas as queries são montadas por concatenação de string com input do usuário. Ex.: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` (l.28), `login_usuario` interpola email/senha direto (l.109-111), e `buscar_produtos` concatena `termo`/`categoria` (l.291-293).
Impact: Atacante pode ler, alterar ou apagar todo o banco (ex.: `email=' OR '1'='1` faz bypass de login).
Recommendation: Usar queries parametrizadas com placeholders `?` e passar valores como tupla em todas as chamadas `cursor.execute`.

### [CRITICAL] Hardcoded Credentials
File: app.py:7
Description: SECRET_KEY fixa no código: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`.
Impact: Segredo versionado no repositório permite forjar sessões/tokens.
Recommendation: Carregar de variável de ambiente (`os.environ["SECRET_KEY"]`), via módulo de config.

### [CRITICAL] Insecure Password Storage
File: models.py:105-120, 122-131
Description: Senhas gravadas e comparadas em texto plano — `criar_usuario` insere `senha` cru (l.126-129) e `login_usuario` faz `WHERE ... senha = '<senha>'` (l.109-111). Seeds também em claro (database.py:76-78).
Impact: Vazamento do banco expõe todas as senhas dos usuários imediatamente.
Recommendation: Hash com bcrypt/Argon2 + salt; no login, verificar o hash em vez de comparar texto.

### [CRITICAL] Sensitive Data Exposure
File: controllers.py:287-289 ; models.py:83, 99
Description: `/health` retorna `secret_key`, `debug` e `db_path` no JSON (l.287-289). Além disso `get_todos_usuarios`/`get_usuario_por_id` incluem o campo `senha` na resposta, exposto por `GET /usuarios` (models.py:83, 99).
Impact: Segredo da aplicação e senhas dos usuários acessíveis por endpoints públicos.
Recommendation: Remover segredos do health check e nunca serializar `senha` nas respostas de usuário.

### [CRITICAL] Missing Authentication
File: app.py:47-57, 59-78
Description: `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário do corpo da requisição — ambos sem qualquer verificação de autenticação/autorização.
Impact: Qualquer pessoa pode destruir ou ler o banco inteiro.
Recommendation: Exigir autenticação+autorização (admin) via middleware/decorator; idealmente remover `/admin/query`.

### [HIGH] God File / Multiple Responsibilities
File: models.py:1-314 ; controllers.py:1-292
Description: `models.py` concentra acesso a dados de 4 entidades + regra de negócio (cálculo de total do pedido, relatório de vendas). `controllers.py` mistura validação, roteamento HTTP, regra de negócio e notificações para todas as entidades.
Impact: Impossível testar/alterar uma entidade isoladamente; alto acoplamento.
Recommendation: Separar por entidade e camada — models/ (repositórios), controllers/ (orquestração), services/ (regra de negócio).

### [HIGH] N+1 Queries
File: models.py:171-201, 203-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` iteram pedidos e, dentro do loop, consultam itens e, em outro loop aninhado, o nome de cada produto (cursor2/cursor3).
Impact: Número de queries cresce com pedidos×itens; degrada e dá timeout com volume real.
Recommendation: Carregar tudo com JOINs (pedidos ⋈ itens_pedido ⋈ produtos) em uma consulta e agrupar em memória.

### [HIGH] Business Logic in Controllers
File: controllers.py:208-210, 247-250
Description: Envio de e-mail/SMS/push em `criar_pedido` e notificações de status em `atualizar_status_pedido` estão embutidos no controller (via `print`). Cálculo de total e baixa de estoque também vazam entre camadas (models.py:133-169).
Impact: Regra não reutilizável nem testável isoladamente; controller acumula responsabilidades.
Recommendation: Extrair para `NotificationService` e `PedidoService`.

### [HIGH] Missing / Improper Error Handling
File: controllers.py:10-12, 21-22, 60-62, ... (todos os handlers) ; app.py:77-78
Description: Cada handler tem `try/except Exception` que retorna `str(e)` ao cliente; erros são só impressos, sem logging estruturado nem tratamento centralizado.
Impact: Vaza detalhes internos/stack ao cliente e não há diagnóstico consistente.
Recommendation: Error handler centralizado (`@app.errorhandler`) com logging e respostas genéricas ao cliente.

### [MEDIUM] Code Duplication
File: controllers.py:28-54, 72-90 ; models.py:9-22, 30-40, 302-313
Description: Validação de produto repetida entre `criar_produto` e `atualizar_produto`; mapeamento row→dict de produto/usuário repetido em vários métodos do model.
Impact: Manutenção multiplicada e risco de divergência entre endpoints.
Recommendation: Extrair `validar_produto(dados)` e um helper `row_to_produto(row)`.

### [MEDIUM] Global Mutable State
File: database.py:4-11
Description: Conexão mantida em variável global `db_connection` com `check_same_thread=False`, compartilhada entre requisições.
Impact: Race conditions e estado imprevisível sob concorrência.
Recommendation: Usar conexão por requisição (app/request context) ou pool.

### [MEDIUM] Magic Strings / Numbers
File: controllers.py:52, 242 ; models.py:256-262
Description: Categorias e status como listas de strings literais espalhadas; faixas de desconto (10000/0.1, 5000/0.05, 1000/0.02) hardcoded no relatório.
Impact: Erros de digitação silenciosos e regras difíceis de manter.
Recommendation: Definir Enums/constantes para status e categorias; extrair regras de desconto para config/constantes.

### [MEDIUM] Missing Input Validation
File: controllers.py:146-165, 237-245
Description: `criar_usuario` não valida formato de e-mail nem tamanho de senha; `atualizar_status_pedido` não checa existência do pedido antes de atualizar.
Impact: Dados inválidos/inconsistentes no banco.
Recommendation: Validar formato de e-mail, força de senha e existência de entidades antes de persistir.

### [LOW] Print for Logging
File: controllers.py:8, 11, 57, 106, 161, 179, 182, 208-210, 219, 248-250 ; app.py:56, 83-86 ; database.py
Description: Uso de `print()` para log de operações e erros em vez de logging estruturado.
Impact: Sem níveis, rotação ou formatação padronizada.
Recommendation: Usar o módulo `logging` com níveis (info/error).

### [LOW] String Concatenation for Formatting
File: controllers.py:8, 11, 54, 57, 106, 208-209
Description: Mensagens montadas com `+ str(...)`, ex.: `"Listando " + str(len(produtos)) + " produtos"`.
Impact: Menos legível e propenso a erro.
Recommendation: Usar f-strings.

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
