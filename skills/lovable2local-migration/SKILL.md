---
name: lovable2local-migration
description: "Guia mestre e orquestrador para migração completa de aplicações originadas na Lovable Stack (React/Vite/TanStack + Supabase BaaS: Auth, Migrations, PostgREST, Edge Functions, Server Functions) para uma arquitetura 100% autônoma, local e de alta performance baseada em PostgreSQL 16 local + Backend dedicado em Go (Golang) com Clean Architecture + Frontend Desacoplado + Systemd Services + Cloudflare Tunnel. Use SEMPRE que o usuário pedir para 'migrar do lovable', 'migrar app lovable', 'tirar supabase', 'desacoplar supabase', 'trocar supabase por postgres e go', 'lovable2local', ou quando quiser transformar um app lovable em um SaaS robusto sem vendor lock-in. A skill coordena a governança via omp-orchestrator e delega a implementação técnica acionando as 3 skills SOTA de Golang: golang-backend-architecture, golang-idiomatic-core e golang-api-docs."
user-invocable: true
license: MIT
metadata:
  author: R7 Treinamentos / BF Labs
  version: "1.0.0"
  openclaw:
    emoji: "🚀"
allowed-tools: Read Edit Write Glob Grep Bash Agent AskUserQuestion
---

# R7 Lovable2Local Migration — O Guia Definitivo de Migração para Go + PostgreSQL Local

Esta skill atua como o **Maestro de Migração**. Ela define a estratégia, a esteira de governança e as regras cirúrgicas para pegar qualquer projeto desenvolvido no ecossistema **Lovable (React/TanStack + Supabase)** e transformá-lo em um **SaaS de alto rendimento, autônomo e sem custos de BaaS**, rodando nativamente no host com backend em Go e banco local.

---

## 🎯 O Triângulo de Especialistas (Skills Acopladas)

Ao executar esta migração, a `r7-lovable2local-migration` aciona e exige o cumprimento das diretrizes de quatro habilidades centrais:

1. **`omp-orchestrator`**: Governança pura, fatiamento em GitHub Issues atômicas (`to-issues`), proibição de código na raiz pelo orquestrador e despacho de frotas paralelas de subagentes (`scout`, `task`, `reviewer`, `sonic`).
2. **`golang-backend-architecture`**: Clean Architecture em Go (`cmd/api`, `internal/domain`, `service`, `handler`, `repository`), pool `pgxpool`, transações ACID, isolamento multi-tenant e autenticação segura com JWT + bcrypt.
3. **`golang-idiomatic-core`**: Boas práticas de linguagem (*accept interfaces, return structs*), propagação de `context.Context`, concorrência com Goroutines e worker pools para tarefas em background (WhatsApp, webhooks, conciliação) e envelopes de erro RFC-7807.
4. **`golang-api-docs`**: Anotações padronizadas GoDoc, documentação OpenAPI/Swagger 3.0 via `swaggo/swag` e exposição do Swagger UI interativo.

---

## 🔄 O Ciclo de Vida da Migração em 6 Fases

```text
[Fase 1: Reconhecimento] ──> [Fase 2: Governança] ──> [Fase 3: Banco Local]
         │                            │                         │
         ▼                            ▼                         ▼
Auditoria do Lovable        Fatiamento em Issues      Migrações SQL Adaptadas
(Schema, Auth, Functions)   no GitHub (to-issues)     (auth.users -> public.users)
         │                            │                         │
         └────────────────────────────┼─────────────────────────┘
                                      ▼
                        [Fase 4: Backend Go SOTA]
                                      │
                        Clean Architecture + pgxpool
                        JWT Auth + Swagger + Workers
                                      │
                                      ▼
                        [Fase 5: Frontend Decouple]
                                      │
                        api-client.ts + use-auth.ts
                        Remoção de @supabase-js
                                      │
                                      ▼
                        [Fase 6: Infra & Exposição]
                                      │
                        Systemd Units (:8014 & :8015)
                        Cloudflare Tunnel + QA Final
```

---

## 📋 Fase 1: Reconhecimento Forense do Projeto Lovable

Antes de alterar qualquer arquivo, despache um subagente `scout` para mapear o acoplamento do Lovable:

1. **Schema e Migrações**:
   - Inspecione `supabase/migrations/` e liste todas as tabelas, tipos ENUM, triggers e procedures.
   - Identifique todas as foreign keys que apontam para `auth.users(id)`.
2. **Camada de Backend Oculta no Lovable**:
   - Verifique se existem Edge Functions em `supabase/functions/`.
   - Verifique se o app é TanStack Start / Nitro com rotas de API em `src/routes/api/` ou server functions RPC em `src/lib/*.functions.ts` (`createServerFn`).
