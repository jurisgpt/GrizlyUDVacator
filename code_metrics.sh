#!/bin/bash

# Enhanced Code Metrics Tool
# Usage: ./code_metrics.sh [directory_path] [options]
# If no directory path is provided, the current directory is used
# Options:
#   -a, --all       Run all metrics (default)
#   -b, --basic     Run only basic metrics (lines, files, dirs)
#   -c, --commits   Include git commit statistics
#   -e, --empty     Count empty lines and comment lines
#   -s, --size      Include file size analysis
#   -a, --age       Include file age analysis (requires git)
#   -h, --help      Show this help message

# Default options
RUN_ALL=true
RUN_BASIC=true
RUN_COMMITS=false
RUN_EMPTY_COMMENTS=false
RUN_SIZE=false
RUN_AGE=false

# Process command line arguments
TARGET_DIR="."
for arg in "$@"; do
    if [[ "$arg" == -* ]]; then
        # This is an option
        case "$arg" in
            -a|--all)
                RUN_ALL=true
                RUN_COMMITS=true
                RUN_EMPTY_COMMENTS=true
                RUN_SIZE=true
                RUN_AGE=true
                ;;
            -b|--basic)
                RUN_ALL=false
                RUN_BASIC=true
                ;;
            -c|--commits)
                RUN_ALL=false
                RUN_COMMITS=true
                ;;
            -e|--empty)
                RUN_ALL=false
                RUN_EMPTY_COMMENTS=true
                ;;
            -s|--size)
                RUN_ALL=false
                RUN_SIZE=true
                ;;
            -a|--age)
                RUN_ALL=false
                RUN_AGE=true
                ;;
            -h|--help)
                echo "Usage: ./code_metrics.sh [directory_path] [options]"
                echo "Options:"
                echo "  -a, --all       Run all metrics (default)"
                echo "  -b, --basic     Run only basic metrics (lines, files, dirs)"
                echo "  -c, --commits   Include git commit statistics"
                echo "  -e, --empty     Count empty lines and comment lines"
                echo "  -s, --size      Include file size analysis"
                echo "  -a, --age       Include file age analysis (requires git)"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $arg"
                exit 1
                ;;
        esac
    else
        # This is the directory path
        TARGET_DIR="$arg"
    fi
done

# Check if the directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

echo "====== Code Analysis for: $TARGET_DIR ======"

# Define common code file extensions
CODE_EXTENSIONS=("\.py" "\.java" "\.js" "\.html" "\.css" "\.c" "\.cpp" "\.h" "\.hpp"
                "\.sh" "\.bash" "\.php" "\.rb" "\.pl" "\.swift" "\.go" "\.ts" "\.jsx"
                "\.tsx" "\.scala" "\.kt" "\.rs" "\.m" "\.mm" "\.sql" "\.r")

# Combine extensions for grep pattern
pattern=$(printf "|%s" "${CODE_EXTENSIONS[@]}")
pattern=${pattern:1}  # Remove the first |

