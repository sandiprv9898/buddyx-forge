# Node.js Backend Rules Reference

Use this when generating RULES.md for a Node.js backend (Express, Fastify, NestJS, Hono).

## Detection
package.json with "express"/"fastify"/"@nestjs/core"/"hono" but NOT "react"/"next".

## Tier 1: Universal Node.js Rules

### BEFORE WRITING ANY CODE
1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing middleware, utils, services — NEVER duplicate

### Node.js Conventions
- ES Modules (import/export) — not CommonJS
- async/await for all async operations
- Error handling: always try/catch async routes, or error middleware
- Environment: validated config module — never raw process.env in logic
- Structured logging (pino/winston) — never console.log in production
- Graceful shutdown: handle SIGTERM/SIGINT

### API Patterns
- Router per resource
- Middleware chain: auth, validation, handler, error
- Request validation: Zod schemas at route level
- Consistent response format: { data, error, meta }
- Proper HTTP status codes
- Error middleware: centralized, not try/catch everywhere
- No business logic in routes — delegate to services

### TypeScript
- Strict mode always
- Type request/response
- No any — use unknown for external data
- Zod schemas as types: type User = z.infer<typeof UserSchema>

### Architecture
- routes/ — HTTP definitions + validation
- services/ — business logic
- repositories/ — database access
- middleware/ — auth, logging, errors
- types/ — shared TypeScript types

### Database
- Prisma: singleton client
- Transactions for multi-step writes
- N+1: use include (Prisma) or populate (Mongoose)
- Connection pooling configured

### Security
- Input validation on EVERY endpoint
- JWT: short-lived access + refresh tokens
- Rate limiting
- CORS whitelist — never wildcard in production
- Helmet for security headers
- Parameterized queries only

### Testing
- Vitest or Jest
- Supertest for HTTP tests
- Test services (unit) AND routes (integration)
- Factory functions for test data

### Imports
- Absolute imports with @/ prefix
- Group: Node builtins, third-party, local
- Named exports preferred

## NestJS Rules (if detected)
- Modules: one per feature domain
- Injectable services
- DTOs with class-validator
- Guards for auth
- Pipes for validation

## NEVER DO
- Use console.log in production
- Store secrets in code
- Skip input validation
- Ignore unhandled promise rejections
- Commit node_modules/ or .env
- Write sync file I/O in request handlers
