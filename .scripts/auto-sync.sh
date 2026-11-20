#!/bin/bash
REPO_DIR="/Users/dpedrini/Projects/dannys-pm-workspace-care"
LOG_FILE="$REPO_DIR/.scripts/auto-sync.log"

notify() {
    osascript -e "display notification \"$1\" with title \"PM Workspace Sync (care)\"" 2>> "$LOG_FILE"
}

cd "$REPO_DIR" || { echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: Could not cd to $REPO_DIR" >> "$LOG_FILE"; notify "Could not cd to $REPO_DIR"; exit 1; }

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: skipped — checked out on '$CURRENT_BRANCH', not main" >> "$LOG_FILE"
    notify "Sync skipped — workspace is on branch '$CURRENT_BRANCH', not main. Switch back to main to resume."
    exit 0
fi

git add -A

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    if ! git commit -m "Auto-sync $TIMESTAMP" >> "$LOG_FILE" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: commit failed" >> "$LOG_FILE"
        notify "Commit failed — check auto-sync.log"
        exit 1
    fi
fi

# Always attempt the push (even with nothing new this run) so a previously
# stuck push gets retried automatically instead of sitting unpushed forever.
if git push origin main >> "$LOG_FILE" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') OK: pushed changes" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: push rejected, retrying with pull --rebase" >> "$LOG_FILE"
    if git pull --rebase origin main >> "$LOG_FILE" 2>&1 && git push origin main >> "$LOG_FILE" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') OK: pushed changes after rebase retry" >> "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: push failed after rebase retry" >> "$LOG_FILE"
        notify "Sync push failed twice — needs manual fix. Check auto-sync.log"
    fi
fi
