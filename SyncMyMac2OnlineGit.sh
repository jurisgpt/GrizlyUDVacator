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
#
# Usage: Run this from your repo directory:
#   ./SyncMyMac2OnlineGit.sh
#
# Requirements: You must already have Git set up and a remote called 'origin'
################################################################################

# Check for uncommitted changes first
echo ""
echo "🔍 Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Uncommitted changes detected. Please commit or stash before syncing."
    exit 1
fi

echo ""
echo "🚀 Starting SyncMyMac2OnlineGit"
echo "📁 Working in directory: $(pwd)"
echo "⏰ Current time: $(date)"

echo ""
echo "🔄 Step 1: Fetching latest changes from remote..."
git fetch origin

# Get the commit hashes for comparison
LOCAL=$(git rev-parse @)                 # Current local commit
REMOTE=$(git rev-parse origin/main)     # Latest commit on GitHub
BASE=$(git merge-base @ origin/main)    # Common ancestor of local and remote

echo ""
echo "📊 Comparing local vs. GitHub..."

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



