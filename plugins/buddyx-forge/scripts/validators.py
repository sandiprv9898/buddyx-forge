"""Config validation for buddyx-forge generator."""

import json
import re
from pathlib import Path


def load_config(config_path: str) -> dict:
    """Load and validate the config JSON."""
    if not Path(config_path).exists():
        raise ValueError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    # Validate required keys
    required_keys = ["projectName", "domains", "techStack", "hooks", "commitPolicy", "permissionLevel", "modelBudget"]
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    # Validate project name
    name = config.get("projectName", "")
    if not re.match(r'^[a-z][a-z0-9\-]{2,19}$', name):
        raise ValueError(f"Invalid project name: '{name}'. Must be 3-20 chars, lowercase alphanumeric + hyphens.")

    # Validate domains not empty
    if not config.get("domains"):
        raise ValueError("At least one domain is required.")

    # Validate no duplicate domains
    domains = config["domains"]
    if len(domains) != len(set(domains)):
        raise ValueError(f"Duplicate domain names found: {[d for d in domains if domains.count(d) > 1]}")

    # Validate each domain name
    for domain in domains:
        if not re.match(r'^[a-z][a-z0-9\-]{1,30}$', domain):
            raise ValueError(f"Invalid domain name: '{domain}'")

    # Validate framework
    valid_frameworks = {"laravel", "nextjs", "next.js", "react", "django", "go", "rails",
                        "nodejs", "node", "express", "fastify", "nestjs", "hono"}
    fw = config.get("techStack", {}).get("framework", "").lower()
    if fw and fw not in valid_frameworks:
        raise ValueError(f"Unsupported framework: '{fw}'. Supported: {sorted(valid_frameworks)}")

    # Validate formatter command (security)
    formatter = config.get("techStack", {}).get("formatter", "")
    if formatter and not re.match(r'^[a-zA-Z0-9/_\-. ]+$', formatter):
        raise ValueError(f"Invalid formatter command: '{formatter}'")

    # Validate enum fields
    valid_budgets = ("budget", "balanced", "quality")
    if config.get("modelBudget") not in valid_budgets:
        raise ValueError(f"Invalid modelBudget: '{config.get('modelBudget')}'. Must be one of: {valid_budgets}")

    valid_levels = ("conservative", "balanced", "permissive")
    if config.get("permissionLevel") not in valid_levels:
        raise ValueError(f"Invalid permissionLevel: '{config.get('permissionLevel')}'. Must be one of: {valid_levels}")

    valid_policies = ("user", "claude")
    if config.get("commitPolicy") not in valid_policies:
        raise ValueError(f"Invalid commitPolicy: '{config.get('commitPolicy')}'. Must be one of: {valid_policies}")

    valid_eval_levels = ("full", "basic", "none")
    if config.get("evalLevel", "none") not in valid_eval_levels:
        raise ValueError(f"Invalid evalLevel: '{config.get('evalLevel')}'. Must be one of: {valid_eval_levels}")

    # Validate hooks sub-keys
    valid_hook_keys = {"blockCommits", "blockDangerous", "autoFormat", "contextInjection", "agentTracking", "blockMigration"}
    hooks = config.get("hooks", {})
    unknown_hooks = set(hooks.keys()) - valid_hook_keys
    if unknown_hooks:
        raise ValueError(f"Unknown hook keys: {unknown_hooks}. Valid keys: {sorted(valid_hook_keys)}")

    # Validate sharedDb path if provided
    shared_db = config.get("sharedDb", "")
    if shared_db:
        if not re.match(r'^[a-zA-Z0-9/_\-. ]+$', shared_db):
            raise ValueError(f"Invalid sharedDb path: '{shared_db}'. Contains unsafe characters.")
        if '..' in shared_db:
            raise ValueError(f"Invalid sharedDb path: '{shared_db}'. Path traversal (..) not allowed.")

    return config
