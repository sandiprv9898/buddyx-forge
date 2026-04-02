# Next.js + React Rules Reference

Use this when generating RULES.md for a Next.js project.

## Detection
package.json with "next" dependency.

## Tier 1: Universal Next.js Rules

### BEFORE WRITING ANY CODE
1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing hooks, utils, components — NEVER duplicate
4. Check if component should be Server Component or Client Component

### Next.js App Router
- Default to Server Components — only add 'use client' when needed
- 'use client' at the TOP of the file, before any imports
- Never import server-only code in client components
- Use loading.tsx for Suspense, error.tsx for error boundaries
- Metadata: export metadata object or generateMetadata(), not Head
- Route handlers in app/api/ use export async function GET/POST/PUT/DELETE
- Use next/navigation not next/router (App Router)
- Use next/image for all images, next/link for all internal links

### React Patterns
- Functional components only
- Custom hooks in hooks/ — prefix with use
- Props: destructure in function signature
- useCallback/useMemo only when profiled and needed
- Keys on lists: stable IDs, never array index

### TypeScript
- Strict mode always
- Interfaces for object shapes, types for unions
- No any — use unknown and narrow
- Props types: interface ComponentProps

### Data Fetching
- Server Components: fetch() directly
- Client Components: React Query or SWR
- API routes: validate input with Zod
- Mutations: Server Actions or API routes

### Performance
- Dynamic imports for heavy components
- loading.tsx for every async route
- Suspense boundaries for streaming
- Edge runtime for simple API routes

### Security
- Validate ALL user input (Zod schemas)
- NEXT_PUBLIC_ prefix for client-exposed env vars only
- Never expose server secrets in client components

### Imports
- Absolute imports with @/ prefix
- Group: React, Next, third-party, local
- Prefer named exports except pages/layouts

## Prisma Rules (if Prisma detected)
- Client in lib/prisma.ts (singleton)
- Never instantiate PrismaClient in API routes
- Migrations: npx prisma migrate dev

## NEVER DO
- Import from next/router (use next/navigation)
- Use getServerSideProps/getStaticProps (App Router)
- Put 'use client' on every component
- Use useEffect for data fetching in Server Components
- Commit .env.local
