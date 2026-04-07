"""CLAUDE.md and RULES.md builders for buddyx-forge generator."""

from .frameworks import normalize_framework


def build_claude_md(config: dict) -> str:
    """Build complete CLAUDE.md — no AI needed."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    framework_raw = normalize_framework(
        config.get("techStack", {}).get("framework", "laravel")
    )
    framework = framework_raw.replace("nextjs", "Next.js").replace("nodejs", "Node.js").title() if framework_raw not in ("nextjs", "nodejs") else {"nextjs": "Next.js", "nodejs": "Node.js"}[framework_raw]
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

    # Framework-specific code style rules
    code_style_rules = ""
    if framework_raw == "laravel":
        code_style_rules = """
## Code Style Rules

### No Inline FQCN
- Always add a proper `use` import at the top of the file and reference the short class name.
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
{code_style_rules}
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
    framework = normalize_framework(
        config.get("techStack", {}).get("framework", "laravel")
    )
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

    elif framework == "nextjs":
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

    elif framework in ("nodejs", "express", "fastify", "nestjs", "hono"):
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

"""
    if framework == "laravel":
        rules += "- Never use `$guarded = []` — always define `$fillable`\n"

    rules += """- No string concatenation in raw SQL — use parameterized queries
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
