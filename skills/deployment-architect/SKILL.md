---
name: deployment-architect
description: >
  Complete deployment strategy skill covering platform selection, Cloudflare (Workers, Pages, KV, D1, R2, Wrangler),
  Netlify (CLI, functions, edge functions, netlify.toml), reverse proxies (Caddy, Traefik), DNS configuration,
  environment variable management, and VPS self-hosted deployments. Use when planning or executing any app deployment.
version: 1.0.0
tags:
  - deployment
  - cloudflare
  - netlify
  - caddy
  - traefik
  - dns
  - reverse-proxy
  - devops
  - infrastructure
---

# Deployment Architect

Unified skill for planning and executing deployments across all major platforms. Start with the platform decision tree, then follow the platform-specific sections.

---

## Platform Decision: Which Platform for Which App

Use this decision tree before writing a single config file.

### Primary Question: Where Does Your Code Run?

```
What does your app need?
│
├─ Static files only (HTML/CSS/JS, no server logic)
│   ├─ Want Git-based deploys + global CDN → Cloudflare Pages or Netlify
│   └─ Need advanced CDN rules / WAF → Cloudflare Pages
│
├─ Serverless backend (API routes, SSR)
│   ├─ JavaScript/TypeScript only, edge-first, tight Cloudflare ecosystem → Cloudflare Workers
│   ├─ Node.js runtime, JAMstack-focused, forms/identity built-in → Netlify Functions
│   └─ Full-stack framework (Next.js, Nuxt, Astro, SvelteKit)
│       ├─ Want zero-config, open-source self-hostable → Vercel (separate skill)
│       ├─ Want Cloudflare edge + bindings (KV, D1, R2) → Cloudflare Pages Functions
│       └─ Want Netlify primitives (Blobs, edge functions) → Netlify
│
├─ Long-running processes / WebSockets / Docker containers
│   ├─ Want managed containers at the edge → Cloudflare Containers
│   └─ Want full control (VPS/bare metal)
│       ├─ Need automatic SSL + simple config → Caddy
│       └─ Need Kubernetes autodiscovery / dynamic scaling → Traefik
│
├─ AI / ML workloads
│   ├─ Inference at the edge without GPU server → Cloudflare Workers AI
│   └─ Need GPU cluster or fine-tuning → VPS / cloud GPU provider
│
└─ Database / Storage
    ├─ SQLite-compatible, serverless, global → Cloudflare D1
    ├─ S3-compatible object storage → Cloudflare R2
    ├─ Key-value, low-latency reads → Cloudflare KV
    └─ Postgres/MySQL, managed → Neon / Supabase / PlanetScale
```

### Platform Comparison Matrix

| Criteria | Cloudflare Pages/Workers | Netlify | Caddy (VPS) | Traefik (K8s) |
|---|---|---|---|---|
| Static sites | Excellent | Excellent | Good | Good |
| Serverless functions | Workers (edge JS) | Node.js functions | N/A | N/A |
| SSR / full-stack | Pages Functions | Adapters | Any runtime | Any runtime |
| Database | D1, KV, R2 (native) | External only | External only | External only |
| AI bindings | Workers AI, Vectorize | No | No | No |
| Auto HTTPS | Yes (via Cloudflare) | Yes (Let's Encrypt) | Yes (Let's Encrypt) | Yes (ACME) |
| Free tier | Generous | Generous | Self-host cost | Self-host cost |
| Cold starts | None (always warm) | Sub-100ms | None | None |
| Max execution time | 30s (50ms CPU free) | 10s / 26s (Pro) | No limit | No limit |
| Vendor lock-in | High (runtime APIs) | Medium | None | None |
| Best for | Edge-first, global, AI | JAMstack, forms, identity | VPS single-server | K8s multi-service |

### When to Self-Host (Caddy/Traefik vs Managed Platform)

Self-host when:
- Long-running processes (websockets, video encoding, jobs > 30s)
- Docker containers are part of the stack
- You need direct filesystem access
- Cost at scale is prohibitive on managed platforms
- Compliance requires data in specific regions
- Running databases alongside app logic

Stay managed when:
- Team is small and ops burden matters
- Need global edge presence without infrastructure work
- Budget is unpredictable (pay-per-request)

---

## Cloudflare Platform

### Product Decision Trees

**Need to run code?**
```
├─ Serverless functions at the edge → Workers
├─ Full-stack web app with Git deploys → Pages
├─ Stateful coordination / real-time → Durable Objects
├─ Long-running multi-step jobs → Workflows
├─ Run containers → Containers
├─ Scheduled tasks (cron) → Cron Triggers
└─ Lightweight edge logic (modify HTTP) → Snippets
```

**Need to store data?**
```
├─ Key-value (config, sessions, cache) → KV
├─ Relational SQL → D1 (SQLite) or Hyperdrive (existing Postgres)
├─ Object / file storage (S3-compatible) → R2
├─ Message queue (async) → Queues
├─ Vector embeddings (AI search) → Vectorize
├─ Strongly consistent per-entity state → Durable Objects storage
└─ Persistent cache (long-term retention) → Cache Reserve
```

**Need AI/ML?**
```
├─ Run inference (LLMs, embeddings, images) → Workers AI
├─ Vector database for RAG / search → Vectorize
├─ Build stateful AI agents → Agents SDK
└─ Gateway for any AI provider (caching, routing) → AI Gateway
```

