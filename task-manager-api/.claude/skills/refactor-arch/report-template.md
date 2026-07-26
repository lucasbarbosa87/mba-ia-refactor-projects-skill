# Template de Relatório de Auditoria

Este documento define o formato padronizado do relatório gerado na Fase 2.

---

## Formato do Relatório

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: [nome do projeto/diretório]
Stack:   [linguagem] + [framework]
Files:   [número] analyzed | ~[número] lines of code

## Summary
CRITICAL: [n] | HIGH: [n] | MEDIUM: [n] | LOW: [n]

## Findings

### [SEVERITY] [Nome do Anti-Pattern]
File: [arquivo]:[linha-início]-[linha-fim]
Description: [descrição específica do problema encontrado]
Impact: [impacto concreto no projeto]
Recommendation: [ação recomendada para correção]

[... repetir para cada finding ...]

================================
Total: [número total] findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de Formatação

### 1. Cabeçalho

- **Project:** Nome do diretório raiz do projeto
- **Stack:** Formato `[Linguagem] + [Framework versão]`
  - Exemplo: `Python + Flask 3.1.1`
  - Exemplo: `Node.js + Express 4.18.2`
- **Files:** Número de arquivos de código analisados e estimativa de linhas

### 2. Summary

Contagem de findings por severidade, sempre na ordem:
```
CRITICAL: [n] | HIGH: [n] | MEDIUM: [n] | LOW: [n]
```

### 3. Findings

Ordenar por severidade (CRITICAL primeiro, depois HIGH, MEDIUM, LOW).

Dentro de cada severidade, ordenar por arquivo.

#### Formato de cada finding:

```
### [SEVERITY] [Nome do Anti-Pattern]
File: [caminho/arquivo.ext]:[linha]
Description: [O que está errado, com trecho de código se relevante]
Impact: [Por que isso é um problema]
Recommendation: [Como corrigir]
```

#### Exemplos:

```
### [CRITICAL] SQL Injection
File: models.py:25-27
Description: Query construída com concatenação de string: `"SELECT * FROM users WHERE id = " + str(id)`
Impact: Atacante pode executar SQL arbitrário, comprometendo todo o banco de dados.
Recommendation: Usar query parametrizada: `cursor.execute("SELECT * FROM users WHERE id = ?", [id])`

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY definida diretamente no código: `SECRET_KEY = "minha-chave-secreta-123"`
Impact: Credencial exposta no repositório permite forjar sessões de autenticação.
Recommendation: Usar variável de ambiente: `SECRET_KEY = os.environ.get('SECRET_KEY')`

### [HIGH] N+1 Queries
File: models.py:162-192
Description: Query executada dentro de loop for, resultando em N+1 queries para cada pedido.
Impact: Performance O(n²), degradação exponencial com volume de dados.
Recommendation: Usar JOIN ou eager loading para carregar dados relacionados em uma única query.

### [HIGH] God Class
File: AppManager.js:1-115
Description: Classe única contém inicialização de DB, definição de rotas e toda lógica de negócio.
Impact: Impossível testar em isolamento, qualquer mudança pode afetar sistema inteiro.
Recommendation: Separar em classes com responsabilidade única: DatabaseService, Routes, PaymentService.

### [MEDIUM] Code Duplication
File: controllers.py:28-49, 67-82
Description: Mesma lógica de validação de produto repetida em criar_produto() e atualizar_produto().
Impact: Manutenção duplicada, risco de inconsistências entre endpoints.
Recommendation: Extrair para função validate_product_data() reutilizável.

### [LOW] Poor Naming
File: AppManager.js:28-32
Description: Variáveis com nomes não descritivos: `u`, `e`, `p`, `cid`, `cc`
Impact: Código difícil de entender e manter.
Recommendation: Usar nomes descritivos: `userName`, `email`, `password`, `courseId`, `creditCard`
```

### 4. Rodapé

