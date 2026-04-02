# React (Standalone) Rules Reference

Use this when generating RULES.md for a React project WITHOUT Next.js (Vite, CRA, or custom bundler).

## Detection
package.json with "react" but NOT "next".

## Tier 1: Universal React Rules

### BEFORE WRITING ANY CODE
1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing hooks, utils, components — NEVER duplicate

### React Patterns
- Functional components only — no class components
- Custom hooks in hooks/ — prefix with use
- Props: destructure in function signature
- Composition over inheritance
- Avoid prop drilling — use Context, Zustand, or composition
- useCallback/useMemo only when profiled and needed
- Controlled components for forms

### TypeScript
- Strict mode always
- interface for component props
- No any — use unknown and narrow
- as const for literal types

### State Management
- Local: useState (simple), useReducer (complex)
- Shared: Zustand or Redux Toolkit
- Server state: React Query or SWR — NOT useEffect + fetch
- Form state: React Hook Form

### Data Fetching
- React Query/SWR for all API calls
- Never useEffect + fetch + useState manually
- API client in lib/api.ts — not inline in components
- Type all API responses

### Performance
- React.lazy() + Suspense for code splitting
- Virtualize long lists
- Debounce search inputs
- Avoid creating objects/arrays in render

### Security
- Sanitize user input before rendering
- Environment vars: VITE_ prefix for Vite, REACT_APP_ for CRA
- Never store secrets in frontend code

### File Organization
- src/components/ for shared UI
- src/pages/ or src/views/ for route components
- src/hooks/ for custom hooks
- src/services/ for API client
- src/types/ for shared types

### Imports
- Absolute imports with @/ prefix
- Group: React, third-party, local
- Prefer named exports

## NEVER DO
- Use class components
- Use useEffect for data fetching
- Mutate state directly
- Commit .env.local or API keys
- Create god components (>300 lines)
