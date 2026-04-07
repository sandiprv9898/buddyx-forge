# buddyx-forge — Status Tracker

Last updated: 2026-04-07

## What Was Done (v1.1.0 → v1.1.1)

### Deep Audit (3 rounds, 13 agents)
- 93 findings identified across code quality, security, architecture, templates, docs, and cross-component interactions
- 47+ findings fixed and verified

### Phase 1: Critical Fixes (P0)
| ID | Issue | Status |
|----|-------|--------|
| P0-01 | Safety-guard rm patterns too narrow | Fixed |
| P0-02 | AGENT_TYPE path traversal in eval hooks | Fixed |
| P0-03 | FORMATTER_CMD shell injection | Fixed |
| P0-04 | jq dependency inconsistent across hooks | Fixed |
| P0-05 | modelBudget KeyError crash | Fixed |
| P0-06 | Dashboard EVENTS_DATA always empty | Fixed |
| P0-07 | No atomic generation / rollback | Deferred (v1.2) |
| P0-08 | block-migration.sh missing | Fixed |
| P0-09 | commitPolicy=claude agents reference missing script | Fixed |
| P0-10 | permissionLevel unvalidated | Fixed |
| P0-11 | commitPolicy unvalidated | Fixed |
| P0-12 | Shell operator precedence bug | Fixed |
| P0-13 | Django scan find command AND logic | Fixed |
| P0-14 | autoFormat + empty formatter executes file | Fixed |
| P0-15 | Write|Edit matcher never fires | Fixed |
| P0-16 | Conservative permissions skip framework commands | Fixed |
| P0-17 | XSS in dashboard + audit HTML | Fixed |
| P0-18 | Path containment substring bypass | Fixed |
| P0-19 | grep injection in auto-promote | Fixed |

### Phase 2: Framework Generalization (P1)
| ID | Issue | Status |
|----|-------|--------|
| P1-01 | audit-skill.tmpl hardcoded UMS HR modules | Partially fixed (DOMAIN_LIST consumed, 21 deep interior refs remain) |
| P1-02 | diagram-skill.tmpl "UMS HR System" | Fixed |
| P1-03 | auto-format .php filter | Fixed |
| P1-04 | detect-new-file PHP + app/ filter | Fixed |
| P1-05 | agent-discovery Laravel paths | Fixed |
| P1-06 | $guarded/$fillable in all RULES.md | Fixed |
| P1-07 | customize-guide.md Laravel-only | Fixed (full rewrite) |
| P1-08 | Race condition in auto-promote (no flock) | Fixed |
| P1-09 | {RelevantTest} placeholder leak | Fixed |
| P1-10 | Silent overwrite of existing files | Deferred (v1.2) |
| P1-11 | sharedDb path unvalidated/unquoted | Fixed |
| P1-12 | agentMemory=false agents reference MEMORY.md | Fixed |
| P1-13 | Optional agents missing from orchestrator | Fixed |
| P1-14 | Review agent claims "auto-trigger" | Fixed |
| P1-17 | Stale "AI customization" message | Fixed |
| P1-18 | setup.md says "Laravel projects" | Fixed |
| P1-19 | README skill line counts wrong | Fixed |
| P1-20 | Phantom agentTracking config key | Fixed |
| P1-21 | projectDir in config schema | Fixed |
| P1-22 | agent-db.tmpl Laravel Boost MCP | Fixed |
| P1-23 | agent-maintenance.tmpl PHP paths | Fixed |
| P1-24 | validate-agent-output PHP-only rules | Fixed |
| P1-25 | CLAUDE.md PHP FQCN rule all frameworks | Fixed |
| P1-26 | hookify-rules.tmpl Laravel rules | Fixed |
| P1-27 | plugin.json missing commands | Fixed |

### Phase 3: Prompt Quality Improvements
| ID | Issue | Status |
|----|-------|--------|
| PQ-01 | Domain agent empty "Your Files" section | Fixed (glob hints) |
| PQ-02 | Memory paths use generic `<agent>` literal | Fixed (agent-specific) |
| PQ-03 | migration + mcp-dev hardcoded memory | Fixed |
| PQ-04 | Review agent doesn't identify changed files | Fixed (git diff step) |
| PQ-05 | Team-lead no output format | Fixed (summary table) |
| PQ-06 | Orchestrator role unclear | Fixed (documented as routing table) |
| PQ-07 | Empty test runner = silent broken step | Fixed (guard added) |
| PQ-08 | Query-optimizer Debugbar-only | Fixed (framework fallbacks) |
| PQ-09 | Maintenance "refresh context" no procedure | Fixed (step-by-step) |

