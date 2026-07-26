// Rotas administrativas de relatório — protegidas por autenticação.

const express = require('express');
const reportController = require('../controllers/reportController');
const requireAdmin = require('../middlewares/auth');

const router = express.Router();

router.get('/admin/financial-report', requireAdmin, async (req, res, next) => {
    try {
        const report = await reportController.generateFinancialReport();
        return res.json(report);
    } catch (error) {
        return next(error);
    }
});

module.exports = router;
