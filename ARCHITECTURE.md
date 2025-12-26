# Architecture & Common Pitfalls

## Critical Issue: Client vs Server API Calls

### THE PROBLEM

**NEVER set `NEXT_PUBLIC_API_BASE_URL` in development!**

When this env var is set, client-side code tries to call the backend directly from the browser, causing CORS failures. This is the root cause of recurring "0 papers" failures.

### Why This Happens

Next.js has two types of environment variables:

1. **`NEXT_PUBLIC_*`** - Exposed to browser JavaScript
2. **Regular vars** - Server-side only

The codebase has conditional logic like:
```typescript
const endpoint = API_BASE
  ? `${API_BASE}/api/v1/atlas-db/papers`  // ❌ Browser tries to call localhost:8000 = CORS error
  : `/api/atlas/papers`;                   // ✅ Next.js proxy route = works
```

When `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` is set, browsers try to call `localhost:8000` directly, which fails due to CORS.

### The Correct Architecture

```
Browser → Next.js API Routes → Backend
         (always use these)     (localhost:8000)
```

**NOT:**
```
Browser → Backend  ❌ CORS failure
         (localhost:8000)
```

### Environment Setup

**Development (.env.local):**
```bash
# ❌ DO NOT SET - Causes CORS errors
# NEXT_PUBLIC_API_BASE_URL=

# ✅ Server-side only - Used by Next.js API routes
RESEARCH_API_BASE_URL=http://localhost:8000
```

**Production:**
```bash
# ✅ Only set when backend is publicly accessible with CORS configured
NEXT_PUBLIC_API_BASE_URL=https://api.yourproduction.com

# ✅ Also set for server-side API routes
RESEARCH_API_BASE_URL=https://api.yourproduction.com
```

## Testing Protocol

**Before claiming "it works":**

1. ✅ Test API endpoints directly (curl)
2. ✅ Test Next.js API routes (curl localhost:3000/api/*)
3. ✅ **Test actual browser experience** (open localhost:3000 in browser)
4. ✅ Check browser console for errors
5. ✅ Verify papers actually load in UI

**Common mistake:** Testing only #1-2, missing that browser fails at #3.

## Prevention

- Always test with browser DevTools open
- Check for CORS errors in console
- Run health check before UX swarms: `curl localhost:3000/api/health`
- Never assume API tests = working user experience
