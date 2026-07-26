// Model AuditLog — acesso à tabela `audit_logs`.

const { dbAsync } = require('../database');

const AuditLog = {
    record(action) {
        return dbAsync.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action],
        );
    },
};

module.exports = AuditLog;
