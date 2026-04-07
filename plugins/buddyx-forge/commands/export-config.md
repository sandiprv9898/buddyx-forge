---
name: export-config
description: Export the current buddyx-forge configuration as a shareable .buddyx-forge.json file. Teammates can use this with /buddyx-forge:quick --config to get the same setup.
---

# /buddyx-forge:export-config

Export the current buddyx-forge setup as a shareable `.buddyx-forge.json` config file.

## Why

Teams need consistent setups. One developer configures buddyx-forge, exports the config, commits it to the repo. Everyone else runs `/buddyx-forge:quick --config .buddyx-forge.json` and gets the same agents, hooks, and rules.

## Process

### Step 1: Verify Setup Exists

Check for `.claude/settings.json`. If it doesn't exist:
> "No buddyx-forge setup found. Run `/buddyx-forge:setup` first."

### Step 2: Reconstruct Config from Generated Files

Read the existing setup and reconstruct the config:

**From `.claude/settings.json`:**
- `buddyxForgeVersion` — version that generated the setup
- `permissions.allow` / `permissions.ask` — detect `permissionLevel`
  - Has `Bash(xdg-open *)` in allow → `permissive`
  - Has framework commands in allow → `balanced`
  - Framework commands in ask only → `conservative`
- `hooks.PreToolUse` — detect `commitPolicy` and `hooks`
  - Has `block-git-commit.sh` → `commitPolicy: "user"`
  - No `block-git-commit.sh` → `commitPolicy: "claude"`
  - Has `safety-guard.sh` → `hooks.blockDangerous: true`
  - Has `block-migration.sh` → `hooks.blockMigration: true`
- `hooks.PostToolUse` — detect auto-format
  - Has `auto-format-new-files.sh` → `hooks.autoFormat: true`
- `hooks.UserPromptSubmit` — detect context injection
  - Has `inject-prompt-context.sh` → `hooks.contextInjection: true`
- `hooks.SubagentStart` — detect eval level
  - Has SubagentStart + SubagentStop with 6 hooks → `evalLevel: "full"`
  - Has SubagentStart + SubagentStop with 2 hooks → `evalLevel: "basic"`
  - No SubagentStart → `evalLevel: "none"`
- `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` — detect `agentTeams`
- `worktree.symlinkDirectories` — detect `worktreeSymlinks`

**From `.claude/agents/`:**
- List agent files → extract `projectName` from the agent name prefix (before first domain)
- Extract domains from domain agent files (exclude infrastructure agents: discovery, db, review, team-lead, maintenance, query-optimizer, mcp-dev, migration)

**From `.claude/agents/{name}-{domain}.md` frontmatter:**
- `model:` field → detect `modelBudget`
  - All domain agents use `haiku` → `budget`
  - Domain agents use `sonnet` → `balanced`
  - Both domain and read-only use `sonnet` → `quality`

**From `.claude/skills/{name}/RULES.md`:**
- Detect framework from section headers (## Laravel 11, ## Django, ## Go, etc.)
- Detect `hasFilament` from "## Filament 3" section

**From `.claude/CLAUDE.md`:**
- Detect `promptTemplates` from "## How to Write Prompts" section
- Detect `sharedDb` from "migrations go to" text

**From `.claude/agent-memory/`:**
- Directory exists with content → `agentMemory: true`
- Directory missing → `agentMemory: false`

**From `.claude/scripts/`:**
- Detect formatter from `auto-format-new-files.sh` content (look for the format command)
- Detect test runner from domain agent files (look for test command references)

### Step 3: Build Config JSON

Assemble the reconstructed config:

```json
{
  "projectName": "detected-name",
  "domains": ["detected", "domains"],
  "techStack": {
    "language": "detected",
    "framework": "detected",
    "frameworkVersion": "",
    "hasFilament": false,
    "db": "postgresql",
    "formatter": "detected",
    "testRunner": "detected"
  },
  "hooks": {
    "blockCommits": true,
    "blockDangerous": true,
    "autoFormat": true,
    "contextInjection": false,
    "blockMigration": false
  },
  "sharedDb": null,
  "commitPolicy": "user",
  "permissionLevel": "balanced",
  "agentMemory": true,
  "promptTemplates": true,
  "evalLevel": "full",
  "modelBudget": "balanced",
  "mcpServers": [],
  "worktreeSymlinks": [],
  "agentTeams": false
}
```

### Step 4: Present to User

Show the reconstructed config:

```
Detected configuration:

  Project:     {projectName}
  Framework:   {framework}
  Domains:     {domains joined by ", "}
  Permissions: {permissionLevel}
  Commits:     {commitPolicy}
  Model tier:  {modelBudget}
  Eval:        {evalLevel}
  Memory:      {agentMemory}
  Hooks:       {active hooks list}
```

Ask: "Does this look correct? I'll write it to `.buddyx-forge.json`."

### Step 5: Write File

Write the config to `.buddyx-forge.json` in the project root.

Tell the user:
```
Config exported to .buddyx-forge.json

Teammates can set up the same system with:
  /buddyx-forge:quick --config .buddyx-forge.json

Add it to git:
  git add .buddyx-forge.json
```

## Error Handling

- If settings.json is missing: suggest running `/buddyx-forge:setup` first
- If agents directory is empty: warn that setup may be incomplete
- If reconstruction fails for any field: use the default value and note which fields were guessed
