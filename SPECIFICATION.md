# POSIX Agent Specification (PAS)
## Technical Standard for Agent-Compatible CLI Tools

**Version:** 0.1.0-draft
**Status:** Request for Comments (RFC)
**Last Updated:** February 3, 2026

---

## Abstract

This specification defines a minimal set of behavioral requirements for command-line tools to be natively compatible with AI agents. Adherence to this standard ensures tools are deterministic, composable, and require minimal additional context for agents to use effectively.

**Design Goals:**
1. **Zero Custom Code:** Eliminate the need for wrapper servers or translation layers
2. **Token Efficiency:** Minimize context required to explain tool usage
3. **Composability:** Enable piping between tools via standard Unix mechanisms
4. **Safety:** Provide deterministic, auditable behavior

---

## 1. Conformance Levels

A tool may claim conformance at one of three levels:

### Level 1: Agent-Safe (Minimum)
- Implements `--agent` flag or equivalent
- Provides non-interactive execution mode
- Returns structured errors

### Level 2: Agent-Optimized (Recommended)
- Level 1 requirements, plus:
- Outputs JSON Lines (NDJSON) for list data
- Provides `--help-agent` or `.llm` documentation
- Uses semantic exit codes

### Level 3: Agent-Native (Ideal)
- Level 2 requirements, plus:
- Supports streaming output
- Provides FUSE interface for data-heavy operations (where applicable)
- Implements comprehensive error recovery guidance

---

## 2. Core Requirements

### 2.1 The Agent Flag

**Requirement:** All conforming tools MUST provide a flag (recommended: `--agent`) that enforces deterministic behavior.

**Behavior when `--agent` is active:**

#### 2.1.1 Output Purity (MANDATORY)

**Success Case (exit code 0):**
```bash
# stdout MUST contain ONLY the requested data
# No preambles, no success messages, no decorations

$ weather --agent --city "Boston"
{"temp": 45, "condition": "Cloudy", "wind": "10mph"}
```

**Failure Case (exit code > 0):**
```bash
# stderr MUST contain structured error information
# stdout MUST be empty

$ weather --agent --city "InvalidCity"
# stdout: (empty)
# stderr: {"error": "CITY_NOT_FOUND", "message": "No data for city 'InvalidCity'", "code": 404}
# exit code: 1
```

**Rationale:** Agents cannot parse mixed human-readable and machine-readable output. Separation of concerns (data on stdout, errors on stderr) enables reliable pipe composition.

#### 2.1.2 Zero Interactivity (MANDATORY)

```bash
# FORBIDDEN: Blocking prompts
$ deploy --agent
? Delete existing deployment? (y/N)  # ❌ BLOCKS FOREVER

# REQUIRED: Fail with explicit flag requirement
$ deploy --agent
# stderr: {"error": "MISSING_FLAG", "message": "Destructive operation requires --force", "suggestion": "--force"}
# exit code: 1
```

**Requirement:** The tool MUST NOT:
- Read from stdin unless explicitly accepting piped data
- Display confirmation prompts
- Wait for user input of any kind

**Exception:** Tools designed to process stdin (e.g., `jq`, `grep`) may read stdin when data is piped, but MUST fail if stdin is a TTY.

#### 2.1.3 State Suppression (MANDATORY)

When `--agent` is active, the tool MUST disable:
- Progress bars
- Spinners / loading indicators
- ANSI color codes (unless `--color=always` explicitly set)
- Pagination (no automatic piping to `less` or `more`)
- Bells / beeps / audio feedback
- Dynamic line updates (e.g., "Downloading... 45%")

```bash
# BAD: Progress output
$ large-download --agent https://example.com/file.zip
Downloading... ████████░░░░░░░░ 45% (12.3 MB/s)  # ❌

# GOOD: Silent until complete, or structured progress
$ large-download --agent https://example.com/file.zip
{"status": "downloading", "progress": 0.45, "speed": "12.3MB/s"}
{"status": "complete", "path": "/tmp/file.zip", "size": 27865432}
```

**Rationale:** Agents cannot interpret ephemeral terminal updates. All state changes must be parseable events.

---

## 3. Data Interchange Format

### 3.1 JSON Lines (NDJSON) for Collections

**Requirement (Level 2):** When outputting multiple items, tools SHOULD use JSON Lines format.

**Specification:**
- Each line is a complete, valid JSON object
- Lines are separated by newline (`\n`)
- No trailing comma after last object
- Each object is self-contained (no references between lines)

