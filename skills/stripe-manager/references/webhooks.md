# Webhooks: Signature Verification, Idempotency, Critical Events

## Table of contents

- The raw body requirement (most common bug)
- Framework-specific handler setup
- Idempotency
- Critical events and what to do with each
- Local development

---

## The raw body requirement

Stripe signature verification requires the **raw, unparsed request body**.
If your framework parses JSON before you can access the raw bytes, the
signature check will always fail (400 errors on every webhook).

Framework-specific approach:

| Framework | How to get raw body |
|---|---|
| **Express** | Use `express.raw({ type: 'application/json' })` on the webhook route only |
| **Next.js App Router** | `const body = await req.text()` — not `req.json()` |
| **Fastify** | Add `addContentTypeParser('application/json', { parseAs: 'buffer' }, ...)` |
| **FastAPI (Python)** | `body = await request.body()` |
| **Django** | `request.body` (already raw bytes) |

---

## Framework-specific handler setup

### Express / Node.js

```typescript
import express from 'express'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-03-25.dahlia',
})

const app = express()

// CRITICAL: express.raw() only on this route — not app-wide express.json()
app.post(
  '/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const signature = req.headers['stripe-signature'] as string

    let event: Stripe.Event
    try {
      event = stripe.webhooks.constructEvent(
        req.body,
        signature,
        process.env.STRIPE_WEBHOOK_SECRET!,
      )
    } catch (err) {
      return res.status(400).send('Webhook signature failed')
    }

    try {
      await handleEvent(event)
    } catch (err) {
      return res.status(500).send('Handler failed')
    }

    res.json({ received: true })
  }
)
```

### Next.js App Router

```typescript
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe'
import { headers } from 'next/headers'

export async function POST(req: Request) {
  const body = await req.text()  // raw text — NOT req.json()
  const signature = headers().get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!,
    )
  } catch {
    return new Response('Webhook signature failed', { status: 400 })
  }

  try {
    await handleEvent(event)
  } catch {
    return new Response('Handler failed', { status: 500 })
  }

  return new Response(null, { status: 200 })
}
```

### Python / FastAPI

```python
import stripe
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            body, signature, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    await handle_event(event)
    return {"received": True}
```

---

## Idempotency

Stripe retries webhooks for up to 3 days on non-2xx responses. Your handlers
will receive the same event multiple times. Always guard against duplicate
processing.

Store processed event IDs in your DB and check before acting:

```typescript
async function handleEvent(event: Stripe.Event) {
  // 1. Skip if already processed
  const alreadyProcessed = await db.webhookEvents.exists(event.id)
  if (alreadyProcessed) return

  // 2. Dispatch
  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutCompleted(event.data.object as Stripe.CheckoutSession)
      break
    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      await handleSubscriptionUpsert(event.data.object as Stripe.Subscription)
      break
    case 'customer.subscription.deleted':
      await handleSubscriptionDeleted(event.data.object as Stripe.Subscription)
      break
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object as Stripe.Invoice)
      break
    case 'invoice.paid':
      await handleInvoicePaid(event.data.object as Stripe.Invoice)
      break
    default:
      break
  }

  // 3. Mark as processed
  await db.webhookEvents.insert({ id: event.id, type: event.type })
}
```

Use upsert (not insert) for all DB writes in handlers to stay safe against
re-delivery:

```typescript
await db.subscriptions.upsert({ id: subscription.id, ...data })
```

---

## Critical events and what to do with each

### checkout.session.completed

Earliest signal that a subscription was created and payment confirmed (or
trial started).

```typescript
async function handleCheckoutCompleted(session: Stripe.CheckoutSession) {
  if (session.mode !== 'subscription') return

  // Retrieve full subscription — session fields may be limited
  const subscription = await stripe.subscriptions.retrieve(
    session.subscription as string
  )

  await syncSubscriptionToDB(subscription)
}
```

### customer.subscription.created / updated

Fires on creation, renewal, upgrade, downgrade, trial changes, status changes,
and cancellation scheduling.

```typescript
async function handleSubscriptionUpsert(subscription: Stripe.Subscription) {
  await syncSubscriptionToDB(subscription)
}

async function syncSubscriptionToDB(subscription: Stripe.Subscription) {
  // Resolve user from metadata set at checkout creation (see checkout.md)
  const userId = subscription.metadata.user_id
  if (!userId) {
    console.error('Subscription missing user_id metadata:', subscription.id)
    return
  }

  await db.subscriptions.upsert({
    id: subscription.id,
    userId,
    status: subscription.status,
    priceId: subscription.items.data[0].price.id,
    cancelAtPeriodEnd: subscription.cancel_at_period_end,
    currentPeriodEnd: new Date(subscription.current_period_end * 1000),
    trialEnd: subscription.trial_end
      ? new Date(subscription.trial_end * 1000)
      : null,
  })
}
```

### customer.subscription.deleted

Fires when a subscription ends (immediate cancel or after period end).

```typescript
async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  await syncSubscriptionToDB(subscription)  // status will be 'canceled'
  // Revoke access, trigger win-back flow, etc.
}
```

### invoice.payment_failed

Fires on every failed renewal attempt. Update status and notify the user.

```typescript
async function handlePaymentFailed(invoice: Stripe.Invoice) {
  await db.subscriptions.update(invoice.subscription as string, {
    status: 'past_due',
  })
  // See portal-dunning.md for dunning sequence
}
```

### invoice.paid

Fires on successful renewal. Sync subscription state (status may move from
`past_due` back to `active`).

```typescript
async function handleInvoicePaid(invoice: Stripe.Invoice) {
  if (!invoice.subscription) return
  const subscription = await stripe.subscriptions.retrieve(
    invoice.subscription as string
  )
  await syncSubscriptionToDB(subscription)
}
```

---

## Local development

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/webhooks/stripe

# CLI prints a local webhook secret (whsec_...) — use it as STRIPE_WEBHOOK_SECRET locally
```

Trigger specific events:
```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_failed
```

---

## Webhook endpoint registration (production)

Register in Stripe Dashboard → Developers → Webhooks:
- URL: `https://yourdomain.com/webhooks/stripe`
- Events: `checkout.session.completed`, `customer.subscription.created`,
  `customer.subscription.updated`, `customer.subscription.deleted`,
  `invoice.paid`, `invoice.payment_failed`

Copy the signing secret (`whsec_...`) into your production environment.
