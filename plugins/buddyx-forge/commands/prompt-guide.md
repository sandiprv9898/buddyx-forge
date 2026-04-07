---
name: prompt-guide
description: Interactive prompt engineering guide for Claude Code. Shows how to write effective prompts for your multi-agent system — with examples, patterns, anti-patterns, and framework-specific tips.
---

# /buddyx-forge:prompt-guide

Interactive prompt engineering guide. Teaches you how to write better prompts for Claude Code and your multi-agent setup.

## How to Use

When the user runs this command, present the guide interactively. Start with the quick reference, then offer to deep-dive into any section.

---

## Quick Reference — The Prompt Formula

```
[action]: [file/location] — [what's wrong or what to do]. [scope limit].
```

### Actions

| Action | When to Use | Example |
|--------|------------|---------|
| `fix:` | Something is broken | `fix: PaymentService — returns null on zero amount` |
| `add:` | New functionality | `add: PDF export to InvoiceResource` |
| `refactor:` | Improve without changing behavior | `refactor: extract validation into FormRequest` |
| `check:` / `audit:` | Review and report | `audit: auth module — check for security issues` |
| `update:` | Change existing behavior | `update: email template — add company logo` |
| `optimize:` | Improve performance | `optimize: dashboard query — takes 3s, should be <500ms` |
| `explain:` | Understand code | `explain: how does the payment webhook flow work?` |
| `diagram:` | Visual representation | `diagram: ER tables for billing module` |

---

## Section 1: The 5 Rules of Good Prompts

### Rule 1: Be Specific About Location
**Bad:** `fix the login bug`
**Good:** `fix: AuthController@login — returns 500 when email has uppercase letters`

**Why:** Claude has access to your entire codebase. Without a location, it has to search everything. With a location, it goes straight to the right file.

### Rule 2: Describe Current vs Expected Behavior
**Bad:** `the payment is broken`
**Good:** `fix: PaymentService@charge — returns null when amount is 0. Should return a zero-amount receipt.`

**Why:** "Broken" means different things. Describing both behaviors lets Claude verify the fix is correct.

### Rule 3: Set Scope Limits
**Bad:** `add sorting to the users table`
**Good:** `add: sortable columns to UserResource list page. Only touch the Resource file, don't modify the model.`

**Why:** Without limits, Claude might refactor 10 files when you only wanted one change. Scope limits prevent over-engineering.

### Rule 4: Reference Working Examples
**Bad:** `add export to the billing page`
**Good:** `add: CSV export to BillingResource — match the export pattern in StudentResource`

**Why:** Your codebase already has patterns. Pointing to an existing example means consistent code with zero explanation needed.

### Rule 5: One Task Per Prompt
**Bad:** `fix the login bug, add export, and refactor the payment service`
**Good:** Send three separate prompts. Each gets its own agent, proper review, and focused commit.

**Why:** Multi-task prompts confuse agent routing. The orchestrator works best with clear, single-domain requests.

---

## Section 2: Modifiers That Save Time

Add these to any prompt to control Claude's behavior:

| Modifier | Effect | Example |
|----------|--------|---------|
| `only touch [file]` | Limits changes to one file | `fix: UserService — only touch app/Services/UserService.php` |
| `don't modify [file]` | Excludes specific files | `refactor: billing module — don't modify the migration files` |
| `show me before changing` | Preview before edit | `add: caching to DashboardController — show me before changing` |
| `read only` | Just analyze, no edits | `check: auth module — read only, report issues` |
| `match [file] pattern` | Follow existing code style | `add: StudentExport — match InvoiceExport pattern` |
| `max N files` | Limit blast radius | `refactor: extract service — max 3 files` |
| `with tests` | Include test coverage | `add: discount calculation — with tests` |
| `explain first` | Get explanation before code | `fix: race condition in queue — explain first` |

---

## Section 3: Multi-Agent Prompt Patterns

### Pattern: Domain-Specific Task
```
fix: PaymentService — charge() returns null on zero amount
```
Orchestrator detects "Payment" → dispatches billing domain agent → auto-review after fix.

### Pattern: Cross-Domain Task
```
add: when student enrolls, create billing invoice automatically
```
Orchestrator detects students + billing → dispatches team-lead → sequential agents → review.

**Tip:** For cross-domain tasks, name both domains explicitly:
```
add: student enrollment → billing invoice creation. Touches students and billing domains.
```

### Pattern: Full Audit
```
audit: all modules
```
Team-lead dispatches all domain agents in parallel → collects results → review.

### Pattern: Discovery First
```
explain: how does the payment webhook flow work? read only
```
Dispatches discovery agent (read-only) → maps the flow → reports back without changes.

### Pattern: Database Change
```
add: soft deletes to invoices table. Need migration + model update.
```
Orchestrator detects DB change → db-agent first → domain agent → review.

### Pattern: Targeted Review
```
check: billing module — audit security, check for SQL injection and mass assignment
```
Dispatches review agent with specific focus areas.

---

## Section 4: Framework-Specific Prompt Tips

### Laravel
```
# Good: mentions specific Laravel patterns
fix: InvoiceObserver — created event fires twice. Check if ObservedBy attribute is registered correctly.

# Good: references Filament patterns
add: bulk export action to StudentResource — use Filament's BulkAction pattern with queue.

# Good: includes eager loading concern
optimize: ListInvoices — N+1 on customer relationship. Add to getEloquentQuery.
```

