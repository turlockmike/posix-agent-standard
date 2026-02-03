# PAS Implementation Examples

## Complete Reference Implementation: Word Counter

This is a complete Level 2 compliant tool that demonstrates all key patterns:

```bash
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
```

## Python API Client Example

Level 2 compliant tool that wraps an API:

```python
#!/usr/bin/env python3
"""
weather-cli v1.0.0 (PAS Level 2 Compliant)
"""

import json
import sys
import requests
from typing import Dict, Any

def usage():
    print("""Usage: weather-cli [OPTIONS] <city>

Options:
  --agent          Agent-compatible output (JSON)
  --agent --help   Show agent-optimized help
  -h, --help       Show this help

Examples:
  weather-cli Boston
  weather-cli --agent "San Francisco"
""")

def agent_help():
    print("""USAGE:
  weather-cli [--agent] <city>

COMMON PATTERNS:
  weather-cli --agent Boston                        # Get weather as JSON
  weather-cli --agent Boston | jq -r '.temperature' # Extract temperature

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 City not found
  103 Request timeout
  104 Network error
""")

def get_weather(city: str, agent_mode: bool = False) -> Dict[str, Any]:
    """Fetch weather data for a city."""
    try:
        # Example API call (replace with real API)
        response = requests.get(
            f"https://api.weather.example.com/current?city={city}",
            timeout=10
        )

        if response.status_code == 404:
            error = {
                "error": "CITY_NOT_FOUND",
                "message": f"City not found: {city}",
                "code": 100
            }
            if agent_mode:
                print(json.dumps(error), file=sys.stderr)
            else:
                print(f"Error: City not found: {city}", file=sys.stderr)
            sys.exit(100)

        response.raise_for_status()
        data = response.json()

        return {
            "city": city,
            "temperature": data.get("temp"),
            "condition": data.get("condition"),
            "humidity": data.get("humidity")
        }

    except requests.Timeout:
        error = {
            "error": "TIMEOUT",
            "message": "Request timed out",
            "code": 103
        }
        if agent_mode:
            print(json.dumps(error), file=sys.stderr)
        else:
            print("Error: Request timed out", file=sys.stderr)
        sys.exit(103)

    except requests.RequestException as e:
        error = {
            "error": "NETWORK_ERROR",
            "message": str(e),
            "code": 104
        }
        if agent_mode:
            print(json.dumps(error), file=sys.stderr)
        else:
            print(f"Error: Network error: {e}", file=sys.stderr)
        sys.exit(104)

def main():
    agent_mode = '--agent' in sys.argv

    # Remove --agent from args for easier processing
    args = [arg for arg in sys.argv[1:] if arg != '--agent']

    # Handle help
    if '-h' in args or '--help' in args:
        if agent_mode:
            agent_help()
        else:
            usage()
        sys.exit(0)

    # Validate arguments
    if len(args) == 0:
        if agent_mode:
            error = {
                "error": "MISSING_ARGUMENT",
                "message": "No city specified",
                "suggestion": "Provide a city name"
            }
            print(json.dumps(error), file=sys.stderr)
        else:
            print("Error: No city specified", file=sys.stderr)
            usage()
        sys.exit(2)

    city = args[0]

    # Get weather
    result = get_weather(city, agent_mode)

    # Output
    if agent_mode:
        print(json.dumps(result))
    else:
        print(f"{result['city']}: {result['temperature']}°F, {result['condition']}")
        print(f"Humidity: {result['humidity']}%")

if __name__ == "__main__":
    main()
```

## Minimal 10-Line Example

The simplest possible PAS Level 1 tool:

```bash
#!/bin/bash
# hello.sh - PAS Level 1 compliant

if [ "$1" = "--agent" ]; then
    echo '{"message":"Hello, '"${2:-World}"'!"}'
else
    echo "Hello, ${2:-World}!"
fi
```

Usage:
```bash
$ ./hello.sh Alice
Hello, Alice!

$ ./hello.sh --agent Alice
{"message":"Hello, Alice!"}
```

## Level 3: Navigation Example

Tool that browses a remote API with Unix-like commands:

```bash
#!/usr/bin/env bash
# github-browser - PAS Level 3 compliant

set -euo pipefail

AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true && shift

COMMAND="${1:-ls}"
PATH_ARG="${2:-.}"

case "$COMMAND" in
    ls)
        # List resources
        if [ "$AGENT_MODE" = true ]; then
            gh api "/repos/owner/repo/issues" | jq -c '.[]'
        else
            gh issue list
        fi
        ;;
    cat)
        # Read resource
        ISSUE_NUM=$(basename "$PATH_ARG")
        if [ "$AGENT_MODE" = true ]; then
            gh api "/repos/owner/repo/issues/$ISSUE_NUM"
        else
            gh issue view "$ISSUE_NUM"
        fi
        ;;
    stat)
        # Get metadata
        ISSUE_NUM=$(basename "$PATH_ARG")
        if [ "$AGENT_MODE" = true ]; then
            gh api "/repos/owner/repo/issues/$ISSUE_NUM" | \
                jq '{path: .html_url, type: "issue", size: (.body | length), modified: .updated_at}'
        else
            gh issue view "$ISSUE_NUM" --json updatedAt,body
        fi
        ;;
esac
```

