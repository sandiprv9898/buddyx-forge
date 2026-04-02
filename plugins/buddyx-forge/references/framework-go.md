# Go Rules Reference

Use this when generating RULES.md for a Go project.

## Detection

```
// go.mod
module github.com/user/project
go 1.22
```

Also detect:
- `github.com/gin-gonic/gin` → Gin web framework
- `github.com/gofiber/fiber` → Fiber web framework
- `github.com/labstack/echo` → Echo web framework
- `gorm.io/gorm` → GORM ORM
- `github.com/jackc/pgx` → PostgreSQL driver
- `github.com/stretchr/testify` → Test assertions

## Tier 1: Universal Go Rules (always include)

### BEFORE WRITING ANY CODE

1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing functions, interfaces, packages — NEVER duplicate
4. Run `go vet` and `golangci-lint` mentally before writing

### Go Conventions

- `gofmt` formatting is mandatory — never argue about style
- Exported names: PascalCase. Unexported: camelCase
- Package names: short, lowercase, single word — no underscores
- Error handling: always check errors — never `_ = err`
- Return early: check errors first, avoid deep nesting
- `context.Context` as first parameter in functions that do I/O
- Interfaces: define where consumed, not where implemented (accept interfaces, return structs)
- Small interfaces: 1-3 methods. Split large interfaces

### Error Handling

- Always check returned errors: `if err != nil { return fmt.Errorf("context: %w", err) }`
- Wrap errors with `fmt.Errorf("doing X: %w", err)` for context
- Sentinel errors: `var ErrNotFound = errors.New("not found")`
- Custom error types for errors that carry data
- Never panic in library code — only in main/init for unrecoverable
- `errors.Is()` and `errors.As()` for checking — not string comparison

### Concurrency

- Goroutines: always ensure they terminate (use `context.Context`)
- Channels: prefer over shared memory + mutex
- `sync.WaitGroup` for waiting on multiple goroutines
- `defer` for cleanup: mutex unlock, file close, connection release
- Never leak goroutines: use `select` with `ctx.Done()`
- Race conditions: run tests with `-race` flag

### Database (GORM or raw)

- Connection pooling: set `MaxOpenConns`, `MaxIdleConns`, `ConnMaxLifetime`
- Prepared statements for repeated queries
- Transactions: `db.Transaction(func(tx *gorm.DB) error { ... })`
- GORM: use `Preload()` to prevent N+1 queries
- Raw SQL: parameterized only — `db.Raw("SELECT * FROM users WHERE id = ?", id)`
- Migrations: use `golang-migrate` or GORM AutoMigrate (dev only)

### API Design

- RESTful: proper HTTP methods + status codes
- Request validation: parse + validate before business logic
- JSON tags on all struct fields: `json:"field_name"`
- Middleware for auth, logging, CORS, rate limiting
- Graceful shutdown: listen for `SIGINT`/`SIGTERM`

### Testing

- Table-driven tests: `tests := []struct{ name string; input; want }{ ... }`
- `t.Parallel()` for independent tests
- `testify/assert` for assertions (if available)
- Test file next to source: `handler.go` → `handler_test.go`
- Mocks: interfaces + mock implementations, or `testify/mock`
- `t.Helper()` in test helper functions
- Integration tests with build tag: `//go:build integration`

### File Organization

```
cmd/
  server/main.go          — entry point
internal/
  handler/                — HTTP handlers
  service/                — business logic
  repository/             — database access
  model/                  — domain models
  middleware/             — HTTP middleware
pkg/                      — shared packages (importable by other projects)
config/                   — configuration loading
migrations/               — database migrations
```

- `internal/` for private packages — cannot be imported externally
- `cmd/` for entry points — one per binary
- Domain logic in `service/`, not in handlers
- Database access in `repository/` — handlers never query DB directly

### Imports

- Group: stdlib → third-party → local
- `goimports` handles formatting and grouping
- No dot imports (except in test files if needed)
- No alias unless name collision

### Performance

- `sync.Pool` for frequently allocated objects
- `strings.Builder` for string concatenation in loops
- Profile before optimizing: `pprof`
- Avoid allocations in hot paths
- Use `[]byte` not `string` for large data manipulation

## NEVER DO

- Ignore errors: `result, _ := doSomething()`
- Use `panic` for normal error flow
- Use `init()` for complex logic — keep it for simple registration
- Commit vendor/ (use go modules)
- Use global mutable state — pass dependencies explicitly
- Write to stdout — use structured logging (`slog` or `zap`)
