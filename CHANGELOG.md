# Changelog

All notable changes to buddyx-forge are documented here.

## [Unreleased]

## [1.1.1] - 2026-04-07

### Fixed
- **plugin.json missing 4 commands** — `upgrade`, `export-config`, `prompt-guide`, `reverse` now registered and discoverable by Claude Code
- **Version mismatch** — marketplace.json, plugin.json, and settings.py all synced to 1.1.1
- **next.js alias inconsistency** — `"next.js"` (with dot) now resolves identically to `"nextjs"` across all framework maps via `normalize_framework()`. Previously, auto-detected `"next.js"` silently fell through to Laravel defaults in FILE_EXT_MAP, SOURCE_DIR_MAP, DISCOVERY_COMMANDS_MAP, DB_TOOLS_MAP, and MAINTENANCE_COMMANDS_MAP
- **SharedDb path traversal** — `../` segments now blocked (previously `../../../etc/shadow` passed validation)
- **Global mutable `dry_run_count`** — replaced with `FileCounter` class passed through function arguments
- **Framework variable shadowing** — `framework` set once at top of `generate()` instead of re-read mid-function

### Added
- `normalize_framework()` helper — canonicalizes framework names (`"next.js"` → `"nextjs"`, `"node"` → `"nodejs"`)
- Framework validation — unsupported frameworks (e.g., `"flutter"`, `"spring-boot"`) now raise `ValueError` instead of silently defaulting to Laravel
- Hook config key validation — unknown keys (e.g., `"agentTracking"`) now produce a warning on stderr
- Safety guard blocks `curl | bash` supply chain attacks, `eval $(curl ...)`, and environment variable exfiltration via `curl`/`wget`
- `.editorconfig` for consistent formatting across editors
- 13 new tests covering: framework validation (3), hooks key warning (1), sharedDb path traversal (2), next.js alias consistency (3), normalize_framework (4). Test count: 47 → 60

### Changed
- Test config no longer includes deprecated `projectDir` and `agentTracking` keys
- Placeholder warning regex restored to uppercase-only (was incorrectly catching template examples like `{Module}`)

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