## Composability Examples

### Example 1: Pipeline Processing
```bash
# Find all inactive users and send them emails
users-cli list --agent --status inactive \
  | jq -r '.email' \
  | xargs -I {} email-cli send --agent \
      --to {} \
      --subject "Account activity notice" \
      --template inactive.txt
```

### Example 2: Aggregation
```bash
# Total word count across all markdown files
find . -name "*.md" \
  | xargs word-counter --agent \
  | jq -s 'map(.words) | add'
```

### Example 3: Filtering and Formatting
```bash
# Get high-severity security issues and format for Slack
security-scan --agent . \
  | jq -c 'select(.severity == "high")' \
  | while read issue; do
      gh issue create \
        --title "Security: $(echo $issue | jq -r .title)" \
        --body "$(echo $issue | jq -r .description)"
    done
```

## Testing Examples

### Test Suite for PAS Compliance

```bash
#!/usr/bin/env bash
# test-pas-compliance.sh

TOOL="./mytool"
PASSED=0
FAILED=0

test_json_output() {
    echo "Test: JSON output validity"
    if $TOOL --agent test.txt | jq . > /dev/null 2>&1; then
        echo "✓ PASSED"
        ((PASSED++))
    else
        echo "✗ FAILED: Invalid JSON"
        ((FAILED++))
    fi
}

test_error_to_stderr() {
    echo "Test: Errors go to stderr"
    output=$($TOOL --agent nonexistent.txt 2>&1 >/dev/null)
    if echo "$output" | jq . > /dev/null 2>&1; then
        echo "✓ PASSED"
        ((PASSED++))
    else
        echo "✗ FAILED: Error not JSON or not to stderr"
        ((FAILED++))
    fi
}

test_exit_codes() {
    echo "Test: Semantic exit codes"
    $TOOL --agent nonexistent.txt > /dev/null 2>&1
    code=$?
    if [ $code -ge 100 ] && [ $code -le 125 ]; then
        echo "✓ PASSED (exit code: $code)"
        ((PASSED++))
    else
        echo "✗ FAILED: Exit code $code not in semantic range (100-125)"
        ((FAILED++))
    fi
}

test_json_lines() {
    echo "Test: JSON Lines format"
    line_count=$($TOOL --agent list | wc -l)
    valid_count=$($TOOL --agent list | jq -c . 2>/dev/null | wc -l)
    if [ "$line_count" -eq "$valid_count" ]; then
        echo "✓ PASSED"
        ((PASSED++))
    else
        echo "✗ FAILED: Not all lines are valid JSON"
        ((FAILED++))
    fi
}

test_no_decorations() {
    echo "Test: No ANSI codes in agent mode"
    if $TOOL --agent test.txt | grep -q $'\033'; then
        echo "✗ FAILED: ANSI codes detected"
        ((FAILED++))
    else
        echo "✓ PASSED"
        ((PASSED++))
    fi
}

# Run tests
test_json_output
test_error_to_stderr
test_exit_codes
test_json_lines
test_no_decorations

echo ""
echo "Results: $PASSED passed, $FAILED failed"
[ $FAILED -eq 0 ] && exit 0 || exit 1
```

## Anti-Pattern Examples

### ❌ BAD: Mixed Output
```bash
# Don't do this
echo "Processing file..."  # Human text
echo '{"result": "done"}'  # JSON
```

### ✅ GOOD: Clean Output
```bash
# Do this
[ "$AGENT_MODE" = false ] && echo "Processing file..." >&2
echo '{"result": "done"}'
```

### ❌ BAD: JSON Array for Large List
```bash
# Don't do this
echo "["
for item in "${items[@]}"; do
    echo "  {\"id\": $item},"
done
echo "]"
```

### ✅ GOOD: JSON Lines
```bash
# Do this
for item in "${items[@]}"; do
    echo "{\"id\": $item}"
done
```

### ❌ BAD: Generic Errors
```bash
# Don't do this
echo '{"error": "something failed"}' >&2
exit 1
```

### ✅ GOOD: Specific Errors
```bash
# Do this
echo '{"error":"FILE_NOT_FOUND","message":"Config file missing","code":100}' >&2
exit 100
```

## Real-World Use Cases

### Use Case 1: CI/CD Pipeline
```bash
#!/bin/bash
# deploy-pipeline.sh

set -e

# Validate
validate-config --agent config.yml || exit 1

# Build
build-tool --agent --env production > build-result.json

# Test
test-runner --agent \
  | jq -c 'select(.status == "failed")' \
  | while read failure; do
      echo "Test failed: $(echo $failure | jq -r .name)"
      exit 1
  done

# Deploy
deploy-tool --agent --target production < build-result.json
```

### Use Case 2: Data Analysis
```bash
# Analyze API usage across services
for service in api-gateway auth-service user-service; do
    metrics-tool --agent --service $service --range 24h
done | jq -s 'group_by(.status) | map({status: .[0].status, count: length})'
```

### Use Case 3: Monitoring Alert
```bash
# Check system health and alert on issues
system-check --agent \
  | jq -c 'select(.status == "critical")' \
  | while read alert; do
      slack-cli post --agent \
        --channel ops \
        --text "Critical: $(echo $alert | jq -r .message)"
    done
```
