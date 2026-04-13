---
name: networks-and-proxy-expert
description: >
  Opinionated reverse proxy and infrastructure routing expert covering Caddy and Traefik: tool
  selection (when to use each), automatic TLS/HTTPS with Let's Encrypt, reverse proxy configuration,
  load balancing, health checks, Docker and Docker Swarm integration, Kubernetes Ingress, WebSocket
  proxying, path and subdomain routing, authentication layers (basic auth, forward auth, oauth2-proxy),
  CORS, security headers, middleware chains, monitoring/metrics, and production directory layouts.
  Use for any reverse proxy setup, TLS automation, routing architecture, infrastructure config, or
  proxy tooling decision.
---

# Networks and Proxy Expert

Opinionated infrastructure routing guide for engineers who need a clear answer — not a list of
options. This skill covers Caddy and Traefik, evaluates them against real use cases, picks winners,
and provides copy-paste-ready configs.

---

## TOOL SELECTION GUIDE (Opinionated)

### Default Choice: Caddy

**Use Caddy for everything except orchestrated container environments.**

Caddy wins on:
- Zero-config TLS — automatic cert issuance and renewal, no `acme.json`, no `chmod 600`
- Human-readable Caddyfile — a junior can read and modify it safely
- Single binary, minimal resource use — 20-40 MB RAM idle
- Reload without restart via admin API or `caddy reload`
- Serves static files, PHP-FPM, and reverse proxy in one tool

**Caddy is the right choice when:**
- You run a VPS or bare-metal server with 1–20 services
- Your services are defined at deploy time (not dynamically registered)
- You want the simplest possible production setup
- You serve static assets, PHP apps, or mixed workloads alongside proxy

### Exception: Traefik for Orchestrated Environments

**Use Traefik when you run Docker Swarm or Kubernetes with dynamic service registration.**

Traefik wins on:
- Zero-config routing from Docker/Swarm/K8s labels and annotations — no manual config per service
- Auto-discovery of new containers as they start — no reload needed
- Native Prometheus metrics and distributed tracing out of the box
- Production-grade Swarm/K8s integration (rolling deploys, weighted routing)

**Traefik is the right choice when:**
- You run Docker Swarm or Kubernetes
- New services register themselves (CI/CD deploys new containers and routing just works)
- You need distributed tracing (Jaeger, Zipkin) at the proxy layer
- You manage 20+ services in a dynamic environment

### Summary Table

| Factor | Caddy | Traefik |
|--------|-------|---------|
| Config style | Human-readable Caddyfile | Labels / YAML / TOML |
| Auto-discovery | No | Yes (Docker, Swarm, K8s) |
| TLS automation | Simpler (built-in) | Powerful (ACME resolvers) |
| Resource use | ~20-40 MB idle | ~50-100 MB idle |
| Dashboard | No built-in | Yes (auth-gated) |
| Middleware | Via modules + Caddyfile | Rich built-in middleware |
| Best for | VPS, static setups | Swarm, K8s, dynamic |

**Conflict resolution note:** Both tools require pinning versions — never use `latest` in production.
This is consistent guidance, not a conflict.

---

## Recommended Infrastructure Directory Layout

### Caddy (VPS / Single-Host)

```
/opt/myproject/
├── Caddyfile                # All virtual hosts, routing, TLS
├── docker-compose.yml       # Caddy + all services
├── .env                     # Secrets (CF_API_TOKEN, etc.)
└── volumes/
    ├── caddy-data/          # TLS certs live here — MUST be a named volume
    ├── caddy-config/        # Caddy runtime config
    └── caddy-logs/          # Per-site access logs
```

Docker Compose volumes:
```yaml
volumes:
  caddy-data:      # Named volume — DO NOT delete
  caddy-config:
```

### Traefik (Docker Swarm)

```
/opt/traefik/
├── traefik.yml              # Static config (EntryPoints, providers, cert resolvers)
├── dynamic/                 # Dynamic file provider — hot-reloaded
│   ├── middlewares.yml      # All middleware definitions
│   ├── routers.yml          # Non-Docker routers / static services
│   └── tls.yml              # TLS options, manual certs
├── acme/
│   └── acme.json            # Let's Encrypt state (chmod 600 required)
├── docker-compose.yml       # Traefik stack definition
└── .env                     # Secrets
```

---

## TLS / HTTPS

All TLS guidance applies to both tools unless noted.

### ACME / Let's Encrypt

**HTTP-01 Challenge** (default, requires port 80 public):
- Caddy: automatic — set `email` in global block, done
- Traefik: configure `httpChallenge` in `certificatesResolvers`

**DNS-01 Challenge** (wildcards, servers behind firewall):
- Caddy: build with `xcaddy` + DNS provider module; use `tls { dns cloudflare {env.CF_API_TOKEN} }`
- Traefik: configure `dnsChallenge` + provider env vars (e.g. `CF_DNS_API_TOKEN`)

**Wildcard certificates** always require DNS-01 challenge regardless of tool.

**Staging (testing):**
- Caddy: `acme_ca https://acme-staging-v02.api.letsencrypt.org/directory` in global block
- Traefik: `caServer: https://acme-staging-v02.api.letsencrypt.org/directory`

### Internal / Dev TLS

- Caddy: `tls internal` — uses Caddy's local CA. Run `caddy trust` to install root cert.
- Traefik: use file provider with self-signed cert or local CA cert.

For details and full configs → `references/tls-guide.md`

---

## Routing Patterns

### Path-Based Routing

