---
name: websocket-manager
description: >
  Full-lifecycle WebSocket skill: create server+client implementations (Node.js/Python),
  fix and debug WebSocket issues, audit existing WebSocket usage in applications, and
  plan the needs and risks of adopting WebSockets for a given requirement. Covers
  Socket.IO, native ws, uWebSockets.js, horizontal scaling with Redis, security,
  presence, rooms, namespaces, and alternatives (SSE, long polling, WebRTC).
version: "1.0.0"
tags:
  - websocket
  - socket.io
  - real-time
  - bidirectional
  - chat
  - presence
  - pub-sub
  - scaling
  - redis
  - debugging
  - audit
  - planning
---

# WebSocket Manager

## Capability Overview

This skill covers four modes of operation:

| Mode | When to use |
|------|-------------|
| **Create** | Building a WebSocket server, client, or full stack from scratch |
| **Fix** | Debugging connection drops, auth failures, scaling bugs, backpressure issues |
| **Audit** | Reviewing existing WS usage for correctness, security, and scalability gaps |
| **Plan** | Evaluating whether WebSockets are the right choice and identifying risks |

---

## Mode: Plan — When to Use WebSockets

### Technology Decision Matrix

| Criterion | WebSocket | SSE | Long Polling | WebRTC |
|-----------|-----------|-----|--------------|--------|
| Bidirectional | Yes | No | Yes | Yes |
| Real-time latency | 5–20ms p99 | 10–50ms p99 | 100–500ms p99 | <10ms p99 |
| Browser support | Excellent | Good | Universal | Good |
| Proxy/firewall issues | Some | Rare | Rare | Some |
| Per-message overhead | 2–6 bytes | ~20 bytes | 500–2000 bytes | Medium |
| Throughput/connection | 10,000+ msg/s | 1,000+ msg/s | 1–10 msg/s | High |
| Max connections/server | 50k–100k | 50k–100k | 10k–20k | N/A |
| Use case fit | Chat, games, collab | Feeds, tickers, notifs | Legacy/fallback | Audio/video/P2P |

### Choose WebSocket when:
- Bidirectional communication is required
- Latency must be < 50ms
- Message frequency > 1 msg/sec per client
- Use cases: chat, multiplayer games, collaborative editing, live dashboards, binary data transfer

### Choose SSE when:
- Server-to-client only (no client → server messages needed)
- Stock tickers, live feeds, push notifications
- Better proxy/corporate firewall compatibility required
- Simpler implementation preferred (automatic reconnection built in)

### Choose Long Polling when:
- Legacy browser support required (IE8/9)
- WebSocket blocked by firewalls in target environment
- Very infrequent updates
- Used only as a fallback transport

### Choose WebRTC when:
- Peer-to-peer communication needed
- Audio/video calls, screen sharing, file transfer between peers

### Key risks when adopting WebSockets:
- **Stateful connections** require sticky sessions or a distributed adapter (Redis); HTTP load balancers don't work out of the box
- **Connection limits** per process (~50k–100k); must plan horizontal scaling before launch
- **Thundering herd** on reconnect after server restart; use jitter in client backoff
- **Memory leaks** from uncleaned presence/room state on disconnect
- **Corporate proxies** may block WebSocket upgrades; keep polling fallback available
- **TCP keepalive is insufficient** for dead connection detection; implement application-level heartbeat
- **No built-in ordering guarantees** under Redis pub/sub with multiple nodes; design for idempotency

---

## Mode: Create — Implementation

### Core Build Workflow

1. **Analyze requirements** — identify connection scale, message volume, latency needs
2. **Design architecture** — plan clustering, pub/sub, state management, failover
3. **Implement** — build server with auth middleware, rooms/namespaces, event handlers
4. **Validate locally** — test with `npx wscat -c ws://localhost:3000`; confirm auth rejection on missing/invalid tokens, room join/leave events, message delivery
5. **Scale** — verify Redis pub/sub round-trip before enabling adapter; configure sticky sessions; test across multiple instances
6. **Monitor** — track connections, latency, throughput, error rates; alert on connection-count spikes and error-rate thresholds

### Output Checklist

Every implementation must include:
- [ ] Server with JWT/cookie authentication middleware
- [ ] Client with reconnection + exponential backoff + message queue
- [ ] Room/namespace organization
- [ ] Typed event definitions
- [ ] Error handling and recovery
- [ ] Heartbeat/ping-pong for dead connection detection
- [ ] Connection cleanup on disconnect (presence, rooms, timers)
- [ ] Rate limiting per socket
- [ ] Redis adapter (or note when not needed for single-instance)
- [ ] Graceful shutdown handler

---

### Node.js Server — Socket.IO (Production-Ready)

