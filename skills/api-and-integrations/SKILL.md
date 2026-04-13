---
name: api-and-integrations
description: >
  Complete guide for working with APIs — evaluating third-party APIs before building,
  reading documentation, designing REST and GraphQL APIs, creating API documentation,
  and handling all categories of API errors (REST, GraphQL, WebSocket, auth, rate limits,
  timeouts, network failures). Use when consuming, designing, or debugging any API.
version: "1.0.0"
tags:
  - api
  - rest
  - graphql
  - integrations
  - error-handling
  - documentation
  - design
---

# API and Integrations

## When to Use This Skill

- Evaluating a third-party API before integrating it
- Reading and making sense of API documentation
- Designing new REST or GraphQL endpoints
- Creating API documentation (OpenAPI, inline, reference)
- Debugging API errors — authentication, rate limits, network, timeouts, business logic
- Planning API versioning, pagination, filtering, security

---

## Part 1: Evaluating an API Before Building

Before writing a single line of integration code, answer these questions:

### Authentication Model
- What auth does it use? API key, OAuth 2.0, Bearer JWT, session cookies?
- Are credentials per-environment (staging vs. production)?
- How are credentials rotated? What happens when they expire mid-request?

### Rate Limits
- What are the rate limits? Per endpoint or global?
- Are there burst limits vs. sustained limits?
- How does the API signal rate-limit state (headers, response body)?
- What is the retry strategy when limits are hit?

### Stability and Versioning
- Does the API version its endpoints? (`/v1/`, `Accept:` header, query param?)
- Is the API stable, or are breaking changes frequent?
- Is there a changelog, deprecation policy, or sunset timeline?
- Does it expose a status page or uptime SLA?

### Error Behavior
- What HTTP status codes does it use? Does it use them correctly (200 for errors is a red flag)?
- Does it return structured errors or plain strings?
- What errors are retryable vs. permanent?

### Data Shape and Contracts
- Are responses consistent in shape, or do nullable fields appear unpredictably?
- Are lists always arrays, or can they be null?
- Does it return paginated results? Which strategy (offset, cursor, page)?
- Are timestamps ISO 8601? Are IDs strings or integers?

### Documentation Quality
- Does the documentation match the actual behavior? Test it — do not trust docs blindly.
- Are there code examples in your language?
- Is there an OpenAPI/Swagger spec, Postman collection, or SDK?

### Sandbox and Testing
- Is there a sandbox or test environment?
- Are there test credentials or test card numbers?
- Can you trigger error conditions in the sandbox?

---

## Part 2: Reading API Documentation

### Reading Strategy

1. **Start with authentication** — nothing works without it.
2. **Find the base URL and version** — `/api/v1/`, `https://api.example.com`.
3. **Scan the endpoint list** — identify what operations exist before going deep.
4. **Read the error reference** — understand what failures look like before you hit them.
5. **Look for rate limit docs** — find the limits and the headers that communicate them.
6. **Read request/response examples** — examples are more reliable than prose descriptions.
7. **Check SDKs** — if an official SDK exists, read its source code. It encodes the correct behavior.

### Third-Party API Responses Are Untrusted Data

Always treat API responses as untrusted input, even from reputable providers:
- Validate the shape before using any field
- Never assume a field exists because the docs say it does
- Null-check or provide defaults for optional fields
- Parse and validate dates, IDs, and enums — do not pass through raw strings

```typescript
// Validate external API responses before use
const result = ExternalUserSchema.safeParse(apiResponse);
if (!result.success) {
  logger.error('Unexpected shape from external API', { response: apiResponse, error: result.error });
  throw new ExternalAPIError('Unexpected response shape');
}
const user = result.data; // now safe to use
```

---

## Part 3: Designing REST APIs

### Core Principles

**Hyrum's Law:** With enough users, every observable behavior becomes a dependency — including undocumented quirks, error message text, and ordering. Design implications:
- Every exposed behavior is a commitment. Be intentional about what you expose.
- Don't leak implementation details. If users can observe it, they will depend on it.
- Plan for deprecation at design time.

**Contract First:** Define the interface before implementing it. The contract is the spec.

**Prefer Addition Over Modification:** Extend interfaces without breaking existing consumers. New optional fields are safe. Removing or renaming fields requires a version bump.

