# buddyx-forge

[![Tests](https://github.com/sandiprv9898/buddyx-forge/actions/workflows/test.yml/badge.svg)](https://github.com/sandiprv9898/buddyx-forge/actions/workflows/test.yml)

Generate a complete multi-agent development system for any project. One command, 50+ files, ready to use.

Supports **7 frameworks**: Laravel, Next.js, React, Node.js, Django, Go, Rails.

## Why?

Without buddyx-forge, setting up Claude Code for a real project means manually writing CLAUDE.md rules, configuring settings.json permissions, creating agent definitions, building safety hooks, and figuring out how agents should coordinate — easily 2-3 hours of setup that most people skip entirely, leaving Claude working without guardrails.

**With buddyx-forge**, you answer 10 questions and get a production-ready system: domain-specialized agents that know your codebase structure, safety hooks that block destructive commands, a code review agent with framework-specific checklists, self-improving shared memory, and metrics tracking. The setup that took hours now takes 2 minutes.

**See what it generates:** Browse the [examples/](examples/) directory for complete Laravel and Django output.

## What is Multi-Agent Development?

Instead of one AI assistant handling everything, multi-agent splits the work into specialists:

- **Domain agents** know specific parts of your codebase (billing, auth, users). They own files and follow rules for their area.
- **Infrastructure agents** handle cross-cutting tasks — database inspection, code review, file discovery — without modifying code.
- **An orchestrator** reads your request, detects which domain it belongs to, and dispatches the right agent automatically.
- **Shared memory** lets agents learn from each other. When one agent discovers a pattern, others can use it too.

**Why does this work better?** Each agent has a focused context window. A billing agent doesn't waste tokens reading authentication code. A review agent has a framework-specific checklist, not generic advice. The result: faster, more accurate responses with domain expertise built in.

**What buddyx-forge does:** Generates all of this — agents, orchestrator, rules, hooks, memory — configured for your specific framework and project structure. You get a working multi-agent system in 2 minutes instead of building one from scratch.

## Real-World Examples

### Fix a bug

```
fix: PaymentService — returns 500 when amount is zero
```

What happens behind the scenes:
1. Orchestrator reads the request, detects "Payment" → **billing domain**
2. Dispatches `myapp-billing` agent (knows billing files, eager loading rules)
3. Agent reads `PaymentService.php`, finds the bug, applies fix
4. Orchestrator auto-dispatches `myapp-review` — checks for N+1 queries, security, code style
5. Review agent reports: PASS (0 violations)

### Audit before deploy

```
audit: all modules
```

1. Orchestrator sees "all" → dispatches `myapp-team-lead`
2. Team-lead dispatches all domain agents **in parallel** (max 5 at once)
3. Each agent audits its files — code quality, security, performance
4. Team-lead collects results → dispatches `myapp-review` for final check
5. You get a summary table: which modules passed, which have issues

### Cross-domain feature

```
add: export student grades as PDF with billing invoice attached
```

1. Orchestrator detects two domains: **students** + **billing** → dispatches `myapp-team-lead`
2. Team-lead dispatches `myapp-discovery` first (research phase, read-only)
3. Discovery agent finds relevant files, reports back
4. Team-lead dispatches `myapp-db` → checks schema for both tables
5. Dispatches domain agents sequentially (billing depends on student data)
6. Final `myapp-review` checks everything

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
| `/buddyx-forge:upgrade` | Upgrade setup to latest version, preserving customizations |
| `/buddyx-forge:export-config` | Export config as `.buddyx-forge.json` for team sharing |
| `/buddyx-forge:prompt-guide` | Interactive prompt engineering guide |
| `/buddyx-forge:reverse` | Reverse-engineer existing setup — explains every file |
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

## Prompt Engineering Tips

Write better prompts to get better results from your multi-agent system. Run `/buddyx-forge:prompt-guide` for the full interactive guide.

### The Formula

```
[action]: [location] — [what's wrong / what to do]. [scope limit].
```

### Good vs Bad Prompts

| Bad | Good | Why |
|-----|------|-----|
| `fix the login bug` | `fix: AuthController@login — returns 500 on uppercase emails` | Specific location + exact error |
| `the payment is broken` | `fix: PaymentService@charge — returns null when amount is 0. Should return zero-amount receipt.` | Current vs expected behavior |
| `add sorting to users` | `add: sortable columns to UserResource. Only touch the Resource file.` | Scope limit prevents over-engineering |
| `refactor billing` | `refactor: extract validation from BillingController into BillingRequest — match OrderRequest pattern` | References existing code pattern |
| `fix login, add export, refactor payments` | Send 3 separate prompts | One task per prompt = better agent routing |

### Power Modifiers

| Modifier | Example |
|----------|---------|
| `only touch [file]` | `fix: UserService — only touch app/Services/UserService.php` |
| `don't modify [file]` | `refactor: billing — don't modify migrations` |
| `show me before changing` | `add: caching to DashboardController — show me before changing` |
| `read only` | `check: auth module — read only, report issues` |
| `match [file] pattern` | `add: StudentExport — match InvoiceExport pattern` |
| `with tests` | `add: discount calculation — with tests` |

### Chain Prompts for Complex Work

```
1. explain: how does the payment webhook flow work? read only
2. diagram: payment flow from checkout to confirmation
3. add: retry logic to PaymentService@charge — max 3 retries with backoff
4. audit: payment module — focus on error handling
```

### Claude Code Official Tips

- **Use `@` to reference files** — `fix: @app/Services/PaymentService.php` gives Claude exact context
- **Let Claude interview you** for big features — start minimal, say "interview me about requirements first"
- **Interrupt anytime** — press Escape + Enter to course-correct mid-response
- **Start vague when exploring** — `what would you improve in this file?` surfaces unexpected issues
- **Avoid over-engineering** — add `no new files` or `keep it in the existing file` to prevent abstractions
- **Use CLI tools** — `gh`, `aws`, `gcloud` are more context-efficient than API calls

Run `/buddyx-forge:prompt-guide` for the full interactive guide with 7 sections, framework-specific examples, and practice mode.

> Sources: [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) | [Claude Prompting Guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

## How It Works Under the Hood

### Generation Flow

```
Your answers to 10 questions
        ↓
   Config JSON
        ↓
   Python Generator (7 modules, zero dependencies)
        ↓
   .claude/ directory (50-80 files)
        ↓
   Claude Code reads agents, rules, hooks automatically
```

### What Each Module Does

| Module | Input | Output |
|--------|-------|--------|
| `validators.py` | Config JSON | Validated config (rejects bad names, invalid enums, unsafe paths) |
| `builders/settings.py` | Config | `settings.json` — permissions, hooks, env vars |
| `builders/agents.py` | Config | Review agent + team-lead agent (framework-specific checklists) |
| `builders/rules.py` | Config | `CLAUDE.md` + `RULES.md` (framework rules, delegation table) |
| `builders/orchestrator.py` | Config | Orchestrator SKILL.md + domain-map.md |
| `builders/frameworks.py` | — | Framework maps: file extensions, discovery commands, DB tools, hookify rules |
| `generate.py` | All above | Orchestrates everything + renders templates + writes files |

### How Agent Routing Works

When you type a prompt, Claude Code reads:
1. **CLAUDE.md** — sees the delegation table, knows which agent handles which domain
2. **Orchestrator SKILL.md** — sees keyword-to-domain mapping and dispatch strategy
3. **Domain agent file** — sees the agent's tools, model, rules, and file ownership

```
"fix: PaymentService — bug"
     ↓
Claude reads CLAUDE.md → "Payment" matches billing domain
     ↓
Dispatches {name}-billing agent (owns billing files, knows framework rules)
     ↓
Agent reads RULES.md, reads its memory, fixes the bug
     ↓
Orchestrator auto-dispatches {name}-review agent
     ↓
Review agent checks: N+1? Security? Code style? → PASS/FAIL
```

### How Safety Hooks Work

Hook scripts run automatically before/after Claude uses tools:

```
Claude wants to run: rm -rf /var
     ↓
PreToolUse hook fires → safety-guard.sh
     ↓
Script checks: recursive delete on sensitive path? → BLOCKED
     ↓
Claude sees: "BLOCKED: Recursive delete on sensitive path."
```

| Hook | When | What It Blocks |
|------|------|---------------|
| `safety-guard.sh` | Before any Bash command | `rm -rf /`, `chmod 777`, dangerous patterns |
| `block-git-commit.sh` | Before any Bash command | `git commit`, `git push` (when commitPolicy=user) |
| `block-migration.sh` | Before Write/Edit | Migration files (when sharedDb is set) |
| `auto-format-new-files.sh` | After Write | Runs formatter on new files |
| `detect-new-file-created.sh` | After Write/Edit | Logs new files for domain-map updates |

### How Memory Works

```
Agent discovers pattern → writes to agent-memory/{name}/MEMORY.md
     ↓
Extract-learnings hook captures it → adds to shared-learnings.md as [NEW 0/3]
     ↓
Next agent encounters same pattern → confirms it → [NEW 1/3]
     ↓
After 3 confirmations → auto-promoted to [CONFIRMED]
     ↓
All agents now apply this pattern by default
```

Run `/buddyx-forge:reverse` to analyze your existing setup and see all of this in action.

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
Plugin (55+ files)
├── Generator: 7 Python modules (1,588 lines total, stdlib-only)
│   ├── generate.py — CLI + orchestration (436 lines)
│   ├── validators.py — config validation (68 lines)
│   └── builders/ — settings, agents, rules, orchestrator, frameworks
├── Templates: 10 agent + 11 hook + 4 skill templates
├── Commands: setup, quick, scan, health, add-domain, dashboard, upgrade, export-config, prompt-guide, reverse, dream
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

### v1.1.1 (2026-04-07)
- Split generator into 7 focused modules (was 1,541 lines in one file)
- Added `/buddyx-forge:upgrade` and `/buddyx-forge:export-config` commands
- Added "What is multi-agent?" and real-world examples to README
- Added GitHub Actions CI, issue templates, repo topics
- Added `--dry-run` to dream command, tempfile for setup config

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
