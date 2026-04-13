# Setup: Env Vars, Products, and Prices

## Table of contents

- Environment variables
- SDK initialization
- Creating products and prices
- Using lookup keys

---

## Environment variables

```bash
STRIPE_SECRET_KEY=sk_test_...          # Never expose to the browser
STRIPE_PUBLISHABLE_KEY=pk_test_...     # Safe for client-side / Stripe.js
STRIPE_WEBHOOK_SECRET=whsec_...        # From Stripe Dashboard → Webhooks
```

Use separate key sets per environment (development, staging, production).
Never commit keys to source control. In production, use a secrets manager.

Add to `.gitignore`:
```
.env
.env.local
.env*.local
```

---

## Creating products and prices

Run this once to seed your Stripe account. After running, copy the resulting
Price IDs into your environment config.

```typescript
// scripts/seed-stripe.ts
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-03-25.dahlia',
})

async function seed() {
  const starter = await stripe.products.create({
    name: 'Starter',
    metadata: { tier: '1' },
  })

  const growth = await stripe.products.create({
    name: 'Growth',
    metadata: { tier: '2' },
  })

  const pro = await stripe.products.create({
    name: 'Pro',
    metadata: { tier: '3' },
  })

  const prices = await Promise.all([
    stripe.prices.create({
      product: starter.id,
      unit_amount: 2900,
      currency: 'usd',
      recurring: { interval: 'month' },
      lookup_key: 'starter_monthly',
    }),
    stripe.prices.create({
      product: growth.id,
      unit_amount: 7900,
      currency: 'usd',
      recurring: { interval: 'month' },
      lookup_key: 'growth_monthly',
    }),
    stripe.prices.create({
      product: pro.id,
      unit_amount: 19900,
      currency: 'usd',
      recurring: { interval: 'month' },
      lookup_key: 'pro_monthly',
    }),
  ])

  console.log('Prices created:')
  prices.forEach((p) =>
    console.log(`  ${p.lookup_key}: ${p.id}`)
  )
}

seed().catch(console.error)
```

---

## Using lookup keys instead of hardcoded Price IDs

Hardcoding Price IDs breaks when switching between test and live mode.
Use `lookup_keys` to retrieve prices by name at runtime:

```typescript
const prices = await stripe.prices.list({
  lookup_keys: ['starter_monthly', 'growth_monthly', 'pro_monthly'],
  expand: ['data.product'],
})

const priceMap = Object.fromEntries(
  prices.data.map((p) => [p.lookup_key!, p.id])
)
// priceMap.starter_monthly === 'price_...'
```

---

## DB: what to store about Stripe objects

You need at minimum:

| Column | Table | Notes |
|---|---|---|
| `stripe_customer_id` | users / profiles | Set at Customer creation; index it |
| `stripe_subscription_id` | subscriptions | The `sub_...` ID |
| `status` | subscriptions | `active`, `trialing`, `past_due`, `canceled`, etc. |
| `price_id` | subscriptions | Current Price |
| `current_period_end` | subscriptions | For gating access |

Everything else (invoice history, payment methods, plan details) can be
fetched from the Stripe API on demand — no need to replicate the full object.

---

## Checking a user's current plan

```typescript
// Example using a generic DB client — adapt to your ORM/DB
const subscription = await db.subscriptions
  .findFirst({
    where: { userId, status: { in: ['active', 'trialing'] } },
    orderBy: { createdAt: 'desc' },
  })

const hasAccess = !!subscription
```
