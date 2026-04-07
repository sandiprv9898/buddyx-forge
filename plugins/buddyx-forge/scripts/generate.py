#!/usr/bin/env python3
"""
buddyx-forge generator — creates .claude/ directory from config + templates.
Zero external dependencies. Python 3.8+ stdlib only.
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

# Ensure scripts/ is on sys.path for both CLI and test imports
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Re-export for backward compatibility (tests import from generate)
from validators import load_config  # noqa: E402
from builders.settings import build_settings_json  # noqa: E402
from builders.agents import build_review_agent, build_team_lead_agent
from builders.rules import build_rules_md, build_claude_md
from builders.orchestrator import build_orchestrator_skill, build_domain_map
from builders.frameworks import (
    FILE_EXT_MAP, SOURCE_DIR_MAP, DISCOVERY_COMMANDS_MAP,
    DB_TOOLS_MAP, MAINTENANCE_COMMANDS_MAP, HOOKIFY_RULES_MAP,
)


def render_template(template_name: str, replacements: dict) -> str:
    """Read a .tmpl file and perform string replacements."""
    tmpl_path = TEMPLATES_DIR / template_name
    if not tmpl_path.exists():
        raise FileNotFoundError(f"Required template missing: {tmpl_path}")
    content = tmpl_path.read_text()
    for key, value in replacements.items():
        content = content.replace(f"{{{key}}}", str(value))
    # Warn about unreplaced placeholders (exclude bash ${VAR}, HTML {{VAR}}, and lowercase doc examples)
    remaining = re.findall(r'(?<!\$)(?<!\{)\{[A-Z][A-Z_]{2,}\}(?!\})', content)
    if remaining:
        print(f"WARNING: Unreplaced placeholders in {template_name}: {remaining}", file=sys.stderr)
    return content


_dry_run_counter = [0]


def write_file(output_dir: str, rel_path: str, content: str, dry_run: bool = False):
    """Write content to a file, creating directories as needed."""
    full_path = Path(output_dir) / rel_path
    if dry_run:
        _dry_run_counter[0] += 1
        print(f"  WOULD CREATE: {full_path}")
        return
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)


def make_executable(output_dir: str, rel_path: str, dry_run: bool = False):
    """Make a file executable."""
    if dry_run:
        return
    full_path = Path(output_dir) / rel_path
    if full_path.exists():
        full_path.chmod(full_path.stat().st_mode | 0o111)


# ─── MAIN GENERATOR ───


def generate(config: dict, output_dir: str, dry_run: bool = False):
    """Generate the complete .claude/ directory."""
    _dry_run_counter[0] = 0

    name = config["projectName"]
    title = name.replace("-", " ").title()
    domains = config["domains"]
    hooks_cfg = config.get("hooks", {})
    eval_level = config.get("evalLevel", "none")
    has_memory = config.get("agentMemory", True)
    commit_policy = config.get("commitPolicy", "user")
    model_budget = config.get("modelBudget", "balanced")
    formatter = config.get("techStack", {}).get("formatter", "")
    test_runner = config.get("techStack", {}).get("testRunner", "")

    # Model mapping
    model_map_ro = {"budget": "haiku", "balanced": "haiku", "quality": "sonnet"}
    model_map_rw = {"budget": "haiku", "balanced": "sonnet", "quality": "sonnet"}
    ro_model = model_map_ro.get(model_budget, "haiku")
    rw_model = model_map_rw.get(model_budget, "sonnet")

    # Framework
    framework = config.get("techStack", {}).get("framework", "laravel").lower()

    if dry_run:
        print(f"\n=== buddyx-forge DRY RUN for '{name}' ===\n")

    # Memory instructions (conditional on agentMemory flag)
    if has_memory:
        memory_instructions_domain = f"1. READ `.claude/agent-memory/{name}-{{DOMAIN}}/MEMORY.md`\n2. READ `.claude/agent-memory/shared-learnings.md`"
        memory_write_domain = f"WRITE to `.claude/agent-memory/{name}-{{DOMAIN}}/MEMORY.md`:"
        memory_after_domain = f"""WRITE to `.claude/agent-memory/{name}-{{DOMAIN}}/MEMORY.md`:
