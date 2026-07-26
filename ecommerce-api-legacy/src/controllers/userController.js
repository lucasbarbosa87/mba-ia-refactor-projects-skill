// Controller de usuários — regra de negócio de exclusão.
// Corrige o bug legado que deixava matrículas e pagamentos órfãos:
// remove os registros relacionados antes de excluir o usuário.

const User = require('../models/User');
const Enrollment = require('../models/Enrollment');
const Payment = require('../models/Payment');
const AppError = require('../utils/AppError');

async function deleteUser(id) {
    const user = await User.findById(id);
    if (!user) {
        throw new AppError('Usuário não encontrado', 404);
    }

    const enrollmentIds = await Enrollment.findIdsByUserId(id);
    await Payment.deleteByEnrollmentIds(enrollmentIds);
    await Enrollment.deleteByUserId(id);
    await User.deleteById(id);

    return { deletedUserId: Number(id), removedEnrollments: enrollmentIds.length };
}

module.exports = { deleteUser };