**Need security?**
```
├─ Web Application Firewall → WAF
├─ DDoS protection → DDoS Protection
├─ Bot detection → Bot Management
├─ API protection → API Shield
└─ CAPTCHA alternative → Turnstile
```

### Wrangler CLI

```bash
# Install
npm install wrangler --save-dev

# Auth
wrangler login
wrangler whoami

# Project lifecycle
wrangler init [name]              # Create new project
wrangler dev                      # Local dev server (simulated)
wrangler dev --remote             # Dev with real remote resources
wrangler deploy                   # Deploy to production
wrangler deploy --env staging     # Deploy to named environment
wrangler versions list            # List deployed versions
wrangler rollback [version-id]    # Rollback
wrangler tail                     # Real-time logs
wrangler tail --status error      # Filter error logs
```

**Resource management:**
```bash
# KV
wrangler kv namespace create NAME
wrangler kv key put "key" "value" --namespace-id=<id>

# D1
wrangler d1 create NAME
wrangler d1 migrations create NAME "description"
wrangler d1 migrations apply NAME --remote
wrangler d1 execute NAME --remote --command="SELECT * FROM users"
wrangler d1 export NAME --remote --output=./backup.sql

# R2
wrangler r2 bucket create NAME
wrangler r2 object put BUCKET/key --file path

# Secrets
wrangler secret put NAME           # Set encrypted secret
wrangler secret list
wrangler secret bulk FILE.json     # Bulk upload from JSON

# Secrets Store (centralized, reusable)
wrangler secrets-store secret create <store-id> --name SECRET_NAME --scopes workers --remote

# Pages
wrangler pages project create NAME
wrangler pages deployment create --project NAME --branch main

# Other resources
wrangler queues create NAME
wrangler vectorize create NAME --dimensions N --metric cosine
wrangler hyperdrive create NAME --connection-string "..."
wrangler workflows create NAME
```

### wrangler.jsonc / wrangler.toml Configuration

```jsonc
// wrangler.jsonc — preferred format
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-01-01",

  // KV bindings
  "kv_namespaces": [
    { "binding": "MY_KV", "id": "kv-namespace-id" }
  ],

  // D1 database
  "d1_databases": [
    { "binding": "DB", "database_name": "my-db", "database_id": "db-id" }
  ],

  // R2 bucket
  "r2_buckets": [
    { "binding": "MY_BUCKET", "bucket_name": "my-bucket" }
  ],

  // Workers AI
  "ai": { "binding": "AI" },

  // Durable Objects
  "durable_objects": {
    "bindings": [{ "name": "MY_DO", "class_name": "MyDurableObject" }]
  },

  // Environment variables (not secret)
  "vars": {
    "API_URL": "https://api.example.com",
    "NODE_ENV": "production"
  },

  // Multiple environments
  "env": {
    "staging": {
      "vars": { "API_URL": "https://api-staging.example.com" },
      "d1_databases": [
        { "binding": "DB", "database_name": "my-db-staging", "database_id": "staging-db-id" }
      ]
    }
  }
}
```

**Generate TypeScript types for bindings:**
```bash
npx wrangler types
```

**Access bindings in a Worker:**
```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // KV
    const value = await env.MY_KV.get('key');
    await env.MY_KV.put('key', 'value', { expirationTtl: 3600 });

    // D1
    const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(userId).first();
    const { results } = await env.DB.prepare('SELECT * FROM users').all();

    // D1 batch (atomic)
    await env.DB.batch([
      env.DB.prepare('INSERT INTO logs VALUES (?)').bind(Date.now()),
      env.DB.prepare('UPDATE users SET last_seen = ? WHERE id = ?').bind(Date.now(), userId)
    ]);

    // R2
    const object = await env.MY_BUCKET.get('file.pdf');
    await env.MY_BUCKET.put('file.pdf', fileData);

    // Workers AI
    const response = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
      messages: [{ role: 'user', content: 'Hello' }]
    });

    // Environment variables and secrets (same access pattern)
    const apiKey = env.API_KEY; // secret set via wrangler secret put
    const apiUrl = env.API_URL; // var set in wrangler.jsonc

    return new Response('OK');
  }
};
```

### Cloudflare Pages

**Git-based deployment:**
- Connect repo in Cloudflare Dashboard → Pages → Create project
- Set build command and output directory per framework
- Automatic deploys on push; preview URLs for every PR

**Common framework build settings:**

| Framework | Build Command | Output Dir |
|---|---|---|
| React (Vite) | `npm run build` | `dist` |
| Next.js | `npm run build` | `.next` |
| Nuxt | `npm run build` | `.output/public` |
| Astro | `npm run build` | `dist` |
| SvelteKit | `npm run build` | `build` |
| Hugo | `hugo` | `public` |

**Pages Functions (full-stack):**
```
functions/
  api/
    hello.ts          # → /api/hello
    users/
      [id].ts         # → /api/users/:id (dynamic route)
  _middleware.ts      # Middleware for all routes
```

```typescript
// functions/api/users/[id].ts
export async function onRequest(context: EventContext<Env, 'id', Record<string, unknown>>) {
  const { params, env } = context;
  const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(params.id).first();
  return Response.json(user);
}
```

**Bindings for Pages Functions** — configure in Cloudflare Dashboard → Pages → Settings → Functions, or via wrangler.toml:
```toml
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "db-id"
```

### Cloudflare Workers — Routing

**Route matching (wrangler.jsonc):**
```jsonc
{
  "routes": [
    { "pattern": "example.com/api/*", "zone_name": "example.com" },
    { "pattern": "*.example.com/*", "zone_name": "example.com" }
  ]
}
```

