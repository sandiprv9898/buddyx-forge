---
name: myapp
description: Use when working on any Myapp task — auditing, implementing features, fixing bugs, analyzing code.
disable-model-invocation: true
---

# Myapp — Project Orchestrator

Orchestrator for the Myapp project. Parses intent, selects domain/infrastructure agents, dispatches with context.

## STRICT RULES

- NEVER commit code. User commits manually.
- NEVER modify files outside the assigned domain ownership.
- ALWAYS run review-agent on any code changes before reporting done.

## Domain Detection Keywords

| Domain | Keywords |
|--------|----------|
| billing | invoice payment subscription |
| auth | login token session |
| users | profile account settings |

## Dispatch Strategy

- **Single agent** (1 domain, no DB change): dispatch domain agent only
- **Sequential chain** (DB change needed): db-agent → domain-agent → review-agent
- **Parallel** (independent domains): dispatch in parallel → review-agent
- **Full sweep** (all domains): all domain agents → review-agent

## Agent Inventory

| Agent | Model | Memory | Description |
|-------|-------|--------|-------------|
| myapp-billing | sonnet | project | billing domain specialist |
| myapp-auth | sonnet | project | auth domain specialist |
| myapp-users | sonnet | project | users domain specialist |
| myapp-discovery | haiku | project | pre-implementation research (READ ONLY) |
| myapp-db | haiku | project | database schema (READ ONLY) |
| myapp-review | haiku | project | code quality gate (READ ONLY) |
| myapp-team-lead | sonnet | project | multi-agent coordinator |
| myapp-maintenance | sonnet | project | context file maintenance |
| myapp-query-optimizer | sonnet | project | database query optimization |

## Inter-Agent Communication

- **DONE** → dispatch review-agent (if code changed)
- **DONE_WITH_CONCERNS** → read concerns, decide if action needed
- **NEEDS_CONTEXT** → dispatch requested agent, re-dispatch original
- **BLOCKED** → stop, ask user for guidance
