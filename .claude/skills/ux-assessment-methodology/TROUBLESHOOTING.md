# Troubleshooting Common Issues

Solutions for common problems encountered during UX assessments.

---

## Screenshot Path Errors

### Error: "file path is outside of the output directory"

**Cause**: Chrome DevTools MCP requires screenshots within its designated output directory.

**Solution**: Use relative paths within `.chrome-devtools-mcp/` directory.

```
# Good
take_screenshot(filename: "assessments/persona-1/01-landing.png")

# Bad
take_screenshot(filename: "/tmp/screenshots/01-landing.png")
take_screenshot(filename: "/Users/me/Desktop/screenshot.png")
```

**Best Practice**: Create your output directory first:
```bash
mkdir -p .chrome-devtools-mcp/assessments/persona-1
```

---

## 404 Errors on Discovery Routes

### Expected routes that may return 404:
- `/discovery/learning-path`
- `/discovery/tldr`
- `/discovery/techniques`
- `/discovery/rising`
- `/discovery/reproducible`

**What to do**:

1. **Document the missing feature** - This is a finding, not a blocker
2. **Take a screenshot** of the 404 page as evidence
3. **Look for alternatives** on the main page:
   - Trending widget might replace `/discovery/rising`
   - Research Advisor might replace `/discovery/techniques`
   - "Has Code" filter might replace `/discovery/reproducible`
4. **Note the gap** in your final report under "Missing Expected Features"
5. **Continue with remaining steps** - Don't let missing features block the assessment

**Report format**:
```markdown
### Step 6: Learning Path Assessment
- **Screenshot**: `06-learning-path-404.png`
- **Status**: Feature not available (404)
- **Alternative found**: None / [describe alternative if found]
- **Impact**: [How this affects your workflow]
- **Emotional state**: [1-5]
```

---

## Search Returns 0 Results

### When specific/semantic queries return nothing:

**Cause**: Basic search may use keyword matching only, not semantic understanding.

**Solutions**:

1. **Try the Research Advisor** - It often handles natural language better
   ```
   Instead of: "efficient attention mechanisms mobile"
   Use Advisor: "I'm looking for papers on efficient attention for mobile deployment"
   ```

2. **Simplify to keywords** - Remove qualifiers
   ```
   Instead of: "efficient attention mechanisms for mobile deployment"
   Try: "attention transformer"
   ```

3. **Document the limitation** - This is valuable UX feedback
   ```markdown
   | Query | Results | Notes |
   |-------|---------|-------|
   | "efficient attention mechanisms mobile" | 0 | Too specific |
   | "attention transformer" | 101 | Broad works |
   ```

4. **Compare search vs Advisor** - Note the capability gap in your report

---

## Browser Already In Use Errors

### Error: "Browser is already in use" or "Cannot connect to browser"

**Cause**: Another process is using the Chrome instance, or previous session wasn't closed properly.

**Solutions**:

1. **Close the browser explicitly**:
   ```
   close_page()
   ```

2. **Wait a moment** before restarting (1-2 seconds)

3. **Restart navigation**:
   ```
   navigate_page(url: "http://localhost:3000")
   ```

4. **If persistent**, the MCP server may need restart. Note this in your assessment and continue with available functionality.

**Prevention**: Avoid running multiple browser operations in parallel within a single persona assessment.

---

## Slow or Hanging Pages

### When pages take more than 10 seconds to load:

**What to do**:

1. **Document the performance issue** with timestamp
   ```markdown
   - **Time**: 14:32:15
   - **Page**: /discovery/techniques
   - **Load time**: >30 seconds (timeout)
   ```

2. **Try refreshing once** - Might be transient
   ```
   navigate_page(url: "http://localhost:3000/discovery/techniques")
   ```

3. **If still slow**:
   - Take screenshot of current state
   - Note it as performance issue
   - Continue with assessment

4. **Include in Performance Metrics** section of final report
   ```markdown
   ## Performance Metrics
   - **Slowest operation**: /discovery/techniques at >30s (timeout)
   - **Note**: This page consistently fails to load
   ```

---

## Element Not Found / Click Failures

### When interactions fail:

**Cause**: Element ref doesn't match current page state.

**Solutions**:

1. **Always `take_snapshot()` first**:
   ```
   take_snapshot()  # Get fresh page structure
   click(ref: "button[Search]")  # Use ref from snapshot
   ```

2. **Check if element is visible**:
   - Is it behind a modal?
   - Is it scrolled out of view?
   - Is it disabled?

3. **Try alternative selectors**:
   ```
   # If ref doesn't work, try selector
   click(selector: "#search-button")
   click(selector: "button[type='submit']")
   ```

4. **Wait for element to appear**:
   ```
   wait_for(selector: "#search-button")
   click(selector: "#search-button")
   ```

---

## JavaScript Evaluation Errors

### When `evaluate_script` fails:

**Common causes and solutions**:

1. **Syntax error** - Test in browser console first
   ```javascript
   // Wrap in IIFE to avoid scope issues
   (() => {
     return document.title;
   })()
   ```

2. **Timing issue** - Page not fully loaded
   ```
   wait_for(text: "some content")
   evaluate_script(script: "...")
   ```

3. **Return value** - Always return explicitly
   ```javascript
   // Bad - no return
   (() => { document.title })()

   // Good - explicit return
   (() => { return document.title })()
   ```

---

## Parallel Assessment Conflicts

### When running multiple personas simultaneously:

**Potential issues**:
- Chrome instances competing for resources
- Screenshot path collisions
- Network bandwidth saturation

**Prevention**:

1. **Unique output paths** per persona:
   ```
   persona-1: .chrome-devtools-mcp/assessments/persona-1-maya/
   persona-2: .chrome-devtools-mcp/assessments/persona-2-james/
   ```

2. **Dedicated Chrome instances** - Use assigned `mcp__chrome_X__*` tools only

3. **Resource management** - If system is struggling:
   - Run 3 + 2 personas in waves
   - Add `--headless` to MCP config for lower memory usage

---

## Assessment Continuity

### If assessment is interrupted:

1. **Document where you stopped** - Note last completed step
2. **Resume from last step** - Don't restart from beginning
3. **Note the interruption** in your report:
   ```markdown
   ## Session Notes
   - Assessment interrupted at Step 7 due to [reason]
   - Resumed after [time]
   ```

---

## Getting Help

If you encounter issues not covered here:

1. **Take a snapshot** of the current state
2. **Check console messages**: `list_console_messages(level: "error")`
3. **Document the error** exactly as it appears
4. **Note workaround attempted** and whether it worked
5. **Include in final report** under "Technical Issues Encountered"
