# Quick Start Guide

Get started with the POSIX Agent Standard in 15 minutes.

---

## What Is This?

The POSIX Agent Standard (PAS) is a simple way to make your CLI tools AI agent-friendly **without building wrappers or servers**.

**The core idea:** Large language models already know Unix commands. Stop teaching them custom APIs and let them use what they already know.

---

## The 3 Rules (TL;DR)

### 1. Add `--agent` flag
```bash
$ mytool --agent input.txt
{"result": "success", "data": {...}}
```
**Guarantees:** Non-interactive, structured output (JSON), structured errors (stderr)

### 2. Use JSON Lines for lists
```bash
$ mytool list --agent
{"id":1,"name":"Alice"}
{"id":2,"name":"Bob"}
{"id":3,"name":"Charlie"}
```
**Why:** Streaming, pipe-friendly, works with `jq`

### 3. Document concisely
```bash
$ mytool --agent --help
USAGE: mytool [--agent] <input>
COMMON PATTERNS:
  mytool --agent file.txt    # Process file
ERROR CODES:
  0   Success
  1   General error
  100 Custom error
```
**Why:** Saves token overhead

---

## 5-Minute Implementation

Turn any existing CLI into a PAS-compliant tool:

### Before (human-only)
```bash
#!/bin/bash
# mytool.sh
echo "Processing $1..."
result=$(do_some_work "$1")
echo "Result: $result"
```

### After (agent-friendly)
```bash
#!/bin/bash
# mytool.sh

AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true && shift

if [ "$AGENT_MODE" = true ]; then
    # Agent mode: Pure JSON output
    result=$(do_some_work "$1")
    echo "{\"result\": \"$result\"}"
else
    # Human mode: Pretty output
    echo "Processing $1..."
    result=$(do_some_work "$1")
    echo "Result: $result"
fi
```

**That's it.** Your tool is now agent-compatible.

---

## Complete Example: Word Counter

A fully PAS-compliant tool in ~50 lines:

```bash
#!/usr/bin/env bash
# word-counter - Count words in files (PAS Level 2)

set -euo pipefail

show_agent_help() {
    cat << 'EOF'
USAGE:
  word-counter [--agent] <file...>

COMMON PATTERNS:
  word-counter --agent file.txt
  find . -name "*.md" | xargs word-counter --agent
  word-counter --agent *.txt | jq -s 'map(.words) | add'

ERROR CODES:
  0   Success
  100 File not found
  101 File not readable
EOF
}

count_words() {
    local file="$1"

    if [ ! -f "$file" ]; then
        if [ "$AGENT_MODE" = true ]; then
            echo '{"error":"FILE_NOT_FOUND","message":"File not found: '"$file"'"}' >&2
        else
            echo "Error: File not found: $file" >&2
        fi
        exit 100
    fi

    local count=$(wc -w < "$file" | tr -d ' ')

    if [ "$AGENT_MODE" = true ]; then
        echo "{\"file\":\"$file\",\"words\":$count}"
    else
        echo "$file: $count words"
    fi
}

# Parse arguments
AGENT_MODE=false
while [ $# -gt 0 ]; do
    case "$1" in
        --agent) AGENT_MODE=true; shift ;;
        --agent --help) show_agent_help; exit 0 ;;
        -h|--help) show_help; exit 0 ;;
        -*) echo '{"error":"INVALID_ARG","message":"Unknown: '"$1"'"}' >&2; exit 2 ;;
        *) break ;;
    esac
done

[ $# -eq 0 ] && echo '{"error":"MISSING_ARG","message":"No files specified"}' >&2 && exit 2

# Process files
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
$ word-counter --agent README.md
{"file":"README.md","words":1250}

# Composition with jq
$ word-counter --agent *.md | jq -s 'map(.words) | add'
3700
```

---

## Testing Your Tool

### Test 1: Non-interactive
```bash
# Should complete without hanging
$ echo "" | mytool --agent input.txt
```

