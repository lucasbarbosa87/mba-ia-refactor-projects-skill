# Catálogo de Anti-Patterns

Este documento define os anti-patterns a serem detectados na Fase 2, com sinais de identificação, severidade e recomendações.

---

## Severidades

- **CRITICAL:** Falhas graves de segurança ou arquitetura que expõem dados sensíveis ou impedem funcionamento correto
- **HIGH:** Fortes violações de MVC/SOLID que dificultam muito manutenção e testes
- **MEDIUM:** Problemas de padronização, duplicação ou performance moderada
- **LOW:** Melhorias de legibilidade e nomenclatura

---

## CRITICAL

### 1. SQL Injection

**Severidade:** CRITICAL

**Descrição:** Queries SQL construídas com concatenação de strings ou interpolação direta de input do usuário.

**Sinais de detecção:**

```python
# Python - VULNERÁVEL
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = '%s'" % user_id)
query = "SELECT * FROM users WHERE name = '" + name + "'"
```

```javascript
// JavaScript - VULNERÁVEL
db.query("SELECT * FROM users WHERE id = " + userId);
db.query(`SELECT * FROM users WHERE id = ${userId}`);
db.run("DELETE FROM users WHERE id = " + req.params.id);
```

**Impacto:** Atacante pode ler, modificar ou deletar todo o banco de dados.

**Recomendação:** Usar queries parametrizadas ou prepared statements.

---

### 2. Hardcoded Credentials

**Severidade:** CRITICAL

**Descrição:** Credenciais, chaves de API ou secrets definidos diretamente no código-fonte.

**Sinais de detecção:**

```python
# Python - VULNERÁVEL
SECRET_KEY = "minha-chave-secreta-123"
DB_PASSWORD = "senha123"
API_KEY = "sk_live_xxxxx"
app.config['SECRET_KEY'] = 'hardcoded-secret'
```

```javascript
// JavaScript - VULNERÁVEL
const config = {
    dbPassword: "senha_secreta",
    apiKey: "pk_live_12345",
    jwtSecret: "my-secret-key"
};
const SECRET = "hardcoded-value";
```

**Padrões regex:**
- `(password|passwd|pwd|secret|key|token|api_key|apikey)\s*[:=]\s*['"][^'"]+['"]`
- `(sk_live|pk_live|sk_test|pk_test)_[a-zA-Z0-9]+`

**Impacto:** Credenciais expostas no repositório comprometem segurança de toda aplicação.

**Recomendação:** Usar variáveis de ambiente ou serviço de secrets (AWS Secrets Manager, HashiCorp Vault).

---

### 3. Insecure Password Storage

**Severidade:** CRITICAL

**Descrição:** Senhas armazenadas em texto plano, com encoding reversível (base64) ou hash fraco (MD5, SHA1).

**Sinais de detecção:**

```python
# VULNERÁVEL - Texto plano
user.password = senha
if user.password == senha_digitada:

# VULNERÁVEL - MD5
import hashlib
hashlib.md5(password.encode()).hexdigest()

# VULNERÁVEL - SHA1
hashlib.sha1(password.encode()).hexdigest()
```

```javascript
// VULNERÁVEL - Base64
Buffer.from(password).toString('base64')

// VULNERÁVEL - Comparação direta
if (user.pass === inputPassword)

// VULNERÁVEL - MD5
crypto.createHash('md5').update(password).digest('hex')
```

**Impacto:** Vazamento do banco expõe todas as senhas dos usuários.

**Recomendação:** Usar bcrypt, Argon2 ou PBKDF2 com salt.

---

### 4. Sensitive Data Exposure

**Severidade:** CRITICAL

**Descrição:** Dados sensíveis expostos em logs, respostas de API ou endpoints públicos.

**Sinais de detecção:**

```python
# VULNERÁVEL - Log de dados sensíveis
print(f"Senha do usuário: {senha}")
print(f"Cartão: {numero_cartao}")
logger.info(f"Token: {api_token}")

# VULNERÁVEL - Retorno de senha na API
return {"user": user.name, "password": user.password}
```

```javascript
// VULNERÁVEL - Log de dados sensíveis
console.log(`Card: ${creditCard}`);
console.log(`Processing with key ${apiKey}`);

// VULNERÁVEL - Exposição em response
res.json({ password: user.password, secret: config.secret });
```

