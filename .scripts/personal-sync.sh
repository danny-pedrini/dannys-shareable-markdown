#!/bin/bash
SOURCE="/Users/dpedrini/Projects/dannys-pm-workspace-care"
TARGET="/Users/dpedrini/Projects/dannys-care-personal-files"
LOG_FILE="$SOURCE/.scripts/personal-sync.log"

notify() {
    osascript -e "display notification \"$1\" with title \"Personal Files Sync (care)\"" 2>> "$LOG_FILE"
}

CURRENT_BRANCH=$(git -C "$SOURCE" rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: skipped — $SOURCE is on branch '$CURRENT_BRANCH', not main" >> "$LOG_FILE"
    notify "Sync skipped — source workspace is on branch '$CURRENT_BRANCH', not main."
    exit 0
fi

cd "$TARGET" || { echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: Could not cd to $TARGET" >> "$LOG_FILE"; notify "Could not cd to $TARGET"; exit 1; }

rsync -a --delete "$SOURCE/.claude/" "$TARGET/.claude/"
rsync -a --delete --exclude='*.log' --exclude='.shareable-sync/' "$SOURCE/.scripts/" "$TARGET/.scripts/"
rsync -a --delete "$SOURCE/AI-Reference-Materials/" "$TARGET/AI-Reference-Materials/"
rsync -a --delete "$SOURCE/Learning-and-Development/" "$TARGET/Learning-and-Development/"
rsync -a --delete "$SOURCE/Templates/" "$TARGET/Templates/"
# CLAUDE.md is a symlink to AGENTS.md, so copy both or the link points at nothing.
rsync -a "$SOURCE/AGENTS.md" "$TARGET/AGENTS.md"
rsync -a "$SOURCE/CLAUDE.md" "$TARGET/CLAUDE.md"
mkdir -p "$TARGET/Quality-of-Care"
rsync -a "$SOURCE/Quality-of-Care/Danny's To Do List.md" "$TARGET/Quality-of-Care/Danny's To Do List.md"
# Renamed or moved on 2026-11-20 and 2026-11-23 (AI-Learning became AI-Reference-Materials). Remove the stale copies so the target matches the source.
rm -rf "$TARGET/AI-Best-Practices" "$TARGET/AI-Learning" "$TARGET/Danny's To Do List.md"

git add -A

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    if ! git commit -m "Auto-sync $TIMESTAMP" >> "$LOG_FILE" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: commit failed" >> "$LOG_FILE"
        notify "Commit failed — check personal-sync.log"
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
        notify "Sync push failed twice — needs manual fix. Check personal-sync.log"
    fi
fi