### Next.js / React
```
# Good: specifies component type
add: DashboardChart as Server Component — fetch data server-side, no useEffect.

# Good: mentions rendering strategy
optimize: ProductList — switch to dynamic import with loading skeleton.

# Good: includes TypeScript expectation
add: useCart hook — return typed CartItem[], handle empty state.
```

### Django
```
# Good: mentions Django patterns
add: BillingSerializer — separate list and detail serializers with different field sets.

# Good: includes query optimization
optimize: InvoiceViewSet.list — add select_related for customer, prefetch_related for items.
```

### Go
```
# Good: mentions error handling
fix: PaymentHandler — wrapping error without context. Use fmt.Errorf with %w.

# Good: includes concurrency concern
add: batch processor — use goroutine pool with context cancellation.
```

### Rails
```
# Good: mentions Rails patterns
add: InvoiceService — extract billing logic from controller into service object.

# Good: includes query concern
optimize: StudentsController#index — use includes(:courses, :grades) to prevent N+1.
```

---

## Section 5: Anti-Patterns to Avoid

| Anti-Pattern | Problem | Better Version |
|-------------|---------|---------------|
| `make it better` | No direction | `optimize: DashboardQuery — reduce from 3s to <500ms` |
| `fix everything` | Too broad | `audit: billing module — report top 5 issues` |
| `just do it` | No context | `add: PDF export to InvoiceResource — match StudentExport pattern` |
| `something is wrong with login` | No error details | `fix: LoginController — returns 422 on valid credentials since commit abc123` |
| `refactor the whole app` | Unbounded scope | `refactor: extract PaymentService from PaymentController — only these 2 files` |
| `add feature X and also Y and Z` | Multi-task | Send 3 separate prompts |
| `I think there's a bug somewhere` | No location | `check: auth module — users report intermittent 401s` |

---

## Section 6: Advanced Techniques

### Chaining Prompts
For complex work, chain prompts in sequence:

```
1. explain: how does the payment flow work? read only
2. diagram: payment flow from checkout to confirmation
3. add: retry logic to PaymentService@charge — max 3 retries with exponential backoff
4. audit: payment module — focus on error handling and edge cases
```

### Using Memory
After agents learn patterns, reference them:
```
fix: InvoiceService — same N+1 pattern we fixed in StudentService last week
```
The agent checks shared-learnings.md and applies the confirmed pattern.

### Scoped Audits
```
audit: billing module — only check:
1. N+1 queries
2. Missing authorization
3. Unvalidated input
```
Numbered lists give the review agent a focused checklist.

### Comparative Prompts
```
check: why does StudentExport work but InvoiceExport fails on large datasets?
```
Discovery agent compares both implementations and reports differences.

---

## Section 7: Claude Code Official Best Practices

These tips come from Anthropic's official Claude Code documentation and community patterns.

### Use @ to Reference Files
Don't describe where code lives — reference it directly:
```
# Bad: describing the file
fix: the payment service in the services folder

# Good: direct reference
fix: @app/Services/PaymentService.php — charge() returns null on zero amount
```
Claude reads the file before responding. This gives it exact context instead of guessing.

### Let Claude Interview You for Big Features
For complex features, don't write a massive prompt. Start minimal and let Claude ask questions:
```
add: real-time notifications system
```
Then tell Claude: "Interview me about requirements first."
Claude will ask about: technical approach, UI/UX, edge cases, tradeoffs — things you might not have considered.

### Interrupt and Course-Correct
Claude Code is conversational. If it's going down the wrong path:
- Just type your correction and press **Escape** then **Enter**
- Claude stops and adjusts based on your input
- You don't need to start over

### Use CLI Tools Over APIs
```
# Good: uses gh CLI (context-efficient)
check: what's the status of PR #42

# Instead of asking Claude to use the GitHub API
```
CLI tools like `gh`, `aws`, `gcloud` are the most context-efficient way to interact with external services.

### Write CLAUDE.md Like a Contract
Your CLAUDE.md should be explicit, bounded, and easy to check:
- **Role**: What the agent does
- **Goal**: What success looks like
- **Constraints**: What it must NOT do
- **Uncertainty rule**: What to do when unsure (ask, not guess)

buddyx-forge generates this structure automatically — but you can customize it.

### Start Vague When Exploring
Not every prompt needs to be precise. When exploring:
```
what would you improve in this file?
explain: how does this module work?
```
Vague prompts surface things you wouldn't have thought to ask about. Use precise prompts for execution, vague prompts for discovery.

### Avoid Over-Engineering
Claude Opus models tend to create extra files and unnecessary abstractions. Add constraints:
```
# Without constraint: Claude might create 5 new helper files
add: discount calculation

# With constraint: focused change
add: discount calculation to InvoiceService — keep it in the existing file, no new abstractions
```

### Parallel Sessions for Independent Work
For truly independent tasks, use separate Claude Code sessions:
```
# Session 1: fix: billing module — payment edge case
# Session 2: add: export feature to reports module
# Session 3: audit: auth module — security review
```
Each session gets its own context window. buddyx-forge's agent system does this automatically via the team-lead.

> **Sources:** [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) | [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | [Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

---

## Interactive Mode

After presenting the guide, ask the user:

> **Which section would you like to practice?**
> 1. Rewrite a bad prompt into a good one (I'll give you examples to fix)
> 2. Write prompts for your specific project domains
> 3. See more framework-specific examples
> 4. Learn about agent routing — how prompts map to agents

If the user picks an option, run that section interactively with their actual project context (read their domains from `.claude/skills/*/SKILL.md`).
