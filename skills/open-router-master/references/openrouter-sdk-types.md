# OpenRouter SDK — Type Reference

Full TypeScript interface definitions for `@openrouter/sdk`. Reference this when building
agents that need to handle raw events, inspect response shapes, or implement custom stop
conditions.

---

## Message Roles

| Role | Description |
|---|---|
| `user` | User-provided input |
| `assistant` | Model-generated responses |
| `system` | System instructions |
| `developer` | Developer-level directives |
| `tool` | Tool execution results |

---

## Input Message Shapes

```typescript
// Simple text
interface TextMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Multimodal (image + text)
interface MultimodalMessage {
  role: 'user';
  content: Array<
    | { type: 'input_text'; text: string }
    | { type: 'input_image'; imageUrl: string; detail?: 'auto' | 'low' | 'high' }
    | {
        type: 'image';
        source: {
          type: 'url' | 'base64';
          url?: string;
          media_type?: string;
          data?: string;
        };
      }
  >;
}

// Tool function call (assistant → model)
interface ToolCallMessage {
  role: 'assistant';
  content?: null;
  tool_calls?: Array<{
    id: string;
    type: 'function';
    function: {
      name: string;
      arguments: string; // JSON-encoded
    };
  }>;
}

// Tool result (tool → model)
interface ToolResultMessage {
  role: 'tool';
  tool_call_id: string;
  content: string; // JSON-encoded result
}
```

---

## Response Shapes

```typescript
// getResponse() return type
interface OpenResponsesNonStreamingResponse {
  output: Array<ResponseMessage>;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    cachedTokens?: number;
  };
  finishReason?: string;
  warnings?: Array<{ type: string; message: string }>;
  experimental_providerMetadata?: Record<string, unknown>;
}

// Text/content output message
interface ResponseOutputMessage {
  type: 'message';
  role: 'assistant';
  content: string | Array<ContentPart>;
  reasoning?: string; // Reasoning models (o1, etc.)
}

// Tool result in output
interface FunctionCallOutputMessage {
  type: 'function_call_output';
  call_id: string;
  output: string;
}

// Parsed tool call (after schema validation)
interface ParsedToolCall {
  id: string;
  name: string;
  arguments: unknown; // Validated against inputSchema
}

// Tool execution result
interface ToolExecutionResult {
  toolCallId: string;
  toolName: string;
  result: unknown;           // Validated against outputSchema
  preliminaryResults?: unknown[]; // From generator tools
  error?: Error;
}
```

---

## Stop Condition Context

```typescript
// Available in custom stopWhen callbacks
interface StepResult {
  stepType: 'initial' | 'continue';
  text: string;
  toolCalls: ParsedToolCall[];
  toolResults: ToolExecutionResult[];
  response: OpenResponsesNonStreamingResponse;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    cachedTokens?: number;
  };
  finishReason?: string;
  warnings?: Array<{ type: string; message: string }>;
  experimental_providerMetadata?: Record<string, unknown>;
}
```

---

## Turn Context (dynamic params & nextTurnParams)

```typescript
interface TurnContext {
  numberOfTurns: number;                      // 1-indexed
  turnRequest?: OpenResponsesRequest;         // Current request
  toolCall?: OpenResponsesFunctionToolCall;   // In tool context
}
```

---

## Streaming Event Types

`getFullResponsesStream()` yields `EnhancedResponseStreamEvent`:

```typescript
type EnhancedResponseStreamEvent =
  | ResponseCreatedEvent
  | ResponseInProgressEvent
  | OutputTextDeltaEvent
  | OutputTextDoneEvent
  | ReasoningDeltaEvent
  | ReasoningDoneEvent
  | FunctionCallArgumentsDeltaEvent
  | FunctionCallArgumentsDoneEvent
  | ResponseCompletedEvent
  | ToolPreliminaryResultEvent;
```

| Event type | Payload |
|---|---|
| `response.created` | `{ response: ResponseObject }` |
| `response.in_progress` | `{}` |
| `response.output_text.delta` | `{ delta: string }` |
| `response.output_text.done` | `{ text: string }` |
| `response.reasoning.delta` | `{ delta: string }` (o1 models) |
| `response.reasoning.done` | `{ reasoning: string }` |
| `response.function_call_arguments.delta` | `{ delta: string }` |
| `response.function_call_arguments.done` | `{ arguments: string }` |
| `response.completed` | `{ response: OpenResponsesNonStreamingResponse }` |
| `tool.preliminary_result` | `{ toolCallId: string; result: unknown }` (generator tools) |

```typescript
// Full event processing example
for await (const event of result.getFullResponsesStream()) {
  switch (event.type) {
    case 'response.output_text.delta':
      process.stdout.write(event.delta);
      break;
    case 'response.reasoning.delta':
      console.log('[Reasoning]', event.delta);
      break;
    case 'tool.preliminary_result':
      console.log(`[Progress: ${event.toolCallId}]`, event.result);
      break;
    case 'response.completed':
      console.log('\n[Complete]', event.response.usage);
      break;
  }
}
```

### Tool Stream Events

`getToolStream()` yields:

```typescript
type ToolStreamEvent =
  | { type: 'delta'; content: string }
  | { type: 'preliminary_result'; toolCallId: string; result: unknown };
```

### Message Stream Events

`getNewMessagesStream()` yields OpenResponses format updates:

```typescript
type MessageStreamUpdate =
  | ResponsesOutputMessage        // Text/content updates
  | OpenResponsesFunctionCallOutput; // Tool results

// Usage
for await (const message of result.getNewMessagesStream()) {
  if (message.type === 'message') {
    console.log('Assistant:', message.content);
  } else if (message.type === 'function_call_output') {
    console.log('Tool result:', message.output);
  }
}
```
