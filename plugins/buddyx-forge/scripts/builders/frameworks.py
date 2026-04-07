"""Framework-specific data maps and checklists for buddyx-forge generator."""


# ─── Permission commands per framework (used by settings builder) ───

_JS_COMMANDS = {
    "allow": ["Bash(npx *)", "Bash(node *)", "Bash(tsx *)"],
    "ask": ["Bash(npm install *)", "Bash(npm uninstall *)", "Bash(yarn add *)"],
}

FW_COMMANDS = {
    "laravel": {
        "allow": ["Bash(php -l *)", "Bash(php artisan *)", "Bash(composer show *)", "Bash(composer dump-autoload *)"],
        "ask": ["Bash(composer update *)", "Bash(composer require *)"],
    },
    "django": {
        "allow": ["Bash(python3 *)", "Bash(pip show *)", "Bash(python manage.py *)"],
        "ask": ["Bash(pip install *)", "Bash(pip uninstall *)"],
    },
    "go": {
        "allow": ["Bash(go build *)", "Bash(go test *)", "Bash(go vet *)", "Bash(go run *)"],
        "ask": ["Bash(go install *)", "Bash(go get *)"],
    },
    "rails": {
        "allow": ["Bash(ruby *)", "Bash(bundle exec *)", "Bash(rails *)"],
        "ask": ["Bash(bundle install *)", "Bash(bundle update *)", "Bash(gem install *)"],
    },
}
for _js_fw in ("nextjs", "next.js", "react", "nodejs", "node", "express", "fastify", "nestjs", "hono"):
    FW_COMMANDS[_js_fw] = _JS_COMMANDS


# ─── File extension filter per framework ───

FILE_EXT_MAP = {
    "laravel": r"\.php$", "django": r"\.py$", "go": r"\.go$",
    "rails": r"\.rb$", "nextjs": r"\.(ts|tsx|js|jsx)$", "react": r"\.(ts|tsx|js|jsx)$",
    "express": r"\.(ts|js)$",
}
for _alias in ("next.js", "nodejs", "node", "fastify", "nestjs", "hono"):
    FILE_EXT_MAP[_alias] = r"\.(ts|js)$"


# ─── Source directory filter per framework ───

SOURCE_DIR_MAP = {
    "laravel": "app/",
    "django": "",
    "go": "",
    "rails": "app/",
    "nextjs": "src/",
    "react": "src/",
    "express": "src/",
}
for _alias in ("next.js", "nodejs", "node", "fastify", "nestjs", "hono"):
    SOURCE_DIR_MAP[_alias] = "src/"


# ─── Discovery commands per framework ───

DISCOVERY_COMMANDS_MAP = {
    "laravel": """find app/Models -name "*.php" | sort
find app/Filament/Resources -maxdepth 1 -name "*.php" 2>/dev/null | sort
find app/Http/Controllers -name "*.php" | sort
find app/Services app/Jobs -name "*.php" 2>/dev/null | sort
find app/Policies -name "*.php" 2>/dev/null | sort""",
    "django": """find . -path "*/models.py" -type f | sort
find . -path "*/views.py" -type f | sort
find . -path "*/serializers.py" -type f 2>/dev/null | sort
find . -path "*/admin.py" -type f | sort
find . -path "*/tasks.py" -type f 2>/dev/null | sort""",
    "go": """find internal cmd pkg -name "*.go" -type f 2>/dev/null | sort
find . -name "*_test.go" -type f | sort
find . -name "*.go" -path "*/handler*" -o -name "*.go" -path "*/service*" 2>/dev/null | sort""",
    "rails": """find app/models -name "*.rb" | sort
find app/controllers -name "*.rb" | sort
find app/services -name "*.rb" 2>/dev/null | sort
find app/jobs -name "*.rb" 2>/dev/null | sort""",
    "nextjs": """find src/app -name "page.tsx" -o -name "layout.tsx" 2>/dev/null | sort
find src/components -name "*.tsx" 2>/dev/null | sort
find src/lib src/hooks -name "*.ts" 2>/dev/null | sort
find prisma -name "*.prisma" 2>/dev/null | sort""",
    "react": """find src/components -name "*.tsx" -o -name "*.jsx" 2>/dev/null | sort
find src/hooks -name "*.ts" -o -name "*.js" 2>/dev/null | sort
find src/lib src/utils -name "*.ts" 2>/dev/null | sort""",
    "express": """find src/api app/api -name "*.ts" -o -name "*.js" 2>/dev/null | sort
find src/services -name "*.ts" -o -name "*.js" 2>/dev/null | sort
find src/middleware -name "*.ts" -o -name "*.js" 2>/dev/null | sort""",
}
DISCOVERY_COMMANDS_MAP["next.js"] = DISCOVERY_COMMANDS_MAP["nextjs"]
for _alias in ("nodejs", "node", "fastify", "nestjs", "hono"):
    DISCOVERY_COMMANDS_MAP[_alias] = DISCOVERY_COMMANDS_MAP["express"]


