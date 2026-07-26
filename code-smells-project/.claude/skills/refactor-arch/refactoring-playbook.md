# Playbook de Refatoração

Este documento define padrões concretos de transformação para cada anti-pattern, com exemplos de código antes/depois.

---

## 1. SQL Injection → Queries Parametrizadas

### Antes (Vulnerável)

**Python:**
```python
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
    return cursor.fetchone()

def search_products(name):
    query = f"SELECT * FROM products WHERE name LIKE '%{name}%'"
    cursor.execute(query)
    return cursor.fetchall()
```

**JavaScript:**
```javascript
function getUser(userId) {
    return db.query("SELECT * FROM users WHERE id = " + userId);
}

function searchProducts(name) {
    return db.query(`SELECT * FROM products WHERE name LIKE '%${name}%'`);
}
```

### Depois (Seguro)

**Python:**
```python
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])
    return cursor.fetchone()

def search_products(name):
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", [f'%{name}%'])
    return cursor.fetchall()
```

**JavaScript:**
```javascript
function getUser(userId) {
    return db.query("SELECT * FROM users WHERE id = ?", [userId]);
}

function searchProducts(name) {
    return db.query("SELECT * FROM products WHERE name LIKE ?", [`%${name}%`]);
}
```

---

## 2. Hardcoded Credentials → Variáveis de Ambiente

### Antes (Vulnerável)

**Python:**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
app.config['DATABASE_URI'] = 'postgresql://admin:senha123@localhost/db'
API_KEY = 'sk_live_1234567890'
```

**JavaScript:**
```javascript
const config = {
    secretKey: 'my-secret-key-123',
    dbPassword: 'senha_super_secreta',
    paymentKey: 'pk_live_abcdef'
};
```


### Depois (Seguro)

**Python:**
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URI = os.environ.get('DATABASE_URI')
    API_KEY = os.environ.get('API_KEY')
    
    @classmethod
    def validate(cls):
        required = ['SECRET_KEY', 'DATABASE_URI']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f'Missing env vars: {missing}')
```

**JavaScript:**
```javascript
// config/index.js
require('dotenv').config();

const config = {
    secretKey: process.env.SECRET_KEY,
    dbPassword: process.env.DB_PASSWORD,
    paymentKey: process.env.PAYMENT_KEY,
    
    validate() {
        const required = ['SECRET_KEY', 'DB_PASSWORD'];
        const missing = required.filter(key => !process.env[key]);
        if (missing.length) {
            throw new Error(`Missing env vars: ${missing.join(', ')}`);
        }
    }
};

config.validate();
module.exports = config;
```

**Criar arquivo .env.example:**
```
SECRET_KEY=your-secret-key-here
DATABASE_URI=postgresql://user:pass@localhost/db
API_KEY=your-api-key-here
```

---

## 3. Insecure Password Storage → Hash Seguro

### Antes (Vulnerável)

**Python:**
```python
# Texto plano
user.password = senha

# MD5 (quebrado)
import hashlib
user.password = hashlib.md5(senha.encode()).hexdigest()
```

**JavaScript:**
```javascript
// Base64 (não é hash!)
user.pass = Buffer.from(password).toString('base64');

// Comparação direta
if (user.password === inputPassword) { }
```


### Depois (Seguro)

**Python (com werkzeug):**
```python
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**Python (com bcrypt):**
```python
import bcrypt

class User:
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
```

**JavaScript:**
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 10;

class User {
    async setPassword(password) {
        this.passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
    }
    
    async checkPassword(password) {
        return bcrypt.compare(password, this.passwordHash);
    }
}
```

---

## 4. N+1 Queries → JOINs / Eager Loading

### Antes (N+1)

**Python:**
```python
def get_orders_with_items():
    orders = db.execute("SELECT * FROM orders").fetchall()
    result = []
    for order in orders:
        # Query para cada pedido!
        items = db.execute(
            f"SELECT * FROM items WHERE order_id = {order['id']}"
        ).fetchall()
        order['items'] = items
        result.append(order)
    return result
```

**JavaScript:**
```javascript
async function getOrdersWithItems() {
    const orders = await db.query("SELECT * FROM orders");
    for (const order of orders) {
        // Query para cada pedido!
        order.items = await db.query(
            "SELECT * FROM items WHERE order_id = ?", [order.id]
        );
    }
    return orders;
}
```


### Depois (Otimizado)

**Python (com JOIN):**
```python
def get_orders_with_items():
    query = """
        SELECT o.*, i.id as item_id, i.product_id, i.quantity, i.price
        FROM orders o
        LEFT JOIN items i ON o.id = i.order_id
        ORDER BY o.id
    """
    rows = db.execute(query).fetchall()
    
    # Agrupa por pedido
    orders = {}
    for row in rows:
        order_id = row['id']
        if order_id not in orders:
            orders[order_id] = {
                'id': row['id'],
                'status': row['status'],
                'items': []
            }
        if row['item_id']:
            orders[order_id]['items'].append({
                'id': row['item_id'],
                'product_id': row['product_id'],
                'quantity': row['quantity']
            })
    
    return list(orders.values())
```

