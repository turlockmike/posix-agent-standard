# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **POSIX Agent Standard (PAS)** repository - a specification and documentation project defining how CLI tools should work with AI agents. This is NOT a code implementation project; it's a standards documentation project similar to RFC documents.

**Key concept:** PAS advocates that instead of building custom MCP servers or API wrappers for agents, developers should make their CLI tools agent-friendly by adding an `--agent` flag that outputs structured JSON.

## Repository Structure

```
.
├── README.md              # Main landing page with 30-second pitch and examples
├── MANIFESTO.md           # Philosophy and evidence (the "why")
├── SPECIFICATION.md       # Technical requirements (the "what")
├── QUICKSTART.md          # 5-minute implementation guide
├── SKILLS.md              # How PAS works with Agent Skills frameworks
├── SHARING.md             # Distribution and marketing guide
├── CONTRIBUTING.md        # Contribution guidelines
└── examples/              # Before/after comparisons and reference implementations
    ├── weather/           # Weather tool comparison (MCP vs PAS)
    ├── user-management/   # User CRUD comparison
    ├── before-after/      # Token usage analysis
    └── reference-implementations/
        ├── word-counter.sh    # Complete PAS Level 2 example
        └── api-client.py      # Python reference implementation
```

## Document Hierarchy and Purpose

### Core Documents (Must Read for Understanding)
1. **README.md** - Entry point, contains the pitch and quick examples
2. **SPECIFICATION.md** - Authoritative technical standard (RFC 2119 style)
3. **MANIFESTO.md** - Deep dive into philosophy and case studies

### Supporting Documents
- **QUICKSTART.md** - Quick implementation patterns for developers
- **SKILLS.md** - How PAS complements Agent Skills (not replaces them)
- **SHARING.md** - How to distribute and promote PAS-compliant tools
- **CONTRIBUTING.md** - How to contribute to the standard

## Working with This Repository

### This is a Documentation Project
- There is **no build system** or test suite
- There is **no code to run** (except example scripts)
- Changes are primarily to Markdown files
- Focus is on clarity, consistency, and technical accuracy

### Key Concepts to Understand

1. **The `--agent` flag** - Global mode switch that makes CLI output machine-readable JSON
2. **JSON Lines (NDJSON)** - One JSON object per line (not an array) for streaming
3. **Conformance Levels** - Level 1 (minimum), Level 2 (recommended), Level 3 (navigation), Level 4 (state)
4. **PAS vs MCP** - PAS replaces *local* MCP servers, not remote ones
5. **PAS + Skills** - Skills provide workflow/policy, PAS tools provide capabilities

### Editing Guidelines

**When editing SPECIFICATION.md:**
- Use RFC 2119 keywords: MUST, SHOULD, MAY (consistently capitalized)
- Keep backward compatibility - breaking changes require major version bump
- Every requirement needs rationale and examples
- Test code examples for syntax correctness

**When editing README.md:**
- Maintain the "30-second pitch" clarity
- Keep token economics examples accurate (cite sources)
- Update version badges when SPECIFICATION.md versions change
- Ensure all internal links work

**When editing MANIFESTO.md:**
- Cite sources for claims (especially Vercel case study)
- Include concrete metrics when available
- Use examples liberally

**Common patterns:**
```bash
# Validate markdown rendering
open README.md  # (or your markdown preview tool)

# Check links work
grep -r "](\./" *.md  # Find all relative links

# Test example scripts
chmod +x examples/reference-implementations/word-counter.sh
./examples/reference-implementations/word-counter.sh --agent test.txt
```

### Version Control Conventions

**Commit message style (from git log):**
- Imperative mood: "Add section" not "Added section"
- Concise first line under 50 chars
- Focus on what changed, not why (unless non-obvious)
- Examples from history:
  - "Add PAS acronym to README title and key sections"
  - "Fix critical consistency issues identified in repository review"
  - "Apply --agent as global modifier architecture"

**Branch naming:**
- This repo uses `master` as main branch (not `main`)
- Create PRs against `master`

## Writing Style Guide

### Tone
- **Direct and technical** - This is a specification, not marketing copy
- **Evidence-based** - Claims need citations (especially performance numbers)
- **Unix philosophy** - Emphasize simplicity, composability, do-one-thing-well

### Formatting
- Use `**Bold**` for MUST/SHOULD/MAY keywords in specs
- Use `code` formatting for commands, flags, filenames
- Use triple backticks with language tags for code blocks
- Use tables for comparisons (before/after, metrics)

### Examples Are Critical
Every concept should have:
1. A code example showing usage
2. Explanation of why it works this way
3. Common patterns or anti-patterns

## Common Tasks

### Adding a New Example
1. Create directory under `examples/`
2. Include both "before" (MCP/wrapper) and "after" (PAS) versions
3. Add README.md with side-by-side comparison and metrics
4. Update `examples/README.md` to link to new example

### Clarifying a Specification Section
1. Read related sections for consistency
2. Check if there are already examples demonstrating it
3. Add concrete code examples
4. Consider if this should be in QUICKSTART.md too

### Responding to Issues/PRs
- Assume good faith - many contributors are new to standards work
- Ask for concrete examples when requirements are vague
- Point to existing patterns in the spec
- Consider backward compatibility impact

## Key Technical Details

### What Makes a Tool "PAS-Compliant"?
- **Level 1 (minimum):** Has `--agent` flag, non-interactive, structured errors
- **Level 2 (recommended):** Level 1 + JSON Lines output + semantic exit codes
- **Level 3:** Level 2 + navigation verbs (ls, cat, stat) for remote resources
- **Level 4:** Level 3 + state verbs (cp, rm, sync, mount)

### Semantic Exit Codes
- `0` - Success
- `1` - General error
- `2` - Invalid usage (bad flags/arguments)
- `100-125` - Tool-specific semantic errors (e.g., 100=FILE_NOT_FOUND)

### JSON Lines vs JSON Arrays
**Bad (JSON array):**
```json
[{"id":1},{"id":2}]  // Requires closing bracket, can't stream
```

**Good (JSON Lines):**
```json
{"id":1}
{"id":2}
```
Reason: Pipes, streaming, `jq` processing line-by-line

## Reference Links

- Model Context Protocol (MCP): https://modelcontextprotocol.io/
- Agent Skills spec: https://agentskills.io/
- Vercel case study: Referenced in MANIFESTO.md (Dec 2024 blog post)
- murl (MCP client): https://github.com/turlockmike/murl

## Things to Avoid

- **Don't add example implementations without clear metrics** - Every example should show quantitative improvement
- **Don't propose breaking changes lightly** - This affects all implementers
- **Don't duplicate content across files** - Use cross-references instead
- **Don't add dependencies** - This is a documentation repo, keep it simple
- **Don't inflate numbers** - The 95% token savings is *theoretical maximum*, Vercel saw 30-40% real-world

## Project Status

- **Version:** 0.1.0-draft
- **Status:** Request for Comments (RFC)
- **Stability:** Specification is in draft; breaking changes possible before 1.0
- **License:** CC BY 4.0 (documentation), implementations can use any license

## Getting Help

- Read SPECIFICATION.md first for technical questions
- Read MANIFESTO.md for philosophical questions
- Check examples/ for implementation patterns
- Open GitHub Discussion for design questions
- Open GitHub Issue for bugs/inconsistencies in the spec