**Custom domain via dashboard:**
Dashboard → Workers → your worker → Triggers → Custom Domains

### D1 Database — Key Limits

| Limit | Free | Paid |
|---|---|---|
| Database size | 500 MB | 10 GB |
| Row size | 1 MB | 1 MB |
| Query timeout | 30s | 30s |
| Batch size | 1,000 statements | 10,000 statements |
| Time Travel | 7 days | 30 days |

Pricing: $0.001/million rows read + $1.00/million rows written + $0.75/GB storage/month.

### Workers AI — Common Models

```typescript
// Text generation
const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  messages: [{ role: 'user', content: prompt }]
});

// Embeddings
const embedding = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
  text: inputText
});

// Image classification
const classification = await env.AI.run('@cf/microsoft/resnet-50', {
  image: imageData
});
```

### Cloudflare Environment Variable Scoping

- **Vars** (wrangler.jsonc `vars`) — committed to code, not encrypted, public config only
- **Secrets** (wrangler secret put) — encrypted at rest, never appear in code or logs
- **Per-environment** — configure separate values in `env.staging`, `env.production` sections
- **Pages env vars** — set in Dashboard → Pages → Site Settings → Environment Variables; scope to Production or Preview

---

## Netlify Platform

### Deployment Workflow

```bash
# Install CLI
npm install -g netlify-cli   # global
# or
npm install netlify-cli -D   # local (for CI use npx netlify)

# Auth
netlify login     # Browser OAuth
netlify status    # Check auth + linked site
# For CI: export NETLIFY_AUTH_TOKEN=your_token

# Site setup
netlify init                         # Create new site with Git CI/CD
netlify init --manual                # Create without Git CI/CD
netlify link                         # Link to existing site (interactive)
netlify link --git-remote-url <url>  # Link by Git remote

# Deploy
netlify deploy                       # Draft/preview deploy
netlify deploy --prod                # Production deploy
netlify deploy --dir=dist --prod     # Specify output directory
netlify deploy --message="Fix bug"   # Add deploy message
netlify build                        # Run build locally (mirrors Netlify env)

# Local dev
netlify dev                  # Wraps framework dev server + injects env + functions
netlify dev --port 3000
netlify dev --live           # Live session sharing
netlify dev:exec <cmd>       # Run command with Netlify env loaded

# Manage
netlify open                 # Open site in Netlify dashboard
netlify rollback             # Rollback to previous deploy
netlify logs                 # Stream function logs
netlify logs:function NAME
```

**For Vite-based projects**, use the Vite plugin instead of `netlify dev`:
```bash
npm install @netlify/vite-plugin
```
```typescript
// vite.config.ts
import netlify from "@netlify/vite-plugin";
export default defineConfig({ plugins: [netlify()] });
```
Then run `npm run dev` normally — provides Blobs, DB, Functions, env vars in dev.

**CLI flags:** `--json`, `--silent`, `--debug`, `--force`

**CI environment variables:**
```bash
netlify env:set API_KEY "value"
netlify env:set API_KEY "value" --secret              # Hidden from logs
netlify env:set API_URL "https://prod.com" --context production
netlify env:set API_URL "https://staging.com" --context deploy-preview
netlify env:set DEBUG "true" --context branch:feature-x
netlify env:list
netlify env:list --plain > .env   # Export
netlify env:import .env           # Import from file
netlify env:unset API_KEY
netlify env:get API_KEY
```

**Functions CLI:**
```bash
netlify functions:list
netlify functions:invoke FUNCTION_NAME
netlify functions:invoke hello --payload '{"name":"World"}'
netlify functions:serve            # Serve functions only
netlify functions:create NAME
```

### netlify.toml Reference

```toml
[build]
  command = "npm run build"
  publish = "dist"                   # Output directory
  functions = "netlify/functions"    # Functions directory
  base = "packages/web"             # Monorepo base dir (optional)

  # Skip build if nothing changed in these paths
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF packages/web"

[build.environment]
  NODE_VERSION = "20"
  NODE_OPTIONS = "--max-old-space-size=4096"

[functions]
  node_bundler = "esbuild"

[dev]
  command = "npm run dev"
  port = 3000
  targetPort = 5173

# Context-specific overrides
[context.production]
  command = "npm run build:prod"
  [context.production.environment]
    NODE_ENV = "production"
    API_URL = "https://api.example.com"

[context.deploy-preview]
  command = "npm run build:preview"
  [context.deploy-preview.environment]
    API_URL = "https://api-staging.example.com"

[context.branch-deploy]
  command = "npm run build"

# Named branch context
[context.staging]
  command = "npm run build:staging"
  [context.staging.environment]
    API_URL = "https://api-staging.example.com"

# Redirects (processed top-to-bottom, first match wins)
[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301

[[redirects]]
  from = "/api/*"
  to = "https://api.example.com/:splat"
  status = 200
  force = true

# SPA fallback — MUST be last
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Conditional redirects
[[redirects]]
  from = "/"
  to = "/uk"
  status = 302
  conditions = {Country = ["GB"]}

# Role-based redirects (Netlify Identity)
[[redirects]]
  from = "/admin/*"
  to = "/admin/dashboard"
  status = 200
  conditions = {Role = ["admin"]}

# Security headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:"

# Long-term cache for hashed assets
[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# Build processing
[build.processing]
  skip_processing = false
[build.processing.css]
  bundle = true
  minify = true
[build.processing.js]
  bundle = true
  minify = true
[build.processing.images]
  compress = true

# Edge functions
[[edge_functions]]
  function = "geolocation"
  path = "/api/location"

# Build plugins
[[plugins]]
  package = "@netlify/plugin-lighthouse"
  [plugins.inputs]
    output_path = "reports/lighthouse.html"
```