3. **Chamadas de Dados no Frontend**:
   - Busque por `supabase.from(` em `src/` (queries diretas no client dependentes de RLS).
   - Busque por `supabase.rpc(` (procedures do banco expostas).
   - Busque por `supabase.auth.` (login, signup, resetPassword, onAuthStateChange).
4. **Infraestrutura do Host**:
   - Localize o container Docker de PostgreSQL (porta `5432`).
   - Identifique portas livres para a nova API (ex: `8014`) e Web (ex: `8015`).
   - Verifique o Cloudflare Tunnel ativo em `/etc/cloudflared/config.yml`.

> Consulte o guia detalhado em [references/01-auditoria-lovable-stack.md](./references/01-auditoria-lovable-stack.md).

---

## 🏛️ Fase 2: Governança e Fatiamento via OMP Orchestrator

Siga as Leis Invioláveis do `omp-orchestrator`:
- O Orchestrator **NUNCA codifica diretamente** no seu turno.
- Toda modificação é fatiada em uma Epic com Slices verticais no GitHub (`to-issues`).
- Crie ou atualize `CONTEXT.md`, `AGENTS.md`, `docs/adr/` e `ORCHESTRATOR-ROADMAP.md`.
- Slices com arquivos disjuntos são despachadas juntas em lotes paralelos via `task(tasks=[...])`.

### Estrutura Padrão de Slices para Lovable2Local:
- **Slice 1 (Database)**: Criação do banco local e adaptação das migrações SQL.
- **Slice 2 (Go Core & Auth)**: Scaffolding Clean Architecture, `pgxpool`, JWT Auth e Swagger.
- **Slice 3 (Go Domain & Workers)**: Handlers de domínio, regras de negócio e background workers.
- **Slice 4 (Frontend Decoupling)**: Cliente REST tipado e substituição do `@supabase/supabase-js`.
- **Slice 5 (Infra & Tunnel)**: Criação dos serviços systemd e rota no Cloudflare Tunnel.

> Consulte o guia detalhado em [references/06-governance-orchestrator-parallel.md](./references/06-governance-orchestrator-parallel.md).

---

## 🗄️ Fase 3: Migração do Banco de Dados para PostgreSQL Local

1. **Criação da Base e Usuário Isolados**:
   - Crie o database (ex: `r7<nome_app>`) no container Docker do PostgreSQL 16.
   - Crie um usuário dedicado com permissões concedidas apenas àquela base.
