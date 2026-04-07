"""Orchestrator SKILL.md and domain-map builders for buddyx-forge generator."""


def build_domain_map(config: dict) -> str:
    """Build domain-map.md — one section per domain."""
    sections = []
    for domain in config["domains"]:
        section = f"""## {domain}

### Read/Write
<!-- Populated by /buddyx-forge:scan or AI customization -->
<!-- Run /buddyx-forge:scan after adding code to populate this section -->

### Read Only
<!-- Dependencies from other domains -->"""
        sections.append(section)
    header = "# Domain Map - File Ownership\n\nEach domain agent owns specific files (read/write). Files not listed are READ ONLY for that agent.\n\n---\n\n"
    return header + "\n\n---\n\n".join(sections) + "\n"


def build_orchestrator_skill(config: dict, optional_agents: list = None) -> str:
    """Build the orchestrator SKILL.md."""
    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    keywords = config.get("domainKeywords", {})
    model_budget = config.get("modelBudget", "balanced")
    rw_model = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}.get(model_budget, "sonnet")
    ro_model = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}.get(model_budget, "haiku")

    # Build keywords table
    kw_rows = []
    for d in domains:
        kw = keywords.get(d, d.replace("-", ", "))
        kw_rows.append(f"| {d} | {kw} |")
    kw_table = "| Domain | Keywords |\n|--------|----------|\n" + "\n".join(kw_rows)

    # Build agent inventory with actual model from config
    inv_rows = []
    for d in domains:
        inv_rows.append(f"| {name}-{d} | {rw_model} | project | {d} domain specialist |")
    inv_rows.extend([
        f"| {name}-discovery | {ro_model} | project | pre-implementation research (READ ONLY) |",
        f"| {name}-db | {ro_model} | project | database schema (READ ONLY) |",
        f"| {name}-review | {ro_model} | project | code quality gate (READ ONLY) |",
        f"| {name}-team-lead | sonnet | project | multi-agent coordinator |",
        f"| {name}-maintenance | sonnet | project | context file maintenance |",
    ])
    # Add optional agents if present
    if optional_agents:
        for opt in optional_agents:
            if opt == "query-optimizer":
                opt_model = {"budget": "sonnet", "balanced": "sonnet", "quality": "opus"}.get(model_budget, "sonnet")
                inv_rows.append(f"| {name}-query-optimizer | {opt_model} | project | database query optimization |")
            elif opt == "mcp-dev":
                inv_rows.append(f"| {name}-mcp-dev | sonnet | project | MCP server development |")
            elif opt == "migration":
                inv_rows.append(f"| {name}-migration | sonnet | project | migration & permission specialist |")
    inv_table = "| Agent | Model | Memory | Description |\n|-------|-------|--------|-------------|\n" + "\n".join(inv_rows)

    return f"""---
name: {name}
description: Use when working on any {title} task — auditing, implementing features, fixing bugs, analyzing code.
disable-model-invocation: true
---

# {title} — Project Orchestrator

Orchestrator for the {title} project. This is a **routing table** (not an active agent) — Claude's main context reads this skill to decide which agent to dispatch for a given task.

## STRICT RULES

- NEVER commit code. User commits manually.
- NEVER modify files outside the assigned domain ownership.
- ALWAYS run review-agent on any code changes before reporting done.

## Domain Detection Keywords

{kw_table}

## Dispatch Strategy

- **Single agent** (1 domain, no DB change): dispatch domain agent only
- **Sequential chain** (DB change needed): db-agent → domain-agent → review-agent
- **Multi-domain** (keywords match 2+ domains): dispatch team-lead to coordinate
- **Parallel** (independent domains): dispatch in parallel → review-agent
- **Full sweep** ("audit all", "check everything", "full review"): all domain agents → review-agent

## Agent Inventory

{inv_table}

## Inter-Agent Communication

- **DONE** → dispatch review-agent (if code changed)
- **DONE_WITH_CONCERNS** → read concerns, decide if action needed
- **NEEDS_CONTEXT** → dispatch requested agent, re-dispatch original
- **BLOCKED** → stop, ask user for guidance
"""
