# buddyx-forge

Generate a complete multi-agent development system for any project. One command, 50+ files, ready to use.

Supports **7 frameworks**: Laravel, Next.js, React, Node.js, Django, Go, Rails.

## Why?

Without buddyx-forge, setting up Claude Code for a real project means manually writing CLAUDE.md rules, configuring settings.json permissions, creating agent definitions, building safety hooks, and figuring out how agents should coordinate — easily 2-3 hours of setup that most people skip entirely, leaving Claude working without guardrails.

**With buddyx-forge**, you answer 10 questions and get a production-ready system: domain-specialized agents that know your codebase structure, safety hooks that block destructive commands, a code review agent with framework-specific checklists, self-improving shared memory, and metrics tracking. The setup that took hours now takes 2 minutes.

**See what it generates:** Browse the [examples/](examples/) directory for complete Laravel and Django output.

## Install

```
/plugin marketplace add sandiprv9898/buddyx-forge
/plugin install buddyx-forge
/reload-plugins
```

## Quick Start

```
/buddyx-forge:setup
```

Follow the interactive setup (10 questions). The Python generator creates everything — no manual file creation needed.

After setup:
```
/buddyx-forge:scan      # populate domain-map with real file paths
/buddyx-forge:health    # verify setup (target: 100/100)
```

## What It Creates

```
.claude/
  CLAUDE.md                 — Project rules + prompt templates
  AGENTS.md                 — Cross-tool agent config (Cursor, Copilot, Codex)
  settings.json             — Permissions, hooks, env flags (framework-aware)
  agents/                   — Domain agents + 5 infrastructure agents
  skills/{project}/         — Orchestrator, rules, diagram, audit skills
  scripts/                  — Safety hooks + eval scripts
  agent-memory/             — Shared learnings + per-agent memory
  dashboard/                — Agent metrics
  hookify-rules.md          — Auto-generated hookify rules
```

## Supported Frameworks

| Framework | Detection | Rules | Permissions |
|-----------|-----------|-------|-------------|
| **Laravel** + Filament | `composer.json` | Model conventions, eager loading, Filament forms | `php artisan`, `composer` |
| **Next.js** + Prisma | `package.json` | Server/Client components, App Router, TypeScript | `npx`, `node` |
| **React** (Vite/CRA) | `package.json` | Hooks, React Query, functional components | `npx`, `node` |
| **Node.js** (Express/Fastify/NestJS) | `package.json` | Service layer, Zod validation, error middleware | `npx`, `node` |
| **Django** + DRF | `requirements.txt` | select_related, serializers, Celery | `python manage.py`, `pip` |
| **Go** (Gin/Fiber/GORM) | `go.mod` | Error handling, goroutines, table-driven tests | `go build`, `go test` |
| **Rails** + Sidekiq | `Gemfile` | Services, strong params, RSpec | `bundle exec`, `rails` |

Each framework gets:
- Tailored review checklist for the code quality agent
- Framework-specific coding rules in RULES.md
- Correct file permissions in settings.json
- Appropriate scan paths for file discovery

## Commands

| Command | Purpose |
|---------|---------|
| `/buddyx-forge:setup` | First-time setup — asks 10 questions, generates all files |
| `/buddyx-forge:scan` | Re-scan codebase, update domain-map + context packs |
| `/buddyx-forge:health` | Validate setup integrity (score 0-100) |
| `/buddyx-forge:add-domain X` | Add a new domain agent |
| `/buddyx-forge:dashboard` | Open agent metrics dashboard in browser |
| `/buddyx-forge:dream` | Memory consolidation — clean stale entries, promote hypotheses |

## Setup Questions

The `/buddyx-forge:setup` command asks:

1. **Project name** — prefix for all agents (e.g., `myapp` → `myapp-auth`)
2. **Domains/modules** — auto-detected from codebase, you confirm
3. **Safety hooks** — block commits, dangerous commands, auto-format
4. **Shared database** — dual-project setup (creates migration agent)
5. **Who commits** — you or Claude
6. **Permission level** — conservative / balanced / permissive
7. **Agent memory** — shared learning system across sessions
8. **Prompt templates** — adds prompt guide to CLAUDE.md
9. **Observability** — agent metrics tracking (full / basic / none)
10. **Model budget** — budget (haiku) / balanced (haiku+sonnet) / quality (sonnet+opus)

## Agents Created

### Always Created (5 infrastructure)
| Agent | Purpose |
|-------|---------|
| `{name}-discovery` | Pre-implementation research (read-only) |
| `{name}-db` | Database schema inspection (read-only) |
| `{name}-review` | Code quality gate — runs after every change (read-only) |
| `{name}-team-lead` | Multi-agent coordinator for parallel tasks |
| `{name}-maintenance` | Refreshes domain-map and context packs |