**Impacto:** Dados sensíveis acessíveis a atacantes ou em logs de produção.

**Recomendação:** Nunca logar ou retornar senhas, tokens, números de cartão ou PII.

---

### 5. Missing Authentication

**Severidade:** CRITICAL

**Descrição:** Endpoints administrativos ou sensíveis sem verificação de autenticação.

**Sinais de detecção:**

```python
# VULNERÁVEL - Endpoint admin sem auth
@app.route('/admin/delete-all', methods=['POST'])
def delete_all():
    db.execute("DELETE FROM users")
    
@app.route('/admin/query', methods=['POST'])
def run_query():
    query = request.json['sql']
    cursor.execute(query)  # Executa SQL arbitrário!
```

```javascript
// VULNERÁVEL - Rota admin sem middleware de auth
app.delete('/api/users/:id', (req, res) => {
    db.run("DELETE FROM users WHERE id = ?", [req.params.id]);
});

app.post('/admin/reset-db', (req, res) => {
    // Sem verificação de auth!
});
```

**Impacto:** Qualquer pessoa pode executar operações administrativas.

**Recomendação:** Implementar middleware de autenticação e autorização.

---

## HIGH

### 6. God Class / God File

**Severidade:** HIGH

**Descrição:** Uma única classe ou arquivo concentra múltiplas responsabilidades (banco de dados, lógica de negócio, rotas, etc.).

**Sinais de detecção:**
- Arquivo com mais de 500 linhas de código
- Classe que faz: conexão DB + queries + validação + roteamento
- Arquivo com mais de 10 funções/métodos públicos não relacionados
- Imports de muitos módulos diferentes (DB, HTTP, email, etc.)

**Exemplo:**
```javascript
// VULNERÁVEL - God Class
class AppManager {
    constructor() {
        this.db = new Database();  // Gerencia DB
    }
    
    setupRoutes(app) {            // Define rotas
        app.get('/users', ...);
        app.post('/checkout', ...);
    }
    
    processPayment() { }          // Lógica de negócio
    sendEmail() { }               // Notificações
    generateReport() { }          // Relatórios
}
```

**Impacto:** Impossível testar em isolamento, mudança em uma área afeta todas as outras.

**Recomendação:** Separar em classes/módulos com responsabilidade única (SRP).

---

### 7. N+1 Queries

**Severidade:** HIGH

**Descrição:** Query executada dentro de loop, gerando N queries adicionais para N registros.

**Sinais de detecção:**

```python
# VULNERÁVEL
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    # Query dentro do loop!
    itens = db.execute(f"SELECT * FROM itens WHERE pedido_id = {pedido.id}")
    for item in itens:
        # Outro nível de N+1!
        produto = db.execute(f"SELECT * FROM produtos WHERE id = {item.produto_id}")
```

```javascript
// VULNERÁVEL
const orders = await db.query("SELECT * FROM orders");
for (const order of orders) {
    // Query dentro do loop!
    const items = await db.query("SELECT * FROM items WHERE order_id = ?", [order.id]);
}
```

**Padrões:**
- `for`/`foreach` seguido de query no mesmo bloco
- Callbacks aninhados com queries em cada nível

**Impacto:** Performance O(n²) ou pior, timeout com volume de dados real.

**Recomendação:** Usar JOINs, eager loading ou batch queries.

---

### 8. Business Logic in Routes/Controllers

**Severidade:** HIGH

**Descrição:** Lógica de negócio complexa implementada diretamente em handlers de rota.

**Sinais de detecção:**

```python
# VULNERÁVEL - Lógica de negócio na rota
@app.route('/checkout', methods=['POST'])
def checkout():
    # Validação complexa
    if not validate_card(request.json['card']):
        return error
    
    # Cálculo de desconto
    discount = calculate_discount(user, items)
    
    # Processamento de pagamento
    payment = process_payment(card, total)
    
    # Envio de notificações
    send_email(user.email, "Pedido confirmado")
    send_sms(user.phone, "Seu pedido foi recebido")
    
    # Atualização de estoque
    for item in items:
        update_stock(item.product_id, item.quantity)
```

