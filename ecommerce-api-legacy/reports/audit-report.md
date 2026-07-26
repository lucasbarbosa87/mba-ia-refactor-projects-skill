================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials
File: src/utils.js:1-7
Description: Objeto `config` contém senha de banco, chave do gateway de pagamento e usuário SMTP hardcoded: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`.
Impact: Credenciais de produção expostas no repositório comprometem banco, gateway de pagamento e e-mail de toda a aplicação.
Recommendation: Mover para variáveis de ambiente (`process.env`) via módulo de config, com `.env` fora do versionamento.

### [CRITICAL] Insecure Password Storage
File: src/utils.js:17-23
Description: `badCrypto()` deriva o "hash" concatenando `Buffer.from(pwd).toString('base64')` em loop e truncando para 10 chars — encoding reversível, sem salt e não criptográfico.
Impact: Vazamento do banco expõe todas as senhas; base64 é trivialmente reversível.
Recommendation: Usar bcrypt ou Argon2 com salt por usuário.

### [CRITICAL] Sensitive Data Exposure
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` loga o número completo do cartão de crédito e a chave do gateway.
Impact: Dados de cartão (PCI) e secret do gateway vazam para logs de produção.
Recommendation: Nunca logar PAN de cartão nem secrets; mascarar dados e remover a chave dos logs.

### [CRITICAL] Missing Authentication
File: src/AppManager.js:80-137
Description: Endpoints `GET /api/admin/financial-report` (linha 80) e `DELETE /api/users/:id` (linha 131) executam operações administrativas e destrutivas sem qualquer verificação de autenticação/autorização.
Impact: Qualquer pessoa pode ler o relatório financeiro completo e deletar usuários arbitrários.
Recommendation: Adicionar middleware de autenticação/autorização protegendo rotas administrativas.

### [HIGH] God Class
File: src/AppManager.js:1-141
Description: `AppManager` concentra conexão/seed do banco (`initDb`), definição de todas as rotas (`setupRoutes`) e toda a lógica de negócio de checkout, relatório e exclusão.
Impact: Impossível testar em isolamento; qualquer mudança em uma área arrisca quebrar as outras.
Recommendation: Separar em camadas com responsabilidade única: Models (dados), Controllers (regra), Routes (HTTP), Config e Database service.

### [HIGH] Callback Hell / Pyramid of Doom
File: src/AppManager.js:37-77
Description: O checkout aninha 4+ níveis de callbacks (`db.get` course → `db.get` user → `db.run` enrollment → `db.run` payment → `db.run` audit).
Impact: Código ilegível, difícil de depurar e propenso a erros de fluxo.
Recommendation: Promisificar o acesso ao SQLite e usar async/await, extraindo passos para métodos.

### [HIGH] N+1 Queries
File: src/AppManager.js:83-128
Description: O relatório financeiro faz uma query por curso e, dentro do loop, uma query de enrollments; para cada enrollment, mais duas queries (user e payment).
Impact: Complexidade O(n²+) — degrada e sofre timeout com volume real de dados.
Recommendation: Substituir por um único JOIN (courses × enrollments × users × payments) com agregação.

### [HIGH] Business Logic in Routes
File: src/AppManager.js:28-78
Description: Validação, criação de usuário, processamento de pagamento, matrícula, registro de pagamento e auditoria estão todos inline no handler de `POST /api/checkout`.
Impact: Regra de negócio não reutilizável nem testável isoladamente; handler acoplado ao HTTP.
Recommendation: Extrair para uma camada de Controller/Service (ex.: `CheckoutController`).

### [HIGH] Missing Error Handling
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` ignora o parâmetro `err` do callback e sempre responde sucesso; a mensagem admite deixar matrículas e pagamentos órfãos no banco.
Impact: Falhas silenciosas e violação de integridade referencial (registros órfãos).
Recommendation: Tratar `err`, usar transação/cascade para dados relacionados e centralizar o error handling.

### [MEDIUM] Global Mutable State
File: src/utils.js:9-10
Description: `globalCache = {}` e `totalRevenue = 0` são estados mutáveis globais compartilhados entre todas as requisições (usados por `logAndCache`).
Impact: Race conditions e estado imprevisível entre requisições concorrentes.
Recommendation: Encapsular estado por requisição/serviço ou usar um cache com escopo controlado.

### [MEDIUM] Missing Input Validation
File: src/AppManager.js:35
Description: A validação só checa presença de `usr`, `eml`, `c_id`, `card`; não valida formato de e-mail, formato/tamanho do cartão nem torna a senha obrigatória.
Impact: Dados inválidos entram no banco e no fluxo de pagamento, gerando erros e inconsistência.
Recommendation: Validar tipos, formatos e limites de todos os inputs antes de processar.

### [MEDIUM] Magic Strings / Magic Numbers
File: src/AppManager.js:46-48
Description: Status de pagamento como literais `"PAID"`/`"DENIED"` e regra de aprovação por `cc.startsWith("4")` espalhados sem constantes nomeadas.
Impact: Erros de digitação passam silenciosamente; regra de negócio obscura e difícil de alterar.
Recommendation: Definir constantes/enum para status de pagamento e isolar a regra de aprovação.

### [LOW] Poor Naming Conventions
File: src/AppManager.js:29-33
Description: Variáveis não descritivas: `u`, `e`, `p`, `cid`, `cc`.
Impact: Código difícil de entender e manter.
Recommendation: Renomear para `userName`, `email`, `password`, `courseId`, `creditCard`.

### [LOW] Console.log for Logging
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: Uso de `console.log` para logging de fluxo e cache em vez de logging estruturado.
Impact: Sem níveis de log, rotação ou formatação padronizada.
Recommendation: Adotar biblioteca de logging (winston/pino) com níveis.

### [LOW] Unused Imports / Dead Code
File: src/AppManager.js:2
Description: `totalRevenue` é importado de `./utils` mas nunca utilizado no arquivo; `totalRevenue` em utils.js também nunca é mutado.
Impact: Código poluído e confusão sobre dependências reais.
Recommendation: Remover import e variável não utilizados.

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
