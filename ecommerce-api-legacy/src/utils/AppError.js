// Erro de aplicação com status HTTP, consumido pelo error handler centralizado.
// Permite que controllers sinalizem falhas de negócio sem conhecer req/res.

class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.name = 'AppError';
        this.statusCode = statusCode;
    }
}

module.exports = AppError;
