# PAS + Agent Skills: Better Together

## The Integration Pattern

The POSIX Agent Standard (PAS) and Agent Skills (like those in Claude Code or agentskills.io) are **complementary abstractions** that solve different problems:

- **PAS CLI Tools** = "Here's WHAT I can do and HOW to use me"
- **Agent Skills** = "Here's WHEN to use tools and WHY, plus opinionated workflows"

When combined, you get both **capability** (tools) and **procedural knowledge** (skills) without duplication or complexity.

---

## The Problem: Duplication

### Without This Pattern (❌ Antipattern)

Many agent frameworks today conflate two distinct concerns:

**Skill File (Bloated):**
```markdown
# Code Review Skill

## Overview
This skill helps review code changes.

## Tools Available
- `eslint`: Lints JavaScript code
  - Usage: `eslint [options] file.js`
  - Options:
    - `--fix`: Auto-fix issues
    - `--format json`: Output JSON
    - `--quiet`: Only report errors
  - Exit codes:
    - 0: No issues
    - 1: Issues found
    - 2: Fatal error

- `pytest`: Runs Python tests
  - Usage: `pytest [options] [path]`
  - Options:
    - `-v`: Verbose output
    - `--json-report`: JSON output
    - `-x`: Stop on first failure
  - Exit codes:
    - 0: All tests passed
    - 1: Tests failed

## Workflow
1. Run eslint on changed files
2. Run pytest on test files
3. If both pass, approve
4. If either fails, suggest fixes
```

**Problems:**
- 🔴 **Duplication:** Tool usage instructions should live in the tool itself (`eslint --help`)
- 🔴 **Maintenance burden:** Every flag change requires updating the skill
- 🔴 **Token waste:** Agent loads tool docs it doesn't need yet
- 🔴 **Fragility:** Skill breaks when tool updates

---

## The Solution: Separation of Concerns

### PAS CLI Tools (Self-Documenting)

Build your CLI tools to be **self-documenting** following PAS:

**eslint (built-in tool with `--agent --help` added):**
```bash
$ eslint --agent --help
USAGE:
  eslint [--agent] [--fix] <file...>

COMMON PATTERNS:
  eslint --agent file.js                    # Check one file
  eslint --agent --fix src/**/*.js          # Fix all issues
  git diff --name-only | grep '\.js$' | xargs eslint --agent

ERROR CODES:
  0   No issues
  1   Issues found
  2   Fatal error (invalid config, etc.)

ANTI-PATTERNS:
  eslint file.js           # Use --agent for machine-readable output
```

**pytest (with PAS compliance):**
```bash
$ pytest --agent --help
USAGE:
  pytest [--agent] [path]

COMMON PATTERNS:
  pytest --agent tests/                     # Run all tests
  pytest --agent -x tests/                  # Stop on first failure
  pytest --agent --json-report tests/       # JSON output

ERROR CODES:
  0   All passed
  1   Some failed
  5   No tests found

ANTI-PATTERNS:
  pytest -v tests/         # Use --agent for structured output
```

### Agent Skill (Workflow-Focused)

Now your skill file can focus on **procedural knowledge**:

**`code-review.skill.md` (Clean):**
```markdown
---
name: code-review
description: Review code changes following team standards
---

# Code Review Workflow

## When to Use
Use this when asked to review code, check a PR, or validate changes.

## Standard Operating Procedure

### 1. Identify Changed Files
```bash
# Get list of modified files
git diff --name-only HEAD~1
```

### 2. Lint Code (JavaScript/TypeScript)
```bash
# Run eslint on changed JS/TS files
git diff --name-only HEAD~1 | grep -E '\.(js|ts)x?$' | xargs eslint --agent
```

**Important:** If eslint returns exit code 1, issues exist but can be auto-fixed.
Try running with `--fix` flag before rejecting the PR.

### 3. Run Tests
```bash
# Run all tests in agent mode
pytest --agent tests/
```

**Policy:** Code review fails if ANY test fails (exit code 1).

### 4. Check for TODOs
```bash
# Find any new TODO comments
git diff HEAD~1 | grep -i '^\+.*TODO'
```

**Opinion:** New TODOs are discouraged. Suggest creating a ticket instead.

## Decision Tree

```
Changed files found?
├─ Yes → Continue
└─ No  → Skip review, note "No changes detected"

