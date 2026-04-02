# Laravel 11 + Filament 3 Rules Reference

Use this when generating RULES.md for a Laravel project.

## Tier 1: Universal Laravel Rules (always include)

### BEFORE WRITING ANY CODE

1. READ the file you are about to modify (never assume content)
2. READ one sibling file in the same directory to confirm patterns
3. SEARCH the codebase for existing helpers, services, traits — NEVER duplicate
4. If task involves data, verify table structure BEFORE writing model code

### PHP & Laravel 11

- `match` over `switch` always
- Helpers: `auth()`, `redirect()`, `str()` — NOT Facades
- Observers via `#[ObservedBy([Observer::class])]` attribute
- Scopes via `#[ScopedBy(ScopeClass::class)]` attribute
- No `Model::query()->create()` — use `Model::create()`
- Relationship keys always explicit: `->belongsTo(Model::class, 'FK', 'PK')`
- `$fillable` defined on every model (never `$guarded = []`)
- No empty catch blocks — at minimum log the error
- Inject services: constructor if multi-use, method if single-use

### Performance

- Eager load ALL relationships used in views/tables
- `->exists()` not `->count() > 0`
- `->select()` on large queries
- Debounce on live search inputs

### Security

- `$fillable` defined (never `$guarded = []`)
- No string concatenation in `whereRaw()` — use `?` bindings
- No `addslashes()` for SQL — use parameter bindings
- Parameterized queries always — never concatenate user input into SQL

### Import Organization

Group imports: App\ → Illuminate\ → third-party
Always `use` at top of file. NEVER inline FQCN like `\Illuminate\Support\Facades\DB::`

### AFTER CODE CHANGES

1. Run tests if they exist
2. Verify eager loading covers all new relationship usage
3. Show evidence: what changed, why, how to verify
4. Report status: DONE | DONE_WITH_CONCERNS | PARTIAL_DONE | NEEDS_CONTEXT | BLOCKED

## Filament 3 Rules (include only if Filament detected)

### Forms
- Section → Tabs → Tab → Grid pattern (if multi-field)
- Translation keys: `__('module.form.field_name')` dot notation

### Tables
- `ResourceName::getUrl('index')` — never `route()`
- `->authorize('ability')` on every action
- Unique validation must exclude soft-deleted records
- Notifications: `Notification::make()->success()->title('...')->send()`

### Navigation
- `getNavigationGroup()`, `getNavigationLabel()` methods
- Translation-aware labels

## NEVER DO (include always)

- Use `snake_case` for columns/tables if project uses PascalCase (or vice versa) — match existing
- Add features the user didn't ask for
- Say "done" without showing evidence
- Use `switch` — use `match`
- Modify files outside your domain ownership
- Commit code (if user commits manually)