# Basic metrics: files, directories, lines of code
if [ "$RUN_BASIC" = true ] || [ "$RUN_ALL" = true ]; then
    echo -e "\n=== Basic Metrics ==="

    # Count total number of files (excluding hidden files)
    total_files=$(find "$TARGET_DIR" -type f -not -path "*/\.*" | wc -l)
    echo "Total Files: $total_files"

    # Count total number of directories (excluding hidden directories)
    total_dirs=$(find "$TARGET_DIR" -type d -not -path "*/\.*" | wc -l)
    # Subtract 1 to exclude the target directory itself
    total_dirs=$((total_dirs - 1))
    echo "Total Directories: $total_dirs"

    # Count lines of code in all code files
    echo -e "\n=== Lines of Code Analysis ==="
    total_loc=0

    for ext in "${CODE_EXTENSIONS[@]}"; do
        # Remove the backslash before the dot
        ext_clean=${ext//\\/}

        # Count lines for this extension
        loc=$(find "$TARGET_DIR" -type f -name "*$ext_clean" -not -path "*/\.*" -exec wc -l {} \; | awk '{sum+=$1} END {print sum}')

        # If there are files with this extension
        if [ "$loc" -gt 0 ]; then
            # Count number of files with this extension
            file_count=$(find "$TARGET_DIR" -type f -name "*$ext_clean" -not -path "*/\.*" | wc -l)

            echo "$ext_clean files: $file_count files, $loc lines"
            total_loc=$((total_loc + loc))
        fi
    done

    echo -e "\nTotal Lines of Code: $total_loc"

    # Optional: Add detailed analysis by folder
    echo -e "\n=== Top 5 Largest Directories (by file count) ==="
    find "$TARGET_DIR" -type d -not -path "*/\.*" | while read dir; do
        file_count=$(find "$dir" -maxdepth 1 -type f -not -path "*/\.*" | wc -l)
        echo "$file_count $dir"
    done | sort -nr | head -5
fi

# Empty lines and comment lines analysis
if [ "$RUN_EMPTY_COMMENTS" = true ] || [ "$RUN_ALL" = true ]; then
    echo -e "\n=== Empty Lines & Comments Analysis ==="

    # Define comment markers for different languages
    declare -A COMMENT_MARKERS
    COMMENT_MARKERS[".py"]="#"
    COMMENT_MARKERS[".js"]="//"
    COMMENT_MARKERS[".java"]="//"
    COMMENT_MARKERS[".c"]="//"
    COMMENT_MARKERS[".cpp"]="//"
    COMMENT_MARKERS[".sh"]="#"
    COMMENT_MARKERS[".php"]="//"

    total_empty=0
    total_comment=0

    for ext_key in "${!COMMENT_MARKERS[@]}"; do
        marker="${COMMENT_MARKERS[$ext_key]}"
        empty_lines=0
        comment_lines=0

        # Find all files with this extension
        while IFS= read -r file; do
            # Count empty lines
            empty_in_file=$(grep -c "^[[:space:]]*$" "$file")
            empty_lines=$((empty_lines + empty_in_file))

            # Count comment lines
            if [ -n "$marker" ]; then
                comment_in_file=$(grep -c "^[[:space:]]*$marker" "$file")
                comment_lines=$((comment_lines + comment_in_file))
            fi
        done < <(find "$TARGET_DIR" -type f -name "*$ext_key" -not -path "*/\.*")

        # Only show if we found files with this extension
        if [ $empty_lines -gt 0 ] || [ $comment_lines -gt 0 ]; then
            echo "$ext_key files: $empty_lines empty lines, $comment_lines comment lines"
            total_empty=$((total_empty + empty_lines))
            total_comment=$((total_comment + comment_lines))
        fi
    done

    echo -e "\nTotal Empty Lines: $total_empty"
    echo "Total Comment Lines: $total_comment"

    # Calculate code to comment ratio if we have comments
    if [ $total_comment -gt 0 ] && [ $total_loc -gt 0 ]; then
        code_lines=$((total_loc - total_empty - total_comment))
        ratio=$(awk "BEGIN {printf \"%.2f\", $code_lines / $total_comment}")
        echo "Code to Comment Ratio: $ratio:1"
    fi
fi

# File size analysis
if [ "$RUN_SIZE" = true ] || [ "$RUN_ALL" = true ]; then
    echo -e "\n=== File Size Analysis ==="

    # Calculate total size of code files
    total_size=0
    for ext in "${CODE_EXTENSIONS[@]}"; do
        ext_clean=${ext//\\/}
        size=$(find "$TARGET_DIR" -type f -name "*$ext_clean" -not -path "*/\.*" -exec du -b {} \; | awk '{sum+=$1} END {print sum}')

        if [ "$size" -gt 0 ]; then
            # Convert bytes to human-readable form
            if [ $size -ge 1048576 ]; then
                size_hr=$(echo "scale=2; $size/1048576" | bc)
                echo "$ext_clean files: ${size_hr}MB"
            elif [ $size -ge 1024 ]; then
                size_hr=$(echo "scale=2; $size/1024" | bc)
                echo "$ext_clean files: ${size_hr}KB"
            else
                echo "$ext_clean files: ${size}B"
            fi

            total_size=$((total_size + size))
        fi
    done

    # Display total size in human-readable form
    if [ $total_size -ge 1048576 ]; then
        total_size_hr=$(echo "scale=2; $total_size/1048576" | bc)
        echo -e "\nTotal Code Size: ${total_size_hr}MB"
    elif [ $total_size -ge 1024 ]; then
        total_size_hr=$(echo "scale=2; $total_size/1024" | bc)
        echo -e "\nTotal Code Size: ${total_size_hr}KB"
    else
        echo -e "\nTotal Code Size: ${total_size}B"
    fi

    # Find largest files
    echo -e "\n=== Top 5 Largest Files ==="
    find "$TARGET_DIR" -type f -not -path "*/\.*" -exec du -h {} \; | sort -rh | head -n 5
fi

# Git commit stats (if it's a git repository)
if ( [ "$RUN_COMMITS" = true ] || [ "$RUN_ALL" = true ] ) && [ -d "$TARGET_DIR/.git" ]; then
    echo -e "\n=== Git Commit Statistics ==="

    # Change to the target directory
    cd "$TARGET_DIR"

    # Total number of commits
    commit_count=$(git rev-list --count HEAD)
    echo "Total Commits: $commit_count"

    # Get commit dates to calculate project age
    first_commit_date=$(git log --reverse --format=%cd --date=short | head -1)
    last_commit_date=$(git log -1 --format=%cd --date=short)
    echo "Project Timespan: $first_commit_date to $last_commit_date"

    # Get contributors count
    contributor_count=$(git shortlog -sn | wc -l)
    echo "Total Contributors: $contributor_count"

    # Top 3 contributors
    echo -e "\n=== Top 3 Contributors ==="
    git shortlog -sn | head -3

    # Commits by month (last 6 months)
    echo -e "\n=== Commit Activity (Last 6 Months) ==="
    git log --date=format:%Y-%m --format="%ad" --since="6 months ago" | sort | uniq -c

    # Files with most changes
    echo -e "\n=== Top 5 Most Changed Files ==="
    git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -5
fi

# File age analysis (if it's a git repository)
if ( [ "$RUN_AGE" = true ] || [ "$RUN_ALL" = true ] ) && [ -d "$TARGET_DIR/.git" ]; then
    echo -e "\n=== File Age Analysis ==="

    # Change to the target directory if not already there
    cd "$TARGET_DIR"

    # Get the newest files
    echo "Newest Files (last modified):"
    git ls-files | xargs -I{} git log -1 --format="%ad %h {}" --date=short -- {} | sort -r | head -5

    # Get the oldest files
    echo -e "\nOldest Files (first created):"
    git ls-files | xargs -I{} git log --reverse --format="%ad %h {}" --date=short -- {} | head -5 | sort

    # Average file age
    echo -e "\nFiles by Age:"
    current_year=$(date +%Y)
    current_month=$(date +%m)

    echo "Files created this month: $(git log --since=$(date +%Y-%m-01) --name-only --pretty=format: | sort -u | wc -l)"
    echo "Files created this year: $(git log --since=$(date +%Y-01-01) --name-only --pretty=format: | sort -u | wc -l)"
    echo "Files older than 1 year: $(git log --until=$(date -v-1y +%Y-%m-%d) --name-only --pretty=format: | sort -u | wc -l)"
fi

echo -e "\n====== Analysis Complete ======"
