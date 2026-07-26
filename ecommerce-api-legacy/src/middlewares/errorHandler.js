// Error handler centralizado — registrado por último no app.
// Traduz AppError em status HTTP e evita vazar detalhes internos ao cliente.

function errorHandler(err, req, res, _next) {
    if (err && err.name === 'AppError') {
        return res.status(err.statusCode).json({ error: err.message });
    }

    console.error('[error]', err && err.stack ? err.stack : err);
    return res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
