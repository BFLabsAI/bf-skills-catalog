---
name: open-router-master
description: >
  OpenRouter master skill — complete gateway to 300+ AI models. Covers free model discovery,
  model search and filtering, model comparison, provider performance, trending models, and
  expert-level OpenRouter API usage via the official @openrouter/sdk (callModel, Zod tools,
  stop conditions, OAuth PKCE, account management) and via the OpenAI-compatible SDK and raw
  HTTP. Use when the user asks anything about OpenRouter models, pricing, free models, API
  integration, TypeScript SDK, or wants to compare or select models.
version: 2.0.0
category: ai-service
tags:
  - openrouter
  - llm
  - ai
  - free-models
  - model-comparison
  - api
  - streaming
  - cost-optimization
  - multi-model
  - typescript-sdk
  - callmodel
  - oauth
  - tool-use
requires_tools: []
---

# OpenRouter Master Skill

Complete reference for OpenRouter: discover models (including all free ones), compare models,
find the right provider, and build production-grade integrations.

## Prerequisites

- `OPENROUTER_API_KEY` — optional for most queries; required for `get-endpoints.ts`. Get one at https://openrouter.ai/keys
- Node + `npx tsx`, or Bun (`bun run`) for the trending models script

## First-Time Setup

```bash
cd <skill-path>/scripts && npm install
```

---

## Decision Tree

| User wants to... | Script / Action |
|---|---|
| List all free models | `free-models.ts` |
| Find free models by type/query | `free-models.ts "embedding"` |
| Find free multimodal models | `free-models.ts --modality image` |
| List all models | `list-models.ts` |
| Find cheapest models | `list-models.ts --sort price` |
| Find newest models | `list-models.ts --sort newest` |
| Find largest context models | `list-models.ts --sort context` |
| Find models in a category | `list-models.ts --category programming` |
| Search models by name/provider | `search-models.ts "grok"` |
| Search image-capable models | `search-models.ts --modality image` |
| Resolve informal model name | `resolve-model.ts "claude sonnet"` |
| List a specific model's details | `search-models.ts "exact-model-id"` |
| Compare two or more models | `compare-models.ts A B` |
| Know which model is best (A vs B) | `compare-models.ts A B` + interpret |
| Check provider latency / uptime | `get-endpoints.ts "model-id"` |
| Find fastest provider | `get-endpoints.ts "model-id" --sort throughput` |
| Get trending coding models | `bun run scripts/get-trending-models.ts` |
| Build chat completion API calls | See **API Expert** section |
| Use official TypeScript SDK | See **Official SDK (`@openrouter/sdk`)** section |
| Implement streaming | See **Streaming** section |
| Use function calling / tools | See **Function Calling** / **Tool System** sections |
| Multi-turn agents with stop conditions | See **Official SDK → Stop Conditions** |
| OAuth PKCE for user-facing apps | See **Account & Auth Management** section |
| Manage API keys programmatically | See **Account & Auth Management** section |

---

## Free Models

Free models have `pricing.prompt = "0"` and `pricing.completion = "0"`. Many are variants
with a `:free` suffix (e.g. `google/gemini-2.0-flash-exp:free`).

**Always show pricing when a model is NOT free.** For free models, display `FREE` explicitly.

### List All Free Models

```bash
cd <skill-path>/scripts && npx tsx free-models.ts
```

### Find Free Models by Query

Query matches model ID, name, and description.

```bash
# All free embedding models
cd <skill-path>/scripts && npx tsx free-models.ts "embedding"

# All free Llama models
cd <skill-path>/scripts && npx tsx free-models.ts "llama"

# All free Gemini models
cd <skill-path>/scripts && npx tsx free-models.ts "gemini"

# All free Grok models
cd <skill-path>/scripts && npx tsx free-models.ts "grok"

# All free coding / programming models
cd <skill-path>/scripts && npx tsx free-models.ts "code"
```

### Find Free Models by Modality

