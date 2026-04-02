# buddyx-forge

Generate a complete multi-agent development system for any project. One command, 50+ files, ready to use.

## Install

```
/plugin marketplace add sandiprv9898/buddyx-forge
/plugin install buddyx-forge
/reload-plugins
```

## Quick Start

```
/buddyx-forge:init
```

Follow the interactive setup (10 questions). The Python generator creates everything — no manual file creation needed.

## What It Creates

```
.claude/
  CLAUDE.md                 — Project rules + prompt templates
  AGENTS.md                 — Cross-tool agent config (Cursor, Copilot, Codex)
  settings.json             — Permissions, hooks, env flags
  agents/                   — Domain agents + 5 infrastructure agents
  skills/{project}/         — Orchestrator, rules, diagram, audit skills
  scripts/                  — Safety hooks + eval scripts
  agent-memory/             — Shared learnings + per-agent memory
  dashboard/                — Agent metrics
  hookify-rules.md          — Auto-generated hookify rules
```

## Supported Frameworks

| Framework | Detection | Rules |
|-----------|-----------|-------|
| **Laravel** + Filament | `composer.json` | Model conventions, eager loading, Filament forms |
| **Next.js** + Prisma | `package.json` | Server/Client components, App Router, TypeScript |
| **React** (Vite/CRA) | `package.json` | Hooks, React Query, functional components |
| **Node.js** (Express/Fastify/NestJS) | `package.json` | Service layer, Zod validation, error middleware |
| **Django** + DRF | `requirements.txt` | select_related, serializers, Celery |
| **Go** (Gin/Fiber/GORM) | `go.mod` | Error handling, goroutines, table-driven tests |
| **Rails** + Sidekiq | `Gemfile` | Services, strong params, RSpec |

## Commands

| Command | Purpose |
|---------|---------|
| `/buddyx-forge:init` | First-time setup — asks 10 questions, generates all files |
| `/buddyx-forge:scan` | Re-scan codebase, update domain-map + context packs |
| `/buddyx-forge:health` | Validate setup integrity (score 0-100) |
| `/buddyx-forge:add-domain X` | Add a new domain agent |
| `/buddyx-forge:dashboard` | Open agent metrics dashboard in browser |
| `/buddyx-forge:dream` | Memory consolidation — clean stale entries, promote hypotheses |

## Setup Questions

The `/buddyx-forge:init` command asks:

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

## Self-Improving System

- **Shared learnings** — agents write discoveries, confirmed after 3 verifications
- **Learning queue** — auto-captured from agent transcripts
- **Auto-promote** — hypotheses become rules after 3 confirmations
- **Dream mode** — `/buddyx-forge:dream` cleans stale memory, promotes hypotheses

## Requirements

- Python 3.8+
- jq (recommended, not required)
- Claude Code v2.1+

## Example Output

For a Laravel project with 3 domains (students, courses, grades):

```
buddyx-forge generated for 'school':
  Domains: students, courses, grades
  Agents: 3 domain + 5 infrastructure + 1 optional = 9
  Skills: orchestrator, rules, diagram, audit
  Hook scripts: 11
  Files created: 50
```

## License

MIT

## Author

Sandip Vanodiya