### Test 2: Valid JSON output
```bash
# Should parse without errors
$ mytool --agent input.txt | jq .
```

### Test 3: Structured errors
```bash
# Should emit JSON to stderr, exit non-zero
$ mytool --agent nonexistent.txt 2>&1 >/dev/null | jq .
```

### Test 4: Pipe-friendly
```bash
# Should work in a pipeline
$ echo "file1.txt file2.txt" | xargs mytool --agent | jq -s .
```

### Test 5: Concise help
```bash
# Should be < 50 lines
$ mytool --agent --help | wc -l
```

---

## Real-World Example: Weather API

### The "Enterprise" Way (MCP Server)

**Setup:**
1. Write 247 lines of Python wrapper
2. Install 4 dependencies: `pip install mcp-sdk fastapi uvicorn requests`
3. Start server: `python weather_server.py`
4. Configure agent to connect to `localhost:8080`
5. Load 430-token schema into agent context

**Agent usage:** `call_tool("get_weather", {"city": "Boston"})`

**Maintenance:** Update server as MCP spec evolves

### The PAS Way (Simple CLI)

**Setup:**
1. Write 28 lines of bash: [see examples/weather/after-pas.sh](./examples/weather/after-pas.sh)
2. No dependencies (uses `curl` and `jq`)
3. Make executable: `chmod +x weather.sh`

**Agent usage:** `./weather.sh --agent --city Boston`

**Maintenance:** None (uses stable APIs)

**Result:**
- **88% less code** (247 → 28 lines)
- **95% fewer tokens** (430 → 20 tokens)
- **Zero server overhead**
- **Fully composable**

[See full comparison →](./examples/weather/README.md)

---

## Common Patterns

### Pattern 1: Multiple Items (JSON Lines)
```bash
#!/bin/bash
# list-users.sh --agent

if [ "$1" = "--agent" ]; then
    # Output one JSON object per line
    cat users.csv | while IFS=, read id name email; do
        echo "{\"id\":$id,\"name\":\"$name\",\"email\":\"$email\"}"
    done
else
    # Pretty table for humans
    cat users.csv | column -t -s,
fi
```

### Pattern 2: Error Handling
```bash
#!/bin/bash
# process-file.sh --agent <file>

AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true && shift

FILE="$1"

if [ ! -f "$FILE" ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo '{"error":"FILE_NOT_FOUND","message":"File '"$FILE"' does not exist","code":100}' >&2
    else
        echo "Error: File not found: $FILE" >&2
    fi
    exit 100
fi

# Process file...
```

### Pattern 3: Streaming Progress
```bash
#!/bin/bash
# long-task.sh --agent

if [ "$1" = "--agent" ]; then
    echo '{"event":"start","timestamp":"'$(date -Iseconds)'"}'
    for i in {1..10}; do
        # Do work
        echo '{"event":"progress","step":'$i',"total":10}'
        sleep 1
    done
    echo '{"event":"complete","result":"success"}'
else
    # Human-friendly progress bar
    for i in {1..10}; do
        echo -ne "Progress: [$i/10]\r"
        sleep 1
    done
    echo -e "\nComplete!"
fi
```

---

## Composing Tools (The Killer Feature)

PAS tools work with standard Unix pipes:

### Example: "Find inactive users and email them"

```bash
# Three separate PAS-compliant tools, composed:

users-cli list --agent --status inactive \
  | jq -r '.email' \
  | xargs -I {} email-cli send --agent \
      --to {} \
      --subject "Account inactivity notice" \
      --template inactive.txt
```

**What happened:**
1. `users-cli` output JSON Lines of users
2. `jq` filtered for inactive users (instant, free)
3. `xargs` called `email-cli` for each user

**Key insight:** Logic (filtering) happened in `jq`, not in the LLM. This saves tokens and time.

---

## Migration from MCP

### Step 1: Identify candidates
Look for MCP servers that just wrap existing APIs or CLIs.