```js
import { createServer } from "http";
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";
import jwt from "jsonwebtoken";

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: process.env.ALLOWED_ORIGIN, credentials: true },
  pingTimeout: 20000,
  pingInterval: 25000,
  maxHttpBufferSize: 1e6, // 1MB max message size
});

// Authentication middleware — runs before connection is established
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error("Authentication required"));
  try {
    socket.data.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    next(new Error("Invalid token"));
  }
});

// Redis adapter for horizontal scaling
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));

io.on("connection", (socket) => {
  const { userId } = socket.data.user;
  console.log(`connected: ${userId} (${socket.id})`);

  // Presence: mark user online
  pubClient.hSet("presence", userId, socket.id);

  // Join user personal room
  socket.join(`user:${userId}`);

  socket.on("join-room", async (roomId) => {
    const hasAccess = await checkRoomAccess(userId, roomId);
    if (!hasAccess) {
      socket.emit("error", { message: "Access denied" });
      return;
    }
    socket.join(roomId);
    socket.to(roomId).emit("user-joined", { userId });
  });

  socket.on("leave-room", (roomId) => {
    socket.leave(roomId);
    socket.to(roomId).emit("user-left", { userId });
  });

  socket.on("message", ({ roomId, text }) => {
    if (!socket.rooms.has(roomId)) {
      socket.emit("error", { message: "Not in room" });
      return;
    }
    io.to(roomId).emit("message", { userId, text, ts: Date.now() });
  });

  socket.on("disconnect", () => {
    pubClient.hDel("presence", userId);
    console.log(`disconnected: ${userId}`);
  });

  socket.on("error", (err) => {
    console.error(`Socket error [${userId}]:`, err);
  });
});

// Graceful shutdown
const gracefulShutdown = () => {
  io.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 30000);
};
process.on("SIGTERM", gracefulShutdown);
process.on("SIGINT", gracefulShutdown);

httpServer.listen(3000);
```

### Node.js Server — TypeScript with Namespaces

```typescript
// server.ts
import express from "express";
import { createServer } from "http";
import { Server, Socket } from "socket.io";
import { verifyToken } from "./auth";

const app = express();
const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: { origin: process.env.CLIENT_URL, credentials: true },
  pingInterval: 25000,
  pingTimeout: 60000,
});

// Auth middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error("Authentication required"));
  try {
    socket.data.user = await verifyToken(token);
    next();
  } catch {
    next(new Error("Invalid token"));
  }
});

io.on("connection", (socket: Socket) => {
  const user = socket.data.user;
  socket.join(`user:${user.id}`);

  socket.on("disconnect", () => {
    console.log(`User disconnected: ${user.id}`);
  });
});

// Chat namespace
export function setupChatNamespace(io: Server) {
  const chatNs = io.of("/chat");

  chatNs.on("connection", (socket: Socket) => {
    const user = socket.data.user;

    socket.on("join-room", async (roomId: string) => {
      if (!(await canAccessRoom(user.id, roomId))) {
        socket.emit("error", { message: "Access denied" });
        return;
      }
      socket.join(`room:${roomId}`);
      socket.to(`room:${roomId}`).emit("user-joined", { userId: user.id, name: user.name });
    });

    socket.on("leave-room", (roomId: string) => {
      socket.leave(`room:${roomId}`);
      socket.to(`room:${roomId}`).emit("user-left", { userId: user.id });
    });

    socket.on("send-message", async (data: { roomId: string; content: string }) => {
      const message = await db.message.create({
        data: { roomId: data.roomId, authorId: user.id, content: data.content },
        include: { author: true },
      });
      chatNs.to(`room:${data.roomId}`).emit("new-message", {
        id: message.id,
        content: message.content,
        author: { id: user.id, name: user.name },
        createdAt: message.createdAt,
      });
    });

    socket.on("typing-start", (roomId: string) => {
      socket.to(`room:${roomId}`).emit("user-typing", { userId: user.id, name: user.name });
    });

    socket.on("typing-stop", (roomId: string) => {
      socket.to(`room:${roomId}`).emit("user-stopped-typing", { userId: user.id });
    });
  });

  return chatNs;
}

httpServer.listen(3001);
export { io };
```

### Python Server — aiohttp

