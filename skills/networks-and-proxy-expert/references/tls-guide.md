# TLS / HTTPS Reference

Merged from: traefik/references/traefik-tls.md + caddy/references/caddy-tls.md

---

## How Automatic TLS Works (Both Tools)

Both Caddy and Traefik implement the ACME protocol (RFC 8555) to:
1. Generate a key pair per domain
2. Complete a challenge (HTTP-01 or DNS-01) to prove domain ownership
3. Receive a signed certificate from Let's Encrypt (or another CA)
4. Store the cert and renew it automatically before expiry

**Caddy** renews at 30 days before expiry, checks every 12h.  
**Traefik** renews at 30 days before expiry, polls every 24h.

---

## HTTP-01 Challenge (Default)

Requirements: port 80 publicly reachable.

### Caddy
```
{
    email admin@example.com
    # That's it. TLS is automatic for all site blocks with real hostnames.
}

example.com {
    reverse_proxy localhost:3000
}
```

### Traefik
```yaml
# traefik.yml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /etc/traefik/acme/acme.json
      httpChallenge:
        entryPoint: web   # Must be EntryPoint on port 80

# On router (via Docker label or file provider):
# traefik.http.routers.myapp.tls.certresolver=letsencrypt
```

---

## DNS-01 Challenge (Wildcards + Private Servers)

Requirements: DNS provider API credentials.

### Caddy (DNS-01)

Build Caddy with the DNS module:
```dockerfile
FROM caddy:2.8-builder AS builder
RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare

FROM caddy:2.8-alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Caddyfile:
```
{
    email admin@example.com
}

*.example.com, example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }
    # ... routing
}
```

Supported providers (via xcaddy): cloudflare, route53, digitalocean, namecheap, duckdns, and more.

### Traefik (DNS-01)

```yaml
# traefik.yml
certificatesResolvers:
  letsencrypt-dns:
    acme:
      email: admin@example.com
      storage: /etc/traefik/acme/acme.json
      dnsChallenge:
        provider: cloudflare
        resolvers:
          - "1.1.1.1:53"
          - "8.8.8.8:53"
```

Environment variables (Cloudflare):
```bash
CF_API_EMAIL=admin@example.com
CF_DNS_API_TOKEN=your-cloudflare-api-token
```

For wildcard via Docker label:
```yaml
- "traefik.http.routers.myapp.tls.domains[0].main=example.com"
- "traefik.http.routers.myapp.tls.domains[0].sans=*.example.com"
- "traefik.http.routers.myapp.tls.certresolver=letsencrypt-dns"
```

---

## Internal / Development TLS

### Caddy — Local CA
```
myapp.local {
    tls internal    # Caddy generates and signs cert with its local CA
    reverse_proxy localhost:3000
}
```

Install Caddy's root CA to trust it:
```bash
caddy trust
# Docker:
docker exec caddy caddy trust
```

### Traefik — Manual Self-Signed
```yaml
# dynamic/tls.yml
tls:
  certificates:
    - certFile: /etc/traefik/certs/self-signed.crt
      keyFile: /etc/traefik/certs/self-signed.key
```

---

## TLS Protocol Options

### Caddy
```
example.com {
    tls {
        protocols tls1.2 tls1.3
        ciphers TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        curves x25519 p384
    }
}
```

### Traefik
```yaml
# dynamic/tls.yml
tls:
  options:
    modern:
      minVersion: VersionTLS13
    intermediate:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305
      sniStrict: true
```

Apply to a router:
```yaml
# Docker label
- "traefik.http.routers.myapp.tls.options=modern@file"
```

---

## Cert Storage

| | Caddy | Traefik |
|---|---|---|
| Location | `/data/caddy/certificates/` | `acme.json` (single file) |
| Docker volume | Named volume at `/data` | Named volume at `/etc/traefik/acme` |
| Permissions | Managed by Caddy | `chmod 600 acme.json` **required** |
| Format | Individual .crt + .key files | JSON blob (all certs) |

```bash
# Traefik — initial setup (run before first start)
touch /opt/traefik/acme/acme.json
chmod 600 /opt/traefik/acme/acme.json
```

---

## Staging / Rate Limit Testing

Always test with staging before production. Let's Encrypt rate limits: 5 cert requests per domain per week.

**Caddy:**
```
{
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
    email admin@example.com
}
```

**Traefik:**
```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      caServer: https://acme-staging-v02.api.letsencrypt.org/directory
```

---

## Common TLS Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| 429 Too Many Requests | LE rate limit | Use staging ACME URL |
| Port 80 not accessible | Firewall / NAT | Open port 80 for HTTP-01 |
| Wildcard cert not working | HTTP-01 challenge used | Switch to DNS-01 |
| Cert lost after restart | Data volume not persisted | Use named Docker volume |
| Traefik: cert not renewed | `acme.json` not writable | `chmod 600 acme.json` |
| `tls internal` not trusted | Caddy CA not installed | Run `caddy trust` |
| Too slow renewal | High cert count | Increase ACME DNS propagation wait time |
