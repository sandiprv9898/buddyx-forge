# buddyx-forge

Generate a complete multi-agent development system for any Laravel project.

## Install

```
/plugin marketplace add sandip-vanodiya/buddyx-forge
/plugin install buddyx-forge
```

## Usage

```
/buddyx-forge
```

Follow the interactive setup (10 questions). Creates:
- Domain-specific agents with file ownership
- Safety hook scripts (block commits, dangerous commands)
- Shared memory + self-improving learning system
- Code review gate agent
- Module audit + diagram generation skills
- Prompt templates in CLAUDE.md

## Requirements

- Python 3.8+
- jq (recommended, not required)
- Laravel 11 project (Filament 3 optional)

## Commands

| Command | Purpose |
|---------|---------|
| `/buddyx-forge` | First-time setup |
| `/buddyx-forge --dry-run` | Preview without creating files |
| `/buddyx-forge:scan` | Re-scan codebase, update context |
| `/buddyx-forge:add-domain X` | Add a new domain agent |
| `/buddyx-forge:health` | Validate setup integrity (0-100 score) |

## License

MIT
