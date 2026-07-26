# Skill: refactor-arch

Refatoração arquitetural automatizada de projetos legados para o padrão MVC.

## Descrição

Esta skill analisa codebases, identifica anti-patterns e code smells, gera relatórios de auditoria estruturados e refatora projetos para o padrão MVC (Model-View-Controller), independente da linguagem ou framework.

## Trigger

Execute esta skill quando o usuário solicitar:
- `/refactor-arch`
- Análise de arquitetura de um projeto
- Auditoria de código para identificar problemas
- Refatoração para padrão MVC

## Execução

Esta skill opera em **3 fases sequenciais**. Cada fase deve ser completada antes de avançar para a próxima.

---

### FASE 1: Análise do Projeto

**Objetivo:** Detectar stack tecnológica e mapear arquitetura atual.

**Passos:**

1. **Identificar linguagem e framework:**
   - Analisar arquivos de configuração (package.json, requirements.txt, pom.xml, Gemfile, go.mod, etc.)
   - Verificar extensões dos arquivos fonte (.py, .js, .ts, .java, .rb, .go, etc.)
   - Detectar framework através de imports e dependências

2. **Mapear estrutura atual:**
   - Listar todos os arquivos de código-fonte
   - Identificar padrão de organização existente (ou ausência dele)
   - Detectar banco de dados utilizado

3. **Identificar domínio:**
   - Analisar nomes de entidades, tabelas e rotas
   - Inferir o propósito da aplicação

4. **Imprimir resumo formatado:**

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      [linguagem detectada]
Framework:     [framework e versão]
Dependencies:  [principais dependências]
Domain:        [domínio inferido da aplicação]
Architecture:  [descrição da arquitetura atual]
Source files:  [número] files analyzed
DB tables:     [tabelas identificadas, se aplicável]
================================
```

**Referência:** Consultar `project-analysis.md` para heurísticas de detecção.

---

### FASE 2: Auditoria de Código

**Objetivo:** Identificar anti-patterns e gerar relatório estruturado.

**Passos:**

1. **Analisar código contra catálogo de anti-patterns:**
   - Verificar cada arquivo fonte contra os padrões definidos em `anti-patterns-catalog.md`
   - Registrar arquivo e linhas exatas de cada problema encontrado
   - Classificar por severidade (CRITICAL, HIGH, MEDIUM, LOW)

2. **Verificar APIs deprecated:**
   - Identificar uso de APIs obsoletas
   - Recomendar equivalentes modernos

3. **Gerar relatório de auditoria:**
   - Seguir formato definido em `report-template.md`
   - Ordenar findings por severidade (CRITICAL primeiro)
   - Incluir descrição, impacto e recomendação para cada finding

4. **Imprimir relatório completo**

5. **Salvar relatório em arquivo:**
   - Criar diretório `reports/` na raiz do projeto se não existir
   - Salvar o relatório completo em `reports/audit-report.md`
   - O arquivo deve conter exatamente o mesmo conteúdo impresso no console

6. **OBRIGATÓRIO - Solicitar confirmação:**
   ```
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```
   
   **AGUARDAR resposta do usuário antes de prosseguir.**
   - Se `y` ou `yes`: Avançar para Fase 3
   - Se `n` ou `no`: Encerrar execução
   - Se outra resposta: Perguntar novamente

**Referências:** 
- `anti-patterns-catalog.md` para padrões a detectar
- `report-template.md` para formato do relatório

---

### FASE 3: Refatoração

**Objetivo:** Reestruturar projeto para padrão MVC e validar funcionamento.

**Passos:**

1. **Planejar nova estrutura:**
   - Definir estrutura de diretórios baseada em `mvc-guidelines.md`
   - Mapear código existente para novas camadas

2. **Executar transformações:**
   - Aplicar padrões de refatoração de `refactoring-playbook.md`
   - Criar módulo de configuração (extrair credenciais hardcoded)
   - Separar Models (acesso a dados)
   - Separar Views/Routes (apresentação/roteamento)
   - Criar Controllers (lógica de negócio)
   - Centralizar error handling
   - Criar entry point claro

3. **Preservar funcionalidade:**
   - Manter todos os endpoints originais funcionando
   - Não alterar contratos de API existentes

4. **Validar resultado:**
   - Tentar iniciar a aplicação
   - Verificar se não há erros de sintaxe ou import
   - Confirmar que endpoints respondem

5. **Imprimir resumo da refatoração:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
[estrutura de diretórios criada]

## Changes Made
- [lista de mudanças principais]

## Validation
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly
  ✓/✗ Anti-patterns eliminated
================================
```

**Referências:**
- `mvc-guidelines.md` para estrutura alvo
- `refactoring-playbook.md` para transformações

---

## Arquivos de Referência

Esta skill utiliza os seguintes arquivos de conhecimento:

| Arquivo | Propósito |
|---------|-----------|
| `project-analysis.md` | Heurísticas para detecção de linguagem, framework e arquitetura |
| `anti-patterns-catalog.md` | Catálogo de anti-patterns com sinais de detecção e severidade |
| `report-template.md` | Formato padronizado do relatório de auditoria |
| `mvc-guidelines.md` | Regras e estrutura do padrão MVC alvo |
| `refactoring-playbook.md` | Padrões de transformação com exemplos antes/depois |

---

## Regras Importantes

1. **Agnóstico de tecnologia:** Esta skill deve funcionar com qualquer linguagem/framework backend
2. **Confirmação obrigatória:** NUNCA pular a confirmação entre Fase 2 e Fase 3
3. **Preservar funcionalidade:** A aplicação DEVE continuar funcionando após refatoração
4. **Relatório completo:** Cada finding deve ter arquivo, linha, descrição e recomendação
5. **Mínimo de findings:** A Fase 2 deve identificar pelo menos 5 problemas
6. **Severidade obrigatória:** Pelo menos 1 finding deve ser CRITICAL ou HIGH