# ─── DB tools per framework ───

DB_TOOLS_MAP = {
    "laravel": "Use Laravel Boost MCP `database-schema` and `database-query` tools if available, or `php artisan` schema commands.",
    "django": "Use `python manage.py inspectdb` for schema inspection, or connect directly with `psql`/`mysql` CLI.",
    "go": "Use `psql` or `mysql` CLI for direct database inspection. Check for GORM/sqlx migration files.",
    "rails": "Use `rails dbconsole` or `bundle exec rails db:schema:dump`. Check `db/schema.rb` for current state.",
    "nextjs": "Use Prisma CLI (`npx prisma db pull`, `npx prisma studio`) or direct `psql`/`mysql` access.",
    "react": "Check for API layer database access. Use `psql`/`mysql` CLI if backend is colocated.",
    "express": "Check for Sequelize/Knex/TypeORM migrations. Use `psql`/`mysql` CLI for direct access.",
}
DB_TOOLS_MAP["next.js"] = DB_TOOLS_MAP["nextjs"]
for _alias in ("nodejs", "node", "fastify", "nestjs", "hono"):
    DB_TOOLS_MAP[_alias] = DB_TOOLS_MAP["express"]


# ─── Maintenance commands per framework ───

MAINTENANCE_COMMANDS_MAP = {
    "laravel": """find app/Models -name "*.php" | sort
find app/Filament/Resources -maxdepth 1 -name "*.php" 2>/dev/null | sort
find app/Jobs -name "*.php" 2>/dev/null | sort
find app/Policies -name "*.php" 2>/dev/null | sort""",
    "django": """find . -path "*/models.py" -type f | sort
find . -path "*/views.py" -type f | sort
find . -path "*/tasks.py" -type f 2>/dev/null | sort""",
    "go": """find internal cmd pkg -name "*.go" -type f 2>/dev/null | sort
find . -name "*_test.go" -type f | sort""",
    "rails": """find app/models -name "*.rb" | sort
find app/controllers -name "*.rb" | sort
find app/services -name "*.rb" 2>/dev/null | sort""",
    "nextjs": """find src/app -name "*.tsx" -o -name "*.ts" 2>/dev/null | sort
find src/components -name "*.tsx" 2>/dev/null | sort""",
    "react": """find src/components -name "*.tsx" -o -name "*.jsx" 2>/dev/null | sort
find src/hooks -name "*.ts" 2>/dev/null | sort""",
    "express": """find src/api app/api -name "*.ts" -o -name "*.js" 2>/dev/null | sort
find src/services -name "*.ts" -o -name "*.js" 2>/dev/null | sort""",
}
MAINTENANCE_COMMANDS_MAP["next.js"] = MAINTENANCE_COMMANDS_MAP["nextjs"]
for _alias in ("nodejs", "node", "fastify", "nestjs", "hono"):
    MAINTENANCE_COMMANDS_MAP[_alias] = MAINTENANCE_COMMANDS_MAP["express"]


# ─── Hookify rules per framework ───