```python
from aiohttp import web
import aiohttp
import json
from datetime import datetime

class WebSocketServer:
    def __init__(self):
        self.app = web.Application()
        self.rooms: dict[str, set] = {}
        self.users: dict[str, web.WebSocketResponse] = {}
        self.app.router.add_get("/ws", self.websocket_handler)
        self.app.router.add_post("/api/message", self.send_message_api)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        user_id = None
        room_id = None

        async for msg in ws.iter_any():
            if isinstance(msg, aiohttp.WSMessage):
                data = json.loads(msg.data)
                event_type = data.get("type")
                try:
                    if event_type == "auth":
                        user_id = data.get("userId")
                        self.users[user_id] = ws
                        await ws.send_json({
                            "type": "authenticated",
                            "timestamp": datetime.now().isoformat()
                        })

                    elif event_type == "join_room":
                        room_id = data.get("roomId")
                        if room_id not in self.rooms:
                            self.rooms[room_id] = set()
                        self.rooms[room_id].add(user_id)
                        await self.broadcast_to_room(room_id, {
                            "type": "user_joined",
                            "userId": user_id,
                            "timestamp": datetime.now().isoformat()
                        }, exclude=user_id)

                    elif event_type == "message":
                        message = {
                            "id": f"msg_{datetime.now().timestamp()}",
                            "userId": user_id,
                            "text": data.get("text"),
                            "roomId": room_id,
                            "timestamp": datetime.now().isoformat()
                        }
                        await self.save_message(message)
                        await self.broadcast_to_room(room_id, message)

                    elif event_type == "leave_room":
                        if room_id in self.rooms:
                            self.rooms[room_id].discard(user_id)

                except Exception as error:
                    await ws.send_json({"type": "error", "message": str(error)})

        # Cleanup
        if user_id:
            del self.users[user_id]
        if room_id and user_id and room_id in self.rooms:
            self.rooms[room_id].discard(user_id)
        return ws

    async def broadcast_to_room(self, room_id, message, exclude=None):
        if room_id not in self.rooms:
            return
        for uid in self.rooms[room_id]:
            if uid != exclude and uid in self.users:
                try:
                    await self.users[uid].send_json(message)
                except Exception as e:
                    print(f"Error sending to {uid}: {e}")

    async def save_message(self, message):
        pass  # implement DB persistence

    async def send_message_api(self, request):
        data = await request.json()
        await self.broadcast_to_room(data.get("roomId"), {
            "type": "message",
            "text": data.get("text"),
            "timestamp": datetime.now().isoformat()
        })
        return web.json_response({"sent": True})

if __name__ == "__main__":
    server = WebSocketServer()
    web.run_app(server.app, port=3000)
```

### Native ws Library — Heartbeat

```js
const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080, maxPayload: 1024 * 1024 });

wss.on("connection", (ws) => {
  ws.isAlive = true;
  ws.on("pong", () => { ws.isAlive = true; });
  ws.on("message", (data) => { /* handle */ });
});

// Ping every 30s, terminate unresponsive clients
const heartbeat = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on("close", () => clearInterval(heartbeat));
```

### uWebSockets.js — Maximum Performance

```js
const uWS = require("uWebSockets.js");

uWS.App()
  .ws("/*", {
    compression: uWS.SHARED_COMPRESSOR,
    maxPayloadLength: 16 * 1024,
    idleTimeout: 60,
    open: (ws) => { console.log("connected"); },
    message: (ws, message, isBinary) => { ws.send(message, isBinary); },
    close: (ws, code, message) => { console.log("disconnected"); },
  })
  .listen(9001, (token) => { if (token) console.log("Listening on 9001"); });
```

---

### Client — Socket.IO with Reconnection + Message Queue

```js
import { io } from "socket.io-client";

const socket = io("wss://api.example.com", {
  auth: { token: getAuthToken() },
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,       // initial delay (ms)
  reconnectionDelayMax: 30000,   // cap at 30s
  randomizationFactor: 0.5,      // jitter to prevent thundering herd
  timeout: 20000,
});

let messageQueue = [];

socket.on("connect", () => {
  console.log("connected:", socket.id);
  messageQueue.forEach((msg) => socket.emit("message", msg));
  messageQueue = [];
});

socket.on("disconnect", (reason) => {
  console.warn("disconnected:", reason);
  if (reason === "io server disconnect") socket.connect();
});

socket.on("connect_error", (err) => {
  if (err.message === "Authentication required") {
    redirectToLogin();
  } else {
    console.error("connection error:", err.message);
  }
});

socket.on("reconnect", (n) => {
  console.log(`reconnected after ${n} attempts`);
  socket.emit("sync-state"); // re-sync after reconnect
});

socket.on("reconnect_failed", () => {
  showToast("Connection lost. Please refresh.");
});

function sendMessage(roomId, text) {
  const msg = { roomId, text };
  if (socket.connected) socket.emit("message", msg);
  else messageQueue.push(msg);
}
```

### Client — React Hook (TypeScript)

