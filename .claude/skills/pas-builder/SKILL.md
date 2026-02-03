---
name: pas-builder
description: Use when building CLI tools that need to work with AI agents, adding --agent flags to tools, making tools agent-compatible, or implementing POSIX Agent Standard (PAS) compliance. Use when the user wants machine-readable output from CLI tools or asks about JSON output for automation. CRITICAL - Use when building scripts for skills - instead of multiple individual scripts, build one PAS-compliant CLI with subcommands for easier maintenance, testing, and composability.
---

# PAS Builder: POSIX Agent Standard Compliance

## Core Principle

**LLMs already know Unix.** Instead of building custom MCP servers or API wrappers, make CLI tools agent-friendly by adding an `--agent` flag that outputs structured JSON.

## The Three Rules

### Rule 1: Add --agent Flag
```bash
$ mytool --agent input.txt
{"result": "success", "data": {...}}
```

**Guarantees when --agent is active:**
- Non-interactive (never waits for user input)
- Structured output (JSON or JSON Lines to stdout)
- Structured errors (JSON to stderr)
- No decorations (no spinners, colors, progress bars, or ANSI codes)

### Rule 2: Use JSON Lines for Lists
```bash
# NOT a JSON array [...] which requires closing bracket
# Instead, one JSON object per line:

$ users list --agent
{"id":1,"name":"Alice","status":"active"}
{"id":2,"name":"Bob","status":"active"}
{"id":3,"name":"Charlie","status":"inactive"}
```

**Why JSON Lines?**
- Enables streaming (don't need to wait for completion)
- Works with pipes and `jq` line-by-line
- Processing starts immediately, not after entire array loads

### Rule 3: Document Concisely
```bash
$ mytool --agent --help

USAGE:
  mytool [--agent] <input>

COMMON PATTERNS:
  mytool --agent file.txt              # Process file
  mytool --agent --format json file.txt # JSON output

ERROR CODES:
  0   Success
  1   General error
  100 File not found
```

**Why concise?** Agents don't need verbose help. They need the 5 most common patterns and semantic error codes.

## Quick Implementation (5 Minutes)

### Bash Template
```bash
#!/usr/bin/env bash
set -euo pipefail

AGENT_MODE=false

# Parse --agent flag
for arg in "$@"; do
    if [ "$arg" = "--agent" ]; then
        AGENT_MODE=true
        break
    fi
done

# Do work
result=$(do_your_work "$@")

# Output based on mode
if [ "$AGENT_MODE" = true ]; then
    echo "{\"result\":\"$result\"}"  # Machine-readable
else
    echo "Success: $result"          # Human-readable
fi
```

### Python Template
```python
#!/usr/bin/env python3
import json
import sys

def main():
    agent_mode = '--agent' in sys.argv

    try:
        result = do_work()

        if agent_mode:
            print(json.dumps(result))  # Machine-readable
        else:
            print(f"Success: {result['message']}")  # Human-readable

    except Exception as e:
        if agent_mode:
            error = {"error": "WORK_FAILED", "message": str(e)}
            print(json.dumps(error), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Conformance Levels

### Level 1: Agent-Safe (Minimum)
- Has `--agent` flag
- Non-interactive execution
- Structured errors

**Good enough for:** Quick additions, prototypes, wrappers

### Level 2: Agent-Optimized (Recommended)
- Level 1 requirements, plus:
- JSON Lines output for lists
- Semantic exit codes (0, 1, 2, 100-125)
- Concise `--agent --help`

**Good enough for:** Production tools, frequently-used CLIs

### Level 3: Navigation (Optional)
- Level 2 requirements, plus:
- Unix-style verbs for remote resources: `ls`, `cat`, `stat`
- Hierarchical paths (e.g., `/users/123/orders`)

**Use when:** Building read-only interfaces to external data (APIs, databases, cloud storage)

### Level 4: State (Advanced)
- Level 3 requirements, plus:
- State verbs: `cp` (write), `rm` (delete), `sync`, `mount`

**Use when:** Building full read/write interfaces with synchronization

## Implementation Checklist

When implementing PAS compliance, follow this order:

### 1. Add Basic --agent Flag
```bash
# Bash
AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true

# Python
agent_mode = '--agent' in sys.argv
```

### 2. Implement JSON Output
```bash
# Success output (stdout)
if [ "$AGENT_MODE" = true ]; then
    echo '{"status":"success","data":'"$result"'}'
else
    echo "Success: $result"
fi
```

### 3. Implement JSON Errors
```bash
# Error output (stderr)
if [ "$AGENT_MODE" = true ]; then
    echo '{"error":"FILE_NOT_FOUND","message":"File missing","code":100}' >&2
else
    echo "Error: File not found" >&2
fi
exit 100
```

### 4. Use JSON Lines for Lists
```bash
# For each item in a list
for item in "${items[@]}"; do
    if [ "$AGENT_MODE" = true ]; then
        echo "{\"id\":$id,\"name\":\"$name\"}"  # One JSON per line
    else
        echo "$id: $name"  # Human table format
    fi
done
```

### 5. Add Semantic Exit Codes
```bash
# 0   = Success
# 1   = General error
# 2   = Invalid usage (bad flags/arguments)
# 100-125 = Tool-specific errors

exit 100  # FILE_NOT_FOUND
exit 101  # FILE_NOT_READABLE
exit 102  # INVALID_FORMAT
```

### 6. Create Agent Help
```bash
agent_help() {
    cat << 'EOF'
USAGE:
  mytool [--agent] <input>

COMMON PATTERNS:
  mytool --agent file.txt
  mytool --agent *.txt | jq -s 'map(.count) | add'

ERROR CODES:
  0   Success
  1   General error
  100 File not found
EOF
}
```

## Common Patterns

### Pattern: Flag-First Design
```bash
# Parse --agent FIRST before other flags
AGENT_MODE=false
for arg in "$@"; do
    if [ "$arg" = "--agent" ]; then
        AGENT_MODE=true
        break
    fi
done

# Then parse rest of arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --agent) AGENT_MODE=true; shift ;;
        -h|--help)
            [ "$AGENT_MODE" = true ] && agent_help || usage
            exit 0
            ;;
        *) break ;;
    esac
