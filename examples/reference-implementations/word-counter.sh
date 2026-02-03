#!/usr/bin/env bash
# word-counter v1.0.0 (PAS Level 2 Compliant)

set -euo pipefail

AGENT_MODE=false

usage() {
    cat << 'EOF'
Usage: word-counter [OPTIONS] <file...>

Options:
  --agent          Agent-compatible output (JSON Lines)
  --agent --help   Show agent-optimized help
  -h, --help       Show this help

Examples:
  word-counter file.txt
  word-counter --agent file1.txt file2.txt
EOF
}

agent_help() {
    cat << 'EOF'
USAGE:
  word-counter [--agent] <file...>

COMMON PATTERNS:
  word-counter --agent file.txt                    # Count words in one file
  find . -name "*.md" | xargs word-counter --agent # Count all markdown files
  word-counter --agent *.txt | jq -s 'map(.words) | add' # Total word count

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 File not found
  101 File not readable

ANTI-PATTERNS:
  word-counter *.txt > out.txt     # Use --agent for machine-readable output
EOF
}

count_words() {
    local file="$1"

    if [ ! -f "$file" ]; then
        if [ "$AGENT_MODE" = true ]; then
            echo '{"error":"FILE_NOT_FOUND","message":"File not found: '"$file"'","code":100}' >&2
        else
            echo "Error: File not found: $file" >&2
        fi
        exit 100
    fi

    if [ ! -r "$file" ]; then
        if [ "$AGENT_MODE" = true ]; then
            echo '{"error":"FILE_NOT_READABLE","message":"Cannot read file: '"$file"'","code":101}' >&2
        else
            echo "Error: Cannot read file: $file" >&2
        fi
        exit 101
    fi

    local count=$(wc -w < "$file" | tr -d ' ')

    if [ "$AGENT_MODE" = true ]; then
        echo "{\"file\":\"$file\",\"words\":$count}"
    else
        echo "$file: $count words"
    fi
}

# Parse arguments
# First pass: check for --agent flag
for arg in "$@"; do
    if [ "$arg" = "--agent" ]; then
        AGENT_MODE=true
        break
    fi
done

while [ $# -gt 0 ]; do
    case "$1" in
        --agent)
            AGENT_MODE=true
            shift
            ;;
        -h|--help)
            if [ "$AGENT_MODE" = true ]; then
                agent_help
            else
                usage
            fi
            exit 0
            ;;
        -*)
            if [ "$AGENT_MODE" = true ]; then
                echo '{"error":"INVALID_ARGUMENT","message":"Unknown option: '"$1"'","suggestion":"See --agent --help"}' >&2
            else
                echo "Error: Unknown option: $1" >&2
                usage >&2
            fi
            exit 2
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -eq 0 ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo '{"error":"MISSING_ARGUMENT","message":"No files specified","suggestion":"Provide at least one file path"}' >&2
    else
        echo "Error: No files specified" >&2
        usage >&2
    fi
    exit 2
fi

# Process each file
for file in "$@"; do
    count_words "$file"
done