```bash
# Correct: JSON Lines
$ users list --agent --limit 3
{"id":1,"name":"Alice","status":"active"}
{"id":2,"name":"Bob","status":"active"}
{"id":3,"name":"Charlie","status":"inactive"}

# AVOID: JSON Array (breaks streaming)
$ users list --agent --limit 3
[
  {"id":1,"name":"Alice","status":"active"},
  {"id":2,"name":"Bob","status":"active"},
  {"id":3,"name":"Charlie","status":"inactive"}
]
```

**Why JSON Lines?**

1. **Streaming:** Consumers can process line 1 while line 100 is still generating
2. **Pipe-friendly:** Works with `jq -c`, `grep`, and standard Unix tools
3. **Memory-efficient:** No need to buffer entire dataset
4. **Fault-tolerant:** Partial results available even if process is interrupted

**Compatibility:** Tools SHOULD also support `--format=array` for legacy use cases requiring standard JSON arrays.

### 3.2 Markdown for Documents

**Requirement (Level 2):** When outputting unstructured text (logs, articles, documentation), tools SHOULD use clean Markdown.

**Rationale:**
- LLMs are trained on massive amounts of Markdown
- Significantly fewer tokens than JSON-escaped strings
- Human-readable in raw form

```bash
# Good: Markdown output
$ docs get --agent "API Authentication"
# Authentication

Use Bearer tokens in the Authorization header:

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

See [Rate Limits](./rate-limits.md) for usage quotas.

# Avoid: JSON-wrapped with escaped newlines
$ docs get --agent "API Authentication"
{"content": "# Authentication\n\nUse Bearer tokens...\n\nSee [Rate Limits](./rate-limits.md)..."}
```

### 3.3 Exit Codes

**Requirement (Level 2):** Tools SHOULD use semantic exit codes beyond simple success/failure.

**Standard Ranges:**
- `0`: Success
- `1`: General error
- `2`: Misuse of command (invalid arguments)
- `64-78`: Reserved (see `sysexits.h` for traditional meanings)
- `100-125`: Custom application errors (tool-specific)

**Documentation:** Tools MUST document their exit codes in `--help-agent` output.

```bash
$ mytool --help-agent
...
Exit Codes:
  0   Success
  1   General error
  2   Invalid arguments
  100 Resource not found
  101 Permission denied
  102 Network timeout
```

**Usage in pipelines:**
```bash
# Agent can handle specific failures
weather --agent --city "Boston" || {
  code=$?
  if [ $code -eq 100 ]; then
    echo "City not found, trying geocoding..."
  fi
}
```

---

## 4. Documentation Standard

### 4.1 Agent-Optimized Help

**Requirement (Level 2):** Tools SHOULD provide concise help via `--help-agent`.

**Structure:**
```
USAGE:
  <tool> [FLAGS] <ARGS>

COMMON PATTERNS:
  <3-5 example one-liners>

ERROR CODES:
  <List of exit codes and meanings>

ANTI-PATTERNS:
  <Common mistakes to avoid>
```

**Example:**
```bash
$ git --help-agent
USAGE:
  git <command> [options] [args]

COMMON PATTERNS:
  git clone --depth 1 <url>              # Shallow clone (faster)
  git log --oneline -n 10                # Recent commits
  git diff --stat HEAD~1                 # Summary of last commit
  git branch --show-current              # Current branch name
  git restore --staged <file>            # Unstage file

ERROR CODES:
  0   Success
  1   General error (see stderr)
  128 Git operation failed (e.g., not a repo)

ANTI-PATTERNS:
  git pull             # May trigger merge conflicts; use fetch + merge
  git commit -a        # Interactive editor; use -m "message" or -F file
  git add .            # May include unintended files; be specific
```

**Rationale:** Standard `--help` is optimized for human browsing (verbose, formatted). `--help-agent` is optimized for context window efficiency.

### 4.2 LLM Documentation Files (Optional, Level 3)

Tools MAY provide a `.llm` file at `docs/<tool>.llm` or `/usr/share/doc/<tool>/agent.llm`.

**Format:** Simplified Markdown, target length: 50-200 lines.

**Sections:**
1. **Purpose** (1 sentence)
2. **Signature** (exact syntax)
3. **Cheatsheet** (5-10 common patterns)
4. **Anti-patterns** (what NOT to do)
5. **Error codes** (exit code meanings)

---

## 5. Advanced Features (Level 3)

### 5.1 Streaming Output

For long-running operations, tools SHOULD emit progress events as JSON Lines:

```bash
$ large-task --agent
{"event":"start","timestamp":"2026-02-03T10:00:00Z"}
{"event":"progress","step":1,"total":10,"message":"Validating input"}
{"event":"progress","step":2,"total":10,"message":"Connecting to API"}
...
{"event":"complete","result":{"id":12345,"status":"success"}}
```

**Requirements:**
- Each event is a complete JSON object
- Flush stdout after each line (no buffering)
- Final line indicates completion or error

