# playwright-cli Reference

Full command reference for `playwright-cli`. Use `npx playwright-cli` if not installed globally.

Install: `npm install -g @playwright/cli@latest`

---

## Core Commands

```bash
playwright-cli open [url]         # Open browser (optionally navigate)
playwright-cli goto <url>         # Navigate to URL
playwright-cli snapshot           # Accessibility tree with refs (e1, e2, ...)
playwright-cli click e15          # Click by ref
playwright-cli dblclick e7        # Double-click
playwright-cli fill e5 "text" --submit  # Fill + press Enter
playwright-cli type "text"        # Type at current focus
playwright-cli drag e2 e8         # Drag and drop
playwright-cli hover e4           # Hover
plaintiff-cli select e9 "value"   # Select dropdown
playwright-cli upload ./file.pdf  # Upload file
playwright-cli check e12          # Check checkbox
playwright-cli uncheck e12        # Uncheck
playwright-cli eval "document.title"        # Evaluate JS expression
playwright-cli eval "el => el.id" e5        # Evaluate against element
playwright-cli dialog-accept ["text"]       # Accept dialog
playwright-cli dialog-dismiss               # Dismiss dialog
playwright-cli resize 1920 1080             # Resize viewport
playwright-cli close                        # Close browser
```

## Navigation

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

## Keyboard and Mouse

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift

playwright-cli mousemove 150 300
playwright-cli mousedown [right]
playwright-cli mouseup [right]
playwright-cli mousewheel 0 100
```

## Screenshots, PDF, Video

```bash
playwright-cli screenshot                   # Default filename
playwright-cli screenshot e5                # Element screenshot
playwright-cli screenshot --filename=p.png  # Custom path
playwright-cli pdf --filename=page.pdf

playwright-cli video-start video.webm
playwright-cli video-chapter "Title" --description="..." --duration=2000
playwright-cli video-stop
```

## Tabs

```bash
playwright-cli tab-list
playwright-cli tab-new [url]
playwright-cli tab-close [index]
playwright-cli tab-select <index>
```

## Storage and Cookies

```bash
playwright-cli state-save [auth.json]
playwright-cli state-load auth.json

playwright-cli cookie-list [--domain=example.com]
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123 [--domain=... --httpOnly --secure]
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

playwright-cli localstorage-list
playwright-cli localstorage-get key
playwright-cli localstorage-set key value
playwright-cli localstorage-delete key
playwright-cli localstorage-clear

playwright-cli sessionstorage-list
playwright-cli sessionstorage-get key
playwright-cli sessionstorage-set key value
playwright-cli sessionstorage-delete key
playwright-cli sessionstorage-clear
```

## Network and DevTools

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "**/api/**" --body='{"mock":true}'
playwright-cli route-list
playwright-cli unroute ["**/*.jpg"]

playwright-cli console [warning]
playwright-cli network
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js
```

## Snapshots

```bash
playwright-cli snapshot                     # Full accessibility tree
playwright-cli snapshot --filename=f.yaml  # Save to file
playwright-cli snapshot "#main"            # Scope to selector
playwright-cli snapshot --depth=4          # Limit depth
playwright-cli snapshot e34                # Scope to element
```

## Targeting Elements

```bash
playwright-cli click e15                                         # By ref (default)
playwright-cli click "#main > button.submit"                     # CSS selector
playwright-cli click "getByRole('button', { name: 'Submit' })"  # Role locator
playwright-cli click "getByTestId('submit-button')"             # Test ID
```

## Sessions

```bash
playwright-cli -s=mysession open example.com --persistent
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close
playwright-cli -s=mysession delete-data

playwright-cli list
playwright-cli close-all
playwright-cli kill-all    # Force-kill zombie processes
```

## Open Options

```bash
playwright-cli open --browser=chrome|firefox|webkit|msedge
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile
playwright-cli attach --extension
playwright-cli open --config=my-config.json
playwright-cli delete-data
```

## Raw Output

Strip page status, code, snapshot sections — use for piping:

```bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd'
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
```

## Advanced: run-code

Execute arbitrary Playwright code for capabilities not covered by CLI commands:

```bash
# Geolocation
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

# Device emulation
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# Wait strategies
playwright-cli run-code "async page => {
  await page.waitForFunction(() => window.appReady === true);
}"

# File downloads
playwright-cli run-code "async page => {
  const dl = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download' }).click();
  const download = await dl;
  await download.saveAs('./file.pdf');
}"
```

## Request Mocking (Advanced)

```bash
# Conditional response based on request body
playwright-cli run-code "async page => {
  await page.route('**/api/login', route => {
    const body = route.request().postDataJSON();
    if (body.username === 'admin') {
      route.fulfill({ body: JSON.stringify({ token: 'mock-token' }) });
    } else {
      route.fulfill({ status: 401, body: JSON.stringify({ error: 'Invalid' }) });
    }
  });
}"

# Simulate network failure
playwright-cli run-code "async page => {
  await page.route('**/api/offline', route => route.abort('internetdisconnected'));
}"
```
