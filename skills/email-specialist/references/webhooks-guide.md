# Resend Webhooks Guide

Consolidated reference covering webhook concepts, setup, signature verification, and framework implementations.

---

## What Are Resend Webhooks?

Resend uses webhooks to notify your application when email events occur. Instead of polling the API for delivery status, Resend sends HTTP POST requests to your configured endpoint URL whenever something happens—like an email being delivered, bounced, or opened.

Resend uses [Svix](https://www.svix.com/) as its webhook delivery infrastructure, which means webhook signatures use the Svix format (`svix-id`, `svix-timestamp`, `svix-signature` headers).

---

## Event Types

### Outbound Email Events

| Event | Triggered When | Common Use Cases |
|-------|----------------|------------------|
| `email.sent` | Email accepted by Resend | Update send status, start delivery tracking |
| `email.delivered` | Email delivered to recipient's mail server | Confirm delivery, update records |
| `email.delivery_delayed` | Delivery is temporarily delayed | Monitor delivery health |
| `email.bounced` | Email bounced (permanent or temporary) | Remove invalid addresses, notify sender |
| `email.complained` | Recipient marked as spam | Unsubscribe user, prevent future sends |
| `email.opened` | Recipient opened the email | Track engagement metrics |
| `email.clicked` | Recipient clicked a link | Track engagement, attribution |

### Inbound Email Events

| Event | Triggered When | Common Use Cases |
|-------|----------------|------------------|
| `email.received` | Email arrives at your receiving domain | Support tickets, email parsing, forwarding |

**Critical:** The `email.received` webhook contains metadata only (sender, recipient, subject, attachment info). To get the email body and attachment content, call the Resend API separately:

```javascript
// Get email body
const { data: email } = await resend.emails.receiving.get(event.data.email_id);
console.log(email.html);  // HTML body
console.log(email.text);  // Plain text body

// Get attachments
const { data: attachments } = await resend.emails.receiving.attachments.list({
  emailId: event.data.email_id
});
```

---

## Event Payload Structure

All Resend webhook events share a common structure:

```json
{
  "type": "email.delivered",
  "created_at": "2024-02-22T23:41:12.126Z",
  "data": {
    "email_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "from": "sender@example.com",
    "to": ["recipient@example.com"],
    "subject": "Welcome to our service",
    "created_at": "2024-02-22T23:41:10.000Z"
  }
}
```

### Inbound Email Payload (`email.received`)

```json
{
  "type": "email.received",
  "created_at": "2024-02-22T23:41:12.126Z",
  "data": {
    "email_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "from": "customer@example.com",
    "to": ["support@yourdomain.com"],
    "cc": [],
    "bcc": [],
    "subject": "Question about my order",
    "attachments": [
      {
        "id": "att_abc123",
        "filename": "receipt.pdf",
        "content_type": "application/pdf"
      }
    ]
  }
}
```

---

## Delivery Guarantees

- Webhooks are delivered at least once — you may receive duplicates
- Failed deliveries are retried with exponential backoff
- Use `email_id` for idempotent processing
- Resend stores events even if your webhook is temporarily down

---

## Setup

### Prerequisites

- Resend account with API access
- Your application's webhook endpoint URL (must be HTTPS in production)

### Via Resend Dashboard

1. Go to [Resend Dashboard → Webhooks](https://resend.com/webhooks)
2. Click **Add Webhook**
3. Enter your endpoint URL (e.g., `https://your-app.com/webhooks/resend`)
4. Select the events you want to receive
5. Click **Add**
6. Click on your new webhook to view details
7. Copy the **Signing Secret** (`whsec_...`)

### Recommended Events

| Use Case | Events |
|----------|--------|
| Email tracking | `email.sent`, `email.delivered`, `email.bounced`, `email.complained` |
| Inbound email processing | `email.received` |
| Engagement tracking | `email.opened`, `email.clicked` |

### Environment Variables

```bash
RESEND_API_KEY=re_xxxxx           # From Resend dashboard
RESEND_WEBHOOK_SECRET=whsec_xxxxx # From webhook endpoint settings
```

Never commit secrets to version control. Use environment variables or a secrets manager.

---

## Setting Up Inbound Email

To receive emails at your domain via Resend:

### Option 1: Resend-Managed Domain (Fastest)

Use your auto-generated address: `<anything>@<your-id>.resend.app`

No DNS configuration needed. Find your address in Dashboard → Emails → Receiving → "Receiving address".

### Option 2: Custom Domain

Add an MX record to receive at `<anything>@yourdomain.com`:

| Setting | Value |
|---------|-------|
| Type | MX |
| Host | Your domain or subdomain |
| Value | Provided in Resend dashboard |
| Priority | 10 |

**Critical:** Your MX record must have the lowest priority number, or emails won't route to Resend.

**Subdomain Recommendation:** If you already have MX records (Google Workspace, Microsoft 365), use a subdomain like `support.yourdomain.com` to avoid disrupting existing email.

---

## Local Development

For local webhook testing, use a tunnel service:

**Hookdeck CLI (recommended):**
```bash
brew install hookdeck/hookdeck/hookdeck
hookdeck listen 3000 --path /webhooks/resend
```

Provides: public URL, web UI for inspecting/replaying requests, automatic retries.

**ngrok alternative:**
```bash
ngrok http 3000
# Use https://abc123.ngrok.io/webhooks/resend as endpoint
```

### Test from Dashboard

1. Go to your webhook in the Dashboard
2. Click **Send Test**
3. Select an event type
4. Click **Send**

---

## Signature Verification

### How It Works

Each webhook request includes three Svix headers:

| Header | Description |
|--------|-------------|
| `svix-id` | Unique message identifier |
| `svix-timestamp` | Unix timestamp when the webhook was sent |
| `svix-signature` | HMAC-SHA256 signature(s), base64 encoded |

The signature is computed over: `{svix-id}.{svix-timestamp}.{raw-body}`

### Using the Resend SDK (Recommended — Node.js/TypeScript)

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

// Throws an error if invalid, returns parsed payload if valid
const event = resend.webhooks.verify({
  payload: rawBody,  // Raw request body as string — NOT parsed JSON
  headers: {
    id: request.headers.get('svix-id'),           // Note: short key names
    timestamp: request.headers.get('svix-timestamp'),
    signature: request.headers.get('svix-signature'),
  },
  webhookSecret: process.env.RESEND_WEBHOOK_SECRET!,  // Your whsec_... secret
});
```

### Manual Verification — Node.js

```javascript
const crypto = require('crypto');

function verifySvixSignature(payload, headers, secret, tolerance = 300) {
  const msgId = headers['svix-id'];
  const msgTimestamp = headers['svix-timestamp'];
  const msgSignature = headers['svix-signature'];

  if (!msgId || !msgTimestamp || !msgSignature) return false;

  // Check timestamp tolerance (prevent replay attacks)
  const now = Math.floor(Date.now() / 1000);
  const timestamp = parseInt(msgTimestamp, 10);
  if (Math.abs(now - timestamp) > tolerance) return false;

  // Remove 'whsec_' prefix and decode secret
  const secretKey = secret.startsWith('whsec_') ? secret.slice(6) : secret;
  const secretBytes = Buffer.from(secretKey, 'base64');

  // Create signed content
  const signedContent = `${msgId}.${msgTimestamp}.${payload}`;

  // Compute expected signature
  const expectedSig = crypto
    .createHmac('sha256', secretBytes)
    .update(signedContent)
    .digest('base64');

  // Check against provided signatures (may be multiple, space-separated)
  const signatures = msgSignature.split(' ');
  for (const sig of signatures) {
    if (sig.startsWith('v1,')) {
      const providedSig = sig.slice(3);
      try {
        if (crypto.timingSafeEqual(Buffer.from(providedSig), Buffer.from(expectedSig))) {
          return true;
        }
      } catch {
        // Length mismatch, continue checking
      }
    }
  }
  return false;
}
```

### Manual Verification — Python

```python
import hmac
import hashlib
import base64
import time

def verify_svix_signature(payload: bytes, headers: dict, secret: str, tolerance: int = 300) -> bool:
    msg_id = headers.get("svix-id")
    msg_timestamp = headers.get("svix-timestamp")
    msg_signature = headers.get("svix-signature")

    if not all([msg_id, msg_timestamp, msg_signature]):
        return False

    try:
        timestamp = int(msg_timestamp)
        now = int(time.time())
        if abs(now - timestamp) > tolerance:
            return False
    except ValueError:
        return False

    if secret.startswith("whsec_"):
        secret = secret[6:]
    secret_bytes = base64.b64decode(secret)

    signed_content = f"{msg_id}.{msg_timestamp}.{payload.decode()}"

    expected_sig = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()

    for sig in msg_signature.split():
        if sig.startswith("v1,"):
            if hmac.compare_digest(sig[3:], expected_sig):
                return True
    return False
```

---

## Common Verification Gotchas

### 1. Raw Body Requirement (Most Common Failure)

The signature is computed over the raw request body. Parsing JSON first invalidates it.

**Express:**
```javascript
// WRONG - body is already parsed
app.use(express.json());
app.post('/webhooks/resend', (req, res) => {
  resend.webhooks.verify({ payload: req.body, ... }); // Fails!
});

// CORRECT - use raw body for webhook route
app.post('/webhooks/resend',
  express.raw({ type: 'application/json' }),
  (req, res) => {
    resend.webhooks.verify({ payload: req.body.toString(), ... }); // Works!
  }
);
```

### 2. Middleware Ordering in Express

If you use a global JSON parser, configure the webhook route **before** the parser:

```javascript
// Webhook route with raw body (FIRST)
app.post('/webhooks/resend', express.raw({ type: 'application/json' }), handleWebhook);

// Global JSON parser (AFTER)
app.use(express.json());
```

### 3. Secret Format

The webhook secret starts with `whsec_`. When verifying manually:
1. Strip the `whsec_` prefix
2. Base64-decode the remaining string

### 4. Timestamp Tolerance

Svix rejects requests older than 5 minutes by default (prevents replay attacks). Issues arise if:
- Your server clock is significantly off
- You're replaying old events for testing

### 5. Multiple Signature Versions

The `svix-signature` header may contain multiple signatures (space-separated), each prefixed with `v1,`. Always check all and accept if any match.

---

## Framework Implementations

### Express (Using Resend SDK)

```javascript
const express = require('express');
const { Resend } = require('resend');

const resend = new Resend(process.env.RESEND_API_KEY);
const app = express();

// CRITICAL: Use express.raw() for webhook endpoint
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
        case 'email.sent':
          console.log('Email sent:', event.data.email_id);
          break;
        case 'email.delivered':
          console.log('Email delivered:', event.data.email_id);
          break;
        case 'email.bounced':
          console.log('Email bounced:', event.data.email_id);
          break;
        case 'email.received':
          // Fetch full content separately
          const { data: email } = await resend.emails.receiving.get(event.data.email_id);
          console.log(email.text);
          break;
        default:
          console.log('Unhandled event:', event.type);
      }

      res.json({ received: true });
    } catch (err) {
      console.error('Webhook verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);
```

### Next.js App Router

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  const payload = await request.text(); // Must use raw text, not request.json()

  try {
    const event = resend.webhooks.verify({
      payload,
      headers: {
        id: request.headers.get('svix-id'),
        timestamp: request.headers.get('svix-timestamp'),
        signature: request.headers.get('svix-signature'),
      },
      webhookSecret: process.env.RESEND_WEBHOOK_SECRET!,
    });

    switch (event.type) {
      case 'email.delivered':
        // Handle delivery confirmation
        break;
      case 'email.bounced':
        // Handle bounce — remove from list
        break;
      case 'email.received':
        // Fetch full email body separately
        const { data: email } = await resend.emails.receiving.get(event.data.email_id);
        break;
    }

    return new Response('OK', { status: 200 });
  } catch (err) {
    return new Response(`Webhook Error: ${err.message}`, { status: 400 });
  }
}
```

### FastAPI (Python — Manual Verification)

```python
import os
from fastapi import FastAPI, Request, HTTPException
from .verify import verify_svix_signature  # use the function above

app = FastAPI()
webhook_secret = os.environ.get("RESEND_WEBHOOK_SECRET")

@app.post("/webhooks/resend")
async def resend_webhook(request: Request):
    payload = await request.body()

    if not verify_svix_signature(payload, dict(request.headers), webhook_secret):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    event = json.loads(payload)
    event_type = event.get("type")

    if event_type == "email.delivered":
        pass  # handle delivery
    elif event_type == "email.bounced":
        pass  # handle bounce
    elif event_type == "email.received":
        pass  # fetch full email via API

    return {"received": True}
```

> For complete working examples with tests, see:
> - [examples/express/](../examples/express/) — Full Express implementation
> - [examples/nextjs/](../examples/nextjs/) — Next.js App Router implementation
> - [examples/fastapi/](../examples/fastapi/) — Python FastAPI implementation

---

## Debugging Verification Failures

### Error: "Missing required headers"

Check all three headers are present:
```javascript
console.log('svix-id:', req.headers['svix-id']);
console.log('svix-timestamp:', req.headers['svix-timestamp']);
console.log('svix-signature:', req.headers['svix-signature']);
```

### Error: "Invalid signature"

1. **Check the raw body** — ensure you're using the unparsed request body
2. **Check the secret** — must be the `whsec_...` value from your webhook endpoint
3. **Check for modifications** — any proxy or middleware that modifies the body breaks verification

### Error: "Timestamp too old"

1. **Check server time** — run `date` and compare to actual time
2. **For testing only** — increase the tolerance parameter temporarily

---

## Full Documentation

- [Resend Webhooks Documentation](https://resend.com/docs/webhooks)
- [Svix Signature Verification](https://docs.svix.com/receiving/verifying-payloads/how)
