# Example Generated Output

These directories show what `buddyx-forge` generates for real projects. Browse them to see the agents, hooks, skills, and configuration before installing the plugin.

## Laravel Example (`laravel-example/`)

- **3 domains:** billing, auth, users
- **9 agents:** 3 domain + 5 infrastructure + query-optimizer
- **11 hook scripts** with safety guards and eval tracking
- **50 files** total

## Django Example (`django-example/`)

- **2 domains:** api, dashboard
- **8 agents:** 2 domain + 5 infrastructure + query-optimizer
- **11 hook scripts** with safety guards and eval tracking
- **47 files** total

## How these were generated

```bash
python3 plugins/buddyx-forge/scripts/generate.py \
  --config laravel-config.json \
  --output examples/laravel-example
```

See `buddyx-forge.example.json` in the repo root for a complete config file you can customize.
