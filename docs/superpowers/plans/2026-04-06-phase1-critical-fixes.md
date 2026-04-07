# Phase 1: Critical Fixes (P0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 19 P0-level critical findings — crashes, security holes, and completely broken features.

**Architecture:** All fixes are in the existing codebase. No new files except `block-migration.sh.tmpl` template. Changes are isolated per-file and independently testable.

**Tech Stack:** Python 3.8+ (stdlib), Bash, JSON

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `plugins/buddyx-forge/scripts/generate.py` | Modify | Config validation, matcher fixes, atomicity, autoFormat guard, conservative perms, model budget safety |
| `plugins/buddyx-forge/templates/hooks/safety-guard.sh.tmpl` | Modify | Expand rm/chmod patterns |
| `plugins/buddyx-forge/templates/hooks/eval/track-agent-start.sh.tmpl` | Modify | Sanitize AGENT_TYPE |
| `plugins/buddyx-forge/templates/hooks/eval/track-session-count.sh.tmpl` | Modify | Sanitize AGENT_TYPE |
| `plugins/buddyx-forge/templates/hooks/eval/extract-learnings.sh.tmpl` | Modify | Fix operator precedence, add jq check |
| `plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl` | Modify | Fix operator precedence, sanitize grep, add jq check |
| `plugins/buddyx-forge/templates/hooks/auto-format-new-files.sh.tmpl` | Modify | Fix path containment check |
| `plugins/buddyx-forge/templates/hooks/detect-new-file-created.sh.tmpl` | Modify | Fix path containment check |
| `plugins/buddyx-forge/templates/hooks/block-git-commit.sh.tmpl` | Modify | Consistent jq handling |
| `plugins/buddyx-forge/templates/hooks/safety-guard.sh.tmpl` | Modify | Add jq check |
| `plugins/buddyx-forge/templates/hooks/block-migration.sh.tmpl` | Create | New template for migration blocking |
| `plugins/buddyx-forge/templates/dashboard.html.tmpl` | Modify | Add fetch() for events.jsonl, fix XSS |
| `plugins/buddyx-forge/templates/module-audit-template.html` | Modify | Fix XSS in AUDIT_DATA injection |
| `plugins/buddyx-forge/commands/scan.md` | Modify | Fix Django find command |
| `tests/test_generator.py` | Modify | Add tests for new validation + critical paths |

---

### Task 1: Config Validation Hardening (P0-05, P0-10, P0-11)

**Files:**
- Modify: `plugins/buddyx-forge/scripts/generate.py:19-57`
- Test: `tests/test_generator.py`

- [ ] **Step 1: Write failing tests for enum validation**

Add these tests after the existing config validation section in `tests/test_generator.py`:

```python
# === Enum Validation ===
print("\n=== Enum Validation ===")

# modelBudget
try:
    cfg = make_config({"modelBudget": "premium"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("invalid modelBudget rejected", False)
except ValueError:
    test("invalid modelBudget rejected", True)

# permissionLevel
try:
    cfg = make_config({"permissionLevel": "strict"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("invalid permissionLevel rejected", False)
except ValueError:
    test("invalid permissionLevel rejected", True)

# commitPolicy
try:
    cfg = make_config({"commitPolicy": "manual"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("invalid commitPolicy rejected", False)
except ValueError:
    test("invalid commitPolicy rejected", True)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 tests/test_generator.py 2>&1 | grep -E "Enum|FAIL"`
Expected: 3 FAIL lines

- [ ] **Step 3: Add validation to load_config()**

In `plugins/buddyx-forge/scripts/generate.py`, add after line 55 (after the formatter validation):

```python
    # Validate enum fields
    valid_budgets = ("budget", "balanced", "quality")
    if config.get("modelBudget") not in valid_budgets:
        raise ValueError(f"Invalid modelBudget: '{config.get('modelBudget')}'. Must be one of: {valid_budgets}")

    valid_levels = ("conservative", "balanced", "permissive")
    if config.get("permissionLevel") not in valid_levels:
        raise ValueError(f"Invalid permissionLevel: '{config.get('permissionLevel')}'. Must be one of: {valid_levels}")

    valid_policies = ("user", "claude")
    if config.get("commitPolicy") not in valid_policies:
        raise ValueError(f"Invalid commitPolicy: '{config.get('commitPolicy')}'. Must be one of: {valid_policies}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 tests/test_generator.py 2>&1 | tail -5`
