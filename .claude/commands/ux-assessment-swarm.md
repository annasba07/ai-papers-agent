---
description: Run 5 parallel persona-based UX assessments of AI Paper Atlas
allowed-tools: Bash, Read, Write
---

# UX Assessment Swarm

This command runs 5 parallel UX assessments using different researcher personas. Each persona authentically explores AI Paper Atlas with their own browser instance.

## How It Works

Due to a known limitation where subagents cannot access MCP tools, we use external orchestration:
- A shell script launches 5 separate Claude Code sessions
- Each session has its own Chrome DevTools MCP connection (chrome-1 through chrome-5)
- Each persona explores the app authentically with different searches and paths
- Reports are written to `.chrome-devtools-mcp/assessments/`

## Prerequisites

1. **Dev server running**: `npm run dev` at http://localhost:3000
2. **Chrome MCP instances configured**: You should have chrome-1 through chrome-5 added via:
   ```bash
   claude mcp add chrome-1 -- npx @anthropic-ai/chrome-devtools-mcp@latest --isolated
   claude mcp add chrome-2 -- npx @anthropic-ai/chrome-devtools-mcp@latest --isolated
   claude mcp add chrome-3 -- npx @anthropic-ai/chrome-devtools-mcp@latest --isolated
   claude mcp add chrome-4 -- npx @anthropic-ai/chrome-devtools-mcp@latest --isolated
   claude mcp add chrome-5 -- npx @anthropic-ai/chrome-devtools-mcp@latest --isolated
   ```

## Running the Assessment

### Step 1: Run the Swarm
```bash
./run-ux-swarm.sh
```

This launches 5 parallel Claude sessions. Each persona:
- Opens their own browser via their assigned Chrome MCP instance
- Navigates AI Paper Atlas using their natural search patterns
- Captures screenshots of their journey
- Writes their assessment report

**Duration**: 5-10 minutes depending on system load.

### Step 2: Run Synthesis
```bash
./run-ux-synthesis.sh
```

This reads all 5 persona reports and creates a combined assessment at:
`.chrome-devtools-mcp/assessments/COMBINED.md`

## The 5 Personas

1. **Dr. Maya Chen** (chrome-1) - CMU postdoc, efficient transformers, time-pressured
2. **Prof. James Williams** (chrome-2) - MIT faculty, NLP, teaching focus
3. **Sarah Kim** (chrome-3) - Stanford PhD student, new to field, overwhelmed
4. **Dr. Raj Patel** (chrome-4) - FAANG ML Engineer, production focus
5. **Dr. Emily Zhang** (chrome-5) - National Lab, AI for climate, interdisciplinary

## Output Structure

```
.chrome-devtools-mcp/assessments/
├── screenshots/
│   ├── maya-01-landing.png
│   ├── maya-02-search.png
│   ├── ...
│   ├── emily-05-final.png
├── logs/
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── persona-1-maya.log
│       └── ...
├── persona-1-maya.md
├── persona-2-james.md
├── persona-3-sarah.md
├── persona-4-raj.md
├── persona-5-emily.md
└── COMBINED.md
```

## Troubleshooting

- **"Dev server not running"**: Start with `npm run dev`
- **Chrome MCP not found**: Run `claude mcp list` to verify chrome-1 through chrome-5 exist
- **Missing reports**: Check logs in `.chrome-devtools-mcp/assessments/logs/`
- **Browser not opening**: Ensure Chrome is installed and accessible