**Caddy:**
```
api.example.com {
    handle /users/* { reverse_proxy users-svc:8081 }
    handle_path /products/* { reverse_proxy products-svc:8082 }  # strips prefix
    handle { reverse_proxy app:3000 }
}
```

**Traefik (Docker labels):**
```yaml
- "traefik.http.routers.api.rule=Host(`api.example.com`) && PathPrefix(`/users`)"
```

### Subdomain Routing

**Caddy (wildcard):**
```
*.example.com {
    tls { dns cloudflare {env.CF_API_TOKEN} }
    @app host app.example.com
    handle @app { reverse_proxy app:3000 }
    @api host api.example.com
    handle @api { reverse_proxy api:8080 }
}
```

**Traefik (per-container):** Each container declares its own `Host()` rule via labels.

For full routing configs → `references/routing-patterns.md`

---

## Docker Integration

### Caddy with Docker

Caddy does NOT auto-discover containers. All routing is in the Caddyfile.
Services must be on the same Docker network as Caddy.

```yaml
# docker-compose.yml
services:
  caddy:
    image: caddy:2.8-alpine
    ports: ["80:80", "443:443", "443:443/udp"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    networks: [proxy]

  myapp:
    image: myapp:latest
    networks: [proxy]  # Caddy references by service name
    # No port exposure needed

networks:
  proxy:
volumes:
  caddy-data:
  caddy-config:
```

### Traefik with Docker Swarm

Traefik auto-discovers containers. Each service configures itself via labels.

```yaml
# Required on Traefik stack
services:
  traefik:
    deploy:
      placement:
        constraints: [node.role == manager]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

# On each backend service
    deploy:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
        - "traefik.http.routers.myapp.entrypoints=websecure"
        - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
        - "traefik.http.services.myapp.loadbalancer.server.port=3000"
```

For complete Docker Compose files → `references/docker-setup.md`

---

## Load Balancing

Both tools support: round-robin (default), least-conn, random, IP hash, URI hash, sticky cookie.

**Caddy:**
```
reverse_proxy backend1:3000 backend2:3000 {
    lb_policy least_conn
    health_uri /health
    health_interval 10s
    max_fails 3
    fail_duration 30s
    lb_policy cookie { name lb_sticky; secret {env.LB_SECRET} }
}
```

**Traefik:**
```yaml
http:
  services:
    myapp:
      loadBalancer:
        healthCheck: { path: /health, interval: 10s, timeout: 3s }
        servers:
          - url: "http://app1:3000"
          - url: "http://app2:3000"
        sticky:
          cookie: { name: lb_session, secure: true, httpOnly: true }
```

---

## Authentication

| Method | Caddy | Traefik |
|--------|-------|---------|
| Basic auth | `basicauth` directive | `basicAuth` middleware |
| Forward auth (Authelia, oauth2-proxy) | `forward_auth` directive | `forwardAuth` middleware |
| IP allowlist | `remote_ip` matcher + `respond 403` | `ipWhiteList` middleware |
| JWT | caddy-jwt module (xcaddy) | Built-in (v3) |

For auth configs → `references/authentication.md`

---

## Security Headers (Both Tools)

Canonical header set for production:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
# Remove:
Server: (empty)
X-Powered-By: (remove)
```

**Caddy:**
```
header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server
    -X-Powered-By
}
```

**Traefik (middleware in dynamic/middlewares.yml):**
```yaml
http:
  middlewares:
    secure-headers:
      headers:
        forceSTSHeader: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        contentTypeNosniff: true
        customResponseHeaders:
          X-Frame-Options: "SAMEORIGIN"
          Server: ""
```

---

## Monitoring

**Caddy:** Per-site JSON logging. No built-in metrics endpoint. Integrate with Loki/Promtail for log aggregation.

```
log {
    output file /var/log/caddy/app.log { roll_size 100mb; roll_keep 10 }
    format json
}
```

**Traefik:** Native Prometheus metrics and tracing.
```yaml
# traefik.yml
metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    addRoutersLabels: true

tracing:
  jaeger:
    samplingServerURL: http://jaeger:5778/sampling
```

---

## Rules and Invariants

- **Never use `latest` in production** — pin both Caddy and Traefik to a specific version tag
- **Traefik**: `exposedByDefault: false` always — opt-in routing only, never auto-expose all containers
- **Traefik**: `acme.json` must be `chmod 600` — Traefik refuses or logs errors otherwise
- **Traefik**: dashboard must have auth middleware — never expose unauthenticated in production
- **Caddy**: always set `email` in global block — required for Let's Encrypt account registration
- **Caddy**: always mount `data` directory as a named Docker volume — certs are stored there
- **Caddy**: never expose admin API (port 2019) publicly — bind to localhost only
- **Both**: use DNS-01 challenge for wildcard certs — HTTP-01 cannot issue wildcards
- **Both**: use staging ACME URL first to avoid rate limits while testing
- **Both**: forward `X-Real-IP` and `X-Forwarded-Proto` to backends
- **Both**: strip `Server` header from responses

---

## When to Use This Skill

- Deciding between Caddy and Traefik for a new project
- Configuring a reverse proxy for Docker, Docker Swarm, or bare-metal
- Setting up TLS with Let's Encrypt (HTTP-01 or DNS-01)
- Routing requests by path, subdomain, or header
- Load balancing across multiple backend instances
- Adding authentication (basic auth, forward auth, oauth2-proxy)
- Configuring security headers and CORS
- Setting up Traefik middleware chains or Caddy named matchers
- Integrating Traefik with Prometheus/Jaeger for observability
- Production infrastructure layout and directory structure
- Blue-green deployments and zero-downtime config reloads