done
```

### Pattern: Streaming Results
```bash
# Process and output immediately, don't buffer
find . -name "*.txt" | while read -r file; do
    count=$(wc -w < "$file")
    if [ "$AGENT_MODE" = true ]; then
        echo "{\"file\":\"$file\",\"words\":$count}"  # Immediate JSON Line
    else
        echo "$file: $count words"
    fi
done
```

### Pattern: Error Context
```bash
# Include helpful context in errors
if [ ! -f "$file" ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo "{\"error\":\"FILE_NOT_FOUND\",\"message\":\"File not found: $file\",\"suggestion\":\"Check path and permissions\",\"code\":100}" >&2
    else
        echo "Error: File not found: $file" >&2
        echo "Tip: Check the file path and permissions" >&2
    fi
    exit 100
fi
```

## Testing Your Implementation

### Test 1: Basic Operation
```bash
# Should output JSON
./mytool --agent test.txt
# Expected: {"result": ...}

# Should be valid JSON
./mytool --agent test.txt | jq .
# Expected: No jq errors
```

### Test 2: Error Handling
```bash
# Should output JSON error to stderr
./mytool --agent nonexistent.txt 2>&1 >/dev/null | jq .
# Expected: {"error": "...", "code": 100}

# Check exit code
./mytool --agent nonexistent.txt
echo $?
# Expected: 100 (not 0 or 1)
```

### Test 3: List Output (JSON Lines)
```bash
# Should output one JSON per line
./mytool --agent list | head -1 | jq .
# Expected: Valid JSON object

# Should be pipeable
./mytool --agent list | jq -r '.name'
# Expected: Names extracted line by line
```

### Test 4: Human Mode Still Works
```bash
# Without --agent, should be human-readable
./mytool test.txt
# Expected: Formatted output, not JSON
```

### Test 5: Help Text
```bash
# Agent help should be concise
./mytool --agent --help
# Expected: USAGE, COMMON PATTERNS, ERROR CODES (not verbose docs)

# Human help can be verbose
./mytool --help
# Expected: Full documentation
```

## Anti-Patterns to Avoid

❌ **Don't output mixed formats**
```bash
# BAD: Mixing human text with JSON
echo "Processing..."  # Human text
echo '{"result": "done"}'  # JSON

# GOOD: Only JSON in agent mode
[ "$AGENT_MODE" = false ] && echo "Processing..."
echo '{"result": "done"}'
```

❌ **Don't use JSON arrays for large lists**
```bash
# BAD: Requires waiting for closing bracket
echo "["
echo '{"id":1},'
echo '{"id":2}'
echo "]"

# GOOD: JSON Lines - streamable
echo '{"id":1}'
echo '{"id":2}'
```

❌ **Don't swallow errors in agent mode**
```bash
# BAD: Silent failure
result=$(risky_operation) || echo "{}"

# GOOD: Explicit error
if ! result=$(risky_operation); then
    echo '{"error":"OPERATION_FAILED"}' >&2
    exit 1
fi
```

❌ **Don't forget stderr for errors**
```bash
# BAD: Errors to stdout
echo '{"error":"failed"}'

# GOOD: Errors to stderr
echo '{"error":"failed"}' >&2
```

❌ **Don't use generic exit codes**
```bash
# BAD: Everything exits with 1
exit 1  # What kind of error?

# GOOD: Semantic codes
exit 100  # FILE_NOT_FOUND
exit 101  # PERMISSION_DENIED
exit 102  # INVALID_FORMAT
```

## Building PAS CLIs for Skills

**IMPORTANT:** When creating scripts for skills, build ONE PAS-compliant CLI instead of multiple individual scripts.

### The Problem: Script Proliferation

❌ **Bad approach - Multiple scripts:**
```
skills/
  my-skill/
    scripts/
      rotate_pdf.py
      merge_pdf.py
      split_pdf.py
      extract_text.py
      add_watermark.py
```

**Issues:**
- 5 separate scripts to maintain
- Duplicated argument parsing logic
- Inconsistent error handling
- No composability
- Hard to test comprehensively

### The Solution: Single PAS CLI

✅ **Good approach - One PAS-compliant CLI:**
```
skills/
  my-skill/
    scripts/
      pdf-tool         # Single CLI with subcommands
```

**Usage:**
```bash
pdf-tool --agent rotate input.pdf --degrees 90
pdf-tool --agent merge file1.pdf file2.pdf
pdf-tool --agent split input.pdf --pages 1-10
pdf-tool --agent extract input.pdf
pdf-tool --agent watermark input.pdf --text "DRAFT"
```

**Benefits:**
- ✅ One tool to maintain
- ✅ Consistent interface and error handling
- ✅ Composable via pipes
- ✅ Single test suite
- ✅ Self-documenting via `--agent --help`
- ✅ Can be used outside the skill

### Pattern: CLI with Subcommands

```bash
#!/usr/bin/env bash
# pdf-tool - PAS Level 2 compliant

set -euo pipefail

AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true && shift

COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    rotate)
        # Rotate PDF
        input="$1"
        degrees="${2:-90}"
        # ... implementation
        if [ "$AGENT_MODE" = true ]; then
            echo "{\"status\":\"success\",\"output\":\"${input%.pdf}_rotated.pdf\"}"
        else
            echo "Rotated $input by $degrees degrees"
        fi
        ;;

    merge)
        # Merge PDFs
        output="merged.pdf"
        # ... implementation
        if [ "$AGENT_MODE" = true ]; then
            echo "{\"status\":\"success\",\"output\":\"$output\",\"inputs\":$(printf '%s\n' "$@" | jq -R . | jq -s .)}"
        else
            echo "Merged ${#@} files into $output"
        fi
        ;;

    split)
        # Split PDF
        # ... implementation
        ;;

    extract)
        # Extract text
        # ... implementation
        ;;

    help)
        if [ "$AGENT_MODE" = true ]; then
            cat << 'EOF'
