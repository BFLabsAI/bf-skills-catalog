# Secrets & Credential Detection

Merged from: vibe-security/references/secrets-and-env.md + security-review/references/secret-patterns.md

---

## Client-Side Environment Variable Prefixes

These prefixes cause env vars to be inlined into the client bundle at build time. Everything in the bundle is visible to anyone:

| Framework | Client Prefix | Danger |
|-----------|--------------|--------|
| Next.js | `NEXT_PUBLIC_` | Inlined into browser JS at build time |
| Vite | `VITE_` | Inlined into browser JS at build time |
| Expo / React Native | `EXPO_PUBLIC_` | Baked into the app bundle |
| Create React App | `REACT_APP_` | Inlined into browser JS at build time |

**Safe client-side values:**
- Stripe publishable key (`pk_live_*`, `pk_test_*`)
- Supabase anon key
- Firebase client config (apiKey, authDomain, projectId)
- Public analytics IDs

**Must NEVER be client-side:**
- Supabase `service_role` key (bypasses all RLS)
- Stripe secret key (`sk_live_*`, `sk_test_*`)
- Any database connection string
- Any third-party API secret key
- JWT signing secrets
- OAuth client secrets

---

## .gitignore Rules

Ensure `.env`, `.env.local`, `.env.*.local`, and any file containing secrets is in `.gitignore` **before the first commit**.

Check that `.env.example` / `.env.sample` files contain only placeholder values.

**If a secret was ever committed to git, consider it compromised — deleting the file doesn't remove it from history. Rotate immediately.** Run `gitleaks detect` to scan for leaked secrets.

---

## High-Confidence Secret Patterns (Regex)

### API Keys & Tokens
```regex
# OpenAI
sk-[a-zA-Z0-9]{48}

# Anthropic
sk-ant-[a-zA-Z0-9\-_]{90,}

# AWS Access Key
AKIA[0-9A-Z]{16}

# AWS Secret Key (look for near AWS_ACCESS_KEY_ID)
[0-9a-zA-Z/+]{40}

# GitHub Token
gh[pousr]_[a-zA-Z0-9]{36,}
github_pat_[a-zA-Z0-9]{82}

# Stripe (also flag: sk_live_, rk_live_)
sk_live_[a-zA-Z0-9]{24,}
rk_live_[a-zA-Z0-9]{24,}

# Twilio
AC[a-z0-9]{32}
SK[a-z0-9]{32}

# SendGrid
SG\.[a-zA-Z0-9\-_.]{66}

# Slack
xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+
xoxp-[0-9]+-[0-9]+-[0-9]+-[a-zA-Z0-9]+

# Google API Key
AIza[0-9A-Za-z\-_]{35}

# Mailgun
key-[a-zA-Z0-9]{32}
```

### Private Keys & Certificates
```regex
-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY( BLOCK)?-----
-----BEGIN CERTIFICATE-----
```

### Database Connection Strings
```regex
mongodb(\+srv)?:\/\/[^:]+:[^@]+@
(postgres|postgresql|mysql):\/\/[^:]+:[^@]+@
redis:\/\/:[^@]+@
(connection[_-]?string|connstr|db[_-]?url).*password=
```

### Hardcoded Passwords
```regex
(password|passwd|pwd|secret|api_key|apikey|auth_token|access_token|private_key)
  \s*[=:]\s*["'][^"']{8,}["']
```

---

## Entropy-Based Detection

Apply to string literals > 20 characters in assignment context.
Shannon entropy > 4.5 bits/char AND length > 20 = likely secret.

Common false positives to exclude: lorem ipsum, HTML/CSS content, UUIDs, base64-encoded non-sensitive config.

---

## Files That Should Never Be Committed

```
.env, .env.local, .env.production, .env.staging
*.pem, *.key, *.p12, *.pfx
id_rsa, id_ed25519
credentials.json, service-account.json, gcp-key.json
secrets.yaml, secrets.json, config/secrets.yml
```

---

## CI/CD & IaC Secret Risks

**GitHub Actions** — flag hardcoded values in `env:` blocks (should use `${{ secrets.NAME }}`); flag `echo ${{ secrets.X }}` (leaks to logs).

**Docker** — flag `ENV AWS_SECRET_KEY=actual-value` (persisted in image layers); flag `ARG API_KEY=actual-value` (visible in image history).

**Terraform** — flag `password = "hardcoded-password"` or `access_key = "AKIA..."` (use var or data source instead).

---

## Detection Tips (Code Audit)

When auditing, search for:
- Files named `.env` tracked by git: `git ls-files | grep .env`
- Strings: `sk_live_`, `sk_test_`, `AKIA`, `ghp_`, `glpat-`, `xoxb-`, `Bearer `
- `process.env.NEXT_PUBLIC_` or `import.meta.env.VITE_` referencing anything with "secret", "private", "service", or "key" in the name
- Hardcoded URLs with credentials: `postgresql://user:password@host`

---

## Safe Patterns (Do NOT Flag)

```
"your-api-key-here"
"<YOUR_API_KEY>"
"${API_KEY}"
"${process.env.API_KEY}"
"os.environ.get('API_KEY')"
"REPLACE_WITH_YOUR_KEY"
"xxx...xxx"
"sk-..." (in documentation/comments)
```