**Python (com batch query — evita loop):**
```python
def get_orders_with_items():
    orders = db.execute("SELECT * FROM orders").fetchall()
    order_ids = [o['id'] for o in orders]
    if not order_ids:
        return []

    # Uma única query para TODOS os itens dos pedidos
    placeholders = ','.join('?' * len(order_ids))
    items = db.execute(
        f"SELECT * FROM items WHERE order_id IN ({placeholders})",
        order_ids
    ).fetchall()

    # Agrupa itens por pedido em memória
    items_by_order = {}
    for item in items:
        items_by_order.setdefault(item['order_id'], []).append(dict(item))

    return [
        {**dict(order), 'items': items_by_order.get(order['id'], [])}
        for order in orders
    ]
```

**JavaScript (com JOIN):**
```javascript
async function getOrdersWithItems() {
    const query = `
        SELECT o.*, i.id as item_id, i.product_id, i.quantity
        FROM orders o
        LEFT JOIN items i ON o.id = i.order_id
        ORDER BY o.id
    `;
    const rows = await db.query(query);
    
    // Agrupa por pedido
    const ordersMap = new Map();
    for (const row of rows) {
        if (!ordersMap.has(row.id)) {
            ordersMap.set(row.id, { ...row, items: [] });
        }
        if (row.item_id) {
            ordersMap.get(row.id).items.push({
                id: row.item_id,
                product_id: row.product_id,
                quantity: row.quantity
            });
        }
    }
    
    return Array.from(ordersMap.values());
}
```

---

## 5. God Class → Separação de Responsabilidades

### Antes (God Class)

```javascript
// AppManager.js - FAZ TUDO
class AppManager {
    constructor() {
        this.db = new Database();
    }
    
    initDb() { /* cria tabelas */ }
    
    setupRoutes(app) {
        app.post('/checkout', (req, res) => {
            // Validação
            // Criação de usuário
            // Processamento de pagamento
            // Criação de matrícula
            // Envio de email
            // Log de auditoria
        });
        
        app.get('/report', (req, res) => { /* ... */ });
        app.delete('/users/:id', (req, res) => { /* ... */ });
    }
}
```


### Depois (Separado)

```javascript
// models/User.js
class User {
    static async findByEmail(email) { /* ... */ }
    static async create(data) { /* ... */ }
}

// models/Enrollment.js
class Enrollment {
    static async create(userId, courseId) { /* ... */ }
}

// controllers/checkoutController.js
const User = require('../models/User');
const Enrollment = require('../models/Enrollment');
const paymentService = require('../services/paymentService');
const emailService = require('../services/emailService');

class CheckoutController {
    async processCheckout(userData, courseId, paymentData) {
        // 1. Busca ou cria usuário
        let user = await User.findByEmail(userData.email);
        if (!user) {
            user = await User.create(userData);
        }
        
        // 2. Processa pagamento
        const payment = await paymentService.charge(paymentData);
        if (!payment.success) {
            throw new Error('Pagamento recusado');
        }
        
        // 3. Cria matrícula
        const enrollment = await Enrollment.create(user.id, courseId);
        
        // 4. Notifica usuário
        await emailService.sendWelcome(user.email);
        
        return { enrollment, payment };
    }
}

// routes/checkoutRoutes.js
const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

router.post('/', async (req, res, next) => {
    try {
        const result = await checkoutController.processCheckout(
            req.body.user,
            req.body.courseId,
            req.body.payment
        );
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// services/paymentService.js
class PaymentService {
    async charge(paymentData) { /* ... */ }
}

// services/emailService.js
class EmailService {
    async sendWelcome(email) { /* ... */ }
}
```

---

## 6. Callback Hell → Async/Await

### Antes (Callback Hell)

```javascript
app.post('/checkout', (req, res) => {
    db.get("SELECT * FROM courses WHERE id = ?", [req.body.courseId], (err, course) => {
        if (err) return res.status(500).send("Erro");
        db.get("SELECT * FROM users WHERE email = ?", [req.body.email], (err, user) => {
            if (err) return res.status(500).send("Erro");
            if (!user) {
                db.run("INSERT INTO users ...", [], function(err) {
                    if (err) return res.status(500).send("Erro");
                    db.run("INSERT INTO enrollments ...", [], function(err) {
                        if (err) return res.status(500).send("Erro");
                        db.run("INSERT INTO payments ...", [], function(err) {
                            if (err) return res.status(500).send("Erro");
                            res.json({ success: true });
                        });
                    });
                });
            }
        });
    });
});
```