### URL Structure

```
# Resources are nouns, plural, lowercase, kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id        # Full replacement
PATCH  /api/v1/users/:id        # Partial update
DELETE /api/v1/users/:id

# Sub-resources for relationships
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders
GET    /api/v1/users/:id/orders/:orderId

# Actions that don't map to CRUD (use verbs sparingly)
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
```

```
# GOOD
/api/v1/team-members          # kebab-case for multi-word resources
/api/v1/orders?status=active  # query params for filtering

# BAD
/api/v1/getUsers              # verb in URL
/api/v1/user                  # singular
/api/v1/team_members          # snake_case in URLs
```

### HTTP Method Semantics

| Method | Idempotent | Safe | Use For |
|--------|-----------|------|---------|
| GET    | Yes | Yes | Retrieve resources |
| POST   | No  | No  | Create resources, trigger actions |
| PUT    | Yes | No  | Full replacement of a resource |
| PATCH  | No* | No  | Partial update of a resource |
| DELETE | Yes | No  | Remove a resource |

*PATCH can be made idempotent with proper implementation.

### HTTP Status Codes

```
# Success
200 OK                    — GET, PUT, PATCH (with response body)
201 Created               — POST; include Location header pointing to the new resource
204 No Content            — DELETE, PUT (no response body)

# Client Errors
400 Bad Request           — Malformed JSON, missing required fields
401 Unauthorized          — Missing or invalid authentication
403 Forbidden             — Authenticated but not authorized
404 Not Found             — Resource doesn't exist
409 Conflict              — Duplicate entry, state conflict
422 Unprocessable Entity  — Valid JSON but semantically invalid (validation failures)
429 Too Many Requests     — Rate limit exceeded

# Server Errors
500 Internal Server Error — Unexpected failure; never expose internal details
502 Bad Gateway           — Upstream service failed
503 Service Unavailable   — Temporary overload; include Retry-After header
```

Common mistakes:
- Using 200 for everything — use semantic status codes
- Using 500 for validation errors — use 400/422
- Omitting Location header on 201

### Response Format

