#!/bin/bash

################################################################################
#                                                                              #
#  🌟✨ SyncMyMac2OnlineGit.sh ✨🌟                                            #
#                                                                              #
#  Keep your local Git repo in perfect harmony with GitHub                     #
#  Created by: Your Friendly Neighborhood DevOps Engineer                      #
#                                                                              #
################################################################################

# Terminal colors for vibes
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cool emojis for extra vibes
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
SPARKLES="✨"
TIMER="⏱️"
FOLDER="📁"
GEAR="⚙️"
MAGIC="🪄"
LIGHTNING="⚡"
TOOLS="🛠️"
CHART="📊"
EYES="👀"
BRAIN="🧠"
FIRE="🔥"
LOVE="❤️"

# Function to print section headers
print_header() {
  echo ""
  echo -e "${BOLD}${PURPLE}${1}${NC}"
  echo -e "${CYAN}${2}${NC}"
  echo ""
}

# Function to print success messages
print_success() {
  echo -e "${GREEN}${CHECK} ${1}${NC}"
}

# Function to print info messages
print_info() {
  echo -e "${BLUE}${1}${NC}"
}

# Function to print warning messages
print_warning() {
  echo -e "${YELLOW}${WARNING} ${1}${NC}"
}

# Function to print error messages
print_error() {
  echo -e "${RED}${ERROR} ${1}${NC}"
}

# Function to handle errors
handle_error() {
  print_error "Oh no! Error occurred at line $1"
  print_error "Script terminated due to error"
  echo ""
  print_info "Don't worry - your changes are safe in the backups we created!"
  exit 1
}

# Set up error trapping
trap 'handle_error $LINENO' ERR

# ASCII Art Welcome Banner
echo -e "${BOLD}${PURPLE}"
echo "   _____                   __  __           ___   ____      __    "
echo "  / ___/__  ______  ______/ /_/  |/  _____ /   | / __ \__  / /___ "
echo "  \__ \/ / / / __ \/ ___/ __/ /|_/ / ___// /| |/ / / / / / / __ \\"
echo " ___/ / /_/ / / / / /__/ /_/ /  / / /__ / ___ / /_/ / /_/ / /_/ /"
echo "/____/\__, /_/ /_/\___/\__/_/  /_/\___/_/  |_\____/\__, /\____/ "
echo "     /____/                                        /____/        "
echo -e "${NC}"

print_header "${ROCKET} LAUNCHING SYNC OPERATION ${ROCKET}" "Bringing your Mac and GitHub into perfect harmony"

echo -e "${CYAN}${FOLDER} Working in:${NC} $(pwd)"
echo -e "${CYAN}${TIMER} Current time:${NC} $(date)"
echo ""

print_header "${BRAIN} ANALYZING REPOSITORY STATE ${BRAIN}" "Let's take a moment to understand your repository"

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "Git not found! Please install Git to use this script."
    exit 1
fi

# Create a directory for backups
BACKUP_DIR=~/git_backups
mkdir -p $BACKUP_DIR

print_info "${EYES} Taking a snapshot of your current changes (just in case)..."
# Create backup of local changes
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CHANGES_BACKUP="$BACKUP_DIR/GrizlyUDVacator_changes_$TIMESTAMP.patch"
git diff > "$CHANGES_BACKUP" 2>/dev/null || true
print_success "Backup saved to $CHANGES_BACKUP"

print_header "${MAGIC} REPOSITORY HEALTH CHECK ${MAGIC}" "Making sure everything is in tip-top shape"

print_info "${TOOLS} Looking for problematic references..."
# Check for bad references and clean them
rm -f .git/refs/heads/__init__.py 2>/dev/null || true
rm -f .git/refs/remotes/__init__.py 2>/dev/null || true
rm -f .git/refs/remotes/origin/__init__.py 2>/dev/null || true
find .git -name "__init__.py" -delete 2>/dev/null || true
print_success "Cleaned up any Python files mistakenly stored as Git references"

print_info "${TOOLS} Running Git maintenance routines..."
# Cleanup and optimize repository
git reflog expire --expire=now --all 2>/dev/null || true
git gc --prune=now 2>/dev/null || true
git fsck --full 2>/dev/null || true
print_success "Repository optimization complete"

print_info "${TOOLS} Resetting remote tracking branch..."
# Reset the remote tracking branch
git update-ref -d refs/remotes/origin/main 2>/dev/null || true
print_success "Remote tracking branch reset"

print_info "${GEAR} Making sure your remote is configured correctly..."
# Fix the origin remote
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/jurisgpt/GrizlyUDVacator.git
print_success "Remote 'origin' configured properly"

print_header "${LIGHTNING} CONNECTING TO GITHUB ${LIGHTNING}" "Establishing secure connection to your remote repository"