### New Files Created
| File | Purpose |
|------|---------|
| LICENSE | MIT license (legally required) |
| CONTRIBUTING.md | Framework addition guide |
| CHANGELOG.md | Standalone changelog |
| Roadmap.md | Prioritized improvement roadmap |
| STATUS.md | This file |
| buddyx-forge.example.json | Example config |
| examples/README.md | Examples documentation |
| examples/laravel-example/ | Full Laravel generated output (50 files) |
| examples/django-example/ | Full Django generated output (47 files) |
| plugins/buddyx-forge/commands/quick.md | Zero-question auto-setup |
| plugins/buddyx-forge/templates/hooks/block-migration.sh.tmpl | Migration blocking hook |
| plugins/buddyx-forge/commands/upgrade.md | Upgrade command — preserves memory + customizations |
| plugins/buddyx-forge/commands/export-config.md | Export config for team sharing |
| plugins/buddyx-forge/scripts/validators.py | Config validation module (split from generate.py) |
| plugins/buddyx-forge/scripts/builders/ | Builder modules: settings, agents, rules, orchestrator, frameworks |
| .github/workflows/test.yml | GitHub Actions CI — runs tests on Python 3.8/3.10/3.12 |
| .github/ISSUE_TEMPLATE/ | Bug report, feature request, framework request templates |

### Tests
- Original: 36 tests
- Current: 47 tests
- Coverage added: enum validation, conservative permissions, hookify migration, version stamp, sharedDb validation

---

## Remaining Issues (To Fix)

### Quick Fixes — ALL DONE

| # | Issue | Status |
|---|-------|--------|
| QF-01 | Domain agent shared-learnings ref when agentMemory=false | Fixed (conditional MEMORY_AFTER_DOMAIN) |
| QF-02 | Discovery agent shared-learnings ref when agentMemory=false | Fixed (uses MEMORY_WRITE_INFRA) |
| QF-03 | Review agent `.php` in output format | Fixed (generic `<file-path>`) |
| QF-04 | Discovery grep hits .git/vendor/node_modules | Fixed (--exclude-dir added) |
| QF-05 | agent-db `{TableName}` curly braces | Fixed (uses `<TableName>`) |

### Audit Skill Rewrite — DONE

| # | Issue | Status |
|---|-------|--------|
| AS-01 | Laravel/PHP refs in audit-skill.tmpl | Fixed — reduced from 862 to 703 lines, replaced JSON example block with generic skeleton, replaced PHP-specific steps with framework-agnostic versions, added note that text examples are illustrative. 26 refs remain in teaching examples (annotated). |

### Remaining v1.2 Features

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| V12-01 | `/buddyx-forge:upgrade` command — preserve memory, merge hooks, show diff | Done | — |
| V12-02 | `/buddyx-forge:export-config` — shareable team config | Done | — |
| V12-03 | Atomic generation (temp dir + rollback) | High | 2-3 hours |
| V12-04 | Split generate.py into modules | Done | — |
| V12-05 | Security audit agent | Medium | 2-3 hours |
| V12-06 | Test writer agent | Medium | 2-3 hours |
| V12-07 | Auto model routing (Haiku for reads, Opus for complex) | Medium | 2-3 hours |
| V12-08 | `--demo` flag for preview generation | Low | 1 hour |
| V12-09 | `--dry-run` for dream command | Done | — |
| V12-10 | Use tempfile for config instead of predictable /tmp path | Done | — |

### Adoption / Marketing (from competitive research)

| # | Action | Priority |
|---|--------|----------|
| MK-01 | Add GitHub description + topics | Done |
| MK-02 | Create GitHub release tag v1.1.1 | Done |
| MK-03 | Record GIF/video of setup flow | This week |
| MK-04 | Write "What is multi-agent?" README section | Done |
| MK-05 | Add use-case stories to README | Done |
| MK-06 | Write blog post / dev.to article | This month |
| MK-07 | Post in Claude Code community | This month |
| MK-08 | Set up GitHub Actions CI | Done |
| MK-09 | Add GitHub issue templates | Done |

---

## Competitive Position

| Feature | buddyx-forge | oh-my-claudecode (2.6k stars) | Claude Flow (12.9k stars) |
|---------|-------------|-------------------------------|--------------------------|
| Framework-specific agents | 7 frameworks | Generic | Generic |
| Domain file ownership | Yes | No | No |
| Safety hooks (11) | Yes | Basic | No |
| Self-improving memory | Yes (3-confirm) | Auto-learner | Shared memory |
| Zero-config setup | `/quick` command | `/omc-setup` | Complex |
| Parallel execution | No | 5 modes | Pipeline |
| Auto model routing | Manual (3 tiers) | Automatic | Manual |
| Stars | New | 2.6k | 12.9k |

**Unique strengths:** Framework knowledge, domain ownership, safety hooks, memory system
**Biggest gaps:** No parallel execution, no auto model routing

