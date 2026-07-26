// Controller de checkout — orquestra a regra de negócio do fluxo de compra.
// Não conhece HTTP (req/res); recebe dados já parseados e devolve/《lança》resultado.

const User = require('../models/User');
const Course = require('../models/Course');
const Enrollment = require('../models/Enrollment');
const Payment = require('../models/Payment');
const AuditLog = require('../models/AuditLog');
const passwordService = require('../services/passwordService');
const paymentService = require('../services/paymentService');
const AppError = require('../utils/AppError');

async function processCheckout({ name, email, password, courseId, card }) {
    const course = await Course.findActiveById(courseId);
    if (!course) {
        throw new AppError('Curso não encontrado', 404);
    }

    // Busca ou cria o usuário.
    let user = await User.findByEmail(email);
    if (!user) {
        const passwordHash = passwordService.hash(password || '123456');
        user = await User.create({ name, email, passwordHash });
    }

    // Processa o pagamento via serviço dedicado.
    const payment = paymentService.charge(card, course.price);
    if (!payment.success) {
        throw new AppError('Pagamento recusado', 400);
    }

    // Persiste matrícula, pagamento e auditoria.
    const enrollment = await Enrollment.create(user.id, courseId);
    await Payment.create(enrollment.id, course.price, payment.status);
    await AuditLog.record(`Checkout curso ${courseId} por ${user.id}`);

    return { enrollmentId: enrollment.id };
}

module.exports = { processCheckout };