### 5.2 FUSE Interfaces

For data-heavy tools (databases, APIs, cloud storage), tools SHOULD provide a FUSE mount option:

```bash
$ db-fuse mount --agent ./db-mount
# stderr: {"event":"mounted","path":"./db-mount"}

$ ls ./db-mount/tables
users.json
products.json
orders.json

$ cat ./db-mount/tables/users.json | head -n 1
{"id":1,"name":"Alice","email":"alice@example.com"}

$ echo '{"name":"Bob","email":"bob@example.com"}' > ./db-mount/tables/users.json
# Automatically translates to: INSERT INTO users ...
```

**Rationale:**
- Agents learn ONE interface (file I/O) for ALL data sources
- Standard tools (`cat`, `grep`, `jq`) work immediately
- No custom API learning required

---

## 6. Error Handling

### 6.1 Structured Errors

**Requirement (Level 1):** All errors MUST be emitted as JSON to stderr.

**Schema:**
```json
{
  "error": "ERROR_CODE_CONSTANT",
  "message": "Human-readable explanation",
  "code": 404,  // Optional: HTTP-style code
  "suggestion": "Try --retry or check credentials",  // Optional
  "details": {  // Optional: Additional context
    "attempted_url": "https://api.example.com/users",
    "timeout_seconds": 30
  }
}
```

**Example:**
```bash
$ api-client get --agent /users/999999
# stderr: {
#   "error": "NOT_FOUND",
#   "message": "User ID 999999 does not exist",
#   "code": 404,
#   "suggestion": "Use 'api-client search --agent' to find valid user IDs"
# }
# exit code: 1
```

### 6.2 Recovery Guidance

**Requirement (Level 3):** Errors SHOULD include actionable recovery steps.

**Example:**
```json
{
  "error": "AUTH_EXPIRED",
  "message": "API credentials have expired",
  "code": 401,
  "recovery": [
    {"step": 1, "action": "Run: auth-tool refresh"},
    {"step": 2, "action": "Retry this command"}
  ]
}
```

---

## 7. Security Considerations

### 7.1 Sandboxing Compatibility

Tools SHOULD be designed to work in restricted environments:

```bash
# Must work with:
# - No network access (if --offline flag provided)
# - Read-only filesystem (use /tmp for temp files)
# - Limited PATH (no shell-out to unknown binaries)
```

### 7.2 Credential Handling

**Requirement (Level 1):** Tools MUST NOT:
- Print credentials/tokens to stdout
- Include credentials in error messages
- Log sensitive data without explicit `--debug-insecure` flag

```bash
# BAD: Exposes token
$ api-client --agent --token abc123 get /users
# stderr: {"error": "Request failed", "attempted_url": "https://api.example.com/users?token=abc123"}

# GOOD: Redacts token
$ api-client --agent --token abc123 get /users
# stderr: {"error": "Request failed", "attempted_url": "https://api.example.com/users?token=[REDACTED]"}
```

### 7.3 Audit Logging

**Recommendation (Level 3):** Tools SHOULD support structured audit logs:

```bash
$ mytool --agent --audit-log ./audit.jsonl action
# Emits to audit.jsonl:
{"timestamp":"2026-02-03T10:00:00Z","command":"mytool action","user":"agent","result":"success"}
```

---

## 8. Testing & Validation

### 8.1 Conformance Test Suite

A reference test suite is provided at `github.com/posix-agent-standard/tests`.

**Key tests:**
- **No TTY dependency:** Tool works with stdin/stdout/stderr redirected
- **Determinism:** Same input produces same output across runs
- **Timeout handling:** Long operations respect `SIGTERM`
- **Pipe compatibility:** `tool --agent | jq` succeeds
- **Error structure:** All errors are valid JSON

### 8.2 Self-Validation

Tools MAY implement `--validate-pas` to self-check conformance:

```bash
$ mytool --validate-pas
✓ Implements --agent flag
✓ Produces valid JSON Lines output
✓ Structured errors on stderr
✓ Non-interactive mode works
✓ Documentation via --help-agent available
⚠ Warning: No .llm file provided (Level 3 optional)

Conformance: Level 2 (Agent-Optimized)
```

---

## 9. Migration Guide

### 9.1 Adding `--agent` to Existing Tools

**Minimal implementation (Python example):**

