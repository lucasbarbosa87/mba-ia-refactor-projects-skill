# Guidelines de Arquitetura MVC

Este documento define a estrutura alvo e as responsabilidades de cada camada no padrão MVC (Model-View-Controller) para a refatoração.

---

## Visão Geral do Padrão MVC

```
┌─────────────────────────────────────────────────────────────┐
│                         REQUEST                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     ROUTES / VIEWS                           │
│  • Recebe requisições HTTP                                   │
│  • Valida formato básico                                     │
│  • Delega para Controller                                    │
│  • Formata resposta HTTP                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CONTROLLERS                             │
│  • Orquestra fluxo da operação                              │
│  • Implementa lógica de negócio                             │
│  • Chama Services quando necessário                         │
│  • Interage com Models para dados                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        MODELS                                │
│  • Define estrutura dos dados                               │
│  • Abstrai acesso ao banco de dados                         │
│  • Encapsula queries SQL/ORM                                │
│  • Validação de dados de domínio                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Diretórios Alvo

### Python/Flask

```
projeto/
├── app.py                    # Entry point (composition root)
├── config/
│   ├── __init__.py
│   └── settings.py           # Configurações (env vars)
├── models/
│   ├── __init__.py
│   ├── base.py               # Conexão DB / Base Model
│   ├── user.py               # User model
│   ├── product.py            # Product model
│   └── order.py              # Order model
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py    # Lógica de usuários
│   ├── product_controller.py # Lógica de produtos
│   └── order_controller.py   # Lógica de pedidos
├── routes/
│   ├── __init__.py
│   ├── user_routes.py        # Rotas de usuários
│   ├── product_routes.py     # Rotas de produtos
│   └── order_routes.py       # Rotas de pedidos
├── services/                 # Opcional - serviços externos
│   ├── __init__.py
│   ├── email_service.py
│   └── payment_service.py
├── middlewares/
│   ├── __init__.py
│   ├── auth.py               # Middleware de autenticação
│   └── error_handler.py      # Handler de erros centralizado
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Funções utilitárias
└── requirements.txt
```

### Node.js/Express

```
projeto/
├── src/
│   ├── app.js                # Entry point
│   ├── config/
│   │   └── index.js          # Configurações (env vars)
│   ├── models/
│   │   ├── index.js          # Exporta todos os models
│   │   ├── User.js
│   │   ├── Product.js
│   │   └── Order.js
│   ├── controllers/
│   │   ├── index.js
│   │   ├── userController.js
│   │   ├── productController.js
│   │   └── orderController.js
│   ├── routes/
│   │   ├── index.js          # Agrupa todas as rotas
│   │   ├── userRoutes.js
│   │   ├── productRoutes.js
│   │   └── orderRoutes.js
│   ├── services/
│   │   ├── emailService.js
│   │   └── paymentService.js
│   ├── middlewares/
│   │   ├── auth.js
│   │   └── errorHandler.js
│   └── utils/
│       └── helpers.js
├── package.json
└── .env.example
```

---

## Responsabilidades por Camada

### 1. Config

**Responsabilidade:** Centralizar todas as configurações da aplicação.

**DEVE conter:**
- Carregamento de variáveis de ambiente
- Configurações de banco de dados
- Chaves e secrets (via env vars)
- Configurações por ambiente (dev/staging/prod)

**NÃO DEVE conter:**
- Lógica de negócio
- Valores hardcoded de credenciais

**Exemplo Python:**
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

**Exemplo JavaScript:**
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
    secretKey: process.env.SECRET_KEY || 'dev-key',
    databaseUrl: process.env.DATABASE_URL || 'sqlite::memory:',
    port: parseInt(process.env.PORT) || 3000,
    env: process.env.NODE_ENV || 'development'
};
```

---

### 2. Models

**Responsabilidade:** Representar dados e encapsular acesso ao banco.

**DEVE conter:**
- Definição de estrutura/schema
- Queries de CRUD básico
- Validações de dados de domínio
- Relacionamentos entre entidades

**NÃO DEVE conter:**
- Lógica de negócio complexa
- Formatação para API
- Tratamento de requisições HTTP

**Exemplo Python (sqlite3 puro):**
```python
# models/base.py
import sqlite3
from config.settings import Config

def get_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
    return conn
```

```python
# models/user.py
from models.base import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, name=None, email=None, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return User(
            id=row['id'], name=row['name'],
            email=row['email'], password_hash=row['password']
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, email):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", [email]
            ).fetchone()
            return cls._from_row(row)
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, user_id):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", [user_id]
            ).fetchone()
            return cls._from_row(row)
        finally:
            conn.close()

    def save(self):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                [self.name, self.email, self.password_hash]
            )
            self.id = cursor.lastrowid
            conn.commit()
            return self
        finally:
            conn.close()
```

