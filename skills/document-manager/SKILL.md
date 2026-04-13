---
name: document-manager
description: >
  Full-spectrum document and planning manager. Use for organizing files and folders (clean up Downloads, find duplicates, restructure directories), writing technical documentation with the Diátaxis framework (tutorials, how-to guides, reference, explanation), creating and executing implementation plans (phased sprints, atomic tasks, TDD-style step-by-step plans), designing architecture decisions (ADR creation, trade-off analysis, technology comparison), auditing and improving CLAUDE.md files across repositories, and CLAUDE.md maintenance or project memory optimization. Also triggers on: "plan harder", implement a plan, write a plan, create implementation plan, organize my files, document this, architecture decision, ADR.
tools: Read, Glob, Grep, Bash, Edit
---

# Document Manager

Unified skill for the full lifecycle of documents, plans, and knowledge artifacts: file organization, technical writing, implementation planning, architecture decisions, and CLAUDE.md quality management.

---

## Domain 1: File Organization

Intelligently organizes files and folders by understanding context, finding duplicates, suggesting structures, and automating cleanup.

**Use when:** Downloads folder is chaotic, files are scattered, duplicates waste space, folder structure needs restructuring, starting/archiving a project.

### Workflow

1. **Scope check** — Ask: which directory, main problem, files to avoid, aggressiveness level.
2. **Analyze** — Survey file types, sizes, counts, and date ranges.
3. **Propose plan** — Present proposed folder structure and move list. Await approval.
4. **Execute** — Create folders, move/rename files with logging. Always confirm before deleting.
5. **Summary** — Report changes, provide maintenance schedule.

**Rules:**
- Always confirm before deleting anything.
- Preserve original modification dates.
- Handle filename conflicts gracefully.
- Stop and ask on unexpected situations.

For detailed bash commands, organization patterns, and naming conventions, see [references/file-organization.md](references/file-organization.md).

---

## Domain 2: Technical Documentation (Diátaxis)

Expert technical writer guided by the Diátaxis framework. Creates tutorials, how-to guides, reference docs, and explanations.

**Use when:** Writing software docs, creating API references, drafting tutorials, or structuring explanation content.

### Diátaxis Document Types

| Type | Purpose | Analogy |
|------|---------|---------|
| Tutorial | Learning-oriented, practical steps for newcomers | A lesson |
| How-to Guide | Problem-oriented, steps to solve a specific problem | A recipe |
| Reference | Information-oriented, technical description of machinery | A dictionary |
| Explanation | Understanding-oriented, clarifying a topic | A discussion |

### Workflow

1. **Clarify** — Determine document type, target audience, user's goal, and scope.
2. **Propose structure** — Outline with section descriptions. Await approval.
3. **Generate** — Write full Markdown content adhering to: Clarity, Accuracy, User-Centricity, Consistency.

**Rules:**
- Use context from provided Markdown files for tone/style, but do not copy content unless asked.
- No external sources unless explicitly provided.

---

## Domain 3: Implementation Planning

Three complementary planning modes — choose based on the request:

### Mode A: Plan Harder (Phased Sprint Planning)
**Trigger:** User says "plan harder"

Creates detailed phased plans with sprints and atomic tasks. Process:
1. Research codebase — architecture, patterns, dependencies.
2. Clarify requirements — ask up to 10 targeted questions.
3. Create plan — Sprints → Tasks → Gotchas → Review.
4. Save as `[name]-plan.md`, then review with a subagent.

Each sprint must produce a demoable, runnable, testable increment. Each task must be atomic, committable, and independently testable.

See [references/plan-harder-template.md](references/plan-harder-template.md) for the full sprint/task template.

### Mode B: Writing Plans (TDD Step-by-Step)
**Trigger:** Have a spec or requirements for a multi-step task, before touching code.

Announces: "I'm using the writing-plans skill to create the implementation plan."

