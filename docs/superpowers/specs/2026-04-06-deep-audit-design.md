# buddyx-forge Deep Audit Report & Fix Plan

**Date:** 2026-04-06
**Scope:** Full deep audit across code quality, generated output, architecture, tests, docs, cross-component interactions, and template correctness
**Method:** 13 parallel specialized agents (3 rounds), plus manual test execution and edge-case config testing
**Test Results:** 36 PASS, 0 FAIL (all existing tests pass)

---

## Executive Summary

buddyx-forge is a well-conceived multi-agent system generator with strong foundations. However, the audit uncovered **93 unique findings** across three audit rounds — including issues that would cause hard runtime failures for users of non-Laravel frameworks or specific config flags.

**The #1 systemic issue:** The plugin was built and tested against Laravel first, and many templates, hooks, commands, and references still contain Laravel-specific hardcoding that was never generalized for the other 6 supported frameworks.

**The #2 systemic issue:** Config values (`modelBudget`, `permissionLevel`, `commitPolicy`) pass validation without value-level checks, causing silent wrong behavior or crashes on typos.

**The #3 systemic issue:** Several template variables (`DOMAIN_LIST`, `EXAMPLE_DOMAIN`) are computed but never consumed by their templates, while hardcoded project-specific content (UMS HR modules, "UMS HR System" strings) leaked into generic templates.

---

## Priority-Ranked Fix List

### P0 — CRITICAL: Hard runtime failures or security issues (14 findings)

| ID | Category | File(s) | Issue | Impact |
|----|----------|---------|-------|--------|
| P0-01 | Security | `safety-guard.sh.tmpl:14-19` | `rm -rf` pattern only blocks root `/` path. `rm -rf /var/www`, `rm -rf ~`, `rm -r -f` all bypass it. | False sense of safety; destructive deletions pass through unblocked |
| P0-02 | Security | `track-agent-start.sh.tmpl:17-20` | `AGENT_TYPE` from jq input used directly in `/tmp` file paths without sanitization — path traversal vector | Malicious hook input writes files to arbitrary paths |
| P0-03 | Security | `auto-format-new-files.sh.tmpl:26` | `FORMATTER_CMD` injected bare into shell without quoting — word-splitting/injection risk | Shell command injection on formatter values with spaces |
| P0-04 | Bug | All hook templates | `jq` missing: `block-git-commit.sh` blocks ALL bash (fails closed), but `safety-guard.sh` + all eval hooks silently pass through (fails open) — inconsistent | On systems without jq, safety hooks are disabled or bash is entirely blocked |
| P0-05 | Bug | `generate.py:286,949,1013` | `modelBudget` unvalidated value causes `KeyError` crash (bare dict lookup) | User typo crashes generator with confusing traceback |
| P0-06 | Bug | `dashboard.html.tmpl:46` | `EVENTS_DATA = []` is never populated. No `fetch()` call to load `events.jsonl`. Dashboard is completely non-functional. | Users see empty dashboard regardless of agent activity |
| P0-07 | Bug | `generate.py:generate()` | No atomicity — partial generation failure leaves corrupted `.claude/` directory. No rollback mechanism. | Broken half-generated setup with no recovery path |
| P0-08 | Bug | `generate.py:200-204` | `blockMigration=True` registers `block-migration.sh` in settings.json but no template exists and script is never generated | Every Write/Edit fails with script-not-found for shared-DB projects |
| P0-09 | Bug | `generate.py:1140-1143` + all agent templates | `commitPolicy=claude` skips generating `block-git-commit.sh`, but all agent templates unconditionally embed hooks pointing to it | Agents reference non-existent script; either silent failure or startup error |
| P0-10 | Bug | `generate.py:148-172` | `permissionLevel` value never validated. Unrecognized value silently produces empty permission lists (only `WebSearch` allowed) | Typo like "strict" silently locks agent out of all tools |
| P0-11 | Bug | `generate.py:192-199` | `commitPolicy` value never validated. Any value other than `"user"` (including typos like `"manual"`) grants Claude full git access | Typo silently gives Claude unrestricted git commit/push |
| P0-12 | Bug | `extract-learnings.sh.tmpl:14`, `auto-promote-learnings.sh.tmpl:14` | Shell `\|\|`/`&&` operator precedence bug: `[ -z "$X" ] \|\| [ "$X" = "null" ] && exit 0` — exit never fires on empty string | Scripts continue with empty input, may corrupt learning files |
| P0-13 | Bug | `commands/scan.md:52` | Django `find` command uses multiple AND-ed `-path` flags — always returns empty. Should use `-o` (OR). | Django project scans produce zero results; domain-map never populated |
| P0-14 | Bug | `generate.py:1145-1148` | `autoFormat=true` + empty `formatter` renders script that executes the target file as a command (`"$FILE_PATH"`) | Newly created files are executed instead of formatted |