### Depois (Async/Await)

```javascript
// Promisify das operações de DB
const dbAsync = {
    get: (sql, params) => new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
    }),
    run: (sql, params) => new Promise((resolve, reject) => {
        db.run(sql, params, function(err) {
            err ? reject(err) : resolve({ lastID: this.lastID });
        });
    })
};

// Controller com async/await
async function processCheckout(courseId, email, userData) {
    const course = await dbAsync.get(
        "SELECT * FROM courses WHERE id = ?", [courseId]
    );
    if (!course) throw new Error('Curso não encontrado');
    
    let user = await dbAsync.get(
        "SELECT * FROM users WHERE email = ?", [email]
    );
    
    if (!user) {
        const result = await dbAsync.run(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [userData.name, email]
        );
        user = { id: result.lastID };
    }
    
    const enrollment = await dbAsync.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [user.id, courseId]
    );
    
    await dbAsync.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollment.lastID, course.price, 'PAID']
    );
    
    return { enrollmentId: enrollment.lastID };
}

// Rota limpa
router.post('/checkout', async (req, res, next) => {
    try {
        const result = await processCheckout(
            req.body.courseId,
            req.body.email,
            req.body.user
        );
        res.json(result);
    } catch (error) {
        next(error);
    }
});
```

---

## 7. Business Logic in Routes → Controller Layer

### Antes (Lógica nas Rotas)

```python
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    conn = get_connection()

    # Validação de negócio na rota
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", [data['user_id']]
    ).fetchone()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    total = 0
    for item in data['items']:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", [item['product_id']]
        ).fetchone()
        if product['stock'] < item['quantity']:
            return jsonify({'error': f'Estoque insuficiente para {product["name"]}'}), 400
        total += product['price'] * item['quantity']

    # Aplicação de desconto na rota
    if total > 1000:
        total *= 0.9  # 10% desconto

    # Criação do pedido
    cursor = conn.execute(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)",
        [user['id'], total]
    )
    order_id = cursor.lastrowid

    for item in data['items']:
        # Atualização de estoque na rota
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            [item['quantity'], item['product_id']]
        )
        # ...

    # Notificação na rota
    print(f"EMAIL: Pedido {order_id} criado")
    print(f"SMS: Seu pedido foi recebido")

    conn.commit()
    return jsonify({'order_id': order_id}), 201
```


### Depois (Com Controller)

```python
# controllers/order_controller.py
from models.order import Order
from models.product import Product
from models.user import User
from services.notification_service import NotificationService

class OrderController:
    def __init__(self):
        self.notification_service = NotificationService()
    
    def create_order(self, user_id, items):
        # Validação de usuário
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError('Usuário não encontrado')
        
        # Validação de estoque
        self._validate_stock(items)
        
        # Cálculo de total com desconto
        total = self._calculate_total(items)
        
        # Criação do pedido
        order = Order.create(user_id=user_id, total=total)
        
        # Adiciona itens e atualiza estoque
        for item in items:
            order.add_item(item['product_id'], item['quantity'])
            Product.decrease_stock(item['product_id'], item['quantity'])
        
        order.save()
        
        # Notificações
        self.notification_service.notify_order_created(user, order)
        
        return order
    
    def _validate_stock(self, items):
        for item in items:
            product = Product.find_by_id(item['product_id'])
            if not product:
                raise ValueError(f'Produto {item["product_id"]} não encontrado')
            if product.stock < item['quantity']:
                raise ValueError(f'Estoque insuficiente para {product.name}')
    
    def _calculate_total(self, items):
        total = sum(
            Product.find_by_id(item['product_id']).price * item['quantity']
            for item in items
        )
        # Regra de desconto
        if total > 1000:
            total *= 0.9
        return total

# routes/order_routes.py
from flask import Blueprint, request, jsonify
from controllers.order_controller import OrderController

order_bp = Blueprint('orders', __name__)
controller = OrderController()

@order_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'items' not in data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    try:
        order = controller.create_order(data['user_id'], data['items'])
        return jsonify({'order_id': order.id, 'total': order.total}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

---

## 8. Missing Error Handler → Centralizado

### Antes (Tratamento Espalhado)

```python
@app.route('/users/<int:id>')
def get_user(id):
    try:
        user = User.find_by_id(id)
        if not user:
            return jsonify({'error': 'Não encontrado'}), 404
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:id>')
def get_product(id):
    try:
        product = Product.find_by_id(id)
        if not product:
            return jsonify({'error': 'Não encontrado'}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```


### Depois (Centralizado)

```python
# exceptions.py
class AppException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, resource):
        super().__init__(f'{resource} não encontrado', 404)

class ValidationError(AppException):
    def __init__(self, message):
        super().__init__(message, 400)

# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        return jsonify({'error': error.message}), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.exception('Erro interno')
        return jsonify({'error': 'Erro interno do servidor'}), 500

