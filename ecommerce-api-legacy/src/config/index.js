// Configuração centralizada da aplicação.
// Todas as credenciais e secrets vêm de variáveis de ambiente (ver .env.example).
// Fallbacks aqui são apenas valores de desenvolvimento NÃO sensíveis.

const config = {
    port: parseInt(process.env.PORT, 10) || 3000,
    env: process.env.NODE_ENV || 'development',

    // Secrets — SEM valores hardcoded. Devem vir do ambiente em produção.
    dbUser: process.env.DB_USER,
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,

    // Token usado pelo middleware de autenticação das rotas administrativas.
    // Em dev cai num valor previsível para permitir testes locais.
    adminToken: process.env.ADMIN_TOKEN || 'dev-admin-token',
};

// Em produção, exige que os secrets sensíveis estejam definidos.
if (config.env === 'production') {
    const required = ['PAYMENT_GATEWAY_KEY', 'ADMIN_TOKEN'];
    const missing = required.filter((key) => !process.env[key]);
    if (missing.length) {
        throw new Error(`Variáveis de ambiente obrigatórias ausentes: ${missing.join(', ')}`);
    }
}

module.exports = config;
