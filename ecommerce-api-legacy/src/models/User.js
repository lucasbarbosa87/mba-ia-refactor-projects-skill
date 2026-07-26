// Model User — encapsula acesso à tabela `users` com queries parametrizadas.

const { dbAsync } = require('../database');

const User = {
    findByEmail(email) {
        return dbAsync.get('SELECT * FROM users WHERE email = ?', [email]);
    },

    findById(id) {
        return dbAsync.get('SELECT * FROM users WHERE id = ?', [id]);
    },

    async create({ name, email, passwordHash }) {
        const result = await dbAsync.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
        );
        return { id: result.lastID, name, email };
    },

    deleteById(id) {
        return dbAsync.run('DELETE FROM users WHERE id = ?', [id]);
    },
};

module.exports = User;