```python
import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent', action='store_true',
                       help='Enable agent-compatible mode')
    parser.add_argument('--city', required=True)

    args = parser.parse_args()

    try:
        result = get_weather(args.city)

        if args.agent:
            # Agent mode: pure JSON to stdout
            print(json.dumps(result))
        else:
            # Human mode: pretty output
            print(f"Weather in {args.city}:")
            print(f"  Temperature: {result['temp']}°F")
            print(f"  Conditions: {result['condition']}")

    except Exception as e:
        if args.agent:
            # Agent mode: structured error to stderr
            error = {
                "error": type(e).__name__.upper(),
                "message": str(e),
                "code": getattr(e, 'code', 1)
            }
            print(json.dumps(error), file=sys.stderr)
            sys.exit(1)
        else:
            # Human mode: friendly message
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
```

### 9.2 Replacing MCP Servers

**Before (MCP wrapper):**
```python
# weather_mcp_server.py - 250 lines

from mcp import Server, Tool

server = Server()

@server.tool(name="get_weather")
def get_weather(city: str) -> dict:
    # Call weather API
    # Parse response
    # Return structured data
    pass

server.run()
```

**After (PAS-compliant CLI):**
```bash
# Agents just run:
$ weather-cli --agent --city "Boston"
```

**Result:**
- 250 lines → 0 lines (use existing CLI)
- No server to maintain
- No schema definitions needed
- Works with any agent immediately

---

## 10. Governance & Evolution

### 10.1 Reference Implementation

The official reference implementation is maintained at:
**[github.com/posix-agent-standard/reference](https://github.com/posix-agent-standard/reference)**

### 10.2 Versioning

This specification uses Semantic Versioning:
- **Major:** Breaking changes to core requirements
- **Minor:** New optional features or recommendations
- **Patch:** Clarifications and corrections

Current version: **0.1.0-draft** (pre-release)

### 10.3 Contributing

This is an open standard. Contributions welcome via:
- GitHub issues for clarification requests
- Pull requests for improvement proposals
- Real-world case studies demonstrating impact

### 10.4 Endorsements

Organizations implementing this standard:
- *(List will be populated as adoption grows)*

---

## 11. FAQ

### Q: Does this replace MCP?

**A:** No—it's complementary. Use PAS for tools that can be CLIs. Use MCP for truly custom internal logic that has no CLI equivalent.

**Decision tree:**
```
Does a CLI tool already exist for this? → Use it directly (PAS)
├─ No → Could you build a CLI? → Yes → Build PAS-compliant CLI
└─ No → Is the logic highly custom? → Yes → Consider MCP
```

### Q: What about Windows compatibility?

**A:** The principles apply universally:
- PowerShell supports pipes and exit codes
- JSON Lines works everywhere
- `--agent` flag is cross-platform

Windows-specific consideration: Use `CRLF` line endings or handle both `LF` and `CRLF`.

### Q: Doesn't this give agents too much power?

**A:** Safety is achieved through sandboxing, not through limiting interfaces.

**Safe patterns:**
```bash
# Run agent in restricted container
docker run --rm --network=none --read-only \
  -v $(pwd)/workspace:/work:rw \
  agent-sandbox
```

Tools are just as dangerous whether called via MCP or CLI—the difference is that CLI calls are auditable plaintext.

---

## 12. License

This specification is released under **CC BY 4.0**.

You are free to:
- Implement this standard in your tools (no attribution required)
- Share and adapt this document (attribution required)

---

## Appendix A: Complete Example

**Tool:** `word-counter` - Counts words in files

**Implementation:**

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
  --help-agent     Show agent-optimized help
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
while [ $# -gt 0 ]; do
    case "$1" in
        --agent)
            AGENT_MODE=true
            shift
            ;;
        --help-agent)
            agent_help
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo '{"error":"INVALID_ARGUMENT","message":"Unknown option: '"$1"'","suggestion":"See --help"}' >&2
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

**Usage:**

```bash
# Human mode
$ word-counter README.md
README.md: 1250 words

# Agent mode
$ word-counter --agent README.md LICENSE.md
{"file":"README.md","words":1250}
{"file":"LICENSE.md","words":450}

# Composition with jq
$ word-counter --agent *.md | jq -s 'map(.words) | add'
1700

# Error handling
$ word-counter --agent nonexistent.txt
# stderr: {"error":"FILE_NOT_FOUND","message":"File not found: nonexistent.txt","code":100}
# exit code: 100
```

---

## Appendix B: Resources

- **Reference implementation:** [github.com/posix-agent-standard/reference](https://github.com/posix-agent-standard/reference)
- **Test suite:** [github.com/posix-agent-standard/tests](https://github.com/posix-agent-standard/tests)
- **Community examples:** [github.com/posix-agent-standard/examples](https://github.com/posix-agent-standard/examples)
- **Discussion forum:** [github.com/posix-agent-standard/discussions](https://github.com/posix-agent-standard/discussions)

---

**End of Specification**

**Version:** 0.1.0-draft
**Published:** February 3, 2026
**Next Review:** March 2026