_JS_HOOKIFY = """## Rule: No any type
- trigger: Write or Edit containing `: any` or `as any`
- action: warn
- message: "Avoid 'any' type -- use proper TypeScript types."

## Rule: Error boundaries
- trigger: Write or Edit to `*/components/*.tsx`
- action: warn
- message: "Consider error boundaries for component error handling." """

HOOKIFY_RULES_MAP = {
    "laravel": """## Rule: No $guarded = []
- trigger: Write or Edit containing `$guarded = []`
- action: block
- message: "Use $fillable instead of $guarded = []. Security requirement."

## Rule: No inline FQCN
- trigger: Write or Edit containing `\\App\\Models\\` or `\\App\\Enum\\` inline
- action: warn
- message: "Add a use import at the top of the file instead of inline FQCN."

## Rule: Match over switch
- trigger: Write or Edit containing `switch (`
- action: warn
- message: "Use match() instead of switch(). PHP 8.1+ convention." """,
    "django": """## Rule: No raw SQL
- trigger: Write or Edit containing `.raw(` or `cursor.execute(`
- action: warn
- message: "Prefer ORM queries over raw SQL."

## Rule: Check for N+1 queries
- trigger: Write or Edit to `*/views.py`
- action: warn
- message: "Check for N+1 queries -- use select_related/prefetch_related." """,
    "go": """## Rule: No unchecked errors
- trigger: Write or Edit containing `_ = err` or `_ = error`
- action: warn
- message: "Do not ignore errors -- handle them explicitly."

## Rule: Context propagation
- trigger: Write or Edit to `*/handler*.go`
- action: warn
- message: "Ensure context.Context is passed through request handlers." """,
    "rails": """## Rule: Strong parameters required
- trigger: Write or Edit to `*/controllers/*.rb`
- action: warn
- message: "Use strong parameters for mass assignment protection."

## Rule: Check for N+1 queries
- trigger: Write or Edit to `*/controllers/*.rb`
- action: warn
- message: "Check for N+1 queries -- use .includes() or .preload()." """,
}
for _fw in ("nextjs", "react", "express", "nodejs", "node", "fastify", "nestjs", "hono"):
    HOOKIFY_RULES_MAP[_fw] = _JS_HOOKIFY


# ─── Framework-specific review checklist ───

