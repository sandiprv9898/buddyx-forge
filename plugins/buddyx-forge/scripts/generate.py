#!/usr/bin/env python3
"""
buddyx-forge generator — creates .claude/ directory from config + templates.
Zero external dependencies. Python 3.8+ stdlib only.
"""

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"


def load_config(config_path: str) -> dict:
    """Load and validate the config JSON."""
    if not Path(config_path).exists():
        raise ValueError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    # Validate required keys
    required_keys = ["projectName", "domains", "techStack", "hooks", "commitPolicy", "permissionLevel", "modelBudget"]
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    # Validate project name
    name = config.get("projectName", "")
    if not re.match(r'^[a-z][a-z0-9\-]{2,19}$', name):
        raise ValueError(f"Invalid project name: '{name}'. Must be 3-20 chars, lowercase alphanumeric + hyphens.")

    # Validate domains not empty
    if not config.get("domains"):
        raise ValueError("At least one domain is required.")

    # Validate no duplicate domains
    domains = config["domains"]
    if len(domains) != len(set(domains)):
        raise ValueError(f"Duplicate domain names found: {[d for d in domains if domains.count(d) > 1]}")

    # Validate each domain name
    for domain in domains:
        if not re.match(r'^[a-z][a-z0-9\-]{1,30}$', domain):
            raise ValueError(f"Invalid domain name: '{domain}'")

    # Validate formatter command (security)
    formatter = config.get("techStack", {}).get("formatter", "")
    if formatter and not re.match(r'^[a-zA-Z0-9/_\-. ]+$', formatter):
        raise ValueError(f"Invalid formatter command: '{formatter}'")

    return config


def render_template(template_name: str, replacements: dict) -> str:
    """Read a .tmpl file and perform string replacements."""
    tmpl_path = TEMPLATES_DIR / template_name
    if not tmpl_path.exists():
        raise FileNotFoundError(f"Required template missing: {tmpl_path}")
    content = tmpl_path.read_text()
    for key, value in replacements.items():
        content = content.replace(f"{{{key}}}", str(value))
    # Warn about unreplaced placeholders (exclude bash ${VAR} and HTML {{VAR}})
    remaining = re.findall(r'(?<!\$)(?<!\{)\{[A-Z][A-Z_]+\}(?!\})', content)
    if remaining:
        print(f"WARNING: Unreplaced placeholders in {template_name}: {remaining}", file=sys.stderr)
    return content


dry_run_count = 0


def write_file(output_dir: str, rel_path: str, content: str, dry_run: bool = False):
    """Write content to a file, creating directories as needed."""
    global dry_run_count
    full_path = Path(output_dir) / rel_path
    if dry_run:
        dry_run_count += 1
        print(f"  WOULD CREATE: {full_path}")
        return
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)


def make_executable(output_dir: str, rel_path: str, dry_run: bool = False):
    """Make a file executable."""
    if dry_run:
        return
    full_path = Path(output_dir) / rel_path
    if full_path.exists():
        full_path.chmod(full_path.stat().st_mode | 0o111)


# ─── BUILDER FUNCTIONS (complex files that need logic, not templates) ───


