---
name: dashboard
description: Open the agent metrics dashboard in browser. Shows session counts, pass/fail rates, duration, files changed per agent. Reads from .claude/dashboard/events.jsonl.
---

# /buddyx-forge:dashboard

Open the interactive agent metrics dashboard.

## Process

### Step 1: Check Data Exists

```bash
test -f .claude/dashboard/events.jsonl
```

If not found: "No agent sessions recorded yet. Run some agents first, then try again."

### Step 2: Read Events

```bash
cat .claude/dashboard/events.jsonl
```

Parse each line as JSON. Collect all events.

### Step 3: Generate Dashboard

1. Find the dashboard template from the plugin
2. Read `.claude/dashboard/events.jsonl` — convert to JSON array
3. Replace `const EVENTS_DATA = [];` with the actual events array
4. Replace `{PROJECT_TITLE}` with project name
5. Write to `.claude/dashboard/dashboard.html`

### Step 4: Open

```bash
xdg-open .claude/dashboard/dashboard.html
```

Tell user: "Dashboard opened. Refresh the page to see latest data after running agents."
