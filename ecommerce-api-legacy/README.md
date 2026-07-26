# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada para o padrão MVC pela skill `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`. Variáveis de ambiente em `.env.example`.

## Arquitetura (MVC)

```
src/
├── app.js               # Entry point / composition root
├── config/              # Configuração via variáveis de ambiente
├── constants/           # Enums e constantes de domínio
├── database/            # Conexão SQLite + helpers async + schema/seed
├── models/              # Acesso a dados (queries parametrizadas)
├── services/            # Pagamento e hashing de senha (scrypt)
├── controllers/         # Regra de negócio (sem HTTP)
├── routes/              # Endpoints HTTP e validação de formato
├── middlewares/         # Autenticação e error handler centralizado
└── utils/               # Validadores e AppError
```

## Autenticação

As rotas administrativas (`GET /api/admin/financial-report` e `DELETE /api/users/:id`)
exigem o header `x-admin-token` com o valor de `ADMIN_TOKEN` (padrão de dev: `dev-admin-token`).