1. New patterns discovered
2. Gotchas encountered
3. If you verified a hypothesis from shared-learnings.md, write: `[CONFIRM: pattern description]`
4. If you discovered a new pattern, add to shared-learnings.md as `[NEW 0/3] [YYYY-MM-DD] description`"""
    else:
        memory_instructions_domain = "1. Check project CLAUDE.md for recent learnings and conventions."
        memory_write_domain = "Report any new patterns or conventions you discovered."
        memory_after_domain = "Report any new patterns or conventions you discovered to the user."

    # Per-agent infra memory (agent-specific paths)
    def _mem_infra(agent_suffix):
        if has_memory:
            return (
                f"1. READ `.claude/agent-memory/{name}-{agent_suffix}/MEMORY.md`\n2. READ `.claude/agent-memory/shared-learnings.md`",
                f"WRITE to `.claude/agent-memory/{name}-{agent_suffix}/MEMORY.md` if you discovered new patterns."
            )
        return (
            "1. Check project CLAUDE.md for recent learnings and conventions.",
            "Report any new patterns or conventions you discovered."
        )

    # Commit hook block (conditional on commitPolicy)
    if commit_policy == "user":
        commit_hook_block = """hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ".claude/scripts/block-git-commit.sh\""""
    else:
        commit_hook_block = ""

    # Common replacements for templates
    common = {
        "PROJECT_NAME": name,
        "PROJECT_TITLE": title,
        "READONLY_MODEL": ro_model,
        "DOMAIN_MODEL": rw_model,
        "FORMATTER_CMD": formatter,
        "TEST_RUNNER": test_runner,
        "FRAMEWORK": framework,
        "FILE_EXT_FILTER": FILE_EXT_MAP.get(framework, r"\.php$"),
        "SOURCE_DIR_FILTER": SOURCE_DIR_MAP.get(framework, ""),
        "DISCOVERY_COMMANDS": DISCOVERY_COMMANDS_MAP.get(framework, DISCOVERY_COMMANDS_MAP["laravel"]),
        "DB_TOOLS": DB_TOOLS_MAP.get(framework, DB_TOOLS_MAP["laravel"]),
        "MAINTENANCE_COMMANDS": MAINTENANCE_COMMANDS_MAP.get(framework, MAINTENANCE_COMMANDS_MAP["laravel"]),
        "FRAMEWORK_HOOKIFY_RULES": (
            ('## Rule: Block migrations in this project\n- trigger: Write or Edit to `database/migrations/` or `database/seeders/`\n- action: block\n- message: "Migrations must be created in the shared database project, not here."\n\n' if config.get("sharedDb") else '')
            + HOOKIFY_RULES_MAP.get(framework, HOOKIFY_RULES_MAP.get("laravel", ""))
        ),
        "MEMORY_INSTRUCTIONS_DOMAIN": memory_instructions_domain,
        "MEMORY_INSTRUCTIONS_INFRA": _mem_infra("discovery")[0],
        "MEMORY_WRITE_DOMAIN": memory_write_domain,
        "MEMORY_AFTER_DOMAIN": memory_after_domain,
        "MEMORY_WRITE_INFRA": _mem_infra("discovery")[1],
        "COMMIT_HOOK_BLOCK": commit_hook_block,
    }

    # Pre-compute optional agents for orchestrator inventory
    pre_optional = []
    fw_for_opt = config.get("techStack", {}).get("framework", "laravel").lower()
    if config.get("sharedDb"):
        pre_optional.append("migration")
    if fw_for_opt in ("laravel", "django", "rails", "nextjs", "next.js"):
        pre_optional.append("query-optimizer")
    if bool(config.get("mcpServers")) or fw_for_opt in ("nodejs", "node", "express", "fastify"):
        pre_optional.append("mcp-dev")

    # ─── Phase A: Python-generated files ───

    # 1. settings.json (builder)
    write_file(output_dir, "settings.json", build_settings_json(config), dry_run)

    # 2. Domain agents (template)
    for domain in domains:
        domain_title = domain.replace("-", " ").title()
        source_dir = SOURCE_DIR_MAP.get(framework, "")
        ext = FILE_EXT_MAP.get(framework, r"\.php$").replace(r"\.", ".").replace("$", "").replace("(", "").replace(")", "").replace("|", ", ")
        domain_files_hint = f"Look for files related to `{domain}` in `{source_dir}` with extensions: {ext}\n<!-- Run /buddyx-forge:scan to populate exact file paths -->"
        replacements = {
            **common,
            "DOMAIN": domain,
            "DOMAIN_TITLE": domain_title,
            "DOMAIN_DESCRIPTION": f"{domain_title} specialist. Use when working on {domain}-related tasks.",
            "DOMAIN_FILES_HINT": domain_files_hint,
        }
        content = render_template("agent-domain.tmpl", replacements)
        write_file(output_dir, f"agents/{name}-{domain}.md", content, dry_run)

    # 3. Infrastructure agents (template + builders)
    for agent_tmpl in ["agent-discovery.tmpl", "agent-db.tmpl", "agent-maintenance.tmpl"]:
        agent_name = agent_tmpl.replace("agent-", "").replace(".tmpl", "")
        mem_read, mem_write = _mem_infra(agent_name)
        infra_replacements = {**common, "MEMORY_INSTRUCTIONS_INFRA": mem_read, "MEMORY_WRITE_INFRA": mem_write}
        content = render_template(agent_tmpl, infra_replacements)
        write_file(output_dir, f"agents/{name}-{agent_name}.md", content, dry_run)

    # Review agent (builder)
    write_file(output_dir, f"agents/{name}-review.md", build_review_agent(config), dry_run)

    # Team-lead agent (builder)
    write_file(output_dir, f"agents/{name}-team-lead.md", build_team_lead_agent(config), dry_run)

    # 3b. Optional agents
    optional_agents = []

    # Migration agent — only if shared DB configured
    shared_db = config.get("sharedDb")
    if shared_db:
        mig_mem_r, mig_mem_w = _mem_infra("migration")
        mig_content = render_template("agent-migration.tmpl", {
            **common,
            "SHARED_DB_PATH": shared_db,
            "MEMORY_INSTRUCTIONS_INFRA": mig_mem_r,
            "MEMORY_WRITE_INFRA": mig_mem_w,
        })
        write_file(output_dir, f"agents/{name}-migration.md", mig_content, dry_run)
        optional_agents.append("migration")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-migration"})
            write_file(output_dir, f"agent-memory/{name}-migration/MEMORY.md", mem_content, dry_run)

    # Query optimizer agent — always for Laravel/Filament, optional for others
    if framework in ("laravel", "django", "rails", "nextjs", "next.js"):
        optimizer_model = {"budget": "sonnet", "balanced": "sonnet", "quality": "opus"}.get(model_budget, "sonnet")
        qo_mem_r, qo_mem_w = _mem_infra("query-optimizer")
        opt_content = render_template("agent-query-optimizer.tmpl", {
            **common,
            "OPTIMIZER_MODEL": optimizer_model,
            "MEMORY_INSTRUCTIONS_INFRA": qo_mem_r,
            "MEMORY_WRITE_INFRA": qo_mem_w,
        })
        write_file(output_dir, f"agents/{name}-query-optimizer.md", opt_content, dry_run)
        optional_agents.append("query-optimizer")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-query-optimizer"})
            write_file(output_dir, f"agent-memory/{name}-query-optimizer/MEMORY.md", mem_content, dry_run)

    # MCP dev agent — if project has .mcp.json or builds MCP servers
    has_mcp = bool(config.get("mcpServers")) or framework in ("nodejs", "node", "express", "fastify")
    if has_mcp:
        mcp_mem_r, mcp_mem_w = _mem_infra("mcp-dev")
        mcp_content = render_template("agent-mcp-dev.tmpl", {**common, "MEMORY_INSTRUCTIONS_INFRA": mcp_mem_r, "MEMORY_WRITE_INFRA": mcp_mem_w})
        write_file(output_dir, f"agents/{name}-mcp-dev.md", mcp_content, dry_run)
        optional_agents.append("mcp-dev")
        if has_memory:
            mem_content = render_template("memory.tmpl", {"AGENT_NAME": f"{name}-mcp-dev"})
            write_file(output_dir, f"agent-memory/{name}-mcp-dev/MEMORY.md", mem_content, dry_run)

    # 4. Orchestrator SKILL.md (builder)
    write_file(output_dir, f"skills/{name}/SKILL.md", build_orchestrator_skill(config, pre_optional), dry_run)

    # 5. Domain map (builder)
    write_file(output_dir, f"skills/{name}/context/domain-map.md", build_domain_map(config), dry_run)

    # 6. Shared learnings + memory (respect agentMemory flag)
    if has_memory:
        content = render_template("shared-learnings.tmpl", common)
        write_file(output_dir, "agent-memory/shared-learnings.md", content, dry_run)

        # Learning queue
        write_file(output_dir, "agent-memory/learning-queue.md",
                   "# Learning Queue\n\n> Auto-captured from agent transcripts. Review periodically.\n> Move useful entries to shared-learnings.md as [NEW 0/3].\n", dry_run)

        # Per-agent memory
        all_agents = [f"{name}-{d}" for d in domains] + [
            f"{name}-discovery", f"{name}-db", f"{name}-review",
            f"{name}-team-lead", f"{name}-maintenance",
        ]
        for agent in all_agents:
            content = render_template("memory.tmpl", {"AGENT_NAME": agent})
            write_file(output_dir, f"agent-memory/{agent}/MEMORY.md", content, dry_run)

    # 7. Agent context skeletons
    for domain in domains:
        write_file(output_dir, f"skills/{name}/context/agent-context/{domain}-context.md",
                   f"# {domain.replace('-', ' ').title()} Domain Context\n\n## Table Schemas\n<!-- Populated by /buddyx-forge:scan -->\n\n## Model Snippets\n<!-- Populated by /buddyx-forge:scan -->\n", dry_run)

    # 8. Database tables skeleton
    write_file(output_dir, f"skills/{name}/context/database-tables.md",
               "# Database Tables\n\n<!-- Populated by /buddyx-forge:scan -->\n", dry_run)

    # 9. AGENTS.md (cross-tool compatibility — Cursor, Copilot, Codex)
    agents_rows = []
    for d in domains:
        agents_rows.append(f"| {name}-{d} | {d.replace('-', ' ').title()} specialist | {rw_model} | Domain |")
    agents_rows.extend([
        f"| {name}-discovery | Pre-implementation research | {ro_model} | Infrastructure |",
        f"| {name}-db | Database schema inspection | {ro_model} | Infrastructure |",
        f"| {name}-review | Code quality gate | {ro_model} | Infrastructure |",
        f"| {name}-team-lead | Multi-agent coordinator | sonnet | Infrastructure |",
        f"| {name}-maintenance | Context maintenance | sonnet | Infrastructure |",
    ])
    agents_table = "| Agent | Description | Model | Type |\n|-------|-------------|-------|------|\n" + "\n".join(agents_rows)
    agents_md = render_template("agents-md.tmpl", {
        **common,
        "AGENTS_TABLE": agents_table,
    })
    write_file(output_dir, "AGENTS.md", agents_md, dry_run)

    # 10. CLAUDE.md (complete — no AI needed)
    write_file(output_dir, "CLAUDE.md", build_claude_md(config), dry_run)

    # 11. RULES.md (complete — framework-specific, no AI needed)
    write_file(output_dir, f"skills/{name}/RULES.md", build_rules_md(config), dry_run)

    # 12. Diagram skill
    diagram_content = render_template("diagram-skill.tmpl", {
        **common,
        "EXAMPLE_DOMAIN": domains[0] if domains else "example",
    })
    write_file(output_dir, f"skills/{name}/diagram/SKILL.md", diagram_content, dry_run)

    # 13. Audit skill
    domain_list_md = "\n".join([f"| `{d}` | {d.replace('-', ' ').title()} |" for d in domains])
    audit_content = render_template("audit-skill.tmpl", {
        **common,
        "DOMAIN_LIST": f"| Module | Description |\n|--------|-------------|\n{domain_list_md}",
    })
    write_file(output_dir, f"skills/{name}/audit/SKILL.md", audit_content, dry_run)

    # 14. Audit HTML template (copy as-is)
    audit_html_src = TEMPLATES_DIR / "module-audit-template.html"
    if audit_html_src.exists():
        content = audit_html_src.read_text()
        write_file(output_dir, "templates/module-audit-template.html", content, dry_run)

    # 15. Output directories
    write_file(output_dir, "diagrams/.gitkeep", "", dry_run)
    write_file(output_dir, "audits/.gitkeep", "", dry_run)

    # 16. Dashboard HTML template
    dash_src = TEMPLATES_DIR / "dashboard.html.tmpl"
    if dash_src.exists():
        content = dash_src.read_text().replace("{PROJECT_TITLE}", title)
        write_file(output_dir, "dashboard/dashboard-template.html", content, dry_run)

    # 17. Hookify rules
    hookify_content = render_template("hookify-rules.tmpl", common)
    write_file(output_dir, "hookify-rules.md", hookify_content, dry_run)

    # ─── Hook scripts ───

    hook_scripts = []

    if hooks_cfg.get("contextInjection", False):
        content = render_template("hooks/inject-prompt-context.sh.tmpl", common)
        write_file(output_dir, "scripts/inject-prompt-context.sh", content, dry_run)
        hook_scripts.append("scripts/inject-prompt-context.sh")

    if hooks_cfg.get("blockDangerous", False):
        content = render_template("hooks/safety-guard.sh.tmpl", common)
        write_file(output_dir, "scripts/safety-guard.sh", content, dry_run)
        hook_scripts.append("scripts/safety-guard.sh")

    if commit_policy == "user":
        content = render_template("hooks/block-git-commit.sh.tmpl", common)
        write_file(output_dir, "scripts/block-git-commit.sh", content, dry_run)
        hook_scripts.append("scripts/block-git-commit.sh")

    if hooks_cfg.get("blockMigration", False):
        content = render_template("hooks/block-migration.sh.tmpl", common)
        write_file(output_dir, "scripts/block-migration.sh", content, dry_run)
        hook_scripts.append("scripts/block-migration.sh")

    if hooks_cfg.get("autoFormat", False) and formatter:
        content = render_template("hooks/auto-format-new-files.sh.tmpl", common)
        write_file(output_dir, "scripts/auto-format-new-files.sh", content, dry_run)
        hook_scripts.append("scripts/auto-format-new-files.sh")

    content = render_template("hooks/detect-new-file-created.sh.tmpl", common)
    write_file(output_dir, "scripts/detect-new-file-created.sh", content, dry_run)
    hook_scripts.append("scripts/detect-new-file-created.sh")

    # Eval scripts
    if eval_level in ("full", "basic"):
        for tmpl in ["track-agent-start.sh.tmpl", "track-session-count.sh.tmpl"]:
            content = render_template(f"hooks/eval/{tmpl}", common)
            script_name = tmpl.replace(".tmpl", "")
            write_file(output_dir, f"scripts/eval/{script_name}", content, dry_run)
            hook_scripts.append(f"scripts/eval/{script_name}")

    if eval_level == "full":
        for tmpl in ["validate-agent-output.sh.tmpl", "extract-learnings.sh.tmpl",
                      "prompt-save-learnings.sh.tmpl", "auto-promote-learnings.sh.tmpl"]:
            content = render_template(f"hooks/eval/{tmpl}", common)
            script_name = tmpl.replace(".tmpl", "")
            write_file(output_dir, f"scripts/eval/{script_name}", content, dry_run)
            hook_scripts.append(f"scripts/eval/{script_name}")

    # Dashboard directory
    if eval_level in ("full", "basic"):
        write_file(output_dir, "dashboard/events.jsonl", "", dry_run)

    # Plans directory
    write_file(output_dir, "plans/.gitkeep", "", dry_run)

    # Make scripts executable
    for script in hook_scripts:
        make_executable(output_dir, script, dry_run)

    # Summary
    file_count = sum(1 for _ in Path(output_dir).rglob("*") if _.is_file()) if not dry_run else _dry_run_counter[0]
    print(f"\n{'DRY RUN — ' if dry_run else ''}buddyx-forge generated for '{name}':")
    print(f"  Domains: {', '.join(domains)}")
    opt_str = f" + {len(optional_agents)} optional ({', '.join(optional_agents)})" if optional_agents else ""
    print(f"  Agents: {len(domains)} domain + 5 infrastructure{opt_str} = {len(domains) + 5 + len(optional_agents)}")
    print(f"  Skills: orchestrator, rules, diagram, audit")
    print(f"  Hook scripts: {len(hook_scripts)}")
    print(f"  Files created: {file_count}")
    print(f"\n  Next steps:")
    print(f"  1. Run /buddyx-forge:scan to populate domain-map with real file paths")
    print(f"  2. Run /buddyx-forge:health to verify setup")
    print(f"  3. Customize agent files if needed (see references/customize-guide.md)")


# ─── CLI ENTRY POINT ───

def main():
    parser = argparse.ArgumentParser(description="buddyx-forge generator")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--output", required=True, help="Output directory (e.g., .claude/)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    config = load_config(args.config)
    generate(config, args.output, args.dry_run)


if __name__ == "__main__":
    main()