**Good candidates for PAS:**
- ✅ Tools that fetch data from APIs
- ✅ Tools that run existing commands
- ✅ Tools with simple input/output
- ✅ Tools that could be shell scripts

**Keep as MCP:**
- ❌ Tools with complex state
- ❌ Tools requiring authentication flow
- ❌ Tools with truly custom business logic

### Step 2: Build the CLI
Extract the core logic from your MCP server:

```python
# Before: MCP server
@server.tool(name="get_data")
def get_data(id: str) -> dict:
    response = requests.get(f"https://api.example.com/items/{id}")
    return response.json()
```

```bash
# After: PAS CLI
#!/bin/bash
# get-data.sh --agent <id>

AGENT_MODE=false
[ "$1" = "--agent" ] && AGENT_MODE=true && shift

ID="$1"
RESPONSE=$(curl -sf "https://api.example.com/items/$ID")

if [ "$AGENT_MODE" = true ]; then
    echo "$RESPONSE"
else
    echo "$RESPONSE" | jq .
fi
```

### Step 3: Update agent config
```diff
- # Old: Agent calls MCP server
- result = agent.call_tool("get_data", {"id": "123"})

+ # New: Agent runs CLI
+ result = subprocess.run(
+     ["get-data.sh", "--agent", "123"],
+     capture_output=True, text=True
+ )
+ data = json.loads(result.stdout)
```

### Step 4: Measure the impact
```python
# Before
baseline_tokens = measure_agent_with_mcp()
baseline_time = measure_execution_time()

# After
pas_tokens = measure_agent_with_cli()
pas_time = measure_execution_time()

print(f"Token reduction: {(baseline - pas) / baseline * 100}%")
print(f"Speed improvement: {baseline_time / pas_time}x")
```

**Expected results:** 30-40% token reduction, 2-3x speedup

---

## Further Reading

- **Why?** [Read the Manifesto](./MANIFESTO.md) (15 min)
- **How?** [Read the Specification](./SPECIFICATION.md) (30 min)
- **Integration** [PAS + Agent Skills](./SKILLS.md) (20 min)
- **Show me!** [See Examples](./examples/README.md) (20 min)
- **I want to help** [Contributing Guide](./CONTRIBUTING.md) (5 min)

---

## Common Questions

**Q: Isn't this just "give the agent bash"?**
A: Almost. PAS adds conventions (`--agent` flag, JSON Lines, stderr errors) that make bash output **reliable** and **composable** for agents.

**Q: What if my tool needs authentication?**
A: Use environment variables or config files. Example:
```bash
export API_TOKEN="..."
mytool --agent --resource foo  # Reads $API_TOKEN
```

**Q: Can I use Python/Ruby/Node instead of Bash?**
A: Absolutely! PAS is language-agnostic. The key is the interface (stdin/stdout, JSON, --agent flag), not the implementation language.

**Q: How do I handle long-running operations?**
A: Emit progress events as JSON Lines:
```json
{"event":"progress","step":1,"total":10,"message":"Downloading..."}
{"event":"progress","step":2,"total":10,"message":"Processing..."}
{"event":"complete","result":"success"}
```

**Q: What about Windows?**
A: PAS works on Windows with PowerShell. The principles (JSON output, structured errors, non-interactive) are universal.

---

## Next Steps

1. **Try the example:** Run `examples/weather/after-pas.sh`
2. **Build your own:** Pick a simple tool and add `--agent` mode
3. **Share results:** Tell us your token savings and speedup
4. **Contribute:** Add your tool to the examples directory

**Questions?** [Open an issue](https://github.com/turlockmike/posix-agent-standard/issues)

---

## Summary: The 3 Rules

1. **`--agent` flag** → Non-interactive, JSON output, structured errors
2. **JSON Lines format** → Streaming, pipe-friendly, works with `jq`
3. **Concise help** → `--agent --help` for token efficiency

**Result:** 88% less code, 95% fewer tokens, full composability.

**Get started:** [Read the full spec →](./SPECIFICATION.md)
