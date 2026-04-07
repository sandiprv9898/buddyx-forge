#!/usr/bin/env python3
"""
Basic tests for buddyx-forge generator.
Run: python3 tests/test_generator.py
"""

import json
import os
import shutil
import sys
import tempfile
import io

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'plugins', 'buddyx-forge', 'scripts'))
from generate import load_config, generate
from builders.frameworks import normalize_framework

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def make_config(overrides=None):
    config = {
        "projectName": "test-proj",
        "techStack": {
            "language": "php",
            "framework": "laravel",
            "frameworkVersion": "11",
            "hasFilament": False,
            "db": "postgresql",
            "formatter": "vendor/bin/pint",
            "testRunner": "php artisan test --filter="
        },
        "domains": ["core", "api"],
        "domainKeywords": {"core": "main", "api": "endpoint"},
        "hooks": {
            "blockCommits": True,
            "blockDangerous": True,
            "autoFormat": True,
            "contextInjection": True,
            "blockMigration": False
        },
        "sharedDb": None,
        "commitPolicy": "user",
        "permissionLevel": "balanced",
        "agentMemory": True,
        "promptTemplates": True,
        "evalLevel": "full",
        "modelBudget": "balanced",
        "mcpServers": [],
        "worktreeSymlinks": ["vendor"],
        "agentTeams": True
    }
    if overrides:
        config.update(overrides)
    return config


def write_config(config):
    path = os.path.join(tempfile.gettempdir(), "bf-test-config.json")
    with open(path, "w") as f:
        json.dump(config, f)
    return path


# ─── TEST 1: Config Validation ───

print("\n=== Config Validation ===")

try:
    load_config("/tmp/nonexistent.json")
    test("missing config file raises error", False)
except ValueError:
    test("missing config file raises error", True)

try:
    path = write_config({"projectName": "ab"})
    load_config(path)
    test("short name rejected", False)
except ValueError:
    test("short name rejected", True)

try:
    path = write_config(make_config({"domains": ["auth", "auth"]}))
    load_config(path)
    test("duplicate domains rejected", False)
except ValueError:
    test("duplicate domains rejected", True)

try:
    path = write_config(make_config({"projectName": "UPPER"}))
    load_config(path)
    test("uppercase name rejected", False)
except ValueError:
    test("uppercase name rejected", True)

path = write_config(make_config())
config = load_config(path)
test("valid config loads", config["projectName"] == "test-proj")


# ─── TEST 2: Generator Output — All 7 Frameworks ───

print("\n=== Framework Generation ===")

for fw in ["laravel", "nextjs", "django", "go", "rails", "react", "express"]:
    outdir = tempfile.mkdtemp()
    try:
        cfg = make_config({
            "techStack": {
                "language": "x", "framework": fw, "frameworkVersion": "1",
                "hasFilament": False, "db": "pg", "formatter": "fmt", "testRunner": "test"
            }
        })
        generate(cfg, os.path.join(outdir, ".claude"))

        # Check key files
        has_claude = os.path.exists(os.path.join(outdir, ".claude", "CLAUDE.md"))
        has_agents = os.path.exists(os.path.join(outdir, ".claude", "AGENTS.md"))
        has_settings = os.path.exists(os.path.join(outdir, ".claude", "settings.json"))

        # Check settings.json is valid JSON
        with open(os.path.join(outdir, ".claude", "settings.json")) as f:
            settings = json.load(f)
        valid_json = "hooks" in settings

        # Check review agent has framework-specific checklist
        review_path = os.path.join(outdir, ".claude", "agents", "test-proj-review.md")
        has_review = os.path.exists(review_path)

        # Count files
        file_count = sum(len(files) for _, _, files in os.walk(os.path.join(outdir, ".claude")))

        test(f"{fw}: generates files ({file_count})", file_count > 30)
        test(f"{fw}: CLAUDE.md exists", has_claude)
        test(f"{fw}: settings.json valid", valid_json)
    except Exception as e:
        test(f"{fw}: generation", False)
        print(f"    Error: {e}")
    finally:
        shutil.rmtree(outdir)


# ─── TEST 3: Optional Agents ───

print("\n=== Optional Agents ===")

