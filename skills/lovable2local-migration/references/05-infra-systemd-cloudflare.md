# Guia de Infraestrutura, Systemd e Cloudflare Tunnel

Este guia detalha a configuração de processos como serviços Linux nativos e a criação de rotas transparentes no Cloudflare Tunnel.

---

## 1. Unit Systemd para a API Go (`/etc/systemd/system/<app>-api.service`)

```ini
[Unit]
Description=<app> Go REST API
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/<app>/backend
ExecStart=/root/<app>/backend/bin/api
Restart=always
RestartSec=3
Environment="PORT=8014"
Environment="DATABASE_URL=postgres://<user>:<password>@127.0.0.1:5432/<database>?sslmode=disable"
Environment="JWT_SECRET=<sua_chave_secreta_jwt_longa>"
Environment="JWT_EXPIRY=15m"
Environment="REFRESH_EXPIRY=168h"
Environment="GIN_MODE=release"

[Install]
WantedBy=multi-user.target
```

Ativação:
```bash
systemctl daemon-reload
systemctl enable --now <app>-api
systemctl status <app>-api
```

---

## 2. Unit Systemd para o Frontend SSR (`/etc/systemd/system/<app>-web.service`)

```ini
[Unit]
Description=<app> Web SSR Service
After=network.target <app>-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/<app>
ExecStart=/usr/local/bin/node /root/<app>/.output/server/index.mjs
Restart=always
RestartSec=3
Environment="PORT=8015"
Environment="HOST=0.0.0.0"
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
```

Ativação:
```bash
systemctl daemon-reload
systemctl enable --now <app>-web
systemctl status <app>-web
```

---

## 3. Configuração do Ingress no Cloudflare Tunnel (`/etc/cloudflared/config.yml`)

No arquivo `/etc/cloudflared/config.yml`, insira as regras de path-routing **antes da regra catch-all 404**:

```yaml
  # Roteamento da API Go
  - hostname: <subdominio>.r7treinamentos.online
    path: api/*
    service: http://localhost:8014

  # Roteamento do Swagger UI
  - hostname: <subdominio>.r7treinamentos.online
    path: swagger/*
    service: http://localhost:8014

  # Roteamento do Frontend SSR
  - hostname: <subdominio>.r7treinamentos.online
    service: http://localhost:8015

  # catch-all final obrigatório
  - service: http_status:404
```

Reinicie o túnel:
```bash
systemctl restart cloudflared
systemctl status cloudflared
```

---

## 4. Criação do Registro CNAME na Cloudflare via API

Execute o script de automação para registrar o subdomínio:

```bash
CF_TOKEN=$(cat /root/.cf_token)
ZONE_ID="8532ae569da93ecbe31c553e0421b00a"
TUNNEL_ID=$(cat /root/.cf_tunnel_id)
SUBDOMINIO="<subdominio>"

curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{\"type\":\"CNAME\",\"name\":\"${SUBDOMINIO}\",\"content\":\"${TUNNEL_ID}.cfargotunnel.com\",\"proxied\":true,\"ttl\":1}"
```
