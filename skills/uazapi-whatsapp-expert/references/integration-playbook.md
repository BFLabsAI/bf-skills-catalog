# Uazapi Integration Playbook

## Implementation Sequence

1. Choose the endpoint family and operation.
2. Confirm whether auth is `token`, `admintoken`, or a query-string token for SSE.
3. Read the exact request schema in `references/uazapi-openapi-spec.yaml`.
4. Encode Uazapi-specific behavior in the client abstraction.
5. Add operational verification for session state, queue state, or webhook safety.

## Practical Defaults

### Sending Messages

- Build a shared send request base for `number`, `delay`, `readchat`, `readmessages`, `replyid`, `mentions`, `forward`, `track_source`, `track_id`, and `async`
- Surface destination type clearly: phone, user JID, or group JID
- Distinguish synchronous API success from asynchronous delivery success

### Webhooks

- Default to simple mode
- Recommend `excludeMessages: ["wasSentByApi"]`
- Explain that `GET /webhook` returns an array
- Use dynamic URL path options only when the receiver is designed for them

### SSE

- Pass `token` and `events` in the query string
- Treat the connection as long-lived and reconnectable
- Filter event types aggressively to avoid noisy consumers

### Instance Management

- Check instance status before message-heavy operations
- Surface `disconnected`, `connecting`, and `connected` explicitly in application state
- Expect capacity or environment constraints on some operations

## Common Failure Modes

### Auth mismatch

Symptoms:

- `401` on otherwise valid payloads

Likely cause:

- Used `token` where `admintoken` was required, or treated SSE like a header-auth endpoint

### Webhook loops

Symptoms:

- Recursive message storms after automated replies

Likely cause:

- Did not exclude `wasSentByApi` and did not detect self-originated events

### False-positive send success

Symptoms:

- API returns `200` but message is never delivered

Likely cause:

- Used `async: true` and assumed enqueue success meant delivery success

### Destination format errors

Symptoms:

- Message routing failures or unexpected target lookup problems

Likely cause:

- Passed a raw phone number where a group JID or user JID was required

### Environment restrictions

Symptoms:

- `403` or disabled behavior on admin/global operations

Likely cause:

- Running against a public/demo environment with restricted features

## Output Patterns To Prefer

- Small typed clients grouped by domain
- `curl` examples that show the correct header/query auth shape
- Webhook receivers with loop-prevention comments and validation
- Worker/job logic that reconciles enqueue responses with follow-up status checks
- Thin DTOs or validators that follow the OpenAPI schema instead of hand-wavy field guesses
