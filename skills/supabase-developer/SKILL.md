---
name: supabase-developer
description: >
  Complete Supabase and Prisma Postgres expert covering all products and tasks: Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues, RLS, Postgres performance, and Prisma Postgres provisioning. Use for any Supabase task — schema design, migrations, authentication (sign-up, sign-in, sessions, JWT, OAuth, password reset), Row Level Security (policies, audit, bypass testing), Edge Functions (deploy, invoke, local dev, secrets), Realtime (WebSocket subscriptions, broadcast, presence), connection pooling, indexing strategy, query optimization, security audits, Supabase CLI, MCP server, and framework integrations (Next.js, SvelteKit, Astro, Remix, React) with supabase-js and @supabase/ssr. Also covers Prisma Postgres: Console setup, create-db CLI provisioning, Management API, and Management API SDK.
metadata:
  fused-from:
    - supabase
    - supabase-audit-rls
    - supabase-auth
    - supabase-development
    - supabase-edge-functions
    - supabase-postgres-best-practices
    - supabase-realtime
    - prisma-postgres
  version: "1.0.0"
---

# Supabase Developer

## Core Principles

**1. Supabase changes frequently — verify against current docs before implementing.**
Do not rely on training data for Supabase features. Function signatures, config.toml settings, and API conventions change between versions. Before implementing, look up the relevant topic using the documentation access methods below.

**2. Verify your work.**
After implementing any fix, run a test query to confirm the change works. A fix without verification is incomplete.

**3. Recover from errors, don't loop.**
If an approach fails after 2-3 attempts, stop and reconsider. Try a different method, check documentation, inspect the error more carefully, and review relevant logs. Supabase issues are not always solved by retrying the same command.

**4. RLS by default in exposed schemas.**
Enable RLS on every table in any exposed schema, especially `public`. Tables in exposed schemas are reachable through the Data API. For private schemas, prefer RLS as defense in depth. After enabling RLS, create policies that match the actual access model rather than defaulting every table to the same `auth.uid()` pattern.

**5. Security checklist.**
When working on any task touching auth, RLS, views, storage, or user data, run through this checklist:

- **Auth and session security**
  - **Never use `user_metadata` claims in JWT-based authorization.** `raw_user_meta_data` is user-editable and can appear in `auth.jwt()` — it is unsafe for RLS policies. Store authorization data in `raw_app_meta_data` / `app_metadata` instead.
  - **Deleting a user does not invalidate existing access tokens.** Sign out or revoke sessions first; keep JWT expiry short for sensitive apps.
  - **JWT claims are not always fresh** until the user's token is refreshed — do not rely on stale `app_metadata` for time-sensitive authorization.

- **API key and client exposure**
  - **Never expose the `service_role` key in public clients.** In Next.js, any `NEXT_PUBLIC_` env var is sent to the browser.

- **RLS, views, and privileged database code**
  - **Views bypass RLS by default.** In Postgres 15+, use `CREATE VIEW ... WITH (security_invoker = true)`. In older versions, revoke access from `anon` and `authenticated` roles, or place views in an unexposed schema.
  - **UPDATE requires a SELECT policy.** Without a SELECT policy, updates silently return 0 rows — no error, just no change.
  - **Do not put `security definer` functions in an exposed schema.**

- **Storage access control**
  - **Storage upsert requires INSERT + SELECT + UPDATE.** Granting only INSERT allows new uploads but file replacement silently fails.

For any security concern not covered above, fetch: `https://supabase.com/docs/guides/security/product-security.md`

---

## Supabase CLI

Always discover commands via `--help` — never guess. The CLI structure changes between versions.

```bash
supabase --help                    # All top-level commands
supabase <group> --help            # Subcommands
supabase <group> <command> --help  # Flags for a specific command
```

**Known gotchas:**
- `supabase db query` requires **CLI v2.79.0+** → use MCP `execute_sql` or `psql` as fallback
- `supabase db advisors` requires **CLI v2.81.3+** → use MCP `get_advisors` as fallback
- Always create migration files with `supabase migration new <name>` — never invent filenames manually

**Version check:** `supabase --version`

---

## Supabase MCP Server

