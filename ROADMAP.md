# buddyx-forge Roadmap

Organized by impact. Do the top items first.

---

## Priority 1: Remove Friction (This Week)

### 1.1 Add `/buddyx-forge:quick` command
**Why:** 10 questions before seeing value kills adoption. A zero-question command that auto-detects everything and uses recommended defaults lets someone try it in 30 seconds.
**Status:** Done

### 1.2 GitHub topics and description
**Why:** Repo has no description or topics. GitHub search relies on these.
- Description: "Generate a complete multi-agent system for Claude Code"
- Topics: claude-code, multi-agent, scaffolding, developer-tools, laravel, nextjs, django, rails, golang, ai-agents

**Effort:** 5 minutes

### 1.3 Create a GitHub release with tag
**Why:** No releases published. Tagged releases show up in GitHub's feed and signal maturity.
```bash
git tag v1.1.0 && git push --tags
```
**Effort:** 10 minutes

---

## Priority 2: Make It Shareable (This Month)

### 2.1 Add a GIF/video to the README
**Why:** A 30-second recording showing "run command -> answer questions -> 50 files created -> agent working" is worth more than 100 lines of documentation. Use `asciinema` or screen recording.

**Effort:** 1-2 hours

### 2.2 Add `/buddyx-forge:export-config` command
**Why:** Teams need standardization. One developer sets up, exports config, everyone else imports it.
```
/buddyx-forge:export-config -> .buddyx-forge.json (add to git)
# Teammate runs:
/buddyx-forge:quick --config .buddyx-forge.json
```
**Effort:** 2-3 hours

### 2.3 Write a "What is multi-agent?" section
**Why:** Most Claude Code users don't know what agents are. Explain in simple terms:
- What agents are (specialized AI assistants for different parts of your code)
- Why multiple agents beat one (each knows its area deeply)
- What an orchestrator does (routes your request to the right agent)
- What memory/learnings do (agents get better over time)

**Effort:** 1 hour

### 2.4 Add use-case stories to README
Show real scenarios like "Fix a bug" and "Audit before deploy" with step-by-step what happens behind the scenes.

**Effort:** 30 minutes

---

## Priority 3: Technical Improvements (Before v1.2)

### 3.1 Add `/buddyx-forge:upgrade` command
**Why:** When v1.2 comes, users need a way to update without losing agent-memory and customizations. The version stamp in settings.json enables this.

**Effort:** 4-6 hours

### 3.2 Split generate.py into modules
**Why:** At 1,486 lines, it's hard for contributors to navigate.
```
scripts/
  generate.py          -> CLI + orchestration (~100 lines)
  validators.py        -> load_config + validation
  builders/
    settings.py        -> build_settings_json
    agents.py          -> build_review_agent, build_team_lead_agent
    rules.py           -> build_rules_md, build_claude_md
    orchestrator.py    -> build_orchestrator_skill, build_domain_map
    frameworks.py      -> all framework-specific maps and checklists
```
**Effort:** 4-6 hours

### 3.3 Add `--dry-run` to dream command
**Why:** Dream command modifies memory files. Users want to see what would change before it happens.

**Effort:** Small addition to commands/dream.md

### 3.4 Use tempfile for config instead of predictable /tmp path
**Effort:** 10 minutes in setup.md

---

## Priority 4: Community Growth

### 4.1 Write a blog post / dev.to article
Title ideas:
- "I built a tool that sets up Claude Code multi-agent systems in 2 minutes"
- "How I use 9 AI agents to manage my Laravel project"
- "Stop configuring Claude Code by hand"

### 4.2 Post in relevant communities
- Claude Code Discord/community
- r/ClaudeAI on Reddit
- Laravel/Django/Rails community forums
- Dev.to, Hashnode, Medium

### 4.3 Add GitHub issue templates
Create `.github/ISSUE_TEMPLATE/` with bug_report.md, framework_request.md, feature_request.md.

### 4.4 Set up GitHub Actions for CI
Run `python3 tests/test_generator.py` on every PR. Shows a green badge in README.

### 4.5 Translate README to Hindi
Large Indian developer community would benefit from Hindi documentation of the "Why?" and "Quick Start" sections.

---

## Quick Reference

| Action | Effort | Impact | When |
|--------|--------|--------|------|
| `/buddyx-forge:quick` command | 1 hour | Very high | Done |
| GitHub topics + description | 5 min | High | Today |
| GitHub release tag | 10 min | High | Today |
| GIF in README | 1-2 hours | Very high | This week |
| "What is multi-agent?" section | 1 hour | High | This week |
| Use-case stories | 30 min | Medium | This week |
| Export-config for teams | 2-3 hours | High | This month |
| Upgrade command | 4-6 hours | Medium | Before v1.2 |
| Split generate.py | 4-6 hours | Medium | Before v1.2 |
| Blog post | 3-4 hours | Very high | When GIF + quick are done |
