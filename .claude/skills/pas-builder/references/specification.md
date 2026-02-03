# POSIX Agent Standard (PAS) - Technical Specification

**Version:** 0.1.0-draft
**Status:** Request for Comments (RFC)

## Conformance Levels

### Level 1: Agent-Safe (Minimum)
- Implements `--agent` flag or equivalent
- Provides non-interactive execution mode
- Returns structured errors

### Level 2: Agent-Optimized (Recommended)
- Level 1 requirements, plus:
- Outputs JSON Lines (NDJSON) for list data
- Provides `--agent --help` or `.llm` documentation
- Uses semantic exit codes

### Level 3: The Navigation Contract (Optional)
- Level 2 requirements, plus:
- Implements Unix-style navigation verbs for remote resources
- Standard verbs: `ls` (list), `cat` (read), `stat` (metadata)
- Hierarchical path structure (e.g., `/users/123/orders`)

### Level 4: The State Contract (Advanced)
- Level 3 requirements, plus:
- Implements manipulation verbs: `cp` (write), `rm` (delete)
- Supports `sync` command for one-way synchronization
- Optional: `mount` command for FUSE virtualization
- Implements `feedback` command for reporting tool issues

## Core Requirements

### The Agent Flag as Global Modifier

**Requirement:** All conforming tools MUST provide a flag (recommended: `--agent`) that acts as a global mode switch.

**Core concept:** `--agent` is not just another flag—it modifies the behavior of ALL other flags and subcommands, transforming the tool into Strict Machine Mode.

**Flag ordering:** Tools SHOULD accept `--agent` in any position, but conventionally it appears first.

**Behavior when `--agent` is active:**

1. **Non-interactive:** Never prompt for input, never wait
2. **Structured output:** JSON or JSON Lines to stdout
3. **Structured errors:** JSON to stderr
4. **No decorations:** No spinners, colors, progress bars, or ANSI codes
5. **Deterministic:** Same input produces same output

### Output Format

**For single results:**
```json
{"result": "value", "status": "success"}
```

**For lists (JSON Lines):**
```json
{"id":1,"name":"Alice"}
{"id":2,"name":"Bob"}
```

**NOT this (JSON array):**
```json
[{"id":1},{"id":2}]
```

### Error Format

Errors MUST go to stderr as JSON:

```json
{
  "error": "ERROR_TYPE",
  "message": "Human-readable description",
  "code": 100
}
```

**Required fields:**
- `error`: Machine-readable error type (UPPER_SNAKE_CASE)
- `message`: Human-readable description

**Optional fields:**
- `code`: Numeric exit code
- `suggestion`: Hint for fixing the error
- `context`: Additional debugging information

### Exit Codes

**Standard codes:**
- `0` - Success
- `1` - General error
- `2` - Invalid usage (bad flags/arguments)

**Semantic codes (100-125):**
- `100` - Resource not found
- `101` - Permission denied
- `102` - Invalid format
- `103` - Timeout
- `104` - Network error
- `105-125` - Tool-specific errors

### Help Text

**Agent help (`--agent --help`) MUST include:**

1. **USAGE:** Concise syntax
2. **COMMON PATTERNS:** 3-5 most frequent use cases
3. **ERROR CODES:** Semantic exit codes with descriptions

**Format:**
```
USAGE:
  tool [--agent] <required> [optional]

COMMON PATTERNS:
  tool --agent file.txt
  tool --agent --filter status=active list

ERROR CODES:
  0   Success
  1   General error
  100 File not found
```

**Agent help SHOULD NOT include:**
- Verbose descriptions
- Examples with commentary
- ASCII art or formatting
- Background information

## Level 3: Navigation Contract

Tools managing external datasets (APIs, databases, cloud storage) SHOULD implement:

### ls (list)
```bash
$ tool --agent ls /users
{"id":1,"name":"Alice","type":"user"}
{"id":2,"name":"Bob","type":"user"}
```

### cat (read)
```bash
$ tool --agent cat /users/1
{"id":1,"name":"Alice","email":"alice@example.com","status":"active"}
```

### stat (metadata)
```bash
$ tool --agent stat /users/1
{"path":"/users/1","type":"user","size":256,"modified":"2025-02-03T10:00:00Z"}
```

## Level 4: State Contract

### cp (write/create)
```bash
$ tool --agent cp local.json /users/new
{"id":3,"path":"/users/3","status":"created"}
```

### rm (delete)
```bash
$ tool --agent rm /users/3
{"path":"/users/3","status":"deleted"}
```

### sync (synchronize)
```bash
$ tool --agent sync --from /users --to ./local/
{"synced":10,"skipped":2,"errors":0}
```

## JSON Lines Specification

**Format:** One complete JSON object per line, separated by newline (`\n`).

**Benefits:**
- Streamable (process before completion)
- Pipeable with `jq`
- Appendable (no array closing bracket)
- Memory efficient (line-by-line parsing)

**Example:**
```bash
$ tool --agent list | jq -r '.name'
Alice
Bob
Charlie
```

## Non-Interactive Requirement

Tools in agent mode MUST NEVER:
- Wait for user input
- Display progress spinners
- Show interactive prompts
- Use readline/TTY features
- Check if stdout is a terminal

## Determinism Requirement

Same input → Same output (except for time-based or random data that's explicitly part of the result).

**Violations:**
- Inconsistent output order without sorting
- Non-reproducible random values
- Undeclared side effects

## Backward Compatibility

Adding `--agent` flag MUST NOT change existing behavior when the flag is absent.

Existing users see no difference; new agent users get structured output.

## Implementation Notes

### Bash Implementation
```bash
#!/usr/bin/env bash
set -euo pipefail

AGENT_MODE=false
for arg in "$@"; do
    [ "$arg" = "--agent" ] && AGENT_MODE=true && break
done

if [ "$AGENT_MODE" = true ]; then
    # Machine mode
    echo '{"result":"success"}'
else
    # Human mode
    echo "Success!"
fi
```

### Python Implementation
```python
#!/usr/bin/env python3
import json
import sys

agent_mode = '--agent' in sys.argv

if agent_mode:
    print(json.dumps({"result": "success"}))
else:
    print("Success!")
```

### Testing Compliance

**Test suite checklist:**
1. `--agent` flag accepted
2. JSON output is valid (pipe to `jq .`)
3. Errors go to stderr
4. Exit codes are semantic
5. JSON Lines for lists (not arrays)
6. No interactive prompts
7. No progress indicators
8. Help text is concise

## Versioning

This specification uses semantic versioning:
- Major version: Breaking changes
- Minor version: Backward-compatible additions
- Patch version: Clarifications and fixes

## References

- Unix Philosophy: Doug McIlroy, 1978
- JSON Lines: https://jsonlines.org/
- RFC 2119: Key words for use in RFCs (MUST, SHOULD, MAY)
- Vercel agent optimization case study (2024)

## Conformance Declaration

Tools MAY declare conformance in help text:

```
$ tool --version
mytool v1.0.0 (PAS Level 2 Compliant)
```
