# Guia de Configuração e Migração do PostgreSQL Local

Este guia contém os comandos e scripts DDL exatos para provisionar o banco local no container PostgreSQL 16 existente e adaptar as migrações SQL do Supabase.

---

## 1. Criação do Banco e Usuário Dedicado

Execute no host (onde o container Docker `postgres` está ativo):

```bash
# 1. Conectar como superusuário postgres e criar role + database
docker exec postgres psql -U postgres -c "CREATE USER r7<app>_app WITH PASSWORD '<sua_senha_segura>';"
docker exec postgres psql -U postgres -c "CREATE DATABASE r7<app> OWNER r7<app>_app;"
docker exec postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE r7<app> TO r7<app>_app;"

# 2. Habilitar extensões na nova base
docker exec postgres psql -U postgres -d r7<app> -c 'CREATE EXTENSION IF NOT EXISTS "pgcrypto";'
docker exec postgres psql -U postgres -d r7<app> -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
```

---

## 2. DDL da Tabela `public.users` (Substituta de `auth.users`)

Antes de rodar qualquer migração de tabelas que possuam foreign keys para usuários, execute:

```sql
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
```

---

## 3. Adaptação Cirúrgica das Migrações SQL

Para cada arquivo de migração original em `supabase/migrations/`:

1. **Substituição de Referências**:
   - De: `REFERENCES auth.users(id)` $\rightarrow$ Para: `REFERENCES public.users(id)`
   - De: `REFERENCES auth.users` $\rightarrow$ Para: `REFERENCES public.users`
2. **Remoção de RLS e Policies Dependente de `auth.uid()`**:
   - Como o acesso a dados no novo modelo é mediado pelo backend em Go com queries filtradas por `organization_id`, políticas de RLS no PostgreSQL podem ser desabilitadas (`ALTER TABLE ... DISABLE ROW LEVEL SECURITY;`) ou mantidas como camada secundária de defesa.
3. **Consolidação em Script Único**:
   - Após aplicar todas as migrações sequencialmente no banco, salve o estado final em:
     `<repo>/backend/migrations/0001_initial_schema.sql`

---

## 4. Verificação de Integridade

```bash
# Testar conexão com o usuário dedicado
psql -h 127.0.0.1 -U r7<app>_app -d r7<app> -c "\dt"

# Validar quantidade de tabelas criadas
psql -h 127.0.0.1 -U r7<app>_app -d r7<app> -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"
```
