# Tech Stack Detection Guide

Read this when performing Step 1 of /buddyx-forge setup.

## Framework Auto-Detection (check in order)

### 1. Check for config files

```bash
ls composer.json package.json requirements.txt pyproject.toml go.mod Gemfile Cargo.toml 2>/dev/null
```

| File Found | Framework | Language |
|------------|-----------|---------|
| `composer.json` with `laravel/framework` | **Laravel** | PHP |
| `package.json` with `next` | **Next.js** | TypeScript/JavaScript |
| `package.json` with `react` (no `next`) | **React (standalone)** | TypeScript/JavaScript |
| `package.json` with `express`/`fastify`/`@nestjs/core`/`hono` (no `react`/`next`) | **Node.js Backend** | TypeScript/JavaScript |
| `requirements.txt` or `pyproject.toml` with `django` | **Django** | Python |
| `go.mod` | **Go** | Go |
| `Gemfile` with `rails` | **Rails** | Ruby |

### 2. Framework-Specific Detection

#### Laravel (composer.json)
```bash
grep -q "laravel/framework" composer.json 2>/dev/null
```
- Version: extract from `"laravel/framework": "^11.0"`
- Filament: `grep -q "filament/filament" composer.json`
- Packages: spatie/permission, activitylog, maatwebsite/excel, mpdf
- MCP: check `.mcp.json` for `laravel-boost`
- DB: read `.env` → `DB_CONNECTION`
- Formatter: `vendor/bin/pint`
- Test runner: `php artisan test --filter=`
- Worktree symlinks: `["vendor", "node_modules"]`

#### Next.js (package.json)
```bash
grep -q '"next"' package.json 2>/dev/null
```
- Version: extract from `"next": "^15.0"`
- Prisma: `grep -q '"prisma"' package.json` or `grep -q '"@prisma/client"' package.json`
- tRPC: `grep -q '"@trpc/server"' package.json`
- Tailwind: `grep -q '"tailwindcss"' package.json`
- DB: read `.env` → `DATABASE_URL` or check Prisma schema
- Formatter: `npx prettier --write` or `npx eslint --fix`
- Test runner: `npx vitest run` or `npx jest --testPathPattern=`
- Worktree symlinks: `["node_modules", ".next"]`

#### React Standalone (package.json — has react, no next)
```bash
grep -q '"react"' package.json && ! grep -q '"next"' package.json 2>/dev/null
```
- Version: extract from `"react": "^19.0"`
- Router: `grep -q '"react-router-dom"' package.json`
- State: Zustand, Redux Toolkit, or Jotai
- Bundler: Vite (`"vite"`) or Webpack
- Styling: Tailwind, CSS Modules, styled-components
- DB: typically none (frontend-only) — check for API layer
- Formatter: `npx prettier --write` or `npx eslint --fix`
- Test runner: `npx vitest run` or `npx jest`
- Worktree symlinks: `["node_modules"]`

#### Node.js Backend (package.json — has express/fastify/nestjs/hono, no react/next)
```bash
grep -qE '"express"|"fastify"|"@nestjs/core"|"hono"' package.json && ! grep -q '"react"' package.json 2>/dev/null
```
- Framework: Express, Fastify, NestJS, or Hono
- ORM: Prisma, Mongoose, Sequelize, TypeORM, Drizzle
- Queue: BullMQ, Bull
- Auth: passport, jsonwebtoken
- Validation: Zod, Joi, class-validator (NestJS)
- DB: read `.env` → `DATABASE_URL`
- Formatter: `npx prettier --write` or `npx eslint --fix`
- Test runner: `npx vitest run` or `npx jest`
- Worktree symlinks: `["node_modules"]`

#### Django (requirements.txt / pyproject.toml)
```bash
grep -qi "django" requirements.txt pyproject.toml 2>/dev/null
```
- Version: extract from `django>=5.0` or `Django==5.0`
- DRF: `grep -q "djangorestframework" requirements.txt`
- Celery: `grep -q "celery" requirements.txt`
- DB: read `settings.py` → `DATABASES['default']['ENGINE']`
- Formatter: `black` or `ruff format`
- Test runner: `pytest` or `python manage.py test`
- Worktree symlinks: `["venv", ".venv"]`

#### Go (go.mod)
```bash
test -f go.mod
```
- Version: extract from `go 1.22`
- Web framework: `grep -E "gin-gonic|gofiber|labstack/echo" go.mod`
- ORM: `grep -q "gorm.io/gorm" go.mod`
- DB driver: `grep -E "pgx|go-sql-driver" go.mod`
- Formatter: `gofmt` (built-in)
- Test runner: `go test -run`
- Worktree symlinks: `[]` (Go uses module cache)

#### Rails (Gemfile)
```bash
grep -q "rails" Gemfile 2>/dev/null
```
- Version: extract from `gem 'rails', '~> 7.1'`
- Sidekiq: `grep -q "sidekiq" Gemfile`
- Devise: `grep -q "devise" Gemfile`
- RSpec: `grep -q "rspec-rails" Gemfile`
- DB: read `config/database.yml` → adapter
- Formatter: `rubocop -a` or `standardrb --fix`
- Test runner: `bundle exec rspec` or `rails test`
- Worktree symlinks: `["vendor/bundle"]`

### 3. Domain Detection (per framework)

| Framework | Scan | Domain Heuristic |
|-----------|------|-----------------|
| Laravel | `app/Models/`, `app/Filament/Resources/`, `app/Http/Controllers/` | Model name prefix, Resource name, Controller namespace |
| Next.js | `src/app/`, `src/components/`, `prisma/schema.prisma` | Route groups `(auth)`, `(dashboard)`, Prisma model groups |
| Django | `apps/*/`, `*/models.py`, `*/views.py` | Django app names |
| Go | `internal/*/`, `cmd/*/`, `pkg/*/` | Package directory names |
| Rails | `app/models/`, `app/controllers/`, `app/services/` | Model clusters, Controller namespaces |

### 4. MCP Server Detection

Read `.mcp.json` if it exists. Extract server names.

Also detect framework-specific MCP:
- Laravel: `laravel-boost` (in composer.json or .mcp.json)
- Prisma: `prisma` MCP (in package.json)

### 5. Output

Present to user:

```
Detected tech stack:
  Framework: {framework} {version}
  Language: {language}
  Sub-frameworks: {Filament/Prisma/DRF/Gin/Sidekiq etc.}
  Database: {type}
  Formatter: {command}
  Test runner: {command}
  MCP servers: {list or "none"}
  Potential domains: [{list}]

Framework rules: references/framework-{name}.md

Is this correct? Any changes?
```
