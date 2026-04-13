# Authentication and Session Management

Covers login flows, session persistence, multi-session patterns, and proxy for all three browser tools.
Sources: agent-browser/authentication.md, agent-browser/session-management.md, playwright-cli/session-management.md, browser-use/multi-session.md, agent-browser/proxy-support.md.

---

## Auth: Common Rules (All Tools)

- **Never hardcode credentials** — use environment variables: `$USERNAME`, `$PASSWORD`.
- **Never commit state files** — they contain session tokens in plaintext. Add to `.gitignore`.
- **Use short-lived sessions in CI** — don't persist state; start fresh each run.
- **Encrypt state at rest** when needed:
  ```bash
  export AGENT_BROWSER_ENCRYPTION_KEY=$(openssl rand -hex 32)
  agent-browser --session-name secure open https://app.example.com
  ```

---

## agent-browser Auth Patterns

### Fastest: Import from Your Chrome

```bash
# Start Chrome with remote debugging (macOS)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
# Log in normally, then:
agent-browser --auto-connect state save ./my-auth.json
agent-browser --state ./my-auth.json open https://app.example.com/dashboard
```

### Persistent Profile

```bash
agent-browser --profile ~/.myapp-profile open https://app.example.com/login
# Login once; all subsequent runs reuse the profile
agent-browser --profile ~/.myapp-profile open https://app.example.com/dashboard
```

### Session Persistence (auto save/restore by name)

```bash
agent-browser --session-name twitter open https://twitter.com
# Login, then:
agent-browser close          # State saved to ~/.agent-browser/sessions/
# Next time:
agent-browser --session-name twitter open https://twitter.com  # Already logged in
```

### Basic Login Flow

```bash
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$APP_USERNAME"
agent-browser fill @e2 "$APP_PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save ./auth-state.json  # Save for reuse
```

### Auth Restore / Token Refresh

```bash
if [[ -f auth-state.json ]]; then
  agent-browser state load auth-state.json
  agent-browser open https://app.example.com/dashboard
  URL=$(agent-browser get url)
  if [[ "$URL" == *"/login"* ]]; then
    echo "Session expired, re-authenticating..."
    # repeat login flow...
  fi
fi
```

---

## playwright-cli Auth and Session Patterns

### Named Sessions

```bash
playwright-cli -s=auth open https://app.example.com/login
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=auth fill e2 "$PASSWORD"
playwright-cli -s=auth click e3

playwright-cli -s=public open https://example.com   # Fully isolated
```

### Persistent Profile

```bash
playwright-cli open https://example.com --persistent           # Auto-generated dir
playwright-cli open https://example.com --profile=/path/to/dir # Custom dir
```

### Session Cleanup

```bash
playwright-cli list
playwright-cli close            # default session
playwright-cli close-all
playwright-cli kill-all         # Force-kill zombie processes
playwright-cli -s=oldsession delete-data
```

---

## browser-use Multi-Session

Each `--session NAME` is fully isolated (own daemon, socket, PID, browser instance).

```bash
browser-use --session scraper cloud connect
browser-use --session scraper open https://example.com

browser-use --session auth --profile "Default" open https://github.com

browser-use sessions                # List all sessions + state
browser-use --session scraper close
browser-use close --all

export BROWSER_USE_SESSION=work     # Default session via env var
```

Key rule: always pass `--session` on every command targeting that session. Omitting it sends the command to `default` (different browser).

---

## Concurrent Scraping (Multi-Session)

```bash
# agent-browser
agent-browser --session site1 open https://site1.com &
agent-browser --session site2 open https://site2.com &
wait
agent-browser --session site1 get text body > site1.txt

# playwright-cli
playwright-cli -s=site1 open https://site1.com &
playwright-cli -s=site2 open https://site2.com &
wait
playwright-cli -s=site1 snapshot
playwright-cli close-all
```

---

## Proxy Configuration (agent-browser)

```bash
# Basic
agent-browser --proxy "http://proxy.example.com:8080" open https://example.com

# Via env vars
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# SOCKS5
export ALL_PROXY="socks5://user:pass@proxy.example.com:1080"

# Bypass
agent-browser --proxy "http://proxy:8080" --proxy-bypass "localhost,*.internal.com" open <url>
export NO_PROXY="localhost,127.0.0.1,.company.com"
```

**Rules:** Use env vars, not hardcoded credentials. Test connectivity first (`curl -x <proxy> https://httpbin.org/ip`). Rotate proxies for large scraping jobs.

For Playwright scripting proxy: `chromium.launch({ proxy: { server: 'http://proxy:8080' } })`
