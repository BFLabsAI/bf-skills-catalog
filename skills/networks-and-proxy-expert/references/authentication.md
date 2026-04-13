# Authentication Reference

Merged from: caddy-reverse-proxy/references/caddy-auth-patterns.md + traefik/references/traefik-middleware-patterns.md (auth sections)

---

## Basic Auth

### Caddy
```
# Generate password hash:
# caddy hash-password --plaintext "mypassword"
# docker run --rm caddy caddy hash-password --plaintext "mypassword"

admin.example.com {
    basicauth /* {
        admin $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvO
        readonly $2a$14$...
    }
    reverse_proxy admin-app:8080
}
```

### Traefik
```yaml
# dynamic/middlewares.yml
http:
  middlewares:
    basicauth:
      basicAuth:
        users:
          - "admin:$apr1$..."    # Generate: htpasswd -nb admin password
        realm: "Protected"
        removeHeader: true       # Strip Authorization header from backend request
```

Apply via label: `- "traefik.http.routers.admin.middlewares=basicauth@file"`

---

## Forward Auth — Authelia (Full SSO + 2FA)

Best for: multi-app, enterprise, OIDC, MFA.

### Docker Compose addition
```yaml
  authelia:
    image: authelia/authelia:4
    restart: unless-stopped
    volumes:
      - ./authelia/config:/config
    networks:
      - proxy
    environment:
      TZ: UTC
```

### Caddy
```
# Auth portal
auth.example.com {
    reverse_proxy authelia:9091
}

# Protected app
app.example.com {
    forward_auth authelia:9091 {
        uri /api/verify?rd=https://auth.example.com
        copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    }
    reverse_proxy app:3000
}
```

### Traefik
```yaml
# dynamic/middlewares.yml
http:
  middlewares:
    forward-auth:
      forwardAuth:
        address: "http://authelia:9091/api/verify"
        trustForwardHeader: true
        authResponseHeaders:
          - "Remote-User"
          - "Remote-Groups"
          - "Remote-Email"
          - "Remote-Name"
```

---

## oauth2-proxy (Google, GitHub, OIDC)

Best for: restricting access to Google Workspace or GitHub org members.

```yaml
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    networks:
      - proxy
    command:
      - --provider=google
      - --email-domain=example.com
      - --upstream=http://app:3000
      - --http-address=0.0.0.0:4180
      - --cookie-secure=true
      - --reverse-proxy=true
    environment:
      OAUTH2_PROXY_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      OAUTH2_PROXY_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
      OAUTH2_PROXY_COOKIE_SECRET: ${COOKIE_SECRET}  # 32-byte random: openssl rand -base64 32
```

### Caddy
```
app.example.com {
    forward_auth oauth2-proxy:4180 {
        uri /oauth2/auth
        copy_headers X-Auth-Request-User X-Auth-Request-Email
    }
    reverse_proxy app:3000
}
```

### Traefik
```yaml
http:
  middlewares:
    oauth2:
      forwardAuth:
        address: "http://oauth2-proxy:4180/oauth2/auth"
        authResponseHeaders:
          - "X-Auth-Request-User"
          - "X-Auth-Request-Email"
```

---

## IP Allowlist

### Caddy
```
internal.example.com {
    @not_internal {
        not remote_ip 10.0.0.0/8 192.168.0.0/16
    }
    respond @not_internal "Forbidden" 403

    reverse_proxy internal-tool:8080
}
```

### Traefik
```yaml
http:
  middlewares:
    ip-whitelist:
      ipWhiteList:
        sourceRange:
          - "10.0.0.0/8"
          - "172.16.0.0/12"
          - "192.168.0.0/16"
        # Behind CDN/proxy, use ipStrategy to get real IP:
        # ipStrategy:
        #   depth: 1
```

---

## Rate Limiting

### Caddy (caddy-ratelimit module)

Requires building with `github.com/mholt/caddy-ratelimit`:
```
api.example.com {
    rate_limit {
        zone api {
            key {remote_host}
            events 100
            window 1m
        }
    }
    reverse_proxy api:8080
}
```

### Traefik (built-in)
```yaml
http:
  middlewares:
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
```

---

## Combining Auth Layers (Both Tools)

**Recommended order:**
1. IP allowlist (fast, zero cost)
2. Rate limit (prevent DoS before auth processing)
3. Authentication (basic auth, forward auth, JWT)
4. Authorization (route by group/role from auth headers)

### Caddy example
```
secure.example.com {
    # 1. IP check
    @blocked not remote_ip 10.0.0.0/8 0.0.0.0/0
    respond @blocked 403

    # 2. SSO (Authelia)
    forward_auth authelia:9091 {
        uri /api/verify
        copy_headers Remote-User Remote-Groups
    }

    # 3. Route by group
    @admin header Remote-Groups *admins*
    handle @admin { reverse_proxy admin-backend:9000 }

    reverse_proxy standard-backend:3000
}
```

### Traefik example
```yaml
# labels
- "traefik.http.routers.secure.middlewares=ip-whitelist@file,rate-limit@file,forward-auth@file"
```

---

## JWT Authentication

### Caddy (caddy-jwt module)
```
api.example.com {
    jwtauth {
        sign_key {env.JWT_SECRET}
        sign_alg HS256
        from_header Authorization
        header_prefix Bearer
    }
    reverse_proxy api:8080
}
```

### Traefik v3 (built-in plugin)
```yaml
http:
  middlewares:
    jwt-verify:
      plugin:
        jwt:
          secret: "{env.JWT_SECRET}"
```
