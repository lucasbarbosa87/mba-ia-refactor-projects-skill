================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   14 analyzed | ~1158 lines of code

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials
File: app.py:11-13
Description: URI do banco e SECRET_KEY definidos direto no código: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e `'sqlite:///tasks.db'`.
Impact: Credencial de assinatura de sessão exposta no repositório permite forjar tokens/sessões; configuração não varia por ambiente.
Recommendation: Externalizar em módulo de config lendo de variáveis de ambiente (`os.environ` / python-dotenv), com fallback apenas para dev.

### [CRITICAL] Hardcoded Credentials
File: services/notification_service.py:7-10
Description: Credenciais de SMTP hardcoded: `self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'`.
Impact: Senha de e-mail exposta em texto plano no código-fonte, comprometendo a conta de envio.
Recommendation: Ler host/porta/usuário/senha de variáveis de ambiente via módulo de config.

### [CRITICAL] Insecure Password Storage
File: models/user.py:27-32
Description: Senhas são hasheadas com MD5: `hashlib.md5(pwd.encode()).hexdigest()` em `set_password` e `check_password`.
Impact: MD5 é criptograficamente quebrado e sem salt; vazamento do banco expõe todas as senhas via rainbow tables.
Recommendation: Usar bcrypt, Argon2 ou PBKDF2 com salt (ex.: `werkzeug.security.generate_password_hash` / `check_password_hash`).

### [CRITICAL] Sensitive Data Exposure
File: models/user.py:16-25
Description: `User.to_dict()` inclui o campo `'password'` (hash) no dicionário retornado, e é usado nas respostas de `create_user` (user_routes.py:85) e `login` (user_routes.py:209).
Impact: O hash de senha é devolvido em respostas JSON de endpoints públicos, expondo material sensível a qualquer cliente.
Recommendation: Remover `password` do `to_dict()`; expor apenas campos seguros (id, name, email, role, active, created_at).

### [CRITICAL] Missing Authentication
File: user_routes.py:134-151, 185-211
Description: Endpoints destrutivos e sensíveis não têm autenticação/autorização: `DELETE /users/<id>` remove usuário e todas as tasks sem verificar identidade; `login` emite um token falso `'fake-jwt-token-' + str(user.id)`. O mesmo vale para `DELETE /tasks/<id>` (task_routes.py:225) e `DELETE /categories/<id>` (report_routes.py:211).
Impact: Qualquer pessoa pode deletar usuários, tasks e categorias; não há autenticação real protegendo a API.
Recommendation: Implementar autenticação real (JWT assinado) e um decorator/middleware de autorização aplicado às rotas mutáveis/admin.

### [HIGH] N+1 Queries
File: task_routes.py:41-57
Description: Em `get_tasks`, para cada task o código executa `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` dentro do loop, gerando 2N queries extras. Padrão repetido em report_routes.py:53-68 e 55-61.
Impact: Performance degrada linearmente com o número de tasks/usuários; timeouts com volume real de dados.
Recommendation: Usar eager loading (`joinedload`) ou JOINs, aproveitando os relacionamentos `Task.user`/`Task.category` já definidos.

### [HIGH] Business Logic in Routes
File: task_routes.py:85-154, report_routes.py:12-101
Description: Validação, montagem de payload, parsing de datas, cálculo de "overdue", agregações e estatísticas estão implementados diretamente nos handlers de rota (ex.: `summary_report` concentra toda a lógica de relatório).
Impact: Lógica não reutilizável e impossível de testar isoladamente das rotas HTTP; handlers enormes e frágeis.
Recommendation: Extrair para camada de Controllers/Services (TaskController, ReportService, etc.), deixando as rotas apenas roteando.

### [HIGH] Missing Error Handling
File: task_routes.py:62-63, 236-238; user_routes.py:130-132; report_routes.py:186-188, 207-209, 221-223
Description: Múltiplos `except:` nus que silenciam qualquer erro e retornam mensagem genérica, sem logging estruturado nem distinção de causa.
Impact: Erros reais (ex.: falha de banco) ficam ocultos e indiagnosticáveis; comportamento imprevisível.
Recommendation: Centralizar tratamento de erros com error handlers do Flask (`@app.errorhandler`) e logging adequado; capturar exceções específicas.