### P1 — HIGH: Broken features or significantly wrong output (21 findings)

| ID | Category | File(s) | Issue |
|----|----------|---------|-------|
| P1-01 | Framework | `audit-skill.tmpl:29-44` | Hardcoded Laravel/PHP paths (`app/Filament/Resources/`, `mcp__laravel-boost__`), UMS HR module names. `{DOMAIN_LIST}` key passed but never consumed by template. |
| P1-02 | Framework | `diagram-skill.tmpl:169` | Hardcoded "UMS HR System" in HTML meta. Zero template placeholders consumed — `EXAMPLE_DOMAIN`, `PROJECT_NAME`, `PROJECT_TITLE` all silently ignored. |
| P1-03 | Framework | `auto-format-new-files.sh.tmpl:9-10` | Hardcodes `\.php$` filter — autoFormat is completely non-functional for non-PHP frameworks |
| P1-04 | Framework | `detect-new-file-created.sh.tmpl:10-13` | Hardcodes PHP + `app/` — domain-map enforcement non-functional for non-Laravel |
| P1-05 | Framework | `agent-discovery.tmpl:21-38` | Hardcodes `find app/Models -name "*.php"` etc. — discovery agent useless for non-Laravel |
| P1-06 | Framework | `generate.py:883-893` | `build_rules_md` includes Laravel `$guarded`/`$fillable` rule in ALL frameworks' RULES.md |
| P1-07 | Framework | `references/customize-guide.md:87,144-151` | Tier 1 always reads `framework-laravel.md`; Your Files paths are Laravel-only |
| P1-08 | Bug | `auto-promote-learnings.sh.tmpl:26-44` | Race condition — `sed -i` on shared-learnings.md with no `flock`; corrupts on parallel agents |
| P1-09 | Bug | `agent-domain.tmpl:46` | `{RelevantTest}` mixed-case placeholder bypasses warning regex, appears literally in every domain agent |
| P1-10 | Bug | `generate.py:write_file()` | Overwrites existing `.claude/` files silently — data loss risk on regeneration |
| P1-11 | Bug | `agent-migration.tmpl:33-34` | `sharedDb` path unvalidated and unquoted in shell commands — breaks on spaces |
| P1-12 | Bug | `generate.py:942,1041-1056` | `agentMemory=false` leaves all agents referencing non-existent MEMORY.md files |
| P1-13 | Interaction | `build_orchestrator_skill:299-306` | Optional agents (query-optimizer, mcp-dev, migration) absent from orchestrator inventory — invisible to dispatch |
| P1-14 | Interaction | Orchestrator + review agent | Review agent has no automatic trigger mechanism. "Auto-trigger" promise in description is not fulfilled for single-agent tasks. |
| P1-15 | Interaction | `audit-skill.tmpl:151-153` | References `php .claude/scripts/extract-agent-context.php` — script is never generated. Always falls back. |
| P1-16 | Docs | `references/customize-guide.md` | Entire file describes AI-fill workflow that no longer exists (v1.1.0 is Option B) |
| P1-17 | Docs | `generate.py:1191` | Generator prints stale "AI customization will fill CLAUDE.md" — contradicts core design |
| P1-18 | Docs | `commands/setup.md:8` | Body says "Laravel projects" — plugin supports 7 frameworks |
| P1-19 | Docs | `README.md:111,122,195,221` | Skill line counts: 955, 913, actual 706/860 — three conflicting numbers |
| P1-20 | Docs | `commands/setup.md:127-128` | Config schema has phantom `agentTracking` hook key — does not exist in generator |
| P1-21 | Docs | `commands/setup.md:109` | `projectDir` marked as config field but generator never reads it |