**SPA + API proxy pattern:**
```toml
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Monorepo:**
```toml
[build]
  base = "packages/web"
  command = "npm run build"
  publish = "dist"
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF packages/web"
```

**`_redirects` file** (place in publish directory — alternative to netlify.toml):
```
/old-path   /new-path   301
/api/*      https://api.example.com/:splat   200
/*          /index.html   200
```

### Netlify Functions

**Always use the modern default export + Config pattern.** Never use the legacy `exports.handler`.

```typescript
// netlify/functions/hello.mts
import type { Context, Config } from "@netlify/functions";

export default async (req: Request, context: Context): Promise<Response> => {
  try {
    if (req.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }
    const body = await req.json();
    return Response.json({ message: `Hello ${body.name}` });
  } catch (error) {
    console.error("Function error:", error);
    return Response.json({ error: "Internal Server Error" }, { status: 500 });
  }
};

export const config: Config = {
  path: "/api/hello",           // Custom path (replaces /.netlify/functions/hello)
  method: ["GET", "POST"],      // Restrict methods
  rateLimit: {
    windowSize: 60,
    windowLimit: 100,
  },
};
```

**File structure:**
```
netlify/functions/
  _shared/           # Non-function shared code (underscore = not a function)
    auth.ts
    db.ts
  items.ts           # → /.netlify/functions/items (or custom path via config)
  users/index.ts     # → /.netlify/functions/users
```

Use `.ts` or `.mts` extensions. If both `.ts` and `.js` exist, `.js` wins.

**Path parameters:**
```typescript
// config: { path: "/api/items/:id" }
export default async (req: Request, context: Context) => {
  const { id } = context.params;
  const { name } = context.params;  // multi-segment
  return Response.json({ id });
};
```

**Multiple paths + method routing:**
```typescript
export const config: Config = {
  path: ["/api/items", "/api/items/:id"],
};

export default async (req: Request, context: Context) => {
  switch (req.method) {
    case "GET":    return handleGet(context.params.id);
    case "POST":   return handlePost(await req.json());
    case "DELETE": return handleDelete(context.params.id);
    default:       return new Response("Method not allowed", { status: 405 });
  }
};
```

**Background functions** (up to 15 minutes, client gets immediate 202):
```typescript
// MUST have -background suffix: netlify/functions/process-video-background.mts
import { getStore } from "@netlify/blobs";

export default async (req: Request, context: Context) => {
  const { videoId } = await req.json();
  const result = await processVideo(videoId);  // long-running
  const store = getStore("processed-videos");
  await store.setJSON(videoId, result);
  // Return value ignored
  return new Response("Processing complete");
};

export const config: Config = { path: "/api/process-video" };
```

**Scheduled functions:**
```typescript
export default async (req: Request) => {
  const { next_run } = await req.json();
  console.log("Next invocation at:", next_run);
  await performCleanup();
  return new Response("Done");
};

export const config: Config = {
  schedule: "@daily",    // shortcuts: @hourly, @weekly, @monthly, @yearly
  // schedule: "0 9 * * 1-5",  // cron syntax (UTC)
};
```

**Scheduled function timeout: 30 seconds. Only runs on published deploys.**

**Streaming:**
```typescript
export default async (req: Request) => {
  const stream = new ReadableStream({ /* ... */ });
  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream" },
  });
};
```

**Function resource limits:**

| Resource | Limit |
|---|---|
| Synchronous timeout | 60 seconds (26s on Pro for older runtimes) |
| Background timeout | 15 minutes |
| Scheduled timeout | 30 seconds |
| Memory | 1024 MB |
| Buffered payload | 6 MB |
| Streamed payload | 20 MB |

**Context object:**
```typescript
context.params         // Path parameters
context.geo            // { city, country: {code, name}, latitude, longitude, subdivision, timezone, postalCode }
context.ip             // Client IP
context.cookies        // .get(), .set(), .delete()
context.deploy         // { context, id, published }
context.site           // { id, name, url }
context.requestId      // Unique request ID
context.waitUntil(p)   // Extend execution after response
```

**Environment variables in functions:**
```typescript
// Preferred
const apiKey = Netlify.env.get("API_KEY");

// Also works
const dbUrl = process.env.DATABASE_URL;
```

**Client-side env var rules:**
- Vite: Only `VITE_`-prefixed vars via `import.meta.env.VITE_VAR`
- Astro: Only `PUBLIC_`-prefixed vars via `import.meta.env.PUBLIC_VAR`
- Never use `VITE_` or `PUBLIC_` prefixes for secrets

### Edge Functions (Deno runtime)

```typescript
// netlify/edge-functions/geo-redirect.ts
import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  const country = context.geo.country?.code || "US";

  if (country === "DE") {
    return Response.redirect(new URL("/de", request.url));
  }

  // Pass through to origin
  return context.next();
};

export const config = {
  path: "/*",
  excludedPath: ["/api/*", "/_next/*"],
};
```

**Transform response:**
```typescript
export default async (request: Request, context: Context) => {
  const response = await context.next();
  response.headers.set("X-Custom-Header", "value");
  const html = await response.text();
  const modified = html.replace("</body>", '<script>console.log("injected");</script></body>');
  return new Response(modified, response);
};