**Impacto:** Código não reutilizável, impossível testar lógica separadamente.

**Recomendação:** Extrair para camada de Services ou Controllers.

---

### 9. Missing Error Handling

**Severidade:** HIGH

**Descrição:** Ausência de tratamento de erros adequado, expondo stack traces ou falhando silenciosamente.

**Sinais de detecção:**

```python
# VULNERÁVEL - Catch genérico sem tratamento
try:
    result = do_something()
except:
    pass  # Silencia erro!

# VULNERÁVEL - Expõe detalhes internos
except Exception as e:
    return {"error": str(e)}  # Stack trace para o cliente
```

```javascript
// VULNERÁVEL - Sem tratamento
db.query(sql, (err, result) => {
    res.json(result);  // E se err existir?
});

// VULNERÁVEL - Catch vazio
try {
    await process();
} catch (e) {
    // Nada aqui
}
```

**Impacto:** Erros não diagnosticados, possível exposição de informações internas.

**Recomendação:** Implementar error handling centralizado com logging adequado.

---

### 10. Callback Hell / Pyramid of Doom

**Severidade:** HIGH

**Descrição:** Múltiplos níveis de callbacks aninhados tornando código ilegível.

**Sinais de detecção:**

```javascript
// VULNERÁVEL - Callback hell
db.query("SELECT * FROM users", (err, users) => {
    if (err) return res.status(500).send("Error");
    db.query("SELECT * FROM orders", (err, orders) => {
        if (err) return res.status(500).send("Error");
        db.query("SELECT * FROM items", (err, items) => {
            if (err) return res.status(500).send("Error");
            db.query("SELECT * FROM products", (err, products) => {
                // 4+ níveis de aninhamento
            });
        });
    });
});
```

**Critério:** 4 ou mais níveis de callbacks aninhados.

**Impacto:** Código ilegível, difícil debugar, propenso a erros.

**Recomendação:** Usar Promises, async/await ou refatorar em funções separadas.

---

## MEDIUM

### 11. Code Duplication

**Severidade:** MEDIUM

**Descrição:** Blocos de código repetidos em múltiplos lugares.

**Sinais de detecção:**
- Mesma validação em múltiplos endpoints
- Mesma lógica de formatação/transformação repetida
- Copy-paste de blocos de código

```python
# VULNERÁVEL - Validação duplicada
def create_product():
    if not data.get('name'):
        return error
    if len(data['name']) < 3:
        return error
    if data['price'] < 0:
        return error
    # ...

def update_product():
    # Mesma validação repetida!
    if not data.get('name'):
        return error
    if len(data['name']) < 3:
        return error
    if data['price'] < 0:
        return error
```

**Impacto:** Manutenção multiplicada, risco de inconsistências.

**Recomendação:** Extrair para funções reutilizáveis ou decorators/middlewares.

---

### 12. Global Mutable State

**Severidade:** MEDIUM

**Descrição:** Variáveis globais mutáveis compartilhadas entre requisições.

**Sinais de detecção:**

```python
# VULNERÁVEL
db_connection = None  # Global mutável
cache = {}            # Estado compartilhado

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = connect()
    return db_connection
```

```javascript
// VULNERÁVEL
let globalCache = {};
let totalRevenue = 0;

module.exports = { globalCache, totalRevenue };
```

**Impacto:** Race conditions, estado imprevisível entre requisições.

**Recomendação:** Usar injeção de dependência ou contexto de requisição.

---

### 13. Missing Input Validation

**Severidade:** MEDIUM

**Descrição:** Inputs do usuário não são validados antes de processamento.

**Sinais de detecção:**

```python
# VULNERÁVEL - Sem validação
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Usa dados diretamente sem validar
    user = User(name=data['name'], email=data['email'])
    db.save(user)
```

```javascript
// VULNERÁVEL - Sem validação de tipo/formato
app.post('/users', (req, res) => {
    const { name, email, age } = req.body;
    // Nenhuma validação!
    db.run("INSERT INTO users VALUES (?, ?, ?)", [name, email, age]);
});
```

**Impacto:** Dados inválidos no banco, possíveis erros de runtime.

**Recomendação:** Validar tipos, formatos e limites de todos os inputs.

---

### 14. Magic Strings / Magic Numbers