```bash
# Free models that accept images
cd <skill-path>/scripts && npx tsx free-models.ts --modality image

# Free audio models
cd <skill-path>/scripts && npx tsx free-models.ts --modality audio

# Free text-only models
cd <skill-path>/scripts && npx tsx free-models.ts --modality text
```

### Sort Free Models

```bash
# By context window (largest first)
cd <skill-path>/scripts && npx tsx free-models.ts --sort context

# Most recently added
cd <skill-path>/scripts && npx tsx free-models.ts --sort newest

# Highest max output tokens
cd <skill-path>/scripts && npx tsx free-models.ts --sort throughput

# Combine query + sort
cd <skill-path>/scripts && npx tsx free-models.ts "llama" --sort context
```

### Free Model Output Fields

```json
{
  "id": "google/gemini-2.0-flash-exp:free",
  "name": "Google: Gemini 2.0 Flash Experimental (free)",
  "description": "...",
  "context_length": 1048576,
  "pricing": { "prompt": "0", "completion": "0" },
  "is_free": true,
  "modality": "text+image->text",
  "input_modalities": ["text", "image"],
  "output_modalities": ["text"],
  "architecture": { "tokenizer": "Gemini", "modality": "text+image->text" },
  "top_provider": { "context_length": 1048576, "max_completion_tokens": 8192 },
  "supported_parameters": ["max_tokens", "temperature", "tools", "..."]
}
```

### Presenting Free Model Results

- Show `FREE` badge instead of dollar amounts for zero-cost models
- Include context length and modalities — key differentiators among free tiers
- Note rate limits: free models often have lower RPM/TPM than paid tiers
- Flag `expiration_date` if present — free models are frequently experimental
- When a user asks "best free model for X", sort by context length or check `supported_parameters` for `tools` / `reasoning`

---

## Model Discovery

### List All Models

```bash
cd <skill-path>/scripts && npx tsx list-models.ts
cd <skill-path>/scripts && npx tsx list-models.ts --sort newest
cd <skill-path>/scripts && npx tsx list-models.ts --sort price
cd <skill-path>/scripts && npx tsx list-models.ts --sort context
cd <skill-path>/scripts && npx tsx list-models.ts --sort throughput
cd <skill-path>/scripts && npx tsx list-models.ts --category programming
```

Categories: `programming`, `roleplay`, `marketing`, `marketing/seo`, `technology`, `science`,
`translation`, `legal`, `finance`, `health`, `trivia`, `academia`

### Search Models by Name or Modality

```bash
cd <skill-path>/scripts && npx tsx search-models.ts "claude"
cd <skill-path>/scripts && npx tsx search-models.ts "gpt"
cd <skill-path>/scripts && npx tsx search-models.ts --modality image
cd <skill-path>/scripts && npx tsx search-models.ts "gpt" --modality text
```

Modalities: `text`, `image`, `audio`, `file`

### Resolve an Informal Model Name

Use before feeding a model name into other scripts:

```bash
cd <skill-path>/scripts && npx tsx resolve-model.ts "claude sonnet"
cd <skill-path>/scripts && npx tsx resolve-model.ts "gpt 4o mini"
cd <skill-path>/scripts && npx tsx resolve-model.ts "llama 3.1"
```

Confidence levels:

| Confidence | Score | Action |
|---|---|---|
| `high` (≥0.85) | Use the model directly — unambiguous match |
| `medium` (≥0.55) | Confirm with user before proceeding |
| `low` (≥0.30) | Ask user to clarify |

**Two-step workflow:** `resolve-model.ts` → feed resolved `id` into other scripts.

---

## Model Details

To get full details for a specific model, use `search-models.ts` with the model ID:

```bash
cd <skill-path>/scripts && npx tsx search-models.ts "anthropic/claude-sonnet-4"
```

### Key Fields to Highlight