USAGE:
  pdf-tool [--agent] <command> [args]

COMMANDS:
  rotate <file> [degrees]           Rotate PDF (default: 90)
  merge <file1> <file2> [...]       Merge multiple PDFs
  split <file> --pages <range>      Split PDF by page range
  extract <file>                    Extract text from PDF
  watermark <file> --text <text>    Add watermark

COMMON PATTERNS:
  pdf-tool --agent rotate doc.pdf 180
  pdf-tool --agent merge *.pdf
  find . -name "*.pdf" | xargs -I {} pdf-tool --agent extract {}

ERROR CODES:
  0   Success
  1   General error
  100 File not found
  102 Invalid PDF format
EOF
        else
            echo "Usage: pdf-tool [--agent] <command> [args]"
            echo "Commands: rotate, merge, split, extract, watermark"
            echo "Use 'pdf-tool --agent help' for detailed help"
        fi
        ;;

    *)
        if [ "$AGENT_MODE" = true ]; then
            echo "{\"error\":\"UNKNOWN_COMMAND\",\"message\":\"Unknown command: $COMMAND\",\"suggestion\":\"See --agent help\"}" >&2
        else
            echo "Error: Unknown command: $COMMAND" >&2
        fi
        exit 2
        ;;
esac
```

### Using PAS CLIs in Skills

**In SKILL.md, reference the tool concisely:**

```markdown
# PDF Processing Skill