- Map file structure before decomposing tasks.
- Each step is one action (2–5 min): write failing test → run it → implement → verify → commit.
- No placeholders. Every step has actual code, exact paths, exact commands with expected output.
- Save to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` (or user-specified location).
- After saving, offer two execution options: Subagent-Driven (recommended) or Inline Execution.

See [references/writing-plans-guide.md](references/writing-plans-guide.md) for plan header template, task structure, and self-review checklist.

### Mode C: Create Implementation Plan (AI-Optimized Format)
**Trigger:** Create implementation plan for feature/refactor/upgrade/architecture/infrastructure.

Produces machine-readable, deterministic plans for autonomous AI or human execution.

- Plans saved to `/plan/` with naming `[purpose]-[component]-[version].md`.
- Purpose prefixes: `upgrade|refactor|feature|data|infrastructure|process|architecture|design`.
- Front matter includes: goal, version, date, owner, status (with badge), tags.
- Structured with phases, TASK-NNN identifiers, completion criteria, and parallel-safe task grouping.

See [references/implementation-plan-template.md](references/implementation-plan-template.md) for the full mandatory template.

### Executing Plans
**Trigger:** Have a written implementation plan to execute.

Announces: "I'm using the executing-plans skill to implement this plan."

Process:
1. Load and review plan critically — raise concerns before starting.
2. Execute each task: mark in_progress → follow steps exactly → run verifications → mark complete.
3. **Stop immediately** when: blocker hit, instruction unclear, verification fails. Ask for clarification — never guess.
4. On completion, transition to finishing-a-development-branch workflow.

**Rule:** Never start implementation on main/master branch without explicit user consent.

---

## Domain 4: Architecture Decisions (ADR)

Create or evaluate Architecture Decision Records. Use when choosing technologies, documenting design decisions, reviewing system proposals, or designing new components.

**Use when:** "Should we use X or Y?", "Review this design", "Design the notification system", "Document why we chose X".

### ADR Output Format

```markdown
# ADR-[number]: [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** [Date]
**Deciders:** [Who needs to sign off]

## Context
## Decision
## Options Considered
  (table: Complexity, Cost, Scalability, Team familiarity | Pros | Cons)
## Trade-off Analysis
## Consequences
## Action Items
```

**Tips:**
- State constraints upfront (timeline, scale requirements).
- Name all options explicitly, even if leaning one way.
- Include non-functional requirements: latency, cost, team expertise, maintenance burden.

---

## Domain 5: CLAUDE.md Quality Management

Audit, evaluate, and improve CLAUDE.md files across a repository to ensure Claude Code has optimal project context.

**Trigger phrases:** Check/audit/update/improve/fix CLAUDE.md, CLAUDE.md maintenance, project memory optimization.

### Workflow

1. **Discover** — Find all CLAUDE.md files: `find . -name "CLAUDE.md" -o -name ".claude.md" -o -name ".claude.local.md"`.
2. **Assess** — Score each file against 6 criteria (see [references/claude-md-quality-criteria.md](references/claude-md-quality-criteria.md)).
3. **Report** — Output quality report BEFORE making any changes. Grades: A(90-100), B(70-89), C(50-69), D(30-49), F(0-29).
4. **Confirm** — Ask for user approval before updating.
5. **Update** — Apply targeted additions using Edit tool. Preserve structure.

### Quality Criteria Summary

| Criterion | Weight |
|-----------|--------|
| Commands/Workflows documented | 20pts |
| Architecture clarity | 20pts |
| Non-obvious patterns/gotchas | 15pts |
| Conciseness | 15pts |
| Currency (reflects current state) | 15pts |
| Actionability (copy-paste ready) | 15pts |

### Key Principles

- **What TO add:** Commands discovered, gotchas/non-obvious patterns, package relationships, testing approaches that work, config quirks.
- **What NOT to add:** Obvious code info, generic best practices, one-off fixes, verbose explanations.
- Use `#` shortcut during sessions for Claude to auto-incorporate learnings.
- Personal/local preferences go in `.claude.local.md` (gitignored).
- User-wide defaults go in `~/.claude/CLAUDE.md`.

See [references/claude-md-templates.md](references/claude-md-templates.md) and [references/claude-md-update-guidelines.md](references/claude-md-update-guidelines.md) for templates and detailed update guidance.

---

## Rules and Invariants

- **File operations:** Always confirm before deleting. Log all moves. Stop on unexpected situations.
- **Plans:** Never start implementation on main/master without explicit user consent. Stop when blocked — never guess.
- **Documentation:** Determine document type before writing. Propose structure before generating content.
- **Plans — no placeholders:** TDD-style plans must contain actual code, exact paths, exact commands. Never write "TBD", "TODO", "implement later", "similar to Task N".
- **CLAUDE.md:** Always output quality report before making changes. Get user approval before any edits.
- **Conflict resolution:** File cleanup ("reduces clutter") applies to personal workspace files. Writing-plans code file advice ("don't unilaterally restructure") applies to codebase source files — no conflict.

## When to Use

| Request | Mode |
|---------|------|
| "Organize my Downloads / find duplicates / clean up folders" | Domain 1: File Organization |
| "Write documentation / tutorial / how-to / reference" | Domain 2: Diátaxis Documentation |
| "Plan harder" | Domain 3A: Phased Sprint Planning |
| "Write a plan for this spec" | Domain 3B: TDD Step-by-Step Plans |
| "Create implementation plan for feature/refactor/upgrade" | Domain 3C: AI-Optimized Plan |
| "Execute this plan / implement the plan" | Domain 3: Executing Plans |
| "Architecture decision / ADR / should we use X or Y" | Domain 4: Architecture Decisions |
| "Check/audit/improve CLAUDE.md / project memory" | Domain 5: CLAUDE.md Quality |
