#!/bin/bash
# run_daily_crawl_and_evolve.sh
# Scheduled execution wrapper for via54ADIdeahub daily case crawler and algorithm evolver.

PROJECT_DIR="/Users/david/Desktop/developments/via54ADIdeahub"
PYTHON_BIN="$PROJECT_DIR/.mcp_venv/bin/python"
SCRIPT="$PROJECT_DIR/scripts/daily_kb_crawler_and_evolver.py"
LOG_FILE="$PROJECT_DIR/logs/daily_crawl_and_evolve.log"
DATE_STR=$(date +"%Y-%m-%d %H:%M:%S")

export PATH="/Users/david/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export MMX_CLI_PATH="/Users/david/.local/bin/mmx-cli"

mkdir -p "$PROJECT_DIR/logs"

echo "=================================================================" >> "$LOG_FILE"
echo "[$DATE_STR] Starting Daily Knowledge Base Crawl & Evolution Task" >> "$LOG_FILE"
echo "=================================================================" >> "$LOG_FILE"

"$PYTHON_BIN" "$SCRIPT" --threshold 75.0 >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

END_DATE=$(date +"%Y-%m-%d %H:%M:%S")
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$END_DATE] Daily task finished successfully (code 0)." >> "$LOG_FILE"
else
    echo "[$END_DATE] Daily task failed with exit code $EXIT_CODE." >> "$LOG_FILE"
fi

exit $EXIT_CODE
