# Docker Setup Reference

Merged from: traefik/references/traefik-docker-compose.md + caddy/references/caddyfile-patterns.md
(Docker Compose sections)

---

## Caddy — Docker Compose (VPS / Single Host)

The canonical Caddy + Docker setup for a VPS running multiple services.

```yaml
# docker-compose.yml
version: "3.8"

services:
  caddy:
    image: caddy:2.8-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"    # HTTP/3 / QUIC
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data         # CRITICAL: certs stored here
      - caddy-config:/config
      - caddy-logs:/var/log/caddy
    environment:
      CF_API_TOKEN: ${CF_API_TOKEN:-}  # Only needed for DNS challenge
    networks:
      - proxy

  app:
    image: myapp:latest
    restart: unless-stopped
    networks:
      - proxy         # Reachable by Caddy via service name "app"
      - internal      # NOT reachable from outside

  api:
    image: myapi:latest
    restart: unless-stopped
    networks:
      - proxy
      - internal

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    networks:
      - internal      # DB on internal network only — no Caddy access
    volumes:
      - db-data:/var/lib/postgresql/data

networks:
  proxy:       # Caddy + backend services share this
  internal:    # Backend-to-backend + DB; no external access

volumes:
  caddy-data:    # DO NOT delete — TLS certs live here
  caddy-config:
  caddy-logs:
  db-data:
```

### Initial setup commands (Caddy)
```bash
# Validate config before starting
docker run --rm -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile caddy:2.8-alpine caddy validate --config /etc/caddy/Caddyfile

# Start everything
docker compose up -d

# Reload Caddy config after changes (no downtime)
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
# Or via admin API:
curl -X POST http://localhost:2019/load \
  -H "Content-Type: text/caddyfile" \
  --data-binary @Caddyfile
```

---

## Caddy with Custom Modules (xcaddy)

For DNS challenge or JWT/rate-limit modules:

```dockerfile
# Dockerfile.caddy
FROM caddy:2.8-builder AS builder
RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/mholt/caddy-ratelimit

FROM caddy:2.8-alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

```yaml
# docker-compose.yml override
services:
  caddy:
    build:
      context: .
      dockerfile: Dockerfile.caddy
```

---

## Traefik — Docker Compose (Single Host)

```yaml
# docker-compose.yml
version: "3.8"

services:
  traefik:
    image: traefik:v3.1
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./dynamic:/etc/traefik/dynamic:ro
      - traefik-certs:/etc/traefik/acme
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.middlewares=basicauth@file"

  myapp:
    image: myapp:latest
    restart: unless-stopped
    networks:
      - traefik-public
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
      - "traefik.http.routers.myapp.middlewares=secure-headers@file"
      - "traefik.http.services.myapp.loadbalancer.server.port=3000"
      - "traefik.http.services.myapp.loadbalancer.healthcheck.path=/health"

networks:
  traefik-public:
    external: true    # Created separately (see setup commands)
  internal:
    internal: true

volumes:
  traefik-certs:
```

### Initial setup commands (Traefik)
```bash
# Create shared network (run once)
docker network create traefik-public

# Create acme.json with correct permissions (required)
mkdir -p acme
touch acme/acme.json
chmod 600 acme/acme.json

# Start Traefik
docker compose up -d traefik

# Verify
docker compose logs traefik -f

# Debug — list active routers
curl -s http://localhost:8080/api/http/routers | jq '.[].rule'
```

---

## Traefik — Docker Swarm Stack

```yaml
# traefik-stack.yml
version: "3.8"

services:
  traefik:
    image: traefik:v3.1
    command:
      - "--providers.swarm=true"
      - "--providers.swarm.exposedbydefault=false"
      - "--providers.swarm.network=traefik-public"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/acme/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--api.dashboard=true"
    ports:
      - target: 80
        published: 80
        mode: host
      - target: 443
        published: 443
        mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certs:/acme
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
        - "traefik.http.routers.dashboard.entrypoints=websecure"
        - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
        - "traefik.http.routers.dashboard.service=api@internal"
        - "traefik.http.routers.dashboard.middlewares=basicauth@file"

networks:
  traefik-public:
    external: true

volumes:
  traefik-certs:
```

```bash
# Deploy Traefik stack
docker stack deploy -c traefik-stack.yml traefik

# Deploy app stack (each app declares its own labels)
docker stack deploy -c app-stack.yml myapp
```

### App stack pattern
```yaml
# app-stack.yml
version: "3.8"

services:
  web:
    image: myapp:v1.2.3
    networks:
      - traefik-public
    deploy:
      replicas: 3
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
        - "traefik.http.routers.myapp.entrypoints=websecure"
        - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
        - "traefik.http.services.myapp.loadbalancer.server.port=3000"
        - "traefik.http.services.myapp.loadbalancer.healthcheck.path=/health"

networks:
  traefik-public:
    external: true
```