### P2 — MEDIUM: Degraded quality, test gaps, or architectural debt (22 findings)

| ID | Category | Issue |
|----|----------|-------|
| P2-01 | Arch | `generate.py` is a 1,210-line monolith with 6+ distinct concerns; adding a framework requires editing 5 locations |
| P2-02 | Arch | Template `{PLACEHOLDER}` syntax collides with shell `${VAR}`; inconsistent processing paths (dashboard bypasses render_template) |
| P2-03 | Arch | No version stamps in generated files; no migration path when plugin updates; `--force` flag referenced but doesn't exist |
| P2-04 | Arch | `deny` array always `[]` — conservative mode has no explicit denies for `curl`, `wget`, `ssh` |
| P2-05 | Arch | Domain ownership enforced by text instructions only — no technical guard via hooks |
| P2-06 | Arch | Config validation accepts unknown keys silently; missing nested `techStack` validation |
| P2-07 | Arch | 4 SubagentStop hooks all write to shared files without `flock` |
| P2-08 | Arch | Commands have no pre/post conditions; partial apply leaves orphaned files |
| P2-09 | Test | 5 critical config validation paths untested (missing keys, formatter regex, domain format) |
| P2-10 | Test | `commitPolicy=claude`, `permissionLevel` conservative/permissive — untested branches |
| P2-11 | Test | CLAUDE.md/RULES.md content never verified — only file existence checked |
| P2-12 | Test | `evalLevel` basic/none, `modelBudget` budget/quality, `agentTeams`, `worktreeSymlinks` — all untested |
| P2-13 | Test | Hook scripts: executable bit, dry-run mode, single-domain edge case — all untested |
| P2-14 | Test | No unreplaced placeholder assertion — broken templates pass all tests |
| P2-15 | Docs | `health.md` Check 12 scans `app/*.php` — Laravel-only, not framework-aware |
| P2-16 | Docs | Example output shows "Hook scripts: 11" — generator max is 10 |
| P2-17 | Docs | `health.md` references `/buddyx-forge --force` — command doesn't exist |
| P2-18 | Docs | `commands/setup.md:164-178` — `customize-guide.md` is never invoked; AI customization phase missing from setup |
| P2-19 | Compat | `md5sum`, `xdg-open`, `sed -i` are Linux-only — no macOS fallback |
| P2-20 | Interaction | Team-lead/domain agents duplicate global `block-git-commit.sh` hook (runs twice per bash call) |
| P2-21 | Interaction | `detect-new-file-created.sh` always writes to dashboard but dashboard dir only created with evalLevel != none |
| P2-22 | Docs | `dream.md` checks for non-existent `claude --dream` feature; dead code |

### P3 — LOW: Cosmetic, minor inconsistencies, nice-to-have (16 findings)

| ID | Issue |
|----|-------|
| P3-01 | Plugin file count "48" in README — actual is ~46 |
| P3-02 | "67 plugins and MCP servers" overcounts cross-framework duplicates (~35 unique) |
| P3-03 | `extract-learnings.sh` trim normalizes to 86 lines, not 100 |
| P3-04 | `prompt-save-learnings.sh` grep fallback is dead code |
| P3-05 | Duplicate comment `# 11.` in generate.py |
| P3-06 | `agents-md.tmpl` claims cross-tool compatibility but `background: true` is Claude-only |
| P3-07 | `{name}-review` not marked read-only in README agents table |
| P3-08 | `chmod` instruction in setup.md is redundant — generator already handles it |
| P3-09 | `dream.md` and `scan.md` duplicate dream mode docs inconsistently |
| P3-10 | `.pyc` cache file still present despite changelog claiming removal |
| P3-11 | Global `dry_run_count` never reset between calls — wrong count on repeated runs |
| P3-12 | `build_claude_md` produces double space when `frameworkVersion` is empty |
| P3-13 | `add-domain.md` hardcodes `sonnet` model in orchestrator row, ignoring `modelBudget` |
| P3-14 | `detect-stack.md` React detection snippet missing `2>/dev/null` on first grep |
| P3-15 | Go/Rails PostgreSQL MCP entries in tech-recommendations missing install commands |
| P3-16 | `auto-promote-learnings.sh` sed leaves unstaged changes that cause false git-diff in next session |

