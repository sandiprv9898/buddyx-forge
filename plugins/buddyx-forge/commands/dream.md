---
name: dream
description: Memory consolidation — clean stale entries, merge duplicates, promote hypotheses, trim oversized files. Combines Anthropic Auto-Dream with buddyx-forge memory cleanup.
---

# /buddyx-forge:dream

Memory consolidation for the agent system. Like sleep for your agents.

## Flags

- `--dry-run` — show what would be cleaned without making changes. Report all actions as "WOULD trim", "WOULD remove", etc.

## Process

### Step 0: Check for --dry-run

Parse the user's command for `--dry-run` flag. If present, set `DRY_RUN=true`. In dry-run mode:
- Perform all analysis (count lines, find stale entries)
- Report what WOULD change (with "WOULD" prefix)
- Do NOT modify any files

### Step 1: Detect Project

Read any agent in `.claude/agents/` to get the project name prefix.

### Step 2: Check Native Auto-Dream

Check if Anthropic's native Auto-Dream is available:
```bash
claude --help 2>&1 | grep -i "dream"
```

If available: "Native Auto-Dream detected. Running Anthropic's /dream first, then buddyx-forge cleanup."
If not: "Native Auto-Dream not available. Running buddyx-forge memory cleanup."

### Step 3: Agent Memory Cleanup

For each `.claude/agent-memory/{agent}/MEMORY.md`:

1. Count lines: `wc -l`
2. If over 180 lines:
   - Keep first 20 lines (headers + section names)
   - Keep last 150 lines (recent sessions)
   - Remove middle (oldest entries)
3. Report: "{agent}: trimmed from {old} to {new} lines" or "{agent}: OK ({lines} lines)"

### Step 4: Shared Learnings Cleanup

Read `.claude/agent-memory/shared-learnings.md`:

1. Find entries with `[NEW 0/3]` that are older than 90 days
   - Pattern: `[NEW 0/3] [YYYY-MM-DD]` where date is > 90 days ago
   - Remove these entries (never confirmed = stale)
2. Keep ALL `[CONFIRMED]` entries regardless of age
3. Keep `[NEW 1/3]`, `[NEW 2/3]` entries (in progress)
4. Report: "Removed {count} stale hypotheses"

### Step 5: Learning Queue Cleanup

Read `.claude/agent-memory/learning-queue.md`:

1. Count lines
2. If over 100 lines: trim to last 80 entries (keep header)
3. Report: "Learning queue: trimmed" or "Learning queue: OK"

### Step 6: Events Log Rotation

Read `.claude/dashboard/events.jsonl` (if exists):

1. Count lines
2. If over 1000 lines: keep last 500 entries
3. Report: "Events log: rotated" or "Events log: OK"

### Step 7: Report

```
buddyx-forge dream {DRY RUN — no changes made | complete}:

Agent Memories:
  {agent1}: OK (45 lines)
  {agent2}: trimmed 210 → 170 lines
  ...

Shared Learnings:
  Stale hypotheses removed: {count}
  Confirmed rules kept: {count}
  Active hypotheses: {count}

Learning Queue: {trimmed/OK} ({lines} lines)
Events Log: {rotated/OK} ({lines} lines)

Total cleaned: {bytes_freed} bytes freed
```
