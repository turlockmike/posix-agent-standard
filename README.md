# The POSIX Agent Standard

> **"Don't teach your AI to use an API. Teach it to use a Computer."**

A lightweight standard for building AI agent-compatible CLI tools based on Unix principles—because the best interface is the one your agent already knows.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Status: RFC](https://img.shields.io/badge/Status-RFC-yellow.svg)](https://github.com/turlockmike/posix-agent-standard)
[![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0--draft-blue.svg)](./SPECIFICATION.md)

---

## The 30-Second Pitch

**The Problem:** We're building complex wrappers (MCP servers, custom tools, JSON schemas) just to let AI agents use existing CLIs.

**The Evidence:** Vercel deleted 80% of their agent's custom tools, gave it `bash` instead, and got:
- ✅ **3.5x faster** execution
- ✅ **37% fewer** tokens
- ✅ **95-100%** success rate (up from 80%)

**The Solution:** Stop building wrappers. Make your CLIs agent-friendly by following simple Unix conventions.

---

## Quick Comparison

### Building a Weather Tool

<table>
<tr>
<th width="50%">The "Enterprise" Way</th>
<th width="50%">The POSIX Way</th>
</tr>
<tr>
<td>

**1. Build MCP Server** (`weather_server.py`):
```python
from mcp import Server, Tool

@server.tool(name="get_weather")
def get_weather(city: str) -> dict:
    # 200 lines of wrapper code
    ...
```

**2. Define JSON Schema:**
```json
{
  "name": "get_weather",
  "parameters": {
    "city": {"type": "string"}
  },
  "returns": {...}
}
```

**3. Start Server:**
```bash
python weather_server.py
```

**4. Configure Agent:**
```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080"
    }
  }
}
```

**5. Agent Uses It:**
```python
result = agent.call_tool(
    "get_weather",
    {"city": "Boston"}
)
```

**Cost:** 200+ lines of code, server maintenance, API docs

</td>
<td>

**1. Write Simple CLI** (`weather.sh`):
```bash
#!/bin/bash
# 10 lines total

if [ "$1" = "--agent" ]; then
  curl -s "wttr.in/$2?format=j1"
else
  curl "wttr.in/$2"
fi
```

**2. Make Executable:**
```bash
chmod +x weather.sh
```

**3. Agent Uses It:**
```bash
$ weather.sh --agent Boston
{"temp": 45, "condition": "Cloudy"}
```

**Cost:** 10 lines of code, zero maintenance

</td>
</tr>
</table>

**The difference:** The agent already knows how to run bash commands. It doesn't know your custom MCP API.

---

## Real-World Results

### Case Study: Vercel's v0 Agent

**Challenge:** Text-to-SQL agent needed to query databases, validate schemas, and handle errors.

**Original Approach:** Custom tools
- `get_table_schema()` function
- `validate_query()` function
- `list_tables()` function
- Custom error handling for each
- **Result:** 80% success rate, slow, expensive

**New Approach:** Unix tools
- Agent uses: `head -n 5 table.csv`
- Agent uses: `sqlite3 -json "SELECT ..."`
- Standard Bash error handling
- **Result:** 95-100% success rate, 3.5x faster, 37% fewer tokens

**Source:** Vercel engineering blog, December 2024

---

## The Core Insight

### LLMs Are Unix Natives

Modern AI models have been trained on:
- The entire history of Stack Overflow
- Millions of Bash scripts from GitHub
- GNU Coreutils source code and man pages
- Decades of sysadmin blog posts

**They already know:**
```bash
grep -r "TODO" .                     # Search recursively
jq '.[] | select(.status == "active")' # Filter JSON
curl -H "Auth: Bearer $TOKEN" api.com  # HTTP requests
git log --oneline -n 10              # Recent commits
```

**They don't know:**
- Your custom `search_todos()` function
- Your bespoke MCP tool schema
- Your company's wrapper API

### The Token Economics

Every custom tool requires explaining it to the agent:

```
Custom Tool Overhead:
- Schema definition: ~200 tokens
- Function signature: ~50 tokens
- Error codes: ~100 tokens
- Examples: ~80 tokens
─────────────────────────────
Total per tool: ~430 tokens

Standard CLI:
- Agent already knows it: 0 tokens
- Your specific context: ~20 tokens
─────────────────────────────
Total per tool: ~20 tokens
```

**For a 20-tool agent:**
- Custom approach: 8,600 tokens just for docs
- POSIX approach: 400 tokens

That's **95% token savings** before you even start the task.

**Note on token savings:** The 95% figure represents maximum theoretical savings from eliminating tool documentation overhead. Real-world deployments (like Vercel's) see 30-40% overall reduction because agents still need context for tasks, data, and reasoning—but tool docs no longer consume that valuable space.

---

## The Standard (TL;DR)

Make your CLI "agent-friendly" by following 3 simple rules:

### 1. Add an `--agent` flag

```bash
$ mytool --agent input.txt
{"result": "success", "output": "processed"}
```

**Guarantees:**
- ✅ Non-interactive (never waits for user input)
- ✅ Structured output (JSON or JSON Lines to stdout)
- ✅ Structured errors (JSON to stderr)
- ✅ No decorations (no spinners, colors, or progress bars)

### 2. Use JSON Lines for lists

```bash
# Not a JSON array [...] which requires closing bracket
# Instead, one JSON object per line:

$ users list --agent
{"id":1,"name":"Alice","status":"active"}
{"id":2,"name":"Bob","status":"active"}
{"id":3,"name":"Charlie","status":"inactive"}
```

**Why?** Enables streaming, piping with `jq`, and processing before completion.

### 3. Document concisely

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

**Why?** Agents don't need verbose help. They need the 5 most common patterns.

---

## The Killer Feature: Composability

Because PAS tools output standard text/JSON, you can pipe them together:

### Example: "Find security issues, create GitHub tickets, notify Slack"

```bash
security-scan --agent . \
  | jq -c 'select(.severity == "high")' \
  | while read issue; do
      gh issue create \
        --title "Security: $(echo $issue | jq -r .title)" \
        --body "$(echo $issue | jq -r .description)" \
      | jq -r '.html_url' \
      | xargs -I {} slack-cli post \
          --channel security \
          --text "New critical issue: {}"
    done
```

**What just happened:**
1. `security-scan` finds issues (outputs JSON Lines)
2. `jq` filters for high severity (instant, free)
3. `gh` creates GitHub issues (uses existing GitHub CLI)
4. `slack-cli` posts to Slack (uses existing Slack CLI)

**Lines of custom integration code:** 0

Each tool:
- Does one thing well
- Knows nothing about the others
- Works with any future tool that follows the standard

---

## Integration with Agent Skills

PAS tools and Agent Skills (like Claude Code, agentskills.io) are **complementary** and work best together.

### The Pattern: Separation of Concerns

**PAS CLI Tools** answer:
- ✅ **WHAT** can this tool do?
- ✅ **HOW** do I use it?

**Agent Skills** answer:
- ✅ **WHEN** should I use this tool?
- ✅ **WHY** should I use it this way?
- ✅ **Opinionated workflows** and SOPs

### Example: Code Review

**❌ Bad: Bloated Skill (Duplication)**
```markdown
# Code Review Skill (900 lines)

## Tools
- eslint: Lints JavaScript
  - Usage: eslint [options] file.js
  - Options: --fix, --format json, --quiet
  - Exit codes: 0 (no issues), 1 (issues found)

- pytest: Runs Python tests
  - Usage: pytest [options] [path]
  - Options: -v, --json-report, -x
  - Exit codes: 0 (passed), 1 (failed)

## Workflow
1. Run eslint on changed files...
```

**✅ Good: Clean Skill (Workflow Only)**
```markdown
# Code Review Skill (50 lines)

## When to Use
Use when reviewing PRs or validating code changes.

## Workflow

1. Lint JavaScript/TypeScript files:
   ```bash
   git diff --name-only | grep '\.js$' | xargs eslint --agent
   ```

2. Run tests:
   ```bash
   pytest --agent tests/
   ```

**Policy:** Code fails review if ANY test fails.
**Opinion:** New TODOs are discouraged—create tickets instead.
```

### Why This Works

| Concern | Handled By | Benefit |
|---------|-----------|---------|
| Tool syntax & flags | CLI (`--agent --help`) | Single source of truth |
| Common usage patterns | CLI (`--agent --help`) | Tools self-document |
| Company policies | Skill | Encodes business logic |
| Workflow orchestration | Skill | Focus on procedure |
| Error handling | Both | CLI defines codes, Skill handles them |

### Token Economics

**Without separation:**
- Skill with embedded tool docs: ~900 lines
- Agent loads all upfront: ~2000 tokens

**With separation:**
- Skill (workflow only): ~50 lines
- Tools consulted just-in-time when needed
- Total initial load: ~120 tokens
- **Savings: 94%**

### Progressive Disclosure

```
Agent receives task: "Review this PR"
    ↓
Loads skill (50 lines, ~120 tokens)
    ↓
Skill says: "Run eslint --agent on changed files"
    ↓
Agent needs details → Runs: eslint --agent --help
    ↓
Gets concise docs (20 lines, ~50 tokens)
    ↓
Executes command
    ↓
Continues workflow
```

**Key insight:** Tools loaded **only when needed**, not upfront.

### Reusability

With PAS tools as self-documenting primitives:

- **"Code Review" skill** → Uses `eslint --agent`
- **"Pre-commit Check" skill** → Uses `eslint --agent`
- **"CI Pipeline" skill** → Uses `eslint --agent`

**Result:** Zero duplication. eslint documents itself once via `--agent --help`.

**[📖 Read the complete Skills guide →](./SKILLS.md)**

---

## MCP Integration: Remote Services, Not Local Wrappers

PAS and MCP (Model Context Protocol) are **complementary**, not competing. The key distinction:

- ❌ **Local MCP servers** = Unnecessary overhead (wrapping local tools)
- ✅ **Remote MCP servers** = Valuable standardization (accessing external SaaS, APIs)
- ✅ **PAS CLIs** = Bridge between agents and remote MCP

### The Architecture

```
┌─────────────┐
│   Agent     │
└──────┬──────┘
       │
       ├─→ Local tools (git, npm, docker)    [PAS CLIs]
       │
       └─→ Remote services (GitHub API,       [Remote MCP]
           Slack, Jira, external APIs)
                    ↓
           Accessed via PAS-compliant
           CLI tools (murl, custom CLIs)
```

### Using `murl` for Remote MCP Access

[`murl`](https://github.com/turlockmike/murl) is a PAS-compliant CLI that talks to remote MCP servers:

```bash
# List tools on a remote MCP server
$ murl https://remote.mcpservers.org/fetch/mcp/tools

# Call a remote tool with arguments
$ murl https://remote.mcpservers.org/fetch/mcp/tools/fetch \
  -d url=https://example.com

# Agent-friendly: outputs pure JSON
$ murl --help
# Shows: curl-like interface for MCP servers
```

**The pattern:**
- Agent runs: `murl <remote-mcp-url>/tools/my_tool -d arg=value`
- `murl` handles MCP protocol translation
- Agent receives structured JSON response
- No local server needed

### Custom PAS CLIs for External Services

You can also write your own PAS-compliant wrappers:

```bash
#!/bin/bash
# github-api - PAS CLI wrapping GitHub API

if [ "$1" = "--agent" ]; then
    # Machine mode: call GitHub API, return JSON
    gh api "$2" --jq '.'
else
    # Human mode: pretty output
    gh api "$2" | jq .
fi
```

**Usage:**
```bash
# Agent uses it like any other PAS tool
$ github-api --agent /repos/owner/repo/issues
[{"id": 1, "title": "Bug report"}, ...]

# Or use existing gh CLI directly
$ gh issue list --json id,title
```

### Why This Replaces Local MCP Servers

**Before (Local MCP Server):**
```python
# weather_mcp_server.py - 250 lines
from mcp import Server

@server.tool(name="get_weather")
def get_weather(city: str):
    response = requests.get(f"api.weather.com/{city}")
    return response.json()

# Must run continuously: python weather_mcp_server.py
# Agent connects to: http://localhost:8080
```

**After (PAS CLI + Remote MCP):**
```bash
# Option 1: Direct PAS CLI (28 lines)
$ weather --agent --city Boston
{"temp": 45, "condition": "Cloudy"}

# Option 2: Remote MCP via murl
$ murl https://weather.mcpserver.com/mcp/tools/get_weather \
  -d city=Boston
{"temp": 45, "condition": "Cloudy"}
```

**Result:**
- ✅ No local server to maintain
- ✅ No port conflicts
- ✅ No "is the server running?" debugging
- ✅ Works with standard Unix pipes

### When to Use What

| Scenario | Solution |
|----------|----------|
| Local tool (git, docker, npm) | **PAS CLI** (just add `--agent` flag) |
| External SaaS (GitHub, Slack) | **Existing CLI** (gh, slack-cli) with `--agent` |
| Remote MCP server | **`murl`** (PAS-compliant MCP client) |
| Custom integration | **Write PAS CLI** that calls external API |
| Truly custom logic | **Remote MCP server** (not local) + murl |

### Example: GitHub Integration

**Bad (Local MCP Server):**
```bash
# Start local wrapper
$ python github_mcp_server.py &  # Port 8080

# Agent connects via MCP protocol
agent.call_tool("create_issue", {"title": "Bug", "body": "..."})
```

**Good (PAS CLI):**
```bash
# Direct CLI usage
$ gh issue create --agent --title "Bug" --body "..." --json url
{"url": "https://github.com/owner/repo/issues/123"}

# Or custom wrapper
$ github-cli --agent create-issue --title "Bug" --body "..."
```

### Key Insight

**Local MCP servers add complexity without benefit.** If you can write a local MCP server, you can write a simpler PAS CLI instead.

**Remote MCP servers provide value:** They standardize access to external services you don't control. Access them via `murl` or custom PAS CLIs—not by running your own local MCP server.

---

## Quick Start

### For Tool Builders

**Add agent mode to your existing CLI in 5 minutes:**

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
```

**That's it.** Your tool is now agent-compatible.

### For Agent Builders

**Stop building MCP wrappers:**

```diff
- # Old: Custom wrapper
- @mcp_tool(name="check_weather")
- def check_weather(city: str) -> dict:
-     # 50 lines of wrapper code
-     ...

+ # New: Just use the CLI
+ result = subprocess.run(
+     ["weather", "--agent", "--city", city],
+     capture_output=True, text=True
+ )
+ data = json.loads(result.stdout)
```

**Measure the impact:**

```python
# Before: Custom tools
baseline_tokens = measure_agent("mcp_tools")

# After: POSIX tools
posix_tokens = measure_agent("bash_tools")

print(f"Token reduction: {(baseline - posix) / baseline * 100}%")
# Expected: 30-40% reduction
```

---

## Documentation

📘 **[Read the Manifesto](./MANIFESTO.md)** - The philosophy and evidence (15 min read)

📐 **[Read the Specification](./SPECIFICATION.md)** - Technical requirements for implementers (30 min read)

🔗 **[Skills Guide](./SKILLS.md)** - How PAS works with Agent Skills frameworks (20 min read)

🎯 **[See Examples](./examples/)** - Before/after comparisons and reference implementations

---

## FAQ

### Q: Doesn't this give agents dangerous access?

**A:** Safety comes from sandboxing, not limiting interfaces.

```bash
# Run agent in locked-down container
docker run --rm --network=none --read-only \
  -v $(pwd)/workspace:/work \
  agent-sandbox
```

Tools are equally dangerous via MCP or CLI. The difference: CLI calls are auditable plaintext.

### Q: What about Windows?

**A:** The principles are universal:
- PowerShell has pipes and exit codes
- JSON Lines works everywhere
- `--agent` is cross-platform

### Q: Is this actually part of the official POSIX standard?

**A:** No. PAS builds on POSIX, it doesn't replace it.

**The historical context:**

The original POSIX standard (IEEE 1003.1-1988) standardized the **interface**—pipes, flags, exit codes—but deliberately left the **data format** as unstructured text. This was intentional: POSIX was designed for human operators using interactive shells.

POSIX's only attempt at standardizing output was `LC_ALL=C` (the language locale), which ensured consistent language but not structured data. This was sufficient for humans reading terminal output, but insufficient for machine operators (agents) that need to parse results programmatically.

**Historical precedents:**

PAS isn't a novel idea—it's a formalization of concepts that have existed for decades:

- **FreeBSD's libxo (2014)**: Allowed tools to output XML/JSON via a flag, enabling structured logging while maintaining human-readable defaults. PAS adopts this "flag-switches-mode" pattern with `--agent`.

- **Plan 9's 9P protocol (1992)**: Treated everything—including network resources—as files with a standard interface. PAS Level 3-4 echo this philosophy: `ls`, `cat`, `stat` for remote resources.

**What PAS actually does:**

PAS completes POSIX by standardizing the **missing piece**: structured data interchange for machine operators.

| What POSIX Gave Us | What PAS Adds |
|-------------------|---------------|
| Pipes (`\|`) | Data format (JSON Lines) |
| Exit codes (0, 1, 2) | Semantic codes (100-125) |
| Flags (`--help`) | Agent mode (`--agent --help`) |
| Text streams | Structured streams |

**The relationship:**

```
POSIX (1988)          PAS (2025)
    ↓                     ↓
Interface         +   Data Format
(How to call)         (What you get)
    ↓                     ↓
        Combined = Agent-Native Unix
```

PAS doesn't replace POSIX—it respects every POSIX convention (pipes, exit codes, flags). It simply adds the standardization layer that enables machines to reliably parse what tools output.

**In other words:** POSIX told tools *how* to talk. PAS tells them *what language* to use when talking to machines.

### Q: Does this replace MCP?

**A:** It replaces **local** MCP servers, not remote ones.

**The distinction:**
- ❌ **Local MCP servers** = Unnecessary (use PAS CLIs instead)
- ✅ **Remote MCP servers** = Valuable (for external SaaS, accessed via [`murl`](https://github.com/turlockmike/murl) or custom PAS CLIs)

**Decision tree:**
```
Building a tool for LOCAL operations (git, docker, files)?
└─ Build a PAS-compliant CLI (NOT a local MCP server)

Need to access REMOTE services (GitHub API, Slack)?
├─ Does a CLI exist (gh, slack-cli)?
│  └─ Yes → Use it with --agent flag
└─ No CLI exists?
   ├─ Remote MCP server available?
   │  └─ Yes → Use murl to access it
   └─ No remote MCP?
      └─ Write custom PAS CLI that calls the API
```

**Key insight:** If you're running an MCP server on localhost, you're adding complexity. Just write a PAS CLI instead.

### Q: What about complex workflows?

**A:** Composition handles complexity:

```bash
# Multi-step workflow via pipes
validate-input.sh data.json \
  && process-data.sh data.json \
  && upload-results.sh results.json \
  || handle-error.sh $?
```

Each step is simple. The workflow is transparent.

---

## Get Involved

### ⭐ Star This Repo

Show support for the standard by starring [github.com/turlockmike/posix-agent-standard](https://github.com/turlockmike/posix-agent-standard)

### 🛠️ Adopt It

1. Add `--agent` flag to your CLI tools
2. Output JSON Lines for machine-readable data
3. Share your results (token savings, speed improvements)

### 💬 Join the Discussion

- **Issues:** Report problems or request clarifications
- **Discussions:** Share ideas and use cases
- **PRs:** Improve the spec and examples

### 📣 Spread the Word

If you found this useful:
- Share on Twitter/X with [#POSIXAgentStandard](https://twitter.com/search?q=%23POSIXAgentStandard)
- Write a blog post about your implementation
- Present at local meetups

---

## Contributing

This is an open standard. We welcome:

- 🐛 **Bug reports:** Found an issue? Open an issue
- 💡 **Feature proposals:** Have an idea? Start a discussion
- 📝 **Documentation:** Improve clarity or add examples
- 🧪 **Case studies:** Share your before/after results

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## Supporters

Organizations and projects implementing this standard:

- *(Your project here! Open a PR to add yourself)*

---

## License

This specification and documentation are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**You are free to:**
- ✅ Implement this standard in your tools (no attribution needed)
- ✅ Share and adapt this documentation (attribution required)

---

## Acknowledgments

Inspired by:
- The Unix Philosophy (Doug McIlroy, 1978)
- Vercel's agent optimization case study (2024)
- The [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- The [Agent Skills specification](https://agentskills.io/) community

---

## Contact

- **Specification Issues:** [GitHub Issues](https://github.com/turlockmike/posix-agent-standard/issues)
- **General Discussion:** [GitHub Discussions](https://github.com/turlockmike/posix-agent-standard/discussions)

---

<p align="center">
  <strong>Stop wrapping. Start shipping.</strong><br>
  The agents already know Unix. Let them use it.
</p>

<p align="center">
  <a href="./MANIFESTO.md">Read the Manifesto</a> •
  <a href="./SPECIFICATION.md">Read the Spec</a> •
  <a href="./examples/">See Examples</a>
</p>