Setup: [MCP setup guide](https://supabase.com/docs/guides/getting-started/mcp)

**Troubleshooting connection issues** — follow in order:

1. Check reachability: `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp` — `401` means up, timeout means down.
2. Verify `.mcp.json` in project root points to `https://mcp.supabase.com/mcp`.
3. If tools aren't visible, trigger OAuth 2.1 auth flow in the agent, complete in browser, reload session.

---

## Documentation Access

Before implementing any Supabase feature, find current documentation:

1. **MCP `search_docs`** (preferred — returns relevant snippets directly)
2. **Fetch docs as markdown** — append `.md` to any docs page URL
3. **Web search** for Supabase-specific topics when you don't know which page to look at

---

## Schema Changes Workflow

**To iterate on schema changes:** use `execute_sql` (MCP) or `supabase db query` (CLI). These run SQL directly without creating migration history entries, so you can iterate freely.

**Do NOT use `apply_migration` to change a local schema** — it writes a history entry on every call. You cannot iterate, and `supabase db diff` / `supabase db pull` will produce empty or conflicting diffs.

**When ready to commit:**

1. Run advisors → `supabase db advisors` (CLI v2.81.3+) or MCP `get_advisors`. Fix any issues.
2. Review the Security Checklist if changes involve views, functions, triggers, or storage.
3. Generate migration → `supabase db pull <descriptive-name> --local --yes`
4. Verify → `supabase migration list --local`

---

## Authentication

See [references/auth-operations.md](references/auth-operations.md) for full auth API patterns (sign-up, sign-in, sign-out, token refresh, password reset, admin operations).

**Key auth rules:**
- Use `anon` key for client/public-facing auth operations
- Use `service_role` key **only** for admin operations — never expose to clients
- Implement token refresh before access tokens expire (default: 1 hour)
- Session flow: sign-in → access_token + refresh_token → use access_token → refresh when expired → sign-out invalidates refresh_token

**Framework integration:**
- **Next.js** — use `@supabase/ssr` for server-side auth, middleware for protected routes, Server Components for auth state
- **SvelteKit** — use `@supabase/auth-helpers-sveltekit`, hooks for auth handling, load functions for data fetching

---

## Row Level Security (RLS)

RLS basics — see [references/security-rls-basics.md](references/security-rls-basics.md) and [references/security-rls-performance.md](references/security-rls-performance.md).

**Common patterns:**

```sql
-- User owns their data (all operations)
CREATE POLICY "Users own their data" ON user_data FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Public read, authenticated write
CREATE POLICY "Public read" ON posts FOR SELECT USING (published = true);
CREATE POLICY "Author write" ON posts FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "Author update" ON posts FOR UPDATE USING (auth.uid() = author_id);
```

**RLS audit** — when asked to audit or test RLS policies for vulnerabilities, see [references/rls-audit.md](references/rls-audit.md) for test vectors, output format, and evidence collection.

---

## Edge Functions

See [references/edge-functions.md](references/edge-functions.md) for deployment, invocation, local dev, secrets management, advanced patterns, and testing.

**Quick reference:**
```bash
supabase functions new my-function      # Create
supabase functions serve                # Local dev
supabase functions deploy my-function   # Deploy
supabase secrets set KEY=value          # Set secrets
supabase functions logs my-function     # View logs
```

**Limits:** 2-second CPU time, 150-second wall clock timeout. Functions run on Deno Deploy (TypeScript/JavaScript).

---

## Realtime

See [references/realtime.md](references/realtime.md) for WebSocket connection setup, database change subscriptions, broadcast messaging, presence tracking, and practical listener scripts.

**Three Realtime features:**
- **Postgres Changes** — subscribe to INSERT/UPDATE/DELETE on tables
- **Broadcast** — send/receive messages across clients in a channel
- **Presence** — track online users in a channel

**Enable Realtime:** Database > Replication > enable replication for target tables. RLS is respected — users only receive changes for rows they can access.

---

## Storage

- Organize files in buckets by purpose
- Implement bucket access policies
- Use signed URLs for private files
- Storage upsert requires INSERT + SELECT + UPDATE (see Security Checklist)
- Handle file uploads with proper validation

---

## Postgres Performance

See [references/](references/) for 34 rule files across 8 priority categories:

| Priority | Category | Prefix |
|----------|----------|--------|
| 1 — CRITICAL | Query Performance | `query-` |
| 2 — CRITICAL | Connection Management | `conn-` |
| 3 — CRITICAL | Security & RLS | `security-` |
| 4 — HIGH | Schema Design | `schema-` |
| 5 — MEDIUM-HIGH | Concurrency & Locking | `lock-` |
| 6 — MEDIUM | Data Access Patterns | `data-` |
| 7 — LOW-MEDIUM | Monitoring & Diagnostics | `monitor-` |
| 8 — LOW | Advanced Features | `advanced-` |

Apply these when writing SQL, designing schemas, reviewing query performance, or configuring connection pooling.

---

## Prisma Postgres

Prisma Postgres is a managed PostgreSQL service by Prisma (separate from Supabase) with global
routing, instant provisioning, and an optional TypeScript SDK. Use this section when the user
is working with `prisma postgres`, `create-db`, `@prisma/management-api-sdk`, or the Prisma Console.

### Workflows

| Workflow | When to use |
|---|---|
| **Console** | Manual setup, Studio UI, direct connection details |
| **create-db CLI** | Instant database in seconds (`npx create-db@latest`) |
| **`prisma postgres link`** | Wire an existing local project to a Prisma Postgres DB |
| **Management API** | Programmatic provisioning via REST (`https://api.prisma.io/v1`) |
| **Management API SDK** | Type-safe provisioning from TypeScript/JavaScript |

### Quick CLI Provisioning

```bash
npx create-db@latest    # also: npx create-pg@latest / npx create-postgres@latest
```

Temporary databases auto-delete after ~24 hours unless claimed.

### Link an Existing Project

```bash
prisma postgres link                                      # interactive
prisma postgres link --api-key "<key>" --database "db_..." # non-interactive / CI
```

Updates `.env` with `DATABASE_URL`. Then run `prisma generate` and `prisma migrate dev`.

### Management API SDK

```bash
npm install @prisma/management-api-sdk
```

Use `createManagementApiClient` (existing token) or `createManagementApiSdk` (OAuth + refresh).
API base: `https://api.prisma.io/v1` — docs at `https://api.prisma.io/v1/doc`.

See detailed rules in `references/prisma-*.md`.

---

## Reference Guides

| Reference | When to use |
|-----------|-------------|
| [auth-operations.md](references/auth-operations.md) | Auth API calls, session management, admin user operations |
| [edge-functions.md](references/edge-functions.md) | Deploy, invoke, local dev, secrets, patterns |
| [realtime.md](references/realtime.md) | WebSocket subscriptions, broadcast, presence |
| [rls-audit.md](references/rls-audit.md) | RLS security testing, vulnerability audit |
| [skill-feedback.md](references/skill-feedback.md) | Reporting incorrect or missing skill guidance |
| [prisma-console-and-connections.md](references/prisma-console-and-connections.md) | Prisma Console operations, direct TCP connections, serverless driver choices |
| [prisma-create-db-cli.md](references/prisma-create-db-cli.md) | create-db CLI flags (`--ttl`, `--copy`, `--quiet`, `--open`), programmatic API |
| [prisma-management-api.md](references/prisma-management-api.md) | Prisma Management API — service token and OAuth workflows |
| [prisma-management-api-sdk.md](references/prisma-management-api-sdk.md) | `@prisma/management-api-sdk` typed usage and token storage |
| `query-*.md` | Indexing, query planning, index types |
| `conn-*.md` | Pooling, limits, prepared statements, idle timeout |
| `security-*.md` | Privileges, RLS basics, RLS performance |
| `schema-*.md` | Primary keys, data types, constraints, partitioning |
| `lock-*.md` | Deadlocks, advisory locks, skip locked, short transactions |
| `data-*.md` | Pagination, batch inserts, upsert, N+1 |
| `monitor-*.md` | EXPLAIN ANALYZE, pg_stat_statements, VACUUM |
| `advanced-*.md` | Full-text search, JSONB indexing |
