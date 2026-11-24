#!/bin/bash
# Publishes root-level files, AI-Reference-Materials/, .claude/, .scripts/, and Templates/ to
# danny-pedrini/dannys-shareable-markdown. What publishes is set by
# shareable-sync-filter.txt. shareable-scrub.py then scrubs the export copy, and a secret scan
# runs before every commit. Either one blocks the push on any hit.
# Scheduled by ~/Library/LaunchAgents/com.dpedrini.shareable-sync.plist (every 15 min).
SOURCE="/Users/dpedrini/Projects/dannys-pm-workspace-care"
SYNC_REPO="$SOURCE/.scripts/.shareable-sync"
FILTER="$SOURCE/.scripts/shareable-sync-filter.txt"
LOG_FILE="$SOURCE/.scripts/shareable-sync.log"
REMOTE="https://github.com/danny-pedrini/dannys-shareable-markdown.git"

notify() {
    osascript -e "display notification \"$1\" with title \"Shareable Markdown Sync\"" 2>> "$LOG_FILE"
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

CURRENT_BRANCH=$(git -C "$SOURCE" rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log "WARN: skipped — $SOURCE is on branch '$CURRENT_BRANCH', not main"
    notify "Sync skipped — source workspace is on branch '$CURRENT_BRANCH', not main."
    exit 0
fi

# One run at a time. A lock older than 30 minutes is left over from a killed run.
LOCK="$SOURCE/.scripts/.shareable-sync.lock"
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30)" ]; then
    rmdir "$LOCK"
fi
if ! mkdir "$LOCK" 2>/dev/null; then
    log "WARN: skipped — another shareable sync is running"
    exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

if [ ! -d "$SYNC_REPO/.git" ]; then
    # A buffer without its own repo is stale; start it over from the remote.
    rm -rf "$SYNC_REPO"
    mkdir -p "$SYNC_REPO"
    if ! git clone "$REMOTE" "$SYNC_REPO" >> "$LOG_FILE" 2>&1; then
        log "ERROR: could not clone $REMOTE"
        notify "Shareable sync init failed — check shareable-sync.log"
        exit 1
    fi
    git -C "$SYNC_REPO" checkout -B main >> "$LOG_FILE" 2>&1
fi

# Build the export in a fresh temp folder, so every run starts from the raw workspace files
# and files the filter newly excludes simply don't exist there.
STAGE=$(mktemp -d "${TMPDIR:-/tmp}/shareable-stage.XXXXXX") || { log "ERROR: could not create stage dir"; exit 1; }
trap 'rm -rf "$STAGE"; rmdir "$LOCK" 2>/dev/null' EXIT
if ! rsync -a --filter="merge $FILTER" "$SOURCE/" "$STAGE/" >> "$LOG_FILE" 2>&1; then
    log "ERROR: rsync failed"
    notify "Shareable sync failed — rsync error. Check shareable-sync.log"
    exit 1
fi

# Scrub the stage copy only: names become roles, internal links and work emails are removed,
# internal-only files are stubbed, and dollar figures are altered. Blocks the push if anything known survives.
if ! python3 "$SOURCE/.scripts/shareable-scrub.py" "$STAGE" "$SOURCE/.scripts/shareable-sync-private" >> "$LOG_FILE" 2>&1; then
    log "ERROR: scrub check blocked the push. See SCRUB_CHECK_FAILED above."
    notify "Shareable sync blocked — scrub check failed. Check shareable-sync.log"
    exit 1
fi

# Secret scan. Logs file and line only, never the matched value.
SECRET_PATTERNS='ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,}|sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{40,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}|ya29\.[0-9A-Za-z_-]{20,}|1//0[0-9A-Za-z_-]{30,}|napi_[A-Za-z0-9]{30,}|nfp_[A-Za-z0-9]{30,}'
HITS=$(grep -rIEnl -E "$SECRET_PATTERNS" "$STAGE" 2>/dev/null)
if [ -n "$HITS" ]; then
    log "ERROR: secret scan blocked the push. Files with a match:"
    echo "$HITS" | sed "s#^$STAGE/#  #" >> "$LOG_FILE"
    notify "Shareable sync blocked — possible secret found. Check shareable-sync.log"
    exit 1
fi

# Mirror the finished stage into the push buffer. The buffer's .git is excluded, so --delete never touches it.
if ! rsync -a --delete --exclude="/.git" "$STAGE/" "$SYNC_REPO/" >> "$LOG_FILE" 2>&1; then
    log "ERROR: rsync to buffer failed"
    notify "Shareable sync failed — rsync error. Check shareable-sync.log"
    exit 1
fi

# Guard: only ever commit inside the buffer's own repo, never a parent repo.
if [ "$(git -C "$SYNC_REPO" rev-parse --show-toplevel 2>/dev/null)" != "$SYNC_REPO" ]; then
    log "ERROR: $SYNC_REPO is not its own git repo. Refusing to commit."
    notify "Shareable sync stopped — push buffer lost its git repo. Check shareable-sync.log"
    exit 1
fi

cd "$SYNC_REPO" || { log "ERROR: Could not cd to $SYNC_REPO"; notify "Could not cd to sync buffer"; exit 1; }

git add -A

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    if ! git commit -m "Auto-sync $TIMESTAMP" >> "$LOG_FILE" 2>&1; then
        log "ERROR: commit failed"
        notify "Commit failed — check shareable-sync.log"
        exit 1
    fi
fi

# Always attempt the push (even with nothing new this run) so a previously
# stuck push gets retried automatically instead of sitting unpushed forever.
if git push -u origin main >> "$LOG_FILE" 2>&1; then
    log "OK: pushed changes"
else
    log "WARN: push rejected, retrying with pull --rebase"
    if git pull --rebase origin main >> "$LOG_FILE" 2>&1 && git push -u origin main >> "$LOG_FILE" 2>&1; then
        log "OK: pushed changes after rebase retry"
    else
        log "ERROR: push failed after rebase retry"
        notify "Sync push failed twice — needs manual fix. Check shareable-sync.log"
    fi
fi