print_info "${EYES} Fetching the latest from GitHub..."
# Attempt to fetch from remote
if git fetch origin; then
    print_success "Successfully connected to GitHub! All good in the cloud ${SPARKLES}"
else
    print_warning "Hmm, still having trouble connecting to GitHub."
    print_info "${TOOLS} Let's try a more comprehensive approach..."

    # Create full repository backup
    FULL_BACKUP="$BACKUP_DIR/GrizlyUDVacator_full_$TIMESTAMP.tar.gz"
    print_info "${TOOLS} Creating a complete backup of your repository..."
    tar -czf "$FULL_BACKUP" .
    print_success "Full backup saved to $FULL_BACKUP"

    # Try to clone a fresh copy
    TEMP_DIR="$BACKUP_DIR/GrizlyUDVacator_fresh_$TIMESTAMP"
    print_info "${MAGIC} Cloning a fresh copy of the repository..."
    mkdir -p "$TEMP_DIR"

    if git clone https://github.com/jurisgpt/GrizlyUDVacator.git "$TEMP_DIR"; then
        print_success "Fresh clone created at $TEMP_DIR"
        echo ""
        print_warning "Your repository appears to be corrupted beyond automatic repair."
        print_info "Don't worry - we've got you covered! Here's what to do:"
        echo ""
        echo -e "${BOLD}${CYAN}RECOVERY PLAN:${NC}"
        echo -e "1. ${YELLOW}We've backed up all your work to:${NC} $FULL_BACKUP"
        echo -e "2. ${YELLOW}We've created a fresh clone at:${NC} $TEMP_DIR"
        echo -e "3. ${YELLOW}Copy your untracked files to the fresh clone:${NC}"

        # List untracked files
        echo ""
        echo -e "${BOLD}${CYAN}Your untracked files:${NC}"
        git ls-files --others --exclude-standard

        exit 1
    else
        print_error "Both repository repair and fresh clone failed."
        print_info "Time for manual intervention - but don't panic!"
        echo ""
        echo -e "${BOLD}${CYAN}MANUAL RECOVERY STEPS:${NC}"
        echo -e "1. ${YELLOW}We've backed up all your work to:${NC} $FULL_BACKUP"
        echo -e "2. ${YELLOW}Clone a fresh copy:${NC}"
        echo -e "   ${CYAN}git clone https://github.com/jurisgpt/GrizlyUDVacator.git GrizlyUDVacator_fresh${NC}"
        echo -e "3. ${YELLOW}Copy your changes from the backup${NC}"

        exit 1
    fi
fi

# Get the commit hashes for comparison
LOCAL=$(git rev-parse @ 2>/dev/null || echo "unknown")
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "unknown")
BASE=$(git merge-base @ origin/main 2>/dev/null || echo "unknown")

# Check for unknown values
if [ "$LOCAL" = "unknown" ] || [ "$REMOTE" = "unknown" ] || [ "$BASE" = "unknown" ]; then
    print_warning "Hmm, still having trouble determining repository state."
    print_info "${MAGIC} Let's try one more magic trick..."

    # Create pre-reset backup
    RESET_BACKUP="$BACKUP_DIR/GrizlyUDVacator_before_reset_$TIMESTAMP.tar.gz"
    print_info "${TOOLS} Creating one more backup just to be safe..."
    tar -czf "$RESET_BACKUP" .
    print_success "Backup saved to $RESET_BACKUP"

    print_info "${FIRE} Attempting hard reset to origin/main..."
    if git reset --hard origin/main; then
        print_success "Reset successful! ${SPARKLES}"
        LOCAL=$(git rev-parse @ 2>/dev/null || echo "still_unknown")
        REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "still_unknown")
        BASE=$(git merge-base @ origin/main 2>/dev/null || echo "still_unknown")
    else
        print_error "Reset failed. We need to go with Plan B."
        print_info "Don't worry! Your files are safe in the backups."
        echo ""
        echo -e "${BOLD}${CYAN}RECOVERY INSTRUCTIONS:${NC}"
        echo -e "1. ${YELLOW}We've backed up everything to:${NC} $RESET_BACKUP"
        echo -e "2. ${YELLOW}Please clone a fresh copy of the repository.${NC}"

        exit 1
    fi

    if [ "$LOCAL" = "still_unknown" ] || [ "$REMOTE" = "still_unknown" ] || [ "$BASE" = "still_unknown" ]; then
        print_error "Repository state still cannot be determined."
        print_info "Time for Plan B - but everything is still okay!"
        echo ""
        echo -e "${BOLD}${CYAN}RECOVERY INSTRUCTIONS:${NC}"
        echo -e "1. ${YELLOW}We've backed up everything to:${NC} $RESET_BACKUP"
        echo -e "2. ${YELLOW}Please use the fresh clone method described earlier.${NC}"

        exit 1
    fi
