#!/bin/bash

################################################################################
# 🤖 SyncMyMac2OnlineGit.sh
# 
# This script keeps your Mac's local Git repo in perfect sync with GitHub.
# It automatically detects whether:
#   - You are ahead (need to push)
#   - You are behind (need to pull)
#   - You and GitHub have diverged (need to merge manually)
#
# Usage: Run this from your repo directory:
#   ./SyncMyMac2OnlineGit.sh
#
# Requirements: You must already have Git set up and a remote called 'origin'
################################################################################

echo ""
echo "🚀 Starting SyncMyMac2OnlineGit"
echo "📁 Working in directory: $(pwd)"
echo "⏰ Current time: $(date)"
echo "🔍 Step 1: Checking Git status with remote 'origin'..."

# Update your local knowledge of the GitHub remote
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
    echo "🔄 Pulling changes from GitHub into your Mac..."
    git pull origin main --no-rebase

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
    echo "⚠️  Divergence detected! Both your Mac and GitHub have unique commits."
    echo "🧭 You need to merge the histories manually."
    echo ""
    echo "📄 Your local-only commits:"
    git log --oneline $BASE..$LOCAL
    echo ""
    echo "🌐 GitHub-only commits:"
    git log --oneline $BASE..$REMOTE
    echo ""
    echo "🛠️  To fix this, run:"
    echo "    git pull origin main --no-rebase"
    echo "  Then resolve any merge conflicts, commit the result, and run this script again."
fi

echo ""
echo "✅ SyncMyMac2OnlineGit finished."
echo "💡 Tip: You can re-run this script anytime to re-check sync status."
echo ""