Expected: 3 new PASS lines, 0 FAIL total

- [ ] **Step 5: Also safe-guard the dict lookups in generate()**

In `generate.py`, change the bare dict lookups at lines 949-950 to use `.get()`:

Replace:
```python
    ro_model = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}[model_budget]
    rw_model = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}[model_budget]
```

With:
```python
    model_map_ro = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}
    model_map_rw = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}
    ro_model = model_map_ro.get(model_budget, "haiku")
    rw_model = model_map_rw.get(model_budget, "sonnet")
```

- [ ] **Step 6: Run full test suite**

Run: `python3 tests/test_generator.py`
Expected: All tests pass including 3 new ones

---

### Task 2: Fix Write|Edit Matcher and Conservative Permissions (P0-15, P0-16)

**Files:**
- Modify: `plugins/buddyx-forge/scripts/generate.py:148-151, 200-216`

- [ ] **Step 1: Write failing test for conservative permissions**

Add to `tests/test_generator.py`:

```python
# === Conservative Permissions ===
print("\n=== Conservative Permissions ===")
outdir = tempfile.mkdtemp()
try:
    cfg = make_config({"permissionLevel": "conservative", "techStack": {
        "language": "go", "framework": "go", "formatter": "gofmt", "testRunner": "go test ./..."
    }})
    generate(cfg, outdir)
    with open(os.path.join(outdir, "settings.json")) as f:
        settings = json.load(f)
    perms_str = json.dumps(settings["permissions"])
    test("conservative: framework ask commands present", "go build" in perms_str or "go test" in perms_str)
finally:
    shutil.rmtree(outdir, ignore_errors=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_generator.py 2>&1 | grep "conservative"`
Expected: FAIL

- [ ] **Step 3: Fix conservative permissions — add framework ask commands**

In `generate.py`, replace lines 148-151:

```python
    if perm_level == "conservative":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend(["Bash(ls *)", "Bash(find *)"])
```

With:

```python
    if perm_level == "conservative":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend(["Bash(ls *)", "Bash(find *)"])
        ask.extend(fw.get("allow", []))
        ask.extend(fw.get("ask", []))
```

- [ ] **Step 4: Fix Write|Edit matchers — split into separate entries**

In `generate.py`, replace the `blockMigration` hook entry (lines 200-204):

```python
    if hooks_config.get("blockMigration", False):
        pre_tool_use.append({
            "matcher": "Write",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-migration.sh"}]
        })
        pre_tool_use.append({
            "matcher": "Edit",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-migration.sh"}]
        })
```

Replace the detect-new-file-created entry (lines 214-217):

```python
    post_tool_use.append({
        "matcher": "Write",
        "hooks": [{"type": "command", "command": ".claude/scripts/detect-new-file-created.sh"}]
    })
    post_tool_use.append({
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": ".claude/scripts/detect-new-file-created.sh"}]
    })
```

- [ ] **Step 5: Run tests**

Run: `python3 tests/test_generator.py`
Expected: All pass including the new conservative test

---

### Task 3: Create block-migration.sh Template and Guard autoFormat (P0-08, P0-14)

**Files:**
- Create: `plugins/buddyx-forge/templates/hooks/block-migration.sh.tmpl`
- Modify: `plugins/buddyx-forge/scripts/generate.py:1145-1148, 1128+`

- [ ] **Step 1: Create the block-migration.sh template**

Write `plugins/buddyx-forge/templates/hooks/block-migration.sh.tmpl`:

```bash
#!/bin/bash
# PreToolUse hook: Blocks migration file creation in this project.
# Migrations should go to the shared database project.
# Generated by buddyx-forge.

INPUT=$(cat)

if ! command -v jq &>/dev/null; then
  echo '{"error": "jq not available — allowing write for safety"}' >&2
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE_PATH" ] && exit 0

# Block migration files
if echo "$FILE_PATH" | grep -qE '(database/migrations|migrations/[0-9])'; then
  echo "BLOCKED: Migrations belong in the shared database project. Do not create migration files here." >&2
  exit 2
fi

exit 0
```

- [ ] **Step 2: Add block-migration.sh generation to generate()**