### [HIGH] God File / Misplaced Responsibility
File: report_routes.py:1-223
Description: O blueprint de "reports" também contém o CRUD completo de Categorias (`get_categories`, `create_category`, `update_category`, `delete_category`, linhas 157-223), misturando dois domínios no mesmo arquivo.
Impact: Responsabilidades sem coesão; difícil localizar e manter código de categorias; acoplamento entre features distintas.
Recommendation: Separar categorias em seu próprio módulo/controller (CategoryController + category_routes) e manter reports isolado.

### [HIGH] Code Duplication
File: task_routes.py:30-39 & 71-80; user_routes.py:171-180; report_routes.py:34-37 & 132-135
Description: A lógica de cálculo de "overdue" (due_date < agora AND status not in done/cancelled) está copiada em pelo menos 5 lugares, além de já existir em `Task.is_overdue()` (models/task.py:50). A validação de task também é duplicada entre `create_task` e `update_task`.
Impact: Manutenção multiplicada e risco de regras inconsistentes entre endpoints.
Recommendation: Reutilizar `Task.is_overdue()` e extrair validações para uma função/serviço único.

### [MEDIUM] Missing Input Validation
File: task_routes.py:260-264
Description: Em `search_tasks`, `int(priority)` e `int(user_id)` são chamados diretamente sobre query params sem validação/try-except.
Impact: Um valor não numérico (`?priority=abc`) gera `ValueError` não tratado e HTTP 500.
Recommendation: Validar e converter parâmetros com segurança, retornando 400 para entradas inválidas.

### [MEDIUM] Magic Strings / Magic Numbers
File: task_routes.py:110, 177; report_routes.py:19-28; models/task.py:39
Description: Status (`'pending'`, `'in_progress'`, `'done'`, `'cancelled'`), roles (`'user'`, `'admin'`, `'manager'`) e faixas de prioridade (1-5) aparecem como literais espalhados por rotas e models.
Impact: Erros de digitação passam silenciosamente; refatoração e i18n difíceis.
Recommendation: Centralizar em constantes/Enums (parte já existe em utils/helpers.py:110-116, mas não é reutilizada).

### [MEDIUM] Global Configuration / No Config Layer
File: app.py:9-31
Description: A aplicação é instanciada e configurada em escopo de módulo, com `db.create_all()` no import e sem factory (`create_app`) nem separação de config por ambiente.
Impact: Dificulta testes (import causa efeitos colaterais), múltiplos ambientes e injeção de configuração.
Recommendation: Adotar application factory (`create_app(config)`) e módulo `config/` com classes por ambiente.

### [LOW] Print for Logging
File: task_routes.py:149,153,219,234; user_routes.py:83,89,147; services/notification_service.py:21,24; utils/helpers.py:38-40
Description: Uso de `print()` para logging em vez de biblioteca de logging estruturado.
Impact: Sem níveis, formatação ou rotação de log; ruído em produção.
Recommendation: Usar o módulo `logging` do Python com níveis e handlers configurados.

### [LOW] Unused Imports / Dead Code
File: app.py:7; task_routes.py:7; user_routes.py:6; report_routes.py:8; utils/helpers.py:3-6
Description: Imports não utilizados: `os, sys, json` em app.py (só `datetime` é usado); `json, os, sys, time` em task_routes.py; `hashlib, json` em user_routes.py; `json` em report_routes.py; `os, json, sys, math` em helpers.py.
Impact: Poluição do código e confusão sobre dependências reais.
Recommendation: Remover imports não utilizados.

### [LOW] Deprecated APIs
File: models/user.py:14; models/task.py:15-16; task_routes.py (várias); report_routes.py (várias); seed.py:66-75
Description: Uso disseminado de `datetime.utcnow()`, deprecado a partir do Python 3.12.
Impact: Gera DeprecationWarning e quebrará em versões futuras; produz datetimes "naive" sem timezone.
Recommendation: Migrar para `datetime.now(timezone.utc)`.

================================
Total: 16 findings
================================
