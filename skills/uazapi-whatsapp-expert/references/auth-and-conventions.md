# Uazapi Auth And Conventions

## Base URL

- Base URL pattern: `https://{subdomain}.uazapi.com`
- Available server variables in the spec: `free`, `api`
- Prefer `api` in production-oriented examples

## Authentication

Default security in the OpenAPI document is:

```yaml
security:
  - token: []
```

Interpretation:

- Most instance-scoped endpoints require a `token` header
- Administrative endpoints explicitly override security and require `admintoken`
- `/sse` declares `security: []` and expects `token` as a query parameter instead

## Admin-Scoped Endpoints

Admin token use is explicitly documented for endpoints such as:

- `/instance/init`
- `/instance/all`
- `/instance/updateAdminFields`
- `/globalwebhook`

Treat admin/global lifecycle work as a separate auth path from instance operations.

## Instance Lifecycle

The spec documents these states:

- `disconnected`
- `connecting`
- `connected`

Reflect state assumptions in integrations. Many operations are only meaningful once the instance is connected.

## High-Signal Behavior Notes

- Creating an instance returns a new instance token; retain it for subsequent instance-scoped requests.
- Free/demo environments may disable or restrict some admin/global capabilities.
- The spec strongly recommends WhatsApp Business accounts because normal WhatsApp accounts can be unstable for integrations.
- Some field names are legacy or unconventional, such as `plataform`; preserve them exactly.
- Webhook examples explicitly recommend `excludeMessages: ["wasSentByApi"]` to prevent automation loops.
- `/webhook` GET returns an array, even when a single webhook exists.
- SSE uses a persistent connection and requires event filtering strategy and reconnect handling.

## Working Style

When generating code or docs:

- State the required auth mechanism first
- State whether the path is admin-scoped, instance-scoped, or global
- Use payload keys and enums exactly as written in the spec
- Mention loop-prevention whenever message events can trigger outbound sends
