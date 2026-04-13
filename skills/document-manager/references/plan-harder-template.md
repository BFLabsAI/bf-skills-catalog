# Plan Harder — Sprint/Task Template

## Full Plan Template

```markdown
# Plan: [Task Name]

**Generated**: [Date]
**Estimated Complexity**: [Low/Medium/High]

## Overview
[Summary of task and approach]

## Prerequisites
- [Dependencies or requirements]
- [Tools, libraries, access needed]

## Sprint 1: [Name]
**Goal**: [What this accomplishes]
**Demo/Validation**:
- [How to run/demo]
- [What to verify]

### Task 1.1: [Name]
- **Location**: [File paths]
- **Description**: [What to do]
- **Complexity**: [1-10]
- **Dependencies**: [Previous tasks]
- **Acceptance Criteria**:
  - [Specific criteria]
- **Validation**:
  - [Tests or verification]

### Task 1.2: [Name]
[...]

## Sprint 2: [Name]
[...]

## Testing Strategy
- [How to test]
- [What to verify per sprint]

## Potential Risks & Gotchas
- [What could go wrong]
- [Mitigation strategies]

## Rollback Plan
- [How to undo if needed]
```

## Sprint Requirements

Each sprint must:
- Result in a **demoable, runnable, testable** increment
- Build on prior sprint work
- Include demo/verification checklist

## Task Requirements

Each task must be:
- **Atomic and committable** — small, independent
- Specific with clear inputs/outputs
- Independently testable
- Include file paths when relevant
- Include dependencies for parallel execution
- Include tests or validation method

**Bad:** "Implement Google OAuth"

**Good:**
- "Add Google OAuth config to env variables"
- "Install passport-google-oauth20 package"
- "Create OAuth callback route in src/routes/auth.ts"
- "Add Google sign-in button to login UI"

## Filename Generation

Extract key words → kebab-case → add `-plan.md` suffix.

- "fix xyz bug" → `xyz-bug-plan.md`
- "implement google auth" → `google-auth-plan.md`

## Phase 4: Gotchas (after save)

After saving the plan, identify potential issues and edge cases. Ask:
- Where could something go wrong?
- What in the plan is ambiguous?
- Is there a missing step, dependency, or pitfall?

Use request_user_input again with the saved plan in view. Update plan if improvements found.

## Phase 5: Review

Dispatch a subagent to review the plan file. Provide useful context. Tell it explicitly not to ask questions. Incorporate useful feedback into the plan.
