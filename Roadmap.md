# buddyx-forge Roadmap

Organized by impact. Do the top items first.

---

## Priority 1: Remove Friction — ALL DONE

### 1.1 Add `/buddyx-forge:quick` command
**Status:** Done

### 1.2 GitHub topics and description
**Status:** Done

### 1.3 Create a GitHub release with tag
**Status:** Done (v1.1.1)

---

## Priority 2: Make It Shareable — 3/4 DONE

### 2.1 Add a GIF/video to the README
**Why:** A 30-second recording showing "run command -> answer questions -> 50 files created -> agent working" is worth more than 100 lines of documentation. Use `asciinema` or screen recording.
**Status:** Open
**Effort:** 1-2 hours

### 2.2 Add `/buddyx-forge:export-config` command
**Status:** Done

### 2.3 Write a "What is multi-agent?" section
**Status:** Done

### 2.4 Add use-case stories to README
**Status:** Done

---

## Priority 3: Technical Improvements — ALL DONE

### 3.1 Add `/buddyx-forge:upgrade` command
**Why:** When v1.2 comes, users need a way to update without losing agent-memory and customizations. The version stamp in settings.json enables this.
**Status:** Done

**Effort:** 4-6 hours

### 3.2 Split generate.py into modules
**Why:** At 1,486 lines, it's hard for contributors to navigate.
**Status:** Done
```
scripts/
 generate.py          -> CLI + orchestration (436 lines)
 validators.py        -> load_config + validation (68 lines)
 builders/
   settings.py        -> build_settings_json (149 lines)
   agents.py          -> build_review_agent, build_team_lead_agent (164 lines)
   rules.py           -> build_rules_md, build_claude_md (304 lines)
   orchestrator.py    -> build_orchestrator_skill, build_domain_map (99 lines)
   frameworks.py      -> all framework-specific maps and checklists (367 lines)
```
**Effort:** 4-6 hours

### 3.3 Add `--dry-run` to dream command
**Why:** Dream command modifies memory files. Users want to see what would change before it happens.
**Status:** Done

**Effort:** Small addition to commands/dream.md

### 3.4 Use tempfile for config instead of predictable /tmp path
**Status:** Done
**Effort:** 10 minutes in setup.md

---

## Priority 4: Community Growth

### 4.1 Write a blog post / dev.to article
**Status:** Open
Title ideas:
- "I built a tool that sets up Claude Code multi-agent systems in 2 minutes"
- "How I use 9 AI agents to manage my Laravel project"
- "Stop configuring Claude Code by hand"

### 4.2 Post in relevant communities
**Status:** Open
- Claude Code Discord/community
- r/ClaudeAI on Reddit
- Laravel/Django/Rails community forums
- Dev.to, Hashnode, Medium

### 4.3 Add GitHub issue templates
**Status:** Done

### 4.4 Set up GitHub Actions for CI
**Status:** Done

### 4.5 Translate README to Hindi
**Status:** Open
Large Indian developer community would benefit from Hindi documentation of the "Why?" and "Quick Start" sections.

---

## Quick Reference

| Action | Effort | Impact | Status |
|--------|--------|--------|--------|
| `/buddyx-forge:quick` command | 1 hour | Very high | Done |
| GitHub topics + description | 5 min | High | Done |
| GitHub release tag | 10 min | High | Done (v1.1.1) |
| GIF in README | 1-2 hours | Very high | Open |
| "What is multi-agent?" section | 1 hour | High | Done |
| Use-case stories | 30 min | Medium | Done |
| Export-config for teams | 2-3 hours | High | Done |
| Upgrade command | 4-6 hours | Medium | Done |
| Split generate.py | 4-6 hours | Medium | Done |
| `--dry-run` for dream | 30 min | Low | Done |
| Tempfile for config | 10 min | Low | Done |
| GitHub issue templates | 30 min | Medium | Done |
| GitHub Actions CI | 30 min | Medium | Done |
| Blog post | 3-4 hours | Very high | Open |
| Post in communities | — | High | Open |
| Translate README to Hindi | — | Medium | Open |