def build_settings_json(config: dict) -> str:
    """Build settings.json programmatically."""
    name = config["projectName"]
    formatter = config.get("techStack", {}).get("formatter", "")
    hooks_config = config.get("hooks", {})
    eval_level = config.get("evalLevel", "none")
    commit_policy = config.get("commitPolicy", "user")
    perm_level = config.get("permissionLevel", "balanced")
    worktree_symlinks = config.get("worktreeSymlinks", [])
    agent_teams = config.get("agentTeams", False)

    # Build permissions
    allow = ["WebSearch"]
    ask = []

    # Framework-aware permission commands
    framework = config.get("techStack", {}).get("framework", "laravel").lower()
    fw_commands = {
        "laravel": {
            "allow": ["Bash(php -l *)", "Bash(php artisan *)", "Bash(composer show *)", "Bash(composer dump-autoload *)"],
            "ask": ["Bash(composer update *)", "Bash(composer require *)"],
        },
        "django": {
            "allow": ["Bash(python3 *)", "Bash(pip show *)", "Bash(python manage.py *)"],
            "ask": ["Bash(pip install *)", "Bash(pip uninstall *)"],
        },
        "go": {
            "allow": ["Bash(go build *)", "Bash(go test *)", "Bash(go vet *)", "Bash(go run *)"],
            "ask": ["Bash(go install *)", "Bash(go get *)"],
        },
        "rails": {
            "allow": ["Bash(ruby *)", "Bash(bundle exec *)", "Bash(rails *)"],
            "ask": ["Bash(bundle install *)", "Bash(bundle update *)", "Bash(gem install *)"],
        },
    }
    # Next.js, React, Node.js, Express, Fastify, NestJS — all JS/TS
    js_commands = {
        "allow": ["Bash(npx *)", "Bash(node *)", "Bash(tsx *)"],
        "ask": ["Bash(npm install *)", "Bash(npm uninstall *)", "Bash(yarn add *)"],
    }
    for js_fw in ("nextjs", "next.js", "react", "nodejs", "node", "express", "fastify", "nestjs", "hono"):
        fw_commands[js_fw] = js_commands

    fw = fw_commands.get(framework, {"allow": [], "ask": []})

    if perm_level == "conservative":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend(["Bash(ls *)", "Bash(find *)"])
    elif perm_level == "balanced":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend([
            "Bash(wc *)", "Bash(ls *)", "Bash(find *)",
            "Bash(sort *)", "Bash(diff *)", "Bash(python3 *)",
        ])
        allow.extend(fw.get("allow", []))
        ask.extend(["Bash(git *)", "Bash(rm *)", "Bash(chmod *)"])
        ask.extend(fw.get("ask", []))
    elif perm_level == "permissive":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend([
            "Bash(wc *)", "Bash(ls *)", "Bash(find *)",
            "Bash(sort *)", "Bash(diff *)", "Bash(python3 *)",
            "Bash(xdg-open *)",
        ])
        allow.extend(fw.get("allow", []))
        allow.extend(fw.get("ask", []))
        ask.extend(["Bash(git *)", "Bash(rm *)", "Bash(chmod *)"])

    # Add MCP permissions
    for mcp in config.get("mcpServers", []):
        allow.append(f"mcp__{mcp}__*")

    # Build hooks
    hooks = {}

    if hooks_config.get("contextInjection", False):
        hooks["UserPromptSubmit"] = [{"hooks": [
            {"type": "command", "command": ".claude/scripts/inject-prompt-context.sh"}
        ]}]

    pre_tool_use = []
    if hooks_config.get("blockDangerous", False):
        pre_tool_use.append({
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": ".claude/scripts/safety-guard.sh"}]
        })
    if commit_policy == "user":
        pre_tool_use.append({
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-git-commit.sh"}]
        })
    else:
        # commitPolicy="claude" — add git to allow permissions
        allow.extend(["Bash(git add *)", "Bash(git commit *)", "Bash(git push *)"])
    if hooks_config.get("blockMigration", False):
        pre_tool_use.append({
            "matcher": "Write|Edit",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-migration.sh"}]
        })
    if pre_tool_use:
        hooks["PreToolUse"] = pre_tool_use

    post_tool_use = []
    if hooks_config.get("autoFormat", False):
        post_tool_use.append({
            "matcher": "Write",
            "hooks": [{"type": "command", "command": ".claude/scripts/auto-format-new-files.sh"}]
        })
    post_tool_use.append({
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": ".claude/scripts/detect-new-file-created.sh"}]
    })
    if post_tool_use:
        hooks["PostToolUse"] = post_tool_use

    # Eval hooks
    if eval_level in ("full", "basic"):
        hooks["SubagentStart"] = [{"matcher": f"{name}-*", "hooks": [
            {"type": "command", "command": ".claude/scripts/eval/track-agent-start.sh"},
        ]}]
        stop_hooks = [
            {"type": "command", "command": ".claude/scripts/eval/track-session-count.sh"},
        ]
        if eval_level == "full":
            stop_hooks.extend([
                {"type": "command", "command": ".claude/scripts/eval/validate-agent-output.sh"},
                {"type": "command", "command": ".claude/scripts/eval/extract-learnings.sh"},
                {"type": "command", "command": ".claude/scripts/eval/prompt-save-learnings.sh"},
                {"type": "command", "command": ".claude/scripts/eval/auto-promote-learnings.sh"},
            ])
        hooks["SubagentStop"] = [{"matcher": f"{name}-*", "hooks": stop_hooks}]

    # PreCompact
    hooks["PreCompact"] = [{"hooks": [
        {"type": "command", "command": "echo '{\"systemMessage\": \"PRESERVE: current task goal, files changed, agent delegations in progress, any user decisions made this session.\"}'"}
    ]}]

    # Build env
    env = {"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "75"}
    if agent_teams:
        env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"

    settings = {
        "permissions": {"allow": allow, "ask": ask, "deny": []},
        "hooks": hooks,
        "env": env,
        "plansDirectory": ".claude/plans",
        "autoMemoryEnabled": True,
    }

    if worktree_symlinks:
        settings["worktree"] = {"symlinkDirectories": worktree_symlinks}

    return json.dumps(settings, indent=4)


def build_domain_map(config: dict) -> str:
    """Build domain-map.md — one section per domain."""
    sections = []
    for domain in config["domains"]:
        section = f"""## {domain}

### Read/Write
<!-- Populated by /buddyx-forge:scan or AI customization -->
<!-- Run /buddyx-forge:scan after adding code to populate this section -->

### Read Only
<!-- Dependencies from other domains -->"""
        sections.append(section)
    header = "# Domain Map - File Ownership\n\nEach domain agent owns specific files (read/write). Files not listed are READ ONLY for that agent.\n\n---\n\n"
    return header + "\n\n---\n\n".join(sections) + "\n"


def build_orchestrator_skill(config: dict) -> str:
    """Build the orchestrator SKILL.md."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    keywords = config.get("domainKeywords", {})
    model_budget = config.get("modelBudget", "balanced")
    rw_model = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}[model_budget]
    ro_model = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}[model_budget]

    # Build keywords table
    kw_rows = []
    for d in domains:
        kw = keywords.get(d, d.replace("-", ", "))
        kw_rows.append(f"| {d} | {kw} |")
    kw_table = "| Domain | Keywords |\n|--------|----------|\n" + "\n".join(kw_rows)

    # Build agent inventory with actual model from config
    inv_rows = []
    for d in domains:
        inv_rows.append(f"| {name}-{d} | {rw_model} | project | {d} domain specialist |")
    inv_rows.extend([
        f"| {name}-discovery | {ro_model} | project | pre-implementation research (READ ONLY) |",
        f"| {name}-db | {ro_model} | project | database schema (READ ONLY) |",
        f"| {name}-review | {ro_model} | project | code quality gate (READ ONLY) |",
        f"| {name}-team-lead | sonnet | project | multi-agent coordinator |",
        f"| {name}-maintenance | sonnet | project | context file maintenance |",
    ])
    inv_table = "| Agent | Model | Memory | Description |\n|-------|-------|--------|-------------|\n" + "\n".join(inv_rows)

    return f"""---
name: {name}
description: Use when working on any {title} task — auditing, implementing features, fixing bugs, analyzing code.
disable-model-invocation: true
---

# {title} — Project Orchestrator

Orchestrator for the {title} project. Parses intent, selects domain/infrastructure agents, dispatches with context.

## STRICT RULES

- NEVER commit code. User commits manually.
- NEVER modify files outside the assigned domain ownership.
- ALWAYS run review-agent on any code changes before reporting done.

## Domain Detection Keywords

{kw_table}

## Dispatch Strategy

- **Single agent** (1 domain, no DB change): dispatch domain agent only
- **Sequential chain** (DB change needed): db-agent → domain-agent → review-agent
- **Parallel** (independent domains): dispatch in parallel → review-agent
- **Full sweep** (all domains): all domain agents → review-agent

## Agent Inventory

{inv_table}

## Inter-Agent Communication

- **DONE** → dispatch review-agent (if code changed)
- **DONE_WITH_CONCERNS** → read concerns, decide if action needed
- **NEEDS_CONTEXT** → dispatch requested agent, re-dispatch original
- **BLOCKED** → stop, ask user for guidance
"""


def _get_framework_checklist(config: dict) -> str:
    """Return framework-specific review checklist."""
    framework = config.get("techStack", {}).get("framework", "laravel").lower()
    has_filament = config.get("techStack", {}).get("hasFilament", False)

    if framework == "laravel":
        filament = ""
        if has_filament:
            filament = """
### Filament 3
- [ ] Form uses Section → Tabs → Tab → Grid pattern
- [ ] Translation keys: dot notation
- [ ] `->authorize()` on actions
- [ ] `ResourceName::getUrl()` not `route()`
- [ ] Unique validation includes soft delete column check
"""
        return f"""### Laravel
- [ ] `match` over `switch`
- [ ] Helpers (auth(), str()) not Facades
- [ ] `$fillable` updated with inline comments
- [ ] Relationship keys always explicit
- [ ] Activity logging if applicable
{filament}
### Performance
- [ ] Eager loading present (no N+1)
- [ ] `->exists()` not `->count() > 0`

### Security
- [ ] `$fillable` defined (not `$guarded = []`)
- [ ] No string concat in `whereRaw()`
- [ ] No `addslashes()` for SQL

### Imports
- [ ] Grouped and alphabetical
- [ ] No inline FQCN"""

    elif framework in ("nextjs", "next.js"):
        return """### Next.js / React
- [ ] Server Components by default — `'use client'` only when needed
- [ ] `next/image` not raw `<img>`, `next/link` not raw `<a>`
- [ ] No `useEffect` for data fetching in Server Components
- [ ] TypeScript strict mode — no `any`
- [ ] Props destructured in function signature

### Performance
- [ ] Dynamic imports for heavy components
- [ ] `loading.tsx` for async routes
- [ ] No layout shifts (width/height on images)

### Security
- [ ] Zod validation on API inputs
- [ ] `NEXT_PUBLIC_` prefix only for client-exposed env vars
- [ ] No server secrets in client components

### Imports
- [ ] Absolute imports with `@/` prefix
- [ ] Grouped: React → Next → third-party → local"""

    elif framework == "django":
        return """### Django
- [ ] Business logic in services, not views
- [ ] Serializer per use case (list/detail/create)
- [ ] `permission_classes` on every view
- [ ] Validators at model level

### Performance
- [ ] `select_related()` for ForeignKey (N+1)
- [ ] `prefetch_related()` for ManyToMany (N+1)
- [ ] `exists()` not `count() > 0`
- [ ] `bulk_create()` for batch operations

### Security
- [ ] Strong parameters via serializer validation
- [ ] `IsAuthenticated` permission on views
- [ ] No raw SQL with string formatting

### Imports
- [ ] Grouped: stdlib → Django → third-party → local"""

    elif framework == "go":
        return """### Go
- [ ] All errors checked — no `_ = err`
- [ ] Errors wrapped with context: `fmt.Errorf("doing X: %w", err)`
- [ ] `context.Context` as first param for I/O functions
- [ ] Interfaces defined where consumed

### Performance
- [ ] `Preload()` for GORM (N+1)
- [ ] Goroutines terminate (use context)
- [ ] No goroutine leaks

### Security
- [ ] Parameterized SQL queries
- [ ] Input validation before processing
- [ ] No secrets in code

### Imports
- [ ] Grouped: stdlib → third-party → local
- [ ] `goimports` formatted"""

    elif framework == "rails":
        return """### Rails
- [ ] Business logic in services, not controllers
- [ ] Strong parameters: `params.require().permit()`
- [ ] `dependent:` on has_many/has_one
- [ ] Validations at model level

### Performance
- [ ] `includes()` for eager loading (N+1)
- [ ] `find_each` for batch processing
- [ ] `exists?` not `count > 0`

### Security
- [ ] Authorization check on every action
- [ ] CSRF protection enabled
- [ ] No mass assignment without permit

### Imports
- [ ] Follow Zeitwerk naming conventions"""

    elif framework == "react":
        return """### React
- [ ] Functional components only — no class components
- [ ] Custom hooks prefixed with `use`
- [ ] No `useEffect` for data fetching — use React Query/SWR
- [ ] Props destructured in function signature
- [ ] TypeScript strict — no `any`

### Performance
- [ ] `React.lazy()` for code splitting
- [ ] Virtualize long lists
- [ ] No objects/arrays created in render

### Security
- [ ] User input sanitized before rendering
- [ ] No secrets in frontend code
- [ ] Environment vars prefixed correctly (VITE_ or REACT_APP_)

### Imports
- [ ] Absolute imports with `@/` prefix
- [ ] Grouped: React → third-party → local"""

    elif framework in ("nodejs", "node", "express", "fastify", "nestjs", "hono"):
        return """### Node.js Backend
- [ ] Input validation on every endpoint (Zod/Joi)
- [ ] Business logic in services, not routes
- [ ] async/await — no raw callbacks
- [ ] Structured logging — no console.log in production
- [ ] Custom error classes with error middleware

### Performance
- [ ] N+1 prevented (Prisma `include` / Mongoose `populate`)
- [ ] Connection pooling configured
- [ ] Background jobs for heavy processing

### Security
- [ ] JWT tokens: short-lived access + refresh
- [ ] Rate limiting on all endpoints
- [ ] CORS whitelist — not wildcard
- [ ] Helmet middleware for security headers
- [ ] No secrets in code

### Imports
- [ ] ES Modules (import/export)
- [ ] Grouped: Node builtins → third-party → local"""

    else:
        return """### General
- [ ] No duplicate code
- [ ] Error handling present
- [ ] No hardcoded secrets
- [ ] Tests exist for new code"""


def build_review_agent(config: dict) -> str:
    """Build the review agent with framework-specific checklist."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    model = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}.get(config.get("modelBudget", "balanced"), "haiku")

    checklist = _get_framework_checklist(config)

    return f"""---
name: {name}-review
description: Code quality gate. MUST be used PROACTIVELY after any code changes. Auto-trigger when code was written, edited, or created.
tools: Read, Grep, Glob, Bash
disallowedTools: Agent, Write, Edit
model: {model}
memory: project
maxTurns: 20
background: true
skills:
  - {name}/RULES
---

You are the Code Quality Gate for the {title} project. READ ONLY — review and report, never modify.

## Before You Start
1. READ `.claude/agent-memory/{name}-review/MEMORY.md`
2. READ `.claude/agent-memory/shared-learnings.md`

CRITICAL: You did NOT write this code. Review it critically. Do NOT say "looks good" unless verified.

## Constraints
- NEVER commit code.
- NEVER modify any files.

## Checklist

{checklist}

## Response Format
```
### file-path.php
Status: PASS | FAIL
Violations (if FAIL):
1. [RULE] Description (line X) — Fix: ...

### Overall: PASS | FAIL (N violations across M files)
```

## After You Finish
Report findings. Include new patterns, gotchas, violations found.
If you verified a hypothesis: `[CONFIRM: pattern description]`
"""


def build_team_lead_agent(config: dict) -> str:
    """Build the team-lead agent."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]

    domain_list = ", ".join([f"{name}-{d}" for d in domains])

    return f"""---
name: {name}-team-lead
description: Team lead for multi-agent operations. Use when full module audit, cross-domain refactoring, or parallel implementation across multiple domains is needed.
tools: Read, Grep, Glob, Bash, Agent
disallowedTools: Write, Edit
model: sonnet
memory: project
maxTurns: 40
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ".claude/scripts/block-git-commit.sh"
---

You are the Team Lead for {title} multi-agent operations.

## Before You Start
1. READ `.claude/agent-memory/{name}-team-lead/MEMORY.md`
2. READ `.claude/agent-memory/shared-learnings.md`

## Domain Agents Available
{domain_list}

## Infrastructure Agents
{name}-discovery, {name}-db, {name}-review, {name}-maintenance

## How to Coordinate

### 1. Break work into independent tasks per domain
### 2. Dispatch workers (max 5 agents simultaneously)
### 3. Collect results — handle DONE/NEEDS_CONTEXT/BLOCKED
### 4. Dispatch {name}-review as the final step
### 5. Present unified results

## Task Assignment

| Task Type | Agents |
|-----------|--------|
| Full audit | All domain agents (parallel) + {name}-review |
| Cross-domain refactor | Only affected domain agents (sequential if dependent) |
| New feature | {name}-discovery → {name}-db → domain agent → {name}-review |

## Constraints
- NEVER commit code.
- NEVER dispatch more than 5 agents simultaneously.
- ALWAYS dispatch {name}-review as the final step.

## After You Finish
Report findings. Include new patterns, gotchas.
"""


def build_claude_md(config: dict) -> str:
    """Build complete CLAUDE.md — no AI needed."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    framework = config.get("techStack", {}).get("framework", "laravel").title()
    version = config.get("techStack", {}).get("frameworkVersion", "")
    commit_policy = config.get("commitPolicy", "user")
    has_filament = config.get("techStack", {}).get("hasFilament", False)
    prompt_templates = config.get("promptTemplates", True)

    # Framework note
    fw_note = ""
    if commit_policy == "user":
        fw_note += "- NEVER commit code — user commits manually.\n"
    if config.get("sharedDb"):
        fw_note += f"- NEVER create migrations here — migrations go to `{config['sharedDb']}`\n"
    if has_filament:
        fw_note += "- Filament 3 resources use Section → Tabs → Tab → Grid pattern.\n"

    # Agent delegation table
    rows = []
    for d in domains:
        rows.append(f"| {d.replace('-', ' ').title()} tasks | {name}-{d} |")
    rows.extend([
        f"| Unknown domain/feature | {name}-discovery |",
        f"| Check DB schema | {name}-db |",
        f"| After any code change | {name}-review (auto) |",
        f"| Multi-domain task | {name}-team-lead |",
        f"| Refresh context files | {name}-maintenance |",
    ])
    delegation = "| When To Use | Agent |\n|-------------|-------|\n" + "\n".join(rows)

    # Prompt templates section
    prompt_section = ""
    if prompt_templates:
        examples = ""
        if len(domains) >= 1:
            d = domains[0]
            examples += f"fix: {d.title()}Service — returns 500 on edge case. Only touch the service file.\n\n"
        if len(domains) >= 2:
            d = domains[1]
            examples += f"add: export PDF to {d.title()}Resource — include date range filter.\n\n"
        if len(domains) >= 3:
            d = domains[2]
            examples += f"audit: {d} module — check code quality, security, permissions.\n\n"

        prompt_section = f"""
## How to Write Prompts

### Format
[action]: [file/location] — [what's wrong or what to do]. [scope limit].

### Actions
| Action | Meaning |
|--------|---------|
| `fix:` | Something is broken |
| `add:` | New feature |
| `refactor:` | Improve without changing behavior |
| `check:` / `audit:` | Review and report |
| `update:` | Change existing behavior |
| `optimize:` | Improve performance |

### Examples
{examples}
### Modifiers
- `only touch [file]` — limits scope
- `don't modify [file]` — excludes a file
- `show me before changing` — preview first
- `read only` — just analyze

### If My Prompt Is Missing Something, Ask Me:
| Missing Part | Ask |
|---|---|
| No file/location | "Which file or module should I look at?" |
| No clear problem | "What's the current behavior vs expected behavior?" |
| No scope limit | "Should I only touch [file], or can I change related files too?" |
| Ambiguous action | "Do you want me to fix the bug, or refactor the approach?" |
| No reference | "Is there a working example I should match?" |
"""

    return f"""# Project Rules

## This is a {framework} {version} Project

{fw_note}

## Working Rules

- **NEVER ASSUME** — if you don't know something, READ the code. Never guess table names, column types, or behavior.
- **ASK IF UNCLEAR** — if requirements are ambiguous, ask the user.
- **VERIFY** — before claiming anything is correct, verify from the code.
- If a task touches more than 3 files, stop and ask for confirmation.
- Never delete or overwrite files without explicit permission.
- Read files before modifying them — never assume content.
- Keep changes minimal — only change what's needed.

## Code Style Rules

### No Inline FQCN
- Always add a proper `use` import at the top of the file and reference the short class name.

## Agent Delegation

{delegation}

{prompt_section}

## Shared Knowledge

Before starting any task, read `.claude/agent-memory/shared-learnings.md` for patterns and conventions.

**Entries marked `[NEW n/3]`** — unconfirmed, test when relevant.
**Entries marked `[CONFIRMED]`** — apply by default, proven across 3+ tasks.

## Flows & Diagrams

**"create flow"** → simple markdown .md file with step arrows
  - Save to `.claude/docs/{{feature}}/flows.md`

**"diagram:"** → visual interactive HTML (Mermaid, zoom/pan)
  - Types: ER, flowchart, sequence, architecture, state

**On demand only:** Only create flows/diagrams when user explicitly asks.
"""


def build_rules_md(config: dict) -> str:
    """Build complete RULES.md with framework-specific rules — no AI needed."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    framework = config.get("techStack", {}).get("framework", "laravel").lower()
    commit_policy = config.get("commitPolicy", "user")
    has_filament = config.get("techStack", {}).get("hasFilament", False)

    # Universal rules
    rules = f"""# MANDATORY RULES — All {title} agents must follow

## BEFORE WRITING ANY CODE

1. READ the file you are about to modify (never assume content)
2. READ one sibling file in the same directory to confirm patterns
3. SEARCH the codebase for existing helpers, services, traits — NEVER duplicate
4. If task involves data, verify table structure BEFORE writing model code

"""

    # Framework-specific rules
    if framework == "laravel":
        rules += """## Laravel 11

- `match` over `switch` always
- Helpers: `auth()`, `redirect()`, `str()` — NOT Facades
- Observers via `#[ObservedBy([Observer::class])]` attribute
- Scopes via `#[ScopedBy(ScopeClass::class)]` attribute
- No `Model::query()->create()` — use `Model::create()`
- Relationship keys always explicit: `->belongsTo(Model::class, 'FK', 'PK')`
- `$fillable` defined on every model (never `$guarded = []`)
- No empty catch blocks — at minimum log the error

"""
        if has_filament:
            rules += """## Filament 3

- Forms: Section → Tabs → Tab → Grid pattern (if multi-field)
- Translation keys: `__('module.form.field_name')` dot notation
- URLs: `ResourceName::getUrl()` — never `route()`
- Actions: `->authorize('ability')` on every action
- Unique validation must exclude soft-deleted records
- Notifications: `Notification::make()->success()->title('...')->send()`

"""

    elif framework in ("nextjs", "next.js"):
        rules += """## Next.js

- Default to Server Components — only add 'use client' when needed
- Use `next/image` for images, `next/link` for links
- No `useEffect` for data fetching in Server Components — fetch() directly
- TypeScript strict mode — no `any`
- API routes: validate input with Zod
- Dynamic imports for heavy components

"""

    elif framework == "react":
        rules += """## React

- Functional components only — no class components
- Custom hooks prefixed with `use`
- React Query/SWR for data fetching — never `useEffect` + `fetch`
- TypeScript strict mode — no `any`
- Props destructured in function signature

"""

    elif framework in ("nodejs", "node", "express", "fastify", "nestjs", "hono"):
        rules += """## Node.js Backend

- ES Modules (import/export) — not CommonJS
- async/await for all async — no raw callbacks
- Input validation on EVERY endpoint (Zod/Joi)
- Business logic in services, not routes
- Structured logging (pino/winston) — no console.log in production
- Custom error classes with centralized error middleware

"""

    elif framework == "django":
        rules += """## Django

- Business logic in services, not views
- `select_related()` for ForeignKey, `prefetch_related()` for ManyToMany
- Serializer per use case (list/detail/create)
- `permission_classes` on every view
- Validators at model level
- Factory Boy for test data

"""

    elif framework == "go":
        rules += """## Go

- Always check errors — no `_ = err`
- Wrap errors: `fmt.Errorf("context: %w", err)`
- `context.Context` as first param for I/O functions
- Interfaces defined where consumed
- `Preload()` for GORM to prevent N+1
- Table-driven tests

"""

    elif framework == "rails":
        rules += """## Rails

- Business logic in services, not controllers
- Strong parameters: `params.require().permit()`
- `dependent:` on has_many/has_one
- `includes()` for eager loading
- Validations at model level
- RSpec + Factory Bot for tests

"""

    # Universal performance + security
    rules += """## Performance

- Eager loading: prevent N+1 queries
- `exists()` not `count() > 0`
- Debounce on live search inputs

## Security

- Never use `$guarded = []` — always define `$fillable` or equivalent
- No string concatenation in raw SQL — use parameterized queries
- Validate all user input at system boundaries
- No secrets in code — use environment variables

## Imports

- Group: framework → third-party → local
- Always use imports at top of file — never inline fully qualified names

## AFTER CODE CHANGES

1. Run tests if they exist
2. Verify eager loading covers all new relationship usage
3. Show evidence: what changed, why, how to verify
4. Status: DONE | DONE_WITH_CONCERNS | PARTIAL_DONE | NEEDS_CONTEXT | BLOCKED

## NEVER DO

- Add features the user didn't ask for
- Say "done" without showing evidence
- Modify files outside your domain ownership
"""

    if commit_policy == "user":
        rules += "- Commit code (user commits manually)\n"

    if config.get("sharedDb"):
        rules += f"- Create migrations in this project (migrations go to `{config['sharedDb']}`)\n"

    # Detected conventions placeholder
    rules += """
## Detected Conventions

<!-- Run /buddyx-forge:scan to detect conventions from your codebase -->
<!-- Table naming, timestamps, soft deletes, enum folder, primary key pattern -->
"""

    return rules


# ─── MAIN GENERATOR ───


def generate(config: dict, output_dir: str, dry_run: bool = False):
    """Generate the complete .claude/ directory."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    hooks_cfg = config.get("hooks", {})
    eval_level = config.get("evalLevel", "none")
    has_memory = config.get("agentMemory", True)
    commit_policy = config.get("commitPolicy", "user")
    model_budget = config.get("modelBudget", "balanced")
    formatter = config.get("techStack", {}).get("formatter", "")
    test_runner = config.get("techStack", {}).get("testRunner", "")

    # Model mapping
    ro_model = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}[model_budget]
    rw_model = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}[model_budget]

    if dry_run:
        print(f"\n=== buddyx-forge DRY RUN for '{name}' ===\n")

    # Common replacements for templates
    common = {
        "PROJECT_NAME": name,
        "PROJECT_TITLE": title,
        "READONLY_MODEL": ro_model,
        "DOMAIN_MODEL": rw_model,
        "FORMATTER_CMD": formatter,
        "TEST_RUNNER": test_runner,
    }

    # ─── Phase A: Python-generated files ───

    # 1. settings.json (builder)
    write_file(output_dir, "settings.json", build_settings_json(config), dry_run)

    # 2. Domain agents (template)
    for domain in domains:
        domain_title = domain.replace("-", " ").title()
        replacements = {
            **common,
            "DOMAIN": domain,
            "DOMAIN_TITLE": domain_title,
            "DOMAIN_DESCRIPTION": f"{domain_title} specialist. Use when working on {domain}-related tasks.",
        }
        content = render_template("agent-domain.tmpl", replacements)
        write_file(output_dir, f"agents/{name}-{domain}.md", content, dry_run)

    # 3. Infrastructure agents (template + builders)
    for agent_tmpl in ["agent-discovery.tmpl", "agent-db.tmpl", "agent-maintenance.tmpl"]:
        content = render_template(agent_tmpl, common)
        agent_name = agent_tmpl.replace("agent-", "").replace(".tmpl", "")
        write_file(output_dir, f"agents/{name}-{agent_name}.md", content, dry_run)

    # Review agent (builder)
    write_file(output_dir, f"agents/{name}-review.md", build_review_agent(config), dry_run)

    # Team-lead agent (builder)
    write_file(output_dir, f"agents/{name}-team-lead.md", build_team_lead_agent(config), dry_run)

    # 3b. Optional agents (V2.3)
    optional_agents = []

    # Migration agent — only if shared DB configured
    shared_db = config.get("sharedDb")
    if shared_db:
        mig_content = render_template("agent-migration.tmpl", {
            **common,
            "SHARED_DB_PATH": shared_db,
        })
        write_file(output_dir, f"agents/{name}-migration.md", mig_content, dry_run)
        optional_agents.append("migration")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-migration"})
            write_file(output_dir, f"agent-memory/{name}-migration/MEMORY.md", mem_content, dry_run)

    # Query optimizer agent — always for Laravel/Filament, optional for others
    framework = config.get("techStack", {}).get("framework", "").lower()
    if framework in ("laravel", "django", "rails", "nextjs", "next.js"):
        optimizer_model = {"budget": "sonnet", "balanced": "sonnet", "quality": "opus"}[model_budget]
        opt_content = render_template("agent-query-optimizer.tmpl", {
            **common,
            "OPTIMIZER_MODEL": optimizer_model,
        })
        write_file(output_dir, f"agents/{name}-query-optimizer.md", opt_content, dry_run)
        optional_agents.append("query-optimizer")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-query-optimizer"})
            write_file(output_dir, f"agent-memory/{name}-query-optimizer/MEMORY.md", mem_content, dry_run)

    # MCP dev agent — if project has .mcp.json or builds MCP servers
    has_mcp = bool(config.get("mcpServers")) or framework in ("nodejs", "node", "express", "fastify")
    if has_mcp:
        mcp_content = render_template("agent-mcp-dev.tmpl", common)
        write_file(output_dir, f"agents/{name}-mcp-dev.md", mcp_content, dry_run)
        optional_agents.append("mcp-dev")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-mcp-dev"})
            write_file(output_dir, f"agent-memory/{name}-mcp-dev/MEMORY.md", mem_content, dry_run)

    # 4. Orchestrator SKILL.md (builder)
    write_file(output_dir, f"skills/{name}/SKILL.md", build_orchestrator_skill(config), dry_run)

    # 5. Domain map (builder)
    write_file(output_dir, f"skills/{name}/context/domain-map.md", build_domain_map(config), dry_run)

    # 6. Shared learnings + memory (respect agentMemory flag)
    if has_memory:
        content = render_template("shared-learnings.tmpl", common)
        write_file(output_dir, "agent-memory/shared-learnings.md", content, dry_run)

        # Learning queue
        write_file(output_dir, "agent-memory/learning-queue.md",
                   "# Learning Queue\n\n> Auto-captured from agent transcripts. Review periodically.\n> Move useful entries to shared-learnings.md as [NEW 0/3].\n", dry_run)

        # Per-agent memory
        all_agents = [f"{name}-{d}" for d in domains] + [
            f"{name}-discovery", f"{name}-db", f"{name}-review",
            f"{name}-team-lead", f"{name}-maintenance",
        ]
        for agent in all_agents:
            content = render_template("memory.tmpl", {"AGENT_NAME": agent})
            write_file(output_dir, f"agent-memory/{agent}/MEMORY.md", content, dry_run)

    # 7. Agent context skeletons
    for domain in domains:
        write_file(output_dir, f"skills/{name}/context/agent-context/{domain}-context.md",
                   f"# {domain.replace('-', ' ').title()} Domain Context\n\n## Table Schemas\n<!-- Populated by /buddyx-forge:scan -->\n\n## Model Snippets\n<!-- Populated by /buddyx-forge:scan -->\n", dry_run)

    # 8. Database tables skeleton
    write_file(output_dir, f"skills/{name}/context/database-tables.md",
               "# Database Tables\n\n<!-- Populated by /buddyx-forge:scan -->\n", dry_run)

    # 9. AGENTS.md (cross-tool compatibility — Cursor, Copilot, Codex)
    agents_rows = []
    for d in domains:
        agents_rows.append(f"| {name}-{d} | {d.replace('-', ' ').title()} specialist | {rw_model} | Domain |")
    agents_rows.extend([
        f"| {name}-discovery | Pre-implementation research | {ro_model} | Infrastructure |",
        f"| {name}-db | Database schema inspection | {ro_model} | Infrastructure |",
        f"| {name}-review | Code quality gate | {ro_model} | Infrastructure |",
        f"| {name}-team-lead | Multi-agent coordinator | sonnet | Infrastructure |",
        f"| {name}-maintenance | Context maintenance | sonnet | Infrastructure |",
    ])
    agents_table = "| Agent | Description | Model | Type |\n|-------|-------------|-------|------|\n" + "\n".join(agents_rows)
    agents_md = render_template("agents-md.tmpl", {
        **common,
        "AGENTS_TABLE": agents_table,
    })
    write_file(output_dir, "AGENTS.md", agents_md, dry_run)

    # 10. CLAUDE.md (complete — no AI needed, Option B)
    write_file(output_dir, "CLAUDE.md", build_claude_md(config), dry_run)

    # 11. RULES.md (complete — framework-specific, no AI needed, Option B)
    write_file(output_dir, f"skills/{name}/RULES.md", build_rules_md(config), dry_run)

    # 11. Diagram skill
    diagram_content = render_template("diagram-skill.tmpl", {
        **common,
        "EXAMPLE_DOMAIN": domains[0] if domains else "example",
    })
    write_file(output_dir, f"skills/{name}/diagram/SKILL.md", diagram_content, dry_run)

    # 12. Audit skill
    domain_list_md = "\n".join([f"| `{d}` | {d.replace('-', ' ').title()} |" for d in domains])
    audit_content = render_template("audit-skill.tmpl", {
        **common,
        "DOMAIN_LIST": f"| Module | Description |\n|--------|-------------|\n{domain_list_md}",
    })
    write_file(output_dir, f"skills/{name}/audit/SKILL.md", audit_content, dry_run)

    # 13. Audit HTML template (copy as-is)
    audit_html_src = TEMPLATES_DIR / "module-audit-template.html"
    if audit_html_src.exists():
        content = audit_html_src.read_text()
        write_file(output_dir, "templates/module-audit-template.html", content, dry_run)

    # 14. Output directories
    write_file(output_dir, "diagrams/.gitkeep", "", dry_run)
    write_file(output_dir, "audits/.gitkeep", "", dry_run)

    # 15. Dashboard HTML template (V2.1)
    dash_src = TEMPLATES_DIR / "dashboard.html.tmpl"
    if dash_src.exists():
        content = dash_src.read_text().replace("{PROJECT_TITLE}", title)
        write_file(output_dir, "dashboard/dashboard-template.html", content, dry_run)

    # 16. Hookify rules (V2.1)
    hookify_content = render_template("hookify-rules.tmpl", common)
    write_file(output_dir, "hookify-rules.md", hookify_content, dry_run)

    # ─── Hook scripts ───

    hook_scripts = []

    if hooks_cfg.get("contextInjection", False):
        content = render_template("hooks/inject-prompt-context.sh.tmpl", common)
        write_file(output_dir, "scripts/inject-prompt-context.sh", content, dry_run)
        hook_scripts.append("scripts/inject-prompt-context.sh")

    if hooks_cfg.get("blockDangerous", False):
        content = render_template("hooks/safety-guard.sh.tmpl", common)
        write_file(output_dir, "scripts/safety-guard.sh", content, dry_run)
        hook_scripts.append("scripts/safety-guard.sh")

    if commit_policy == "user":
        content = render_template("hooks/block-git-commit.sh.tmpl", common)
        write_file(output_dir, "scripts/block-git-commit.sh", content, dry_run)
        hook_scripts.append("scripts/block-git-commit.sh")

    if hooks_cfg.get("autoFormat", False):
        content = render_template("hooks/auto-format-new-files.sh.tmpl", common)
        write_file(output_dir, "scripts/auto-format-new-files.sh", content, dry_run)
        hook_scripts.append("scripts/auto-format-new-files.sh")

    content = render_template("hooks/detect-new-file-created.sh.tmpl", common)
    write_file(output_dir, "scripts/detect-new-file-created.sh", content, dry_run)
    hook_scripts.append("scripts/detect-new-file-created.sh")

    # Eval scripts
    if eval_level in ("full", "basic"):
        for tmpl in ["track-agent-start.sh.tmpl", "track-session-count.sh.tmpl"]:
            content = render_template(f"hooks/eval/{tmpl}", common)
            script_name = tmpl.replace(".tmpl", "")
            write_file(output_dir, f"scripts/eval/{script_name}", content, dry_run)
            hook_scripts.append(f"scripts/eval/{script_name}")

    if eval_level == "full":
        for tmpl in ["validate-agent-output.sh.tmpl", "extract-learnings.sh.tmpl",
                      "prompt-save-learnings.sh.tmpl", "auto-promote-learnings.sh.tmpl"]:
            content = render_template(f"hooks/eval/{tmpl}", common)
            script_name = tmpl.replace(".tmpl", "")
            write_file(output_dir, f"scripts/eval/{script_name}", content, dry_run)
            hook_scripts.append(f"scripts/eval/{script_name}")

    # Dashboard directory
    if eval_level in ("full", "basic"):
        write_file(output_dir, "dashboard/events.jsonl", "", dry_run)

    # Plans directory
    write_file(output_dir, "plans/.gitkeep", "", dry_run)

    # Make scripts executable
    for script in hook_scripts:
        make_executable(output_dir, script, dry_run)

    # Summary
    file_count = sum(1 for _ in Path(output_dir).rglob("*") if _.is_file()) if not dry_run else dry_run_count
    print(f"\n{'DRY RUN — ' if dry_run else ''}buddyx-forge generated for '{name}':")
    print(f"  Domains: {', '.join(domains)}")
    opt_str = f" + {len(optional_agents)} optional ({', '.join(optional_agents)})" if optional_agents else ""
    print(f"  Agents: {len(domains)} domain + 5 infrastructure{opt_str} = {len(domains) + 5 + len(optional_agents)}")
    print(f"  Skills: orchestrator, rules, diagram, audit")
    print(f"  Hook scripts: {len(hook_scripts)}")
    print(f"  Files created: {file_count}")
    print(f"\n  Next steps:")
    print(f"  1. AI customization will fill CLAUDE.md, RULES.md, and agent file lists")
    print(f"  2. Run /buddyx-forge:scan to populate domain-map and context packs")
    print(f"  3. Run /buddyx-forge:health to verify setup")


# ─── CLI ENTRY POINT ───

def main():
    parser = argparse.ArgumentParser(description="buddyx-forge generator")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--output", required=True, help="Output directory (e.g., .claude/)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    config = load_config(args.config)
    generate(config, args.output, args.dry_run)


if __name__ == "__main__":
    main()