---

## Recommended Fix Order

### Phase 1: Stop the bleeding (P0 — Critical fixes)
Fix all 14 P0 items. These cause crashes, security issues, or completely broken features.

**Estimated scope:** ~25 files modified

1. **Config validation hardening** — validate `modelBudget`, `permissionLevel`, `commitPolicy` values in `load_config()` (P0-05, P0-10, P0-11)
2. **Missing script bugs** — create `block-migration.sh.tmpl` or remove the hook reference; guard `block-git-commit.sh` based on commitPolicy; guard autoFormat on empty formatter (P0-08, P0-09, P0-14)
3. **Security fixes** — expand safety-guard patterns; sanitize AGENT_TYPE; quote FORMATTER_CMD (P0-01, P0-02, P0-03)
4. **Shell bugs** — fix operator precedence in eval hooks; add jq checks to all hooks (P0-04, P0-12)
5. **Generation safety** — write to temp dir first, move atomically on success (P0-07)
6. **Dashboard** — add fetch() for events.jsonl or pre-inject data (P0-06)
7. **Django scan** — fix find command OR logic (P0-13)

### Phase 2: Framework generalization (P1-01 through P1-07)
De-Laravel-ify all templates, hooks, and references to work with all 7 frameworks.

**Estimated scope:** ~15 templates + 3 references modified

1. Make `audit-skill.tmpl` consume `{DOMAIN_LIST}` and remove hardcoded UMS modules
2. Make `diagram-skill.tmpl` consume placeholders and remove "UMS HR System"
3. Make `auto-format-new-files.sh` and `detect-new-file-created.sh` framework-aware
4. Make `agent-discovery.tmpl` framework-aware
5. Move `$guarded`/`$fillable` to Laravel-only section in `build_rules_md`
6. Fix `customize-guide.md` to be framework-conditional
7. Update all command docs to be framework-aware

### Phase 3: Bug fixes and interactions (P1-08 through P1-15)
Fix remaining high-priority bugs and cross-component issues.

**Estimated scope:** ~12 files modified

1. Add `flock` to eval hooks writing shared files
2. Fix `{RelevantTest}` placeholder to `<TestName>`
3. Add overwrite protection/warning to `write_file()`
4. Validate/quote `sharedDb` path
5. Handle `agentMemory=false` in agent templates
6. Add optional agents to orchestrator inventory
7. Document review agent trigger limitations

### Phase 4: Documentation corrections (P1-16 through P1-21)
Fix stale, wrong, or missing documentation.

**Estimated scope:** ~8 files modified

### Phase 5: Architecture and tests (P2)
Improve code structure, add missing test coverage, and fix medium-priority issues.

**Estimated scope:** Major refactoring; consider as separate project

### Phase 6: Polish (P3)
Fix cosmetic issues and minor inconsistencies.

---

## Systemic Patterns to Address

### Pattern A: Laravel-First Bias
**Affected:** P1-01 through P1-07, P2-15, I-1, I-3, I-7, I-8
**Root cause:** Plugin was developed against a Laravel project. Templates, hooks, and docs contain hardcoded PHP/Laravel paths that were never parameterized.
**Fix approach:** Audit every `.tmpl` file for framework-specific content. Either parameterize via template variables or add conditional generation based on `techStack.framework`.

### Pattern B: Config Validation Gaps
**Affected:** P0-05, P0-10, P0-11, P2-06
**Root cause:** `load_config()` checks key presence but not value validity for enum-like fields.
**Fix approach:** Add a validation block for all enum fields: `modelBudget`, `permissionLevel`, `commitPolicy`, `evalLevel`, `techStack.framework`.

### Pattern C: Template-Dict Mismatch
**Affected:** P1-01 (DOMAIN_LIST), P1-02 (EXAMPLE_DOMAIN + all common keys), P1-09 ({RelevantTest})
**Root cause:** Templates were written independently from the render calls. No automated check verifies that every template placeholder has a corresponding dict key.
**Fix approach:** Add a test that generates output and scans all files for `{UPPER_CASE}` patterns. Any match = unreplaced placeholder = test failure.

