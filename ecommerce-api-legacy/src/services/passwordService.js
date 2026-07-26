// Serviço de hashing de senhas.
// Substitui o `badCrypto` legado (base64 reversível) por scrypt com salt aleatório,
// usando apenas o módulo nativo `crypto` — sem novas dependências.

const crypto = require('crypto');

const KEY_LENGTH = 64;

function hash(plainPassword) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(plainPassword, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${derived}`;
}

function verify(plainPassword, stored) {
    if (!stored || !stored.includes(':')) return false;
    const [salt, expected] = stored.split(':');
    const derived = crypto.scryptSync(plainPassword, salt, KEY_LENGTH).toString('hex');
    const expectedBuf = Buffer.from(expected, 'hex');
    const derivedBuf = Buffer.from(derived, 'hex');
    if (expectedBuf.length !== derivedBuf.length) return false;
    return crypto.timingSafeEqual(expectedBuf, derivedBuf);
}

module.exports = { hash, verify };