```typescript
// hooks/useSocket.ts
import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "./useAuth";

export function useSocket({ namespace = "/", autoConnect = true } = {}) {
  const { token } = useAuth();
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !autoConnect) return;

    const socket = io(`${process.env.NEXT_PUBLIC_WS_URL}${namespace}`, {
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    socket.on("connect", () => { setIsConnected(true); setError(null); });
    socket.on("disconnect", () => setIsConnected(false));
    socket.on("connect_error", (err) => { setError(err.message); setIsConnected(false); });

    socketRef.current = socket;
    return () => { socket.disconnect(); };
  }, [token, namespace, autoConnect]);

  const emit = useCallback((event: string, data?: any) => {
    socketRef.current?.emit(event, data);
  }, []);

  const on = useCallback((event: string, handler: (...args: any[]) => void) => {
    socketRef.current?.on(event, handler);
    return () => { socketRef.current?.off(event, handler); };
  }, []);

  return { socket: socketRef.current, isConnected, error, emit, on,
    off: useCallback((event: string, handler?: (...args: any[]) => void) => {
      socketRef.current?.off(event, handler);
    }, []) };
}
```

### Client — Vanilla JS Class

```js
class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.socket = null;
    this.messageQueue = [];
    this.isAuthenticated = false;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.connect();
  }

  connect() {
    this.socket = io(this.url, {
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
    });
    this.socket.on("connect", () => this.processMessageQueue());
    this.socket.on("error", (err) => console.error("Socket error:", err));
    this.socket.on("connect_error", (err) => console.error("Connection error:", err));
  }

  emit(event, data, callback) {
    if (!this.socket.connected) { this.messageQueue.push({ event, data, callback }); return; }
    this.socket.emit(event, data, callback);
  }

  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const { event, data, callback } = this.messageQueue.shift();
      this.socket.emit(event, data, callback);
    }
  }

  on(event, callback) { this.socket.on(event, callback); }
  joinRoom(roomId) { this.emit("room:join", roomId); }
  leaveRoom(roomId) { this.emit("room:leave", roomId); }
  sendMessage(roomId, text) { this.emit("chat:message", { roomId, text }); }
  setTyping(roomId, isTyping) { this.emit(isTyping ? "typing:start" : "typing:stop", roomId); }
  disconnect() { this.socket.disconnect(); }
}
```

---

## Mode: Fix — Debugging Guide

### Common Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Connection immediately drops | Auth middleware rejecting | Log `next(err)` reason; check token source (`auth.token` vs `query.token`) |
| Works on one server, not others | Missing sticky sessions | Enable `ip_hash` in nginx or cookie-based routing |
| Messages lost across pods | Redis adapter not connected | Verify pub/sub round-trip before `io.adapter()` call |
| Memory grows indefinitely | Presence/room not cleaned on disconnect | Always `hDel` / `srem` in `disconnect` handler |
| Client reconnects thrash | No jitter on reconnect delay | Set `randomizationFactor: 0.5` in client config |
| "Max payload size exceeded" | Large message sent | Set `maxPayload` on server, validate client-side before send |
| Dead connections not detected | No heartbeat | Implement ping/pong with `isAlive` flag (see ws example above) |
| CORS rejection | `origin` mismatch in `cors` config | Match exact origin including protocol and port |
| Proxy drops connection after 60s | Proxy timeout | Set `proxy_read_timeout 7d` in nginx; or send periodic pings |

### Debug Commands

```bash
# Test raw WebSocket connection
npx wscat -c ws://localhost:3000

# Test with auth token
npx wscat -c "ws://localhost:3000" --header "Authorization: Bearer <token>"

# Monitor Socket.IO internals (enable debug logging)
DEBUG=socket.io* node server.js

# Check Redis pub/sub is working
redis-cli subscribe socket.io#/#

# Count active connections
redis-cli hlen presence
```

### Auth Failure Debugging

```js
// Add verbose logging to auth middleware
io.use((socket, next) => {
  const token = socket.handshake.auth.token || socket.handshake.query.token;
  console.log("auth attempt:", { socketId: socket.id, hasToken: !!token });
  if (!token) return next(new Error("Authentication required"));
  try {
    socket.data.user = jwt.verify(token, process.env.JWT_SECRET);
    console.log("auth success:", socket.data.user.userId);
    next();
  } catch (err) {
    console.error("auth failure:", err.message);
    next(new Error("Invalid token"));
  }
});
```

### Backpressure Detection

```js
io.on("connection", (socket) => {
  const MAX_BUFFER = 10000;
  let bufferSize = 0;
  const originalEmit = socket.emit.bind(socket);

  socket.emit = function(event, ...args) {
    bufferSize++;
    if (bufferSize > MAX_BUFFER) {
      console.warn(`[${socket.id}] Buffer overflow, dropping message`);
      return false;
    }
    const result = originalEmit(event, ...args);
    socket.once("drain", () => { bufferSize = 0; });
    return result;
  };
});
```

