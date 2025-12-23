#!/bin/bash

# UX Assessment Swarm - Parallel Persona Execution
# Launches 5 separate Claude Code sessions, each conducting an authentic UX assessment
# as a different researcher persona with their own Chrome browser instance.
#
# Each run creates a unique timestamped folder containing:
# - Screenshots for each persona
# - Assessment reports
# - Log files

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSESSMENTS_BASE="$PROJECT_DIR/.chrome-devtools-mcp/assessments"
PROMPTS_DIR="$PROJECT_DIR/.chrome-devtools-mcp/prompts"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Create unique run directory for this execution
RUN_DIR="$ASSESSMENTS_BASE/runs/$TIMESTAMP"
LOG_DIR="$RUN_DIR/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   AI Paper Atlas - UX Assessment Swarm${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Define personas with their Chrome instance and directory names
declare -a PERSONAS=("maya" "james" "sarah" "raj" "emily")
declare -a PERSONA_NAMES=("Dr. Maya Chen" "Prof. James Williams" "Sarah Kim" "Dr. Raj Patel" "Dr. Emily Zhang")
declare -a PERSONA_DIRS=("maya-chen" "james-williams" "sarah-kim" "raj-patel" "emily-zhang")
declare -a CHROME_INSTANCES=("chrome-1" "chrome-2" "chrome-3" "chrome-4" "chrome-5")
declare -a PERSONA_COLORS=("$RED" "$GREEN" "$YELLOW" "$BLUE" "$PURPLE")

# Create run directory structure
echo -e "${BLUE}Creating run directory: ${RUN_DIR}${NC}"
mkdir -p "$LOG_DIR"
for dir in "${PERSONA_DIRS[@]}"; do
    mkdir -p "$RUN_DIR/$dir"
done

echo -e "${YELLOW}Timestamp:${NC} $TIMESTAMP"
echo -e "${YELLOW}Run directory:${NC} $RUN_DIR"
echo ""

# Check if dev server is running
echo -e "${BLUE}Checking if dev server is running...${NC}"
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Dev server is not running at http://localhost:3000${NC}"
    echo -e "${YELLOW}Please start the dev server first: npm run dev${NC}"
    exit 1
fi
echo -e "${GREEN}Dev server is running.${NC}"
echo ""

# Array to hold PIDs
declare -a PIDS=()

echo -e "${CYAN}Launching 5 parallel UX assessments...${NC}"
echo -e "${YELLOW}Model: Claude Sonnet 4.5 (--model sonnet)${NC}"
echo -e "${YELLOW}Using --allowedTools to enable Chrome DevTools MCP access${NC}"
echo ""

