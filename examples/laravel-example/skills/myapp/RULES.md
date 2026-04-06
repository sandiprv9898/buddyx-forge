# MANDATORY RULES — All Myapp agents must follow

## BEFORE WRITING ANY CODE

1. READ the file you are about to modify (never assume content)
2. READ one sibling file in the same directory to confirm patterns
3. SEARCH the codebase for existing helpers, services, traits — NEVER duplicate
4. If task involves data, verify table structure BEFORE writing model code

## Laravel 11

- `match` over `switch` always
- Helpers: `auth()`, `redirect()`, `str()` — NOT Facades
- Observers via `#[ObservedBy([Observer::class])]` attribute
- Scopes via `#[ScopedBy(ScopeClass::class)]` attribute
- No `Model::query()->create()` — use `Model::create()`
- Relationship keys always explicit: `->belongsTo(Model::class, 'FK', 'PK')`
- `$fillable` defined on every model (never `$guarded = []`)
- No empty catch blocks — at minimum log the error

## Filament 3

- Forms: Section → Tabs → Tab → Grid pattern (if multi-field)
- Translation keys: `__('module.form.field_name')` dot notation
- URLs: `ResourceName::getUrl()` — never `route()`
- Actions: `->authorize('ability')` on every action
- Unique validation must exclude soft-deleted records
- Notifications: `Notification::make()->success()->title('...')->send()`

## Performance

- Eager loading: prevent N+1 queries
- `exists()` not `count() > 0`
- Debounce on live search inputs

## Security

- Never use `$guarded = []` — always define `$fillable`
- No string concatenation in raw SQL — use parameterized queries
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
- Commit code (user commits manually)

## Detected Conventions

<!-- Run /buddyx-forge:scan to detect conventions from your codebase -->
<!-- Table naming, timestamps, soft deletes, enum folder, primary key pattern -->
