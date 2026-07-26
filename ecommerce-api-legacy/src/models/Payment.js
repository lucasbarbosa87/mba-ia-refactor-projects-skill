// Model Payment — acesso à tabela `payments`.

const { dbAsync } = require('../database');

const Payment = {
    async create(enrollmentId, amount, status) {
        const result = await dbAsync.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status],
        );
        return { id: result.lastID, enrollmentId, amount, status };
    },

    deleteByEnrollmentIds(enrollmentIds) {
        if (!enrollmentIds.length) return Promise.resolve({ changes: 0 });
        const placeholders = enrollmentIds.map(() => '?').join(',');
        return dbAsync.run(
            `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
            enrollmentIds,
        );
    },
};

module.exports = Payment;
