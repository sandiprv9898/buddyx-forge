---
name: buddyx-forge
description: Generate a complete multi-agent development system for any Laravel project. Creates agents, hooks, skills, memory, and rules in .claude/ directory. Use when user says /buddyx-forge, "setup agents", "init agent system", or "create multi-agent setup".
---

# buddyx-forge

Generate a multi-agent development system for Laravel projects.

## Step 0: Prerequisites

1. Run `python3 --version` — if fails: "Python 3 is required. Install: `apt install python3` or `brew install python3`"
2. Run `jq --version` — if fails: warn "jq is recommended for hook scripts. Install: `apt install jq`" (continue anyway)
3. Check if `.claude/settings.json` exists:
   - If YES → ask user: "(A) Add a new domain agent, (B) Regenerate all (preserves agent-memory/), (C) Cancel"
   - If A → invoke `/buddyx-forge:add-domain` command instead
   - If C → stop
   - If B → proceed with `--force` flag
   - If NO → proceed with fresh setup

If user passes `--dry-run`, add the flag to the generator call in Step 4. Show what WOULD be created without creating anything.

## Step 1: Detect Tech Stack

Read `references/detect-stack.md` for detailed detection logic.

Quick summary:
1. Read `composer.json` → detect Laravel version, Filament presence
2. Read `.mcp.json` → detect MCP servers
3. Read `.env` → detect DB type (`DB_CONNECTION`)
4. Scan `app/` → detect directory structure, potential domains
5. Check for existing formatter (`vendor/bin/pint`)
6. Build a tech profile and present to user for confirmation

## Step 2: Ask 10 Questions (ONE at a time)

**Q1: Project name?**
- "What name for your agent system? Used as prefix (e.g., 'nexus' → nexus-auth, nexus-billing)."
- Validation: lowercase, alphanumeric + hyphens, 3-20 chars
- Default suggestion: derive from directory name

**Q2: Domains/modules?**
- Show auto-detected from Step 1: "I found these potential domains: [auth, billing, users]. Add/remove/rename?"
- For empty projects: "List your planned domains (comma-separated)"

**Q3: Safety hooks?**
- "Which safety hooks? (select all that apply)"
  - A) Block git commit/push (you commit manually) — **recommended**
  - B) Block dangerous commands (rm -rf, DROP TABLE) — **recommended**
  - C) Auto-format new PHP files (uses pint/formatter)
  - D) Inject context into every prompt (branch, status)
  - E) All of the above
- Default: E

**Q4: Shared database?**
- "Does this project share a database with another project (like an admin panel)?"
  - A) No
  - B) Yes — what's the path to the other project?
- If B → also blocks migrations in this project

**Q5: Who commits code?**
- "Who creates git commits?"
  - A) I commit manually (Claude is blocked from committing) — **recommended**
  - B) Claude can commit

**Q6: Permission level?**
- "How much should Claude be allowed to do without asking?"
  - A) Conservative — ask permission for most things
  - B) Balanced — allow read/lint/test, ask for write/git — **recommended**
  - C) Permissive — allow most things, ask only for dangerous ops

**Q7: Agent memory?**
- "Enable shared learning system? Agents remember patterns across sessions."
  - A) Yes — **recommended**
  - B) No

**Q8: Prompt templates?**
- "Add prompt template guide to CLAUDE.md? Shows format like: `fix: File — problem. Only touch [scope].`"
  - A) Yes — **recommended**
  - B) No

**Q9: Agent observability?**
- "Track agent metrics (session count, violations, learnings)?"
  - A) Full — all metrics + auto-promote learnings — **recommended for large projects**
  - B) Basic — just session tracking
  - C) None

**Q10: Model budget?**
- "Which AI models for agents?"
  - A) Budget — haiku for most, sonnet for optimizer (cheapest)
  - B) Balanced — haiku for read-only, sonnet for write agents — **recommended**
  - C) Quality — sonnet for most, opus for optimizer (best but expensive)

## Step 3: Build Config JSON

After all 10 questions, build the config JSON. Include:
- All answers from Q1-Q10
- Tech stack detected in Step 1
- Domain keywords (generate from domain names if user didn't provide custom ones)
- MCP servers detected
- Worktree symlink directories (auto-detected: Laravel → `["vendor", "node_modules"]`)

Write to `/tmp/buddyx-forge-config.json`.

Config schema (all fields required):
```json
{
  "projectName": "string",
  "projectDir": "string — absolute path",
  "techStack": {
    "language": "php",
    "framework": "laravel",
    "frameworkVersion": "string",
    "hasFilament": "boolean",
    "db": "string — pgsql/mysql/sqlite",
    "formatter": "string — command or empty",
    "testRunner": "string — command or empty"
  },
  "domains": ["string"],
  "domainKeywords": { "domain": "comma-separated keywords" },
  "hooks": {
    "blockCommits": "boolean",
    "blockDangerous": "boolean",
    "autoFormat": "boolean",
    "contextInjection": "boolean",
    "agentTracking": "boolean",
    "blockMigration": "boolean"
  },
  "sharedDb": "string path or null",
  "commitPolicy": "user or claude",
  "permissionLevel": "conservative/balanced/permissive",
  "agentMemory": "boolean",
  "promptTemplates": "boolean",
  "evalLevel": "full/basic/none",
  "modelBudget": "budget/balanced/quality",
  "mcpServers": ["string"],
  "worktreeSymlinks": ["string"],
  "agentTeams": true
}
```

## Step 4: Run Python Generator

Find the generator script:
```bash
GENERATOR=$(find ~/.claude/plugins -path '*/buddyx-forge/*/scripts/generate.py' -print -quit 2>/dev/null)
```

If `--dry-run`:
```bash
python3 "$GENERATOR" --config /tmp/buddyx-forge-config.json --output .claude/ --dry-run
```
Show output to user. Ask "Looks good? Run for real?" If yes, run without --dry-run.

If normal run:
```bash
python3 "$GENERATOR" --config /tmp/buddyx-forge-config.json --output .claude/
```

## Step 5: AI Customization

Read `references/customize-guide.md` for detailed instructions.

Quick summary — use Write tool to fill these files:
1. **CLAUDE.md** — fill framework rules, prompt templates, agent delegation table, flows section
2. **RULES.md** — read `references/framework-laravel.md`, detect conventions from existing code, write 3-tier rules
3. **Agent "Your Files" sections** — scan codebase, list real files per domain in each agent.md
4. **domain-map.md** — replace skeleton sections with actual file ownership
5. **database-tables.md** — query MCP schema or parse models

Constraint: Only read 3-5 files per domain. Stay under 150 lines per agent.md. Only include rules verified from actual code.

## Step 6: Post-Generation

1. Make all scripts executable: `chmod +x .claude/scripts/*.sh .claude/scripts/eval/*.sh 2>/dev/null`
2. Add to .gitignore (if not already there): `.claude/agent-memory/`, `.claude/dashboard/`
3. Present summary:

```
buddyx-forge setup complete!

Created for project: {name}
  Agents: {N} domain + 5 infrastructure = {total}
  Hook scripts: {count}
  Skills: orchestrator, rules, diagram, audit
  Memory: shared-learnings + {N} agent memories

Next steps:
  1. Run /buddyx-forge:scan to populate domain-map with real files
  2. Run /buddyx-forge:health to verify setup (target: 100/100)
  3. Start using your agents!

Tip: Type "audit {domain} module" to test your review agent.
```
