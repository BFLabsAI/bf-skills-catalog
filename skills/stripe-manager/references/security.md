# Security: API Keys, RAKs, Webhook Safety

Adapted from Stripe's official security guidance. Apply these rules to all
code written for this project.

## Table of contents

- API key hygiene
- Restricted API keys (RAKs)
- Webhook security
- Client-side rules
- Incident response

---

## API key hygiene

**Never** hardcode keys in source code — not in constants, not in comments,
not in "example" snippets. Even `sk_test_...` test keys can be used to create
charges and cause billing issues.

Store keys in:
- **Development:** `.env.local` (never committed — add to `.gitignore`)
- **Production:** Platform secret manager (Vercel → Environment Variables,
  AWS → Secrets Manager, etc.)

Rules:
- Use **separate keys for each environment** (development, staging, production)
- **Never log** secret keys or include them in error messages
- **Never build** API endpoints that dump environment variables
- **Rotate keys** when any team member with access leaves
- Set up a **pre-commit hook** to catch `sk_...` and `rk_...` patterns in source:

```bash
# .git/hooks/pre-commit
if git diff --cached | grep -E '"(sk|rk)_(test|live)_[a-zA-Z0-9]+"'; then
  echo "ERROR: Stripe API key detected in staged changes. Remove it."
  exit 1
fi
```

---

## Restricted API keys (RAKs)

Use **restricted API keys** (`rk_...`) instead of the full secret key (`sk_...`)
wherever possible. A compromised RAK can only do what you scoped it to — far
less damage than a compromised secret key.

Principle of least privilege: give each RAK only the permissions its specific
service needs.

**Recommended RAKs for a typical SaaS:**

| Service | Permissions needed |
|---|---|
| Webhook handler | Subscriptions read, Customers read |
| Checkout Server Action | Customers write, Checkout Sessions write |
| Admin/reporting | Customers read, Subscriptions read, Invoices read |

**Migration path from secret key to RAK:**
1. Review the key's request logs in Stripe Workbench to see what it calls
2. Create a RAK in test mode with matching permissions
3. Use `stripe logs tail` to watch for `403` errors
4. Fix any `403` by adding missing permissions
5. Create the live-mode RAK and replace the key in production
6. Rotate or expire the old secret key

---

## Webhook security

Always verify the `Stripe-Signature` header using
`stripe.webhooks.constructEvent()`. This is a cryptographic guarantee that
the request came from Stripe and was not tampered with.

Never process a webhook event without verifying the signature first.

For defense in depth, also allowlist [Stripe's IP addresses](https://docs.stripe.com/ips)
on your webhook endpoint. Combined with signature verification, this makes
spoofed requests essentially impossible.

Return `200` for events you've successfully processed (even if you don't handle
that event type). Return `400` only for signature failures or malformed
payloads. Return `500` only for transient errors you want Stripe to retry.

---

## Client-side rules

- **Never** expose the Stripe secret key or RAK in:
  - Client Components (`'use client'`)
  - `NEXT_PUBLIC_*` environment variables
  - Browser-accessible API routes that return the key
- Use `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` for the Stripe.js / Elements
  initialization — this is safe to expose
- All Stripe API calls must go through your backend (Server Actions or
  Route Handlers)

---

## Incident response

If a key is exposed or suspected compromised:

1. **Roll the key immediately** in the Stripe Dashboard → Developers → API keys
   — even if you're not sure it was used maliciously
2. **Audit request logs** in Stripe Workbench for unrecognized activity
3. **Contact Stripe Support** if you see unfamiliar charges or API calls
4. Update the key in all environments and secrets managers
5. Audit your codebase and git history for the exposed key:
   ```bash
   git log -p | grep -E 'sk_(test|live)_'
   ```
   If found, consider the entire branch history compromised — rotate and
   rewrite history or make the repo private

---

## Go-live checklist

Before switching to live mode keys:

- [ ] `STRIPE_SECRET_KEY` is a live-mode RAK (not the full secret key)
- [ ] `STRIPE_WEBHOOK_SECRET` is from the live-mode webhook endpoint
- [ ] No keys appear in source code or committed `.env` files
- [ ] Webhook signature verification is enabled and tested
- [ ] Idempotency is implemented in webhook handler
- [ ] Test mode keys removed from production environment
- [ ] Pre-commit hook installed to prevent accidental key commits