### Per Domain (user-defined)
One agent per module/domain you specify. Each owns specific files and follows project rules.

### Optional (auto-detected)
| Agent | When Created |
|-------|-------------|
| `{name}-migration` | Shared database configured |
| `{name}-query-optimizer` | Laravel, Django, Rails, Next.js (ORMs) |
| `{name}-mcp-dev` | MCP servers configured or Node.js backend |

## Skills Generated

### Module Audit (703 lines)
Deep 11-section analysis of any domain module:
- DB Tables, Relationships, Data Lineage, Field Map
- Data Flow, Enums, Resources, Observers, Jobs, Policies
- Text output (default) or interactive HTML report with dark theme

```
audit billing
audit billing html
```

### Diagram Generator (955 lines)

Interactive HTML diagrams from codebase analysis:
- ER diagrams (custom HTML table cards)
- Flowcharts, Sequence, Architecture, State diagrams (Mermaid.js)

```
diagram: DB tables for billing module
diagram: payment flow from checkout to confirmation
```

## Self-Improving System

- **Shared learnings** — agents write discoveries, confirmed after 3 verifications
- **Learning queue** — auto-captured from agent transcripts
- **Auto-promote** — hypotheses become rules after 3 confirmations (`[NEW 0/3]` → `[CONFIRMED]`)
- **Dream mode** — `/buddyx-forge:dream` cleans stale memory, promotes hypotheses

## Plugin & MCP Recommendations

After setup, buddyx-forge recommends relevant plugins based on your tech stack:

- **Laravel**: laravel-boost MCP, php-lsp, context7
- **Next.js/React**: frontend-design, figma, playwright
- **Django**: PostgreSQL MCP, context7
- **Node.js**: postman, mcp-server-dev
- **Universal**: superpowers, coderabbit, hookify, security-guidance

67 plugins and MCP servers across 12 categories with quick install scripts.

## Daily Usage

After setup, just type your tasks naturally:

```
fix: InvoiceService — returns 500 when amount is zero. Only touch the service file.
add: PDF export to StudentResource — include date range filter.
audit: billing module — check code quality, security, permissions.
diagram: DB tables for student enrollment
```

The orchestrator auto-detects the domain and dispatches the right agent.

## Testing

Run the built-in test suite:

```bash
python3 tests/test_generator.py
```

47 tests covering: config validation, all 7 frameworks, optional agents, memory flags, framework-aware permissions, enum validation, conservative permissions, hookify migration rules, version stamp, sharedDb path validation.

## Requirements

- Python 3.8+ (stdlib only — zero external dependencies)
- jq (recommended, not required)
- Claude Code v2.1+

## Architecture

```
Plugin (48 files)
├── Generator: Python script (1,200+ lines, stdlib-only)
├── Templates: 10 agent + 11 hook + 4 skill templates
├── Commands: setup, scan, health, add-domain, dashboard, dream
├── References: detect-stack, customize-guide, 7 framework packs, tech-recommendations
└── Marketplace: plugin.json + marketplace.json

Generated Output (50-80 files per project)
├── CLAUDE.md — complete project rules (no AI placeholders)
├── RULES.md — framework-specific coding rules
├── Agents — domain + infrastructure + optional
├── Scripts — safety hooks + eval hooks
├── Skills — orchestrator, audit (703 lines), diagram (955 lines)
└── Memory — shared learnings + per-agent memory
```

## Example Output

For a Laravel project with 3 domains:

```
buddyx-forge generated for 'school':
  Domains: students, courses, grades
  Agents: 3 domain + 5 infrastructure + 1 optional = 9
  Skills: orchestrator, rules, diagram, audit
  Hook scripts: 11
  Files created: 50
```

## Changelog

### v1.1.0 (2026-04-03)
- Framework-aware permissions (Laravel, Django, Go, Rails, JS/TS)
- Framework-aware scan paths for all 7 frameworks
- Added 36 automated tests
- Added .gitignore, removed .pyc files
- Fixed plugin.json description (all frameworks, not just Laravel)
- Added tech-stack plugin recommendations (67 plugins/MCP across 12 categories)
- Ported full audit skill (703 lines) and diagram skill (955 lines) from battle-tested HR project
- Option B: generator creates ALL files (no AI dependency)
- Renamed /init to /setup to avoid conflict with built-in /init

### v1.0.0 (2026-04-02)
- Initial release
- 7 framework support, 10-question setup, Python generator
- 5 infrastructure agents + domain agents + 3 optional agents
- 11 hook script templates, memory system, self-improving learnings

## License

MIT

## Author

Sandip Vanodiya — [GitHub](https://github.com/sandiprv9898)
