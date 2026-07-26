// Controller do relatório financeiro — monta a estrutura a partir das linhas
// carregadas em uma única query (sem N+1).

const FinancialReport = require('../models/FinancialReport');
const { PaymentStatus } = require('../constants');

async function generateFinancialReport() {
    const rows = await FinancialReport.fetchRows();

    // Preserva a ordem dos cursos e o formato de saída original.
    const byCourse = new Map();

    for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, {
                course: row.course_title,
                revenue: 0,
                students: [],
            });
        }
        const courseData = byCourse.get(row.course_id);

        // Linhas sem enrollment (LEFT JOIN) representam curso sem matrículas.
        if (row.enrollment_id == null) continue;

        if (row.payment_status === PaymentStatus.PAID) {
            courseData.revenue += row.payment_amount;
        }

        courseData.students.push({
            student: row.student_name || 'Unknown',
            paid: row.payment_amount != null ? row.payment_amount : 0,
        });
    }

    return Array.from(byCourse.values());
}

module.exports = { generateFinancialReport };
