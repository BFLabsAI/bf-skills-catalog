---
name: cyber-security
description: >
  Comprehensive security, code quality, and testing skill. Covers security audits (injection flaws,
  auth bypass, secrets exposure, broken access control, insecure payments, vibe-coded app risks),
  code review (security, performance, correctness, N+1 queries, error handling), technical debt
  identification and prioritization, test strategy design, structured debugging, web app testing
  with Playwright, and Python pytest coverage. Trigger when the user asks about security, code
  review, vulnerabilities, "is this safe?", "check my code", "audit this", "can someone hack this?",
  tech debt, refactoring, code health, test strategy, "how should we test", debugging, error messages,
  stack traces, "something broke", frontend testing, or pytest coverage.
license: MIT
metadata:
  fused-from: vibe-security, code-review, tech-debt, testing-strategy, debug, security-review, webapp-testing, pytest-coverage
  version: "1.0"
---

# Cyber Security & Code Quality

Unified skill covering security auditing, code review, technical debt, test strategy, debugging, web app testing, and pytest coverage. Use any section independently — they are organized by topic, not by source.

**Core Security Principle:** Never trust the client. Every price, user ID, role, subscription status, feature flag, and rate limit counter must be validated or enforced server-side.


## Security Audit

Use for: scanning codebases for vulnerabilities, "is this safe?", "audit this", "review for vulnerabilities", "can someone hack this?", vibe-coded apps, AI-generated code.

Two complementary modes:

**Vibe-Security mode** — targets AI-generated/"vibe-coded" apps; focuses on the specific patterns AI assistants get wrong (RLS disabled, client-side prices, exposed service keys).

**Deep-Scan mode** — full researcher-style analysis; traces data flows, cross-file, self-verifying findings.

### Audit Steps (run in order, skip irrelevant steps)

