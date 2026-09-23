# BF ADE Skill

You are inside BF ADE — a multi-agent Electron IDE.

## MCP Tools  (mcp__ade__ prefix)

pane_spawn(agentType, cwd, model?, role?) → {ok, paneId}
pane_list() → {ok, count, panes[]}
pane_list_providers() → {ok, count, providers[]}
pane_write(paneId, data, submit?) → {ok}
pane_wait_idle(paneId, timeoutMs?) → {ok, idle}
pane_read(paneId, lastN?) → {ok, lines[]}
todo_manager(operation, ...) → list|create|update|delete|complete

## Patterns

- Always pane_wait_idle before pane_read
- For large output: have sub-agent write to file, then read it directly
- Brief sub-agents: include goal, inputs, output format, save location
- Use mailbox_send / mailbox_read for inter-agent messages
- Orchestrators coordinate; workers execute; both can spawn panes