Linting passed (exit 0)?
├─ Yes → Continue
└─ No  → Can auto-fix?
   ├─ Yes → Suggest running with --fix
   └─ No  → Report issues, fail review

Tests passed (exit 0)?
├─ Yes → Continue
└─ No  → Report failures, fail review

New TODOs found?
├─ Yes → Warn (don't fail, but suggest tickets)
└─ No  → Continue

All checks passed → Approve
```

## Example Output Template

When review passes:
```
✅ Code review passed

Linting: No issues (0 errors, 0 warnings)
Tests: All 47 tests passed
TODOs: None found

Changes look good to merge.
```

When review fails:
```
❌ Code review failed

Linting: 3 errors, 2 warnings
Tests: 2 failed, 45 passed

Issues:
1. src/api.js:45 - Unused variable 'result'
2. tests/api.test.js - AssertionError: expected 200, got 404

Suggested fixes:
- Run: eslint --fix src/api.js
- Review API endpoint logic in api.js
```
```

---

## The Benefits

### For the CLI Tool (PAS-Compliant)

**Responsibilities:**
- ✅ Explain what it does
- ✅ Document flags and options
- ✅ Provide common usage patterns
- ✅ Define exit codes
- ✅ Warn about anti-patterns

**Benefits:**
- Used by humans directly (via `--agent --help`)
- Used by agents directly (via `--agent --help`)
- Used by ANY skill that needs it
- Updated independently of skills
- No duplication across skills

### For the Agent Skill

**Responsibilities:**
- ✅ Define WHEN to use tools
- ✅ Provide opinionated workflows
- ✅ Encode company/team policies
- ✅ Handle decision logic
- ✅ Format outputs

**Benefits:**
- Focused on procedure, not tool syntax
- Doesn't break when tool updates
- Easy to read and maintain
- Encodes business logic, not technical details

---

## Real-World Example

### Scenario: "Deploy to Production" Skill

#### The CLI Tools (PAS-Compliant)

**`docker` (existing tool):**
```bash
$ docker --agent --help
USAGE: docker [command] [options]
COMMON PATTERNS:
  docker build --agent -t myapp:latest .
  docker push --agent myapp:latest
  docker run --agent -d -p 8080:8080 myapp:latest
```

**`aws` (existing tool):**
```bash
$ aws --agent --help
USAGE: aws [service] [command] [options]
COMMON PATTERNS:
  aws ecs update-service --agent --cluster prod --service myapp
  aws ecs describe-services --agent --cluster prod --service myapp
```

**`slack-cli` (your custom PAS tool):**
```bash
$ slack-cli --agent --help
USAGE: slack-cli post [--agent] --channel <name> --text <message>
COMMON PATTERNS:
  slack-cli post --agent --channel deploys --text "Deploy started"
ERROR CODES:
  0   Success
  100 Channel not found
  101 Authentication failed
```

#### The Skill (Workflow Only)

**`deploy-prod.skill.md`:**
```markdown
---
name: deploy-prod
description: Deploy application to production following safety protocols
---

# Production Deployment Workflow

## Safety First

**CRITICAL:** This skill deploys to production. Always:
1. Verify current branch is `main`
2. Ensure all tests pass locally
3. Notify team in Slack BEFORE starting
4. Have rollback plan ready

## Prerequisites Check

```bash
# Verify on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
  echo "ERROR: Must be on main branch" >&2
  exit 1
fi

# Verify tests pass
pytest --agent tests/ || {
  echo "ERROR: Tests must pass before deploy" >&2
  exit 1
}
```

## Step 1: Notify Team

```bash
slack-cli post --agent \
  --channel deploys \
  --text "🚀 Production deploy starting for $(git rev-parse --short HEAD)"
```

**Policy:** Wait 30 seconds for team to respond before proceeding.

## Step 2: Build Container

```bash
# Build with commit SHA tag
SHA=$(git rev-parse --short HEAD)
docker build --agent -t myapp:$SHA .
docker tag --agent myapp:$SHA myapp:latest
```

**Important:** Always tag with commit SHA for rollback capability.

## Step 3: Push to Registry

```bash
docker push --agent myapp:$SHA
docker push --agent myapp:latest
```

## Step 4: Update ECS Service

```bash
aws ecs update-service --agent \
  --cluster prod \
  --service myapp \
  --force-new-deployment
```

**Note:** This triggers a rolling deployment. Old tasks remain until new ones are healthy.

## Step 5: Verify Deployment

```bash
# Wait 60 seconds for new tasks to start
sleep 60

# Check service status
aws ecs describe-services --agent \
  --cluster prod \
  --service myapp \
  | jq -r '.services[0].deployments[] | select(.status == "PRIMARY") | .runningCount'
```

**Success criteria:** runningCount should match desiredCount.

## Step 6: Notify Completion

```bash
slack-cli post --agent \
  --channel deploys \
  --text "✅ Production deploy complete for $(git rev-parse --short HEAD)"
```

## Rollback Procedure

If deployment fails:

```bash
# Get previous SHA from git
PREVIOUS_SHA=$(git rev-parse --short HEAD~1)

# Deploy previous version
aws ecs update-service --agent \
  --cluster prod \
  --service myapp \
  --task-definition myapp:$PREVIOUS_SHA

slack-cli post --agent \
  --channel deploys \
  --text "⚠️ Rollback to $PREVIOUS_SHA initiated"
```
```

---

## Key Insights

### 1. Progressive Disclosure

**Without PAS:**
```markdown
# Skill must include all tool docs upfront

## Tools
- docker: (300 lines of docs)
- aws: (500 lines of docs)
- slack-cli: (100 lines of docs)

## Workflow
(50 lines)

Total: ~950 lines loaded into agent context
```

**With PAS:**
```markdown
# Skill includes only workflow

## Workflow
(50 lines)

# Tools are consulted on-demand:
- Agent runs: docker --agent --help (if needed)
- Agent runs: aws ecs --agent --help (if needed)

Total: ~50 lines initially, tools loaded only when used
```

### 2. Maintenance Burden

**Without PAS:**
```
aws CLI adds new flag → Update skill documentation
docker updates output format → Update skill documentation
slack-cli changes authentication → Update skill documentation

Result: Constant maintenance, frequent breakage
```

**With PAS:**
```
aws CLI adds new flag → aws --agent --help reflects it automatically
docker updates output format → docker --agent handles it transparently
slack-cli changes authentication → slack-cli --agent --help explains new method

Result: Skills continue working, tools self-document
```

### 3. Reusability

**Without PAS:**
```
"Code Review" skill includes full eslint docs
"Pre-Commit Check" skill includes full eslint docs
"CI Pipeline" skill includes full eslint docs

Result: Duplication across 3 skills
```

**With PAS:**
```
eslint --agent --help is the single source of truth

"Code Review" skill: workflow for PR reviews
"Pre-Commit Check" skill: workflow for git hooks
"CI Pipeline" skill: workflow for GitHub Actions

Result: DRY (Don't Repeat Yourself)
```

---

## Best Practices

### 1. CLI Tools Should

✅ **DO:**
- Implement `--agent` flag for deterministic output
- Provide `--agent --help` with concise examples
- Use semantic exit codes
- Output structured data (JSON Lines)
- Document anti-patterns to avoid

❌ **DON'T:**
- Include workflow or business logic
- Make assumptions about when/why they're used
- Require reading a skill to understand basic usage

### 2. Skills Should

✅ **DO:**
- Define opinionated workflows
- Encode company/team policies
- Provide decision trees and error handling
- Reference tools by name, not by implementation
- Focus on the "why" and "when"

❌ **DON'T:**
- Duplicate tool documentation
- Hardcode tool syntax (let tools self-document)
- Break when tools update

### 3. Integration Pattern

```
Agent receives task
    ↓
Loads relevant skill (50-200 lines)
    ↓
Skill says: "Run docker build --agent"
    ↓
Agent needs details → Runs: docker build --agent --help
    ↓
Gets concise docs (20-30 lines)
    ↓
Executes command
    ↓
Continues with skill workflow
```

**Key:** Tools are consulted **just-in-time**, not loaded upfront.

---

## Migration Guide

### Step 1: Audit Your Skills

Identify sections that document tool usage:

```markdown
# BEFORE (antipattern)
## git Usage
git is a version control system.

Usage: git [command] [options]

Common commands:
- git status: Show working tree status
- git log: Show commit logs
  Options:
    --oneline: Compact output
    -n <number>: Limit to N commits
...
```

These sections should be **deleted** and replaced with tool references.

### Step 2: Make Tools PAS-Compliant

Add `--agent --help` to your custom tools:

```bash
#!/bin/bash
# deploy.sh

if [ "$1" = "--agent --help" ]; then
    cat << 'EOF'
USAGE: deploy.sh --agent --env <prod|staging>

COMMON PATTERNS:
  deploy.sh --agent --env staging
  deploy.sh --agent --env prod --skip-tests

ERROR CODES:
  0   Success
  1   Deployment failed
  2   Invalid environment
EOF
    exit 0
fi

# Rest of tool implementation...
```

### Step 3: Refactor Skills to Workflows

```markdown
# AFTER (correct pattern)

## Deployment Process

### 1. Verify Environment
Run `git status` to ensure working directory is clean.

**Policy:** Never deploy with uncommitted changes.

### 2. Run Deployment
```bash
deploy.sh --agent --env prod
```

**Important:** If exit code is 1, check logs. If exit code is 2, verify environment name.

### 3. Verify Success
Check application health endpoint:
```bash
curl -sf https://app.example.com/health | jq .
```

Expected: `{"status": "healthy"}`
```

---

## Example: Claude Code Skills

In **Claude Code** (or any skills framework), the pattern is:

### Your CLI Tool
```bash
# ~/.local/bin/analyze-pr

#!/bin/bash
# analyze-pr: GitHub PR analysis tool (PAS-compliant)

show_agent_help() {
    cat << 'EOF'
USAGE:
  analyze-pr --agent <pr-number>

COMMON PATTERNS:
  analyze-pr --agent 123                    # Analyze PR #123
  analyze-pr --agent --repo owner/repo 123  # Different repo

ERROR CODES:
  0   Analysis complete
  100 PR not found
  101 API rate limit
EOF
}

if [ "$1" = "--agent --help" ]; then
    show_agent_help
    exit 0
fi

# Tool implementation...
```

### Your Claude Code Skill
```markdown
<!-- ~/.claude/skills/pr-review/SKILL.md -->
---
name: pr-review
description: Review GitHub PRs following team standards
---

# PR Review Workflow

## Overview
Comprehensive review of GitHub pull requests.

## Process

### 1. Fetch PR Data
```bash
analyze-pr --agent {{PR_NUMBER}}
```

### 2. Review Checklist

**Must verify:**
- [ ] Tests pass
- [ ] No merge conflicts
- [ ] Follows style guide
- [ ] Has description

**Team policy:** PRs with >500 lines should be split.

### 3. Provide Feedback

Format feedback as:
```
## Summary
[Brief overview]

## ✅ Strengths
- [Good things]

## 🔧 Suggestions
- [Improvements]

## ❌ Required Changes
- [Blockers]
```
```

---

## Summary: The Golden Rule

> **CLI tools document capabilities. Skills document workflows.**

- **Tool:** "I can lint JavaScript. Run me with `--agent` flag. Exit 0 means no issues."
- **Skill:** "When reviewing code, always lint. If linting fails, try auto-fix. Our policy requires zero linting errors before merge."

**Together:** Agent has both the capability (tool) and the wisdom (skill) to use it correctly.

---

## Further Reading

- [POSIX Agent Specification](./SPECIFICATION.md) - How to build PAS-compliant tools
- [Agent Skills Specification](https://agentskills.io/specification) - How to structure skills
- [Examples](./examples/README.md) - Real PAS tools to learn from

---

**Questions about integration?** [Open an issue](https://github.com/turlockmike/posix-agent-standard/issues) or [start a discussion](https://github.com/turlockmike/posix-agent-standard/discussions).
