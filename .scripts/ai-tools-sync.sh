#!/bin/bash
SOURCE="/Users/dpedrini/Projects/dannys-pm-workspace-care"
SYNC_REPO="$SOURCE/.scripts/.ai-tools-sync"
LOG_FILE="$SOURCE/.scripts/ai-tools-sync.log"
REMOTE="https://github.com/your-org/dannys-ai-tools.git"

notify() {
    osascript -e "display notification \"$1\" with title \"AI Tools Sync\"" 2>> "$LOG_FILE"
}

CURRENT_BRANCH=$(git -C "$SOURCE" rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: skipped — $SOURCE is on branch '$CURRENT_BRANCH', not main" >> "$LOG_FILE"
    notify "Sync skipped — source workspace is on branch '$CURRENT_BRANCH', not main."
    exit 0
fi

if [ ! -d "$SYNC_REPO/.git" ]; then
    mkdir -p "$SYNC_REPO"
    if ! git clone --depth 1 "$REMOTE" "$SYNC_REPO" >> "$LOG_FILE" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: could not clone $REMOTE" >> "$LOG_FILE"
        notify "AI tools sync init failed — check ai-tools-sync.log"
        exit 1
    fi
fi

# Mirror workspace folders into the push buffer (source of truth stays in SOURCE).
rsync -a --delete "$SOURCE/.claude/skills/" "$SYNC_REPO/skills/" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: rsync failed for skills/" >> "$LOG_FILE"
    notify "AI tools sync failed — rsync error on skills/. Check ai-tools-sync.log"
    exit 1
fi

rsync -a --delete "$SOURCE/.claude/agents/" "$SYNC_REPO/agents/" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: rsync failed for agents/" >> "$LOG_FILE"
    notify "AI tools sync failed — rsync error on agents/. Check ai-tools-sync.log"
    exit 1
fi

rsync -a --delete "$SOURCE/Templates/" "$SYNC_REPO/Templates/" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: rsync failed for Templates/" >> "$LOG_FILE"
    notify "AI tools sync failed — rsync error on Templates/. Check ai-tools-sync.log"
    exit 1
fi

cd "$SYNC_REPO" || { echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: Could not cd to $SYNC_REPO" >> "$LOG_FILE"; notify "Could not cd to sync buffer"; exit 1; }

git add -A

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    if ! git commit -m "Auto-sync $TIMESTAMP" >> "$LOG_FILE" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: commit failed" >> "$LOG_FILE"
        notify "Commit failed — check ai-tools-sync.log"
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
        notify "Sync push failed twice — needs manual fix. Check ai-tools-sync.log"
    fi
fi
