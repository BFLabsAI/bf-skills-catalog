---
name: email-specialist
description: >
  Unified email skill covering: Resend API (transactional sending, inbound email, domains, contacts,
  broadcasts, automations, segments, templates, API keys, logs, events, topics), Resend webhook setup
  and signature verification (Express, Next.js, FastAPI), React Email template development (components,
  Tailwind styling, visual editor, i18n, patterns, testing), Brevo CRM and email platform integration
  (contacts, deals, campaigns, SMS, Membrane CLI), email best practices (deliverability, SPF/DKIM/DMARC,
  compliance — CAN-SPAM/GDPR/CASL, transactional vs marketing email types, email capture, list
  management, sending reliability, bounce/complaint handling).
  Always use this skill when the user mentions Resend, React Email, Brevo, email webhooks, email
  deliverability, or email compliance — it contains critical gotchas (idempotency keys, raw body
  requirement for webhook verification, pixelBasedPreset for Tailwind, template variable syntax,
  List-Unsubscribe header requirements) that prevent common production issues.
license: MIT
version: "2.0.0"
tags:
  - email
  - resend
  - react-email
  - webhooks
  - brevo
  - deliverability
  - compliance
  - best-practices
inputs:
  - name: RESEND_API_KEY
    description: Resend API key for sending and receiving emails. Get yours at https://resend.com/api-keys
    required: true
  - name: RESEND_WEBHOOK_SECRET
    description: Webhook signing secret for verifying event payloads. Found in the Resend dashboard under Webhooks after creating an endpoint.
    required: false
references:
  - sending/overview.md
  - sending/single-email-examples.md
  - sending/batch-email-examples.md
  - sending/best-practices.md
  - sending/email-management.md
  - receiving.md
  - templates.md
  - webhooks.md
  - webhooks-guide.md
  - domains.md
  - contacts.md
  - broadcasts.md
  - api-keys.md
  - logs.md
  - contact-properties.md
  - segments.md
  - topics.md
  - automations.md
  - events.md
  - installation.md
  - fetch-all-templates.mjs
  - COMPONENTS.md
  - STYLING.md
  - PATTERNS.md
  - SENDING.md
  - EDITOR.md
  - I18N.md
  - react-email-tests.md
  - brevo-guide.md
  - compliance.md
  - deliverability.md
  - email-capture.md
  - email-types.md
  - list-management.md
  - marketing-emails.md
  - sending-reliability.md
  - transactional-email-catalog.md
  - transactional-emails.md
  - webhooks-events.md
---

# Email Specialist

Covers the full email stack: **Resend API**, **Resend webhooks**, **React Email templates**, **Brevo CRM/email platform**, and **email best practices** (deliverability, compliance, list management, reliability).

---

## Decision Tree — What Do You Need?

```
Are you sending or receiving email?
├── Sending → What kind?
│   ├── Transactional (receipts, confirmations, notifications)
│   │   ├── Single email → Quick Send (Node.js / Python below)
│   │   ├── Batch (2-100 emails) → Single vs Batch table below
│   │   └── With React components → React Email section below
│   └── Marketing campaign → Broadcasts (see references/broadcasts.md)
│
├── Receiving → Inbound Email Setup → references/receiving.md
│
├── Webhooks (delivery events, inbound) → Webhooks section below
│
├── Building email templates (HTML/React) → React Email section below
│
├── Brevo CRM / campaigns / SMS → Part 4: Brevo below
│
├── Deliverability / spam issues / DNS auth → Part 5: Best Practices below
│
└── Compliance (GDPR, CAN-SPAM, CASL) → references/compliance.md
```

---

## Part 1: Resend API

### Quick Send — Node.js

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send(
  {
    from: 'Acme <onboarding@resend.dev>',
    to: ['delivered@resend.dev'],
    subject: 'Hello World',
    html: '<p>Email body here</p>',
  },
  { idempotencyKey: `welcome-email/${userId}` }
);

if (error) {
  console.error('Failed:', error.message);
  return;
}
console.log('Sent:', data.id);
```

**Key gotcha:** The Resend Node.js SDK does NOT throw exceptions — it returns `{ data, error }`. Always check `error` explicitly instead of using try/catch for API errors.

### Quick Send — Python

```python
import resend
import os

resend.api_key = os.environ["RESEND_API_KEY"]