In `generate.py`, after the `block-git-commit.sh` block (after line 1143), add:

```python
    if hooks_cfg.get("blockMigration", False):
        content = render_template("hooks/block-migration.sh.tmpl", common)
        write_file(output_dir, "scripts/block-migration.sh", content, dry_run)
        hook_scripts.append("scripts/block-migration.sh")
```

- [ ] **Step 3: Guard autoFormat against empty formatter**

In `generate.py`, change the autoFormat block (lines 1145-1148):

```python
    if hooks_cfg.get("autoFormat", False) and formatter:
        content = render_template("hooks/auto-format-new-files.sh.tmpl", common)
        write_file(output_dir, "scripts/auto-format-new-files.sh", content, dry_run)
        hook_scripts.append("scripts/auto-format-new-files.sh")
```

Also guard the settings.json entry — in `build_settings_json()`, change lines 209-213:

```python
    if hooks_config.get("autoFormat", False) and formatter:
        post_tool_use.append({
            "matcher": "Write",
            "hooks": [{"type": "command", "command": ".claude/scripts/auto-format-new-files.sh"}]
        })
```

- [ ] **Step 4: Run tests**

Run: `python3 tests/test_generator.py`
Expected: All pass

---

### Task 4: Security — Expand safety-guard Patterns (P0-01)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/safety-guard.sh.tmpl`

- [ ] **Step 1: Replace the rm patterns with comprehensive ones**

In `safety-guard.sh.tmpl`, replace lines 13-19:

```bash
# Destructive file operations — block rm -rf on ANY path (not just root)
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?|(-[a-zA-Z]*f[a-zA-Z]*\s+)?-[a-zA-Z]*r[a-zA-Z]*\s+)'; then
  echo "BLOCKED: Recursive delete detected. Use specific file removal instead." >&2; exit 2
fi
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/($|\s)'; then
  echo "BLOCKED: rm on root directory." >&2; exit 2
fi
```

- [ ] **Step 2: Expand chmod pattern**

Replace line 35:

```bash
if echo "$COMMAND" | grep -qE 'chmod\s+(777|0777|a\+rwx)\b'; then
  echo "BLOCKED: Overly permissive chmod." >&2; exit 2
fi
```

- [ ] **Step 3: Verify the template is valid bash**

Run: `bash -n plugins/buddyx-forge/templates/hooks/safety-guard.sh.tmpl`
Expected: No output (no syntax errors)

---

### Task 5: Sanitize AGENT_TYPE in Eval Hooks (P0-02)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/eval/track-agent-start.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/track-session-count.sh.tmpl`

- [ ] **Step 1: Add sanitization to track-agent-start.sh.tmpl**

After line 6 (`AGENT_TYPE=$(echo "$INPUT" | jq ...)`), add:

```bash
AGENT_TYPE=$(echo "$AGENT_TYPE" | tr -cd 'a-zA-Z0-9-')
```

- [ ] **Step 2: Add sanitization to track-session-count.sh.tmpl**

Same fix — after the `AGENT_TYPE` jq extraction line, add:

```bash
AGENT_TYPE=$(echo "$AGENT_TYPE" | tr -cd 'a-zA-Z0-9-')
```

- [ ] **Step 3: Verify both templates have valid bash**

Run: `bash -n plugins/buddyx-forge/templates/hooks/eval/track-agent-start.sh.tmpl && bash -n plugins/buddyx-forge/templates/hooks/eval/track-session-count.sh.tmpl`
Expected: No output

---

### Task 6: Fix jq Dependency Consistency (P0-04)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/safety-guard.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/extract-learnings.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/track-agent-start.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/track-session-count.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/validate-agent-output.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/prompt-save-learnings.sh.tmpl`
- Modify: `plugins/buddyx-forge/templates/hooks/block-git-commit.sh.tmpl`

- [ ] **Step 1: Define a consistent jq guard pattern**

Every hook that uses jq should have this at the top (after `#!/bin/bash` and comment):

```bash
if ! command -v jq &>/dev/null; then
  echo '{"warning": "jq not available — skipping hook"}' >&2
  exit 0
fi
```

This is "fail open" — allows the tool call but logs a warning. The block-git-commit.sh currently uses `exit 2` (fail closed). Change it to `exit 0` for consistency.