---

## Mode: Audit — Review Checklist

Use this when reviewing WebSocket code in an existing application.

### Security Audit
- [ ] Auth middleware present and runs before `connection` fires
- [ ] Token verified server-side (not just checked for existence)
- [ ] Room access validated before `socket.join()`
- [ ] Write permissions checked before broadcasting
- [ ] Input validated with schema (e.g., Joi) before processing
- [ ] HTML/text sanitized before re-broadcasting (XSS vector)
- [ ] Per-socket rate limiting implemented
- [ ] Per-IP connection limit enforced (`MAX_CONNECTIONS_PER_IP`)
- [ ] `maxHttpBufferSize` set to reasonable value (default 1MB)
- [ ] CORS `origin` is restrictive (not `"*"` in production)
- [ ] Audit logging in place (connect, message, disconnect)

### Reliability Audit
- [ ] Heartbeat/ping-pong implemented (not relying on TCP keepalive)
- [ ] `disconnect` handler cleans up: presence, room membership, timers, Redis keys
- [ ] Client implements reconnect with exponential backoff + jitter
- [ ] Client queues messages during disconnect window
- [ ] `reconnect` event triggers state re-sync from server

### Scalability Audit
- [ ] Redis adapter (or equivalent) configured for multi-instance deployment
- [ ] Sticky sessions configured at load balancer
- [ ] Per-instance connection limit enforced before accepting new connections
- [ ] Shared state stored in Redis (not in-process memory)
- [ ] Graceful shutdown handler in place (drains connections before exit)
- [ ] HPA or autoscaling configured based on connection count, not just CPU

### Code Quality Audit
- [ ] Rooms/namespaces used for message scoping (not manual filtering)
- [ ] Volatile emit used for high-frequency telemetry (tolerable drops)
- [ ] Acknowledgments used for critical messages requiring delivery confirmation
- [ ] Admin events protected by role check
- [ ] No unbounded in-memory structures (message queues, presence maps)

---

## Patterns Reference

### Broadcasting Patterns (Socket.IO)

```js
io.emit("event", data);                        // Everyone
socket.broadcast.emit("event", data);          // Everyone except sender
io.to("room1").emit("event", data);            // Specific room (includes sender)
socket.to("room1").emit("event", data);        // Room except sender
io.to("room1").to("room2").emit("event", data); // Multiple rooms
io.of("/namespace").emit("event", data);       // All in namespace
socket.volatile.emit("telemetry", data);       // Drop if client not ready
```

### Acknowledgments

```js
// Server requests acknowledgment with timeout
socket.timeout(5000).emit("request", data, (err, response) => {
  if (err) console.log("No ack within 5s");
  else console.log("Response:", response);
});

// Client sends ack
socket.on("save-data", (data, callback) => {
  try {
    saveToDatabase(data);
    callback({ success: true });
  } catch (err) {
    callback({ success: false, error: err.message });
  }
});
```

### Presence System (Redis-backed, multi-instance safe)

```js
class PresenceManager {
  constructor(redisClient) { this.redis = redisClient; }

  async userConnected(userId, socketId) {
    const key = `user:${userId}:sockets`;
    await this.redis.sadd(key, socketId);
    await this.redis.expire(key, 3600);
    const count = await this.redis.scard(key);
    if (count === 1) {
      await this.redis.hset("presence", userId, JSON.stringify({ status: "online", lastSeen: Date.now() }));
      // Notify friends via io.to(`user:${friendId}`)
    }
    return count;
  }

  async userDisconnected(userId, socketId) {
    const key = `user:${userId}:sockets`;
    await this.redis.srem(key, socketId);
    const count = await this.redis.scard(key);
    if (count === 0) {
      await this.redis.hset("presence", userId, JSON.stringify({ status: "offline", lastSeen: Date.now() }));
    }
    return count;
  }

  async getBulkPresence(userIds) {
    const pipeline = this.redis.pipeline();
    userIds.forEach((id) => pipeline.hget("presence", id));
    const results = await pipeline.exec();
    return userIds.map((id, i) => ({
      userId: id,
      ...JSON.parse(results[i][1] || '{"status":"offline"}'),
    }));
  }
}
```

### Notification Service

```typescript
export class NotificationService {
  static sendToUser(userId: string, event: string, data: any) {
    io.to(`user:${userId}`).emit(event, data);
  }
  static sendToUsers(userIds: string[], event: string, data: any) {
    userIds.forEach((id) => io.to(`user:${id}`).emit(event, data));
  }
  static broadcast(event: string, data: any) { io.emit(event, data); }
  static sendToRoom(roomId: string, event: string, data: any) {
    io.to(`room:${roomId}`).emit(event, data);
  }
}
```

