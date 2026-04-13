# Routing Patterns Reference

Merged from: caddy-reverse-proxy/references/caddy-proxy-patterns.md + traefik SKILL.md routing content

---

## Caddy Routing Patterns

### Path-Based Routing

```
api.example.com {
    # handle: mutual exclusion — first match wins
    # handle_path: strips matched prefix before forwarding
    
    # Keep path prefix
    handle /users/* {
        reverse_proxy users-service:8081
    }
    
    # Strip /products prefix before forwarding to backend
    handle_path /products/* {
        reverse_proxy product-service:8082
    }
    
    handle /orders/* {
        reverse_proxy order-service:8083
    }
    
    # Fallback
    respond "Not found" 404
}
```

### Subdomain Routing (Wildcard)

```
{
    email admin@example.com
}

*.example.com {
    tls { dns cloudflare {env.CF_API_TOKEN} }
    
    @app host app.example.com
    handle @app { reverse_proxy app:3000 }
    
    @api host api.example.com
    handle @api { reverse_proxy api:8080 }
    
    @grafana host grafana.example.com
    handle @grafana { reverse_proxy grafana:3000 }
    
    handle { respond "Service not found" 404 }
}
```

### WebSocket Routing

```
app.example.com {
    # Explicit WebSocket routing (optional — Caddy handles WS transparently)
    @ws {
        header Connection *Upgrade*
        header Upgrade websocket
    }
    reverse_proxy @ws ws-backend:8080
    
    # HTTP traffic
    reverse_proxy http-backend:3000
}
```

### Multi-Service VPS (Full Production Caddyfile)

```
{
    email admin@example.com
    admin localhost:2019

    servers {
        trusted_proxies static 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    }
}

# Main app
app.example.com {
    reverse_proxy app:3000

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        -Server
    }

    encode gzip zstd
    log {
        output file /var/log/caddy/app.log { roll_size 100mb; roll_keep 10 }
        format json
    }
}

# API with CORS
api.example.com {
    @cors_preflight method OPTIONS
    handle @cors_preflight {
        header Access-Control-Allow-Origin "https://app.example.com"
        header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
        header Access-Control-Allow-Headers "Content-Type, Authorization"
        header Access-Control-Max-Age "86400"
        respond 204
    }

    header Access-Control-Allow-Origin "https://app.example.com"

    reverse_proxy api:8080 {
        health_uri /healthz
        health_interval 10s
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_down -Server
    }
}

# Static assets with cache headers
static.example.com {
    root * /var/www/static
    file_server
    encode gzip zstd

    @assets path *.css *.js *.png *.jpg *.webp *.svg *.woff2
    header @assets Cache-Control "public, max-age=31536000, immutable"
    @html path *.html
    header @html Cache-Control "no-cache"
}

# Admin (auth-gated)
admin.example.com {
    basicauth {
        admin $2a$14$hashed_password_here
    }
    reverse_proxy admin-app:9000
}

# Monitoring
grafana.example.com {
    reverse_proxy grafana:3000 {
        header_up Host {upstream_hostport}
    }
}

# Redirect www → apex
www.example.com {
    redir https://example.com{uri} permanent
}
```

---

## Traefik Routing Patterns

### Static Config (traefik.yml)

```yaml
api:
  dashboard: true
  insecure: false

log:
  level: INFO

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false    # ALWAYS false
    network: traefik-public
  file:
    directory: /etc/traefik/dynamic
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /etc/traefik/acme/acme.json
      httpChallenge:
        entryPoint: web
```

### Docker Labels (Container Routing)

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
  - "traefik.http.routers.myapp.entrypoints=websecure"
  - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
  - "traefik.http.routers.myapp.middlewares=secure-headers@file,rate-limit@file"
  - "traefik.http.services.myapp.loadbalancer.server.port=3000"
  - "traefik.http.services.myapp.loadbalancer.healthcheck.path=/health"
```

### Path-Based Routing (Traefik)

```yaml
# Per-container labels — each service declares its own path prefix
labels:
  - "traefik.http.routers.users.rule=Host(`api.example.com`) && PathPrefix(`/users`)"
  - "traefik.http.routers.users.middlewares=strip-users-prefix@file"

# dynamic/middlewares.yml — strip the prefix before forwarding
http:
  middlewares:
    strip-users-prefix:
      stripPrefix:
        prefixes: ["/users"]
```

### File Provider Routing (Non-Docker Services)

```yaml
# dynamic/routers.yml
http:
  routers:
    external-api:
      rule: "Host(`legacy.example.com`)"
      entryPoints: [websecure]
      tls:
        certResolver: letsencrypt
      service: external-api
      middlewares: [secure-headers]

  services:
    external-api:
      loadBalancer:
        servers:
          - url: "http://10.0.1.50:8080"
          - url: "http://10.0.1.51:8080"
        healthCheck:
          path: /health
          interval: 10s
```

### Traefik Middleware Chain (dynamic/middlewares.yml)

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
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customResponseHeaders:
          X-Frame-Options: "SAMEORIGIN"
          Server: ""

    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        sourceCriterion:
          ipStrategy:
            depth: 1

    compress:
      compress: {}

    cors:
      headers:
        accessControlAllowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        accessControlAllowHeaders: ["Content-Type", "Authorization"]
        accessControlAllowOriginList: ["https://app.example.com"]
        accessControlMaxAge: 86400
        addVaryHeader: true

    redirect-to-https:
      redirectScheme:
        scheme: https
        permanent: true
```

---

## Blue-Green Deployment (Caddy)

```bash
#!/bin/bash
# deploy.sh — zero-downtime swap

# Start green container
docker compose up -d app-green

# Wait for health
until curl -sf http://localhost:3001/health; do
    echo "Waiting for green..."
    sleep 2
done

# Swap upstream via admin API (no restart, no downtime)
curl -X POST http://localhost:2019/load \
  -H "Content-Type: text/caddyfile" \
  --data-binary @- <<'EOF'
app.example.com {
    reverse_proxy app-green:3001 {
        health_uri /health
    }
    header { -Server }
}
EOF

echo "Traffic switched to green"
sleep 10

# Stop blue
docker compose stop app-blue
echo "Blue stopped. Deploy complete."
```

---

## On-Demand TLS (Caddy — SaaS Customer Domains)

For platforms where each customer has their own domain:

```
{
    on_demand_tls {
        ask http://my-app/verify-domain   # Must return 200 for valid domains
        interval 2m
        burst 5
    }
}

:443 {
    tls {
        on_demand
    }
    reverse_proxy my-app:3000
}
```