- [ ] **Step 2: Add jq check to safety-guard.sh.tmpl**

Add after line 4 (`INPUT=$(cat)`), before the jq calls:

```bash
if ! command -v jq &>/dev/null; then
  echo '{"warning": "jq not available — skipping safety-guard"}' >&2
  exit 0
fi
```

- [ ] **Step 3: Change block-git-commit.sh.tmpl to exit 0 instead of exit 2**

Replace the existing jq check's `exit 2` with `exit 0`.

- [ ] **Step 4: Add jq check to all eval hooks that don't have it**

Add the same guard to: `track-agent-start.sh.tmpl`, `track-session-count.sh.tmpl`, `validate-agent-output.sh.tmpl`, `extract-learnings.sh.tmpl`, `prompt-save-learnings.sh.tmpl`, `auto-promote-learnings.sh.tmpl`.

- [ ] **Step 5: Verify all templates are valid bash**

Run: `for f in plugins/buddyx-forge/templates/hooks/**/*.tmpl plugins/buddyx-forge/templates/hooks/*.tmpl; do bash -n "$f" && echo "OK: $f" || echo "FAIL: $f"; done`
Expected: All OK

---

### Task 7: Fix Shell Operator Precedence (P0-12)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/eval/extract-learnings.sh.tmpl:14`
- Modify: `plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl:14`

- [ ] **Step 1: Fix extract-learnings.sh.tmpl line 14**

Replace:
```bash
[ -z "$LAST_MESSAGE" ] || [ "$LAST_MESSAGE" = "null" ] && exit 0
```

With:
```bash
if [ -z "$LAST_MESSAGE" ] || [ "$LAST_MESSAGE" = "null" ]; then exit 0; fi
```

- [ ] **Step 2: Fix auto-promote-learnings.sh.tmpl line 14**

Same replacement.

- [ ] **Step 3: Verify syntax**

Run: `bash -n plugins/buddyx-forge/templates/hooks/eval/extract-learnings.sh.tmpl && bash -n plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl`
Expected: No output

---

### Task 8: Fix Path Containment Checks (P0-18)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/auto-format-new-files.sh.tmpl:18`
- Modify: `plugins/buddyx-forge/templates/hooks/detect-new-file-created.sh.tmpl:18`

- [ ] **Step 1: Fix auto-format-new-files.sh.tmpl**

Replace line 18:
```bash
echo "$FILE_PATH" | grep -qF "$PROJECT_DIR" || exit 0
```

With:
```bash
[[ "$FILE_PATH" == "$PROJECT_DIR"/* ]] || exit 0
```

- [ ] **Step 2: Fix detect-new-file-created.sh.tmpl**

Same replacement on its line 18.

- [ ] **Step 3: Verify syntax**

Run: `bash -n plugins/buddyx-forge/templates/hooks/auto-format-new-files.sh.tmpl && bash -n plugins/buddyx-forge/templates/hooks/detect-new-file-created.sh.tmpl`

---

### Task 9: Fix grep Injection in auto-promote-learnings (P0-19)

**Files:**
- Modify: `plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl`

- [ ] **Step 1: Escape the pattern before grep**

Find the line that uses `$pattern` in grep (around line 30). Replace:

```bash
MATCH_LINE=$(grep -n "\[NEW [0-2]/3\].*$(echo "$pattern" | head -c 40)" "$SHARED_FILE" | head -1)
```

With:

```bash
ESCAPED_PATTERN=$(echo "$pattern" | head -c 40 | sed 's/[][\\.*^$]/\\&/g')
MATCH_LINE=$(grep -n "\[NEW [0-2]/3\].*${ESCAPED_PATTERN}" "$SHARED_FILE" | head -1)
```

- [ ] **Step 2: Verify syntax**

Run: `bash -n plugins/buddyx-forge/templates/hooks/eval/auto-promote-learnings.sh.tmpl`

---

### Task 10: Atomic Generation with Rollback (P0-07)

**Files:**
- Modify: `plugins/buddyx-forge/scripts/generate.py:935-1194`

- [ ] **Step 1: Wrap generate() to write to a temp dir first**

At the top of `generate()` (after extracting config values, before Phase A), add:

```python
    # Atomic generation: write to temp dir, move on success
    if not dry_run:
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="buddyx-forge-")
        actual_output_dir = output_dir
        output_dir = temp_dir
    try:
```

At the bottom of `generate()` (after the summary print), add the atomic move:

```python
    except Exception:
        if not dry_run:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    else:
        if not dry_run:
            # Move generated files to actual output directory
            for item in Path(temp_dir).rglob("*"):
                if item.is_file():
                    rel = item.relative_to(temp_dir)
                    dest = Path(actual_output_dir) / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dest))
            shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 2: Fix the file_count calculation**

The `file_count` line at 1182 reads from `output_dir`. After the change, this reads from the temp dir which is correct during generation. No change needed here — it will count temp dir files before the move.

- [ ] **Step 3: Run tests**

Run: `python3 tests/test_generator.py`
Expected: All pass

---

### Task 11: Fix Dashboard — Add fetch() for events.jsonl (P0-06, P0-17)

**Files:**
- Modify: `plugins/buddyx-forge/templates/dashboard.html.tmpl`

- [ ] **Step 1: Replace the inline EVENTS_DATA with safe JSON loading**

Replace line 46:
```javascript
const EVENTS_DATA = [];
```

With:
```javascript
let EVENTS_DATA = [];
function loadEvents() {
  try {
    const el = document.getElementById('events-json');
    if (el && el.textContent.trim()) {
      EVENTS_DATA = JSON.parse(el.textContent);
    }
  } catch(e) { console.warn('Failed to parse events data:', e); }
  render();
}
```

Add before the closing `</script>` tag:

```javascript
document.addEventListener('DOMContentLoaded', loadEvents);
```

Add a safe JSON container before the `<script>` tag:

```html
<script type="application/json" id="events-json">[]</script>
```

- [ ] **Step 2: Also fix module-audit-template.html XSS**

In `plugins/buddyx-forge/templates/module-audit-template.html`, replace the inline `AUDIT_DATA = {}` injection point with a safe JSON container:

Replace:
```html
<script>const AUDIT_DATA = {};</script>
```

With:
```html
<script type="application/json" id="audit-json">{}</script>
<script>
const AUDIT_DATA = JSON.parse(document.getElementById('audit-json').textContent || '{}');
</script>
```

---

### Task 12: Fix Django Scan Command (P0-13)

**Files:**
- Modify: `plugins/buddyx-forge/commands/scan.md`

- [ ] **Step 1: Fix the Django find command**

In `plugins/buddyx-forge/commands/scan.md`, replace the broken Django find line (around line 52):

```bash
find . -path "*/urls.py" -path "*/tasks.py" -path "*/admin.py" -type f 2>/dev/null | sort
```

With:

```bash
find . \( -path "*/urls.py" -o -path "*/tasks.py" -o -path "*/admin.py" \) -type f 2>/dev/null | sort
```

---

### Task 13: Fix Stale Generator Summary Message (P0 adjacent — P1-17)

**Files:**
- Modify: `plugins/buddyx-forge/scripts/generate.py:1191`

- [ ] **Step 1: Replace stale AI customization message**

Replace line 1191:
```python
    print(f"  1. AI customization will fill CLAUDE.md, RULES.md, and agent file lists")
```

With:
```python
    print(f"  1. Run /buddyx-forge:scan to populate domain-map with real file paths")
```

And replace line 1192:
```python
    print(f"  2. Run /buddyx-forge:scan to populate domain-map and context packs")
```

With:
```python
    print(f"  2. Run /buddyx-forge:health to verify setup")
```

And replace line 1193:
```python
    print(f"  3. Run /buddyx-forge:health to verify setup")
```

With:
```python
    print(f"  3. Customize agent files if needed (see references/customize-guide.md)")
```

---

### Task 14: Fix Global dry_run_count (P3-11, but easy and prevents test issues)

**Files:**
- Modify: `plugins/buddyx-forge/scripts/generate.py:75, 935`

- [ ] **Step 1: Reset dry_run_count at the start of generate()**

Add at the top of `generate()`, after line 936:

```python
    global dry_run_count
    dry_run_count = 0
