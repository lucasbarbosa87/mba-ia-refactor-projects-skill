// Constantes de domínio — elimina magic strings/numbers espalhados pelo código.

const PaymentStatus = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED',
});

// Regra (legada) de aprovação: cartões que começam com este prefixo são aprovados.
// Isolada aqui para deixar explícita e fácil de alterar.
const APPROVED_CARD_PREFIX = '4';

module.exports = { PaymentStatus, APPROVED_CARD_PREFIX };
