# code-smells-project

API de E-commerce em Python/Flask, refatorada para o padrão MVC pela skill `refactor-arch`.

## Estrutura

```
app.py              # Entry point (composition root: create_app)
config/             # Configuração via variáveis de ambiente
models/             # Acesso a dados (SQL parametrizado): base, product, user, order
controllers/        # Lógica de negócio / orquestração
routes/             # Blueprints Flask (camada HTTP)
services/           # Efeitos colaterais (NotificationService)
middlewares/        # Autenticação admin e error handler centralizado
utils/              # Constantes, exceptions e validators
reports/            # Relatório de auditoria (Fase 2)
```

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # ajuste SECRET_KEY, ADMIN_TOKEN, etc.
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db` por padrão,
configurável via `DATABASE_PATH`) é criado automaticamente no primeiro boot, já com
produtos e usuários de exemplo (senhas gravadas com hash).

## Configuração (variáveis de ambiente)

Ver `.env.example`. Destaques:

- `SECRET_KEY` — segredo do Flask (não é mais hardcoded).
- `ADMIN_TOKEN` — exigido no header `X-Admin-Token` para os endpoints `/admin/*`.
  Sem valor, o acesso administrativo fica desabilitado.
- `DEBUG`, `DATABASE_PATH`, `HOST`, `PORT`, `AMBIENTE`.