export const config = { path: "/*" };
```

**Edge function timeout: 50ms CPU time** (wall clock is longer but CPU budget is tight).

### Netlify Blobs

```typescript
import { getStore } from "@netlify/blobs";

// Site-wide store (persists across deploys)
const store = getStore("my-store");

// Basic operations
await store.set("key", "string value");
await store.setJSON("json-key", { foo: "bar" });
const value = await store.get("key");
const jsonValue = await store.get("json-key", { type: "json" });
await store.delete("key");
const { blobs } = await store.list();

// Binary
const arrayBuffer = await file.arrayBuffer();
await store.set("uploads/file.pdf", arrayBuffer, {
  metadata: { contentType: "application/pdf" },
});
const blob = await store.get("uploads/file.pdf", { type: "blob" });

// Deploy-specific store
const deployStore = getStore({
  name: "cache",
  deployID: context.deploy.id,
});
```

### Netlify Identity (Auth)

```javascript
// In HTML
<script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>

// Protected function
exports.handler = async (event, context) => {
  const { user } = context.clientContext;
  if (!user) return { statusCode: 401, body: "Unauthorized" };
  return { statusCode: 200, body: JSON.stringify({ user: user.email }) };
};
```

### Netlify Forms

```html
<form name="contact" method="POST" data-netlify="true" data-netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />
  <p class="hidden"><label>Don't fill this out: <input name="bot-field" /></label></p>
  <input type="text" name="name" required />
  <input type="email" name="email" required />
  <button type="submit">Send</button>
</form>
```

### Netlify Image CDN

```html
<img src="/.netlify/images?url=/images/hero.jpg&w=800&q=80&fm=webp" alt="Hero">
```

Parameters: `url` (required), `w` (width), `h` (height), `q` (quality 1-100), `fit` (cover/contain/fill), `fm` (webp/avif/auto).

### Framework Considerations

Frameworks with server-side capabilities (Astro, Next.js, Nuxt, SvelteKit, TanStack Start) generate their own serverless functions via adapters. Do **not** write raw Netlify Functions in these projects — the framework handles SSR and API routes.

Write raw Netlify Functions when:
- Using a client-side-only framework (Vite + React SPA, vanilla JS)
- Adding background or scheduled tasks to any project
- Building standalone API endpoints outside the framework's routing

### Netlify Common Pitfalls

1. Adding version numbers to `@netlify/functions` imports
2. Adding CORS headers when not needed
3. Using wrong function type for the use case
4. Forgetting `-background` suffix for background functions
5. Not using Blobs for persistent storage in background functions
6. Hardcoding environment variables
7. Using `process.env` instead of `Netlify.env.get()` inside functions
8. Not setting SPA fallback redirect as the last rule in netlify.toml

### Netlify Troubleshooting

| Error | Fix |
|---|---|
| "Not logged in" | `netlify logout && netlify login` |
| "No site linked" | `netlify link` or `netlify init` |
| "Build failed" | Run `npm run build` locally; check build logs |
| "Publish directory not found" | Verify build output path; check netlify.toml publish value |
| Network errors in deploy | Use `sandbox_permissions=require_escalated` |

### Netlify Deployment Decision Tree

```
Authenticated?
├─ No → netlify login
└─ Yes → Site linked?
    ├─ No → Git repo?
    │   ├─ Yes → netlify link --git-remote-url <url>
    │   │         └─ Fails → netlify init
    │   └─ No → netlify init
    └─ Yes → First deploy or existing?
        ├─ First → netlify deploy --prod
        └─ Existing → netlify deploy (preview) then netlify deploy --prod
