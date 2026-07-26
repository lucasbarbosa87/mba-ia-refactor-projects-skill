// Serviço de pagamento — encapsula a integração (simulada) com o gateway.
// Isola a regra de aprovação e evita logar dados sensíveis (cartão/secret).

const config = require('../config');
const { PaymentStatus, APPROVED_CARD_PREFIX } = require('../constants');

// Mascara o número do cartão para logs seguros: mantém só os 4 últimos dígitos.
function maskCard(card) {
    if (!card || card.length < 4) return '****';
    return `****${card.slice(-4)}`;
}

function charge(card, amount) {
    // Log seguro: sem PAN completo e sem a chave do gateway.
    console.log(`[payment] Cobrança de ${amount} no cartão ${maskCard(card)}`);

    // Regra legada preservada: aprova cartões com o prefixo configurado.
    const approved = typeof card === 'string' && card.startsWith(APPROVED_CARD_PREFIX);
    return {
        success: approved,
        status: approved ? PaymentStatus.PAID : PaymentStatus.DENIED,
    };
}

// Referência explícita ao config para deixar claro de onde viria a credencial real.
void config.paymentGatewayKey;

module.exports = { charge, maskCard };
