# Bot Bypass and Stealth Automation

Bypass bot detection systems using rebrowser-playwright (Node.js) or undetected-chromedriver (Python).
Passes bot.sannysoft.com; works against Cloudflare, Akamai, PerimeterX, and similar systems.

## Why Standard Playwright Gets Detected

| Detection Point | Standard Playwright | Stealth Solution |
|-----------------|---------------------|-----------------|
| `navigator.webdriver` | `true` | Removed |
| WebGL Renderer | SwiftShader (software) | Real GPU (via Chrome binary) |
| User Agent | Contains "HeadlessChrome" | Clean Chrome UA |
| `chrome.runtime` | Missing | Complete runtime object |
| `navigator.plugins` | Empty array | 3 standard plugins |
| `navigator.languages` | `['en-US']` only | Matches Accept-Language header |
| Permissions API | Inconsistent state | Patched to match real Chrome |
| `outerWidth/Height` | Same as inner (no chrome) | Offset like real browser |
| Canvas fingerprint | Deterministic | Noise injected |

## Prerequisites

- **Node.js 18+** with ESM support (`.mjs` files)
- **Google Chrome** installed (not just Chromium)
- **Headed mode** required (`headless: false`) — no display = no stealth

Verify Chrome:
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
# Linux
google-chrome --version
```

## Quick Start (Node.js)

```bash
npm install rebrowser-playwright
```

```javascript
import { createStealthBrowser, humanDelay, humanType, simulateMouseMovement } from './stealth-template.mjs';

const { browser, page } = await createStealthBrowser({
  headless: false,              // Required
  viewport: { width: 1280, height: 800 },
  locale: 'ko-KR',             // Browser locale
  storageState: './session.json', // Cookie persistence (optional)
  proxy: { server: 'http://proxy:8080' }  // Proxy (optional)
});

try {
  await page.goto('https://example.com');
  await simulateMouseMovement(page);       // Avoids Cloudflare Turnstile
  await humanType(page, 'input[name="q"]', 'search query');
  await humanDelay(300, 800);
} finally {
  await browser.close();
}

// Save session for reuse
import { saveSession } from './stealth-template.mjs';
await saveSession(context, './session.json');
```

## Stealth Patches Applied

| # | Patch | Target |
|---|-------|--------|
| 1 | `navigator.webdriver` removal | All bot detectors |
| 2 | `chrome.runtime` object | Cloudflare, sannysoft |
| 3 | `navigator.plugins` (3 plugins) | Cloudflare Bot Management |
| 4 | `navigator.languages` (ko-KR,en) | Akamai |
| 5 | Permissions API normalization | PerimeterX |
| 6 | `hardwareConcurrency` / `deviceMemory` | Advanced fingerprinters |
| 7 | `outerWidth` / `outerHeight` offset | Headless detection |
| 8 | Canvas fingerprint noise | Cloudflare Turnstile |

Launch args: `--disable-blink-features=AutomationControlled`, `--no-sandbox`

## Human Behavior Helpers

```javascript
// Random delay between actions (ms range)
await humanDelay(300, 800);

// Type with human-like speed (per character delay)
await humanType(page, 'input[name="q"]', 'search query');

// Natural mouse movement (5-10 random moves)
await simulateMouseMovement(page);
await simulateMouseMovement(page, 15); // Specify count
```

## Python Support

### undetected-chromedriver (Recommended for Python)

```bash
pip install undetected-chromedriver
```

```python
import undetected_chromedriver as uc

driver = uc.Chrome()  # auto-detects Chrome version
driver.get("https://www.google.com")
search_box = driver.find_element("name", "q")
search_box.send_keys("your search query")
search_box.submit()
```

> `playwright-stealth` for Python only patches at JS level — WebGL still shows SwiftShader. Use `undetected-chromedriver` instead.

### Call Node.js Stealth from Python

```python
import subprocess
result = subprocess.run(['node', 'stealth-script.mjs', query], capture_output=True)
```

## Limitations

- Requires `headless: false` and a display
- Needs real Google Chrome (`channel: 'chrome'`)
- Does NOT bypass CAPTCHAs — only prevents triggering them
- Some sites detect based on behavior patterns — always use `humanDelay`, `humanType`, `simulateMouseMovement`
- TLS/JA3 fingerprint is handled by `channel: 'chrome'` (uses real Chrome binary)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ERR_MODULE_NOT_FOUND` | Run `npm install rebrowser-playwright` in script directory |
| Browser not opening | Verify Chrome is installed |
| WebGL shows SwiftShader | Confirm import is from `rebrowser-playwright`, not `playwright` |
| Still getting detected | Add `simulateMouseMovement()` and `humanDelay()` between actions |
| Process hangs | Ensure `browser.close()` is in a `finally` block |
| `SyntaxError: await` | File must be `.mjs` or have `"type": "module"` in package.json |

## Stealth Template

The full `stealth-template.mjs` is available at:
[references/scripts/stealth-template.mjs](scripts/stealth-template.mjs)

Test stealth bypass:
```bash
node scripts/bot-detection-test.mjs  # Tests against bot.sannysoft.com
```