**Single resource:**
```json
{
  "data": {
    "id": "abc-123",
    "email": "alice@example.com",
    "name": "Alice",
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

**Collection with pagination:**
```json
{
  "data": [
    { "id": "abc-123", "name": "Alice" },
    { "id": "def-456", "name": "Bob" }
  ],
  "meta": {
    "total": 142,
    "page": 1,
    "perPage": 20,
    "totalPages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```

**Error response:**
```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address", "code": "invalid_format" },
      { "field": "age",   "message": "Must be between 0 and 150",     "code": "out_of_range"   }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "requestId": "abc-123-def"
  }
}
```

Pick one error shape and use it everywhere. Never mix patterns where some endpoints throw, some return null, and some return `{ error }`.

### Naming Conventions

| Pattern | Convention | Example |
|---------|-----------|---------|
| REST URL segments | Plural nouns, kebab-case, no verbs | `/api/v1/team-members` |
| Query params | camelCase or snake_case (pick one) | `?sortBy=createdAt&pageSize=20` |
| Response fields | camelCase | `{ createdAt, updatedAt, taskId }` |
| Boolean fields | is/has/can prefix | `isComplete`, `hasAttachments` |
| Enum values | UPPER_SNAKE | `"IN_PROGRESS"`, `"COMPLETED"` |

### Pagination

**Offset-based (simple):**
```
GET /api/v1/users?page=2&per_page=20
```
- Pros: easy to implement, jump to page N
- Cons: slow on large offsets, inconsistent with concurrent inserts

**Cursor-based (scalable):**
```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20
```
- Pros: consistent performance, stable with concurrent inserts
- Cons: can't jump to arbitrary page

| Use Case | Pagination Type |
|----------|----------------|
| Admin dashboards, small datasets (<10K) | Offset |
| Infinite scroll, feeds, large datasets | Cursor |
| Public APIs | Cursor (default) |
| Search results | Offset (users expect page numbers) |

### Filtering, Sorting, and Search

```
# Simple equality
GET /api/v1/orders?status=active&customer_id=abc-123

# Comparison operators
GET /api/v1/products?price[gte]=10&price[lte]=100
GET /api/v1/orders?created_at[after]=2025-01-01

# Multiple values
GET /api/v1/products?category=electronics,clothing

# Sorting (prefix - for descending)
GET /api/v1/products?sort=-created_at,price

# Full-text search
GET /api/v1/products?q=wireless+headphones

# Sparse fieldsets
GET /api/v1/users?fields=id,name,email
```

### Authentication

```
# Bearer token (JWTs, OAuth access tokens)
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API key (server-to-server)
X-API-Key: sk_live_abc123

# Always use HTTPS
```

### Rate Limiting Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# When limit exceeded:
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{ "error": { "code": "rate_limit_exceeded", "message": "Try again in 60 seconds." } }
```

Rate limit tiers to plan for:

| Tier | Limit | Window |
|------|-------|--------|
| Anonymous | 30/min | Per IP |
| Authenticated | 100/min | Per user |
| Premium | 1000/min | Per API key |
| Internal | 10000/min | Per service |

### Versioning

**URL path versioning (recommended):**
```
/api/v1/users
/api/v2/users
```
Explicit, easy to route, cacheable, easy to test.

**Header versioning:**
```
GET /api/users
Accept: application/vnd.myapp.v2+json
```
Clean URLs but harder to test and easy to forget.

**Versioning strategy:**
1. Start with `/api/v1/` — don't version until you need to.
2. Maintain at most 2 active versions (current + previous).
3. Announce deprecation 6 months in advance for public APIs.
4. Add `Sunset: Sat, 01 Jan 2026 00:00:00 GMT` header to deprecated endpoints.
5. Return `410 Gone` after sunset date.

Non-breaking changes (no version bump needed): adding new optional response fields, adding new optional query params, adding new endpoints.

Breaking changes (require new version): removing or renaming fields, changing field types, changing URL structure, changing auth method.

### Validate at Boundaries

Validate all external input at system edges only — API route handlers, form submission, external service responses, environment variables. Do not scatter validation in internal functions.

```typescript
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid task data',
        details: result.error.flatten(),
      },
    });
  }
  const task = await taskService.create(result.data);
  return res.status(201).json({ data: task });
});
```

### Input/Output Type Separation

```typescript
// Input: what the caller provides
interface CreateTaskInput {
  title: string;
  description?: string;
}

// Output: what the system returns (includes server-generated fields)
interface Task {
  id: string;
  title: string;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
}
```

### Implementation Examples

**TypeScript (Next.js App Router):**
```typescript
import { z } from "zod";
import { NextRequest, NextResponse } from "next/server";

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = createUserSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({
      error: {
        code: "validation_error",
        message: "Request validation failed",
        details: parsed.error.issues.map(i => ({
          field: i.path.join("."),
          message: i.message,
          code: i.code,
        })),
      },
    }, { status: 422 });
  }

  const user = await createUser(parsed.data);
  return NextResponse.json(
    { data: user },
    { status: 201, headers: { Location: `/api/v1/users/${user.id}` } },
  );
}
```

**Python (Django REST Framework):**
```python
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create(**serializer.validated_data)
        return Response(
            {"data": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
            headers={"Location": f"/api/v1/users/{user.id}"},
        )
```

**Go (net/http):**
```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid_json", "Invalid request body")
        return
    }
    if err := req.Validate(); err != nil {
        writeError(w, http.StatusUnprocessableEntity, "validation_error", err.Error())
        return
    }
    user, err := h.service.Create(r.Context(), req)
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrEmailTaken):
            writeError(w, http.StatusConflict, "email_taken", "Email already registered")
        default:
            writeError(w, http.StatusInternalServerError, "internal_error", "Internal error")
        }
        return
    }
    w.Header().Set("Location", fmt.Sprintf("/api/v1/users/%s", user.ID))
    writeJSON(w, http.StatusCreated, map[string]any{"data": user})
}
```

---

## Part 4: Designing GraphQL APIs

### Core Principles

- Design for client needs — organize types around use cases, not database tables.
- Be explicit — use clear names, intentional nullability, and descriptions on every type and field.
- Design for evolution — use deprecation before removal, never break backward compatibility.
- Schema-first — write the schema before implementing resolvers.

### Type System Quick Reference

```graphql
"""
A user in the system.
"""
type User {
  id: ID!
  email: String!
  name: String           # Nullable — optional
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}
```

**Nullability rules:**

| Pattern   | Meaning |
|-----------|---------|
| `String`  | Nullable — may be null |
| `String!` | Non-null — always has value |
| `[String!]!` | Non-null list, non-null items (preferred for lists) |

Always use `[Type!]!` for lists — return empty list, never null, never null items.

### Input vs Output Types

```graphql
# Output type
type User {
  id: ID!
  email: String!
  createdAt: DateTime!
}