email = resend.Emails.send({
    "from": "Acme <onboarding@resend.dev>",
    "to": ["delivered@resend.dev"],
    "subject": "Hello World",
    "html": "<p>Email body here</p>",
}, idempotency_key=f"welcome-email/{user_id}")
```

### Single vs Batch

| Choose | When |
|--------|------|
| **Single** (`POST /emails`) | 1 email, needs attachments, needs scheduling |
| **Batch** (`POST /emails/batch`) | 2-100 distinct emails, no attachments, no scheduling |

Batch is atomic — if one email fails validation, the entire batch fails. Batch does NOT support attachments or `scheduled_at`.

### Idempotency Keys (Critical for Retries)

| Key Facts | |
|-----------|---|
| **Format (single)** | `<event-type>/<entity-id>` (e.g., `welcome-email/user-123`) |
| **Format (batch)** | `batch-<event-type>/<batch-id>` (e.g., `batch-orders/batch-456`) |
| **Expiration** | 24 hours |
| **Max length** | 256 characters |
| **Same key + same payload** | Returns original response without resending |
| **Same key + different payload** | Returns 409 error |

### Quick Receive — Inbound Email (Node.js)

```typescript
export async function POST(req: Request) {
  const payload = await req.text(); // Must use raw text, not req.json()

  const event = resend.webhooks.verify({
    payload,
    headers: {
      'svix-id': req.headers.get('svix-id'),
      'svix-timestamp': req.headers.get('svix-timestamp'),
      'svix-signature': req.headers.get('svix-signature'),
    },
    secret: process.env.RESEND_WEBHOOK_SECRET,
  });

  if (event.type === 'email.received') {
    // Webhook has metadata only — call API for body
    const { data: email } = await resend.emails.receiving.get(
      event.data.email_id
    );
    console.log(email.text);
  }

  return new Response('OK', { status: 200 });
}
```

**Key gotcha:** Webhook payloads do NOT contain the email body. You must call `resend.emails.receiving.get()` separately.

### Resend Reference Map

| Task | Reference |
|------|-----------|
| Send a single email | [sending/overview.md](references/sending/overview.md) |
| Send batch emails | [sending/batch-email-examples.md](references/sending/batch-email-examples.md) |
| SDK examples (Node, Python, Go, cURL) | [sending/single-email-examples.md](references/sending/single-email-examples.md) |
| Idempotency, retries, error handling | [sending/best-practices.md](references/sending/best-practices.md) |
| Get, list, reschedule, cancel emails | [sending/email-management.md](references/sending/email-management.md) |
| Receive inbound emails | [receiving.md](references/receiving.md) |
| Manage templates (CRUD, variables) | [templates.md](references/templates.md) |
| Set up webhooks (events, verification) | [webhooks.md](references/webhooks.md) |
| Manage domains (create, verify, DNS) | [domains.md](references/domains.md) |
| Manage contacts (CRUD, properties) | [contacts.md](references/contacts.md) |
| Send broadcasts (marketing campaigns) | [broadcasts.md](references/broadcasts.md) |
| Manage API keys | [api-keys.md](references/api-keys.md) |
| View API request logs | [logs.md](references/logs.md) |
| Define contact properties | [contact-properties.md](references/contact-properties.md) |
| Manage segments (contact groups) | [segments.md](references/segments.md) |
| Manage topics (subscriptions) | [topics.md](references/topics.md) |
| Create automations | [automations.md](references/automations.md) |
| Define and send events (automation triggers) | [events.md](references/events.md) |
| Install SDK (8+ languages) | [installation.md](references/installation.md) |

### SDK Version Requirements

| Language | Package | Min Version | Install |
|----------|---------|-------------|---------|
| Node.js | `resend` | >= 6.9.2 | `npm install resend` |
| Python | `resend` | >= 2.21.0 | `pip install resend` |
| Go | `resend-go/v3` | >= 3.1.0 | `go get github.com/resend/resend-go/v3` |
| Ruby | `resend` | >= 1.0.0 | `gem install resend` |
| PHP | `resend/resend-php` | >= 1.1.0 | `composer require resend/resend-php` |
| Rust | `resend-rs` | >= 0.20.0 | `cargo add resend-rs` |
| Java | `resend-java` | >= 4.11.0 | See [installation.md](references/installation.md) |
| .NET | `Resend` | >= 0.2.1 | `dotnet add package Resend` |

### Common Mistakes — Resend API

| # | Mistake | Fix |
|---|---------|-----|
| 1 | **Retrying without idempotency key** | Always include idempotency key — prevents duplicate sends on retry |
| 2 | **Not verifying webhook signatures** | Always verify with `resend.webhooks.verify()` |
| 3 | **Template variable name mismatch** | Variable names are case-sensitive. Use triple mustache `{{{VAR}}}` syntax |
| 4 | **Expecting email body in webhook payload** | Webhooks contain metadata only — call `resend.emails.receiving.get()` for body |
| 5 | **Using try/catch for Node.js SDK errors** | SDK returns `{ data, error }` — check `error` explicitly |
| 6 | **Using batch for emails with attachments** | Batch doesn't support attachments — use single sends instead |
| 7 | **Testing with fake emails (test@gmail.com)** | Use `delivered@resend.dev` — fake addresses bounce and hurt reputation |
| 8 | **Sending with draft template** | Templates must be published before sending — call `.publish()` first |
| 9 | **`html` + `template` in same send call** | Mutually exclusive — remove `html`/`text`/`react` when using template |
| 10 | **MX record not lowest priority for inbound** | Ensure Resend's MX has the lowest number (highest priority) |
| 11 | **403 when sending from `resend.dev`** | The default `onboarding@resend.dev` is a sandbox — only delivers to your Resend account email. Verify your own domain first |
| 12 | **403 domain mismatch** | The `from` address domain must exactly match a verified domain |
| 13 | **Calling Resend API from the browser** | The API doesn't support CORS — always call from server-side |
| 14 | **401 `restricted_api_key`** | A sending-only API key was used on a non-sending endpoint. Create a full-access key |

### Error Handling Quick Reference

| Code | Action |
|------|--------|
| 400, 422 | Fix request parameters, don't retry |
| 401 | Check API key — `restricted_api_key` means sending-only key used on non-sending endpoint |
| 403 | Verify domain ownership — sandbox restriction, from domain mismatch, or unverified domain |
| 409 | Idempotency conflict — use new key or fix payload |
| 429 | Rate limited — retry with exponential backoff (default: 2 req/s) |
| 500 | Server error — retry with exponential backoff |

### Testing Addresses

| Address | Result |
|---------|--------|
| `delivered@resend.dev` | Simulates successful delivery |
| `bounced@resend.dev` | Simulates hard bounce |
| `complained@resend.dev` | Simulates spam complaint |

### Webhook Event Types

| Event | Trigger |
|-------|---------|
| `email.sent` | API request successful |
| `email.delivered` | Reached recipient's mail server |
| `email.bounced` | Permanently rejected (hard bounce) |
| `email.complained` | Recipient marked as spam |
| `email.opened` / `email.clicked` | Recipient engagement |
| `email.delivery_delayed` | Soft bounce, Resend retries |
| `email.received` | Inbound email arrived |
| `domain.*` / `contact.*` | Domain/contact changes |

---

## Part 2: Resend Webhooks

For complete webhook reference including setup, verification details, and all framework implementations, see [references/webhooks-guide.md](references/webhooks-guide.md).

### Express Handler (Quick Reference)

```javascript
const { Resend } = require('resend');
const express = require('express');