1. **Secrets & Credentials** — hardcoded API keys, client-side env prefixes (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`), `.env` in `.gitignore`. See `references/secrets.md`.
2. **Dependency Audit** — check package.json, requirements.txt, go.mod, Cargo.toml, etc. for known CVEs, deprecated crypto libs. See `references/vulnerable-packages.md`.
3. **Database Access Control** — Supabase RLS, Firebase Security Rules, Convex auth guards. #1 source of critical vulns in vibe-coded apps. See `references/database-security.md`.
4. **Authentication & Authorization** — JWT handling, middleware, Server Actions, BOLA/IDOR, privilege escalation, mass assignment. See `references/authentication.md`.
5. **Injection Flaws** — SQL injection (raw queries, ORM misuse), XSS (innerHTML, dangerouslySetInnerHTML), command injection, LDAP/header/log injection. See `references/vuln-categories.md`.
6. **Rate Limiting & Abuse** — auth endpoints, AI calls, expensive operations. Verify counters are server-side. See `references/rate-limiting.md`.
7. **Payment Security** — client-side price manipulation, webhook signature verification, subscription status. See `references/payments.md`.
8. **Mobile Security** — secure token storage, API key backend proxy, deep link validation. See `references/mobile.md`.
9. **AI/LLM Integration** — exposed AI keys, missing usage caps, prompt injection, unsafe output rendering. See `references/ai-integration.md`.
10. **Deployment & Config** — production settings, security headers, source map exposure, environment separation. See `references/deployment.md`.
11. **Cross-File Data Flow** — trace user-controlled input from entry points (HTTP params, headers, body) to sinks (DB queries, exec calls, HTML output). See `references/vuln-categories.md`.
12. **Self-Verification Pass** — re-read each finding; check for sanitization missed; downgrade false positives.

### Security Output Format

Organize findings by severity: **Critical → High → Medium → Low**.

For each finding: file + line, vulnerability name, concrete attacker impact, before/after fix.

Flag critical issues (exposed secrets, disabled RLS, auth bypass) immediately at the top — don't bury them.

See `references/report-format.md` for the full structured report template.

### Severity Guide

| Severity | Meaning | Example |
|----------|---------|---------|
| CRITICAL | Immediate exploitation risk | SQLi, RCE, auth bypass, service key exposed |
| HIGH | Serious, exploit path exists | XSS, IDOR, hardcoded secrets |
| MEDIUM | Exploitable with conditions | CSRF, open redirect, weak crypto |
| LOW | Best practice violation | Verbose errors, missing headers |
| INFO | Observation, not a vulnerability | Outdated dep (no CVE) |

**Rules:** Report only genuine issues. Prioritize by exploitability. If a technology isn't present (e.g., no Supabase), skip that section. Never auto-apply patches — present for human review.


## Code Review

Use for: PR review, diff review, "review this before I merge", "is this code safe?", N+1 queries, missing edge cases, error handling gaps.

### Review Dimensions

- **Security** — SQL injection, XSS, CSRF, auth flaws, secrets in code, SSRF, path traversal
- **Performance** — N+1 queries, memory leaks, O(n²) in hot paths, missing indexes, unbounded queries, resource leaks
- **Correctness** — edge cases (null, empty, overflow), race conditions, error propagation, off-by-one, type safety
- **Maintainability** — naming, single responsibility, duplication, test coverage, documentation

### Code Review Output

```markdown
## Code Review: [PR title or file]

### Summary
[1-2 sentence overview]

### Critical Issues
| # | File | Line | Issue | Severity |
|---|------|------|-------|----------|

### Suggestions
| # | File | Line | Suggestion | Category |
|---|------|------|------------|----------|

### What Looks Good
- [Positive observations]

### Verdict
[Approve / Request Changes / Needs Discussion]
```

**Tip:** Provide context ("this is a hot path", "handles PII") and specify concerns ("focus on security") for more targeted reviews.


## Technical Debt

Use for: "tech debt", "technical debt audit", "what should we refactor", "code health", refactoring priorities, maintenance backlog.

### Debt Categories

| Type | Examples | Risk |
|------|----------|------|
| Code debt | Duplicated logic, poor abstractions, magic numbers | Bugs, slow development |
| Architecture debt | Monolith that should be split, wrong data store | Scaling limits |
| Test debt | Low coverage, flaky tests, missing integration tests | Regressions ship |
| Dependency debt | Outdated libraries, unmaintained dependencies | Security vulns |
| Documentation debt | Missing runbooks, outdated READMEs, tribal knowledge | Onboarding pain |
| Infrastructure debt | Manual deploys, no monitoring, no IaC | Incidents, slow recovery |

### Prioritization Formula

Score each item: **Priority = (Impact + Risk) × (6 − Effort)**

- Impact: how much does it slow the team? (1–5)
- Risk: what happens if not fixed? (1–5)
- Effort: how hard is the fix? (1–5, inverted — lower effort = higher score)

**Output:** Prioritized list with effort estimates, business justification, and a phased remediation plan that can run alongside feature work.


## Testing Strategy

Use for: "how should we test", "test strategy for", "write tests for", "test plan", "what tests do we need", test coverage, test architecture.

### Testing Pyramid

```
        /   E2E    \         Few, slow, high confidence
       / Integration \       Some, medium speed
      /   Unit Tests  \      Many, fast, focused
```

### Strategy by Component

- **API endpoints** — unit tests for business logic, integration tests for HTTP layer, contract tests for consumers
- **Data pipelines** — input validation, transformation correctness, idempotency
- **Frontend** — component tests, interaction tests, visual regression, accessibility
- **Infrastructure** — smoke tests, chaos engineering, load tests

### What to Cover

Focus on: business-critical paths, error handling, edge cases, security boundaries, data integrity.

Skip: trivial getters/setters, framework code, one-off scripts.

**Output:** Test plan with what to test, test type per area, coverage targets, example test cases, and identification of existing coverage gaps.


## Debugging

Use for: error messages, stack traces, "this works in staging but not prod", "something broke after the deploy", divergent behavior.

### Debug Workflow

1. **Reproduce** — understand expected vs actual behavior; identify exact reproduction steps; determine scope (when did it start? who is affected?)
2. **Isolate** — narrow down the component, service, or code path; check recent changes (deploys, config, dependencies); review logs and error messages
3. **Diagnose** — form hypotheses and test them; trace the code path; identify root cause (not symptoms)
4. **Fix** — propose fix with explanation; consider side effects and edge cases; suggest regression tests

### Debug Output

```markdown
## Debug Report: [Issue Summary]

### Reproduction
- Expected: [What should happen]
- Actual: [What happens instead]
- Steps: [How to reproduce]

### Root Cause
[Why the bug occurs]

### Fix
[Code changes or configuration fixes]

### Prevention
- [Test to add]
- [Guard to put in place]
```

**Tips:**
- Share error messages exactly — don't paraphrase; the exact text matters
- Mention what changed — recent deploys, dependency updates, config changes are top suspects
- Include context — "works in staging but not prod" or "only affects large payloads" narrows things fast

**Conflict resolution:** "Don't leak stack traces in error pages" (security rule) and "share error messages exactly" (debugging guidance) are not contradictory — the security rule applies to production error responses shown to end users; the debugging tip applies to information you share with Claude during a debug session.


## Web App Testing (Playwright)

Use for: testing local web apps, verifying frontend functionality, debugging UI behavior, capturing screenshots, browser logs.

Use the Playwright MCP Server when available. Fallback: run in a local Node.js environment with Playwright installed.

### Core Capabilities

- **Browser Automation** — navigate URLs, click, fill forms, select dropdowns, handle dialogs
- **Verification** — assert element presence, verify text, check visibility, validate URLs, test responsive behavior
- **Debugging** — screenshots, console logs, network request inspection

### Key Patterns

```javascript
// Wait for element
await page.waitForSelector("#element-id", { state: "visible" });

// Check existence
const exists = (await page.locator("#element-id").count()) > 0;

// Capture console logs
page.on("console", (msg) => console.log("Browser log:", msg.text()));

// Screenshot on error
try {
  await page.click("#button");
} catch (error) {
  await page.screenshot({ path: "error.png" });
  throw error;
}
```

### Guidelines

1. Verify the app is running before tests
2. Use explicit waits — don't interact before elements are ready
3. Capture screenshots on failure
4. Prefer `data-testid` or role-based selectors over CSS classes
5. Always close the browser when done
6. Test incrementally — simple interactions first

Helper functions for common tasks: `skills/cyber-security/assets/test-helper.js`


## Pytest Coverage

Use for: running pytest with coverage, finding uncovered lines, increasing coverage to 100%.

### Commands

```bash
# Full coverage report
pytest --cov --cov-report=annotate:cov_annotate

# Specific module
pytest --cov=your_module_name --cov-report=annotate:cov_annotate

# Specific test file + module
pytest tests/test_your_module.py --cov=your_module_name --cov-report=annotate:cov_annotate
```

### Workflow

1. Run coverage report — generates `cov_annotate/` directory
2. Files with 100% coverage: skip (no action needed)
3. Files under 100%: open the matching file in `cov_annotate/`; lines starting with `!` are not covered
4. Add tests to cover missing lines
5. Repeat until all lines are covered


## Rules and Invariants

- **Never trust the client** — server-side validation is non-negotiable for prices, roles, user IDs, feature flags
- **Never auto-apply security patches** — always present patches for human review
- **Report only genuine security issues** — filter false positives; verify before reporting
- **Prioritize by impact** — critical issues (key exposed, RLS disabled, auth bypass) go to the top of every report
- **Topic-first grouping** — group security findings by vulnerability category, not by file
- **Secrets rotated immediately** — if a secret was ever committed to git, it is compromised; rotate it now
- **Error messages in production must not leak** — stack traces, SQL queries, and file paths must not appear in user-facing error responses


## When to Use This Skill

| Trigger | Section |
|---------|---------|
| "is this safe?", "audit this", "review for vulnerabilities", "can someone hack this?" | Security Audit |
| "check my code", "vibe coding", RLS/Firebase/auth/payment/API key concerns | Security Audit |
| PR review, "review this before I merge", N+1, error handling | Code Review |
| "tech debt", "code health", "what should we refactor" | Technical Debt |
| "how should we test", "test plan", "test strategy", coverage architecture | Testing Strategy |
| Error messages, stack traces, "something broke", staging vs prod differences | Debugging |
| Frontend testing, browser automation, Playwright, screenshots, UI verification | Web App Testing |
| pytest, coverage, missing lines, `!` in annotated files | Pytest Coverage |


## References

- `references/secrets.md` — secrets detection: patterns, env var prefixes, .gitignore rules, regex patterns, entropy heuristics
- `references/vuln-categories.md` — deep reference for injection flaws, XSS, SSRF, BOLA, JWT, cryptography, race conditions, path traversal
- `references/language-patterns.md` — framework-specific patterns: Express, React, Next.js, Django, Flask, Spring Boot, PHP, Go, Rails, Rust
- `references/vulnerable-packages.md` — CVE watchlist for npm, pip, Maven, Rubygems, Cargo, Go modules
- `references/report-format.md` — structured report template: finding cards, severity table, dependency audit, secrets scan, patch format
- `references/database-security.md` — Supabase RLS, Firebase Security Rules, Convex auth patterns
- `references/authentication.md` — JWT verification, middleware, Server Actions, session management
- `references/rate-limiting.md` — rate limiting strategies and abuse prevention
- `references/payments.md` — Stripe security, webhook verification, price validation
- `references/mobile.md` — React Native/Expo: secure storage, API proxy, deep links
- `references/ai-integration.md` — LLM API key protection, usage caps, prompt injection, output sanitization
- `references/deployment.md` — production config, security headers, environment separation
