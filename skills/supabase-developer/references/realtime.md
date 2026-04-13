# Realtime

Supabase Realtime enables WebSocket-based subscriptions to database changes, broadcast messaging, and presence tracking.

**Enable Realtime:** Dashboard → Database → Replication → enable replication for target tables, choose events (INSERT/UPDATE/DELETE). RLS is respected — users only receive changes for rows they have access to.

---

## Connect via WebSocket

```bash
WS_URL=$(echo "$SUPABASE_URL" | sed 's/https:/wss:/')
websocat "${WS_URL}/realtime/v1/websocket?apikey=${SUPABASE_KEY}&vsn=1.0.0"
```

**Install websocat:** `brew install websocat` (macOS) or download from GitHub releases (Linux).

---

## Database Change Subscriptions

**Subscribe to all changes on a table:**
```bash
echo '{
  "topic": "realtime:public:users",
  "event": "phx_join",
  "payload": {
    "config": {
      "postgres_changes": [{"event": "*", "schema": "public", "table": "users"}]
    }
  },
  "ref": "1"
}' | websocat "${WS_URL}/realtime/v1/websocket?apikey=${SUPABASE_KEY}&vsn=1.0.0"
```

**Event values:** `"*"` (all), `"INSERT"`, `"UPDATE"`, `"DELETE"`

**Filter subscriptions:**
```json
{
  "config": {
    "postgres_changes": [{
      "event": "*",
      "schema": "public",
      "table": "users",
      "filter": "status=eq.active"
    }]
  }
}
```

---

## Broadcast Messaging

```bash
# Join channel
JOIN='{
  "topic": "realtime:chat-room-1",
  "event": "phx_join",
  "payload": {"config": {"broadcast": {"self": true}}},
  "ref": "1"
}'

# Send broadcast
BROADCAST='{
  "topic": "realtime:chat-room-1",
  "event": "broadcast",
  "payload": {
    "type": "message",
    "event": "new_message",
    "payload": {"user": "Alice", "message": "Hello!"}
  },
  "ref": "2"
}'

{ echo "$JOIN"; sleep 1; echo "$BROADCAST"; } | \
  websocat "${WS_URL}/realtime/v1/websocket?apikey=${SUPABASE_KEY}&vsn=1.0.0"
```

---

## Presence Tracking

```json
// Join with presence
{
  "topic": "realtime:lobby",
  "event": "phx_join",
  "payload": {"config": {"presence": {"key": "user-123"}}},
  "ref": "1"
}

// Track state
{
  "topic": "realtime:lobby",
  "event": "presence",
  "payload": {
    "type": "presence",
    "event": "track",
    "payload": {"user_id": "123", "username": "Alice", "status": "online"}
  },
  "ref": "2"
}
```

---

## Message Formats

**Subscription confirmation:**
```json
{"event": "phx_reply", "payload": {"status": "ok"}, "ref": "1", "topic": "realtime:public:users"}
```

**INSERT event:**
```json
{
  "event": "postgres_changes",
  "payload": {
    "data": {
      "commit_timestamp": "2023-01-01T12:00:00Z",
      "record": {"id": 123, "name": "John"},
      "schema": "public", "table": "users", "type": "INSERT"
    }
  }
}
```

**UPDATE event:** includes both `old_record` and `record` in `data`.

**DELETE event:** includes `old_record` in `data`.

---

## Practical Scripts

**Continuous listener:**
```bash
#!/bin/bash
TABLE="users"
WS_URL=$(echo "$SUPABASE_URL" | sed 's/https:/wss:/')

echo '{
  "topic": "realtime:public:'"$TABLE"'",
  "event": "phx_join",
  "payload": {"config": {"postgres_changes": [{"event": "*", "schema": "public", "table": "'"$TABLE"'"}]}},
  "ref": "1"
}' | websocat "${WS_URL}/realtime/v1/websocket?apikey=${SUPABASE_KEY}&vsn=1.0.0" | \
while IFS= read -r line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $(echo "$line" | jq -c '.')"
done
```

**Process changes with handlers:**
```bash
websocat "${WS_URL}/realtime/v1/websocket?apikey=${SUPABASE_KEY}&vsn=1.0.0" | \
while IFS= read -r line; do
    event_type=$(echo "$line" | jq -r '.payload.data.type // empty')
    case "$event_type" in
        "INSERT") echo "INSERT: $(echo "$line" | jq '.payload.data.record')" ;;
        "UPDATE") echo "UPDATE: $(echo "$line" | jq '.payload.data.record')" ;;
        "DELETE") echo "DELETE: $(echo "$line" | jq '.payload.data.old_record')" ;;
    esac
done
```

**Alternative: REST polling (when WebSockets aren't available):**
```bash
LAST_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
while true; do
    new_records=$(curl -s "${SUPABASE_URL}/rest/v1/users?updated_at=gt.${LAST_TIMESTAMP}&order=updated_at.asc" \
      -H "apikey: ${SUPABASE_KEY}")
    if [[ "$new_records" != "[]" ]]; then
        echo "$new_records" | jq '.'
        LAST_TIMESTAMP=$(echo "$new_records" | jq -r '.[-1].updated_at')
    fi
    sleep 5
done
```

---

## Limitations

- WebSocket connections require persistent connection management
- Bash is not ideal for production WebSocket handling — use Node.js or Python for production apps
- Connection drops require reconnection logic (not automatic in bash)
- Connection limits vary by Supabase plan

**Realtime is good in bash for:** development/debugging tools, simple monitoring scripts, log streaming, testing.

---

## Full API Reference

https://supabase.com/docs/guides/realtime