| Field | Meaning |
|---|---|
| `pricing.prompt` / `pricing.completion` | Cost per token in USD; multiply ×1,000,000 for per-million rate |
| `context_length` | Max total tokens (input + output) |
| `top_provider.max_completion_tokens` | Max output tokens |
| `top_provider.is_moderated` | Whether content moderation is applied |
| `architecture.modality` | e.g. `text+image->text` (multimodal input, text output) |
| `input_modalities` | What the model can accept as input |
| `output_modalities` | What the model produces |
| `supported_parameters` | Which API params work: `tools`, `reasoning`, `structured_outputs`, `web_search_options` |
| `expiration_date` | Non-null = model is being deprecated |

**Pricing display rule**: Always show pricing in per-million-tokens format. For paid models,
never omit the price. For free models, show `FREE ($0.00 / 1M tokens)`.

---

## Model Comparison

Compare two or more models side-by-side. Uses exact ID matching.

```bash
cd <skill-path>/scripts && npx tsx compare-models.ts "anthropic/claude-sonnet-4" "openai/gpt-4o"
cd <skill-path>/scripts && npx tsx compare-models.ts "anthropic/claude-sonnet-4" "openai/gpt-4o" "google/gemini-2.5-pro"
cd <skill-path>/scripts && npx tsx compare-models.ts "anthropic/claude-sonnet-4" "openai/gpt-4o" --sort price
```

Sort options: `price` (cheapest first), `context` (largest first), `speed`/`throughput`

### Comparison Output

```json
[
  {
    "id": "anthropic/claude-sonnet-4",
    "name": "Anthropic: Claude Sonnet 4",
    "context_length": 1000000,
    "max_completion_tokens": 64000,
    "pricing_per_million_tokens": {
      "prompt": "$3.00",
      "completion": "$15.00",
      "cached_input": "$0.30"
    },
    "modalities": { "input": ["text", "image"], "output": ["text"] },
    "supported_parameters": ["max_tokens", "temperature", "tools", "reasoning"],
    "is_moderated": false
  }
]
```

### How to Determine "Which Model Is Best?"

After running `compare-models.ts`, evaluate based on the user's priority:

| Priority | Winning signal |
|---|---|
| **Cost** | Lowest `pricing_per_million_tokens.prompt` + `.completion` |
| **Context window** | Highest `context_length` |
| **Speed / throughput** | Highest `max_completion_tokens`; verify with `get-endpoints.ts --sort throughput` |
| **Multimodal** | Check `modalities.input` includes `image`, `audio`, etc. |
| **Tool use / agents** | `supported_parameters` includes `tools` and `structured_outputs` |
| **Reasoning tasks** | `supported_parameters` includes `reasoning` |
| **Caching savings** | Presence of `cached_input` pricing (90%+ savings on repeated context) |

Always present a recommendation with a one-line rationale, e.g.:
> "For cost-sensitive production use, **Gemini 2.5 Flash** wins at $0.075/1M vs $3.00/1M for Claude Sonnet 4, with a comparable 1M context window."

---

## Provider Performance

Get per-provider latency, uptime, and throughput for any model. Requires `OPENROUTER_API_KEY`.

```bash
cd <skill-path>/scripts && npx tsx get-endpoints.ts "anthropic/claude-sonnet-4"
cd <skill-path>/scripts && npx tsx get-endpoints.ts "anthropic/claude-sonnet-4" --sort throughput
cd <skill-path>/scripts && npx tsx get-endpoints.ts "openai/gpt-4o" --sort latency
cd <skill-path>/scripts && npx tsx get-endpoints.ts "anthropic/claude-sonnet-4" --sort uptime
```

Sort options: `throughput`, `latency`, `uptime`, `price`

### Endpoint Output

```json
{
  "model_id": "anthropic/claude-sonnet-4",
  "total_providers": 5,
  "endpoints": [
    {
      "provider": "Anthropic",
      "status": "operational",
      "uptime_30m": "100.00%",
      "latency_30m_ms": { "p50": 800, "p75": 1200, "p90": 2000, "p99": 5000 },
      "throughput_30m_tokens_per_sec": { "p50": 45, "p75": 55, "p90": 65, "p99": 90 },
      "pricing_per_million_tokens": { "prompt": "$3.00", "completion": "$15.00" },
      "supports_implicit_caching": true
    }
  ]
}
```

