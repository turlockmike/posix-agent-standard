# Contributing to the POSIX Agent Standard

Thank you for your interest in improving the POSIX Agent Standard! This document outlines how you can contribute.

---

## Ways to Contribute

### 1. 🐛 Report Issues

Found something unclear, inconsistent, or broken?

**Before opening an issue:**
- Search existing issues to avoid duplicates
- Check if it's already addressed in unreleased changes

**When reporting:**
- Be specific about which section of the spec is problematic
- Provide concrete examples when possible
- Explain the impact (blocks implementation, causes confusion, etc.)

[Open an Issue →](https://github.com/turlockmike/posix-agent-standard/issues/new)

---

### 2. 💡 Propose Enhancements

Have an idea for improving the standard?

**Good proposals include:**
- **Problem statement:** What limitation does this address?
- **Proposed solution:** Concrete specification language
- **Rationale:** Why is this better than alternatives?
- **Backward compatibility:** How does this affect existing implementations?

**Example:**

> **Problem:** Tools often need to report progress for long operations, but the spec doesn't define a standard format.
>
> **Proposal:** Add section 5.3 "Progress Events" requiring JSON Lines format:
> ```json
> {"event":"progress","step":2,"total":10,"message":"Processing..."}
> ```
>
> **Rationale:** Standardizes what agents currently do ad-hoc.
>
> **Compatibility:** Purely additive; no breaking changes.

[Start a Discussion →](https://github.com/turlockmike/posix-agent-standard/discussions)

---

### 3. 📝 Improve Documentation

Help make the spec clearer, more accessible, or more comprehensive.

**Examples:**
- Fix typos, grammar, or unclear wording
- Add diagrams or visual aids
- Provide additional examples
- Translate to other languages
- Improve navigation or structure

**How to contribute:**
1. Fork the repository
2. Make your changes
3. Submit a pull request
4. Reference any related issues

---

### 4. 🧪 Share Case Studies

Implemented the standard? Share your results!

**What to include:**
- **Context:** What tool/agent did you build?
- **Before:** What was your previous approach? (lines of code, token usage, performance)
- **After:** What changed with PAS? (quantitative metrics preferred)
- **Lessons learned:** What worked well? What was challenging?

**Where to share:**
- Create a markdown file in `case-studies/`
- Include code snippets and metrics
- Link to your project if public

**Format:**
```markdown
# Case Study: [Tool Name]

**Author:** [Your Name/Company]
**Date:** [YYYY-MM-DD]
**Tool:** [Brief description]

## Before PAS
- Approach: [MCP server / custom wrapper / etc.]
- Lines of code: [X]
- Token overhead: [Y tokens]
- Performance: [Z seconds avg]

## After PAS
- Approach: [CLI with --agent flag]
- Lines of code: [X]
- Token savings: [Y%]
- Performance: [Z seconds avg]

## Results
- Speed improvement: [X%]
- Token reduction: [Y%]
- Other benefits: [...]

## Code Example
[Before/after code snippets]

## Lessons Learned
[Key takeaways]
```

[Add Your Case Study →](./case-studies/)

---

### 5. 🛠️ Build Reference Implementations

Create example tools that demonstrate the standard.

**Useful contributions:**
- Minimal "Hello World" PAS-compliant tool
- Complex tool showing advanced features (streaming, FUSE, etc.)
- Migration guide: converting existing MCP tool to PAS
- Testing utilities (conformance checker, etc.)

**Guidelines:**
- Keep examples focused and well-commented
- Include both the tool code and example usage
- Demonstrate best practices
- Test across platforms if possible

[Submit Example →](./examples/)

---

### 6. 🔬 Conduct Research

Help validate the standard's effectiveness.

**Research ideas:**
- Benchmark token efficiency (PAS vs. MCP vs. raw prompts)
- Measure agent success rates with different tool interfaces
- Study error handling patterns in real deployments
- Survey developers on implementation challenges

**How to contribute:**
- Design and run experiments
- Document methodology clearly
- Share raw data and analysis
- Propose spec changes based on findings

[Share Research →](./research/)

---

## Pull Request Process

### 1. Fork and Branch

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/spec
cd spec
git checkout -b feature/my-improvement
```

### 2. Make Changes

- **Specification changes:** Edit `SPECIFICATION.md`
- **Manifesto updates:** Edit `MANIFESTO.md`
- **Documentation:** Edit `README.md` or add files to `docs/`
- **Examples:** Add to `examples/` directory

### 3. Test Your Changes

**For specification text:**
- Ensure Markdown renders correctly
- Check all internal links work
- Verify code examples are syntactically correct

**For code examples:**
```bash
# Run your example
./examples/your-tool.sh --agent test-input

# Verify JSON output is valid
./examples/your-tool.sh --agent test-input | jq .

# Check error handling
./examples/your-tool.sh --agent invalid-input
echo "Exit code: $?"
```

### 4. Commit

```bash
git add .
git commit -m "Brief description of change

More detailed explanation if needed.
Fixes #123"
```

**Commit message guidelines:**
- Use imperative mood ("Add section" not "Added section")
- First line: 50 chars or less
- Reference issues: "Fixes #123" or "Relates to #456"

### 5. Push and Open PR

```bash
git push origin feature/my-improvement
```

Then open a pull request on GitHub.

**PR template:**
```markdown
## Summary
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- [ ] Updated SPECIFICATION.md section X
- [ ] Added example in examples/
- [ ] Updated README.md

## Testing
How was this verified?

## Checklist
- [ ] Markdown renders correctly
- [ ] Links work
- [ ] Code examples tested
- [ ] No typos or grammar errors
```

---

## Style Guide

### Markdown Formatting

**Headers:**
```markdown
# Top-level (document title)
## Section
### Subsection
#### Detail level
```

**Code blocks:**
````markdown
```bash
# Always specify language for syntax highlighting
command --flag value
```
````

**Lists:**
```markdown
- Use hyphens for unordered lists
- Keep items parallel in structure

1. Use numbers for sequential steps
2. Each step should be actionable
```

**Emphasis:**
```markdown
**Bold** for strong emphasis (requirements, warnings)
*Italic* for mild emphasis or introducing terms
`Code` for commands, flags, filenames
```

### Writing Style

**Clarity over cleverness:**
```markdown
# Good
The tool MUST output valid JSON.

# Avoid
The tool should, ideally, endeavor to output something resembling JSON.
```

**Be specific:**
```markdown
# Good
Set timeout to 30 seconds using --timeout 30

# Avoid
Set appropriate timeout
```

**Use examples:**
```markdown
# Good
Use semantic exit codes:
- 0: Success
- 1: General error
- 100: Resource not found

$ mytool --agent missing.txt
# exit code: 100

# Avoid
Use semantic exit codes where appropriate.
```

---

## Specification Changes

### Adding New Requirements

**Backward compatibility is critical.**

**Safe additions:**
- ✅ New optional features (Level 3)
- ✅ Clarifications that don't change behavior
- ✅ Additional examples

**Require discussion:**
- ⚠️ New mandatory requirements (Level 1)
- ⚠️ Changes to existing behavior
- ⚠️ Removal of optional features

**Breaking changes:**
- ❌ Avoid if at all possible
- ❌ Require major version bump
- ❌ Must provide migration guide

### Specification Language

Use RFC 2119 keywords consistently:

- **MUST** / **REQUIRED**: Absolute requirement
- **MUST NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: Strong recommendation, exceptions possible
- **SHOULD NOT**: Not recommended, but not prohibited
- **MAY** / **OPTIONAL**: Truly optional

**Example:**
```markdown
## 2.1 Output Format

Tools MUST emit valid JSON when in agent mode.

Tools SHOULD use JSON Lines for list outputs.

Tools MAY support additional output formats via --format flag.
```

---

## Review Process

### What Reviewers Look For

**For specification changes:**
- ✅ Clear and unambiguous language
- ✅ Consistent with existing requirements
- ✅ Implementable across platforms
- ✅ Includes rationale and examples
- ✅ Backward compatible (or justifies breaking change)

**For examples:**
- ✅ Code is correct and tested
- ✅ Demonstrates best practices
- ✅ Well-commented
- ✅ Includes usage examples

**For documentation:**
- ✅ Clear and accessible
- ✅ Free of jargon (or explains it)
- ✅ Accurate references
- ✅ Proper markdown formatting

### Typical Timeline

- **Small changes** (typos, clarifications): 1-3 days
- **Medium changes** (examples, new sections): 1-2 weeks
- **Large changes** (new requirements, breaking changes): 2-4 weeks

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment.

**We value:**
- Respectful disagreement
- Constructive feedback
- Diverse perspectives
- Collaborative problem-solving

**We do not tolerate:**
- Harassment or discrimination
- Personal attacks
- Unconstructive criticism
- Disruptive behavior

### Reporting Issues

If you experience or witness unacceptable behavior:
- **Public incidents:** Comment on the thread to de-escalate
- **Private concerns:** Email conduct@posix-agents.org *(placeholder)*

---

## Recognition

Contributors are recognized in several ways:

### Changelog
Significant contributions are credited in `CHANGELOG.md`:
```markdown
## v0.2.0 - 2026-03-15

### Added
- New section on progress events (@username)
- Python reference implementation (@username)
```

### Contributors File
All contributors are listed in `CONTRIBUTORS.md`:
```markdown
# Contributors

## Specification
- @username - Section 5 improvements
- @username - Error handling clarifications

## Examples
- @username - Weather tool reference implementation
```

### Case Studies
Authors are credited in their case study files and linked from README.

---

## Questions?

- **Specification questions:** [Open a discussion](https://github.com/turlockmike/posix-agent-standard/discussions)
- **Implementation help:** [Join our Discord](https://discord.gg/posix-agents) *(placeholder)*
- **Email:** hello@posix-agents.org *(placeholder)*

---

## Thank You!

Every contribution—whether it's fixing a typo, adding an example, or proposing a major enhancement—helps make AI agents more efficient and accessible.

**Let's build a better standard together.**

---

## Quick Links

- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Specification](./SPECIFICATION.md)
- [Manifesto](./MANIFESTO.md)
- [Examples](./examples/)
- [Issue Tracker](https://github.com/turlockmike/posix-agent-standard/issues)
- [Discussions](https://github.com/turlockmike/posix-agent-standard/discussions)
