# Traefik Configuration Reference

Source: traefik/references/traefik-middleware-patterns.md + traefik/references/traefik-tls.md

---

## Static Config (traefik.yml) — Full Reference

```yaml
api:
  dashboard: true
  insecure: false    # Never true in production — use auth middleware

log:
  level: INFO        # DEBUG | INFO | WARN | ERROR | FATAL | PANIC
  format: json       # json | common

accessLog:
  filePath: /var/log/traefik/access.log
  format: json
  fields:
    defaultMode: keep
    headers:
      defaultMode: drop
      names:
        User-Agent: keep
        Authorization: drop

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
    http:
      middlewares:
        - secure-headers@file  # Apply globally to all HTTPS routes
  metrics:
    address: ":8082"           # Dedicated metrics endpoint

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false    # CRITICAL — always false
    network: traefik-public
  file:
    directory: /etc/traefik/dynamic
    watch: true               # Hot-reload on file changes

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /etc/traefik/acme/acme.json
      httpChallenge:
        entryPoint: web
  letsencrypt-dns:
    acme:
      email: admin@example.com
      storage: /etc/traefik/acme/acme.json
      dnsChallenge:
        provider: cloudflare
        resolvers: ["1.1.1.1:53", "8.8.8.8:53"]

metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    addRoutersLabels: true
    entryPoint: metrics

tracing:
  jaeger:
    samplingServerURL: http://jaeger:5778/sampling
    localAgentHostPort: jaeger:6831
```

---

## Complete Middleware Reference (dynamic/middlewares.yml)

```yaml
http:
  middlewares:

    # --- Security Headers ---
    secure-headers:
      headers:
        forceSTSHeader: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        permissionsPolicy: "camera=(), microphone=(), geolocation=()"
        customResponseHeaders:
          X-Frame-Options: "SAMEORIGIN"
          Server: ""
          X-Powered-By: ""

    # --- Authentication ---
    basicauth:
      basicAuth:
        users:
          - "admin:$apr1$..."   # htpasswd -nb admin password
        realm: "Protected"
        removeHeader: true

    forward-auth:
      forwardAuth:
        address: "http://authelia:9091/api/verify"
        trustForwardHeader: true
        authResponseHeaders:
          - "Remote-User"
          - "Remote-Groups"
          - "Remote-Email"

    # --- Rate Limiting ---
    rate-limit:
      rateLimit:
        average: 100
        period: 1m
        burst: 50
        sourceCriterion:
          ipStrategy:
            depth: 1

    rate-limit-strict:
      rateLimit:
        average: 10
        period: 1m
        burst: 20

    # --- IP Filtering ---
    ip-whitelist:
      ipWhiteList:
        sourceRange:
          - "10.0.0.0/8"
          - "172.16.0.0/12"
          - "192.168.0.0/16"

    # --- CORS ---
    cors:
      headers:
        accessControlAllowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        accessControlAllowHeaders: ["Content-Type", "Authorization", "X-Request-ID"]
        accessControlAllowOriginList: ["https://app.example.com"]
        accessControlMaxAge: 86400
        addVaryHeader: true

    # --- URL Manipulation ---
    strip-api-prefix:
      stripPrefix:
        prefixes: ["/api"]

    redirect-to-https:
      redirectScheme:
        scheme: https
        permanent: true

    redirect-www-to-apex:
      redirectRegex:
        regex: "^https://www\\.example\\.com(.*)"
        replacement: "https://example.com${1}"
        permanent: true

    # --- Compression ---
    compress:
      compress:
        minResponseBodyBytes: 1024

    # --- Circuit Breaker ---
    circuit-breaker:
      circuitBreaker:
        expression: "ResponseCodeRatio(500, 600, 0, 600) > 0.25"
        checkPeriod: 10s
        fallbackDuration: 30s
        recoveryDuration: 10s

    # --- Retry ---
    retry:
      retry:
        attempts: 3
        initialInterval: 100ms
```

---

## Load Balancer (dynamic/routers.yml)

```yaml
http:
  routers:
    myapp:
      rule: "Host(`app.example.com`)"
      entryPoints: [websecure]
      tls:
        certResolver: letsencrypt
      service: myapp
      middlewares: [secure-headers, rate-limit]

  services:
    myapp:
      loadBalancer:
        healthCheck:
          path: /health
          interval: 10s
          timeout: 3s
        servers:
          - url: "http://app1:3000"
          - url: "http://app2:3000"
          - url: "http://app3:3000"
        sticky:
          cookie:
            name: lb_session
            secure: true
            httpOnly: true
        passHostHeader: true
```

---

## Middleware Chaining Order

Apply in this order to avoid logic errors:

```
Request → [ipWhiteList] → [basicAuth/forwardAuth] → [rateLimit] → [secure-headers] → [compress] → Backend
```

Key rules:
- Auth before rate limit: unauthenticated requests consume quota
- `removeHeader: true` on basicAuth strips credentials before reaching backend
- `ipWhiteList` with CDN: configure `ipStrategy.depth` to extract real client IP
- `forwardAuth` adds one RTT per request — cache auth results in Authelia
