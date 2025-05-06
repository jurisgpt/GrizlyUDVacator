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

# Exit on error
set -e

# Function to handle errors
handle_error() {
  echo "❌ Error occurred at line $1"
  echo "⚠️ Script terminated due to error"
  exit 1
}

# Set up error trapping
trap 'handle_error $LINENO' ERR

# Set timeout for Git operations (10 seconds)
export GIT_TIMEOUT=10

# Function to run Git with timeout
run_git_with_timeout() {
  timeout $GIT_TIMEOUT "$@" || {
    echo "⏱️ Git operation timed out or failed!"
    return 1
  }
}

echo ""
echo "🚀 Starting SyncMyMac2OnlineGit"
echo "📁 Working in directory: $(pwd)"
echo "⏰ Current time: $(date)"
echo "🔍 Step 1: Checking for repository health..."

# Check for and clean bad references
if [ -f ".git/refs/heads/__init__.py" ] || [ -f ".git/refs/remotes/__init__.py" ]; then
  echo "🧹 Cleaning corrupted Git references..."
  find .git -name "__init__.py" -delete
  git update-ref -d refs/remotes/origin/main 2>/dev/null || true
  git reflog expire --expire=now --all 2>/dev/null || true
  git gc --prune=now 2>/dev/null || true
  echo "✅ Repository cleaned"
fi

echo "🔄 Step 2: Fetching latest changes from remote..."
# Update your local knowledge of the GitHub remote
if ! run_git_with_timeout git fetch origin; then
  echo "⚠️ Fetch failed, attempting repository repair..."
  git remote remove origin
  git remote add origin https://github.com/jurisgpt/GrizlyUDVacator.git
  run_git_with_timeout git fetch origin || {
    echo "❌ Repository repair failed. Please fix manually."
    exit 1
  }
fi

# Get the commit hashes for comparison
LOCAL=$(git rev-parse @ 2>/dev/null || echo "unknown")
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "unknown")
BASE=$(git merge-base @ origin/main 2>/dev/null || echo "unknown")

# Check for unknown values
if [ "$LOCAL" = "unknown" ] || [ "$REMOTE" = "unknown" ] || [ "$BASE" = "unknown" ]; then
  echo "❌ Unable to determine repository state. Manual intervention required."
  exit 1
fi

echo ""
echo "📊 Comparing local vs. GitHub..."

# Decision tree based on commit comparison
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✅ Your Mac and GitHub are in sync!"
elif [ "$LOCAL" = "$BASE" ]; then
  echo "🔽 Your Mac is BEHIND GitHub."
  echo "   Running git pull to update your Mac..."
  run_git_with_timeout git pull || {
    echo "❌ Pull failed. Manual intervention required."
    exit 1
  }
  echo "✅ Successfully updated from GitHub!"
elif [ "$REMOTE" = "$BASE" ]; then
  echo "🚀 Your Mac is AHEAD of GitHub."
  echo "📄 These commits will be pushed to GitHub:"
  git log --oneline origin/main..HEAD
  echo ""
  echo "   Running git push to update GitHub..."
  run_git_with_timeout git push origin main || {
    echo "❌ Push failed. Try running git push manually."
    exit 1
  }
  echo "✅ Successfully pushed to GitHub!"
else
  echo "⚠️ Your Mac and GitHub have DIVERGED."
  echo "   This requires manual attention to merge properly."
  echo "   Local commits not on GitHub:"
  git log --oneline origin/main..HEAD
  echo ""
  echo "   GitHub commits not on your Mac:"
  git log --oneline HEAD..origin/main
  echo ""
  echo "❓ Options:"
  echo "   1. Run: git pull --rebase origin main"
  echo "      This puts GitHub's changes first, then adds yours on top."
  echo "   2. Run: git merge origin/main"
  echo "      This creates a merge commit combining both sets of changes."
  exit 0
fi

echo ""
echo "✨ SyncMyMac2OnlineGit complete!"
exit 0
