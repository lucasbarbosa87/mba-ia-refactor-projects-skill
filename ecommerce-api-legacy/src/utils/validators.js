// Validações de formato de entrada reutilizáveis.

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_REGEX = /^\d{13,19}$/;

function isValidEmail(value) {
    return typeof value === 'string' && EMAIL_REGEX.test(value);
}

function isValidCard(value) {
    return typeof value === 'string' && CARD_REGEX.test(value);
}

function isNonEmptyString(value) {
    return typeof value === 'string' && value.trim().length > 0;
}

module.exports = { isValidEmail, isValidCard, isNonEmptyString };