```

---

### Task 15: Final Test Run and Validation

- [ ] **Step 1: Run the full test suite**

Run: `python3 tests/test_generator.py`
Expected: All 39+ tests pass (36 original + 3+ new)

- [ ] **Step 2: Test edge case — commitPolicy=claude**

Run:
```bash
python3 plugins/buddyx-forge/scripts/generate.py --config /dev/stdin --output /tmp/test-claude-policy <<'EOF'
{"projectName":"test-fix","domains":["core"],"techStack":{"language":"python","framework":"django","db":"postgresql","formatter":"black","testRunner":"python manage.py test "},"hooks":{"blockDangerous":true},"commitPolicy":"claude","permissionLevel":"balanced","modelBudget":"balanced"}
EOF
cat /tmp/test-claude-policy/settings.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('git commit in allow:', any('git commit' in x for x in d['permissions']['allow'])); print('block-git-commit in hooks:', 'block-git-commit' in json.dumps(d.get('hooks',{})))"
```
Expected: `git commit in allow: True`, `block-git-commit in hooks: False`

- [ ] **Step 3: Test edge case — blockMigration=true**

Run:
```bash
python3 plugins/buddyx-forge/scripts/generate.py --config /dev/stdin --output /tmp/test-migration <<'EOF'
{"projectName":"test-mig","domains":["core"],"techStack":{"language":"php","framework":"laravel","db":"postgresql","formatter":"vendor/bin/pint","testRunner":"php artisan test --filter="},"hooks":{"blockDangerous":true,"blockCommits":true,"blockMigration":true},"sharedDb":"/shared/api","commitPolicy":"user","permissionLevel":"balanced","modelBudget":"balanced"}
EOF
test -f /tmp/test-migration/scripts/block-migration.sh && echo "block-migration.sh EXISTS" || echo "block-migration.sh MISSING"
```
Expected: `block-migration.sh EXISTS`

- [ ] **Step 4: Test edge case — conservative Go permissions**

Run:
```bash
python3 plugins/buddyx-forge/scripts/generate.py --config /dev/stdin --output /tmp/test-conservative <<'EOF'
{"projectName":"test-cons","domains":["api"],"techStack":{"language":"go","framework":"go","formatter":"gofmt","testRunner":"go test ./..."},"hooks":{},"commitPolicy":"user","permissionLevel":"conservative","modelBudget":"budget"}
EOF
python3 -c "import json; d=json.load(open('/tmp/test-conservative/settings.json')); print('go build in ask:', any('go build' in x for x in d['permissions']['ask']))"
```
Expected: `go build in ask: True`

- [ ] **Step 5: Clean up test artifacts**

Run: `rm -rf /tmp/test-claude-policy /tmp/test-migration /tmp/test-conservative`

---

## Issues & Concerns

### Known Issues in This Codebase (from audit + user review)

| # | Category | Issue | Status in Plan |
|---|----------|-------|---------------|
| IC-01 | Git | Committed `__pycache__/` despite `.gitignore`. A 48KB `.pyc` file at `plugins/buddyx-forge/scripts/__pycache__/generate.cpython-312.pyc` was committed before gitignore was added. Needs `git rm --cached`. | **Not in Phase 1** — add to Phase 6 (polish). Run: `git rm --cached -r plugins/buddyx-forge/scripts/__pycache__/` |
| IC-02 | Security | Config written to `/tmp/buddyx-forge-config.json` with predictable name. On multi-user systems this leaks project structure, domains, and tech stack. `tempfile.mkstemp()` with random name or writing to `.claude/` would be safer. | **Not in Phase 1** — setup.md is a command doc (Claude instructions), not generated code. Add to Phase 4 (docs). |
| IC-03 | Code | Global mutable `dry_run_count` (line 76). Fine for CLI, breaks as library or parallel use. A counter on the function or context object is cleaner. | **Addressed** — Task 14 resets it per call. Full refactor deferred to Phase 5 (architecture). |
| IC-04 | Code | Template placeholder warning regex (line 70) may trigger false positives on Go Template `{{.Foo}}` syntax in `.tmpl` files. Not harmful but noisy. | **Not in Phase 1** — cosmetic. Add to Phase 5 (architecture, template system redesign). |
| IC-05 | Safety | No idempotency protection. Re-running setup with different config overwrites everything in `.claude/` without backup. Setup command warns user but generator has no safeguard. | **Partially addressed** — Task 10 adds atomic generation. Full overwrite protection (P1-10) in Phase 3. |
| IC-06 | Permissions | In "permissive" mode, generated permissions include `Bash(xdg-open *)` and all framework commands without approval. May be too loose for teams. | **Not in Phase 1** — documented behavior, not a bug. Note in Phase 4 (docs improvement). |
| IC-07 | Validation | `evalLevel`, `commitPolicy`, `permissionLevel`, `modelBudget` not validated against enum values. `"modelBudget": "ultra"` causes silent KeyError. | **Addressed** — Task 1 adds enum validation for `modelBudget`, `permissionLevel`, `commitPolicy`. `evalLevel` validation to be added (see correction below). |
| IC-08 | Runtime | Shell scripts assume jq availability. Safety guard and hooks silently fail without it. Setup warns but marks jq "recommended, not required." | **Addressed** — Task 6 adds consistent jq guards to all hooks. |
| IC-09 | Migration | No versioning between plugin versions. No upgrade path from v1.1 to v1.2. No version marker in generated output. | **Not in Phase 1** — add to Phase 5 (P2-03). |
| IC-10 | Code | Duplicate step numbering — lines 1088 and 1092 both say `# 11.` | **Not in Phase 1** — add to Phase 6 (P3-05). |
| IC-11 | Security | Malicious `sharedDb` path gets interpolated into agent templates unsanitized. Only affects markdown Claude reads, not executed code, but worth noting. | **Partially addressed** — P1-11 (Phase 3) will validate/quote `sharedDb`. Low practical risk since config is user-authored. |