# Input type
input CreateUserInput {
  email: String!
  name: String
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserResult!
}
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Object/Interface/Union types | PascalCase, singular | `User`, `BlogPost`, `SearchResult` |
| Fields | camelCase | `firstName`, `createdAt` |
| Boolean fields | is/has/can/should prefix | `isActive`, `hasSubscription` |
| Enum names | PascalCase | `UserRole`, `OrderStatus` |
| Enum values | SCREAMING_SNAKE_CASE | `PENDING_PAYMENT`, `ADMIN` |
| Mutation names | verbNoun | `createUser`, `deletePost`, `publishPost` |
| Input types | MutationName + `Input` | `CreateUserInput`, `UpdatePostInput` |
| Payload/result types | MutationName + `Payload` or `Result` | `DeleteUserPayload`, `CreateOrderResult` |

Do not use Hungarian notation (`TUser`, `strName`), redundant prefixes (`userId` on a `User` type), or expose implementation details (`mysql_id`, `redis_cache_key`).

### Interfaces and Unions

```graphql
# Interface: shared fields across types
interface Node { id: ID! }
interface Timestamped { createdAt: DateTime!; updatedAt: DateTime! }

type User implements Node & Timestamped {
  id: ID!
  email: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Union: mutually exclusive types
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
  node(id: ID!): Node  # Refetch any entity by global ID
}
```

Use interfaces when types share common fields. Use unions when types are mutually exclusive and don't share fields (also for result/error types).

### Mutation Design

- Use single input argument: `mutation createUser(input: CreateUserInput!)`
- Return the affected object or a result union — never void
- Model mutations around business operations, not CRUD

```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserResult!
  publishPost(id: ID!): Post!
  addItemToCart(input: AddItemInput!): Cart!
  followUser(userId: ID!): FollowPayload!
}
```

### ID Strategy

- Use globally unique IDs (implement `Node` interface)
- Use `ID` type, not `String` or `Int`
- Base64-encode compound IDs: `base64("User:123")` → `VXNlcjoxMjM=`
- Expose `databaseId: Int!` separately if clients need the original numeric ID

### Custom Scalars

```graphql
scalar DateTime   # ISO 8601 date-time
scalar Date       # ISO 8601 date
scalar URL        # Valid URL
scalar Email      # Valid email address
scalar UUID       # UUID string
scalar JSON       # Arbitrary JSON (use sparingly — loses type safety)
```

### Pagination (Connection Pattern)

The Relay Connection pattern is the standard for GraphQL pagination:

```graphql
type Query {
  posts(
    first: Int
    after: String
    last: Int
    before: String
    filter: PostFilter
    orderBy: PostOrder
  ): PostConnection!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int        # Nullable — expensive to compute; omit when not needed
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

Pagination arguments:
- Forward: `first` + `after`
- Backward: `last` + `before`
- Do not mix forward and backward in the same request

Always cap maximum page size in resolvers:
```typescript
const limit = Math.min(first ?? 20, 100); // never let clients pull 10,000 items
```

Use cursor columns that are indexed:
```sql
SELECT * FROM posts
WHERE created_at < $cursor_timestamp
ORDER BY created_at DESC
LIMIT 20;
```

### GraphQL Security

**Disable introspection in production:**
```typescript
const server = new ApolloServer({
  introspection: process.env.NODE_ENV !== 'production',
});
```

**Limit query depth:**
```typescript
import depthLimit from 'graphql-depth-limit';
const server = new ApolloServer({
  validationRules: [depthLimit(10)],
});
```

**Limit query complexity:**
```typescript
import { createComplexityLimitRule } from 'graphql-validation-complexity';
const server = new ApolloServer({
  validationRules: [createComplexityLimitRule(1000)],
});
```

**Field-level authorization:**
```typescript
const resolvers = {
  User: {
    email: (user, args, context) => {
      if (context.user?.id !== user.id && !context.user?.isAdmin) return null;
      return user.email;
    },
  },
};
```

**Never leak internal details in errors:**
```typescript
// Bad
throw new Error(`Database error: SQLSTATE[23000]: duplicate key 'users_email_unique'`);