### Message Queue Pattern (offline delivery)

```js
const messageQueue = new Map(); // userId → Message[]

async function sendMessage(userId, message) {
  const userOnline = await isUserOnline(userId);
  if (userOnline) {
    io.to(`user:${userId}`).emit("message", message);
  } else {
    const queue = messageQueue.get(userId) || [];
    queue.push(message);
    messageQueue.set(userId, queue);
    await saveMessageToDb(userId, message); // persist for longer-term storage
  }
}

io.on("connection", (socket) => {
  const userId = socket.data.user.userId;
  const queued = messageQueue.get(userId) || [];
  if (queued.length > 0) {
    socket.emit("queued-messages", queued);
    messageQueue.delete(userId);
  }
});
```

---

## Security Reference

### Auth: JWT (preferred)

```js
io.use((socket, next) => {
  const token = socket.handshake.auth.token; // prefer auth.token over query param
  if (!token) return next(new Error("Authentication error: No token provided"));
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.userId = decoded.userId;
    socket.username = decoded.username;
    next();
  } catch {
    next(new Error("Authentication error: Invalid token"));
  }
});
```

> Avoid `socket.handshake.query.token` — query params appear in server logs. Use `handshake.auth.token` instead.

### Auth: Cookie / Session

```js
io.use((socket, next) => {
  cookieParser(process.env.COOKIE_SECRET)(socket.request, {}, () => {
    const sessionId = socket.request.signedCookies.sessionId;
    if (!sessionId) return next(new Error("No session"));
    verifySession(sessionId)
      .then((user) => { socket.userId = user.id; next(); })
      .catch(() => next(new Error("Invalid session")));
  });
});
```

### Authorization: Room Access + Role Guards

```js
// Room access check
socket.on("join-room", async (roomId) => {
  if (!(await checkRoomAccess(socket.userId, roomId))) {
    socket.emit("error", { message: "Access denied to room" });
    return;
  }
  socket.join(roomId);
});

// Role-based event guard
const ADMIN_EVENTS = ["kick-user", "ban-user", "delete-message"];
ADMIN_EVENTS.forEach((event) => {
  socket.on(event, async (data) => {
    if (socket.role !== "admin") {
      socket.emit("error", { message: "Admin access required" });
      return;
    }
    await handleAdminAction(event, data);
  });
});
```

### Rate Limiting

```js
// In-process (single instance)
class SocketRateLimiter {
  constructor(maxRequests = 100, windowMs = 60000) {
    this.max = maxRequests; this.window = windowMs; this.requests = new Map();
  }
  check(socketId) {
    const now = Date.now();
    const valid = (this.requests.get(socketId) || []).filter((t) => now - t < this.window);
    if (valid.length >= this.max) return false;
    valid.push(now); this.requests.set(socketId, valid); return true;
  }
  reset(socketId) { this.requests.delete(socketId); }
}

// Distributed (Redis, cluster-safe)
async function checkRateLimit(userId, maxRequests = 100, windowSec = 60) {
  const key = `rate_limit:${userId}`;
  const now = Date.now();
  const pipeline = redis.pipeline();
  pipeline.zremrangebyscore(key, 0, now - windowSec * 1000);
  pipeline.zcard(key);
  pipeline.zadd(key, now, `${now}-${Math.random()}`);
  pipeline.expire(key, windowSec);
  const results = await pipeline.exec();
  return results[1][1] < maxRequests;
}
```

### Input Validation + XSS

```js
const Joi = require("joi");
const sanitizeHtml = require("sanitize-html");

const messageSchema = Joi.object({
  roomId: Joi.string().uuid().required(),
  text: Joi.string().min(1).max(1000).required(),
  attachments: Joi.array().items(Joi.string().uri()).max(5).optional(),
});

socket.on("message", (data) => {
  const { error, value } = messageSchema.validate(data);
  if (error) { socket.emit("error", { message: "Invalid format", details: error.details }); return; }
  value.text = sanitizeHtml(value.text, { allowedTags: [], allowedAttributes: {} });
  io.to(value.roomId).emit("message", { userId: socket.userId, ...value, ts: Date.now() });
});
```

### DDoS: Per-IP Connection Limits

```js
const connectionLimits = new Map();
const MAX_PER_IP = 10;

io.engine.on("connection", (rawSocket) => {
  const ip = rawSocket.request.headers["x-forwarded-for"] ||
             rawSocket.request.connection.remoteAddress;
  const count = connectionLimits.get(ip) || 0;
  if (count >= MAX_PER_IP) { rawSocket.close(1008, "Too many connections from IP"); return; }
  connectionLimits.set(ip, count + 1);
  rawSocket.on("close", () => {
    const n = connectionLimits.get(ip) - 1;
    n <= 0 ? connectionLimits.delete(ip) : connectionLimits.set(ip, n);
  });
});
```

