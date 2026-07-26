// Model FinancialReport — encapsula a consulta agregada do relatório financeiro.
// Substitui o padrão N+1 (uma query por curso, por matrícula e por pagamento)
// por um único LEFT JOIN carregando tudo de uma vez.

const { dbAsync } = require('../database');

const FinancialReport = {
    fetchRows() {
        return dbAsync.all(
            `SELECT c.id           AS course_id,
                    c.title        AS course_title,
                    e.id           AS enrollment_id,
                    u.name         AS student_name,
                    p.amount       AS payment_amount,
                    p.status       AS payment_status
             FROM courses c
             LEFT JOIN enrollments e ON e.course_id = c.id
             LEFT JOIN users u       ON u.id = e.user_id
             LEFT JOIN payments p    ON p.enrollment_id = e.id
             ORDER BY c.id, e.id`,
            [],
        );
    },
};

module.exports = FinancialReport;
