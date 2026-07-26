// Rotas de checkout — parsing/validação de formato e formatação da resposta.
// Preserva o contrato original: body { usr, eml, pwd, c_id, card } e
// resposta de sucesso { msg: "Sucesso", enrollment_id }.

const express = require('express');
const checkoutController = require('../controllers/checkoutController');
const { isValidEmail, isValidCard, isNonEmptyString } = require('../utils/validators');

const router = express.Router();

router.post('/checkout', async (req, res, next) => {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;

    // Validação de formato de entrada.
    if (!isNonEmptyString(name) || !isValidEmail(email) || !courseId || !isValidCard(card)) {
        return res.status(400).send('Bad Request');
    }

    try {
        const { enrollmentId } = await checkoutController.processCheckout({
            name,
            email,
            password,
            courseId,
            card,
        });
        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    } catch (error) {
        return next(error);
    }
});

module.exports = router;