// Good
throw new GraphQLError('Email already registered', {
  extensions: { code: 'EMAIL_EXISTS' }
});
```

Disable stack traces in production:
```typescript
const server = new ApolloServer({
  includeStacktraceInErrorResponses: process.env.NODE_ENV === 'development',
});
```

---

## Part 5: Error Handling (All API Types)

This is the most critical operational section. Errors must be caught, categorized, and handled — not swallowed or let through unprocessed.

### REST API Error Handling

**Status code interpretation:**

| Code | Category | Action |
|------|----------|--------|
| 400 | Bad request — your payload is wrong | Fix request structure; do not retry |
| 401 | Unauthenticated | Refresh token or re-authenticate; then retry once |
| 403 | Unauthorized | Do not retry; escalate to user or check permissions |
| 404 | Not found | Do not retry; handle missing resource gracefully |
| 409 | Conflict | Resolve conflict (duplicate, state mismatch); then retry or surface to user |
| 422 | Validation failure | Fix the input fields; do not retry |
| 429 | Rate limited | Wait for `Retry-After` duration; exponential backoff |
| 500 | Server error | Retry with exponential backoff; alert if persistent |
| 502 | Bad gateway | Retry; upstream is down |
| 503 | Service unavailable | Respect `Retry-After`; exponential backoff |

**Retry strategy:**
- Only retry 429, 500, 502, 503 — never retry 4xx except 401 (token refresh) and 429
- Exponential backoff: `delay = base * 2^attempt + jitter`
- Cap retries (3–5 attempts max) and total timeout

**Debug checklist for REST errors:**
1. Log full request (method, URL, headers minus auth values, body)
2. Log full response (status, headers, body)
3. Check `Content-Type: application/json` — some errors return HTML (gateway errors, proxies)
4. Check for response encoding issues (gzip, chunked transfer)
5. Reproduce with curl to isolate library vs. server issues

### GraphQL Error Handling

GraphQL returns HTTP 200 even for errors. The error signal is in the response body, not the status code.

**Built-in error format:**
```json
{
  "data": { "user": null },
  "errors": [
    {
      "message": "User not found",
      "path": ["user"],
      "locations": [{ "line": 2, "column": 3 }],
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

**Error categories and when to use them:**

| Scenario | Pattern |
|----------|---------|
| Unexpected server error | Built-in errors (`extensions.code: 'INTERNAL_ERROR'`) |
| Authentication failure | Built-in errors (`extensions.code: 'UNAUTHENTICATED'`) |
| Authorization failure | Built-in errors (`extensions.code: 'UNAUTHORIZED'`) |
| Input validation failure | Union result types in schema |
| Business rule violation | Union result types in schema |
| Partial success possible | Union or nullable fields |

**Union-based result types (preferred for business errors):**
```graphql
union CreateOrderResult =
  | CreateOrderSuccess
  | ValidationError
  | InsufficientInventory
  | PaymentFailed

type CreateOrderSuccess { order: Order! }
type ValidationError { message: String!; field: String }
type InsufficientInventory { message: String!; unavailableItems: [OrderItem!]! }
type PaymentFailed { message: String!; reason: PaymentFailureReason!; retryable: Boolean! }
```

Client handling:
```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    ... on CreateOrderSuccess { order { id total } }
    ... on ValidationError { message field }
    ... on InsufficientInventory { message unavailableItems { productId availableQuantity } }
    ... on PaymentFailed { message reason retryable }
  }
}
```

**Standardized error codes:**
```graphql
enum ErrorCode {
  VALIDATION_FAILED
  INVALID_INPUT
  REQUIRED_FIELD_MISSING
  UNAUTHENTICATED
  UNAUTHORIZED
  TOKEN_EXPIRED
  NOT_FOUND
  ALREADY_EXISTS
  CONFLICT
  INSUFFICIENT_FUNDS
  LIMIT_EXCEEDED
  OPERATION_NOT_ALLOWED
  INTERNAL_ERROR
  SERVICE_UNAVAILABLE
  RATE_LIMITED
}
```

**Debug checklist for GraphQL errors:**
1. GraphQL errors always come back as HTTP 200 — check `response.errors`, not just the status code
2. Check `extensions.code` for machine-readable category
3. Check `path` to identify which field failed (partial data may still be valid)
4. Check `locations` to map back to query line numbers during development
5. If `data` is partial (some fields null, some populated), inspect `errors` array to understand which resolvers failed
6. Network-level errors (connection refused, timeout) will still surface as non-200 status codes

### Authentication Errors

**Symptoms and fixes:**

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 401 on every request | Expired or missing token | Re-authenticate; check env variable is set |
| 401 only after time | Token expiry | Implement token refresh; check `exp` claim in JWT |
| 403 on specific resources | Insufficient permissions | Check role/scope; token may be valid but underprivileged |
| 401 with valid token | Token format wrong | Check `Bearer ` prefix; verify signing algorithm matches |
| 401 after rotation | Stale token in cache | Invalidate cached tokens after rotation |
| GraphQL `UNAUTHENTICATED` | Auth not passed in GraphQL context | Check middleware that injects user into context |

**OAuth/JWT debugging:**
```
# Decode JWT locally (NOT for production secrets — use a local tool)
echo "eyJhbG..." | cut -d. -f2 | base64 -d | jq .
# Check: exp (expiry), iss (issuer), aud (audience), scopes/roles
```

**Handling token expiry in integration code:**
```typescript
async function callWithTokenRefresh<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    if (err.status === 401) {
      await refreshAccessToken();
      return fn(); // retry once
    }
    throw err;
  }
}
```

### Rate Limit Errors

**Detection:**
- REST: HTTP 429 status + `Retry-After` header
- GraphQL: HTTP 200 with `extensions.code: 'RATE_LIMITED'` or HTTP 429 depending on implementation
- Some APIs return 403 for rate limits (incorrect but real)

**Headers to read:**
```
X-RateLimit-Limit: 100          # Total allowed
X-RateLimit-Remaining: 0        # Remaining in window
X-RateLimit-Reset: 1640000000   # Unix timestamp when limit resets
Retry-After: 60                 # Seconds to wait (or HTTP date)
```

**Backoff implementation:**
```typescript
async function withRateLimitRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 5
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (err.status !== 429 || attempt === maxRetries - 1) throw err;
      const retryAfter = parseInt(err.headers?.['retry-after'] ?? '1', 10);
      const delay = Math.max(retryAfter * 1000, (2 ** attempt) * 1000);
      await sleep(delay);
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Proactive rate limit management:**
- Track `X-RateLimit-Remaining` and slow down before hitting zero
- Batch requests where possible
- Cache responses to reduce API call volume
- Use webhooks instead of polling where the API supports it

### Network Errors and Timeouts

**Error categories:**

| Error | Meaning | Action |
|-------|---------|--------|
| `ECONNREFUSED` | Server not listening | Check host/port; is service running? |
| `ENOTFOUND` | DNS resolution failed | Check hostname; DNS issue or wrong URL |
| `ETIMEDOUT` | Connection timed out | Server unreachable; check firewall/network |
| `ECONNRESET` | Connection dropped mid-flight | Retry; check if server crashed |
| `CERT_HAS_EXPIRED` | TLS certificate expired | Fix certificate; do not disable SSL verification in production |
| `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | TLS verification failed | Check CA bundle; self-signed certs require explicit trust |
| Read timeout | Request sent, no response | Server is processing too slowly; increase timeout or optimize query |
| Write timeout | Cannot send request | Network congestion or broken connection |

**Setting timeouts (always set explicit timeouts):**
```typescript
// fetch
const response = await fetch(url, {
  signal: AbortSignal.timeout(10_000), // 10 seconds
});

// axios
const response = await axios.get(url, { timeout: 10_000 });

// node:http
const options = { hostname, path, timeout: 10_000 };
```

**Distinguish timeouts from other failures:**
```typescript
try {
  const response = await fetchWithTimeout(url, 10_000);
} catch (err) {
  if (err.name === 'AbortError' || err.code === 'ETIMEDOUT') {
    // Timeout — consider retry with backoff
  } else if (err.code === 'ECONNREFUSED') {
    // Service down — alert immediately
  } else {
    // Unknown — log and escalate
  }
}
```

**Circuit breaker pattern** — stop hammering a failing service:
```typescript
// If 5 consecutive failures, open circuit for 30 seconds
// Use a library: opossum (Node), resilience4j (Java), Polly (.NET)
const breaker = new CircuitBreaker(callExternalService, {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
});
```

### WebSocket Errors

**Connection lifecycle errors:**

| Code | Meaning | Action |
|------|---------|--------|
| 1000 | Normal closure | No action needed |
| 1001 | Going away (server shutdown) | Reconnect with backoff |
| 1006 | Abnormal closure (no close frame) | Network failure; reconnect |
| 1008 | Policy violation | Auth or rate limit issue; check headers |
| 1009 | Message too big | Reduce payload size |
| 1011 | Server error | Retry with backoff |
| 4001 | Unauthorized (custom) | Re-authenticate |
| 4429 | Rate limited (custom) | Backoff and reconnect |

**Reconnection with exponential backoff:**
```typescript
class ReliableWebSocket {
  private attempt = 0;

  connect() {
    const ws = new WebSocket(this.url, {
      headers: { Authorization: `Bearer ${this.token}` },
    });

    ws.on('open', () => { this.attempt = 0; });

    ws.on('close', (code) => {
      if (code === 1000) return; // Normal — don't reconnect
      const delay = Math.min(1000 * 2 ** this.attempt++, 30_000);
      setTimeout(() => this.connect(), delay);
    });

    ws.on('error', (err) => {
      console.error('WebSocket error', err);
    });
  }
}
```

**Auth on WebSockets:**
- HTTP `Authorization` header only works during the initial HTTP upgrade handshake
- After upgrade, use the first message as an auth handshake or include token in URL (use with caution — URLs may appear in logs)
- Some APIs require sending an auth frame immediately after connection

### Debugging API Errors — General Process

1. **Reproduce with a raw HTTP client** — curl, httpie, Insomnia, Postman — to isolate your code from the problem.
2. **Enable verbose logging** — log full request headers (mask credentials), full URL, and full response body.
3. **Check the API status page** — many failures are on the provider's side.
4. **Check request ID / trace ID** — most production APIs return a unique request ID in headers (`X-Request-ID`, `cf-ray`, `x-amzn-requestid`). Include this when filing support requests.
5. **Test in sandbox** — reproduce the error in the API sandbox before debugging production.
6. **Examine headers carefully** — errors often manifest as wrong `Content-Type` (HTML error page vs. JSON), missing auth header, or wrong `Accept` header.
7. **Check for proxy interference** — corporate proxies, CDNs, and API gateways can transform responses and inject errors.
8. **Validate your payload** — use the API's schema validator or OpenAPI linter if available.

**curl reproduction template:**
```bash
curl -v -X POST "https://api.example.com/v1/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}'
```

---

## Part 6: API Documentation

### OpenAPI (REST) Specification

Document every endpoint with a full OpenAPI 3.0 spec:

```yaml
openapi: "3.0.3"
info:
  title: "User API"
  version: "1.0.0"
  description: "User management API"

paths:
  /api/v1/users:
    get:
      summary: List all users
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: per_page
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items: { $ref: "#/components/schemas/User" }
                  meta:
                    $ref: "#/components/schemas/PaginationMeta"

    post:
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/CreateUserInput" }
      responses:
        "201":
          description: User created
          headers:
            Location:
              schema: { type: string }
          content:
            application/json:
              schema:
                type: object
                properties:
                  data: { $ref: "#/components/schemas/User" }
        "422":
          description: Validation error
          content:
            application/json:
              schema: { $ref: "#/components/schemas/ErrorResponse" }

components:
  schemas:
    User:
      type: object
      required: [id, email, createdAt]
      properties:
        id: { type: string }
        email: { type: string, format: email }
        name: { type: string }
        createdAt: { type: string, format: date-time }

    CreateUserInput:
      type: object
      required: [email]
      properties:
        email: { type: string, format: email }
        name: { type: string, maxLength: 100 }

    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            code: { type: string }
            message: { type: string }
            details:
              type: array
              items:
                type: object
                properties:
                  field: { type: string }
                  message: { type: string }
                  code: { type: string }

    PaginationMeta:
      type: object
      properties:
        total: { type: integer }
        page: { type: integer }
        perPage: { type: integer }
        totalPages: { type: integer }

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### GraphQL Schema Documentation

Add descriptions to every type, field, and enum value:

```graphql
"""
A user account in the system.
"""
type User {
  "Globally unique identifier."
  id: ID!

  "The user's email address. Unique across all accounts."
  email: String!

  "Display name. Optional — may be null if not set."
  name: String

  "All posts authored by this user, newest first."
  posts(first: Int = 20, after: String): PostConnection!

  "Whether the user's email has been verified."
  isVerified: Boolean!

  "Account creation timestamp in ISO 8601 format."
  createdAt: DateTime!
}
```

### Documentation Requirements

Every API (REST or GraphQL) must document:
- Authentication method and how to obtain credentials
- All endpoints/operations with request and response schemas
- All error codes and what they mean
- Rate limits (per tier if applicable)
- Pagination behavior
- Field nullability and optionality
- Deprecation notices with sunset dates
- Working code examples in at least one language

---

## Part 7: Design Checklists

### REST API Endpoint Checklist

Before shipping a new endpoint:

- [ ] Resource URL follows naming conventions (plural, kebab-case, no verbs)
- [ ] Correct HTTP method used
- [ ] Appropriate status codes returned (not 200 for everything; 201 + Location on create)
- [ ] Input validated with schema (Zod, Pydantic, etc.) at the boundary only
- [ ] Error responses follow the single standard format
- [ ] Pagination implemented for all list endpoints
- [ ] Authentication required (or explicitly marked as public)
- [ ] Authorization checked (user can only access their own resources)
- [ ] Rate limiting configured
- [ ] Response does not leak internal details (no stack traces, SQL error messages)
- [ ] Naming consistent with existing endpoints
- [ ] OpenAPI spec updated
- [ ] New fields are additive and optional (backward compatible)

### GraphQL Schema Checklist

- [ ] Descriptions added to every type, field, and enum value
- [ ] Non-null (`!`) applied to all fields that cannot be null
- [ ] Lists use `[Type!]!` pattern
- [ ] Input types defined for all mutations
- [ ] Mutations return result objects (not void)
- [ ] Business errors modeled as union result types
- [ ] `Node` interface implemented for refetchable types
- [ ] Connection pattern used for paginated relationships
- [ ] Introspection disabled in production
- [ ] Query depth limit configured
- [ ] Query complexity limit configured
- [ ] Authorization checked at field level where needed
- [ ] No internal implementation details exposed in schema

### Integration Checklist (Consuming a Third-Party API)

- [ ] Auth mechanism understood and tested
- [ ] Rate limits documented and handled
- [ ] All error responses parsed and categorized
- [ ] Retry logic implemented for transient errors (429, 5xx)
- [ ] Timeouts set on all outbound calls
- [ ] External API responses validated before use
- [ ] Circuit breaker or fallback implemented for critical integrations
- [ ] Sandbox tested for all error scenarios
- [ ] API status page bookmarked

---

## Red Flags

- Endpoints that return different shapes depending on conditions
- Inconsistent error formats across endpoints
- Validation scattered throughout internal code instead of at boundaries
- Breaking changes to existing fields without a version bump
- List endpoints without pagination
- Verbs in REST URLs (`/api/createTask`)
- Third-party API responses used without validation
- Timeouts not set on outbound HTTP calls
- Swallowed errors — catch blocks that log but don't propagate or handle
- Rate limit errors not retried with backoff
- Auth tokens hardcoded in source code
- `500 Internal Server Error` leaking stack traces to clients
- `200 OK` responses with `"status": "error"` in the body
- GraphQL `errors` array not checked after every call