outdir = tempfile.mkdtemp()
cfg = make_config({"sharedDb": "/other/project"})
generate(cfg, os.path.join(outdir, ".claude"))
test("shared DB → migration agent", os.path.exists(os.path.join(outdir, ".claude", "agents", "test-proj-migration.md")))
shutil.rmtree(outdir)

outdir = tempfile.mkdtemp()
cfg = make_config({"sharedDb": None, "mcpServers": ["custom"]})
cfg["techStack"]["framework"] = "express"
generate(cfg, os.path.join(outdir, ".claude"))
test("MCP + express → mcp-dev agent", os.path.exists(os.path.join(outdir, ".claude", "agents", "test-proj-mcp-dev.md")))
shutil.rmtree(outdir)

outdir = tempfile.mkdtemp()
cfg = make_config({"sharedDb": None, "mcpServers": []})
cfg["techStack"]["framework"] = "go"
generate(cfg, os.path.join(outdir, ".claude"))
test("Go no MCP → no mcp-dev", not os.path.exists(os.path.join(outdir, ".claude", "agents", "test-proj-mcp-dev.md")))
shutil.rmtree(outdir)


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

# evalLevel
try:
    cfg = make_config({"evalLevel": "ultra"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("invalid evalLevel rejected", False)
except ValueError:
    test("invalid evalLevel rejected", True)


# ─── TEST 4: Memory Flag ───

print("\n=== Memory Flag ===")

outdir = tempfile.mkdtemp()
cfg = make_config({"agentMemory": False})
generate(cfg, os.path.join(outdir, ".claude"))
test("agentMemory=false → no shared-learnings", not os.path.exists(os.path.join(outdir, ".claude", "agent-memory", "shared-learnings.md")))
shutil.rmtree(outdir)

outdir = tempfile.mkdtemp()
cfg = make_config({"agentMemory": True})
generate(cfg, os.path.join(outdir, ".claude"))
test("agentMemory=true → shared-learnings exists", os.path.exists(os.path.join(outdir, ".claude", "agent-memory", "shared-learnings.md")))
shutil.rmtree(outdir)


# ─── TEST 5: Permissions Framework-Aware ───

print("\n=== Framework-Aware Permissions ===")

for fw, expected_cmd in [("laravel", "php artisan"), ("django", "python manage.py"), ("go", "go build"), ("rails", "bundle exec"), ("express", "npx")]:
    outdir = tempfile.mkdtemp()
    cfg = make_config()
    cfg["techStack"]["framework"] = fw
    generate(cfg, os.path.join(outdir, ".claude"))
    with open(os.path.join(outdir, ".claude", "settings.json")) as f:
        settings = json.load(f)
    perms = str(settings.get("permissions", {}).get("allow", []))
    test(f"{fw}: has '{expected_cmd}' in permissions", expected_cmd in perms)
    shutil.rmtree(outdir)


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
    test("conservative: framework commands in ask", "go build" in perms_str)
finally:
    shutil.rmtree(outdir, ignore_errors=True)


# === Hookify Migration Rule ===
print("\n=== Hookify Migration Rule ===")

# Without sharedDb — should NOT block migrations
outdir = tempfile.mkdtemp()
try:
    cfg = make_config({"sharedDb": None})
    generate(cfg, os.path.join(outdir, ".claude"))
    hookify_path = os.path.join(outdir, ".claude", "hookify-rules.md")
    hookify_content = open(hookify_path).read()
    test("no sharedDb → no migration block in hookify", "Block migrations" not in hookify_content)
finally:
    shutil.rmtree(outdir, ignore_errors=True)

# With sharedDb — SHOULD block migrations
outdir = tempfile.mkdtemp()
try:
    cfg = make_config({"sharedDb": "/other/project"})
    generate(cfg, os.path.join(outdir, ".claude"))
    hookify_path = os.path.join(outdir, ".claude", "hookify-rules.md")
    hookify_content = open(hookify_path).read()
    test("sharedDb set → migration block in hookify", "Block migrations" in hookify_content)
finally:
    shutil.rmtree(outdir, ignore_errors=True)


# === Version Stamp ===
print("\n=== Version Stamp ===")

outdir = tempfile.mkdtemp()
try:
    cfg = make_config()
    generate(cfg, os.path.join(outdir, ".claude"))
    with open(os.path.join(outdir, ".claude", "settings.json")) as f:
        settings = json.load(f)
    test("settings.json has buddyxForgeVersion", "buddyxForgeVersion" in settings)
    test("version is 1.1.1", settings.get("buddyxForgeVersion") == "1.1.1")
finally:
    shutil.rmtree(outdir, ignore_errors=True)


# === SharedDb Path Validation ===
print("\n=== SharedDb Path Validation ===")

try:
    cfg = make_config({"sharedDb": "/path; rm -rf /"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("dangerous sharedDb path rejected", False)
except ValueError:
    test("dangerous sharedDb path rejected", True)

# Path traversal should be REJECTED
try:
    cfg = make_config({"sharedDb": "../other-project"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("path traversal sharedDb rejected", False)
except ValueError:
    test("path traversal sharedDb rejected", True)

# Absolute path without traversal should be accepted
try:
    cfg = make_config({"sharedDb": "/home/user/other-project"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("absolute sharedDb path accepted", True)
except ValueError:
    test("absolute sharedDb path accepted", False)

# Relative path without traversal should be accepted
try:
    cfg = make_config({"sharedDb": "sibling-project"})
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("relative sharedDb path accepted", True)
except ValueError:
    test("relative sharedDb path accepted", False)


# === Framework Validation ===
print("\n=== Framework Validation ===")

# Unsupported framework should be rejected
try:
    cfg = make_config()
    cfg["techStack"]["framework"] = "flutter"
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("unsupported framework 'flutter' rejected", False)
except ValueError:
    test("unsupported framework 'flutter' rejected", True)

try:
    cfg = make_config()
    cfg["techStack"]["framework"] = "spring-boot"
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("unsupported framework 'spring-boot' rejected", False)
except ValueError:
    test("unsupported framework 'spring-boot' rejected", True)

# Supported framework should pass
try:
    cfg = make_config()
    cfg["techStack"]["framework"] = "nextjs"
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    test("supported framework 'nextjs' accepted", True)
except ValueError:
    test("supported framework 'nextjs' accepted", False)


# === Hooks Key Warning ===
print("\n=== Hooks Key Warning ===")

# Unknown hook keys should trigger warning (on stderr) but not error
old_stderr = sys.stderr
sys.stderr = io.StringIO()
try:
    cfg = make_config()
    cfg["hooks"]["unknownKey"] = True
    cfg_path = write_config(cfg)
    load_config(cfg_path)
    stderr_output = sys.stderr.getvalue()
    test("unknown hook key produces warning", "unknownKey" in stderr_output)
except ValueError:
    test("unknown hook key produces warning (should warn, not error)", False)
finally:
    sys.stderr = old_stderr


# === normalize_framework ===
print("\n=== normalize_framework ===")

test("normalize: next.js → nextjs", normalize_framework("next.js") == "nextjs")
test("normalize: Next.js → nextjs", normalize_framework("Next.js") == "nextjs")
test("normalize: laravel unchanged", normalize_framework("laravel") == "laravel")
test("normalize: node → nodejs", normalize_framework("node") == "nodejs")


# === Next.js Alias Consistency ===
print("\n=== Next.js Alias Consistency ===")

outdir = tempfile.mkdtemp()
try:
    # Generate with "next.js" (the dot version) — should work identically to "nextjs"
    cfg = make_config({
        "techStack": {
            "language": "ts", "framework": "next.js", "frameworkVersion": "14",
            "hasFilament": False, "db": "pg", "formatter": "prettier", "testRunner": "jest"
        }
    })
    generate(cfg, os.path.join(outdir, ".claude"))

    # Verify it generated proper Next.js content (not fallback to Laravel defaults)
    with open(os.path.join(outdir, ".claude", "settings.json")) as f:
        settings = json.load(f)
    perms = str(settings.get("permissions", {}).get("allow", []))
    test("next.js alias: has 'npx' in permissions", "npx" in perms)
    test("next.js alias: no 'php' in permissions", "php" not in perms)

    # Check RULES.md has Next.js rules
    rules_path = os.path.join(outdir, ".claude", "skills", "test-proj", "RULES.md")
    rules_content = open(rules_path).read()
    test("next.js alias: RULES.md has Next.js section", "Next.js" in rules_content or "Server Components" in rules_content)
finally:
    shutil.rmtree(outdir, ignore_errors=True)


# ─── Summary ───

print(f"\n{'='*50}")
print(f"Results: {PASS} PASS, {FAIL} FAIL")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
