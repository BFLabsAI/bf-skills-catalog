---
name: cmux-expert
description: Complete cmux expert covering terminal splits, browser automation
  (headless Chromium with snapshot/ref workflow), markdown viewer panels, sidebar
  status/progress reporting, OS notifications, agent team coordination, and debug
  window management. Use this skill whenever the user mentions cmux for ANY purpose —
  opening splits, automating a browser, displaying markdown, coordinating parallel
  agents, showing progress bars, sending notifications, or debugging cmux itself.
  Even if the user just says "use cmux" without specifying what for.
---

# cmux — AI-Native Terminal Multiplexer (Expert Reference)

cmux is a terminal multiplexer with a programmable socket API designed for AI coding agents. It provides terminal split management, full headless Chromium browser automation, markdown viewer panels, live sidebar status, OS notifications, and agent team coordination — all via a simple CLI.

---

## Orient Yourself

```bash
cmux identify --json          # current window/workspace/pane/surface context
cmux list-panes               # all panes in current workspace
cmux list-pane-surfaces --pane pane:1  # surfaces within a pane
cmux list-workspaces          # all workspaces (tabs) in current window
```

Environment variables set automatically:
- `$CMUX_SURFACE_ID` — your current surface ref
- `$CMUX_WORKSPACE_ID` — your current workspace ref

Handles use short refs: `surface:N`, `pane:N`, `workspace:N`, `window:N`.

---

## Terminal Splits

### Create splits

```bash
cmux --json new-split right   # side-by-side (preferred for parallel work)
cmux --json new-split down    # stacked (good for logs)
```

Always capture the returned `surface_ref`:

```bash
WORKER=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

### Send commands and read output

```bash
cmux send-surface --surface surface:22 "npm run build\n"
cmux capture-pane --surface surface:22              # current screen
cmux capture-pane --surface surface:22 --scrollback  # with full history