### Pattern D: Inconsistent Failure Modes
**Affected:** P0-04 (jq), P0-08 (block-migration), P0-09 (block-git-commit), P0-14 (autoFormat)
**Root cause:** Hooks and scripts are generated unconditionally but depend on conditional runtime state.
**Fix approach:** For every generated hook script, verify that its dependencies (files, tools, config flags) are also satisfied at generation time.

---

## Test Execution Results

```
=== Config Validation ===    5 PASS
=== Framework Generation === 21 PASS (7 frameworks x 3 assertions)
=== Optional Agents ===      3 PASS
=== Memory Flag ===          2 PASS
=== Framework Permissions === 5 PASS
==================================================
Results: 36 PASS, 0 FAIL
```

All tests pass, but the audit identified 14 untested code paths with critical bugs that the current tests cannot detect (test gaps documented in P2-09 through P2-14).

---

## Files Referenced

### Source code
- `plugins/buddyx-forge/scripts/generate.py` (1,210 lines)
- `tests/test_generator.py` (219 lines)

### Templates (26 files)
- `plugins/buddyx-forge/templates/agent-*.tmpl` (7 agent templates)
- `plugins/buddyx-forge/templates/hooks/*.sh.tmpl` (5 hook templates)
- `plugins/buddyx-forge/templates/hooks/eval/*.sh.tmpl` (6 eval hook templates)
- `plugins/buddyx-forge/templates/*.tmpl` (8 other templates)

### Commands (6 files)
- `plugins/buddyx-forge/commands/{setup,scan,health,add-domain,dashboard,dream}.md`

### References (10 files)
- `plugins/buddyx-forge/references/{detect-stack,customize-guide,tech-recommendations}.md`
- `plugins/buddyx-forge/references/framework-{laravel,nextjs,react,nodejs,django,go,rails}.md`

