# Checkout: Sessions, Trials, Upgrades, Cancellation

## Table of contents

- API choice
- Get or create Stripe Customer
- Subscription checkout
- One-time payment
- Subscription with trial
- Upgrade / downgrade
- Cancellation
- Embedded checkout (alternative to redirect)
- Success page guidance

---

## API choice

Always default to **Checkout Sessions** (`stripe.checkout.sessions.create`).
Use raw `PaymentIntents` only when you need off-session charging or must
control the full payment lifecycle independently (rare).

Checkout Sessions handle taxes, discounts, adaptive pricing, proration, trial
management, and saved payment methods automatically.

---

## Get or create Stripe Customer

Create a Stripe Customer the first time a user initiates a billing action.
Store `stripe_customer_id` in your DB immediately — don't wait for a webhook.

```typescript
async function getOrCreateStripeCustomer(userId: string, email: string): Promise<string> {
  const existingCustomerId = await db.users.getStripeCustomerId(userId)
  if (existingCustomerId) return existingCustomerId

  const customer = await stripe.customers.create({
    email,
    metadata: { user_id: userId },
  })

  await db.users.setStripeCustomerId(userId, customer.id)
  return customer.id
}
```

---

## Subscription checkout

```typescript
const customerId = await getOrCreateStripeCustomer(user.id, user.email)

const session = await stripe.checkout.sessions.create({
  customer: customerId,
  mode: 'subscription',
  line_items: [{ price: priceId, quantity: 1 }],
  // Omit payment_method_types — let Stripe use dynamic payment methods
  allow_promotion_codes: true,
  subscription_data: {
    metadata: { user_id: user.id },  // stored on the subscription; read back in webhooks
  },
  success_url: `${BASE_URL}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${BASE_URL}/pricing`,
  metadata: { user_id: user.id },
})

// Redirect user to session.url
return session.url
```

---

## One-time payment

```typescript
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  mode: 'payment',
  line_items: [{
    price_data: {
      currency: 'usd',
      product_data: { name: 'Lifetime Access' },
      unit_amount: 29900,
    },
    quantity: 1,
  }],
  success_url: `${BASE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${BASE_URL}/pricing`,
  payment_intent_data: {
    metadata: { user_id: user.id },
  },
})
```

---

## Subscription with trial

```typescript
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  mode: 'subscription',
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
    metadata: { user_id: user.id },
  },
  // Collect payment method during trial but don't charge yet
  payment_method_collection: 'if_required',
  success_url: `${BASE_URL}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${BASE_URL}/pricing`,
})
```

After trial ends, `customer.subscription.updated` fires when the subscription
becomes `active`. Handle it in your webhook to update your DB.

---

## Upgrade / downgrade (mid-cycle plan change)

```typescript
async function changePlan(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)

  return stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: subscription.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'create_prorations',  // charge/credit the difference immediately
  })
}
```

The `customer.subscription.updated` webhook fires — let that be the source of
truth for updating your DB. Don't write to the DB here.

---

## Cancellation

Prefer the billing portal for cancellations (zero code). For programmatic
cancellation:

```typescript
// Graceful: user keeps access until end of billing period
await stripe.subscriptions.update(subscriptionId, {
  cancel_at_period_end: true,
})

// Immediate (only when user explicitly requests it)
await stripe.subscriptions.cancel(subscriptionId)
```

`customer.subscription.updated` (with `cancel_at_period_end: true`) or
`customer.subscription.deleted` will fire — handle in your webhook.

---

## Embedded checkout (alternative to redirect)

Use when you want checkout rendered inside your page rather than redirecting
to a Stripe-hosted URL.

```typescript
// Backend: return client_secret instead of url
const session = await stripe.checkout.sessions.create({
  // ... same params as above
  ui_mode: 'embedded',
  return_url: `${BASE_URL}/billing/return?session_id={CHECKOUT_SESSION_ID}`,
})

return { clientSecret: session.client_secret }
```

```tsx
// Frontend (React)
import { EmbeddedCheckoutProvider, EmbeddedCheckout } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(process.env.STRIPE_PUBLISHABLE_KEY!)

export function CheckoutForm({ clientSecret }: { clientSecret: string }) {
  return (
    <EmbeddedCheckoutProvider stripe={stripePromise} options={{ clientSecret }}>
      <EmbeddedCheckout />
    </EmbeddedCheckoutProvider>
  )
}
```

---

## Success page guidance

Never fulfill orders (provision access, update DB) on the success page.
The `checkout.session.completed` webhook is the authoritative signal.
The success page is UX confirmation only.

```typescript
// Just confirm the session completed — don't provision here
const session = await stripe.checkout.sessions.retrieve(searchParams.session_id)

if (session.status !== 'complete') {
  return showError('Payment not completed')
}

return showSuccessMessage()
```
