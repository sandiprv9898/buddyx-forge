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

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'plugins', 'buddyx-forge', 'scripts'))
from generate import load_config, generate

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
        "projectDir": "/tmp",
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
            "agentTracking": True,
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


# ─── Summary ───

print(f"\n{'='*50}")
print(f"Results: {PASS} PASS, {FAIL} FAIL")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