const resend = new Resend(process.env.RESEND_API_KEY);
const app = express();

// CRITICAL: Use express.raw() — Resend needs the raw body for signature verification
app.post('/webhooks/resend',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    try {
      const event = resend.webhooks.verify({
        payload: req.body.toString(),
        headers: {
          id: req.headers['svix-id'],
          timestamp: req.headers['svix-timestamp'],
          signature: req.headers['svix-signature'],
        },
        webhookSecret: process.env.RESEND_WEBHOOK_SECRET
      });

      switch (event.type) {
        case 'email.delivered':
          // confirm delivery
          break;
        case 'email.bounced':
          // remove from list
          break;
        case 'email.received':
          // fetch body separately
          const { data: email } = await resend.emails.receiving.get(event.data.email_id);
          break;
      }

      res.json({ received: true });
    } catch (err) {
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);
```

**Key gotcha:** Raw body is mandatory. If you apply `express.json()` globally, register the webhook route **before** the global middleware.

### Working Examples

Full implementations with tests are in the `examples/` directory:

- [`examples/express/`](examples/express/) — Express.js with Resend SDK verification + Mocha tests
- [`examples/nextjs/`](examples/nextjs/) — Next.js App Router with Vitest tests
- [`examples/fastapi/`](examples/fastapi/) — Python FastAPI with manual Svix verification + pytest

### Local Development

```bash
brew install hookdeck/hookdeck/hookdeck
hookdeck listen 3000 --path /webhooks/resend
```

---

## Part 3: React Email

Build HTML email templates using React components — a modern, component-based approach that works across all major email clients.

### Installation

```sh
npx create-email@latest
cd react-email-starter
npm install
npm run dev
```

The dev server runs at localhost:3000 with a preview interface for templates in the `emails` folder.

**Adding to an existing project:**
```json
{
  "scripts": {
    "email": "email dev --dir emails --port 3000"
  }
}
```

### Basic Email Template

```tsx
import {
  Html, Head, Preview, Body, Container, Heading, Text, Button,
  Tailwind, pixelBasedPreset
} from '@react-email/components';

interface WelcomeEmailProps {
  name: string;
  verificationUrl: string;
}

export default function WelcomeEmail({ name, verificationUrl }: WelcomeEmailProps) {
  return (
    <Html lang="en">
      <Tailwind config={{ presets: [pixelBasedPreset] }}>
        <Head />
        <Body className="bg-gray-100 font-sans">
          <Preview>Welcome - Verify your email</Preview>
          <Container className="max-w-xl mx-auto p-5">
            <Heading className="text-2xl text-gray-800">Welcome!</Heading>
            <Text className="text-base text-gray-800">
              Hi {name}, thanks for signing up!
            </Text>
            <Button
              href={verificationUrl}
              className="bg-blue-600 text-white px-5 py-3 rounded block text-center no-underline box-border"
            >
              Verify Email
            </Button>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}

WelcomeEmail.PreviewProps = {
  name: 'John Doe',
  verificationUrl: 'https://example.com/verify/abc123'
} satisfies WelcomeEmailProps;
```

### Behavioral Guidelines

- When iterating, only update what the user asked for — keep the rest intact.
- Never use media queries — most email clients don't support them. Use stacked mobile-first layouts.
- Never write `{{variableName}}` directly in component JSX — it breaks TypeScript. Use `{props.variableName}` in JSX; if the user explicitly wants mustache syntax, put it only in `PreviewProps`.

### Essential Components

**Core Structure:**
- `Html` — Root wrapper with `lang` attribute
- `Head` — Meta elements, styles, fonts (must be **inside** `<Tailwind>`)
- `Body` — Main content wrapper
- `Container` — Outermost centering wrapper (built-in `max-width: 37.5em`). Use only once per email.
- `Section` — Interior content blocks (no built-in max-width)
- `Row` & `Column` — Multi-column layouts (never use flexbox or CSS grid)
- `Tailwind` — Enables Tailwind CSS utility classes

**Content:**
- `Preview` — Inbox preview text, always first inside `<Body>`
- `Heading` — h1-h6 headings
- `Text` — Paragraphs
- `Button` — Styled link buttons (always include `box-border`)
- `Link` — Hyperlinks
- `Img` — Images (absolute URLs only; no SVG/WEBP)
- `Hr` — Horizontal dividers (always specify `border-solid` or other border type)

**Specialized:**
- `CodeBlock` — Syntax-highlighted code (always wrap in `<div className="overflow-auto">`)
- `CodeInline` — Inline code
- `Markdown` — Render markdown
- `Font` — Custom web fonts

See [references/COMPONENTS.md](references/COMPONENTS.md) for complete component documentation.

### Required Classes (Never Omit)

| Component | Required Class | Why |
|-----------|---------------|-----|
| `Button` | `box-border` | Prevents padding from overflowing the button width |
| `Hr` / any border | `border-solid` (or `border-dashed`, etc.) | Email clients don't inherit border type |
| Single-side borders | `border-none` + the side | Resets default borders on other sides |

### Styling Rules

- Use `Tailwind` with `pixelBasedPreset` — email clients don't support `rem`. Import `pixelBasedPreset` from `@react-email/components` (NOT from `@react-email/tailwind`)
- Never use flexbox or grid — use `Row`/`Column` components or tables
- Never use responsive class prefixes (`sm:`, `md:`, `lg:`, `xl:`) — limited email client support
- Never use theme selectors (`dark:`, `light:`) — not supported
- Never use SVG or WEBP images — warn users about rendering issues
- `<Head />` must be **inside** `<Tailwind>`, not outside
- `<Preview>` must be the **first element** inside `<Body>`
- Only include props in `PreviewProps` that the component actually uses

See [references/STYLING.md](references/STYLING.md) for comprehensive styling documentation.

### Before Writing Code

When a user requests an email template, ask clarifying questions FIRST if they haven't provided:

1. **Brand colors** — Ask for primary brand color (hex code)
2. **Logo** — Ask if they have a logo file and its format (PNG/JPG only — warn if SVG/WEBP)
3. **Style preference** — Professional, casual, or minimal tone
4. **Production URL** — Where will static assets be hosted in production?

### Static Files and Images

Local images must go in the `static` folder inside your emails directory:

```
project/
├── emails/
│   ├── welcome.tsx
│   └── static/           ← images go here
│       └── logo.png
```

**Dev vs Production pattern:**

```tsx
const baseURL = process.env.NODE_ENV === "production"
  ? "https://cdn.example.com"  // user's production CDN
  : "";                         // dev server serves /static automatically

<Img src={`${baseURL}/static/logo.png`} alt="Logo" width="150" height="50" />
```

Never hardcode `http://localhost:3000` as the base URL.

### Rendering

```tsx
import { render } from '@react-email/components';

const html = await render(<WelcomeEmail name="John" verificationUrl="..." />);
const text = await render(<WelcomeEmail name="John" verificationUrl="..." />, { plainText: true });
```

### Sending with Resend SDK

```tsx
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: 'Acme <onboarding@resend.dev>',
  to: ['user@example.com'],
  subject: 'Welcome to Acme',
  react: <WelcomeEmail name="John" verificationUrl="https://example.com/verify" />
});
```

The Node SDK automatically handles both HTML and plain-text rendering when `react` is passed.

### CLI Commands

| Command | Description |
|---------|-------------|
| `email dev --dir <path> --port <port>` | Start the preview development server |
| `email build --dir <path>` | Build the preview app for production |
| `email start` | Run the built preview app |
| `email export --outDir <path> --pretty --plainText --dir <path>` | Export templates to static HTML |
| `email resend setup` | Connect the CLI to your Resend account |
| `email resend reset` | Remove the stored Resend API key |

### React Email Reference Map

| Topic | Reference |
|-------|-----------|
| Component reference (all components with props) | [references/COMPONENTS.md](references/COMPONENTS.md) |
| Styling guide (typography, layout, dark mode, brand) | [references/STYLING.md](references/STYLING.md) |
| Common patterns (password reset, orders, notifications, newsletters, invitations) | [references/PATTERNS.md](references/PATTERNS.md) |
| Sending (Resend, Nodemailer, SendGrid) | [references/SENDING.md](references/SENDING.md) |
| Visual email editor (`@react-email/editor`) | [references/EDITOR.md](references/EDITOR.md) |
| Internationalization (next-intl, react-i18next, react-intl) | [references/I18N.md](references/I18N.md) |
| Test scenarios and compliance verification | [references/react-email-tests.md](references/react-email-tests.md) |

### Email Design Best Practices

1. **Test across email clients** — Gmail, Outlook, Apple Mail, Yahoo Mail
2. **Keep max-width around 600px**, test on mobile
3. **Use absolute image URLs** — host on reliable CDN, always include `alt` text
4. **Provide plain text version** — required for accessibility
5. **Keep file size under 102KB** — Gmail clips larger emails
6. **Add proper TypeScript types** — define interfaces for all email props
7. **Include `.PreviewProps`** — for development testing
8. **Use verified domains** — for production `from` addresses

### Email Editor (Visual)

React Email includes a visual editor (`@react-email/editor`) that can be embedded in your app. Built on TipTap/ProseMirror, produces email-ready HTML.

Quick example:

```tsx
import { EmailEditor, type EmailEditorRef } from '@react-email/editor';
import '@react-email/editor/themes/default.css';
import { useRef } from 'react';

export function MyEditor() {
  const ref = useRef<EmailEditorRef>(null);

  return (
    <EmailEditor
      ref={ref}
      content="<p>Start typing...</p>"
      theme="basic"
    />
  );
}
```

See [references/EDITOR.md](references/EDITOR.md) for full documentation.

### Internationalization

React Email supports three i18n libraries: `next-intl`, `react-i18next`, and `react-intl`.

Key rules:
- Make `locale` a required prop on every email component
- Set `lang={locale}` on the `Html` element
- For RTL languages (Arabic, Hebrew): `dir={isRTL ? 'rtl' : 'ltr'}`
- Translate the email `subject` line, not just the body

See [references/I18N.md](references/I18N.md) for complete setup guides for all three libraries.

---

## Part 4: Brevo

Brevo (formerly Sendinblue) is a marketing automation and CRM platform for email campaigns, SMS, and contact/deal management.

Official docs: https://developers.brevo.com/

### What Brevo Covers

- **Email Campaigns** — bulk email to contact lists
- **SMS Campaigns** — SMS messaging
- **Contacts & Lists** — CRM contacts, attributes, lists
- **Transactions** — transactional email and SMS
- **Templates** — email and SMS templates
- **CRM** — Deals, Companies, Tasks (Pipelines)

### Setup via Membrane CLI

Brevo integration uses [Membrane](https://getmembrane.com) for authenticated API access — no manual API key management.

```bash
# Install the CLI
npm install -g @membranehq/cli

# First-time login
membrane login --tenant
# Headless: copy the URL, then: membrane login complete <code>

# Find the Brevo connector
membrane search brevo --elementType=connector --json
# Note the connector ID from output.items[0].element?.id

# Create a connection
membrane connect --connectorId=CONNECTOR_ID --json
# User completes browser auth. Note the connectionId.

# Check existing connections
membrane connection list --json
```

### Running Actions

```bash
# List available actions
membrane action list --intent=QUERY --connectionId=CONNECTION_ID --json

# Run an action
membrane action run --connectionId=CONNECTION_ID ACTION_ID --json

# Run with input parameters
membrane action run --connectionId=CONNECTION_ID ACTION_ID --json --input '{"key": "value"}'
```

### Popular Actions

| Name | Key | Description |
|------|-----|-------------|
| List Contacts | list-contacts | Get all contacts with optional filtering |
| List Deals | list-deals | Get all deals with optional filtering |
| List Companies | list-companies | Get all companies with optional filtering |
| List Tasks | list-tasks | Get all tasks with optional filtering |
| List Lists | list-lists | Get all contact lists |
| Get Contact | get-contact | Get a contact by email, ID, or external ID |
| Get Deal | get-deal | Get details of a specific deal |
| Get Company | get-company | Get details of a specific company |
| Create Contact | create-contact | Create a new contact |
| Create Deal | create-deal | Create a new deal in Brevo CRM |
| Create Company | create-company | Create a new company |
| Create Task | create-task | Create a new task |
| Create List | create-list | Create a new contact list |
| Update Contact | update-contact | Update an existing contact |
| Update Deal | update-deal | Update an existing deal |
| Delete Contact | delete-contact | Delete a contact from Brevo |

### Proxy Requests (Direct API Access)

When available actions don't cover your use case, send requests through the Membrane proxy — auth headers are injected automatically:

```bash
membrane request CONNECTION_ID /path/to/endpoint
```

| Flag | Description |
|------|-------------|
| `-X, --method` | HTTP method (GET, POST, PUT, PATCH, DELETE). Defaults to GET |
| `-H, --header` | Add a header (repeatable) |
| `-d, --data` | Request body |
| `--json` | Send JSON body, set `Content-Type: application/json` |
| `--query` | Query-string parameter (repeatable) |
| `--pathParam` | Path parameter (repeatable) |

### Brevo Best Practices

- **Prefer Membrane actions** — pre-built actions handle auth, pagination, and edge cases; saves tokens vs raw API calls
- **Discover before building** — run `membrane action list --intent=QUERY` before writing custom calls
- **Never ask users for API keys** — use `membrane connect` instead; Membrane manages the full auth lifecycle

See [references/brevo-guide.md](references/brevo-guide.md) for full Brevo reference.

---

## Part 5: Email Best Practices

### Architecture Overview

```
[User] → [Email Form] → [Validation] → [Double Opt-In]
                                              ↓
                                    [Consent Recorded]
                                              ↓
[Suppression Check] ←──────────────[Ready to Send]
        ↓
[Idempotent Send + Retry] ──────→ [Email API]
                                       ↓
                              [Webhook Events]
                                       ↓
              ┌────────┬────────┬─────────────┐
              ↓        ↓        ↓             ↓
         Delivered  Bounced  Complained  Opened/Clicked
                       ↓        ↓
              [Suppression List Updated]
                       ↓
              [List Hygiene Jobs]
```

### Deliverability — SPF / DKIM / DMARC

Gmail, Yahoo, and Microsoft require authentication. Unauthenticated emails will be rejected or spam-filtered.

| Record | Purpose | DNS Type |
|--------|---------|----------|
| SPF | Authorizes servers that can send for your domain | TXT |
| DKIM | Cryptographic signature proving email authenticity | TXT |
| DMARC | Policy for SPF/DKIM failures + reporting | TXT |

**DMARC rollout:** `p=none` (monitor) → `p=quarantine; pct=25` → `p=reject`

**Verify your setup:**
```bash
dig TXT yourdomain.com +short          # SPF
dig TXT resend._domainkey.yourdomain.com +short  # DKIM
dig TXT _dmarc.yourdomain.com +short   # DMARC
```

**Emails going to spam? Check in order:**
1. Authentication (SPF, DKIM, DMARC)
2. `List-Unsubscribe` header (required by Gmail/Yahoo since Feb 2024)
3. Sender reputation (blacklists, complaint rates)
4. Content
5. Sending patterns (sudden volume spikes)

See [references/deliverability.md](references/deliverability.md) for full guide including IP warming schedule and diagnostic tools.

### Compliance — CAN-SPAM / GDPR / CASL

| Law | Region | Key Requirement | Max Penalty |
|-----|--------|-----------------|-------------|
| CAN-SPAM | US | Opt-out, physical address, non-deceptive headers | $53k/email |
| GDPR | EU | Explicit opt-in, right to deletion, immediate unsubscribe | €20M or 4% revenue |
| CASL | Canada | Express consent, honor unsubscribe within 10 days | $10M CAD |

**List-Unsubscribe header (required for bulk senders):**
```typescript
headers: {
  'List-Unsubscribe': '<https://example.com/unsubscribe>',
  'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
}
```

**Best practice:** Follow the most restrictive requirements (GDPR) to ensure compliance across all regions.

See [references/compliance.md](references/compliance.md) for full per-law requirements and consent management guidance.

### Transactional vs Marketing Emails

| | Transactional | Marketing |
|--|--------------|-----------|
| **Definition** | Facilitates a user-initiated transaction | Promotional, informational, not tied to a transaction |
| **Opt-in required** | No (with limitations) | Yes — explicit consent |
| **Unsubscribe** | Not required | Required |
| **Examples** | Password reset, OTP, order confirmation | Newsletter, promotions, announcements |
| **Sending subdomain** | `t.yourdomain.com` (recommended) | `m.yourdomain.com` (recommended) |

**Key rule:** Keep transactional and marketing separate — both infrastructure (subdomains) and list management.

See [references/email-types.md](references/email-types.md) for legal distinctions by jurisdiction and hybrid email guidance.

### Transactional Email Catalog

Plan which emails your app needs before writing any code. Quick reference by app type:

| App Type | Essential Emails |
|----------|-----------------|
| Auth-focused | Email verification, password reset, OTP/2FA, security alerts |
| Newsletter/content | Email verification, password reset, welcome, subscription confirmation |
| E-commerce | Email verification, password reset, order confirmation, shipping, invoice, payment failed |
| SaaS/subscription | All auth emails + subscription confirmation, renewal notice, payment failed, invoice |
| Fintech | All auth emails + transaction confirmations, compliance notices (PHI minimal) |
| Developer tools | Auth emails + API key notifications, usage alerts, subscription/payment emails |

See [references/transactional-email-catalog.md](references/transactional-email-catalog.md) for full catalog with content requirements per email type.

### Email Capture

- **Double opt-in for all marketing emails** — confirms deliverability, satisfies GDPR/CASL
- Validate server-side (format, DNS/MX records, disposable email detection)
- Use unchecked consent checkboxes with specific language
- Rate-limit verification sends: 3/hour per email, 60-second minimum between resends

See [references/email-capture.md](references/email-capture.md) for form design, error handling, and verification email patterns.

### Sending Reliability

- **Always use idempotency keys** — deterministic keys based on the business event (e.g., `order-confirm-${orderId}`)
- **Retry on 5xx and 429 only** — exponential backoff with jitter (1s → 2s → 4s → 8s)
- **Use a queue for critical emails** — survives restarts, handles retries, provides audit trail
- Keys expire after 24 hours — complete all retries within this window

See [references/sending-reliability.md](references/sending-reliability.md) for retry patterns, queue architecture, and timeout configuration.

### List Management

- **Hard bounce → suppress immediately, permanently** (address invalid)
- **Complaint → suppress immediately, permanently** (legal requirement)
- **Soft bounce → suppress after 3 failures** (revisit after 30-90 days)
- **Check suppression before every send**
- **Re-engagement before removal:** Identify inactive (45-90 days), send re-engagement email, remove non-responders after 14-30 days

See [references/list-management.md](references/list-management.md) for suppression schema, hygiene automation, and data retention requirements.

### Best Practices Reference Map

| Need | Reference |
|------|-----------|
| Fix spam issues, set up SPF/DKIM/DMARC | [deliverability.md](references/deliverability.md) |
| CAN-SPAM, GDPR, CASL requirements | [compliance.md](references/compliance.md) |
| Transactional vs marketing decision | [email-types.md](references/email-types.md) |
| Plan which emails your app needs | [transactional-email-catalog.md](references/transactional-email-catalog.md) |
| Password reset, OTP, confirmation design | [transactional-emails.md](references/transactional-emails.md) |
| Build newsletter signup, validate emails | [email-capture.md](references/email-capture.md) |
| Newsletter, promotions, consent | [marketing-emails.md](references/marketing-emails.md) |
| Retry logic, idempotency, error handling | [sending-reliability.md](references/sending-reliability.md) |
| Bounce/complaint webhooks, idempotent processing | [webhooks-events.md](references/webhooks-events.md) |
| Bounces, complaints, suppression lists | [list-management.md](references/list-management.md) |

---

## Part 6: Cross-Cutting Concerns

### API Key Setup

Store in environment variable — never hardcode:

```bash
export RESEND_API_KEY=re_xxxxxxxxx
```

Get your key at [resend.com/api-keys](https://resend.com/api-keys).

### Detect Project Language

Check for: `package.json` (Node.js), `requirements.txt`/`pyproject.toml` (Python), `go.mod` (Go), `Gemfile` (Ruby), `composer.json` (PHP), `Cargo.toml` (Rust), `pom.xml`/`build.gradle` (Java), `*.csproj` (.NET).

### Send + Receive Together

Auto-replies, forwarding, or any receive-then-send workflow:
1. Set up inbound domain first (see [receiving.md](references/receiving.md))
2. Set up sending (see [sending/overview.md](references/sending/overview.md))
3. Note: batch sending does NOT support attachments or scheduling — use single sends when forwarding with attachments

### Domain Warm-up

New domains must gradually increase sending volume. Day 1 limit: ~150 emails (new domain) or ~1,000 (existing domain). See the warm-up schedule in [sending/overview.md](references/sending/overview.md) and [deliverability.md](references/deliverability.md).

### Suppression List

Resend automatically suppresses hard-bounced and spam-complained addresses. Sending to suppressed addresses fires the `email.suppressed` webhook event instead of attempting delivery. Manage in Dashboard → Suppressions.

### AI Agent Inbox

If your system processes untrusted email content and takes actions (refunds, database changes, forwarding), install the `agent-email-inbox` skill — this applies whether or not AI is involved.

---

## Reference Guide Index

### Resend API

| File | Contents |
|------|----------|
| [sending/overview.md](references/sending/overview.md) | Single send, warm-up schedule, domain setup |
| [sending/single-email-examples.md](references/sending/single-email-examples.md) | SDK examples in Node, Python, Go, cURL |
| [sending/batch-email-examples.md](references/sending/batch-email-examples.md) | Batch send examples and constraints |
| [sending/best-practices.md](references/sending/best-practices.md) | Idempotency, retries, error handling |
| [sending/email-management.md](references/sending/email-management.md) | Get, list, reschedule, cancel emails |
| [receiving.md](references/receiving.md) | Inbound email setup and processing |
| [templates.md](references/templates.md) | Template CRUD, variables, publishing |
| [webhooks.md](references/webhooks.md) | Webhook event types and setup |
| [webhooks-guide.md](references/webhooks-guide.md) | Verification, framework implementations |
| [domains.md](references/domains.md) | Domain creation, verification, DNS records |
| [contacts.md](references/contacts.md) | Contact CRUD |
| [broadcasts.md](references/broadcasts.md) | Marketing campaign broadcasts |
| [api-keys.md](references/api-keys.md) | API key management |
| [logs.md](references/logs.md) | Request log access |
| [contact-properties.md](references/contact-properties.md) | Custom contact properties |
| [segments.md](references/segments.md) | Contact segmentation |
| [topics.md](references/topics.md) | Subscription topics |
| [automations.md](references/automations.md) | Automation workflows |
| [events.md](references/events.md) | Event definitions and triggers |
| [installation.md](references/installation.md) | SDK installation (8+ languages) |

### React Email

| File | Contents |
|------|----------|
| [COMPONENTS.md](references/COMPONENTS.md) | All components with props |
| [STYLING.md](references/STYLING.md) | Tailwind, typography, layout, dark mode |
| [PATTERNS.md](references/PATTERNS.md) | Password reset, orders, notifications, newsletters |
| [SENDING.md](references/SENDING.md) | Resend, Nodemailer, SendGrid integration |
| [EDITOR.md](references/EDITOR.md) | Visual email editor (`@react-email/editor`) |
| [I18N.md](references/I18N.md) | i18n with next-intl, react-i18next, react-intl |
| [react-email-tests.md](references/react-email-tests.md) | Test scenarios and compliance verification |

### Brevo

| File | Contents |
|------|----------|
| [brevo-guide.md](references/brevo-guide.md) | Full Brevo integration reference (Membrane CLI, actions, proxy) |

### Email Best Practices

| File | Contents |
|------|----------|
| [deliverability.md](references/deliverability.md) | SPF/DKIM/DMARC, IP warming, reputation, troubleshooting |
| [compliance.md](references/compliance.md) | CAN-SPAM, GDPR, CASL, List-Unsubscribe, consent records |
| [email-types.md](references/email-types.md) | Transactional vs marketing, legal distinctions, hybrid emails |
| [transactional-email-catalog.md](references/transactional-email-catalog.md) | Per-app-type email combinations, full content catalog |
| [transactional-emails.md](references/transactional-emails.md) | Subject lines, content structure, mobile-first design |
| [email-capture.md](references/email-capture.md) | Validation, double opt-in, form design, rate limiting |
| [marketing-emails.md](references/marketing-emails.md) | Opt-in, unsubscribe, content structure, segmentation |
| [sending-reliability.md](references/sending-reliability.md) | Idempotency, retry logic, queuing, timeouts |
| [webhooks-events.md](references/webhooks-events.md) | Event processing patterns, bounce/complaint handlers, idempotency |
| [list-management.md](references/list-management.md) | Suppression lists, hygiene automation, data retention |

---

## Resources

- [Resend Documentation](https://resend.com/docs)
- [Resend API Reference](https://resend.com/docs/api-reference)
- [Resend Dashboard](https://resend.com/emails)
- [React Email Documentation](https://react.email/docs/llms.txt)
- [React Email GitHub](https://github.com/resend/react-email)
- [Email Client CSS Support](https://www.caniemail.com)
- [Brevo API Documentation](https://developers.brevo.com)
- [Membrane CLI](https://getmembrane.com)
- [Google Postmaster Tools](https://postmaster.google.com)
- [MXToolbox Blacklist Check](https://mxtoolbox.com/blacklists.aspx)