# Launch each persona in parallel
for i in "${!PERSONAS[@]}"; do
    persona="${PERSONAS[$i]}"
    name="${PERSONA_NAMES[$i]}"
    persona_dir="${PERSONA_DIRS[$i]}"
    chrome="${CHROME_INSTANCES[$i]}"
    color="${PERSONA_COLORS[$i]}"
    prompt_file="$PROMPTS_DIR/persona-$((i+1))-$persona.md"
    log_file="$LOG_DIR/persona-$((i+1))-$persona.log"

    # Paths for this run
    screenshot_dir="$RUN_DIR/$persona_dir"
    report_file="$RUN_DIR/persona-$((i+1))-$persona.md"

    # Relative paths for the prompts (from project root)
    rel_screenshot_dir=".chrome-devtools-mcp/assessments/runs/$TIMESTAMP/$persona_dir"
    rel_report_file=".chrome-devtools-mcp/assessments/runs/$TIMESTAMP/persona-$((i+1))-$persona.md"

    echo -e "${color}[$((i+1))/5] Launching ${name} (using ${chrome})...${NC}"

    # Read the prompt file
    if [ ! -f "$prompt_file" ]; then
        echo -e "${RED}ERROR: Prompt file not found: $prompt_file${NC}"
        exit 1
    fi

    # Define allowed tools for this persona's Chrome instance
    ALLOWED_TOOLS="mcp__${chrome}__*,Read,Write,Glob,Grep"

    # Substitute placeholders in the prompt and launch Claude Code
    # Placeholders:
    #   {{SCREENSHOT_DIR}} - where to save screenshots
    #   {{REPORT_FILE}} - where to write the final report
    #   {{RUN_TIMESTAMP}} - the run timestamp
    (
        cd "$PROJECT_DIR"
        sed -e "s|{{SCREENSHOT_DIR}}|${rel_screenshot_dir}|g" \
            -e "s|{{REPORT_FILE}}|${rel_report_file}|g" \
            -e "s|{{RUN_TIMESTAMP}}|${TIMESTAMP}|g" \
            "$prompt_file" | claude --print --model sonnet --allowedTools "$ALLOWED_TOOLS" > "$log_file" 2>&1
    ) &

    PIDS+=($!)
    echo -e "  ${color}PID: ${PIDS[$i]} | Model: sonnet | Chrome: ${chrome}${NC}"
    echo -e "  ${color}Screenshots: ${rel_screenshot_dir}${NC}"

    # Longer delay between launches to avoid API rate limiting
    # When multiple Claude sessions start simultaneously, some may get rate-limited
    # and exit silently. Staggering launches by 15s gives each session time to initialize.
    if [ $i -lt $((${#PERSONAS[@]} - 1)) ]; then
        echo -e "  ${YELLOW}Waiting 15s before next launch (avoiding rate limits)...${NC}"
        sleep 15
    fi
done

echo ""
echo -e "${CYAN}All 5 assessments launched. Waiting for completion...${NC}"
echo -e "${YELLOW}This may take 10-15 minutes. Each persona is exploring the app authentically.${NC}"
echo ""

# Function to check if a process is still running
check_status() {
    local running=0
    for i in "${!PIDS[@]}"; do
        if kill -0 "${PIDS[$i]}" 2>/dev/null; then
            running=$((running + 1))
        fi
    done
    echo $running
}

# Wait with status updates
while true; do
    running=$(check_status)
    if [ "$running" -eq 0 ]; then
        break
    fi
    echo -e "${BLUE}[$running/5 assessments still running...]${NC}"
    sleep 30
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   All assessments complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check for generated reports and diagnose failures
echo -e "${CYAN}Generated reports:${NC}"
failed_count=0
for i in "${!PERSONAS[@]}"; do
    persona="${PERSONAS[$i]}"
    name="${PERSONA_NAMES[$i]}"
    report_file="$RUN_DIR/persona-$((i+1))-$persona.md"
    log_file="$LOG_DIR/persona-$((i+1))-$persona.log"

    if [ -f "$report_file" ]; then
        size=$(wc -c < "$report_file" | tr -d ' ')
        echo -e "  ${GREEN}[OK]${NC} $name -> persona-$((i+1))-$persona.md (${size} bytes)"
    else
        log_size=$(wc -c < "$log_file" 2>/dev/null | tr -d ' ' || echo "0")
        if [ "$log_size" -lt 10 ]; then
            echo -e "  ${RED}[FAILED]${NC} $name -> Session terminated early (log: ${log_size} bytes)"
            echo -e "         ${YELLOW}Likely cause: API rate limiting or MCP connection failure${NC}"
        else
            echo -e "  ${RED}[INCOMPLETE]${NC} $name -> Session ran but no report (log: ${log_size} bytes)"
            echo -e "         ${YELLOW}Likely cause: Context exhaustion before report writing${NC}"
        fi
        failed_count=$((failed_count + 1))
    fi
done

if [ $failed_count -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠ $failed_count persona(s) failed to complete. Consider:${NC}"
    echo -e "  ${YELLOW}1. Re-running the swarm (transient API issues)${NC}"
    echo -e "  ${YELLOW}2. Running failed personas individually with: claude --model sonnet${NC}"
fi

echo ""
echo -e "${CYAN}Screenshots captured:${NC}"
total_screenshots=0
for i in "${!PERSONAS[@]}"; do
    persona_dir="${PERSONA_DIRS[$i]}"
    name="${PERSONA_NAMES[$i]}"
    count=$(find "$RUN_DIR/$persona_dir" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    total_screenshots=$((total_screenshots + count))
    if [ "$count" -gt 0 ]; then
        echo -e "  ${GREEN}${name}:${NC} $count screenshots"
    else
        echo -e "  ${RED}${name}:${NC} 0 screenshots"
    fi
done
echo -e "  ${CYAN}Total:${NC} $total_screenshots screenshots"

echo ""
echo -e "${CYAN}Run directory:${NC} $RUN_DIR"
echo -e "${CYAN}Log files:${NC} $LOG_DIR"
echo ""

# Create a summary file in the run directory
cat > "$RUN_DIR/SUMMARY.md" << EOF
# UX Assessment Run: $TIMESTAMP

## Reports
$(for i in "${!PERSONAS[@]}"; do
    persona="${PERSONAS[$i]}"
    name="${PERSONA_NAMES[$i]}"
    report="persona-$((i+1))-$persona.md"
    if [ -f "$RUN_DIR/$report" ]; then
        echo "- [x] $name - $report"
    else
        echo "- [ ] $name - $report (MISSING)"
    fi
done)

## Screenshots
$(for i in "${!PERSONAS[@]}"; do
    persona_dir="${PERSONA_DIRS[$i]}"
    name="${PERSONA_NAMES[$i]}"
    count=$(find "$RUN_DIR/$persona_dir" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    echo "- $name: $count screenshots in $persona_dir/"
done)

## Logs
- Log directory: logs/
EOF

echo -e "${GREEN}Summary written to: $RUN_DIR/SUMMARY.md${NC}"
echo ""
echo -e "${YELLOW}Next step: Review reports in $RUN_DIR${NC}"
echo ""