**Severidade:** MEDIUM

**Descrição:** Valores literais espalhados pelo código sem constantes nomeadas.

**Sinais de detecção:**

```python
# VULNERÁVEL
if status == "pending":      # Magic string
    discount = price * 0.1   # Magic number
elif status == "approved":
    discount = price * 0.05
    
if user.role == "admin":     # Magic string repetida
```

```javascript
// VULNERÁVEL
if (order.status === 'pending') {
    timeout = 3600000;  // O que é esse número?
}
const TAX = 0.23;  // OK, mas usado como 0.23 em outros lugares
```

**Impacto:** Erros de digitação, difícil refatorar ou internacionalizar.

**Recomendação:** Definir constantes nomeadas ou enums.

---

## LOW

### 15. Poor Naming Conventions

**Severidade:** LOW

**Descrição:** Variáveis, funções ou classes com nomes não descritivos.

**Sinais de detecção:**

```python
# VULNERÁVEL
def f(x, y):
    return x + y

def process(d):
    # O que é 'd'?
    pass

temp = get_data()  # 'temp' não diz nada
```

```javascript
// VULNERÁVEL
let u = req.body.usr;
let e = req.body.eml;
let p = req.body.pwd;
let cid = req.body.c_id;
let cc = req.body.card;

function fn(a, b, c) { }
```

**Impacto:** Código difícil de entender e manter.

**Recomendação:** Usar nomes descritivos que indiquem propósito.

---

### 16. Console.log / Print for Logging

**Severidade:** LOW

**Descrição:** Uso de print/console.log ao invés de logging estruturado.

**Sinais de detecção:**

```python
# VULNERÁVEL
print("Usuário criado")
print(f"Erro: {e}")
print("DEBUG:", data)
```

```javascript
// VULNERÁVEL
console.log("Starting server...");
console.log("Error:", err);
console.log("DEBUG", data);
```

**Impacto:** Sem níveis de log, rotação ou formatação padronizada.

**Recomendação:** Usar biblioteca de logging (Python: logging, Node: winston/pino).

---

### 17. Unused Imports / Dead Code

**Severidade:** LOW

**Descrição:** Imports não utilizados ou código morto que nunca é executado.

**Sinais de detecção:**

```python
# VULNERÁVEL
import os, sys, json, time  # Nenhum usado
from utils import helper    # Nunca chamado

def unused_function():      # Nunca chamada
    pass
```

```javascript
// VULNERÁVEL
const fs = require('fs');      // Nunca usado
const moment = require('moment'); // Nunca usado

function oldImplementation() {  // Código morto
    // ...
}
```

**Impacto:** Código poluído, confusão sobre dependências reais.

**Recomendação:** Remover imports não utilizados e código morto.

---

### 18. Deprecated APIs

**Severidade:** LOW

**Descrição:** Uso de APIs obsoletas que serão removidas em versões futuras.

**Sinais de detecção (Python):**

| Deprecated | Substituto |
|------------|------------|
| `urllib2` | `urllib.request` |
| `optparse` | `argparse` |
| `imp` | `importlib` |
| `asyncio.get_event_loop()` | `asyncio.get_running_loop()` |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |

**Sinais de detecção (Node.js):**

| Deprecated | Substituto |
|------------|------------|
| `new Buffer()` | `Buffer.from()` / `Buffer.alloc()` |
| `url.parse()` | `new URL()` |
| `fs.exists()` | `fs.access()` / `fs.stat()` |
| `querystring` | `URLSearchParams` |
| `crypto.createCipher()` | `crypto.createCipheriv()` |

**Impacto:** Código quebrará em atualizações futuras.

**Recomendação:** Migrar para APIs modernas.

---

## Resumo por Severidade

| Severidade | Anti-patterns |
|------------|---------------|
| CRITICAL | SQL Injection, Hardcoded Credentials, Insecure Password Storage, Sensitive Data Exposure, Missing Authentication |
| HIGH | God Class, N+1 Queries, Business Logic in Routes, Missing Error Handling, Callback Hell |
| MEDIUM | Code Duplication, Global Mutable State, Missing Input Validation, Magic Strings/Numbers |
| LOW | Poor Naming, Console.log Logging, Unused Imports, Deprecated APIs |
