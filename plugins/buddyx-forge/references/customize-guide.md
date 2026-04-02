# AI Customization Guide

Read this during Step 5 of /buddyx-forge setup. You (Claude) fill in files that need intelligence.

## CONSTRAINTS

- Only read 3-5 files per domain to detect patterns. Do NOT read entire codebase.
- Each agent.md must stay under 150 lines total.
- Only include rules you can VERIFY from actual code. NEVER invent patterns.
- If project is empty (no code yet), use Laravel defaults and add placeholders.

## File 1: CLAUDE.md

The Python generator created `.claude/CLAUDE.md` from template with placeholders. Use Edit tool to fill:

### {AGENT_DELEGATION_TABLE}
Build a table from the project's agents:

```markdown
| When To Use | Agent |
|-------------|-------|
| Unknown domain/feature | {name}-discovery |
| Check DB schema | {name}-db |
| After any code change | {name}-review (auto) |
| Multi-domain task | {name}-team-lead |
| Refresh context files | {name}-maintenance |
| {domain1} tasks | {name}-{domain1} |
| {domain2} tasks | {name}-{domain2} |
```

### {PROMPT_TEMPLATES_SECTION}
If user chose Q8=Yes, generate:

```markdown
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
{Generate 3-5 examples using actual domain names and likely file patterns from the codebase}

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
```

### {FLOWS_AND_DIAGRAMS_SECTION}
```markdown
## Flows & Diagrams

**"create flow"** → simple markdown .md file with step arrows
  - Save to `.claude/docs/{feature}/flows.md`

**"diagram:"** → visual interactive HTML (Mermaid, zoom/pan)
  - Types: ER, flowchart, sequence, architecture, state

**On demand only:** Only create flows/diagrams when user explicitly asks.
```

## File 2: RULES.md

Create `.claude/skills/{name}/RULES.md` with 3 tiers.

### Tier 1: Universal (always include)
Read `references/framework-laravel.md` for the complete list of Laravel rules.

### Tier 2: Detected Conventions
Read 3-5 existing model files. Use these commands to detect each convention:

**Table naming:**
```bash
grep -r 'protected \$table' app/Models/*.php | head -3
```
If results show `'HR_Employees'` → PascalCase. If `'users'` → snake_case. If missing → standard Laravel (snake_case).

**Primary key:**
```bash
grep -r 'protected \$primaryKey' app/Models/*.php | head -3
```
If `'EmployeeId'` → descriptive PascalCase. If missing → standard `id`.

**Timestamps:**
```bash
grep -r "CREATED_AT\|UPDATED_AT\|DELETED_AT" app/Models/*.php | head -5
```
If `UPDATED_AT = 'ModifiedDateTime'` → custom. If missing → standard `created_at`/`updated_at`.

**Soft deletes:**
```bash
grep -r "DELETED_AT\|SoftDeletes" app/Models/*.php | head -3
```
If `DELETED_AT = 'DeletionTime'` → custom. If just `SoftDeletes` → standard `deleted_at`.

**Enum folder:**
```bash
ls -d app/Enum/ app/Enums/ 2>/dev/null
```

**Import ordering:**
Read top 20 lines of 3 model files. Detect grouping pattern.

Write detected patterns:
```markdown
## Detected Conventions (from codebase scan)
- Table names: {pattern} (from {file})
- Primary keys: {pattern}
- Timestamps: {pattern}
- Soft deletes: {column name}
- Enum folder: {path}
```

If no code exists → skip Tier 2: `<!-- Run /buddyx-forge:scan after adding code to detect conventions -->`

### Tier 3: User-Provided
From setup answers:
- If Q5 = "User commits" → "NEVER commit code. User commits manually."
- If Q4 = shared DB → "NEVER create migrations in this project."
- If Filament detected → add Filament form/table rules

## File 3: Agent "Your Files" Sections

For each domain agent `.claude/agents/{name}-{domain}.md`:

1. Scan `app/Models/` for files matching domain keywords
2. Scan `app/Filament/Resources/` for matching resources
3. Scan `app/Jobs/`, `app/Exports/`, `app/Imports/`, `app/Policies/`, `app/Services/`
4. Use Edit tool to replace placeholder in `## Your Files` section

If no files found → leave placeholder: `<!-- No files detected yet. Run /buddyx-forge:scan after adding code. -->`

## File 4: domain-map.md

Replace skeleton sections with actual file lists:

```markdown
## {domain}

### Read/Write
- app/Models/User.php
- app/Filament/Resources/UserResource.php
- app/Policies/UserPolicy.php

### Read Only
- app/Helpers/AuthHelper.php (used but owned by another domain)
```

If no code → keep skeleton placeholders.

## File 5: database-tables.md

**If MCP `database-schema` is available:**
1. For each model, extract table name from `protected $table` or derive from class name
2. Query: `mcp__laravel-boost__database-schema(filter: "{table_name}", include_column_details: true)`
3. Write structured output per table:
```markdown
## {TableName}
| Column | Type | Nullable | Default | FK |
|--------|------|----------|---------|-----|
```

**If MCP not available (fallback):**
1. Read each model's `$fillable` array for column names
2. Read `$casts` for type information
3. Read relationship methods for FK inference
4. Write best-effort schema (mark as "from model, not verified against DB")

**If no code exists:**
Keep skeleton: `<!-- Populated by /buddyx-forge:scan -->`