**Exemplo JavaScript:**
```javascript
// models/User.js
const db = require('../config/database');
const bcrypt = require('bcrypt');

class User {
    static async findById(id) {
        return new Promise((resolve, reject) => {
            db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }
    
    static async findByEmail(email) {
        return new Promise((resolve, reject) => {
            db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }
    
    static async create(data) {
        const hashedPassword = await bcrypt.hash(data.password, 10);
        return new Promise((resolve, reject) => {
            db.run(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                [data.name, data.email, hashedPassword],
                function(err) {
                    if (err) reject(err);
                    else resolve({ id: this.lastID });
                }
            );
        });
    }
    
    static async verifyPassword(plainPassword, hashedPassword) {
        return bcrypt.compare(plainPassword, hashedPassword);
    }
}

module.exports = User;
```

---

### 3. Controllers

**Responsabilidade:** Implementar lógica de negócio e orquestrar operações.

**DEVE conter:**
- Lógica de negócio
- Validação de regras de negócio
- Orquestração de múltiplos models
- Chamadas a services externos

**NÃO DEVE conter:**
- Detalhes de HTTP (req, res)
- Definição de rotas
- Acesso direto ao banco

**Exemplo Python:**
```python
# controllers/user_controller.py
from models.user import User
from services.email_service import EmailService

class UserController:
    def __init__(self):
        self.email_service = EmailService()
    
    def create_user(self, name, email, password):
        # Validação de negócio
        if User.find_by_email(email):
            raise ValueError('Email já cadastrado')
        
        if len(password) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')
        
        # Criação
        user = User(name=name, email=email)
        user.set_password(password)
        user.save()
        
        # Efeito colateral
        self.email_service.send_welcome_email(user.email, user.name)
        
        return user
    
    def authenticate(self, email, password):
        user = User.find_by_email(email)
        
        if not user or not user.check_password(password):
            raise ValueError('Credenciais inválidas')
        
        if not user.active:
            raise ValueError('Usuário inativo')
        
        return user
    
    def get_user(self, user_id):
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError('Usuário não encontrado')
        return user
```

**Exemplo JavaScript:**
```javascript
// controllers/userController.js
const User = require('../models/User');
const emailService = require('../services/emailService');

class UserController {
    async createUser(name, email, password) {
        // Validação de negócio
        const existing = await User.findByEmail(email);
        if (existing) {
            throw new Error('Email já cadastrado');
        }
        
        if (password.length < 8) {
            throw new Error('Senha deve ter no mínimo 8 caracteres');
        }
        
        // Criação
        const user = await User.create({ name, email, password });
        
        // Efeito colateral
        await emailService.sendWelcomeEmail(email, name);
        
        return user;
    }
    
    async authenticate(email, password) {
        const user = await User.findByEmail(email);
        
        if (!user) {
            throw new Error('Credenciais inválidas');
        }
        
        const valid = await User.verifyPassword(password, user.password);
        if (!valid) {
            throw new Error('Credenciais inválidas');
        }
        
        return user;
    }
}

module.exports = new UserController();
```

---

### 4. Routes / Views

**Responsabilidade:** Definir endpoints HTTP e delegar para controllers.

**DEVE conter:**
- Definição de rotas/endpoints
- Parsing de request (body, params, query)
- Validação de formato de entrada
- Formatação de resposta HTTP
- Tratamento de erros HTTP

**NÃO DEVE conter:**
- Lógica de negócio
- Acesso direto ao banco
- Queries SQL

**Exemplo Python:**
```python
# routes/user_routes.py
from flask import Blueprint, request, jsonify
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__, url_prefix='/api/users')
controller = UserController()

@user_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validação de formato
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    required = ['name', 'email', 'password']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    try:
        user = controller.create_user(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = controller.get_user(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    try:
        user = controller.authenticate(data['email'], data['password'])
        return jsonify({
            'message': 'Login realizado',
            'user': {'id': user.id, 'name': user.name}
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
```

