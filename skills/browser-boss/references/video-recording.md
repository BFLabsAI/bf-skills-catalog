# Video Recording

Capture browser automation sessions as video for debugging, documentation, or verification. Produces WebM (VP8/VP9 codec).

Sources: agent-browser/video-recording.md, playwright-cli/video-recording.md.

---

## agent-browser

```bash
agent-browser record start ./demo.webm    # Start recording
# ... perform actions ...
agent-browser record stop                 # Stop and save
agent-browser record restart ./take2.webm # Stop current + start new
```

**Patterns:**
```bash
# Debug automation failures
agent-browser record start ./debug-$(date +%Y%m%d-%H%M%S).webm
# ... automation steps ...
agent-browser record stop

# CI/CD evidence
cleanup() { agent-browser record stop 2>/dev/null || true; agent-browser close 2>/dev/null || true; }
trap cleanup EXIT
agent-browser record start ./test-evidence.webm
```

---

## playwright-cli

```bash
playwright-cli video-start demo.webm
playwright-cli video-chapter "Getting Started" --description="Opening homepage" --duration=2000
# ... perform actions ...
playwright-cli video-chapter "Filling Form" --description="Entering data" --duration=2000
playwright-cli video-stop
```

### Advanced: Scripted Video with Overlays

For polished documentation videos, use `run-code` with the screencast API. Overlays are `pointer-events: none` — they don't interfere with page interactions.

```javascript
// playwright-cli run-code --filename video-script.js
async page => {
  await page.screencast.start({ path: 'video.webm', size: { width: 1280, height: 800 } });
  await page.goto('https://example.com');

  // Chapter card (blurs page, blocks until duration expires)
  await page.screencast.showChapter('Step 1: Add Items', {
    description: 'Adding items to the list.',
    duration: 2000,
  });

  // Type with human-like speed
  await page.getByRole('textbox').pressSequentially('Walk the dog', { delay: 60 });
  await page.getByRole('textbox').press('Enter');
  await page.waitForTimeout(1000);

  // Sticky annotation overlay
  const annotation = await page.screencast.showOverlay(`
    <div style="position: absolute; top: 8px; right: 8px;
      padding: 6px 12px; background: rgba(0,0,0,0.7);
      border-radius: 8px; font-size: 13px; color: white;">
      ✓ Item added
    </div>
  `);
  await page.waitForTimeout(1500);
  await annotation.dispose();

  // Highlight element with bounding box
  const bounds = await page.getByText('Walk the dog').boundingBox();
  await page.screencast.showOverlay(`
    <div style="position: absolute;
      top: ${bounds.y}px; left: ${bounds.x}px;
      width: ${bounds.width}px; height: ${bounds.height}px;
      border: 2px solid red;"></div>
  `, { duration: 2000 });

  await page.screencast.stop();
}
```

### Overlay API

| Method | Use Case |
|--------|----------|
| `showChapter(title, { description?, duration? })` | Full-screen section card with blurred backdrop |
| `showOverlay(html, { duration? })` | Custom HTML overlay (callouts, labels, highlights) |
| `disposable.dispose()` | Remove sticky overlay added without duration |
| `hideOverlays()` / `showOverlays()` | Temporarily toggle all overlays |

---

## Best Practices (Both Tools)

1. Use descriptive filenames with date/context.
2. Add pauses (`agent-browser wait 500` or `page.waitForTimeout(1000)`) for human viewing.
3. Combine with screenshots for key frames.
4. Always stop recording in error handlers (`trap cleanup EXIT` or `finally` block).

## Tracing vs Video

| Feature | Video | Tracing |
|---------|-------|---------|
| Output | WebM file | Trace file (Trace Viewer) |
| Shows | Visual recording | DOM, network, console, actions |
| Best for | Demos, documentation | Debugging, analysis |
| Size | Larger | Smaller |
