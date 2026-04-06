# Contributing to buddyx-forge

Thanks for considering a contribution! This guide explains how the codebase is structured and how to add support for new frameworks.

## Quick Setup

```bash
git clone https://github.com/sandiprv9898/buddyx-forge.git
cd buddyx-forge
python3 tests/test_generator.py   # all tests should pass
```

No external dependencies needed — the generator uses Python 3.8+ stdlib only.

## Repository Structure

```
plugins/buddyx-forge/
  scripts/generate.py          # Core generator (builds all output files)
  templates/                   # .tmpl files for agents, hooks, skills
  commands/                    # Plugin command definitions (setup, scan, health, etc.)
  references/                  # Framework detection + coding rules per framework
  .claude-plugin/plugin.json   # Plugin metadata

tests/test_generator.py        # Test suite (run with python3)
examples/                      # Generated output samples (Laravel, Django)
buddyx-forge.example.json      # Example config for reference
```

## How to Add a New Framework

This is the most common contribution. Adding support for a new framework (e.g., Spring Boot, Flutter, Rust/Axum) requires changes in **5 files**:

### 1. `references/framework-{name}.md` (create new)

Document the framework's conventions, common packages, and coding patterns. See `references/framework-laravel.md` or `references/framework-django.md` for the format.

### 2. `references/detect-stack.md` (edit)

Add detection logic under "Framework Auto-Detection":
- Which config file identifies the framework (e.g., `pom.xml` for Spring Boot)
- How to extract version, sub-frameworks, DB config
- Formatter and test runner commands
- Domain detection heuristics
- Worktree symlink directories

### 3. `plugins/buddyx-forge/scripts/generate.py` (edit — 6 places)

Search for existing framework entries and add yours in the same pattern:

**a) `fw_commands` dict (~line 120)** — Permission commands for settings.json:
```python
"springboot": {
    "allow": ["Bash(mvn *)", "Bash(gradle *)", "Bash(java *)"],
    "ask": ["Bash(mvn deploy *)", "Bash(gradle publish *)"],
},
```

**b) `_get_framework_checklist()` (~line 349)** — Review agent checklist:
```python
elif framework == "springboot":
    return """### Spring Boot
- [ ] Constructor injection over field injection
- [ ] @Transactional on service methods
- [ ] DTO per endpoint (no entity exposure)
..."""
```

**c) `build_rules_md()` (~line 765)** — Framework-specific coding rules:
```python
elif framework == "springboot":
    rules += """## Spring Boot
- Constructor injection — no @Autowired on fields
- DTOs for API boundaries — never expose entities
..."""
```

**d) `hookify_rules_map` dict (~line 1117)** — Hookify rules:
```python
"springboot": """## Rule: No field injection
- trigger: Write or Edit containing `@Autowired` on a field
- action: warn
- message: "Use constructor injection instead of @Autowired on fields." """,
```

**e) Framework maps (~line 1050-1110)** — File extension, source directory, discovery commands, DB tools, and maintenance commands. Look for `file_ext_map`, `source_dir_map`, `discovery_commands_map`, `db_tools_map`, `maintenance_commands_map` and add entries.

**f) `scan.md` command (~line 29)** — Add framework-specific scan paths.

### 4. `references/tech-recommendations.md` (edit)

Add recommended plugins and MCP servers for the new framework.

### 5. `tests/test_generator.py` (edit)

Add the framework to the generation loop and permission test:

```python
# In the framework generation loop (~line 117)
for fw in ["laravel", "nextjs", "django", "go", "rails", "react", "express", "springboot"]:

# In the permission test (~line 241)
for fw, expected_cmd in [..., ("springboot", "mvn")]:
```

### How to Test Your Changes

```bash
# Run full test suite
python3 tests/test_generator.py

# Generate example output to inspect
python3 plugins/buddyx-forge/scripts/generate.py \
  --config your-test-config.json \
  --output /tmp/test-output \
  --dry-run

# Generate for real and inspect files
python3 plugins/buddyx-forge/scripts/generate.py \
  --config your-test-config.json \
  --output /tmp/test-output
```

## Other Ways to Contribute

### Bug fixes
- Fork, fix, add a test that covers the fix, open a PR.

### New hook templates
- Add `.tmpl` file in `templates/hooks/`
- Always check `command -v jq` before using jq (see existing hooks for pattern)
- Safety-critical hooks should fail closed (`exit 2`), informational hooks fail open (`exit 0`)

### New commands
- Add `.md` file in `commands/`
- Register in `.claude-plugin/plugin.json`

### Improving examples
- Generate output for your framework and add to `examples/`

## Code Style

- Python: stdlib only, no external dependencies
- Shell scripts: always check for `jq` availability
- Templates: use `{PLACEHOLDER_NAME}` (uppercase with underscores) for replacements
- Keep agent `.md` files under 150 lines
- Test every new feature

## Questions?

Open an issue on GitHub. Tag it with `question` or `framework-request` as appropriate.
