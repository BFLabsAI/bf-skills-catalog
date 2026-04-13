# browser-use CLI Reference

Full command reference for the `browser-use` daemon-based CLI. Aliases: `bu`, `browser`, `browseruse`.

## Core Commands

```bash
# Navigation
browser-use open <url>                    # Navigate to URL
browser-use back                          # Go back in history
browser-use scroll down                   # Scroll down (--amount N for pixels)
browser-use scroll up                     # Scroll up
browser-use tab list                      # List all tabs
browser-use tab new [url]                 # Open a new tab
browser-use tab switch <index>            # Switch to tab by index
browser-use tab close <index> [index...]  # Close tabs

# Page State (always run state first to get element indices)
browser-use state                         # URL, title, clickable elements with indices
browser-use screenshot [path.png]         # Screenshot (base64 if no path, --full for full page)

# Interactions (use indices from state)
browser-use click <index>                 # Click element by index
browser-use click <x> <y>                 # Click at pixel coordinates
browser-use type "text"                   # Type into focused element
browser-use input <index> "text"          # Click element, then type
browser-use keys "Enter"                  # Send keyboard keys ("Control+a", etc.)
browser-use select <index> "option"       # Select dropdown option
browser-use upload <index> <path>         # Upload file to file input
browser-use hover <index>                 # Hover over element
browser-use dblclick <index>              # Double-click element
browser-use rightclick <index>            # Right-click element

# Data Extraction
browser-use eval "js code"                # Execute JavaScript, return result
browser-use get title                     # Page title
browser-use get html [--selector "h1"]    # Page HTML (scoped to selector)
browser-use get text <index>              # Element text content
browser-use get value <index>             # Input/textarea value
browser-use get attributes <index>        # Element attributes
browser-use get bbox <index>              # Bounding box (x, y, width, height)

# Wait
browser-use wait selector "css"           # Wait for element (--state, --timeout)
browser-use wait text "text"              # Wait for text to appear

# Cookies
browser-use cookies get [--url <url>]     # Get cookies
browser-use cookies set <name> <value>    # Set cookie (--domain, --secure, etc.)
browser-use cookies clear [--url <url>]   # Clear cookies
browser-use cookies export <file>         # Export to JSON
browser-use cookies import <file>         # Import from JSON

# Session
browser-use close                         # Close browser and stop daemon
browser-use sessions                      # List active sessions
browser-use close --all                   # Close all sessions
```

## Browser Modes

```bash
browser-use open <url>                         # Default: headless Chromium
browser-use --headed open <url>                # Visible window (debugging)
browser-use connect                            # User's Chrome (preserves logins/cookies)
browser-use cloud connect                      # Cloud browser (requires API key)
browser-use --profile "Default" open <url>     # Chrome profile
browser-use --session NAME open <url>          # Named session (isolated browser)
```

## Cloud API

```bash
browser-use cloud connect                 # Provision cloud browser and connect
browser-use cloud login <api-key>         # Save API key (or set BROWSER_USE_API_KEY)
browser-use cloud logout                  # Remove API key
browser-use cloud v2 GET /browsers        # REST passthrough
browser-use cloud v2 POST /tasks '{"task":"...","url":"..."}'
browser-use cloud v2 poll <task-id>       # Poll task until done
```

## Tunnels

```bash
browser-use tunnel <port>                 # Start Cloudflare tunnel (idempotent)
browser-use tunnel list                   # Show active tunnels
browser-use tunnel stop <port>            # Stop tunnel
browser-use tunnel stop --all             # Stop all tunnels
```

## Profile Management

```bash
browser-use profile list                  # List detected browsers and profiles
browser-use profile sync --all            # Sync profiles to cloud
```

## Configuration

```bash
browser-use config list                   # Show all config values
browser-use config set <key> <value>      # Set a value
browser-use config get <key>              # Get a value
browser-use doctor                        # Shows config + diagnostics
browser-use setup                         # Interactive post-install setup
```

Config stored in `~/.browser-use/config.json`.

## Global Options

| Option | Description |
|--------|-------------|
| `--headed` | Show browser window |
| `--profile [NAME]` | Use real Chrome (bare uses "Default") |
| `--cdp-url <url>` | Connect via CDP URL |
| `--session NAME` | Target a named session |
| `--json` | Output as JSON |
| `--mcp` | Run as MCP server |

## Raw CDP (Advanced)

Use `browser-use python` for browser-level CDP control not exposed by CLI commands (tab activation, device emulation, network interception):

```bash
# Get CDP client (persists across calls)
browser-use python "cdp = browser._run(browser._session.get_or_create_cdp_session())"

# Activate a tab (makes it visible to user)
browser-use python "targets = browser._session.session_manager.get_all_page_targets()"
browser-use python "browser._run(cdp.cdp_client.send.Target.activateTarget(params={'targetId': targets[1].target_id}))"

# Emulate mobile device
browser-use python "browser._run(cdp.cdp_client.send.Emulation.setDeviceMetricsOverride(params={'width': 375, 'height': 812, 'deviceScaleFactor': 3, 'mobile': True}, session_id=cdp.session_id))"
```

Variables persist across `browser-use python` calls. Use `browser._run(coroutine)` for async operations (60s timeout).

## Troubleshooting

- **Browser won't start?** `browser-use close` then `browser-use --headed open <url>`
- **Element not found?** `browser-use scroll down` then `browser-use state`
- **Run diagnostics:** `browser-use doctor`
- **Wrong session?** Always pass `--session NAME` on every command targeting that session.

## Cleanup

```bash
browser-use close          # Close current session
browser-use tunnel stop --all   # Stop tunnels if any
```
