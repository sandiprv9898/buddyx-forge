# Changelog

All notable changes to buddyx-forge are documented here.

## [Unreleased]

### Fixed
- Hookify rules no longer block migrations for solo Laravel projects (only when `sharedDb` is configured)
- `customize-guide.md` updated to match current generator workflow (no longer references removed Step 5)
- Health check (Check 12) now uses framework-appropriate scan paths instead of hardcoded `app/`
- Duplicate step numbering (`# 11.`) in generate.py
- `Write|Edit` hook matchers split into separate entries (pipe is not glob OR)
- Conservative permission level now includes framework commands in `ask` list
- Shell operator precedence bug in extract-learnings and auto-promote-learnings hooks
- Path containment checks use prefix match instead of substring match
- grep injection in auto-promote-learnings escaped
- `{RelevantTest}` placeholder replaced with `<TestName>` in domain agent template
- Agent templates no longer reference `block-git-commit.sh` when `commitPolicy=claude`
- Agent templates no longer reference `MEMORY.md` when `agentMemory=false`
- Optional agents (query-optimizer, mcp-dev, migration) now appear in orchestrator inventory
- Review agent description no longer claims auto-triggering
- Setup command description updated for all 7 frameworks
- README skill line counts corrected (audit: 862, diagram: 955)

### Added
- `LICENSE` file (MIT)
- `CONTRIBUTING.md` with framework addition guide
- `CHANGELOG.md` (this file)
- `buddyx-forge.example.json` — complete config reference
- `examples/` directory with generated output for Laravel and Django
- `buddyxForgeVersion: 1.1.0` stamp in generated `settings.json`
- `block-migration.sh.tmpl` — prevents migration creation in shared-DB projects
- `jq` availability checks in all hook scripts (fail-closed for safety, fail-open for informational)
- Enum validation for `modelBudget`, `permissionLevel`, `commitPolicy`, `evalLevel`
- `sharedDb` path sanitization against injection
- Plugin command declarations in `plugin.json`
- "Why?" section in README
- 6 framework-aware template variables (FILE_EXT_FILTER, DISCOVERY_COMMANDS, DB_TOOLS, etc.)
- Framework-specific hookify rules for Django, Go, Rails, JS/TS
- `flock` file locking in auto-promote-learnings hook
- AGENT_TYPE sanitization in all 6 eval hooks
- Conservative permission level includes framework commands in `ask` list

### Changed
- Safety guard expanded to cover more sensitive paths and chmod patterns
- Templates de-Laravelified — discovery, db, maintenance agents now framework-aware
- Audit skill consumes `{DOMAIN_LIST}` instead of hardcoded UMS HR modules
- Diagram skill uses `{PROJECT_TITLE}` instead of hardcoded "UMS HR System"
- Validate-agent-output hook only runs PHP checks for Laravel framework
- CLAUDE.md FQCN rule only included for Laravel
- RULES.md `$guarded`/`$fillable` rule only included for Laravel

## [1.1.0] - 2026-04-03

### Added
- Framework-aware permissions for all 7 frameworks
- Framework-aware scan paths in `/buddyx-forge:scan`
- 36 automated tests
- Tech stack plugin recommendations (67 plugins/MCP across 12 categories)
- Full audit skill (862 lines) and diagram skill (955 lines)
- Changelog in README

### Changed
- Generator creates ALL files (Option B) — no AI dependency for initial setup
- Renamed `/buddyx-forge:init` to `/buddyx-forge:setup`

## [1.0.0] - 2026-04-02

### Added
- Initial release
- 7 framework support: Laravel, Next.js, React, Node.js, Django, Go, Rails
- 10-question interactive setup
- Python generator (stdlib only, zero external dependencies)
- 5 infrastructure agents + domain agents + 3 optional agents
- 11 hook script templates
- Self-improving memory system
- Dry-run mode
- 6 commands: setup, scan, health, add-domain, dashboard, dream
