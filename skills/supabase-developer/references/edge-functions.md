# Edge Functions

Supabase Edge Functions run on Deno Deploy (TypeScript/JavaScript). Limits: 2-second CPU time, 150-second wall clock timeout.

---

## CLI Quick Reference

```bash
supabase functions new my-function          # Create
supabase functions serve                    # Local dev (all functions)
supabase functions serve my-function        # Local dev (specific)
supabase functions deploy my-function       # Deploy
supabase functions deploy                   # Deploy all
supabase functions logs my-function         # View logs
supabase functions logs my-function --follow  # Follow logs
supabase functions logs my-function --level error
supabase secrets set KEY=value              # Set secret
supabase secrets set --env-file .env        # Set from file
supabase secrets list                       # List secret names
supabase secrets unset KEY                  # Remove secret
```

---

## Function Template

**Basic:**
```typescript
// supabase/functions/my-function/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { name } = await req.json()
  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { "Content-Type": "application/json" } },
  )
})
```

**With authentication:**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const authHeader = req.headers.get('Authorization')!
  const token = authHeader.replace('Bearer ', '')

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    { global: { headers: { Authorization: authHeader } } }
  )

  const { data: { user }, error } = await supabase.auth.getUser(token)
  if (error || !user) {
    return new Response('Unauthorized', { status: 401 })
  }

  return new Response(
    JSON.stringify({ message: `Hello ${user.email}!` }),
    { headers: { "Content-Type": "application/json" } },
  )
})
```

**With database access (service role):**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const { userId } = await req.json()
  const { data, error } = await supabase.from('users').select('*').eq('id', userId).single()

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400, headers: { 'Content-Type': 'application/json' }
    })
  }

  return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } })
})
```

**Scheduled (Cron) function:**
```typescript
serve(async (req) => {
  // Verify request is from Supabase Cron
  const authHeader = req.headers.get('Authorization')
  if (authHeader !== `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}`) {
    return new Response('Unauthorized', { status: 401 })
  }

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const { data, error } = await supabase
    .from('logs')
    .delete()
    .lt('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())

  return new Response(JSON.stringify({ deleted: data?.length ?? 0 }), {
    headers: { 'Content-Type': 'application/json' }
  })
})
```

**Set up pg_cron trigger:**
```sql
select cron.schedule(
  'daily-cleanup',
  '0 2 * * *',
  $$
  select net.http_post(
    url := 'https://your-project.supabase.co/functions/v1/daily-cleanup',
    headers := '{"Content-Type": "application/json", "Authorization": "Bearer YOUR_SERVICE_ROLE_KEY"}'::jsonb,
    body := '{}'::jsonb
  ) as request_id;
  $$
);
```

---

## Invoke Functions

**POST:**
```bash
curl -s -X POST "${SUPABASE_URL}/functions/v1/${FUNCTION_NAME}" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${USER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action": "process"}'
```

**GET:**
```bash
curl -s "${SUPABASE_URL}/functions/v1/${FUNCTION_NAME}?id=123" \
  -H "apikey: ${SUPABASE_KEY}"
```

**Local:**
```bash
curl http://localhost:54321/functions/v1/my-function \
  -H "Authorization: Bearer ${SUPABASE_KEY}" \
  -d '{"name": "test"}'
```

---

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (invalid/missing auth) |
| 403 | Forbidden (insufficient permissions) |
| 500 | Internal server error (function crashed) |
| 504 | Gateway timeout (exceeded time limit) |

---

## Security Best Practices

1. Always validate and sanitize request data
2. Never use service role key in public/client-facing functions
3. Store secrets in Supabase secrets — never in function code
4. Configure CORS headers appropriately
5. Don't leak sensitive info in error responses
6. Implement rate limiting for public functions

## Performance Tips

1. Cold starts add 100-200ms — design for it
2. Keep functions small for faster cold starts
3. Cache external data with in-memory caching
4. Use `Promise.all()` for concurrent operations
5. Stream large responses

---

## Full API Reference

- Edge Functions: https://supabase.com/docs/guides/functions
- Deno Deploy: https://deno.com/deploy/docs
