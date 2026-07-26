// Middleware de autenticação para rotas administrativas.
// Fecha a falha de "Missing Authentication": exige o header `x-admin-token`
// batendo com o token configurado (config.adminToken / env ADMIN_TOKEN).

const config = require('../config');

function requireAdmin(req, res, next) {
    const token = req.headers['x-admin-token'];
    if (!token || token !== config.adminToken) {
        return res.status(401).json({ error: 'Não autorizado' });
    }
    return next();
}

module.exports = requireAdmin;
