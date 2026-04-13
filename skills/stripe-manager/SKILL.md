---
name: stripe-manager
description: >-
  Full-cycle Stripe monetization skill covering the complete SaaS billing
  lifecycle: products, prices, subscriptions, checkout, webhooks, billing
  portal, dunning, and security. Use whenever building or modifying anything
  related to payments, subscriptions, pricing, checkout, webhooks, billing
  portal, dunning, or Stripe API work. Prefer this over the individual
  stripe-best-practices, stripe-integration, stripe-payments, and
  stripe-webhooks skills. Trigger on: "add payments", "set up subscriptions",
  "stripe webhook", "billing portal", "customer portal", "trial", "upgrade
  plan", "dunning", "invoice", "checkout session", "price ID", "product ID",
  "stripe customer", MRR, ARR, SaaS billing, or any Stripe integration question.
---

Latest Stripe API version: **2026-03-25.dahlia**. Always use the latest SDK
and API version unless the user specifies otherwise.

---

## Decision routing

| What you're building | Go to |
|---|---|
| Products, prices, env setup | `references/setup.md` |
| One-time payment or subscription checkout | `references/checkout.md` |
| Trials, upgrades, downgrades, cancellation | `references/checkout.md` |
| Webhook handler (signature, idempotency, critical events) | `references/webhooks.md` |
| Billing portal, dunning, failed payment recovery | `references/portal-dunning.md` |
| API key management, RAKs, security review | `references/security.md` |

Read the relevant reference file before writing any code or answering any
integration question. For cross-cutting tasks, read all relevant sections first.

---

## Invariant rules (apply everywhere, no exceptions)

These are the most common sources of bugs and security issues across all
Stripe integrations. Check existing code against these rules when reviewing.

**Never use:**
- `Charges API` → use `Checkout Sessions` or `PaymentIntents` instead
- `Sources API` → use `Setup Intents` instead
- `Card Element` → use `Payment Element` instead
- `payment_method_types: ['card']` → omit it; use dynamic payment methods configured in the Dashboard
- Hardcoded `sk_live_...` or `sk_test_...` anywhere in source code

**Always:**
- Prefer `Checkout Sessions` over raw `PaymentIntents` for on-session payment flows
- Verify webhook signatures with `stripe.webhooks.constructEvent()` before touching the payload
- Handle webhooks idempotently — check if you've already processed an event before acting on it
- Store `stripe_customer_id` on the user record in your DB at Customer creation time
- Use TypeScript types from the `stripe` package when working in TypeScript

---

## SDK initialization

One singleton instance, reused across the app:

```typescript
// lib/stripe.ts
import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-03-25.dahlia',
  typescript: true,
})
```

Never instantiate `new Stripe(...)` inline in route handlers or individual functions.

---

## SaaS billing lifecycle (overview)

```
User signs up
  └─> Create Stripe Customer → store stripe_customer_id in your DB
        └─> User picks plan → Checkout Session (mode: subscription)
              └─> checkout.session.completed webhook
                    └─> Provision access, update subscription state in DB
                          └─> User manages plan via Billing Portal
                                └─> customer.subscription.updated / deleted webhooks
                                      └─> Dunning if invoice.payment_failed
```

Every step above has a reference file. Follow the flow in order when building
a feature from scratch.

---

## Reference files

- `references/setup.md` — env vars, products/prices, SDK init
- `references/checkout.md` — Checkout Sessions, trials, upgrades, cancellation
- `references/webhooks.md` — signature verification, idempotency, critical events
- `references/portal-dunning.md` — billing portal, dunning sequence, failed payment recovery
- `references/security.md` — API key hygiene, RAKs, incident response
