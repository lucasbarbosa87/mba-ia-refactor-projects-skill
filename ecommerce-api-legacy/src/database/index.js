// Camada de acesso ao banco (SQLite in-memory, mesma stack do projeto original).
// Expõe helpers promisificados (get/all/run) para permitir async/await nos models,
// eliminando o callback hell da versão legada.

const sqlite3 = require('sqlite3').verbose();
const { PaymentStatus } = require('../constants');

const db = new sqlite3.Database(':memory:');

const dbAsync = {
    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    },
    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    },
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            db.run(sql, params, function callback(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    },
    exec(sql) {
        return new Promise((resolve, reject) => {
            db.exec(sql, (err) => (err ? reject(err) : resolve()));
        });
    },
};

// Cria o schema (idêntico ao original) e carrega os seeds.
// Recebe o passwordService para hashear a senha do usuário semente.
async function initialize(passwordService) {
    await dbAsync.exec(`
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
        CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
        CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
        CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
    `);

    const seedPass = passwordService.hash('123');
    await dbAsync.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan',
        'leonan@fullcycle.com.br',
        seedPass,
    ]);
    await dbAsync.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
        ['Clean Architecture', 997.0, 1, 'Docker', 497.0, 1],
    );
    await dbAsync.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await dbAsync.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [
        1,
        997.0,
        PaymentStatus.PAID,
    ]);
}

module.exports = { db, dbAsync, initialize };
