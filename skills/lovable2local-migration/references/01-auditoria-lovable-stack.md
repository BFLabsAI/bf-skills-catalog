# Guia de Auditoria Forense da Lovable Stack

Este guia orienta o subagente `scout` na identificação de todos os pontos de contato entre a aplicação gerada pelo Lovable e os serviços externos do Supabase.

---

## 1. Mapeamento do Schema e Migrações

Execute as seguintes buscas no repositório:

```bash
# 1. Listar todas as migrações SQL em ordem cronológica
ls -la supabase/migrations/*.sql

# 2. Identificar todas as referências ao schema auth do Supabase
grep -rn "auth\.users" supabase/migrations/
grep -rn "auth\.uid()" supabase/migrations/

# 3. Mapear procedures e funções PostgreSQL (RPCs)
grep -rn "CREATE OR REPLACE FUNCTION" supabase/migrations/
```

### O que observar:
- Quais tabelas herdam ou referenciam `auth.users(id)`? (Normalmente `profiles`, `user_roles`, logs de auditoria).
- Existem triggers que sincronizavam `auth.users` com `public.profiles`? (Esses triggers devem ser desativados ou reescritos para apontar para `public.users`).

---

## 2. Mapeamento de Backend Oculto (Edge & Server Functions)

O Lovable distribui lógica de backend de três formas:

```bash
# A. Edge Functions clássicas do Supabase
ls -la supabase/functions/

# B. Rotas de API Nitro (h3) em aplicações TanStack Start
ls -la src/routes/api/

# C. Server Functions (RPCs executadas no servidor via createServerFn)
grep -rn "createServerFn" src/
```

### O que catalogar para cada função:
1. **Nome e rota**: Qual o path HTTP ou nome da RPC.
2. **Método e Payload**: O que ela recebe (JSON body, query params, headers de auth).
3. **Regra de negócio**: Envio de WhatsApp, webhook de ERP, conciliação de vendas, cálculo de comissão.
4. **Segredos consumidos**: Quais variáveis de ambiente ela lê (`process.env.*`).

---

## 3. Mapeamento de Chamadas no Frontend

```bash
# 1. Chamadas diretas do Supabase Client (PostgREST)
grep -rn "supabase\.from(" src/

# 2. Chamadas de Stored Procedures (RPCs)
grep -rn "supabase\.rpc(" src/

# 3. Chamadas do módulo de Autenticação
grep -rn "supabase\.auth\." src/

# 4. Imports diretos do SDK do Supabase
grep -rn "@supabase/supabase-js" src/
```

### O que observar:
- Formulários de Login/Registro (`src/routes/auth.tsx` ou similar).
- Hook central de autenticação (`src/hooks/use-auth.ts`).
- Route guards protegidos (`src/routes/_authenticated/` ou layout components).
- Páginas públicas que acessavam o banco com a chave anônima (ex: `/r/:slug` ou landing pages).

---

## 4. Auditoria de Infraestrutura do Host (VPS)

Antes de decidir portas e nomes, rode no host:

```bash
# 1. Status do container Docker do PostgreSQL
docker ps --filter "name=postgres"

# 2. Listar databases existentes no Postgres local
docker exec postgres psql -U postgres -l

# 3. Identificar portas livres na máquina
ss -tulpn | grep LISTEN

# 4. Inspecionar ingress do Cloudflare Tunnel ativo
cat /etc/cloudflared/config.yml
```