```

---

## Caddy — Reverse Proxy & HTTPS

Caddy is the recommended reverse proxy for VPS deployments. It handles SSL automatically via Let's Encrypt, requires no certificate renewal scripts, and has a simple declarative config.

### When to Use Caddy

- VPS with one or a few Docker services
- Need automatic HTTPS for custom domains
- Simple reverse proxy without Kubernetes
- Local development with `.localhost` URLs

### Core Caddyfile Patterns

```
# Global options (must come first)
{
    email admin@example.com
    # For testing: acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}

# Single site
example.com {
    reverse_proxy app:8080
}

# Multiple sites
app.example.com {
    reverse_proxy app:3000
}
api.example.com {
    reverse_proxy api:8080
}

# Path-based routing (handle = keep path, handle_path = strip prefix)
example.com {
    handle /api/* {
        reverse_proxy api:8080    # /api/users → /api/users
    }
    handle {
        reverse_proxy frontend:3000
    }
}

# Strip path prefix
example.com {
    handle_path /api/* {
        reverse_proxy api:8080    # /api/users → /users
    }
}

# www redirect
www.example.com {
    redir https://example.com{uri} permanent
}

# SPA
example.com {
    root * /srv
    try_files {path} /index.html
    file_server
}

# gRPC / HTTP2 cleartext
example.com {
    reverse_proxy h2c://grpc-server:9000
}
```

**Reload config without downtime:**
```bash
caddy reload --config /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile   # Validate first
caddy fmt --overwrite /etc/caddy/Caddyfile     # Format
```

### Request Matchers

```
# Named matchers
@api path /api/*
@post method POST
@websocket header Connection *Upgrade*
@local remote_ip 192.168.0.0/16 10.0.0.0/8
@json header Content-Type application/json

# Combined (AND logic within block)
@api_post {
    path /api/*
    method POST
}

# Regex with captures
@assets path_regexp static \.(css|js|png|jpg)$

# CEL expression
@complex expression `{method} == "POST" && {path}.startsWith("/api")`

# Use a matcher
handle @api { reverse_proxy api:8080 }
```

### Header Manipulation

```
example.com {
    reverse_proxy backend:8080 {
        # Request headers (header_up)
        header_up Host {upstream_hostport}
        header_up +X-Real-IP {remote_host}
        header_up -Authorization              # Remove

        # Response headers (header_down)
        header_down -Server
        header_down +X-Proxy "Caddy"
    }
}
```

**Caddy auto-sets:** `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`.

### Load Balancing

```
example.com {
    reverse_proxy node1:80 node2:80 node3:80 {
        lb_policy round_robin      # random, round_robin, least_conn, first, ip_hash, uri_hash
        lb_retries 3
        lb_try_duration 5s

        # Active health checks
        health_uri /health
        health_interval 30s
        health_timeout 5s
        health_status 200

        # Passive health checks
        fail_duration 30s
        max_fails 3
        unhealthy_status 500 502 503
    }
}
```

### TLS Configuration

**Automatic HTTPS (default)** — works when:
- DNS points to your server
- Ports 80 and 443 are open

```
# Wildcard certificate (requires DNS challenge)
*.example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }

    @app1 host app1.example.com
    handle @app1 { reverse_proxy app1:8080 }

    @app2 host app2.example.com
    handle @app2 { reverse_proxy app2:8080 }
}

# Internal / self-signed
localhost {
    tls internal
    reverse_proxy app:8080
}

# Custom certificate files
example.com {
    tls /path/to/cert.pem /path/to/key.pem
}

# mTLS (client certificates)
example.com {
    tls {
        client_auth {
            mode require_and_verify
            trust_pool file /path/to/ca.pem
        }
    }
}

# On-demand TLS (for unknown domains — saas proxy)
{
    on_demand_tls {
        ask http://auth-service/check-domain    # CRITICAL: always set ask endpoint
    }
}
https:// {
    tls { on_demand }
    reverse_proxy backend:8080
}
```

**Let's Encrypt rate limits:** 50 certs/domain/week, 5 duplicates/week. Always test with staging first.

**Building Caddy with DNS plugins (required for wildcard certs):**
```bash
xcaddy build --with github.com/caddy-dns/cloudflare
```
DNS providers: cloudflare, route53, digitalocean, duckdns, godaddy, namecheap, gandi, vultr.

**Persist certificates** — always mount `/data` as a named Docker volume.

### Security Headers Snippet

```
(security) {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options nosniff
        X-Frame-Options SAMEORIGIN
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}

example.com {
    import security
    reverse_proxy backend:8080
}
```

### Caddy + Docker Compose

```yaml
services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"    # HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data        # CRITICAL: persist certificates
      - caddy_config:/config
    networks:
      - web
    extra_hosts:
      - "host.docker.internal:host-gateway"    # Access host services

  app:
    image: myapp
    networks:
      - web
    expose:
      - "8080"    # No port mapping needed when on same network

volumes:
  caddy_data:      # Named volume = persisted across restarts
  caddy_config:

networks:
  web:
```

**Proxy to container:** use container/service name as hostname (`app:8080`).
**Proxy to host service:** use `host.docker.internal:8080` (add `extra_hosts` entry).
**Linux Docker older versions:** use `172.17.0.1` instead of `host.docker.internal`.

**UFW + Docker:** Docker bypasses UFW. Allow Docker networks explicitly:
```bash
sudo ufw allow from 172.16.0.0/12 to any port 8080
```

**Reload in Docker:**
```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Caddy Local Dev Proxy

Caddy's Admin API (localhost:2019) can manage routes dynamically — useful for local dev.

```bash
# Check status
curl -sf http://localhost:2019/config/

# List routes
curl -sf http://localhost:2019/config/apps/http/servers/local_proxies/routes

# Add route (NAME.localhost → localhost:PORT)
curl -sf -X POST "http://localhost:2019/config/apps/http/servers/local_proxies/routes" \
  -H "Content-Type: application/json" \
  -d '{"@id":"proxy_NAME","match":[{"host":["NAME.localhost"]}],"handle":[{"handler":"reverse_proxy","upstreams":[{"dial":"localhost:PORT"}]}],"terminal":true}'

# Delete route
curl -sf -X DELETE "http://localhost:2019/id/proxy_NAME"
```

On macOS, `*.localhost` resolves to 127.0.0.1 automatically. On Linux, add `/etc/hosts` entries.

**Find free port:**
```bash
for port in $(seq 3000 3100); do
  lsof -i :$port > /dev/null 2>&1 || { echo $port; break; }
done
```

### Caddy Troubleshooting

| Problem | Solution |
|---|---|
| "no upstreams available" | Backend not running or wrong Docker network; verify with `docker exec caddy nslookup backend` |
| "connection refused" | Backend binding to 127.0.0.1 instead of 0.0.0.0 |
| Certificate not obtained | DNS not pointing to server, or ports 80/443 blocked; use staging CA to debug |
| 403 Forbidden | Backend needs `header_up Host localhost` |
| WebSocket fails | Add `flush_interval -1` in reverse_proxy block |
| Slow responses / timeout | Set `transport http { response_header_timeout 120s }` |
| Caddy not running (local) | `brew install caddy && caddy start` |

**Diagnostic commands:**
```bash
# Validate and view config
caddy validate --config /etc/caddy/Caddyfile
docker logs -f caddy 2>&1 | grep -i error
docker exec caddy nslookup backend       # DNS from container
openssl s_client -connect example.com:443 -servername example.com   # Check cert

# Admin API
curl localhost:2019/config/              # View running config
docker exec caddy rm -rf /data/caddy/certificates && docker restart caddy  # Reset certs
```

### Caddyfile Syntax Reference

**Site addresses:**
```
example.com                    # Automatic HTTPS
http://example.com             # HTTP only
:8080                          # All interfaces, port 8080
localhost                      # Self-signed cert
*.example.com                  # Wildcard (DNS challenge required)
example.com, www.example.com   # Multiple domains
```

**Environment variables in Caddyfile:**
```
{$DOMAIN:example.com} {
    reverse_proxy {$BACKEND_HOST}:{$BACKEND_PORT:8080}
    tls { dns cloudflare {$CF_API_TOKEN} }
}
```
`{$VAR:default}` uses the default if VAR is not set.

**Placeholders:** `{host}`, `{path}`, `{uri}`, `{query}`, `{method}`, `{remote_host}`, `{scheme}`, `{upstream_hostport}`

**Compression:**
```
example.com {
    encode gzip zstd
    reverse_proxy backend:8080
}
```

**Basic auth:**
```
example.com {
    basicauth /admin/* {
        admin $2a$14$hash...    # Generate: caddy hash-password
    }
    reverse_proxy admin:8080
}
```

**Access logging:**
```
example.com {
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

**Dynamic upstreams from DNS:**
```
reverse_proxy {
    dynamic srv _http._tcp.backend.service.consul
    dynamic a backend.service.consul 8080 { refresh 30s }
}
```

**caddy-docker-proxy plugin** (auto-generate config from Docker labels):
```yaml
services:
  caddy:
    image: lucaslorentz/caddy-docker-proxy:ci-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - caddy_data:/data
  app:
    image: myapp
    labels:
      caddy: app.example.com
      caddy.reverse_proxy: "{{upstreams 8080}}"
```

---

## Traefik — Kubernetes / Dynamic Service Discovery

Traefik is the recommended reverse proxy for Kubernetes environments or any setup that requires native autodiscovery of services.

### When to Use Traefik Over Caddy

- Kubernetes cluster (Traefik has native IngressRoute CRDs)
- Services scale dynamically and you don't want to reconfigure the proxy on every change
- Docker Swarm environments
- Need circuit breakers, retry middleware at the proxy layer

### Trade-offs

- Traefik has ~10-15% less throughput than Nginx at very high load (>10K RPS), but better developer experience
- Autodiscovery eliminates manual reconfiguration when scaling
- For simple VPS single-server setups, Caddy is simpler

### Kubernetes Deployment

```bash
# Install with Helm
helm install traefik traefik/traefik
```

**IngressRoute for HTTP routing:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-app
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`api.example.com`) && PathPrefix(`/v1`)
      kind: Rule
      services:
        - name: my-service
          port: 8000
  tls:
    certResolver: letsencrypt
```

**Middleware examples:**
```yaml
# Rate limiting
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: rate-limit
spec:
  rateLimit:
    average: 100
    burst: 200

# Circuit breaker
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: circuit-breaker
spec:
  circuitBreaker:
    expression: ResponseCodeRatio(500, 600, 0, 600) > 0.30
```

**Static configuration (traefik.yaml):**
```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /data/acme.json
      httpChallenge:
        entryPoint: web

api:
  dashboard: true    # Enable for development only

metrics:
  prometheus: {}     # Expose Prometheus metrics
```

**Health checks:**
```yaml
services:
  - name: my-service
    port: 8000
    healthCheck:
      path: /health
      interval: 30s
      timeout: 5s
```

---

## DNS Configuration

### Record Types

| Record | Use |
|---|---|
| A | Domain → IPv4 address |
| AAAA | Domain → IPv6 address |
| CNAME | Domain → another domain (not root) |
| MX | Mail server |
| TXT | Verification, SPF, DKIM |
| NS | Nameserver delegation |
| SRV | Service discovery |
| CAA | Certificate Authority Authorization |

### Common DNS Patterns

**Pointing to Netlify:**
```
A       @       75.2.60.5           # Apex domain (load balancer IP)
CNAME   www     your-site.netlify.app
```

**Pointing to Cloudflare Pages:**
- Use Cloudflare DNS — set CNAME to `your-project.pages.dev` (proxied)
- Or add custom domain in Pages dashboard — Cloudflare manages DNS automatically if domain is on Cloudflare

**Pointing to VPS (Caddy/Traefik):**
```
A       @       your.vps.ip
A       www     your.vps.ip
A       api     your.vps.ip
```

**Wildcard:**
```
A       *       your.vps.ip
```

**For Caddy wildcard TLS via Cloudflare DNS API:**
```
CF_API_TOKEN = Cloudflare API token with Zone:DNS:Edit permissions
```

### DNS Propagation

- Changes can take up to 48 hours (TTL-dependent)
- Test with `dig +short example.com` or `nslookup example.com`
- Use low TTL (300s) before making changes; restore after
- Cloudflare proxied records update instantly

---

## Environment Variables — Cross-Platform Strategy

### Principles

1. Never commit secrets to Git
2. Prefer platform-native secret management over .env files in production
3. Use `.env.example` (committed) to document required variables
4. Different values per environment (dev/staging/production) should be explicit, not inferred

### Per-Platform Management

| Platform | Secret Management | Non-Secret Config |
|---|---|---|
| Cloudflare Workers | `wrangler secret put` | `vars` in wrangler.jsonc |
| Cloudflare Pages | Dashboard → Environment Variables | wrangler.toml vars |
| Netlify | `netlify env:set --secret` | netlify.toml `[context.*.environment]` |
| VPS (Caddy) | Docker secrets or `.env` file (not in Git) | Docker environment / Caddyfile `{$VAR}` |

### Local Development

```bash
# .env (never commit — add to .gitignore)
API_KEY=local-dev-key
DATABASE_URL=postgresql://localhost/mydb

# .env.example (commit this)
API_KEY=your-api-key-here
DATABASE_URL=postgresql://localhost/yourdb
```

### Accessing Variables

```typescript
// Node.js / Netlify Functions
process.env.VAR_NAME
Netlify.env.get("VAR_NAME")   // Netlify preferred

// Cloudflare Workers (via binding)
env.VAR_NAME
env.SECRET_NAME

// Vite client-side (public only)
import.meta.env.VITE_VAR_NAME

// Astro client-side (public only)
import.meta.env.PUBLIC_VAR_NAME
```

### Context-Specific Variables (Netlify)

```bash
netlify env:set API_URL "https://api.prod.com" --context production
netlify env:set API_URL "https://api.staging.com" --context deploy-preview
netlify env:set DEBUG "true" --context branch:feature-x
```

### Context-Specific Variables (Cloudflare Workers)

```jsonc
{
  "vars": { "API_URL": "https://api.prod.com" },
  "env": {
    "staging": {
      "vars": { "API_URL": "https://api-staging.com" }
    }
  }
}
```

---

## Folder / Project Structure for Deployment

### Cloudflare Workers (standalone)

```
my-worker/
  src/
    index.ts          # Worker entry point
    handlers/
    lib/
  wrangler.jsonc       # Cloudflare config
  .dev.vars            # Local-only secrets (git-ignored)
  package.json
  tsconfig.json
```

**`.dev.vars`** — local secrets for `wrangler dev` (mirrors production secrets):
```
API_KEY=dev-key-value
DB_SECRET=dev-secret
```

### Cloudflare Pages (full-stack)

```
my-pages-app/
  functions/            # Pages Functions
    api/
      [route].ts
    _middleware.ts
  public/               # Or dist/ after build
  wrangler.toml
  package.json
```

### Netlify (full-stack)

```
my-app/
  netlify/
    functions/          # Serverless functions
      _shared/          # Shared code (non-function)
      api.mts
      background-job-background.mts
      cron-daily.mts
    edge-functions/     # Edge functions
      geo-redirect.ts
  public/               # Or dist/ after build
  netlify.toml
  .env.example
  package.json
```

### VPS with Caddy

```
/srv/myapp/
  docker-compose.yml
  Caddyfile
  .env                  # Production secrets (not in Git)
  app/
    Dockerfile
  ...
```

```
project-repo/
  .env.example          # Committed
  docker-compose.yml    # Committed (no secrets)
  Caddyfile             # Committed
  ...
```

---

## Deployment Strategy Checklist

Before deploying any app, confirm:

- [ ] Platform chosen based on app requirements (see decision tree above)
- [ ] All secrets stored in platform secret manager, not in code
- [ ] `.env.example` documents all required variables
- [ ] DNS records configured and propagated
- [ ] HTTPS configured (auto on Cloudflare/Netlify; Caddy handles automatically)
- [ ] Deploy to preview/staging first, then promote to production
- [ ] Rollback strategy known (Cloudflare: `wrangler rollback`; Netlify: `netlify rollback`; Caddy: restart prior Docker image tag)
- [ ] Health checks configured if using load balancing
- [ ] Build output directory matches platform config (`dist`, `.next`, `public`, etc.)
- [ ] Monorepo base directory set if applicable
- [ ] Framework-specific adapter installed for SSR (Netlify/Cloudflare adapters)

---

## References

| Topic | Source |
|---|---|
| Cloudflare Workers | https://developers.cloudflare.com/workers/ |
| Cloudflare Pages | https://developers.cloudflare.com/pages/ |
| Wrangler CLI | https://developers.cloudflare.com/workers/wrangler/ |
| Cloudflare D1 | https://developers.cloudflare.com/d1/ |
| Cloudflare KV | https://developers.cloudflare.com/kv/ |
| Cloudflare R2 | https://developers.cloudflare.com/r2/ |
| Cloudflare Workers AI | https://developers.cloudflare.com/workers-ai/ |
| Cloudflare changelog | https://developers.cloudflare.com/changelog/ |
| Netlify CLI | https://docs.netlify.com/cli/get-started/ |
| netlify.toml reference | https://docs.netlify.com/configure-builds/file-based-configuration/ |
| Netlify Functions | https://docs.netlify.com/functions/overview/ |
| Netlify Blobs | https://docs.netlify.com/blobs/overview/ |
| Caddyfile docs | https://caddyserver.com/docs/caddyfile |
| Caddy reverse_proxy | https://caddyserver.com/docs/caddyfile/directives/reverse_proxy |
| Caddy automatic HTTPS | https://caddyserver.com/docs/automatic-https |
| Traefik docs | https://doc.traefik.io/traefik/ |
