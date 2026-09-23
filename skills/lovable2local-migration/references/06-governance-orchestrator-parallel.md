# Guia de Governança OMP e Frotas Paralelas de Migração

Este guia descreve como o Orchestrator divide e comanda as frotas de subagentes durante a migração Lovable2Local, cumprindo rigorosamente as 5 Leis Invioláveis do OMP Orchestrator.

---

## 1. As 5 Leis Invioláveis Aplicadas à Migração

1. **LEI 1 — ZERO CÓDIGO NA RAIZ**: O Orchestrator nunca altera arquivos de backend, frontend ou SQL por conta própria. Ele fatia e despacha via `task`.
2. **LEI 2 — TODO LIMPO DE TAREFAS DE DEV**: O `todo` do Orchestrator rastreia apenas marcos de governança (Auditoria, Fatiamento, Despacho, QA e Fechamento).
3. **LEI 3 — MATRIZ DE ESPECIALISTAS**:
   - `scout` (read-only): Auditoria do projeto Lovable e do host.
   - `task`: Implementação do banco, backend Go, cliente frontend e serviços systemd.
   - `reviewer`: Auditoria forense de QA (`qa-analyst`).
   - `sonic`: Ajustes literais e pontuais de refatoração.
4. **LEI 4 — PARALELISMO RADICAL**: Fatias com fronteiras de arquivos mutuamente disjuntas DEVEM rodar em paralelo no mesmo turno `task(tasks=[...])`.
5. **LEI 5 — COORDENAÇÃO VIA BROKER**: Subagentes coordenam contratos via `hub(op="send")` e o Orchestrator aguarda em barreira não-bloqueante via `hub(op="wait")`.

---

## 2. Estrutura Canônica de Fatiamento (GitHub Issues)

Toda migração Lovable2Local deve ser decomposta na seguinte esteira de issues:

```text
[Epic E01: Desacoplamento de Supabase para Go Nativo e PostgreSQL Local]
   ├── Slice 1 (#2): Criação da Base Local e Adaptação das Migrações SQL
   ├── Slice 2 (#3): Scaffolding do Backend Go (Clean Arch + pgxpool + Auth JWT)
   ├── Slice 3 (#4): Módulos de Domínio REST, Webhooks e Background Workers
   ├── Slice 4 (#5): Desacoplamento do Frontend e Substituição do Supabase Client
   └── Slice 5 (#6): Configuração de Systemd Service e Ingress do Cloudflare Tunnel
```

---

## 3. Ondas de Execução Paralela (Waves)

### Onda 1 (Banco + Estrutura Base)
- **Agente 1 (`WorkerDatabase`)**: Foca em `supabase/migrations/`, Docker Postgres e `0001_initial_schema.sql`.
- **Agente 2 (`WorkerGoScaffold`)**: Foca em `backend/go.mod`, `backend/internal/config/`, `auth_middleware.go`, `pgxpool`.
*Fronteiras 100% disjuntas: rodam juntos no mesmo turno.*

### Onda 2 (Domínio Backend + Frontend)
- **Agente 1 (`WorkerGoDomain`)**: Foca em `backend/internal/domain/`, `repository/`, `service/`, `handler/`.
- **Agente 2 (`WorkerFrontend`)**: Foca em `src/lib/api-client.ts`, `src/hooks/use-auth.ts`, componentes.
*Fronteiras 100% disjuntas: rodam juntos no mesmo turno.*

### Onda 3 (Infraestrutura)
- **Agente 1 (`WorkerSystemAndTunnel`)**: Configura os services systemd, ingress do Cloudflare Tunnel e valida conectividade.

### Onda 4 (Gate de QA Forense)
- **Agente `reviewer`**: Executa a bateria de testes de API, concorrência, multi-tenancy e build estático antes da entrega final.
