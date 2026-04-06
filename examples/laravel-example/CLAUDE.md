# Project Rules

## This is a Laravel 11 Project

- NEVER commit code — user commits manually.
- Filament 3 resources use Section → Tabs → Tab → Grid pattern.


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

| When To Use | Agent |
|-------------|-------|
| Billing tasks | myapp-billing |
| Auth tasks | myapp-auth |
| Users tasks | myapp-users |
| Unknown domain/feature | myapp-discovery |
| Check DB schema | myapp-db |
| After any code change | myapp-review (auto) |
| Multi-domain task | myapp-team-lead |
| Refresh context files | myapp-maintenance |


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
fix: BillingService — returns 500 on edge case. Only touch the service file.

add: export PDF to AuthResource — include date range filter.

audit: users module — check code quality, security, permissions.


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