cmux send-key-surface --surface surface:22 ctrl-c
cmux send-key-surface --surface surface:22 enter
```

**Golden rule: never steal focus.** Always use `--surface` targeting.

### Worker split pattern

```bash
WORKER=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux send-surface --surface "$WORKER" "make test 2>&1; echo EXIT_CODE=\$?\n"
sleep 3
cmux capture-pane --surface "$WORKER"
cmux close-surface --surface "$WORKER"
```

### Pane management

```bash
cmux focus-pane --pane pane:2
cmux close-surface --surface surface:22
cmux swap-pane --pane pane:1 --target-pane pane:2
cmux move-surface --surface surface:7 --pane pane:2 --focus true
cmux reorder-surface --surface surface:7 --before surface:3
```

---

## Browser Automation

cmux embeds a full headless Chromium engine (WKWebView-based). No external Chrome required. Every command targets a browser surface by ref.

### Stable agent loop — always follow this pattern

```
navigate → verify url → wait for load → snapshot --interactive → act with refs → re-snapshot
```

```bash
BROWSER=$(cmux --json browser open https://example.com | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux browser $BROWSER get url
cmux browser $BROWSER wait --load-state complete --timeout-ms 15000
cmux browser $BROWSER snapshot --interactive
# use e1, e2, e3 ... refs from snapshot output
cmux --json browser $BROWSER click e2 --snapshot-after
cmux browser $BROWSER snapshot --interactive
```

If `get url` returns empty or `about:blank`, navigate first instead of waiting.

### Navigate

```bash
cmux browser surface:23 goto https://other.com
cmux browser surface:23 back / forward / reload
cmux browser surface:23 get url / get title
```

### Snapshot and element refs

Refs (`e1`, `e2`, ...) replace CSS selectors — they're stable within the current DOM state. Re-snapshot after any navigation or DOM mutation.

```bash
cmux browser surface:23 snapshot --interactive
cmux browser surface:23 snapshot --interactive --compact --max-depth 3
cmux browser surface:23 snapshot --selector "form#login" --interactive
```

### Interact

```bash
cmux browser surface:23 click e1 / dblclick e2 / hover e3 / focus e4
cmux browser surface:23 fill e5 "hello@example.com"   # clear + type
cmux browser surface:23 fill e5 ""                    # clear input
cmux browser surface:23 type e6 "search query"         # type without clearing
cmux browser surface:23 press Enter / Tab
cmux browser surface:23 check e7 / uncheck e7
cmux browser surface:23 select e8 "option-value"
cmux browser surface:23 scroll --dy 500
cmux browser surface:23 scroll-into-view e9
```

### Wait

```bash
cmux browser surface:23 wait --load-state complete --timeout-ms 15000
cmux browser surface:23 wait --selector "#ready" --timeout-ms 10000
cmux browser surface:23 wait --text "Success" --timeout-ms 10000
cmux browser surface:23 wait --url-contains "/dashboard" --timeout-ms 10000
cmux browser surface:23 wait --function "document.readyState === 'complete'" --timeout-ms 10000
```

### Read page content

```bash
cmux browser surface:23 get text body
cmux browser surface:23 get html body
cmux browser surface:23 get value "#email"
cmux browser surface:23 get attr "#link" --attr href
cmux browser surface:23 get count ".items"
cmux browser surface:23 is visible "#modal" / is enabled "#submit" / is checked "#agree"
```

### JavaScript, frames, dialogs

```bash
cmux browser surface:23 eval "document.title"
cmux browser surface:23 frame "#iframe-selector" / frame main
cmux browser surface:23 dialog accept / dismiss / accept "prompt text"
```

### Cookies, storage, and state

```bash
cmux browser surface:23 cookies get / set session_token "abc" / clear
cmux browser surface:23 storage local get / set myKey "val" / clear
cmux browser surface:23 state save ./auth-state.json   # save cookies + storage + tabs
cmux browser surface:23 state load ./auth-state.json   # restore in new surface
```

### Diagnostics

```bash
cmux browser surface:23 console list / errors list
cmux browser surface:23 screenshot
cmux browser surface:23 highlight "#el"
```

### WKWebView limits (returns `not_supported`)

viewport/geolocation/offline emulation, trace recording, network route interception, raw input injection. Use high-level commands instead.

### Troubleshooting `js_error`

```bash
cmux browser surface:7 get url        # verify navigation happened
cmux browser surface:7 get text body  # fallback when snapshot/eval fails
cmux browser surface:7 get html body
```

**Deep-dive references:** `references/browser-commands.md` · `references/snapshot-refs.md` · `references/authentication.md` · `references/session-management.md` · `references/video-recording.md` · `references/proxy-support.md`

**Templates:** `templates/form-automation.sh` · `templates/authenticated-session.sh` · `templates/capture-workflow.sh`

---

## Markdown Viewer

Display formatted markdown in a live-reloading split panel alongside the terminal.

```bash
cmux markdown open plan.md                           # open in caller's workspace
cmux markdown open /path/to/PLAN.md                  # absolute path
cmux markdown open design.md --workspace workspace:2 # specific workspace
cmux markdown open plan.md --surface surface:5       # split from specific surface
```

The panel auto-updates whenever the file changes on disk — direct writes, editor saves, atomic replace, and progressive agent writes all work. Write the full file first, then open it, to avoid rendering a partial state.

If the file is deleted and does not reappear, the panel shows "file unavailable" — close and reopen to reconnect.

**Deep-dive references:** `references/markdown-commands.md` · `references/live-reload.md`

---

## Sidebar, Progress & Notifications

Show live status to the user without interrupting their flow:

```bash
cmux set-status agent "working" --icon hammer --color "#ff9500"
cmux set-status agent "done" --icon checkmark --color "#34c759"
cmux clear-status agent

cmux set-progress 0.3 --label "Running tests..."
cmux set-progress 1.0 --label "Complete"
cmux clear-progress

cmux log "Starting build"
cmux log --level success "All tests passed"
cmux log --level error --source build "Compilation failed"

cmux notify --title "Task Complete" --body "All tests passing"
cmux notify --title "Need Input" --subtitle "Permission" --body "Approve deployment?"
```

---

## Debug Windows (cmux app development)

For tuning cmux's own Sidebar Debug, Background Debug, and Menu Bar Extra Debug windows.

**Workflow:**
1. Verify debug menu wiring in `Sources/cmuxApp.swift` under `CommandMenu("Debug")` (only visible in DEBUG builds via `./scripts/reload.sh --tag ...`).
2. Keep these in `Menu("Debug Windows")`: Sidebar Debug…, Background Debug…, Menu Bar Extra Debug…, Open All Debug Windows.
3. For a combined debug snapshot, run:

```bash
skills/cmux-debug-windows/scripts/debug_windows_snapshot.sh --copy
# or from this skill:
scripts/debug_windows_snapshot.sh --copy
scripts/debug_windows_snapshot.sh --domain <bundle-id> --copy
```

4. After code edits, build and reload:
```bash
xcodebuild -project GhosttyTabs.xcodeproj -scheme cmux -configuration Debug \
  -destination 'platform=macOS' build
./scripts/reload.sh --tag <tag>
```

**Key files:** `Sources/cmuxApp.swift` (debug menu + controllers), `Sources/AppDelegate.swift` (menu bar extra debug defaults).

---

## Agent Teams with cmux

Use cmux splits to give each teammate a visible workspace. Coordinate via `SendMessage` — never by reading each other's terminal output.

```bash
# Create visible splits first
SPLIT_1=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
SPLIT_2=$(cmux --json new-split down  | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

Then in each teammate's prompt:
```
You have a cmux terminal split at surface:42.
Run commands:  cmux send-surface --surface surface:42 "command\n"
Read output:   cmux capture-pane --surface surface:42
Set status:    cmux set-status myagent "working" --icon hammer
Log progress:  cmux log "message"
Never steal focus — always use --surface targeting.
```

**Key rules:**
- Never spawn `claude -p` in splits — use the Agent tool instead
- Create splits before spawning teammates — pass refs in their prompts
- One split per teammate
- Coordinate via `SendMessage`
- Clean up: `cmux close-surface --surface <ref>` when done

**Mixed layout: terminals + browsers**

```bash
BUILD=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
DOCS=$(cmux --json browser open https://docs.example.com | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
TEST=$(cmux --json new-split down | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Where am I? | `cmux identify --json` |
| Split right | `cmux --json new-split right` |
| Split down | `cmux --json new-split down` |
| Send command | `cmux send-surface --surface <ref> "cmd\n"` |
| Read output | `cmux capture-pane --surface <ref>` |
| Open browser | `cmux --json browser open <url>` |
| Page snapshot | `cmux browser <ref> snapshot --interactive` |
| Click element | `cmux browser <ref> click e1` |
| Fill input | `cmux browser <ref> fill e1 "text"` |
| Wait for load | `cmux browser <ref> wait --load-state complete --timeout-ms 15000` |
| Read page text | `cmux browser <ref> get text body` |
| Evaluate JS | `cmux browser <ref> eval "expression"` |
| Save auth | `cmux browser <ref> state save ./auth.json` |
| Load auth | `cmux browser <ref> state load ./auth.json` |
| Open markdown | `cmux markdown open <file.md>` |
| Set status | `cmux set-status <key> "text" --icon <name>` |
| Progress bar | `cmux set-progress 0.5 --label "Working..."` |
| Log message | `cmux log "message"` |
| Notify | `cmux notify --title "T" --body "B"` |
| Close split | `cmux close-surface --surface <ref>` |
| Screenshot | `cmux browser <ref> screenshot` |
| Debug snapshot | `scripts/debug_windows_snapshot.sh --copy` |

---

## Reference Index

| File | When to read |
|------|-------------|
| `references/browser-commands.md` | Full browser command syntax, agent-browser→cmux mapping, WKWebView gaps |
| `references/snapshot-refs.md` | Ref lifecycle, stale-ref troubleshooting, scoping snapshots |
| `references/authentication.md` | Login flows, OAuth/SSO, 2FA, cookie-based auth, token refresh |
| `references/session-management.md` | Multi-surface isolation, parallel sessions, state persistence |
| `references/video-recording.md` | Why recording isn't supported, screenshot/snapshot alternatives |
| `references/proxy-support.md` | Proxy behavior, WKWebView limits, egress verification |
| `references/markdown-commands.md` | Full `cmux markdown` command syntax, panel behavior, session persistence |
| `references/live-reload.md` | File watching internals, atomic write handling, edge cases |
