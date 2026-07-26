// Entry point / composition root.
// Apenas compõe a aplicação: middlewares, rotas, DB e error handler.

const express = require('express');
const config = require('./config');
const routes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');
const database = require('./database');
const passwordService = require('./services/passwordService');

const app = express();

app.use(express.json());
app.use('/api', routes);
app.use(errorHandler); // deve ser o último

async function start() {
    await database.initialize(passwordService);
    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    console.error('[fatal] Falha ao iniciar a aplicação:', err);
    process.exit(1);
});

module.exports = app;
