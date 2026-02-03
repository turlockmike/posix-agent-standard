#!/usr/bin/env bash
# PAS Template Script (Level 2 Compliant)
# Copy this template and customize for your tool

set -euo pipefail

AGENT_MODE=false

usage() {
    cat << 'EOF'
Usage: mytool [OPTIONS] <args>

Options:
  --agent          Agent-compatible output (JSON)
  --agent --help   Show agent-optimized help
  -h, --help       Show this help

Examples:
  mytool input.txt
  mytool --agent input.txt
EOF
}

agent_help() {
    cat << 'EOF'
USAGE:
  mytool [--agent] <args>

COMMON PATTERNS:
  mytool --agent file.txt              # Process file
  mytool --agent file.txt | jq '.result' # Extract result

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 Resource not found
  101 Permission denied
EOF
}

do_work() {
    local input="$1"

    # Your tool's actual logic here
    # Return results that will be formatted based on AGENT_MODE

    echo "result from $input"
}

# Parse arguments - First pass: check for --agent flag
for arg in "$@"; do
    if [ "$arg" = "--agent" ]; then
        AGENT_MODE=true
        break
    fi
done

# Second pass: handle all arguments
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

# Validate required arguments
if [ $# -eq 0 ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo '{"error":"MISSING_ARGUMENT","message":"No input specified","suggestion":"Provide required arguments"}' >&2
    else
        echo "Error: No input specified" >&2
        usage >&2
    fi
    exit 2
fi

# Main logic
INPUT="$1"

# Check if input exists (example validation)
if [ ! -e "$INPUT" ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo '{"error":"NOT_FOUND","message":"Input not found: '"$INPUT"'","code":100}' >&2
    else
        echo "Error: Input not found: $INPUT" >&2
    fi
    exit 100
fi

# Do the actual work
result=$(do_work "$INPUT")

# Output based on mode
if [ "$AGENT_MODE" = true ]; then
    echo "{\"status\":\"success\",\"result\":\"$result\"}"
else
    echo "Success: $result"
fi
