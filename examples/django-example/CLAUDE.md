# Project Rules

## This is a Django 5 Project

- NEVER commit code — user commits manually.


## Working Rules

- **NEVER ASSUME** — if you don't know something, READ the code. Never guess table names, column types, or behavior.
- **ASK IF UNCLEAR** — if requirements are ambiguous, ask the user.
- **VERIFY** — before claiming anything is correct, verify from the code.
- If a task touches more than 3 files, stop and ask for confirmation.
- Never delete or overwrite files without explicit permission.
- Read files before modifying them — never assume content.
- Keep changes minimal — only change what's needed.

## Agent Delegation

| When To Use | Agent |
|-------------|-------|
| Api tasks | webapp-api |
| Dashboard tasks | webapp-dashboard |
| Unknown domain/feature | webapp-discovery |
| Check DB schema | webapp-db |
| After any code change | webapp-review (auto) |
| Multi-domain task | webapp-team-lead |
| Refresh context files | webapp-maintenance |


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
fix: ApiService — returns 500 on edge case. Only touch the service file.

add: export PDF to DashboardResource — include date range filter.


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


## Shared Knowledge

Before starting any task, read `.claude/agent-memory/shared-learnings.md` for patterns and conventions.

**Entries marked `[NEW n/3]`** — unconfirmed, test when relevant.
**Entries marked `[CONFIRMED]`** — apply by default, proven across 3+ tasks.

## Flows & Diagrams

**"create flow"** → simple markdown .md file with step arrows
  - Save to `.claude/docs/{feature}/flows.md`

**"diagram:"** → visual interactive HTML (Mermaid, zoom/pan)
  - Types: ER, flowchart, sequence, architecture, state

**On demand only:** Only create flows/diagrams when user explicitly asks.
