---
name: webapp
description: Use when working on any Webapp task — auditing, implementing features, fixing bugs, analyzing code.
disable-model-invocation: true
---

# Webapp — Project Orchestrator

Orchestrator for the Webapp project. This is a **routing table** (not an active agent) — Claude's main context reads this skill to decide which agent to dispatch for a given task.

## STRICT RULES

- NEVER commit code. User commits manually.
- NEVER modify files outside the assigned domain ownership.
- ALWAYS run review-agent on any code changes before reporting done.

## Domain Detection Keywords

| Domain | Keywords |
|--------|----------|
| api | endpoint serializer viewset |
| dashboard | admin panel reports |

## Dispatch Strategy

- **Single agent** (1 domain, no DB change): dispatch domain agent only
- **Sequential chain** (DB change needed): db-agent → domain-agent → review-agent
- **Multi-domain** (keywords match 2+ domains): dispatch team-lead to coordinate
- **Parallel** (independent domains): dispatch in parallel → review-agent
- **Full sweep** ("audit all", "check everything", "full review"): all domain agents → review-agent

## Agent Inventory

| Agent | Model | Memory | Description |
|-------|-------|--------|-------------|
| webapp-api | sonnet | project | api domain specialist |
| webapp-dashboard | sonnet | project | dashboard domain specialist |
| webapp-discovery | haiku | project | pre-implementation research (READ ONLY) |
| webapp-db | haiku | project | database schema (READ ONLY) |
| webapp-review | haiku | project | code quality gate (READ ONLY) |
| webapp-team-lead | sonnet | project | multi-agent coordinator |
| webapp-maintenance | sonnet | project | context file maintenance |
| webapp-query-optimizer | sonnet | project | database query optimization |

## Inter-Agent Communication

- **DONE** → dispatch review-agent (if code changed)
- **DONE_WITH_CONCERNS** → read concerns, decide if action needed
- **NEEDS_CONTEXT** → dispatch requested agent, re-dispatch original
- **BLOCKED** → stop, ask user for guidance
