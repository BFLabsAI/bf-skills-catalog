---
name: uazapi-whatsapp-expert
description: This skill should be used when the user asks to "integrate with uazapi", "call the Uazapi API", "configure Uazapi webhooks", "send WhatsApp messages with Uazapi", "manage Uazapi instances", "use Uazapi SSE", "build against uazapi-openapi-spec.yaml", or needs help with Uazapi WhatsApp, chatbot, campaign, contact, group, or business endpoints.
version: 0.1.0
---

# Uazapi Skill

Use this skill to work against the local Uazapi OpenAPI documentation bundled with the repository. Treat the skill as the entry point for understanding authentication, endpoint families, operational caveats, and where to find the full schema.

## Purpose

Translate requests about Uazapi into concrete implementation work without re-discovering the API surface from scratch. Use the local OpenAPI spec as the source of truth, then narrow to the smallest relevant endpoint family before writing code, curl examples, docs, workflows, or automations.

## Workflow

1. Read `references/auth-and-conventions.md` first.
2. Read `references/domain-map.md` to identify the right endpoint family.
3. Read `references/integration-playbook.md` before writing implementation code, automations, or examples.
4. Open `references/uazapi-openapi-spec.yaml` only for the relevant paths and schemas instead of loading the whole file at once.
5. Confirm which authentication model applies before building requests:
   - Default API calls use the `token` header.
   - Administrative endpoints use the `admintoken` header.
   - `/sse` is an exception and expects `token` in query parameters.
6. Prefer the `api` server subdomain for production-style examples unless the task is explicitly about demo or free environments.
7. Preserve Uazapi field names and payload shapes exactly as documented, including mixed casing and legacy names.
8. Call out loop-prevention, async queue semantics, and connection-state risks whenever work involves webhooks, SSE, chatbots, or message automation.

## Default Assumptions

- Base URL format: `https://{subdomain}.uazapi.com`
- Server variable `subdomain` supports `free` and `api`
- Instance operations usually assume an existing instance token unless the task is explicitly about provisioning
- Instance state matters: `disconnected`, `connecting`, and `connected` materially change what can succeed

## High-Signal Conventions

Apply these conventions proactively:

- Use `admintoken` only for administrative lifecycle/global endpoints such as instance creation, listing all instances, and global webhook management.
- Use the instance `token` header for normal instance-scoped operations.
- Treat `/webhook` simple mode as the default recommendation.
- Include `"excludeMessages": ["wasSentByApi"]` in webhook recommendations unless the user clearly needs self-originated events and has loop protection.
- Note that `/webhook` GET returns an array even for a single configured webhook.
- Note that `/sse` disables OpenAPI security and moves auth into query parameters.
- Treat `async: true` on send endpoints as queue acceptance rather than delivery confirmation.
- Treat group destinations as JIDs such as `@g.us`, not always raw phone numbers.
- Verify whether an endpoint is instance-scoped, admin-scoped, or global before generating code.
- Preserve payload quirks such as fields like `plataform` instead of silently correcting them.

## Endpoint Selection Guide

Use these families to narrow work quickly:

- Instance lifecycle and configuration: init, connect, disconnect, status, proxy, privacy, presence, profile, admin fields
- Messaging and content delivery: text, media, contact, location, presence, status, menus, carousel, payment, PIX
- Message operations: download, search, mark read, react, delete, edit
- Group and community management: create, join, leave, list, invite, metadata, participants, permissions
- Event ingestion: instance webhook, global webhook, SSE
- AI/chatbot platform: agent, trigger, knowledge, function, chatbot settings
- Campaigns and broadcast sender: simple, advanced, edit, clear, list folders, list messages
- Chat/contact CRM actions: block, labels, archive, read, mute, pin, find, lead editing, contacts, chat details, contact add/remove
- Business features: profile, categories, catalog
- Integrations: Chatwoot config

## Implementation Rules

- Start with the smallest relevant path set from the OpenAPI spec.
- Extract example payloads from the spec when the user asks for working requests or SDK generation.
- Surface required headers, query parameters, and request body shape explicitly in generated examples.
- Include status/error handling when building automation around connection lifecycle, webhook setup, or campaigns.
- For send flows, distinguish enqueue success from delivery success and recommend follow-up verification when needed.
- Mention demo/free server restrictions when recommending admin/global endpoints.
- For webhook and SSE consumers, document event filtering and reconnect/duplicate handling.

## Additional Resources

Reference files:

- `references/auth-and-conventions.md` - Authentication model, server behavior, and important quirks
- `references/domain-map.md` - Endpoint families and selection guidance
- `references/integration-playbook.md` - Implementation defaults, failure modes, and output patterns
- `references/uazapi-openapi-spec.yaml` - Full local OpenAPI documentation copied from repository context

## Output Expectations

When using this skill:

- Produce exact request examples when the user asks for integration help
- Cite the specific path and auth model being used
- Mention operational caveats that could cause loops, auth errors, or state-dependent failures
- Keep implementation advice scoped to the relevant Uazapi feature area instead of summarizing the entire API