**Exemplo JavaScript:**
```javascript
// routes/userRoutes.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

router.post('/', async (req, res, next) => {
    const { name, email, password } = req.body;
    
    // Validação de formato
    if (!name || !email || !password) {
        return res.status(400).json({ error: 'Campos obrigatórios faltando' });
    }
    
    try {
        const user = await userController.createUser(name, email, password);
        res.status(201).json({ id: user.id, message: 'Usuário criado' });
    } catch (error) {
        if (error.message.includes('já cadastrado')) {
            return res.status(409).json({ error: error.message });
        }
        next(error);
    }
});

router.get('/:id', async (req, res, next) => {
    try {
        const user = await userController.getUser(req.params.id);
        res.json({ id: user.id, name: user.name, email: user.email });
    } catch (error) {
        res.status(404).json({ error: error.message });
    }
});

router.post('/login', async (req, res, next) => {
    const { email, password } = req.body;
    
    if (!email || !password) {
        return res.status(400).json({ error: 'Email e senha são obrigatórios' });
    }
    
    try {
        const user = await userController.authenticate(email, password);
        res.json({ message: 'Login realizado', userId: user.id });
    } catch (error) {
        res.status(401).json({ error: 'Credenciais inválidas' });
    }
});

module.exports = router;
```

---

### 5. Services (Opcional)

**Responsabilidade:** Encapsular integrações externas e lógica complexa reutilizável.

**DEVE conter:**
- Integrações com APIs externas
- Envio de emails/notificações
- Processamento de pagamentos
- Lógica complexa reutilizável

**Exemplo:**
```python
# services/email_service.py
import smtplib
from config.settings import Config

class EmailService:
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_pass = Config.SMTP_PASS
    
    def send_email(self, to, subject, body):
        # Implementação de envio
        pass
    
    def send_welcome_email(self, email, name):
        subject = "Bem-vindo!"
        body = f"Olá {name}, sua conta foi criada com sucesso."
        self.send_email(email, subject, body)
```

---

### 6. Middlewares

**Responsabilidade:** Processamento transversal de requisições.

**DEVE conter:**
- Autenticação
- Autorização
- Logging de requisições
- Error handling centralizado
- CORS, rate limiting, etc.

**Exemplo Python:**
```python
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requisição inválida'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Não autorizado'}), 401
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Erro interno: {error}')
        return jsonify({'error': 'Erro interno do servidor'}), 500
```

**Exemplo JavaScript:**
```javascript
// middlewares/errorHandler.js
const logger = require('../utils/logger');

function errorHandler(err, req, res, next) {
    logger.error(err.stack);
    
    if (err.name === 'ValidationError') {
        return res.status(400).json({ error: err.message });
    }
    
    if (err.name === 'UnauthorizedError') {
        return res.status(401).json({ error: 'Não autorizado' });
    }
    
    res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
```

---

### 7. Entry Point (app.py / app.js)

**Responsabilidade:** Composição e inicialização da aplicação.

**DEVE conter:**
- Criação da instância da aplicação
- Registro de middlewares
- Registro de rotas
- Inicialização do banco de dados
- Configuração de CORS

**NÃO DEVE conter:**
- Lógica de negócio
- Definição de rotas inline
- Queries ao banco

**Exemplo Python:**
```python
# app.py
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from models.base import init_db
from routes import register_routes
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializa extensões
    CORS(app)
    
    # Inicializa banco (cria tabelas se necessário, via SQL puro)
    init_db()
    
    # Registra rotas
    register_routes(app)
    
    # Registra error handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG)
```

> **Nota:** `init_db()` em `models/base.py` executa os `CREATE TABLE IF NOT EXISTS` via `sqlite3` puro, sem ORM. Mantenha o mesmo schema já existente no projeto original.

**Exemplo JavaScript:**
```javascript
// app.js
const express = require('express');
const cors = require('cors');
const config = require('./config');
const routes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');
const db = require('./models');

const app = express();

// Middlewares
app.use(cors());
app.use(express.json());

// Rotas
app.use('/api', routes);

// Error handler (deve ser o último)
app.use(errorHandler);

// Inicializa DB e servidor
db.initialize().then(() => {
    app.listen(config.port, () => {
        console.log(`Server running on port ${config.port}`);
    });
});

module.exports = app;
```

---

## Regras de Ouro

1. **Cada arquivo tem uma responsabilidade clara**
2. **Controllers não conhecem HTTP (req/res)**
3. **Routes não conhecem banco de dados**
4. **Models não conhecem regras de negócio complexas**
5. **Configurações vêm de variáveis de ambiente**
6. **Dependências são injetadas, não importadas diretamente**
7. **Error handling é centralizado**
8. **Nenhum arquivo deve ter mais de 300 linhas**
9. **Preservar a tecnologia de acesso a dados existente** — se o projeto usa `sqlite3`/SQL puro, os Models devem encapsular queries parametrizadas em SQL puro. **NÃO introduzir um ORM (SQLAlchemy, etc.) que não existia no projeto**; a refatoração organiza o código, não troca a stack de persistência.
