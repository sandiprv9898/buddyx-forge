---
name: buddyx-forge
description: Multi-agent development system generator. Creates agents, hooks, skills, memory, and rules for any project. Supports Laravel, Next.js, Django, Go, Rails, React, Node.js.
user-invocable: false
---

# buddyx-forge

Multi-agent development system generator for any project.

## Commands

| Command | Description |
|---------|-------------|
| `/buddyx-forge:init` | **Start here** — Initialize new setup. Asks 10 questions, generates all files. |
| `/buddyx-forge:scan` | Re-scan codebase, update domain-map and context packs. |
| `/buddyx-forge:health` | Validate setup integrity, score 0-100. |
| `/buddyx-forge:add-domain` | Add a new domain agent to existing setup. |
| `/buddyx-forge:dashboard` | Open agent metrics dashboard in browser. |
| `/buddyx-forge:dream` | Memory consolidation — clean stale entries, promote hypotheses. |

## Quick Start

1. Run `/buddyx-forge:init` to set up
2. Run `/buddyx-forge:scan` to populate file lists
3. Run `/buddyx-forge:health` to verify (target: 100/100)