---

## Trending Models

Fetch the top trending programming models from OpenRouter rankings.

```bash
bun run <skill-path>/scripts/get-trending-models.ts
bun run <skill-path>/scripts/get-trending-models.ts | jq '.'

# Filter with jq: free models with large context
bun run <skill-path>/scripts/get-trending-models.ts | jq '.models | map(select(.contextLength > 100000)) | sort_by(.pricing.promptPer1M) | .[:3]'
```

### Trending Output

```json
{
  "metadata": { "fetchedAt": "...", "weekEnding": "...", "category": "programming" },
  "models": [
    {
      "rank": 1,
      "id": "x-ai/grok-code-fast-1",
      "name": "Grok Code Fast",
      "tokenUsage": 908664328688,
      "contextLength": 131072,
      "maxCompletionTokens": 32768,
      "pricing": { "promptPer1M": 0.5, "completionPer1M": 1.0 }
    }
  ],
  "summary": { "topProvider": "x-ai", "priceRange": { "min": 0.5, "max": 15.0 } }
}
```

---

## OpenRouter API Expert

### Authentication & Base URL

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

All requests go to `https://openrouter.ai/api/v1` — fully OpenAI-compatible.

Optional but recommended headers:
- `HTTP-Referer: https://your-app.com` — helps OpenRouter analytics
- `X-Title: Your App Name` — shown in usage dashboards

### Basic Chat Completion (TypeScript)

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    'HTTP-Referer': 'https://your-app.com',
    'X-Title': 'Your App',
  },
});

const completion = await client.chat.completions.create({
  model: 'anthropic/claude-sonnet-4',
  messages: [{ role: 'user', content: 'Hello!' }],
});

console.log(completion.choices[0].message.content);
```

### Raw HTTP Request

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-sonnet-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### List Models via API

```bash
# All models (no auth needed)
curl https://openrouter.ai/api/v1/models | jq '.data[] | {id, name}'

# Free models only
curl https://openrouter.ai/api/v1/models | jq '.data[] | select(.pricing.prompt == "0") | {id, name}'

# Models supporting tools
curl https://openrouter.ai/api/v1/models | jq '.data[] | select(.supported_parameters | index("tools")) | {id, name}'
```

### Streaming (TypeScript)

```typescript
const stream = await client.chat.completions.create({
  model: 'anthropic/claude-sonnet-4',
  messages: [{ role: 'user', content: 'Write a haiku about AI' }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content ?? '';
  process.stdout.write(content);
}
```

### Streaming (Raw HTTP / SSE)

```typescript
const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'anthropic/claude-sonnet-4',
    messages: [{ role: 'user', content: 'Tell me a story' }],
    stream: true,
  }),
});

const reader = res.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  for (const line of chunk.split('\n')) {
    if (!line.startsWith('data: ') || line === 'data: [DONE]') continue;
    try {
      const parsed = JSON.parse(line.slice(6));
      process.stdout.write(parsed.choices[0]?.delta?.content ?? '');
    } catch {}
  }
}
```

### Function Calling / Tool Use

```typescript
const tools = [
  {
    type: 'function',
    function: {
      name: 'get_weather',
      description: 'Get weather for a city',
      parameters: {
        type: 'object',
        properties: {
          city: { type: 'string', description: 'City name' },
        },
        required: ['city'],
      },
    },
  },
];

const response = await client.chat.completions.create({
  model: 'openai/gpt-4o',           // Must support tools — check supported_parameters
  messages: [{ role: 'user', content: 'Weather in Tokyo?' }],
  tools,
  tool_choice: 'auto',
});