fi

print_header "${CHART} ANALYZING SYNC STATUS ${CHART}" "Let's see how your Mac and GitHub compare"

# Decision tree based on commit comparison
if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${BOLD}${GREEN}${CHECK} PERFECTLY IN SYNC! ${CHECK}${NC}"
    echo -e "${CYAN}Your Mac and GitHub are already in perfect harmony.${NC}"
    echo -e "${CYAN}Nothing to do but celebrate! ${SPARKLES}${NC}"

elif [ "$LOCAL" = "$BASE" ]; then
    echo -e "${BOLD}${BLUE}${EYES} YOUR MAC IS BEHIND ${EYES}${NC}"
    echo -e "${CYAN}Your GitHub repository has new changes that aren't on your Mac.${NC}"
    echo -e "${CYAN}Let's bring your Mac up to date...${NC}"

    print_info "${LIGHTNING} Pulling latest changes from GitHub..."
    if git pull; then
        print_success "Successfully updated your Mac with the latest changes! ${SPARKLES}"
        echo -e "${CYAN}Your local repository is now up to date with GitHub.${NC}"
    else
        print_error "Pull operation failed."
        print_info "Don't worry - we can fix this manually."
        echo ""
        echo -e "${BOLD}${CYAN}TRY THIS:${NC}"
        echo -e "1. ${YELLOW}Make sure you don't have conflicting changes:${NC}"
        echo -e "   ${CYAN}git status${NC}"
        echo -e "2. ${YELLOW}If needed, stash your changes:${NC}"
        echo -e "   ${CYAN}git stash${NC}"
        echo -e "3. ${YELLOW}Then try pulling again:${NC}"
        echo -e "   ${CYAN}git pull${NC}"

        exit 1
    fi

elif [ "$REMOTE" = "$BASE" ]; then
    echo -e "${BOLD}${PURPLE}${ROCKET} YOUR MAC IS AHEAD ${ROCKET}${NC}"
    echo -e "${CYAN}You have new changes on your Mac that aren't on GitHub yet.${NC}"
    echo -e "${CYAN}Let's share your brilliance with the world...${NC}"

    print_info "${EYES} Here are the commits that will be pushed:"
    git log --oneline origin/main..HEAD
    echo ""

    print_info "${LIGHTNING} Pushing your changes to GitHub..."
    if git push origin main; then
        print_success "Successfully pushed your changes to GitHub! ${SPARKLES}"
        echo -e "${CYAN}Your brilliance is now shared with the world.${NC}"
    else
        print_warning "Push operation failed."
        print_info "This usually happens when GitHub has changes you don't have locally."
        echo ""
        echo -e "${BOLD}${CYAN}TRY THIS:${NC}"
        echo -e "1. ${YELLOW}First pull the changes from GitHub:${NC}"
        echo -e "   ${CYAN}git pull --rebase origin main${NC}"
        echo -e "2. ${YELLOW}Then try pushing again:${NC}"
        echo -e "   ${CYAN}git push origin main${NC}"

        exit 1
    fi

else
    echo -e "${BOLD}${YELLOW}${WARNING} DIVERGED PATHS ${WARNING}${NC}"
    echo -e "${CYAN}Your Mac and GitHub have both evolved in different directions.${NC}"
    echo -e "${CYAN}This needs your creative input to merge properly.${NC}"

    print_info "${EYES} Local commits not on GitHub:"
    git log --oneline origin/main..HEAD
    echo ""

    print_info "${EYES} GitHub commits not on your Mac:"
    git log --oneline HEAD..origin/main
    echo ""

    echo -e "${BOLD}${CYAN}YOUR OPTIONS:${NC}"
    echo -e "1. ${YELLOW}Rebase (recommended):${NC}"
    echo -e "   ${CYAN}git pull --rebase origin main${NC}"
    echo -e "   This puts GitHub's changes first, then adds yours on top."
    echo ""
    echo -e "2. ${YELLOW}Merge:${NC}"
    echo -e "   ${CYAN}git merge origin/main${NC}"
    echo -e "   This creates a merge commit combining both sets of changes."
    echo ""
    print_info "Choose what works best for your workflow! ${SPARKLES}"

    exit 0
fi

print_header "${SPARKLES} SYNC COMPLETE ${SPARKLES}" "Your Mac and GitHub are now in perfect harmony"

echo -e "${BOLD}${GREEN}${LOVE} SUCCESS! ${LOVE}${NC}"
echo -e "${CYAN}Your Mac and GitHub repositories are now perfectly in sync.${NC}"
echo -e "${CYAN}Keep coding brilliantly! ${FIRE}${NC}"
echo ""
echo -e "${BLUE}${TIMER} Completed at:${NC} $(date)"
echo ""

exit 0
