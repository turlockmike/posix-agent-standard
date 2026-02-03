# PAS Builder Plugin

This directory contains the plugin metadata for distributing the PAS Builder skill via Claude Code's plugin marketplace.

## Plugin Structure

```
.claude-plugin/
├── plugin.json          # Plugin metadata
├── marketplace.json     # Marketplace configuration
└── README.md           # This file

.claude/skills/
└── pas-builder/        # The actual skill
```

## Installation

Users can install this plugin via:

```bash
# Add the marketplace
claude plugin marketplace add turlockmike/posix-agent-standard

# Install the plugin
claude plugin install pas-builder@posix-agent-standard
```

Or with the shorter command once the marketplace is added:

```bash
claude plugin install pas-builder
```

## What's Included

The plugin provides:
- **pas-builder skill** - Comprehensive guide for building PAS-compliant CLI tools
- **Template scripts** - Bash and Python templates ready to use
- **Reference documentation** - Complete specification and examples
- **Best practices** - Including how to build CLIs for skills

## Development

To test the plugin locally:

```bash
# Add as local marketplace
claude plugin marketplace add ./path/to/posix-agent-standard

# Install from local
claude plugin install pas-builder@posix-agent-standard
```
