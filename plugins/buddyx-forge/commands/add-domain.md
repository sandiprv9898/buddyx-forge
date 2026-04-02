---
name: add-domain
description: Add a new domain agent to an existing buddyx-forge setup. Creates agent file, memory directory, context pack, and updates domain-map and orchestrator.
---

# /buddyx-forge:add-domain

Add a new domain agent to the existing setup.

## Usage

User says: `/buddyx-forge:add-domain billing` or `/buddyx-forge:add-domain user-management`

## Process

### Step 1: Parse and Validate

Extract domain name from the user's command. Validate:
- Lowercase, alphanumeric + hyphens, 2-30 chars
- Regex: `^[a-z][a-z0-9\-]{1,30}$`

If invalid → show error with examples.

### Step 2: Detect Project Name

Read any existing agent file in `.claude/agents/` and extract the project prefix from the `name:` frontmatter field. For example, if `name: nexus-auth`, then project = `nexus`.

### Step 3: Check Domain Doesn't Exist

```bash
test -f ".claude/agents/{project}-{domain}.md"
```
If exists → "Domain '{domain}' already exists. Nothing to do."

### Step 4: Detect Model Budget

Read an existing domain agent's `model:` frontmatter field. Use the same model for the new agent.

### Step 5: Ask for Domain Keywords

"What keywords should trigger this agent? (comma-separated, e.g., 'invoice, payment, subscription, billing')"

### Step 6: Create Agent File

Read an existing domain agent (e.g., `.claude/agents/{project}-{first_domain}.md`) as a reference. Create the new agent with the same structure but updated:
- name: `{project}-{domain}`
- description: using provided keywords
- skills: `{project}/context/agent-context/{domain}-context`
- Empty "Your Files" section with placeholder comment

### Step 7: Create Memory Directory

```bash
mkdir -p .claude/agent-memory/{project}-{domain}
```

Write `.claude/agent-memory/{project}-{domain}/MEMORY.md`:
```markdown
# {project}-{domain} Memory

> Learnings from past sessions. Read before starting, write after completing.

## Session Log

## File Patterns

## Bug Patterns

## Performance Notes

## Code Conventions

## Cross-Agent Notes
```

### Step 8: Create Context Pack

Write `.claude/skills/{project}/context/agent-context/{domain}-context.md`:
```markdown
# {Domain Title} Domain Context

## Table Schemas
<!-- Populated by /buddyx-forge:scan -->

## Model Snippets
<!-- Populated by /buddyx-forge:scan -->
```

### Step 9: Update Domain Map

Use Edit tool to append to `.claude/skills/{project}/context/domain-map.md`:

```markdown

---

## {domain}

### Read/Write
<!-- Run /buddyx-forge:scan to populate -->

### Read Only
<!-- Dependencies from other domains -->
```

### Step 10: Update Orchestrator Keywords

Use Edit tool to add a row to the keywords table in `.claude/skills/{project}/SKILL.md`:
```
| {domain} | {keywords} |
```

And add to the agent inventory table:
```
| {project}-{domain} | sonnet | project | {domain} specialist |
```

### Step 11: Report

```
Domain '{domain}' added successfully!

Created:
  - .claude/agents/{project}-{domain}.md
  - .claude/agent-memory/{project}-{domain}/MEMORY.md
  - .claude/skills/{project}/context/agent-context/{domain}-context.md

Updated:
  - .claude/skills/{project}/context/domain-map.md
  - .claude/skills/{project}/SKILL.md (keywords + inventory)

Next: Run /buddyx-forge:scan to populate the file list for this domain.
```
