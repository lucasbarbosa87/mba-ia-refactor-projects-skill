// Model Course — acesso à tabela `courses`.

const { dbAsync } = require('../database');

const Course = {
    findActiveById(id) {
        return dbAsync.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    },

    findAll() {
        return dbAsync.all('SELECT * FROM courses', []);
    },
};

module.exports = Course;