# routes/user_routes.py - Rotas limpas
from exceptions import NotFoundError

@user_bp.route('/<int:id>')
def get_user(id):
    user = User.find_by_id(id)
    if not user:
        raise NotFoundError('Usuário')
    return jsonify(user.to_dict())

@product_bp.route('/<int:id>')
def get_product(id):
    product = Product.find_by_id(id)
    if not product:
        raise NotFoundError('Produto')
    return jsonify(product.to_dict())
```

**JavaScript:**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(err.stack);
    
    if (err.name === 'NotFoundError') {
        return res.status(404).json({ error: err.message });
    }
    
    if (err.name === 'ValidationError') {
        return res.status(400).json({ error: err.message });
    }
    
    res.status(500).json({ error: 'Erro interno do servidor' });
}

// app.js - Registrar no final
app.use(errorHandler);
```

---

## 9. Code Duplication → Funções Reutilizáveis

### Antes (Duplicado)

```python
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    if 'name' not in data:
        return jsonify({'error': 'Nome obrigatório'}), 400
    if len(data['name']) < 3:
        return jsonify({'error': 'Nome muito curto'}), 400
    if 'price' not in data:
        return jsonify({'error': 'Preço obrigatório'}), 400
    if data['price'] < 0:
        return jsonify({'error': 'Preço inválido'}), 400
    # ... criar produto

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    if 'name' not in data:
        return jsonify({'error': 'Nome obrigatório'}), 400
    if len(data['name']) < 3:
        return jsonify({'error': 'Nome muito curto'}), 400
    if 'price' not in data:
        return jsonify({'error': 'Preço obrigatório'}), 400
    if data['price'] < 0:
        return jsonify({'error': 'Preço inválido'}), 400
    # ... atualizar produto
```


### Depois (Reutilizável)

```python
# validators/product_validator.py
from exceptions import ValidationError

def validate_product_data(data, required_fields=None):
    if not data:
        raise ValidationError('Dados inválidos')
    
    if required_fields is None:
        required_fields = ['name', 'price']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'{field} é obrigatório')
    
    if 'name' in data:
        if len(data['name']) < 3:
            raise ValidationError('Nome muito curto')
        if len(data['name']) > 200:
            raise ValidationError('Nome muito longo')
    
    if 'price' in data:
        if not isinstance(data['price'], (int, float)) or data['price'] < 0:
            raise ValidationError('Preço inválido')
    
    return data

# routes/product_routes.py
from validators.product_validator import validate_product_data

@product_bp.route('', methods=['POST'])
def create_product():
    data = validate_product_data(request.get_json())
    product = controller.create(data)
    return jsonify(product.to_dict()), 201

@product_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    data = validate_product_data(request.get_json(), required_fields=[])
    product = controller.update(id, data)
    return jsonify(product.to_dict())
```

---

## 10. Magic Strings → Constantes/Enums

### Antes (Magic Strings)

```python
if order.status == "pending":
    # ...
elif order.status == "approved":
    # ...
elif order.status == "shipped":
    # ...

if user.role == "admin":
    # ...
```

### Depois (Constantes/Enum)

```python
# constants.py
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"

# Uso
if order.status == OrderStatus.PENDING:
    # ...
elif order.status == OrderStatus.APPROVED:
    # ...

if user.role == UserRole.ADMIN:
    # ...

# Validação
def validate_status(status):
    try:
        return OrderStatus(status)
    except ValueError:
        raise ValidationError(f'Status inválido. Válidos: {[s.value for s in OrderStatus]}')
```

**JavaScript:**
```javascript
// constants/index.js
const OrderStatus = Object.freeze({
    PENDING: 'pending',
    APPROVED: 'approved',
    SHIPPED: 'shipped',
    DELIVERED: 'delivered',
    CANCELLED: 'cancelled'
});

const UserRole = Object.freeze({
    USER: 'user',
    ADMIN: 'admin',
    MANAGER: 'manager'
});

// Uso
if (order.status === OrderStatus.PENDING) { }

// Validação
function isValidStatus(status) {
    return Object.values(OrderStatus).includes(status);
}
```

---

## Resumo das Transformações

| # | Anti-Pattern | Transformação |
|---|--------------|---------------|
| 1 | SQL Injection | Queries parametrizadas |
| 2 | Hardcoded Credentials | Variáveis de ambiente |
| 3 | Insecure Password | bcrypt/Argon2 |
| 4 | N+1 Queries | JOINs / Eager loading |
| 5 | God Class | Separação em camadas |
| 6 | Callback Hell | Async/Await |
| 7 | Logic in Routes | Controller layer |
| 8 | Scattered Error Handling | Centralizado |
| 9 | Code Duplication | Funções reutilizáveis |
| 10 | Magic Strings | Constantes/Enums |