### Audit Logging

```js
const winston = require("winston");
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.File({ filename: "websocket-audit.log" })],
});

io.on("connection", (socket) => {
  logger.info("Connection", { socketId: socket.id, userId: socket.userId, ip: socket.handshake.address, ts: Date.now() });
  socket.on("message", (data) => {
    logger.info("Message", { socketId: socket.id, userId: socket.userId, roomId: data.roomId, len: data.text?.length, ts: Date.now() });
  });
  socket.on("disconnect", (reason) => {
    logger.info("Disconnect", { socketId: socket.id, userId: socket.userId, reason, ts: Date.now() });
  });
});
```

---

## Scaling Reference

### Architecture

```
┌─────────────────────────┐
│   Load Balancer         │  (nginx/HAProxy — sticky sessions required)
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
  ┌───▼───┐     ┌───▼───┐
  │ WS #1 │ ... │ WS #N │   (Socket.IO servers)
  └───┬───┘     └───┬───┘
      │             │
      └──────┬──────┘
             │
         ┌───▼───┐
         │ Redis │  (pub/sub adapter)
         └───────┘
```

### Redis Adapter

```js
// Standard pub/sub adapter
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));

// Redis Streams adapter (reliable delivery, replay)
import { createAdapter as createStreamsAdapter } from "@socket.io/redis-streams-adapter";
const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();
io.adapter(createStreamsAdapter(redisClient, { streamName: "socket.io-stream", maxLen: 10000, readCount: 100 }));
```

### Nginx — Sticky Sessions + WebSocket Proxy

```nginx
upstream websocket_backend {
    ip_hash;  # sticky sessions by IP
    server ws1.example.com:3000;
    server ws2.example.com:3000;
    server ws3.example.com:3000;
}

server {
    listen 80;
    server_name example.com;

    location /socket.io/ {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
}
```

### HAProxy — Sticky Sessions

```haproxy
frontend websocket_frontend
    bind *:80
    mode http
    use_backend websocket_backend

backend websocket_backend
    mode http
    balance source
    hash-type consistent
    option httpchk GET /health
    http-check expect status 200
    server ws1 10.0.1.1:3000 check
    server ws2 10.0.1.2:3000 check
    server ws3 10.0.1.3:3000 check
```

### Cookie-Based Sticky Sessions (when IP hash is unreliable)

```js
// Server: set affinity cookie
io.engine.on("connection", (rawSocket) => {
  rawSocket.request.res.setHeader(
    "Set-Cookie",
    `io=${process.env.SERVER_ID}; Path=/; HttpOnly; SameSite=Lax`
  );
});
```

```nginx
# Nginx: route by cookie
map $cookie_io $backend_server {
    "server1" ws1.example.com:3000;
    "server2" ws2.example.com:3000;
    default   websocket_backend;
}
location /socket.io/ {
    proxy_pass http://$backend_server;
}
```

### Per-Server Connection Cap

```js
const MAX_CONNECTIONS = 50000;
io.engine.on("connection", (socket) => {
  if (io.engine.clientsCount > MAX_CONNECTIONS) {
    socket.close(1008, "Server at capacity");
  }
});
```

### Node.js Cluster (multi-core)

```js
const cluster = require("cluster");
const os = require("os");

if (cluster.isMaster) {
  const n = os.cpus().length;
  for (let i = 0; i < n; i++) cluster.fork();
  cluster.on("exit", (worker) => { console.log(`Worker ${worker.process.pid} died`); cluster.fork(); });
} else {
  const io = require("./socket-server");
  io.listen(3000);
}
```

### Kubernetes HPA — Connection-Based Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: websocket-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: websocket-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: websocket_connections
      target:
        type: AverageValue
        averageValue: "40000"
```

---

## Protocol Reference

### Handshake

```
Client → Server:
GET /socket.io/?EIO=4&transport=websocket HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Version: 13