2. **Criação da Tabela `public.users` (Substituta do Supabase Auth)**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

   CREATE TABLE IF NOT EXISTS public.users (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       email VARCHAR(255) UNIQUE NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       full_name VARCHAR(255),
       created_at TIMESTAMPTZ DEFAULT now(),
       updated_at TIMESTAMPTZ DEFAULT now()
   );
   ```
3. **Adaptação das Migrações**:
   - Substitua todas as cláusulas `REFERENCES auth.users(id)` por `REFERENCES public.users(id)`.
   - Remova dependências de schemas internos do Supabase (`auth.uid()`, `storage.objects`).
   - Aplique as migrações sequencialmente e salve o schema consolidado em `backend/migrations/0001_initial_schema.sql`.

> Consulte o guia detalhado em [references/02-database-postgres-local.md](./references/02-database-postgres-local.md).

---

## ⚡ Fase 4: Construção do Backend Dedicado em Go

Construa o serviço em `<repo>/backend` aplicando rigorosamente as 3 skills SOTA:

### 1. Clean Architecture (`golang-backend-architecture`)
```text
backend/
├── cmd/api/main.go               # Setup do Gin, middlewares e shutdown gracioso
├── internal/
│   ├── config/                   # 12-factor env config (PORT, DATABASE_URL, JWT_SECRET)
│   ├── domain/                   # Structs de entidades e DTOs (sem dependências externas)
│   ├── repository/postgres/      # Queries SQL nativas com pgxpool (scoping por organization_id)
│   ├── service/                  # Casos de uso e integrações (WhatsApp, ERP, Webhooks)
│   ├── handler/                  # HTTP Handlers (Gin) com validação e mapeamento de status
│   ├── middleware/               # JWT Auth, TenantContext, CORS, RateLimiter
│   └── worker/                   # Background workers concorrentes
├── docs/                         # OpenAPI Swagger specs geradas pelo swag
└── migrations/                   # Scripts SQL versionados
```

### 2. Concorrência e Resiliência (`golang-idiomatic-core`)
- Disparos de WhatsApp (Uazapi) e webhooks externos DEVEM rodar em Goroutines assíncronas com worker pool e canais bufferizados para nunca bloquear a thread de resposta HTTP.
- Respostas de erro devem adotar o padrão RFC-7807 (`Problem Details`).
- Todo método de repositório e chamada externa DEVE aceitar `ctx context.Context`.

### 3. Documentação Automática (`golang-api-docs`)
- Documente cada handler com anotações `@Summary`, `@Tags`, `@Router`, `@Security`.
- Execute `swag init -g cmd/api/main.go -o ./docs`.
- Exponha o Swagger UI em `/swagger/*any`.

> Consulte o guia detalhado em [references/03-backend-go-clean-architecture.md](./references/03-backend-go-clean-architecture.md).

---

## 💻 Fase 5: Desacoplamento Completo do Frontend

O frontend não deve conter nenhum vestígio de chamadas a servidores remotos do Supabase.

1. **Crie `src/lib/api-client.ts`**:
   - Um cliente HTTP tipado (`fetch` encapsulado) com suporte a Bearer token (`localStorage`).
   - Métodos utilitários: `api.get`, `api.post`, `api.patch`, `api.delete`.
   - URL base via variável de ambiente: `VITE_API_URL || "/api/v1"`.
2. **Migração do Hook de Autenticação (`use-auth.ts`)**:
   - Substitua `supabase.auth.signInWithPassword` por `api.post('/auth/login', { email, password })`.
   - Armazene o `access_token` e carregue o usuário atual via `GET /auth/me`.
   - Atualize os formulários em `src/routes/auth.tsx` e os route guards em `_authenticated`.
3. **Substituição de Queries Diretas**:
   - Migre todas as chamadas `supabase.from("tabela").select(...)` e `supabase.rpc(...)` para chamadas aos novos endpoints da API Go.
4. **Validação de Build**:
   - Execute `npm run build` ou `bun run build`. O build deve concluir com sucesso com **zero erros de TypeScript**.

> Consulte o guia detalhado em [references/04-frontend-decoupling.md](./references/04-frontend-decoupling.md).

---

## 🌐 Fase 6: Infraestrutura, Cloudflare Tunnel e Gate de QA

1. **Configuração de Serviços Nativos no Systemd**:
   - Crie `/etc/systemd/system/<app>-api.service` (Porta da API Go, ex: 8014).
   - Crie `/etc/systemd/system/<app>-web.service` (Porta do Frontend SSR Node, ex: 8015).
   - Habilite e inicie ambos com `systemctl daemon-reload && systemctl enable --now ...`.
2. **Configuração do Cloudflare Tunnel**:
   - No `/etc/cloudflared/config.yml`, configure o roteamento transparente de domínio único (evitando problemas de CORS):
     ```yaml
       - hostname: <subdominio>.r7treinamentos.online
         path: api/*
         service: http://localhost:8014
       - hostname: <subdominio>.r7treinamentos.online
         path: swagger/*
         service: http://localhost:8014
       - hostname: <subdominio>.r7treinamentos.online
         service: http://localhost:8015
     ```
   - Crie o registro CNAME correspondente na zona da Cloudflare via API (usando `/root/.cf_token`).
   - Reinicie o túnel: `systemctl restart cloudflared`.
3. **Gate Obrigatório de QA (`qa-analyst`)**:
   - Despache um agente `reviewer` com a skill `qa-analyst` para auditoria forense.
   - Valide: healthchecks (200), fluxos de autenticação (201/200/401), isolamento multi-tenant, validação de payload inválido (400) e carregamento do Swagger UI e Frontend SSR.

> Consulte o guia detalhado em [references/05-infra-systemd-cloudflare.md](./references/05-infra-systemd-cloudflare.md).

---

## 📚 Guias de Referência Detalhados

Para implementar cada etapa com snippets de código prontos e comandos exatos, consulte os guias em `references/`:
- [01-auditoria-lovable-stack.md](./references/01-auditoria-lovable-stack.md) — Roteiro de mapeamento de código e dependências.
- [02-database-postgres-local.md](./references/02-database-postgres-local.md) — DDL, migração de `auth.users` e verificação.
- [03-backend-go-clean-architecture.md](./references/03-backend-go-clean-architecture.md) — Scaffolding completo do Go com as 3 skills.
- [04-frontend-decoupling.md](./references/04-frontend-decoupling.md) — Substituição de `@supabase/supabase-js` por REST client.
- [05-infra-systemd-cloudflare.md](./references/05-infra-systemd-cloudflare.md) — Templates de systemd e script de API Cloudflare.
- [06-governance-orchestrator-parallel.md](./references/06-governance-orchestrator-parallel.md) — Governança OMP, fatiamento e frotas paralelas.