### Security Assessment

The plugin is low-risk for a developer tool. The formatter command sanitization is good. The safety hooks block real dangers. The main surface area is the generated shell scripts running as Claude Code hooks — these are transparent `.sh` files the user can inspect. No network calls, no telemetry, no secrets handling.

One edge case: if someone crafts a malicious config JSON with a carefully constructed `sharedDb` path, it gets interpolated into agent templates unsanitized. In practice this only affects the markdown files Claude reads, not executed code. Addressed in Phase 3 (P1-11).

---

## Plan Review Corrections

The following corrections were identified by code review and must be applied during implementation:

### Correction 1: Task 1 Step 3 — Wrong insertion point

**Problem:** Plan says "add after line 55" but that places code inside the `if formatter` guard block.
**Fix:** Insert the enum validation block **before the `return config` statement** (before line 58), not after line 55.

### Correction 2: Task 1 — Missing evalLevel validation

**Problem:** `evalLevel` is also an enum field not validated by load_config(). Plan validates 3 of 4 enums.
**Fix:** Add to the validation block in Task 1 Step 3:

```python
    valid_eval_levels = ("full", "basic", "none")
    if config.get("evalLevel", "none") not in valid_eval_levels:
        raise ValueError(f"Invalid evalLevel: '{config.get('evalLevel')}'. Must be one of: {valid_eval_levels}")
```

### Correction 3: Task 4 Step 1 — rm pattern is over-broad

**Problem:** The plan blocks ALL recursive `rm` commands. `rm -rf node_modules`, `rm -rf dist/` are legitimate.
**Fix:** Replace the proposed rm pattern with one that blocks recursive deletes on sensitive paths only:

```bash
# Block recursive delete on sensitive paths (root, home, system dirs)
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?|(-[a-zA-Z]*f[a-zA-Z]*\s+)?-[a-zA-Z]*r[a-zA-Z]*\s+)(/($|\s)|~|/home|/var|/etc|/usr|/opt|/sys|/boot|\$HOME)'; then
  echo "BLOCKED: Recursive delete on sensitive path." >&2; exit 2
fi
```

### Correction 4: Task 5 — Sanitize AGENT_TYPE in ALL 6 eval templates

**Problem:** Plan only sanitizes 2 of 6 templates. All 6 eval hooks use AGENT_TYPE in file paths.
**Fix:** Apply the same `AGENT_TYPE=$(echo "$AGENT_TYPE" | tr -cd 'a-zA-Z0-9-')` line after the jq extraction in ALL of:
- `track-agent-start.sh.tmpl`
- `track-session-count.sh.tmpl`
- `extract-learnings.sh.tmpl`
- `auto-promote-learnings.sh.tmpl`
- `validate-agent-output.sh.tmpl`
- `prompt-save-learnings.sh.tmpl`