def get_framework_checklist(config: dict) -> str:
    """Return framework-specific review checklist."""
    framework = config.get("techStack", {}).get("framework", "laravel").lower()
    has_filament = config.get("techStack", {}).get("hasFilament", False)

    if framework == "laravel":
        filament = ""
        if has_filament:
            filament = """
### Filament 3
- [ ] Form uses Section -> Tabs -> Tab -> Grid pattern
- [ ] Translation keys: dot notation
- [ ] `->authorize()` on actions
- [ ] `ResourceName::getUrl()` not `route()`
- [ ] Unique validation includes soft delete column check
"""
        return f"""### Laravel
- [ ] `match` over `switch`
- [ ] Helpers (auth(), str()) not Facades
- [ ] `$fillable` updated with inline comments
- [ ] Relationship keys always explicit
- [ ] Activity logging if applicable
{filament}
### Performance
- [ ] Eager loading present (no N+1)
- [ ] `->exists()` not `->count() > 0`

### Security
- [ ] `$fillable` defined (not `$guarded = []`)
- [ ] No string concat in `whereRaw()`
- [ ] No `addslashes()` for SQL

### Imports
- [ ] Grouped and alphabetical
- [ ] No inline FQCN"""

    elif framework in ("nextjs", "next.js"):
        return """### Next.js / React
- [ ] Server Components by default -- `'use client'` only when needed
- [ ] `next/image` not raw `<img>`, `next/link` not raw `<a>`
- [ ] No `useEffect` for data fetching in Server Components
- [ ] TypeScript strict mode -- no `any`
- [ ] Props destructured in function signature

### Performance
- [ ] Dynamic imports for heavy components
- [ ] `loading.tsx` for async routes
- [ ] No layout shifts (width/height on images)

### Security
- [ ] Zod validation on API inputs
- [ ] `NEXT_PUBLIC_` prefix only for client-exposed env vars
- [ ] No server secrets in client components

### Imports
- [ ] Absolute imports with `@/` prefix
- [ ] Grouped: React -> Next -> third-party -> local"""

    elif framework == "django":
        return """### Django
- [ ] Business logic in services, not views
- [ ] Serializer per use case (list/detail/create)
- [ ] `permission_classes` on every view
- [ ] Validators at model level

### Performance
- [ ] `select_related()` for ForeignKey (N+1)
- [ ] `prefetch_related()` for ManyToMany (N+1)
- [ ] `exists()` not `count() > 0`
- [ ] `bulk_create()` for batch operations

### Security
- [ ] Strong parameters via serializer validation
- [ ] `IsAuthenticated` permission on views
- [ ] No raw SQL with string formatting

### Imports
- [ ] Grouped: stdlib -> Django -> third-party -> local"""

    elif framework == "go":
        return """### Go
- [ ] All errors checked -- no `_ = err`
- [ ] Errors wrapped with context: `fmt.Errorf("doing X: %w", err)`
- [ ] `context.Context` as first param for I/O functions
- [ ] Interfaces defined where consumed

### Performance
- [ ] `Preload()` for GORM (N+1)
- [ ] Goroutines terminate (use context)
- [ ] No goroutine leaks

### Security
- [ ] Parameterized SQL queries
- [ ] Input validation before processing
- [ ] No secrets in code

### Imports
- [ ] Grouped: stdlib -> third-party -> local
- [ ] `goimports` formatted"""

    elif framework == "rails":
        return """### Rails
- [ ] Business logic in services, not controllers
- [ ] Strong parameters: `params.require().permit()`
- [ ] `dependent:` on has_many/has_one
- [ ] Validations at model level

### Performance
- [ ] `includes()` for eager loading (N+1)
- [ ] `find_each` for batch processing
- [ ] `exists?` not `count > 0`

### Security
- [ ] Authorization check on every action
- [ ] CSRF protection enabled
- [ ] No mass assignment without permit

### Imports
- [ ] Follow Zeitwerk naming conventions"""

    elif framework == "react":
        return """### React
- [ ] Functional components only -- no class components
- [ ] Custom hooks prefixed with `use`
- [ ] No `useEffect` for data fetching -- use React Query/SWR
- [ ] Props destructured in function signature
- [ ] TypeScript strict -- no `any`

### Performance
- [ ] `React.lazy()` for code splitting
- [ ] Virtualize long lists
- [ ] No objects/arrays created in render

### Security
- [ ] User input sanitized before rendering
- [ ] No secrets in frontend code
- [ ] Environment vars prefixed correctly (VITE_ or REACT_APP_)

### Imports
- [ ] Absolute imports with `@/` prefix
- [ ] Grouped: React -> third-party -> local"""

    elif framework in ("nodejs", "node", "express", "fastify", "nestjs", "hono"):
        return """### Node.js Backend
- [ ] Input validation on every endpoint (Zod/Joi)
- [ ] Business logic in services, not routes
- [ ] async/await -- no raw callbacks
- [ ] Structured logging -- no console.log in production
- [ ] Custom error classes with error middleware

### Performance
- [ ] N+1 prevented (Prisma `include` / Mongoose `populate`)
- [ ] Connection pooling configured
- [ ] Background jobs for heavy processing

### Security
- [ ] JWT tokens: short-lived access + refresh
- [ ] Rate limiting on all endpoints
- [ ] CORS whitelist -- not wildcard
- [ ] Helmet middleware for security headers
- [ ] No secrets in code

### Imports
- [ ] ES Modules (import/export)
- [ ] Grouped: Node builtins -> third-party -> local"""

    else:
        return """### General
- [ ] No duplicate code
- [ ] Error handling present
- [ ] No hardcoded secrets
- [ ] Tests exist for new code"""