### Documentation
- `README.md`
- `plugins/buddyx-forge/SKILL.md`
- `plugins/buddyx-forge/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

### HTML Templates
- `plugins/buddyx-forge/templates/dashboard.html.tmpl`
- `plugins/buddyx-forge/templates/module-audit-template.html`

---

## Round 3 Findings (NEW — not in Rounds 1-2)

### P0-R3 — Additional Critical Findings

| ID | Category | File(s) | Issue |
|----|----------|---------|-------|
| P0-15 | Bug | `generate.py:202,215` | `"Write\|Edit"` matcher never fires — pipe `\|` is not a glob OR. `block-migration.sh` and `detect-new-file-created.sh` PostToolUse hooks are never triggered. |
| P0-16 | Bug | `generate.py:148-151` | `conservative` permission level skips ALL framework commands. Go/Rails/Django agents cannot run build/test commands at all. |
| P0-17 | Security | `dashboard.html.tmpl:46`, `module-audit-template.html:196` | XSS via `</script>` injection — raw JSON substituted into inline `<script>` blocks. If scanned source code contains `</script>`, HTML breaks. |
| P0-18 | Bug | `auto-format-new-files.sh.tmpl:18`, `detect-new-file-created.sh.tmpl:18` | Path containment uses `grep -qF` substring match, not prefix match — directory traversal bypass. |
| P0-19 | Bug | `auto-promote-learnings.sh.tmpl:30` | Unescaped user content in grep pattern — shell special chars `[`, `*`, `\` cause malformed grep or wrong-line matches. |

### P1-R3 — Additional High Findings

| ID | Category | File(s) | Issue |
|----|----------|---------|-------|
| P1-22 | Framework | `agent-db.tmpl:19-21` | Hardcodes "Laravel Boost MCP" + `php artisan` for ALL frameworks — Django/Go db agents are useless |
| P1-23 | Framework | `agent-maintenance.tmpl:32-35` | Hardcodes `find app/Models -name "*.php"` for ALL frameworks — maintenance agent non-functional for Django/Go |
| P1-24 | Framework | `validate-agent-output.sh.tmpl:18-36` | Validates `$guarded = []` and `addslashes` (PHP-only) for ALL frameworks — no Django/Go rules exist |
| P1-25 | Framework | `generate.py:735-738` | CLAUDE.md includes PHP "No Inline FQCN" + `use` import rule for ALL frameworks |
| P1-26 | Framework | `hookify-rules.tmpl:17-29` | 3 Laravel-specific hookify rules emitted for ALL frameworks (migration paths, $guarded, FQCN) |
| P1-27 | Metadata | `plugin.json` | Missing `commands` field — plugin cannot register its 6 commands with Claude Code's plugin system |
| P1-28 | Compat | `module-audit-template.html:200` | Mermaid.js loaded from CDN — 3 of 11 audit tabs break when opened offline or via `file://` |

### P2-R3 — Additional Medium Findings

| ID | Category | Issue |
|----|----------|-------|
| P2-23 | Regex | Project/domain name validation allows trailing hyphens (`my-project-`) and consecutive hyphens (`my--project`) — produces malformed agent names |
| P2-24 | Bash | `safety-guard.sh` has no `set -e`/`set -u` — unexpected failures silently exit 0 (allow). `chmod 777` check misses `a+rwx`, `0777`. |
| P2-25 | Bash | `block-git-commit.sh` doesn't block `git reset --hard`, `git clean -fd`, `git stash pop`, `git branch -D` |
| P2-26 | Bash | `inject-prompt-context.sh` — commit message containing literal `EOF` breaks heredoc output |
| P2-27 | Bash | `track-agent-start.sh`, `track-session-count.sh` — non-atomic writes to `live-status.json` corrupt on concurrent agents |
| P2-28 | Bash | `detect-new-file-created.sh:14` — `sed` path stripping with unescaped PROJECT_DIR breaks on dots/brackets in paths |
| P2-29 | Docs | `setup.md:127` — phantom `agentTracking` hook key in config schema; doesn't exist in generator |
| P2-30 | Docs | `setup.md:109` — `projectDir` marked as config field but generator never reads it |
| P2-31 | HTML | `module-audit-template.html:299` — `sortRows` uses `Object.keys()[col]` — sorts by wrong field if key order differs from headers |
| P2-32 | HTML | `module-audit-template.html:555` — `erDragStart()` dead code, never called |
| P2-33 | Bash | `generate.py:157` — `python3` explicitly allowed for Go/Rails projects in balanced mode (unnecessary attack surface) |

### Edge Case Testing Summary

6 edge-case configurations were tested by tracing generator code paths:

| Config | Result | Key Findings |
|--------|--------|-------------|
| Single domain (1 domain) | PASS | Orchestrator works; "Parallel" dispatch text misleading for 1 agent |
| Max domains (8 domains) | PASS | All 8 agents generated correctly; AGENTS.md still missing optional agents |
| commitPolicy=claude | **FAIL** | All agents reference non-existent `block-git-commit.sh` (P0-09 confirmed) |
| sharedDb + blockMigration | **FAIL** | `block-migration.sh` never generated (P0-08 confirmed); settings.json hook breaks all writes |
| Minimal config (required keys only) | PASS | All optional keys use safe defaults; double-space in CLAUDE.md when version empty |
| Dry-run mode | PASS | Output directory stays empty; file count correct |

### Updated Fix Phase Order

**Phase 1 additions:** P0-15 (Write\|Edit matcher), P0-16 (conservative permissions), P0-17 (XSS), P0-18 (path containment), P0-19 (grep injection)
**Phase 2 additions:** P1-22 through P1-26 (5 more Laravel-biased templates to generalize), P1-27 (plugin.json commands), P1-28 (Mermaid offline)
**Phase 5 additions:** P2-23 through P2-33 (regex, bash, HTML quality)

---

## Final Statistics

| Round | Agents | New Findings | Focus |
|-------|--------|-------------|-------|
| 1 | 5 | 52 | Code quality, output quality, architecture, tests, docs |
| 2 | 4 | 21 | Line-by-line, cross-component, templates, commands |
| 3 | 4 | 20 | Generated output verification, edge cases, regex/bash, HTML/metadata |
| **Total** | **13** | **93** | |

| Severity | Count |
|----------|-------|
| P0 Critical | 19 |
| P1 High | 28 |
| P2 Medium | 33 |
| P3 Low | 13 |
| **Total** | **93** |
