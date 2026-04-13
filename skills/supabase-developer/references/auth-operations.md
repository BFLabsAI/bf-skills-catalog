# Auth Operations

Complete reference for Supabase Auth API operations via REST. All curl examples use `$SUPABASE_URL` and `$SUPABASE_KEY` env vars.

---

## Sign Up

**Email/password:**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/signup" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123"}'
```

**With user metadata:**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/signup" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "data": {"first_name": "John", "last_name": "Doe"}
  }'
```

**Auto-confirm user (service role key required):**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/signup" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123", "email_confirm": true}'
```

---

## Sign In

**Email/password login:**
```bash
response=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123"}')

access_token=$(echo "$response" | jq -r '.access_token')
refresh_token=$(echo "$response" | jq -r '.refresh_token')
user_id=$(echo "$response" | jq -r '.user.id')
```

**Response fields:** `access_token`, `refresh_token`, `user`, `expires_in` (seconds).

**Token defaults:** access_token expires in 1 hour; refresh_token expires in 30 days.

---

## Get Current User

```bash
curl -s -X GET "${SUPABASE_URL}/auth/v1/user" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

---

## Update User

**Update metadata:**
```bash
curl -s -X PUT "${SUPABASE_URL}/auth/v1/user" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"first_name": "Jane", "avatar_url": "https://example.com/avatar.jpg"}}'
```

**Update email or password:** replace `data` field with `"email"` or `"password"` field.

---

## Sign Out

```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/logout" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

---

## Refresh Token

```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"${REFRESH_TOKEN}\"}"
```

---

## Password Recovery

**Send reset email:**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/recover" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Resend confirmation email:**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/resend" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"type": "signup", "email": "user@example.com"}'
```

---

## Admin Operations (service_role key required)

**List all users:**
```bash
curl -s "${SUPABASE_URL}/auth/v1/admin/users" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"

# Paginated:
curl -s "${SUPABASE_URL}/auth/v1/admin/users?page=1&per_page=50" ...
```

**Get user by ID:**
```bash
curl -s "${SUPABASE_URL}/auth/v1/admin/users/${USER_ID}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"
```

**Create user (no email confirmation):**
```bash
curl -s -X POST "${SUPABASE_URL}/auth/v1/admin/users" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin-created@example.com",
    "password": "securepassword123",
    "email_confirm": true,
    "user_metadata": {"first_name": "Admin"}
  }'
```

**Update user (admin):**
```bash
curl -s -X PUT "${SUPABASE_URL}/auth/v1/admin/users/${USER_ID}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "updated@example.com", "user_metadata": {"role": "admin"}}'
```

**Delete user:**
```bash
curl -s -X DELETE "${SUPABASE_URL}/auth/v1/admin/users/${USER_ID}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"
```

---

## Verify JWT Token (decode only — bash)

```bash
payload=$(echo "$ACCESS_TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null)
echo "$payload" | jq '.'

exp=$(echo "$payload" | jq -r '.exp')
now=$(date +%s)
[[ $now -gt $exp ]] && echo "Token expired" || echo "Token valid"
```

---

## Common Error Codes

| Status | Error | Meaning |
|--------|-------|---------|
| 400 | Invalid login credentials | Wrong email or password |
| 400 | User already registered | Email already exists |
| 401 | Invalid token | Access token expired or invalid |
| 422 | Validation error | Invalid email format or weak password |
| 429 | Too many requests | Rate limit exceeded |

---

## Full API Reference

https://supabase.com/docs/guides/auth