const msg = response.choices[0].message;
if (msg.tool_calls) {
  for (const call of msg.tool_calls) {
    const args = JSON.parse(call.function.arguments);
    const result = await getWeather(args.city);
    // Continue conversation with tool result...
  }
}
```

Models that support tools: check `supported_parameters` includes `"tools"`. Common ones:
`openai/gpt-4o`, `anthropic/claude-sonnet-4`, `google/gemini-2.5-pro`, `mistralai/mistral-large`

### Vision / Multimodal

```typescript
const response = await client.chat.completions.create({
  model: 'openai/gpt-4o',
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: 'What is in this image?' },
        { type: 'image_url', image_url: { url: 'https://example.com/photo.jpg' } },
      ],
    },
  ],
});
```

Use `free-models.ts --modality image` to find free multimodal alternatives.

### Model Fallback Chain

```typescript
const fallbackChain = [
  'anthropic/claude-sonnet-4',
  'openai/gpt-4o',
  'google/gemini-2.5-pro',
  'anthropic/claude-haiku-4-5',
];

async function chatWithFallback(prompt: string): Promise<string> {
  for (const model of fallbackChain) {
    try {
      const res = await client.chat.completions.create({
        model,
        messages: [{ role: 'user', content: prompt }],
      });
      return res.choices[0].message.content ?? '';
    } catch (err: any) {
      if (model === fallbackChain.at(-1)) throw err;
      console.warn(`Model ${model} failed, trying next...`);
    }
  }
  throw new Error('All models failed');
}
```

### Retry with Exponential Backoff

```typescript
async function withRetry<T>(fn: () => Promise<T>, maxRetries = 5): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err: any) {
      if (err.status === 429) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(r => setTimeout(r, delay));
      } else {
        throw err;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

### Cost Estimation

```typescript
// Pricing from list-models.ts or compare-models.ts output
const pricing = { prompt: 3.00, completion: 15.00 }; // per 1M tokens

function estimateCost(inputTokens: number, outputTokens: number) {
  return {
    inputCost: (inputTokens / 1_000_000) * pricing.prompt,
    outputCost: (outputTokens / 1_000_000) * pricing.completion,
    total: (inputTokens / 1_000_000) * pricing.prompt +
           (outputTokens / 1_000_000) * pricing.completion,
  };
}

console.log(estimateCost(10_000, 2_000));
// { inputCost: 0.03, outputCost: 0.03, total: 0.06 }
```

### Error Codes

| Status | Meaning | Action |
|---|---|---|
| 401 | Invalid API key | Check `OPENROUTER_API_KEY` |
| 402 | Insufficient credits | Top up at openrouter.ai |
| 404 | Model not found | Run `resolve-model.ts` to find the correct ID |
| 429 | Rate limited | Retry with exponential backoff |
| 5xx | Provider error | Try fallback model |

---

## Official TypeScript SDK (`@openrouter/sdk`)

The official SDK provides the `callModel` pattern — type-safe, auto-executing tools, multi-turn
support, and streaming built in. Use this for TypeScript agent work. Use the OpenAI SDK (above)
for simpler completions or when you need drop-in OpenAI compatibility.

```bash
npm install @openrouter/sdk
```

```typescript
import OpenRouter from '@openrouter/sdk';

const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY,
});
```

### callModel — Core Pattern

```typescript
// String input (simplest)
const result = client.callModel({
  model: 'openai/gpt-4o',
  input: 'Explain quantum computing in one sentence.',
});
const text = await result.getText();

// With system instructions
const result = client.callModel({
  model: 'openai/gpt-4o',
  instructions: 'You are a concise coding assistant.',
  input: 'How do I reverse a string in Python?',
});

// Message array (multi-turn history)
const result = client.callModel({
  model: 'openai/gpt-4o',
  input: [
    { role: 'user', content: 'What is the capital of France?' },
    { role: 'assistant', content: 'Paris.' },
    { role: 'user', content: 'What is its population?' },
  ],
});

// Multimodal (image + text)
const result = client.callModel({
  model: 'openai/gpt-4o',
  input: [
    {
      role: 'user',
      content: [
        { type: 'text', text: 'What is in this image?' },
        { type: 'image_url', image_url: { url: 'https://example.com/image.png' } },
      ],
    },
  ],
});
```

### Response Methods

| Method | Returns |
|---|---|
| `getText()` | Full text after all tool turns complete |
| `getResponse()` | Full response object including `usage`, `finishReason`, `warnings` |
| `getTextStream()` | Async iterator of text deltas |
| `getReasoningStream()` | Async iterator of reasoning tokens (o1 / reasoning models) |
| `getToolCallsStream()` | Async iterator of completed tool calls with results |
| `getFullResponsesStream()` | All SSE events — see `references/openrouter-sdk-types.md` |

```typescript
// Stream text to console
for await (const delta of result.getTextStream()) {
  process.stdout.write(delta);
}

// Full response with usage
const response = await result.getResponse();
console.log(response.usage.totalTokens);

// Concurrent consumers from one result
const [, response] = await Promise.all([
  (async () => { for await (const d of result.getTextStream()) process.stdout.write(d); })(),
  result.getResponse(),
]);
```

### Tool System (Zod)

Define strongly-typed tools with automatic execution and validation:

```typescript
import { tool } from '@openrouter/sdk';
import { z } from 'zod';

// Regular tool — returns a result
const weatherTool = tool({
  name: 'get_weather',
  description: 'Get current weather for a city',
  inputSchema: z.object({
    city: z.string().describe('City name'),
    units: z.enum(['celsius', 'fahrenheit']).optional().default('celsius'),
  }),
  outputSchema: z.object({
    temperature: z.number(),
    conditions: z.string(),
  }),
  execute: async ({ city, units }) => {
    return { temperature: 22, conditions: 'Sunny' };
  },
});

// Generator tool — yields progress events
const searchTool = tool({
  name: 'web_search',
  description: 'Search the web',
  inputSchema: z.object({ query: z.string() }),
  eventSchema: z.object({ type: z.literal('progress'), message: z.string() }),
  outputSchema: z.object({ results: z.array(z.string()) }),
  execute: async function* ({ query }) {
    yield { type: 'progress', message: 'Searching...' };
    yield { type: 'progress', message: 'Processing...' };
    return { results: ['Result 1', 'Result 2'] };
  },
});

// Manual tool — execute: false, handle calls yourself
const confirmTool = tool({
  name: 'user_confirmation',
  description: 'Request user confirmation',
  inputSchema: z.object({ message: z.string() }),
  execute: false,
});

// Use tools — SDK auto-executes and continues the conversation
const result = client.callModel({
  model: 'openai/gpt-4o',
  input: 'What is the weather in Paris?',
  tools: [weatherTool],
});
const text = await result.getText();
```

### Stop Conditions

Always set limits to prevent runaway agent loops:

```typescript
import { stepCountIs, maxCost, hasToolCall } from '@openrouter/sdk';

const result = client.callModel({
  model: 'openai/gpt-4o',
  input: 'Research this topic thoroughly',
  tools: [searchTool, finishTool],
  stopWhen: [
    stepCountIs(10),        // Stop after 10 turns
    maxCost(1.00),          // Stop if cost exceeds $1.00
    hasToolCall('finish'),  // Stop when 'finish' tool is called
  ],
});

// Custom stop condition
const result = client.callModel({
  model: 'openai/gpt-4o',
  input: 'Complex task',
  tools: [myTool],
  stopWhen: (ctx) => ctx.messages.length > 20,
});
```

### Dynamic Parameters

Compute model or temperature per-turn based on conversation context:

```typescript
const result = client.callModel({
  model: (ctx) => ctx.numberOfTurns > 3 ? 'openai/gpt-4o' : 'openai/gpt-4o-mini',
  temperature: (ctx) => ctx.numberOfTurns > 1 ? 0.3 : 0.7,
  input: 'Start here',
});
// ctx: { numberOfTurns, messages, instructions, totalCost }
```

### nextTurnParams — Context Injection

Tools can modify parameters for subsequent turns (inject skills, memory, mode switching):

```typescript
const skillTool = tool({
  name: 'load_skill',
  description: 'Load a specialized skill',
  inputSchema: z.object({ skill: z.string() }),
  nextTurnParams: {
    instructions: (params, context) => {
      return `${context.instructions}\n\n${loadSkillInstructions(params.skill)}`;
    },
  },
  execute: async ({ skill }) => ({ loaded: skill }),
});
```

### Format Converters

```typescript
import { fromChatMessages, toChatMessage, fromClaudeMessages, toClaudeMessage } from '@openrouter/sdk';

// OpenAI ↔ OpenRouter
const result = client.callModel({ model: 'openai/gpt-4o', input: fromChatMessages(openaiMessages) });
const chatMsg = toChatMessage(await result.getResponse());

// Claude ↔ OpenRouter
const result = client.callModel({ model: 'anthropic/claude-sonnet-4', input: fromClaudeMessages(claudeMessages) });
const claudeMsg = toClaudeMessage(await result.getResponse());
```

### Additional Client APIs

```typescript
// List models
const models = await client.models.list();

// Usage analytics
const activity = await client.analytics.getUserActivity();

// Credit balance
const credits = await client.credits.getCredits();

// Chat completions (alternative to callModel, same params as OpenAI SDK)
const completion = await client.chat.send({
  model: 'openai/gpt-4o',
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

For message shapes, event type interfaces, and `StepResult` / `TurnContext` types, see
`references/openrouter-sdk-types.md`.

---

## Account & Auth Management

### API Key Management (programmatic)

```typescript
// List all keys
const keys = await client.apiKeys.list();

// Create
const newKey = await client.apiKeys.create({ name: 'Production Key' });

// Read, update, delete by hash
const key = await client.apiKeys.get({ hash: 'sk-or-v1-...' });
await client.apiKeys.update({ hash: 'sk-or-v1-...', requestBody: { name: 'New Name' } });
await client.apiKeys.delete({ hash: 'sk-or-v1-...' });

// Current key metadata
const info = await client.apiKeys.getCurrentKeyMetadata();
```

**Key hygiene rules:** rotate keys periodically; use separate keys for dev/staging/prod; store encrypted; never expose in client-side code.

### OAuth PKCE (user-facing apps)

Use when users should control their own API keys — your app never touches their credentials.

```typescript
// Step 1: generate auth URL
const { authorizationUrl } = await client.oAuth.createAuthCode({
  callbackUrl: 'https://your-app.com/auth/callback',
});
res.redirect(authorizationUrl);  // redirect user

// Step 2: exchange code → API key (in callback handler)
const { key: userApiKey } = await client.oAuth.exchangeAuthCodeForAPIKey({
  code: req.query.code as string,
});
await saveUserApiKey(req.session.userId, userApiKey);

// Step 3: use user's key for their requests
const userClient = new OpenRouter({ apiKey: userApiKey });
const text = await userClient.callModel({ model: 'openai/gpt-4o', input: 'Hello!' }).getText();
```

---

## Presenting Results

- **Always convert raw pricing** (`0.000003`) to per-million-tokens format (`$3.00 / 1M`)
- **Paid models**: always show input + output price. Never omit for paid models
- **Free models**: show `FREE` or `$0.00 / 1M` — make it explicit
- **Comparisons**: use a markdown table with models as columns
- **Provider endpoints**: highlight lowest p50 latency and highest uptime
- **Cache pricing**: mention when available — can cut input costs by 90%+
- **Deprecation**: flag any model with `expiration_date`
- **Informal names**: always resolve with `resolve-model.ts` before proceeding

---

## Resources

- API docs: https://openrouter.ai/docs
- API reference: https://openrouter.ai/docs/api-reference
- Models list: https://openrouter.ai/models
- Rankings: https://openrouter.ai/rankings
- Pricing: https://openrouter.ai/docs/pricing
- API keys: https://openrouter.ai/keys
- Status: https://status.openrouter.ai