```
================================
Total: [N] findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Campos Obrigatórios por Finding

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| Severity | Sim | CRITICAL, HIGH, MEDIUM ou LOW |
| Nome | Sim | Nome do anti-pattern (do catálogo) |
| File | Sim | Caminho do arquivo e linha(s) |
| Description | Sim | O que está errado (específico) |
| Impact | Sim | Consequência do problema |
| Recommendation | Sim | Ação corretiva |

---

## Exemplo Completo de Relatório

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] SQL Injection
File: models.py:25-27
Description: Query construída com concatenação: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
Impact: Permite execução de SQL arbitrário por atacantes.
Recommendation: Usar query parametrizada com placeholders.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Impact: Credencial exposta permite forjar tokens de sessão.
Recommendation: Mover para variável de ambiente.

### [CRITICAL] Missing Authentication
File: app.py:51-66
Description: Endpoint `/admin/query` executa SQL arbitrário sem verificar autenticação.
Impact: Qualquer pessoa pode executar comandos SQL na aplicação.
Recommendation: Adicionar middleware de autenticação e autorização.

### [CRITICAL] Sensitive Data Exposure
File: controllers.py:248
Description: Health check retorna SECRET_KEY na resposta JSON.
Impact: Credencial de segurança exposta em endpoint público.
Recommendation: Remover dados sensíveis do health check.

### [HIGH] Insecure Password Storage
File: models.py:96-106
Description: Senhas armazenadas e comparadas em texto plano sem hash.
Impact: Vazamento do banco expõe todas as senhas.
Recommendation: Implementar hash com bcrypt ou Argon2.

### [HIGH] N+1 Queries
File: models.py:162-192
Description: Loop com queries aninhadas em get_pedidos_usuario().
Impact: Performance O(n²), timeout com volume de dados.
Recommendation: Usar JOINs para carregar dados relacionados.

### [HIGH] Business Logic in Routes
File: controllers.py:171-173
Description: Envio de notificações (email, SMS, push) implementado diretamente no controller.
Impact: Lógica não testável isoladamente, não reutilizável.
Recommendation: Extrair para NotificationService.

### [HIGH] God Class
File: models.py:1-250
Description: Arquivo único contém todas as operações de banco para 4 entidades diferentes.
Impact: Impossível testar ou modificar uma entidade sem afetar outras.
Recommendation: Separar em arquivos por entidade: ProdutoModel, UsuarioModel, PedidoModel.

### [HIGH] Missing Error Handling
File: app.py:51-66
Description: Endpoint admin/query não trata erros de SQL, apenas retorna exceção raw.
Impact: Stack traces expostos, erros não logados adequadamente.
Recommendation: Implementar error handler centralizado.

### [MEDIUM] Code Duplication
File: controllers.py:28-49, 67-82
Description: Validação de produto duplicada entre criar_produto e atualizar_produto.
Impact: Manutenção multiplicada, possíveis inconsistências.
Recommendation: Extrair para função de validação única.

### [MEDIUM] Magic Strings
File: controllers.py:204
Description: Status de pedido como strings literais: "pendente", "aprovado", "enviado"
Impact: Erros de digitação passam silenciosamente.
Recommendation: Definir constantes ou Enum para status.

### [LOW] Print Logging
File: controllers.py:10, 57
Description: Uso de print() para logging ao invés de biblioteca adequada.
Impact: Sem níveis de log, rotação ou formatação.
Recommendation: Usar módulo logging do Python.

### [LOW] String Concatenation
File: controllers.py:10
Description: Concatenação com + ao invés de f-strings: `"Listando " + str(len(produtos)) + " produtos"`
Impact: Menos legível, estilo antiquado.
Recommendation: Usar f-strings: `f"Listando {len(produtos)} produtos"`

### [LOW] Global Mutable State
File: database.py:5-6
Description: Variável global db_connection para conexão de banco.
Impact: Dificulta testes e operação multi-thread.
Recommendation: Usar connection pool ou injeção de dependência.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Critérios de Qualidade do Relatório

- [ ] Mínimo de 5 findings identificados
- [ ] Pelo menos 1 finding CRITICAL ou HIGH
- [ ] Cada finding tem arquivo e linha exatos
- [ ] Findings ordenados por severidade
- [ ] Descrições são específicas (não genéricas)
- [ ] Recomendações são acionáveis
- [ ] Pergunta de confirmação presente no final
