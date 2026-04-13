# RLS Policy Audit

Security testing reference for Row Level Security (RLS) policies — common vulnerabilities, test vectors, output format, and evidence collection.

> **Progressive writes required:** If running a full audit, update tracking files AS YOU GO, not just at the end. Write findings to `.sb-pentest-context.json` after each finding; log to `.sb-pentest-audit.log` before and after each test. If the audit is interrupted, prior findings must already be saved.

---

## When to Audit

- After discovering potential data exposure
- To verify RLS policies are correctly implemented
- To test for common bypass techniques
- As part of a comprehensive security review

## Prerequisites

- List of tables to audit
- Anon key available
- Ideally also an authenticated user token for cross-user tests

---

## RLS Fundamentals

```sql
-- Enable RLS on a table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Create a policy
CREATE POLICY "Users see own posts"
  ON posts FOR SELECT
  USING (auth.uid() = author_id);
```

**If RLS is enabled but no policies exist → ALL access is blocked.**

---

## Common Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| RLS Disabled | P0 | Table has no RLS protection at all |
| Overly Permissive | P0–P1 | Policy `USING (true)` allows everyone |
| Missing Operation | P1 | SELECT policy exists but INSERT/UPDATE/DELETE missing |
| USING vs WITH CHECK | P1 | Read allowed but write inconsistent with data ownership |
| Missing Policy | Variable | RLS enabled but no SELECT policy (blocks all access) |

---

## Test Vectors

### 1. Unauthenticated Access

```bash
# No Authorization header — only anon key
curl -s "${SUPABASE_URL}/rest/v1/users?select=*" \
  -H "apikey: ${ANON_KEY}"
```

### 2. Cross-User Access

```bash
# As user A, try to access user B's data
curl -s "${SUPABASE_URL}/rest/v1/orders?user_id=eq.${USER_B_ID}" \
  -H "apikey: ${ANON_KEY}" \
  -H "Authorization: Bearer ${USER_A_TOKEN}"
```

### 3. Filter Bypass

```bash
# Try to bypass filters with OR conditions
curl -s "${SUPABASE_URL}/rest/v1/posts?or=(published.eq.true,published.eq.false)" \
  -H "apikey: ${ANON_KEY}"
```

### 4. Join Exploitation

```bash
# Try to access data through related tables
curl -s "${SUPABASE_URL}/rest/v1/comments?select=*,posts(*)" \
  -H "apikey: ${ANON_KEY}"
```

### 5. RPC Bypass

```bash
# Check if RPC functions bypass RLS
curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/get_all_users" \
  -H "apikey: ${ANON_KEY}"
```

---

## Good RLS Patterns

```sql
-- User owns their data (all operations)
CREATE POLICY "Users own their data" ON user_data FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Public read, authenticated write
CREATE POLICY "Public read" ON posts FOR SELECT USING (published = true);
CREATE POLICY "Author write" ON posts FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "Author update" ON posts FOR UPDATE USING (auth.uid() = author_id);
```

## Bad RLS Patterns

```sql
-- ❌ Too permissive — everyone reads everything
CREATE POLICY "Anyone" ON secrets FOR SELECT USING (true);

-- ❌ Missing WITH CHECK — users can INSERT any user_id
CREATE POLICY "Insert" ON posts FOR INSERT WITH CHECK (true);
```

---

## Audit Output Format

```
═══════════════════════════════════════════════════════════
 RLS POLICY AUDIT
═══════════════════════════════════════════════════════════
 Tables Audited: N

 1. <table_name>
    RLS Enabled: ✅ YES / ❌ NO
    Status: 🔴 P0 / 🟠 P1 / ✅ OK

    [Policies found if RLS enabled]
    [Test results per operation]
    [Recommendation / Fix SQL if issue found]

 Summary
 ─────────────────────────────────────────────────────────
 RLS Disabled: N tables ← CRITICAL
 RLS Enabled: N tables
   ├── Properly Configured: N
   ├── Partial Issues: N
   └── Major Issues: N

 Bypass Tests:
 ├── Unauthenticated access: N tables vulnerable
 ├── Cross-user access: N tables vulnerable
 ├── Filter bypass: N tables vulnerable
 └── Join exploitation: N tables vulnerable
═══════════════════════════════════════════════════════════
```

---

## Evidence Collection

**Evidence directory:** `.sb-pentest-evidence/03-api-audit/rls-tests/`

| File | Content |
|------|---------|
| `rls-tests/[table]-anon.json` | Anonymous access test results |
| `rls-tests/[table]-auth.json` | Authenticated access test results |
| `rls-tests/cross-user-test.json` | Cross-user access attempts |

**Evidence format for a finding:**
```json
{
  "evidence_id": "RLS-001",
  "timestamp": "2025-01-31T10:25:00Z",
  "category": "api-audit",
  "type": "rls_test",
  "severity": "P0",
  "table": "users",
  "rls_enabled": false,
  "tests": [
    {
      "test_name": "anon_select",
      "description": "Anonymous user SELECT access",
      "request": {
        "curl_command": "curl -s '$URL/rest/v1/users?select=*&limit=5' -H 'apikey: $ANON_KEY'"
      },
      "response": {"status": 200, "rows_returned": 5, "total_accessible": 1247},
      "result": "VULNERABLE",
      "impact": "All user data accessible without authentication"
    }
  ],
  "remediation_sql": "ALTER TABLE users ENABLE ROW LEVEL SECURITY;\nCREATE POLICY \"Users see own data\" ON users FOR SELECT USING (auth.uid() = id);"
}
```

**Context file (`.sb-pentest-context.json`):**
```json
{
  "rls_audit": {
    "timestamp": "...",
    "tables_audited": 8,
    "summary": {"rls_disabled": 2, "rls_enabled": 6, "properly_configured": 3},
    "findings": [
      {"table": "users", "rls_enabled": false, "severity": "P0", "issue": "No RLS protection"}
    ]
  }
}
```

**Log file (`.sb-pentest-audit.log`):**
```
[TIMESTAMP] [rls-audit] [START] Auditing RLS policies
[TIMESTAMP] [rls-audit] [FINDING] P0: users table has no RLS
[TIMESTAMP] [rls-audit] [CONTEXT_UPDATED] .sb-pentest-context.json updated
```

---

## Related Audits

- List tables before auditing to know your scope
- Check RPC functions — they can bypass RLS if not properly secured
- Storage buckets also need access policies; check them in the same review
