"""settings.json builder for buddyx-forge generator."""

import json

from .frameworks import FW_COMMANDS


def build_settings_json(config: dict) -> str:
    """Build settings.json programmatically."""
    name = config["projectName"]
    formatter = config.get("techStack", {}).get("formatter", "")
    hooks_config = config.get("hooks", {})
    eval_level = config.get("evalLevel", "none")
    commit_policy = config.get("commitPolicy", "user")
    perm_level = config.get("permissionLevel", "balanced")
    worktree_symlinks = config.get("worktreeSymlinks", [])
    agent_teams = config.get("agentTeams", False)

    # Build permissions
    allow = ["WebSearch"]
    ask = []

    # Framework-aware permission commands
    framework = config.get("techStack", {}).get("framework", "laravel").lower()
    fw = FW_COMMANDS.get(framework, {"allow": [], "ask": []})

    if perm_level == "conservative":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend(["Bash(ls *)", "Bash(find *)"])
        ask.extend(fw.get("allow", []))
        ask.extend(fw.get("ask", []))
    elif perm_level == "balanced":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend([
            "Bash(wc *)", "Bash(ls *)", "Bash(find *)",
            "Bash(sort *)", "Bash(diff *)", "Bash(python3 *)",
        ])
        allow.extend(fw.get("allow", []))
        ask.extend(["Bash(git *)", "Bash(rm *)", "Bash(chmod *)"])
        ask.extend(fw.get("ask", []))
    elif perm_level == "permissive":
        if formatter:
            allow.append(f"Bash({formatter} *)")
        allow.extend([
            "Bash(wc *)", "Bash(ls *)", "Bash(find *)",
            "Bash(sort *)", "Bash(diff *)", "Bash(python3 *)",
            "Bash(xdg-open *)",
        ])
        allow.extend(fw.get("allow", []))
        allow.extend(fw.get("ask", []))
        ask.extend(["Bash(git *)", "Bash(rm *)", "Bash(chmod *)"])

    # Add MCP permissions
    for mcp in config.get("mcpServers", []):
        allow.append(f"mcp__{mcp}__*")

    # Build hooks
    hooks = {}

    if hooks_config.get("contextInjection", False):
        hooks["UserPromptSubmit"] = [{"hooks": [
            {"type": "command", "command": ".claude/scripts/inject-prompt-context.sh"}
        ]}]

    pre_tool_use = []
    if hooks_config.get("blockDangerous", False):
        pre_tool_use.append({
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": ".claude/scripts/safety-guard.sh"}]
        })
    if commit_policy == "user":
        pre_tool_use.append({
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-git-commit.sh"}]
        })
    else:
        # commitPolicy="claude" — add git to allow permissions
        allow.extend(["Bash(git add *)", "Bash(git commit *)", "Bash(git push *)"])
    if hooks_config.get("blockMigration", False):
        pre_tool_use.append({
            "matcher": "Write",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-migration.sh"}]
        })
        pre_tool_use.append({
            "matcher": "Edit",
            "hooks": [{"type": "command", "command": ".claude/scripts/block-migration.sh"}]
        })
    if pre_tool_use:
        hooks["PreToolUse"] = pre_tool_use

    post_tool_use = []
    if hooks_config.get("autoFormat", False) and formatter:
        post_tool_use.append({
            "matcher": "Write",
            "hooks": [{"type": "command", "command": ".claude/scripts/auto-format-new-files.sh"}]
        })
    post_tool_use.append({
        "matcher": "Write",
        "hooks": [{"type": "command", "command": ".claude/scripts/detect-new-file-created.sh"}]
    })
    post_tool_use.append({
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": ".claude/scripts/detect-new-file-created.sh"}]
    })
    if post_tool_use:
        hooks["PostToolUse"] = post_tool_use

    # Eval hooks
    if eval_level in ("full", "basic"):
        hooks["SubagentStart"] = [{"matcher": f"{name}-*", "hooks": [
            {"type": "command", "command": ".claude/scripts/eval/track-agent-start.sh"},
        ]}]
        stop_hooks = [
            {"type": "command", "command": ".claude/scripts/eval/track-session-count.sh"},
        ]
        if eval_level == "full":
            stop_hooks.extend([
                {"type": "command", "command": ".claude/scripts/eval/validate-agent-output.sh"},
                {"type": "command", "command": ".claude/scripts/eval/extract-learnings.sh"},
                {"type": "command", "command": ".claude/scripts/eval/prompt-save-learnings.sh"},
                {"type": "command", "command": ".claude/scripts/eval/auto-promote-learnings.sh"},
            ])
        hooks["SubagentStop"] = [{"matcher": f"{name}-*", "hooks": stop_hooks}]

    # PreCompact
    hooks["PreCompact"] = [{"hooks": [
        {"type": "command", "command": "echo '{\"systemMessage\": \"PRESERVE: current task goal, files changed, agent delegations in progress, any user decisions made this session.\"}'"}
    ]}]

    # Build env
    env = {"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "75"}
    if agent_teams:
        env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"

    settings = {
        "permissions": {"allow": allow, "ask": ask, "deny": []},
        "hooks": hooks,
        "env": env,
        "plansDirectory": ".claude/plans",
        "autoMemoryEnabled": True,
        "buddyxForgeVersion": "1.1.0",
    }

    if worktree_symlinks:
        settings["worktree"] = {"symlinkDirectories": worktree_symlinks}

    return json.dumps(settings, indent=4)
