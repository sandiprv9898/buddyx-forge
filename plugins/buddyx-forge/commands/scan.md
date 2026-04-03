---
name: scan
description: Re-scan codebase, update domain-map and context packs. Use after adding new code, models, or resources. Supports --dream flag for memory cleanup.
---

# /buddyx-forge:scan

Re-scan the codebase and update domain-map, context packs, and rules.

## When to Use

- After adding new models, resources, controllers, jobs
- After a git pull with significant changes
- When `/buddyx-forge:health` reports orphan files
- When context packs feel stale
- With `--dream` flag: for monthly memory cleanup

## Process

### Step 1: Detect Project Name

Read any agent file in `.claude/agents/` and extract the name prefix from frontmatter `name:` field (everything before the first domain segment).

### Step 2: Scan Codebase

Detect the framework from CLAUDE.md or settings.json, then scan framework-appropriate directories:

**Laravel/PHP:**
```bash
find app/Models -name "*.php" -type f 2>/dev/null | sort
find app/Filament/Resources -name "*.php" -type f 2>/dev/null | sort
find app/Http/Controllers -name "*.php" -type f 2>/dev/null | sort
find app/Jobs app/Exports app/Imports -name "*.php" -type f 2>/dev/null | sort
find app/Policies app/Services app/Helpers -name "*.php" -type f 2>/dev/null | sort
find app/Enum app/Enums app/Observers -name "*.php" -type f 2>/dev/null | sort
```

**Next.js/React/Node.js (TypeScript/JavaScript):**
```bash
find src/app -name "*.tsx" -o -name "*.ts" -type f 2>/dev/null | sort
find src/components -name "*.tsx" -type f 2>/dev/null | sort
find src/hooks src/lib src/services -name "*.ts" -type f 2>/dev/null | sort
find src/api app/api -name "*.ts" -type f 2>/dev/null | sort
find prisma -name "*.prisma" -type f 2>/dev/null | sort
```

**Django (Python):**
```bash
find . -path "*/models.py" -type f 2>/dev/null | sort
find . -path "*/views.py" -type f 2>/dev/null | sort
find . -path "*/serializers.py" -type f 2>/dev/null | sort
find . -path "*/urls.py" -path "*/tasks.py" -path "*/admin.py" -type f 2>/dev/null | sort
find . -path "*/tests/*.py" -type f 2>/dev/null | sort
```

**Go:**
```bash
find internal cmd pkg -name "*.go" -type f 2>/dev/null | sort
find . -name "*_test.go" -type f 2>/dev/null | sort
```

**Rails (Ruby):**
```bash
find app/models -name "*.rb" -type f 2>/dev/null | sort
find app/controllers -name "*.rb" -type f 2>/dev/null | sort
find app/services app/jobs app/mailers -name "*.rb" -type f 2>/dev/null | sort
find app/serializers app/policies -name "*.rb" -type f 2>/dev/null | sort
```

### Step 3: Group Files by Domain

Read each agent's description from `.claude/agents/{name}-{domain}.md`. Use description keywords to match files:
- File name contains domain keyword → assign
- Resource name matches domain → assign
- If matches multiple → most specific wins
- If matches none → mark "unassigned"

### Step 4: Update domain-map.md

For each domain, update `## {domain}` section in `.claude/skills/{name}/context/domain-map.md`:
- Add newly discovered files under `### Read/Write`
- Remove files that no longer exist on disk
- Keep entries with `# manual` comment intact

### Step 5: Update Agent Context Packs

For each domain, update `.claude/skills/{name}/context/agent-context/{domain}-context.md`:
- Read each model: extract `$fillable`, `$casts`, relationships
- Read each resource: extract form fields, table columns (summary)
- Write structured context

### Step 6: Update Agent "Your Files" Sections

For each domain agent, use Edit tool to update `## Your Files` with actual file list from domain-map.

### Step 7: Detect New Conventions

Read 3-5 model files. Check if conventions changed since last scan:
- Table naming?
- New enum folder?
- New timestamp pattern?

If changes → update RULES.md Tier 2 section.

### Step 8: Report

```
buddyx-forge scan complete:

Files found: {total}
  Models: {count} | Resources: {count} | Jobs: {count} | Other: {count}

Domains updated: {list}
Unassigned files: {count}
  - path/to/file.php
  ...

{If unassigned > 0: "Assign these? Or run /buddyx-forge:add-domain {name}"}
```

## Dream Mode (--dream flag)

When user says `/buddyx-forge:scan --dream`, also run memory cleanup:

1. Read all `.claude/agent-memory/{agent}/MEMORY.md` files
2. If over 180 lines → trim: keep first 20 lines (headers) + last 150 lines (recent)
3. Read `shared-learnings.md`:
   - Remove entries older than 90 days that are still `[NEW 0/3]` (never confirmed)
   - Keep all `[CONFIRMED]` entries regardless of age
4. Read `learning-queue.md`:
   - If over 100 lines → trim to last 80 entries
5. Report:
   ```
   Dream cleanup:
     Agent memories trimmed: {count} (of {total})
     Stale hypotheses removed: {count}
     Learning queue trimmed: yes/no
   ```
