# Writing Plans — Full Guide

## Plan Document Header (Mandatory)

Every plan MUST start with this header:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure Template

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## File Structure Mapping

Before defining tasks, map out all files:
- Design units with clear boundaries and single responsibility.
- Files that change together should live together.
- Follow existing patterns in the codebase.
- If a file has grown unwieldy, a split is reasonable — but don't unilaterally restructure source files.

## Bite-Sized Step Granularity

Each step is one action (2–5 minutes):
- "Write the failing test" — one step
- "Run it to make sure it fails" — one step
- "Implement the minimal code to make the test pass" — one step
- "Run the tests and make sure they pass" — one step
- "Commit" — one step

## No Placeholders — Hard Rules

These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — engineer may read tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Self-Review Checklist (run after writing complete plan)

**1. Spec coverage:** Skim each requirement. Can you point to a task that implements it? List gaps.

**2. Placeholder scan:** Search for red flag patterns listed above. Fix them.

**3. Type consistency:** Do types, method signatures, and property names in later tasks match earlier tasks? Inconsistency is a bug.

Fix issues inline. If a spec requirement has no task, add the task.

## Plan Document Reviewer Prompt

Use this when dispatching a subagent to review a completed plan:

```
You are a plan document reviewer. Verify this plan is complete and ready for implementation.

**Plan to review:** [PLAN_FILE_PATH]
**Spec for reference:** [SPEC_FILE_PATH]

## What to Check

| Category | What to Look For |
|----------|------------------|
| Completeness | TODOs, placeholders, incomplete tasks, missing steps |
| Spec Alignment | Plan covers spec requirements, no major scope creep |
| Task Decomposition | Tasks have clear boundaries, steps are actionable |
| Buildability | Could an engineer follow this plan without getting stuck? |

## Calibration

Only flag issues that would cause real problems during implementation.
Approve unless there are serious gaps — missing requirements, contradictory steps,
placeholder content, or tasks so vague they can't be acted on.

## Output Format

## Plan Review

**Status:** Approved | Issues Found

**Issues (if any):**
- [Task X, Step Y]: [specific issue] - [why it matters for implementation]

**Recommendations (advisory, do not block approval):**
- [suggestions for improvement]
```

## Scope Check

If the spec covers multiple independent subsystems, suggest breaking into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Execution Handoff

After saving, offer two execution options:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration.
Use superpowers:subagent-driven-development

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.
Use superpowers:executing-plans

**Which approach?"**
