// Rotas de usuários — exclusão protegida por autenticação (operação destrutiva).

const express = require('express');
const userController = require('../controllers/userController');
const requireAdmin = require('../middlewares/auth');

const router = express.Router();

router.delete('/users/:id', requireAdmin, async (req, res, next) => {
    try {
        const result = await userController.deleteUser(req.params.id);
        return res.json({
            message: 'Usuário e registros relacionados removidos com sucesso',
            ...result,
        });
    } catch (error) {
        return next(error);
    }
});

module.exports = router;
