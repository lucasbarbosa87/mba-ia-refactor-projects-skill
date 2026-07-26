# Heurísticas de Análise de Projeto

Este documento define as heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura na Fase 1.

---

## 1. Detecção de Linguagem

### Por arquivo de configuração

| Arquivo | Linguagem |
|---------|-----------|
| `package.json` | JavaScript/TypeScript (Node.js) |
| `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile` | Python |
| `pom.xml`, `build.gradle` | Java |
| `Gemfile` | Ruby |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `composer.json` | PHP |
| `*.csproj`, `*.sln` | C# (.NET) |

### Por extensão de arquivos

| Extensão | Linguagem |
|----------|-----------|
| `.py` | Python |
| `.js` | JavaScript |
| `.ts` | TypeScript |
| `.java` | Java |
| `.rb` | Ruby |
| `.go` | Go |
| `.rs` | Rust |
| `.php` | PHP |
| `.cs` | C# |

---

## 2. Detecção de Framework

### Python

| Sinal | Framework |
|-------|-----------|
| `from flask import` ou `Flask(__name__)` | Flask |
| `from django` ou `INSTALLED_APPS` | Django |
| `from fastapi import` ou `FastAPI()` | FastAPI |
| `from bottle import` | Bottle |
| `from tornado` | Tornado |

**Versão:** Verificar em `requirements.txt` ou `setup.py`

### JavaScript/Node.js

| Sinal | Framework |
|-------|-----------|
| `require('express')` ou `from 'express'` | Express |
| `require('koa')` ou `from 'koa'` | Koa |
| `require('fastify')` ou `from 'fastify'` | Fastify |
| `require('hapi')` ou `from '@hapi/hapi'` | Hapi |
| `require('nest')` ou `from '@nestjs'` | NestJS |

**Versão:** Verificar em `package.json` na seção `dependencies`

### Java

| Sinal | Framework |
|-------|-----------|
| `@SpringBootApplication` ou `spring-boot` em pom.xml | Spring Boot |
| `javax.ws.rs` ou JAX-RS annotations | JAX-RS |
| `io.dropwizard` | Dropwizard |
| `io.micronaut` | Micronaut |
| `io.quarkus` | Quarkus |

### Ruby

| Sinal | Framework |
|-------|-----------|
| `Rails.application` ou `gem 'rails'` | Ruby on Rails |
| `Sinatra::Base` ou `gem 'sinatra'` | Sinatra |
| `Hanami` | Hanami |

---

## 3. Detecção de Banco de Dados

### Por dependências

| Dependência | Banco de Dados |
|-------------|----------------|
| `sqlite3`, `sqlite` | SQLite |
| `psycopg2`, `pg`, `postgres` | PostgreSQL |
| `mysql`, `mysql2`, `pymysql` | MySQL |
| `mongodb`, `mongoose`, `pymongo` | MongoDB |
| `redis`, `ioredis` | Redis |
| `sqlalchemy` | ORM (verificar driver) |
| `sequelize`, `typeorm`, `prisma` | ORM (verificar config) |

### Por código

| Padrão | Banco de Dados |
|--------|----------------|
| `sqlite3.connect` ou `new sqlite3.Database` | SQLite |
| `:memory:` em conexão | SQLite in-memory |
| `mongodb://` ou `MongoClient` | MongoDB |
| `postgres://` ou `pg.connect` | PostgreSQL |
| `mysql://` ou `mysql.createConnection` | MySQL |

### Por arquivos

| Arquivo | Banco de Dados |
|---------|----------------|
| `*.db`, `*.sqlite`, `*.sqlite3` | SQLite |
| `docker-compose.yml` com `postgres` | PostgreSQL |
| `docker-compose.yml` com `mysql` | MySQL |
| `docker-compose.yml` com `mongo` | MongoDB |

---

## 4. Mapeamento de Arquitetura

### Padrões de estrutura

#### Monolítico (sem organização)
```
projeto/
├── app.py (ou index.js)
├── database.py
└── ... (poucos arquivos na raiz)
```
**Sinais:**
- Menos de 10 arquivos de código
- Tudo na raiz do projeto
- Um arquivo contém múltiplas responsabilidades

#### Parcialmente organizado
```
projeto/
├── app.py
├── models/
├── routes/ (ou views/)
└── utils/ (ou helpers/)
```
**Sinais:**
- Alguma separação em pastas
- Mas sem controllers ou services
- Lógica de negócio misturada nas routes

#### MVC completo
```
projeto/
├── app.py (entry point)
├── config/
├── models/
├── views/ (ou routes/)
├── controllers/
└── services/ (opcional)
```
**Sinais:**
- Separação clara de responsabilidades
- Controllers separados de routes
- Configuração externalizada

### Identificação de problemas arquiteturais

| Sinal | Problema |
|-------|----------|
| Arquivo com 500+ linhas | God Class / God File |
| Rotas definidas junto com lógica de negócio | Falta de separação |
| Queries SQL nas rotas | Falta de camada de dados |
| Configurações hardcoded | Falta de módulo de config |
| Imports circulares | Acoplamento excessivo |

---

## 5. Identificação de Domínio

### Por nomes de entidades/tabelas

| Termos | Domínio Provável |
|--------|------------------|
| `product`, `cart`, `order`, `payment` | E-commerce |
| `user`, `task`, `project`, `sprint` | Gerenciamento de Projetos |
| `course`, `student`, `enrollment`, `lesson` | LMS (Educação) |
| `patient`, `appointment`, `doctor` | Healthcare |
| `post`, `comment`, `like`, `follow` | Rede Social |
| `account`, `transaction`, `balance` | Financeiro |
| `ticket`, `issue`, `priority` | Helpdesk/Support |

### Por rotas/endpoints

Analisar prefixos de rotas:
- `/api/products`, `/api/orders` → E-commerce
- `/api/tasks`, `/api/projects` → Task Manager
- `/api/courses`, `/api/enrollments` → LMS
- `/api/users`, `/api/auth` → Sistema de autenticação (comum a vários)

---

## 6. Contagem de Métricas

### Arquivos a analisar

**Incluir:**
- Arquivos de código-fonte (`.py`, `.js`, `.ts`, `.java`, etc.)
- Arquivos de configuração relevantes
- Templates (se aplicável)

**Excluir:**
- `node_modules/`, `venv/`, `__pycache__/`
- Arquivos de build/dist
- Arquivos de teste (para contagem principal)
- Assets estáticos

### Métricas a reportar

1. **Total de arquivos de código**
2. **Linhas de código aproximadas**
3. **Número de rotas/endpoints**
4. **Número de tabelas/models**
5. **Número de dependências principais**
