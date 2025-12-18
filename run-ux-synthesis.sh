#!/bin/bash

# UX Assessment Synthesis - Combines all persona reports into a unified assessment

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSESSMENTS_DIR="$PROJECT_DIR/.chrome-devtools-mcp/assessments"

echo "=========================================="
echo "   UX Assessment Synthesis"
echo "=========================================="
echo ""

# Check for persona reports
report_count=0
for i in 1 2 3 4 5; do
    if [ -f "$ASSESSMENTS_DIR/persona-$i-"*.md ]; then
        report_count=$((report_count + 1))
    fi
done

if [ "$report_count" -lt 3 ]; then
    echo "WARNING: Only $report_count/5 persona reports found."
    echo "Run the swarm first: ./run-ux-swarm.sh"
    echo ""
fi

echo "Running synthesis..."
echo ""

cd "$PROJECT_DIR"

claude --print "Read all persona assessment reports in .chrome-devtools-mcp/assessments/ (persona-1-maya.md through persona-5-emily.md). Create a comprehensive combined assessment at .chrome-devtools-mcp/assessments/COMBINED.md that includes:

## Executive Summary
- Overall product assessment across all personas
- Key strengths identified by multiple personas
- Critical issues found by multiple personas

## Persona Ratings Matrix
| Persona | Role | Rating | Would Return? |
|---------|------|--------|---------------|
| (Fill from each report) |

## Consensus Findings
### Issues Found by 3+ Personas
- List issues mentioned by multiple personas

### Unique Insights
- Valuable observations from individual personas

## Priority Recommendations
1. High Priority (mentioned by 3+ personas)
2. Medium Priority (mentioned by 2 personas)
3. Consider (single persona, but valuable)

## Screenshots Summary
Reference key screenshots that illustrate findings.

Be thorough and cite specific quotes from each persona's report."
