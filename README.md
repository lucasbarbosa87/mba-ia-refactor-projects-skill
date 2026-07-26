# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.


---

## Análise Manual

Análise detalhada dos problemas identificados manualmente em cada um dos 3 projetos legados, classificados por severidade.

---

### Projeto 1: code-smells-project (Python/Flask — API E-commerce)

**Stack:** Python 3 + Flask 3.1.1 + SQLite  
**Domínio:** API de E-commerce (produtos, usuários, pedidos)  
**Arquivos analisados:** 4 (app.py, controllers.py, models.py, database.py)

#### CRITICAL (4 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **SQL Injection** | `models.py:25-27, 36-39, 52-55, 98-100, 236-244` | Queries construídas com concatenação de strings: `"SELECT * FROM produtos WHERE id = " + str(id)` | Atacante pode ler/modificar/deletar todo o banco de dados. Vulnerabilidade #1 do OWASP Top 10. |
| 2 | **Hardcoded Credentials** | `app.py:8` | `SECRET_KEY = "minha-chave-super-secreta-123"` | Chave exposta no código-fonte permite forjar sessões e comprometer autenticação. |
| 3 | **Endpoint Admin Query sem Autenticação** | `app.py:51-66` | `/admin/query` executa SQL arbitrário sem verificar autenticação | Qualquer pessoa pode executar comandos SQL arbitrários na aplicação, incluindo DROP TABLE. |
| 4 | **Exposição de SECRET_KEY via API** | `controllers.py:248` | Health check retorna `"secret_key": "minha-chave-super-secreta-123"` | Credenciais de segurança expostas em endpoint público. |

#### HIGH (5 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Senhas em Texto Plano** | `models.py:68-77, 96-106` | Senhas armazenadas e comparadas diretamente sem hash | Vazamento do banco expõe todas as senhas dos usuários. Viola práticas básicas de segurança. |
| 2 | **N+1 Queries** | `models.py:162-192, 196-226` | Loop com queries aninhadas em `get_pedidos_usuario` e `get_todos_pedidos` | Performance degrada exponencialmente com volume de dados. Pode derrubar o servidor. |
| 3 | **Lógica de Negócio no Controller** | `controllers.py:171-173` | Notificações (email, SMS, push) simuladas diretamente no controller de pedidos | Impossível testar isoladamente, viola Single Responsibility Principle, código não reutilizável. |
| 4 | **Ausência de Validação de Email** | `controllers.py:144-145` | Usuário criado sem validar formato de email | Dados inválidos no banco, problemas em integrações futuras com email. |
| 5 | **Endpoint Reset DB sem Autenticação** | `app.py:44-50` | `/admin/reset-db` apaga todo o banco sem autenticação | Qualquer pessoa pode destruir todos os dados da aplicação com uma requisição POST. |

#### MEDIUM (2 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Código Duplicado de Validação** | `controllers.py:28-49, 67-82` | Mesmas validações de produto repetidas em `criar_produto` e `atualizar_produto` | Manutenção difícil, risco de inconsistências entre endpoints similares. |
| 2 | **Magic Strings para Status** | `controllers.py:204`, `models.py` | Status como `"pendente"`, `"aprovado"` espalhados pelo código sem constantes | Erros de digitação passam silenciosamente, difícil refatorar ou internacionalizar. |

#### LOW (3 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Print para Logging** | `controllers.py:10, 57, 172-174` | Uso de `print()` ao invés de logging estruturado | Sem níveis de log, rotação de arquivos ou formatação padronizada. |
| 2 | **Concatenação de Strings** | `controllers.py:10` | `"Listando " + str(len(produtos)) + " produtos"` | Menos legível que f-strings, estilo Python 2. |
| 3 | **Variável Global para DB** | `database.py:5-6` | `db_connection = None` como estado global mutável | Dificulta testes unitários e operação em ambiente multi-thread. |

---

### Projeto 2: ecommerce-api-legacy (Node.js/Express — LMS API)

**Stack:** Node.js + Express 4.18.2 + SQLite3  
**Domínio:** LMS com fluxo de checkout (usuários, cursos, matrículas, pagamentos)  
**Arquivos analisados:** 3 (app.js, AppManager.js, utils.js)

#### CRITICAL (3 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Credenciais Hardcoded** | `utils.js:2-5` | `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_..."` | Credenciais de produção e chave de gateway de pagamento expostas no código-fonte. |
| 2 | **Criptografia Insegura** | `utils.js:14-19` | Função `badCrypto` usa base64 repetido 10.000 vezes como "hash" | Senhas trivialmente reversíveis. Base64 não é criptografia, é encoding. |
| 3 | **Log de Dados Sensíveis** | `AppManager.js:37` | `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` | Número completo do cartão de crédito e chave do gateway nos logs. Viola PCI-DSS. |

#### HIGH (4 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **God Class** | `AppManager.js:1-115` | Uma única classe contém inicialização de DB, definição de rotas e toda lógica de negócio | Impossível testar, manter ou escalar. Viola completamente separação de responsabilidades. |
| 2 | **N+1 Queries (3 níveis)** | `AppManager.js:65-96` | Financial report faz queries aninhadas: courses → enrollments → users → payments | Performance O(n³), timeout garantido com volume de dados real. |
| 3 | **Deleção sem Cascade** | `AppManager.js:100-104` | Delete user deixa enrollments e payments órfãos no banco | Integridade referencial quebrada, dados inconsistentes permanentemente. |
| 4 | **Callback Hell** | `AppManager.js:27-76` | 6+ níveis de callbacks aninhados no fluxo de checkout | Código ilegível, impossível debugar, propenso a vazamento de recursos. |

