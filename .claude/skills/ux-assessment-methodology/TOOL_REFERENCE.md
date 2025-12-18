# Chrome DevTools MCP Tool Reference

Complete reference for all Chrome DevTools MCP tools available for UX assessment.

---

## Navigation & Page Management

### `navigate_page`
Load a URL in the browser.

```
navigate_page(url: "http://localhost:3000")
```

### `close_page`
Close the current browser page/tab.

```
close_page()
```

### `new_page`
Open a new browser tab.

```
new_page()
```

### `list_pages`
List all open browser tabs.

```
list_pages()
```

### `select_page`
Switch to a specific browser tab by index.

```
select_page(index: 0)
```

### `wait_for`
Wait for a condition to be met.

```
wait_for(selector: "#content", timeout: 5000)
wait_for(text: "Loading complete")
```

---

## Input & Interaction

### `click`
Click on an element. Use accessibility refs from `take_snapshot` for reliable targeting.

```
click(ref: "button[Submit]")
click(selector: "#search-button")
```

### `fill`
Fill a text input field.

```
fill(ref: "textbox[Search]", text: "efficient attention mechanisms")
```

### `fill_form`
Fill multiple form fields at once.

```
fill_form(fields: [
  {ref: "textbox[Email]", text: "user@example.com"},
  {ref: "textbox[Password]", text: "password123"}
])
```

### `hover`
Hover over an element (useful for tooltips, dropdowns).

```
hover(ref: "link[More options]")
```

### `press_key`
Press a keyboard key.

```
press_key(key: "Enter")
press_key(key: "Escape")
press_key(key: "ArrowDown")
```

### `drag`
Drag and drop between elements.

```
drag(from_ref: "item[1]", to_ref: "dropzone")
```

---

## Inspection & Debugging

### `take_snapshot`
**CRITICAL**: Capture the accessibility tree of the current page. Use this BEFORE any interaction to understand page structure and get reliable element refs.

```
take_snapshot()
```

Returns an accessibility tree with refs like:
```
- heading "AI Paper Atlas" [ref: heading[AI Paper Atlas]]
- button "Search" [ref: button[Search]]
- textbox "Search papers..." [ref: textbox[Search papers...]]
```

**Best Practice**: Always `take_snapshot` before clicking or interacting with elements.

### `take_screenshot`
Capture a visual screenshot of the current page.

```
take_screenshot(filename: "01-landing.png")
take_screenshot(filename: "error-state.png", fullPage: true)
```

**Parameters**:
- `filename`: Where to save (relative to output directory)
- `fullPage`: Capture entire scrollable page (optional)
- `element`: Screenshot specific element only (optional)

### `evaluate_script`
Execute JavaScript in the browser context. Essential for Performance API.

```
evaluate_script(script: "document.title")

# Performance API example:
evaluate_script(script: `
  (() => {
    const perf = performance.getEntriesByType('navigation')[0];
    return {
      loadTime: Math.round(perf.loadEventEnd - perf.startTime),
      domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.startTime)
    };
  })()
`)
```

### `list_console_messages`
Get console output (errors, warnings, logs).

```
list_console_messages()
list_console_messages(level: "error")  # Filter by level
```

### `get_console_message`
Get a specific console message by index.

```
get_console_message(index: 0)
```

---

## Performance & Emulation

### `resize_page`
Set the browser viewport dimensions.

```
resize_page(width: 1440, height: 900)   # Desktop
resize_page(width: 375, height: 812)    # Mobile (iPhone X)
resize_page(width: 768, height: 1024)   # Tablet
```

### `emulate`
Emulate device characteristics (CPU, network).

```
emulate(device: "iPhone 12")
emulate(network: "Slow 3G")
emulate(cpu: 4)  # 4x CPU throttling
```

### `performance_start_trace`
Start recording a performance trace.

```
performance_start_trace()
```

### `performance_stop_trace`
Stop recording and get performance trace data.

```
performance_stop_trace()
```

---

## Network

### `list_network_requests`
List all network requests made by the page.

```
list_network_requests()
```

### `get_network_request`
Get details of a specific network request.

```
get_network_request(id: "request-123")
```

---

## Common Patterns for UX Assessment

### Pattern 1: Navigate and Measure Performance

```python
# Navigate to page
navigate_page(url: "http://localhost:3000")

# Wait for content to load
wait_for(text: "AI Paper Atlas")

# Capture performance metrics
metrics = evaluate_script(script: `
  (() => {
    const perf = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    return {
      loadTime: Math.round(perf.loadEventEnd - perf.startTime),
      firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime
    };
  })()
`)

# Take screenshot
take_screenshot(filename: "01-landing.png")
```

### Pattern 2: Search and Evaluate Results

```python
# Get page structure
take_snapshot()

# Find and fill search box
fill(ref: "textbox[Search papers...]", text: "efficient attention")

# Submit search
press_key(key: "Enter")

# Wait for results
wait_for(text: "results")

# Capture state
take_snapshot()
take_screenshot(filename: "03-search-results.png")
```

### Pattern 3: Click and Examine Detail View

```python
# Get current page structure
take_snapshot()

# Click on first result
click(ref: "link[Paper Title Here]")

# Wait for detail view
wait_for(selector: ".paper-detail")

# Capture detail view
take_snapshot()
take_screenshot(filename: "04-paper-detail.png")
```

### Pattern 4: Check for Missing Features (404 Handling)

```python
# Navigate to expected route
navigate_page(url: "http://localhost:3000/discovery/learning-path")

# Check if 404
snapshot = take_snapshot()

# If 404, document and continue
if "404" in snapshot or "not found" in snapshot.lower():
    take_screenshot(filename: "06-learning-path-404.png")
    # Record as missing feature, continue assessment
```

---

## Troubleshooting Tool Issues

### Element Not Found
If `click` or `fill` fails:
1. Run `take_snapshot()` first
2. Use the exact ref from the snapshot
3. Check if element is visible/enabled

### Screenshot Path Errors
Use paths within the Chrome DevTools MCP output directory:
- Good: `assessments/persona-1/01-landing.png`
- Bad: `/tmp/screenshots/01-landing.png`

### Script Execution Errors
If `evaluate_script` fails:
1. Test script in browser DevTools console first
2. Wrap in IIFE: `(() => { ... })()`
3. Return values explicitly

### Timeout Errors
If `wait_for` times out:
1. Increase timeout parameter
2. Check if condition is actually achievable
3. Take snapshot to see current state