## Overview
Process PDFs using the pdf-tool CLI.

## Common Operations

**Rotate PDF:**
```bash
pdf-tool --agent rotate document.pdf --degrees 90
```

**Merge PDFs:**
```bash
pdf-tool --agent merge file1.pdf file2.pdf
```

**Extract text:**
```bash
pdf-tool --agent extract document.pdf | jq -r '.text'
```

## Batch Processing

Process all PDFs in a directory:
```bash
find . -name "*.pdf" | while read -r file; do
    pdf-tool --agent extract "$file"
done | jq -s 'map({file: .file, text: .text})'
```
```

**The skill documents the workflow. The PAS CLI handles the operations.**

### Maintenance Benefits

**When you need to update the tool:**

❌ **Multiple scripts:** Update 5 different files, test each separately

✅ **Single PAS CLI:** Update one file, test once, all subcommands benefit

**When you need to add error handling:**

❌ **Multiple scripts:** Add to each script individually

✅ **Single PAS CLI:** Add once in the main error handler

**When you discover a bug:**

❌ **Multiple scripts:** Check all 5 scripts for the same issue

✅ **Single PAS CLI:** Fix in one place

### Testing Benefits

**Test the entire tool comprehensively:**

```bash
#!/bin/bash
# test-pdf-tool.sh

# Test all commands at once
pdf-tool --agent rotate test.pdf 90 | jq .
pdf-tool --agent merge test1.pdf test2.pdf | jq .
pdf-tool --agent extract test.pdf | jq .

# Test error handling
pdf-tool --agent rotate nonexistent.pdf 2>&1 | jq .error
echo "Exit code: $?"  # Should be 100

# Test help
pdf-tool --agent help | grep -q "USAGE"
```

### Composability Benefits

Because the CLI follows PAS, it works with all Unix tools:

```bash
# Chain operations
pdf-tool --agent extract doc.pdf \
  | jq -r '.text' \
  | grep -i "important" \
  | wc -l

# Parallel processing
ls *.pdf | xargs -P 4 -I {} pdf-tool --agent extract {}

# Conditional logic
if pdf-tool --agent extract doc.pdf | jq -e '.pages > 10'; then
    pdf-tool --agent split doc.pdf --pages 1-10
fi
```

## Integration with Skills

PAS tools work great in skills! When documenting a tool usage in a skill:

**In SKILL.md:**
```markdown
## Using the Deploy Tool

Deploy to production:
```bash
deploy-tool --agent --env production
```

Check deployment status:
```bash
deploy-tool --agent status | jq -r '.status'
```
```

**The skill provides workflow/policy, the PAS tool provides capability.**

## Reference Materials

For complete technical specification, see [specification.md](specification.md).

For real-world examples and comparisons, see [examples.md](examples.md).

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ PAS Quick Reference                                 │
├─────────────────────────────────────────────────────┤
│ --agent flag          → JSON output mode            │
│ JSON Lines            → One object per line         │
│ Exit codes            → 0, 1, 2, 100-125            │
│ Errors                → JSON to stderr              │
│ Success               → JSON to stdout              │
│ Help                  → Concise patterns            │
└─────────────────────────────────────────────────────┘

Exit Code Guide:
  0     Success
  1     General error
  2     Invalid usage
  100+  Semantic errors (tool-specific)

JSON Error Format:
  {
    "error": "ERROR_TYPE",
    "message": "Human description",
    "code": 100
  }
```

## When to Use Which Level

```
Simple wrapper around API?
└─ Level 1 (--agent flag only)

Production CLI used frequently?
└─ Level 2 (+ JSON Lines + exit codes)

Read-only API browser/explorer?
└─ Level 3 (+ ls/cat/stat verbs)

Full sync tool with state management?
└─ Level 4 (+ cp/rm/sync/mount)
```

## Summary

**For agents to use your tool:**
1. Add `--agent` flag that outputs JSON
2. Use JSON Lines for lists (one per line)
3. Return semantic exit codes (100-125)
4. Write errors as JSON to stderr
5. Keep `--agent --help` concise

**Result:** Agents can use your tool without custom wrappers, MCP servers, or additional context.
