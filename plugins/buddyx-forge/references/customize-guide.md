# Customization Guide

After running `/buddyx-forge:setup`, the Python generator creates all files with sensible defaults. This guide covers optional enhancements you can make to tailor the setup to your specific codebase.

## When to Use This Guide

- After initial setup, when you want to refine agent behavior
- After `/buddyx-forge:scan` populates file lists and you want to adjust ownership
- When adding project-specific rules beyond framework defaults

## CONSTRAINTS

- Only read 3-5 files per domain to detect patterns. Do NOT read entire codebase.
- Each agent.md must stay under 150 lines total.
- Only include rules you can VERIFY from actual code. NEVER invent patterns.
- If project is empty (no code yet), use framework defaults and add placeholders.

## 1. Refine Agent File Ownership

After `/buddyx-forge:scan` populates `## Your Files` sections in each agent, review and adjust:

- Move files between domains if scan assigned them incorrectly
- Add `# manual` comment to entries you don't want scan to override:
  ```
  app/Services/PaymentGateway.php  # manual
  ```
- Mark cross-domain dependencies under `### Read Only`

## 2. Add Domain-Specific Constraints

Each domain agent has a `## Domain-Specific Constraints` section. Add rules specific to that domain:

```markdown
## Domain-Specific Constraints
- All billing amounts use integer cents (never float dollars)
- InvoiceService is the single entry point for all invoice operations
- Stripe webhook handlers must be idempotent
```

Base these on actual code patterns — read 2-3 files in the domain first.

## 3. Customize RULES.md

The generator creates framework-specific rules. Add project-specific conventions under `## Detected Conventions`:

```markdown
## Detected Conventions
- Tables use `uuid` primary keys (not auto-increment)
- All models use soft deletes (`deleted_at` column)
- Enums stored in `app/Enums/` with `string` backing type
- Timestamps: `created_at`, `updated_at` on every table
```

Run `/buddyx-forge:scan` to auto-detect these, or add manually after reading your schema.

## 4. Tune Orchestrator Keywords

The orchestrator in `skills/{name}/SKILL.md` routes tasks to agents based on keywords. If agents get wrong assignments, edit the keywords table:

```markdown
| Domain | Keywords |
|--------|----------|
| billing | invoice, payment, subscription, stripe, refund, credit |
| auth | login, token, session, password, 2fa, oauth |
```

Add domain-specific terms that appear in your codebase but aren't in the defaults.

## 5. Add Shared Learnings

If you already know project conventions, seed `agent-memory/shared-learnings.md`:

```markdown
## Patterns

[CONFIRMED] [2026-04-01] Always use `->lockForUpdate()` when modifying balance fields
[CONFIRMED] [2026-04-01] Filament forms: use `->reactive()` on fields that trigger other field visibility
[NEW 0/3] [2026-04-01] Consider using `->batch()` for bulk notification sends
```

Mark established conventions as `[CONFIRMED]` and hypotheses as `[NEW 0/3]`.

## 6. Adjust Permission Level

If the generated `settings.json` is too restrictive or too loose, edit the `permissions` section directly. The generator creates three tiers:

- `allow` — runs without asking
- `ask` — prompts for confirmation
- `deny` — blocked entirely

Add project-specific commands as needed:
```json
"allow": ["Bash(php artisan queue:work --once)"],
"ask": ["Bash(php artisan migrate *)"]
```

## What NOT to Customize

- Don't edit hook scripts directly — they're regenerated on setup. Instead, disable by renaming to `.disabled`
- Don't change agent frontmatter `name:` fields — the orchestrator and memory system depend on these
- Don't remove `skills:` references from agents — they load RULES.md at runtime