### Correction 5: Task 6 Step 3 — Do NOT change block-git-commit.sh to exit 0

**Problem:** Changing from exit 2 to exit 0 when jq is missing defeats the purpose of commitPolicy=user. Without jq, commits would silently go through.
**Fix:** Keep `exit 2` for `block-git-commit.sh.tmpl`. Only add the `exit 0` jq guard to non-security hooks (eval hooks, auto-format, detect-new-file, inject-prompt-context). Add a comment to block-git-commit.sh explaining the deliberate fail-closed behavior:

```bash
if ! command -v jq &>/dev/null; then
  # Fail closed: if we cannot parse the command, block it to be safe
  echo '{"error": "jq not available — blocking bash for safety"}' >&2
  exit 2
fi
```

### Correction 6: Task 10 — NameError risk in dry_run mode

**Problem:** `temp_dir` is only defined inside `if not dry_run` but referenced in `except` block.
**Fix:** Initialize before the conditional:

```python
    temp_dir = None
    if not dry_run:
        temp_dir = tempfile.mkdtemp(prefix="buddyx-forge-")
        actual_output_dir = output_dir
        output_dir = temp_dir
    try:
```

And guard the except/else:
```python
    except Exception:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    else:
        if temp_dir:
            for item in Path(temp_dir).rglob("*"):
                ...
```

### Correction 7: Missing P0-03 — Add FORMATTER_CMD quoting

**Problem:** `{FORMATTER_CMD}` is injected bare into shell in `auto-format-new-files.sh.tmpl` line 26.
**Fix:** Add to Task 3 — in `auto-format-new-files.sh.tmpl`, change line 26:

```bash
cd "$PROJECT_DIR" && {FORMATTER_CMD} "$FILE_PATH" >/dev/null 2>&1
```

To (using eval for proper word-splitting of multi-word commands):
```bash
cd "$PROJECT_DIR" && eval '{FORMATTER_CMD}' '"$FILE_PATH"' >/dev/null 2>&1
```

Note: `eval` is needed here because the formatter may be multi-word (e.g., `vendor/bin/pint --config custom.xml`). Direct quoting would treat the entire string as one command. The `load_config()` regex already restricts formatter to safe chars `[a-zA-Z0-9/_\-. ]`, so eval injection is mitigated by input validation.

### Correction 8: Missing P0-09 — Agent template hardcoded hooks

**Problem:** Agent templates (`agent-domain.tmpl`, `agent-maintenance.tmpl`, etc.) and `build_team_lead_agent()` hardcode a `hooks:` YAML block referencing `block-git-commit.sh`. When `commitPolicy=claude`, this script doesn't exist.
**Fix:** This requires template changes (Phase 2/3 scope) since templates need conditional sections. For Phase 1, add a **documentation note** to the generated CLAUDE.md when `commitPolicy=claude` explaining that agent-level git hooks are inactive. The full template fix (making hook blocks conditional) is tracked as Phase 3 work.

---

## Recommendations (Cross-Phase)

These recommendations span multiple phases. Tracked here for visibility:

| # | Recommendation | Phase | Priority |
|---|---------------|-------|----------|
| R1 | Remove committed `__pycache__/` directory: `git rm --cached -r plugins/buddyx-forge/scripts/__pycache__/` | Phase 1 (quick win) | Do immediately |
| R2 | Add enum validation for `modelBudget`, `permissionLevel`, `commitPolicy`, `evalLevel` | Phase 1 | Task 1 + Correction 2 |
| R3 | Use randomly-named tempfile for config instead of predictable `/tmp/buddyx-forge-config.json` path. Update `commands/setup.md` to use `mktemp` pattern. | Phase 4 | Medium |
| R4 | Make jq a hard requirement OR add fallback parsing in shell scripts. Current hybrid (recommended but hooks depend on it) is inconsistent. | Phase 1 | Task 6 adds jq guards; full requirement upgrade in Phase 4 docs |
| R5 | Add `"generatedBy": "buddyx-forge@1.1.0"` field to `settings.json` for version tracking. Enables future migration detection. | Phase 5 | P2-03 |
| R6 | Split `generate.py` into modules (`builders/`, `validators/`, `templates/`) as it grows past 1,200 lines. | Phase 5 | P2-01 |
