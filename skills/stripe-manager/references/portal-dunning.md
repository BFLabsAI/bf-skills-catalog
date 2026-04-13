# Billing Portal and Dunning

## Table of contents

- Billing portal (self-service subscription management)
- Dunning: Stripe Smart Retries (recommended)
- Dunning: custom email sequence via webhooks
- Pausing subscriptions

---

## Billing portal

The Customer Portal lets users upgrade, downgrade, cancel, update payment
methods, and view invoice history — with zero custom UI.

### One-time setup: configure in Stripe Dashboard

Go to: Stripe Dashboard → Settings → Billing → Customer portal.

Configure:
- Allowed plan changes: list which products/prices users can switch to
- Cancellation: enable, set to `at_period_end` (not immediate)
- Cancellation reason collection: enable to capture churn data
- Payment method updates: enable
- Invoice history: enable

### Create a portal session

```typescript
async function createPortalSession(stripeCustomerId: string, returnUrl: string) {
  const session = await stripe.billingPortal.sessions.create({
    customer: stripeCustomerId,
    return_url: returnUrl,
  })

  return session.url  // redirect the user here
}
```

That's all the code needed. Stripe handles every interaction inside the portal.

---

## Dunning: Stripe Smart Retries (recommended)

Enable Smart Retries in Stripe Dashboard → Settings → Billing →
Subscriptions and emails.

With Smart Retries enabled, Stripe automatically:
1. Retries failed charges up to 4 times using ML-optimized timing
2. Sends configurable reminder emails to customers
3. Cancels the subscription after exhausting retries (configurable)

You receive `invoice.payment_failed` on each attempt and
`customer.subscription.deleted` if the subscription is ultimately canceled.

This handles ~90% of dunning needs with zero code. Build a custom sequence
only when you need branded emails, in-app prompts, or additional grace-period
logic beyond what the Dashboard provides.

---

## Dunning: custom email sequence via webhooks

```typescript
async function handlePaymentFailed(invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string
  const attemptCount = invoice.attempt_count  // 1, 2, 3, 4...

  // Update subscription status in your DB
  await db.subscriptions.update(subscriptionId, { status: 'past_due' })

  const customer = await stripe.customers.retrieve(
    invoice.customer as string
  ) as Stripe.Customer

  switch (attemptCount) {
    case 1:
      await sendEmail(customer.email!, 'payment-failed-1')
      break
    case 2:
      await sendEmail(customer.email!, 'payment-failed-2')
      break
    case 3:
      await sendEmail(customer.email!, 'payment-failed-3')
      break
    default:
      await sendEmail(customer.email!, 'payment-failed-final')
  }
}
```

### Recommended dunning sequence

| Day | Attempt | Message tone |
|-----|---------|---|
| 0 | 1st fail | Friendly: "payment didn't go through" |
| 3 | 2nd retry | Urgent: "please update your card" |
| 7 | 3rd retry | Critical: "access at risk" |
| 14 | 4th retry | Final notice — cancel if unresolved |

Set the retry schedule in Dashboard → Settings → Billing → Smart retries.
`invoice.payment_failed` fires on each attempt regardless of retry type.

---

## Pausing subscriptions

Use pause instead of cancel when the user wants to stop billing temporarily
but intends to return:

```typescript
// Pause billing
await stripe.subscriptions.update(subscriptionId, {
  pause_collection: {
    behavior: 'void',        // 'void' stops invoices; 'keep_as_draft' queues them
    resumes_at: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90,  // 90 days
  },
})

// Resume
await stripe.subscriptions.update(subscriptionId, {
  pause_collection: '',  // empty string removes the pause
})
```

When paused, subscription `status` remains `active` but `pause_collection`
is set. Account for this in your access-control logic:

```typescript
function hasActiveAccess(subscription: { status: string } | null): boolean {
  if (!subscription) return false
  return ['active', 'trialing'].includes(subscription.status)
  // If you store pause_collection state, also check it here
}
```

---

## Checking access in your app

```typescript
const subscription = await db.subscriptions.findActiveForUser(userId)

if (!subscription) {
  redirectToUpgrade()
}
```

Gate by `status in ('active', 'trialing')`. Everything else (past_due,
canceled, paused) should be treated as no access unless you explicitly want
a grace period for past_due.
