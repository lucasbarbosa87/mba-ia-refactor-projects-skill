// Model Enrollment — acesso à tabela `enrollments`.

const { dbAsync } = require('../database');

const Enrollment = {
    async create(userId, courseId) {
        const result = await dbAsync.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        );
        return { id: result.lastID, userId, courseId };
    },

    async findIdsByUserId(userId) {
        const rows = await dbAsync.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
        return rows.map((row) => row.id);
    },

    deleteByUserId(userId) {
        return dbAsync.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    },
};

module.exports = Enrollment;
