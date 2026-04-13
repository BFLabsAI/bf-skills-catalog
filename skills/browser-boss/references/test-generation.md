# Playwright Test Generation and Running

## Generating Tests via Playwright MCP

When asked to generate a Playwright test for a scenario:
1. Ask for the scenario if not provided.
2. Run all steps one by one using Playwright MCP tools — do NOT generate test code prematurely.
3. Only after completing all steps, emit a TypeScript test using `@playwright/test`.
4. Save in the `tests/` directory.
5. Execute and iterate until it passes.

## Generating Tests via playwright-cli (Code Recording)

Every action with `playwright-cli` generates corresponding Playwright TypeScript code automatically.

### Example Workflow

```bash
playwright-cli open https://example.com/login
playwright-cli snapshot
# Review elements: e1 [textbox "Email"], e2 [textbox "Password"], e3 [button "Sign In"]

playwright-cli fill e1 "user@example.com"
# Generated: await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

playwright-cli fill e2 "password123"
playwright-cli click e3
# Generated: await page.getByRole('button', { name: 'Sign In' }).click();
```

### Building the Test File

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  // Add assertions manually
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

**Best practices:**
- Use semantic/role-based locators (more resilient than CSS selectors).
- Take snapshots to understand page structure before recording.
- Generated code captures actions — add assertions manually.

---

## Running Playwright Tests

```bash
# Run all tests (suppress interactive HTML report)
PLAYWRIGHT_HTML_OPEN=never npx playwright test

# Via custom npm script
PLAYWRIGHT_HTML_OPEN=never npm run test

# Run specific test file
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/login.spec.ts

# Run in headed mode
PLAYWRIGHT_HTML_OPEN=never npx playwright test --headed
```

## Debugging Failing Tests

```bash
# Run with debug mode — prints session name for playwright-cli to attach
PLAYWRIGHT_HTML_OPEN=never npx playwright test --debug=cli
# ...waits at start, prints: "debugging instructions for 'tw-abcdef' session"

# Attach playwright-cli to the paused test
playwright-cli attach tw-abcdef
```

- Keep the test running in background while you explore.
- Use `playwright-cli` to interact and take snapshots.
- Every action generates code you can copy back to the test.
- After finding the fix (locator change, assertion update, or app bug), stop the background run.
- Rerun to confirm the test passes.