Server → Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
```

### Opcodes

```js
const OPCODES = {
  CONTINUATION: 0x0,
  TEXT: 0x1,
  BINARY: 0x2,
  CLOSE: 0x8,
  PING: 0x9,
  PONG: 0xA,
};
```

### Close Codes

```js
const CLOSE_CODES = {
  1000: "Normal Closure",
  1001: "Going Away",
  1002: "Protocol Error",
  1003: "Unsupported Data",
  1005: "No Status Received",
  1006: "Abnormal Closure",
  1007: "Invalid Payload",
  1008: "Policy Violation",
  1009: "Message Too Big",
  1010: "Mandatory Extension",
  1011: "Internal Server Error",
  1015: "TLS Handshake Fail",
};
```

### Compression

```js
const wss = new WebSocket.Server({
  port: 8080,
  perMessageDeflate: {
    zlibDeflateOptions: { chunkSize: 1024, memLevel: 7, level: 3 },
    zlibInflateOptions: { chunkSize: 10 * 1024 },
    clientNoContextTakeover: true,
    serverNoContextTakeover: true,
    serverMaxWindowBits: 10,
    concurrencyLimit: 10,
    threshold: 1024, // only compress messages > 1KB
  },
});
```

### Binary Data

```js
// Server send
ws.send(Buffer.from([0x00, 0x01, 0x02, 0x03]), { binary: true });

// Server receive
ws.on("message", (data) => {
  if (data instanceof Buffer) console.log("binary:", data);
  else console.log("text:", data.toString());
});

// Browser receive
socket.binaryType = "arraybuffer";
socket.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    const view = new Uint8Array(event.data);
    console.log("binary:", view);
  }
};
```

### WebSocket vs Socket.IO

| Feature | WebSocket (ws) | Socket.IO |
|---------|---------------|-----------|
| Protocol | Native WS | WS + fallbacks |
| Reconnection | Manual | Automatic |
| Broadcasting | Manual | Built-in |
| Rooms | Manual | Built-in |
| Acknowledgments | Manual | Built-in |
| Binary | Native | Converted |
| Overhead | Minimal | Higher |
| Fallback | None | Long polling, SSE |

---

## Standard Message Schema

```json
// Authentication
{ "type": "auth", "userId": "user123", "token": "jwt_token_here" }

// Chat message
{ "type": "message", "roomId": "room123", "text": "Hello!", "timestamp": "2025-01-15T10:30:00Z" }

// Typing indicator
{ "type": "typing", "roomId": "room123", "isTyping": true }

// Presence
{ "type": "presence", "status": "online|away|offline" }

// Notification
{ "type": "notification", "title": "New message", "body": "You have a new message", "data": {} }
```

---

## SSE Reference (Alternative to WebSocket)

### When SSE is Better

- One-way server → client only
- Stock tickers, live feeds, news/notifications
- Better proxy/firewall compatibility needed
- Simpler implementation, automatic reconnection

### SSE Server (Node.js/Express)

```js
const express = require("express");
const app = express();

class SSEManager {
  constructor() { this.clients = new Set(); }
  addClient(res) { this.clients.add(res); }
  removeClient(res) { this.clients.delete(res); }
  broadcast(event, data) {
    const message = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    this.clients.forEach((client) => client.write(message));
  }
}

const sse = new SSEManager();

app.get("/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.write('data: {"message":"Connected"}\n\n');
  sse.addClient(res);
  req.on("close", () => sse.removeClient(res));
});

app.listen(3000);
```

### SSE Client

```js
const eventSource = new EventSource("http://localhost:3000/events");
eventSource.onmessage = (event) => { const data = JSON.parse(event.data); console.log(data); };
eventSource.onerror = (err) => { console.error("SSE error:", err); };
eventSource.addEventListener("update", (event) => { console.log("Update:", event.data); });
// eventSource.close(); // to disconnect
```

### Socket.IO Hybrid Fallback

```js
const io = require("socket.io")(3000, {
  transports: ["websocket", "polling"], // try WS first, fall back to polling
  upgrade: true,
  allowUpgrades: true,
});

io.on("connection", (socket) => {
  console.log("Transport:", socket.conn.transport.name);
  socket.conn.on("upgrade", () => console.log("Upgraded to:", socket.conn.transport.name));
});
```

---

## Constraints

### MUST DO
- Use sticky sessions for load balancing (WebSocket connections are stateful)
- Implement heartbeat/ping-pong — TCP keepalive alone is insufficient for dead connection detection
- Use rooms/namespaces for message scoping, not application-layer filtering
- Queue messages client-side during disconnection to avoid silent data loss
- Plan connection limits per instance before scaling horizontally
- Clean up all state on disconnect: presence records, room membership, in-flight timers, Redis keys

### MUST NOT DO
- Store large state in-process without a clustering strategy (use Redis)
- Use `query.token` for auth in production (appears in server logs); use `handshake.auth.token`
- Mix WebSocket and HTTP on the same port without explicit upgrade handling
- Skip load testing before production — connection-count spikes behave differently from HTTP traffic
- Allow unbounded in-memory growth (message queues, presence maps, connection maps)
- Use `"*"` as CORS origin in production
- Forget graceful shutdown (drain connections before process exit)