#### MEDIUM (2 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Estado Global Mutável** | `utils.js:7-8` | `globalCache = {}` e `totalRevenue = 0` como variáveis globais exportadas | Race conditions em ambiente concorrente, estado imprevisível entre requisições. |
| 2 | **Ausência de Error Handling** | `AppManager.js:37-75` | Apenas `res.status(500).send("Erro")` sem logging ou tratamento adequado | Difícil diagnosticar problemas em produção, usuário não recebe feedback útil. |

#### LOW (3 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Nomes de Variáveis Ruins** | `AppManager.js:28-32` | `u`, `e`, `p`, `cid`, `cc` ao invés de nomes descritivos | Código ilegível, difícil onboarding de novos desenvolvedores. |
| 2 | **Código Duplicado em Callbacks** | `AppManager.js:65-96` | Lógica de agregação de dados repetida em múltiplos callbacks | Manutenção difícil, bugs corrigidos em um lugar mas não em outro. |
| 3 | **Ausência de Documentação** | `AppManager.js` | Nenhum comentário ou JSDoc explicando o fluxo de checkout | Difícil entender regras de negócio sem ler todo o código. |

---

### Projeto 3: task-manager-api (Python/Flask — Task Manager)

**Stack:** Python 3 + Flask + SQLAlchemy + SQLite  
**Domínio:** API de gerenciamento de tarefas (tasks, users, categories)  
**Arquivos analisados:** 15 (estrutura parcialmente organizada com models/, routes/, services/, utils/)

> **Nota:** Este projeto já possui alguma separação de camadas, mas ainda apresenta problemas significativos de segurança e arquitetura.

#### CRITICAL (3 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **MD5 para Hash de Senhas** | `models/user.py:26-27` | `hashlib.md5(pwd.encode()).hexdigest()` | MD5 é criptograficamente quebrado desde 2004. Rainbow tables quebram em segundos. |
| 2 | **Credenciais SMTP Hardcoded** | `services/notification_service.py:9-12` | `email_password = 'senha123'` | Credenciais de email expostas no código-fonte. |
| 3 | **SECRET_KEY Hardcoded** | `app.py:13` | `SECRET_KEY = 'super-secret-key-123'` | Chave de sessão exposta, permite forjar cookies de autenticação. |

#### HIGH (4 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Senha Exposta na API** | `models/user.py:17-25` | Método `to_dict()` retorna `'password': self.password` | Hash de senha exposto em todos os endpoints que retornam dados de usuário. |
| 2 | **Ausência de Autenticação** | `routes/*.py` | Nenhum endpoint verifica autenticação ou autorização | Qualquer pessoa pode acessar, criar, modificar ou deletar qualquer dado. |
| 3 | **Código Duplicado (overdue check)** | `routes/task_routes.py:25-35, 67-77, 224-230` + `routes/user_routes.py:122-132` | Mesma lógica de verificação de task atrasada repetida 4+ vezes | Inconsistências entre implementações, manutenção multiplicada. |
| 4 | **Ausência de Camada Controller** | `routes/*.py` | Lógica de negócio implementada diretamente nas rotas | Viola MVC, impossível reutilizar lógica entre endpoints ou em CLI/jobs. |

#### MEDIUM (3 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **N+1 Queries** | `routes/task_routes.py:17-55` | Loop buscando user e category individualmente para cada task | Performance degradada, queries desnecessárias ao banco. |
| 2 | **Imports Não Utilizados** | `routes/task_routes.py:6` | `import json, os, sys, time` declarados mas nunca usados | Código poluído, confunde leitores sobre dependências reais. |
| 3 | **Token de Autenticação Fake** | `routes/user_routes.py:163` | `'token': 'fake-jwt-token-' + str(user.id)` | Autenticação simulada sem segurança real, ID exposto no token. |

#### LOW (2 problemas)

| # | Problema | Arquivo:Linha | Descrição | Justificativa |
|---|----------|---------------|-----------|---------------|
| 1 | **Métodos Não Utilizados** | `models/task.py:38-53` | `validate_status()`, `validate_priority()`, `is_overdue()` definidos mas nunca chamados | Código morto, validações feitas inline nas rotas em vez de usar os métodos. |
| 2 | **Constantes Não Utilizadas** | `utils/helpers.py:78-84` | `VALID_STATUSES`, `VALID_ROLES`, etc. definidas mas não importadas | Duplicação de definições, constantes ignoradas em favor de listas inline. |

---

### Resumo da Análise

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project | 4 | 5 | 2 | 3 | **14** |
| ecommerce-api-legacy | 3 | 4 | 2 | 3 | **12** |
| task-manager-api | 3 | 4 | 3 | 2 | **12** |
| **Total** | **10** | **13** | **7** | **8** | **38** |

### Padrões Recorrentes Identificados

Os seguintes anti-patterns aparecem em múltiplos projetos e devem ser priorizados no catálogo da skill:

1. **Credenciais Hardcoded** — presente nos 3 projetos (SECRET_KEY, senhas de DB, chaves de API)
2. **Armazenamento Inseguro de Senhas** — texto plano (projeto 1), base64 (projeto 2), MD5 (projeto 3)
3. **SQL Injection / Queries Inseguras** — projetos 1 e 2 com concatenação de strings
4. **N+1 Queries** — presente nos 3 projetos, causando problemas de performance
5. **Ausência de Separação de Camadas** — lógica de negócio misturada com rotas/controllers
6. **Código Duplicado** — validações e lógica repetida em múltiplos lugares
7. **Ausência de Autenticação/Autorização** — endpoints administrativos e sensíveis desprotegidos
8. **God Class / Arquivo Monolítico** — especialmente grave no projeto 2


---

