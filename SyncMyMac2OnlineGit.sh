#!/bin/bash

################################################################################
# 🤖 SyncMyMac2OnlineGit.sh
# 
# This script keeps your Mac's local Git repo in perfect sync with GitHub.
# It automatically handles:
#   - Pulling changes with rebase
#   - Pushing your commits
#   - Resolving divergence with rebase
#   - Checking for uncommitted changes
#   - Logging all activity to a timestamped file
#
# Usage: Run this from your repo directory:
#   ./SyncMyMac2OnlineGit.sh
#
# Requirements: You must already have Git set up and a remote called 'origin'
################################################################################

# 🗂️ Ensure logs directory exists
mkdir -p logs

# 🕒 Timestamp in YYYYMMDD_HHMM format
TIMESTAMP=$(date "+%Y%m%d_%H%M")
LOGFILE="logs/GitSyncStatusReport_${TIMESTAMP}.log"

# ⏺️ Redirect stdout and stderr to both terminal and logfile
exec > >(tee -a "$LOGFILE") 2>&1

echo "📓 Logging to: $LOGFILE"

echo ""
echo "🚀 Starting SyncMyMac2OnlineGit"
echo "📁 Working in directory: $(pwd)"
echo "⏰ Current time: $(date)"

echo ""
echo "🔍 Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Uncommitted changes detected. Please commit or stash before syncing."
    exit 1
fi

log_message "" | tee -a "$LOG_FILE"
log_message "🔄 Step 1: Fetching latest changes from remote..." | tee -a "$LOG_FILE"
git fetch origin 2>&1 | tee -a "$LOG_FILE"

# Get the commit hashes for comparison
LOCAL=$(git rev-parse @)                 # Current local commit
REMOTE=$(git rev-parse origin/main)     # Latest commit on GitHub
BASE=$(git merge-base @ origin/main)    # Common ancestor of local and remote

log_message "" | tee -a "$LOG_FILE"
log_message "📊 Comparing local vs. GitHub..." | tee -a "$LOG_FILE"

################################################################################
# SYNC LOGIC - What should we do based on local/remote state?
################################################################################

# Case 1: Local and remote are the same
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Your local repo is completely up to date with GitHub."
    echo "🎉 Nothing to do! You're in perfect sync."

# Case 2: Local is behind (GitHub has new commits you don't have)
elif [ "$LOCAL" = "$BASE" ]; then
    echo "📥 Your Mac is BEHIND GitHub."
    echo "📄 These commits exist on GitHub that you don't have:"
    git log --oneline $LOCAL..$REMOTE
    echo ""
    echo "🔄 Pulling changes with rebase..."
    git pull --rebase origin main

# Case 3: Local is ahead (you have unpushed commits)
elif [ "$REMOTE" = "$BASE" ]; then
    echo "🚀 Your Mac is AHEAD of GitHub."
    echo "📄 These commits will be pushed to GitHub:"
    git log --oneline $REMOTE..$LOCAL
    echo ""
    echo "🔼 Pushing your changes to GitHub..."
    git push origin main

# Case 4: Local and remote have diverged — both changed
else
    echo "🔄 Your Mac and GitHub have diverged."
    echo "📄 Your local-only commits:"
    git log --oneline $BASE..$LOCAL
    echo ""
    echo "🌐 GitHub-only commits:"
    git log --oneline $BASE..$REMOTE
    echo ""
    echo "🔄 Attempting to rebase your changes on top of GitHub..."
    git pull --rebase origin main
    
    # Check if rebase was successful
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Rebase successful! Pushing changes..."
        git push origin main
    else
        echo ""
        echo "⚠️ Rebase failed. Please resolve conflicts manually and run:"
        echo "    git rebase --continue"
        echo "  Then run this script again."
        exit 1
    fi
fi

echo ""
echo "✅ SyncMyMac2OnlineGit finished."
echo "🌟 Your repository is now in sync with GitHub."
echo "💡 Tip: You can re-run this script anytime to re-check sync status."
echo ""
echo "📝 Sync activity has been logged to: $LOG_FILE"
echo ""



