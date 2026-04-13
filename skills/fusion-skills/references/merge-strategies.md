# Merge Strategies Reference

Guidance for deciding how to merge skills and how to write the result.

---

## Decision Framework

Use this order every time: `DO-NOT-MERGE` gate -> `MERGE` score -> `KEEP SEPARATE` fallback.

### 1) DO-NOT-MERGE Gate (hard stop)

Do not merge when any of these are true:
- Safety/regulatory boundaries differ (for example: prod ops vs local experimentation)
- Lifecycle boundaries differ (for example: migration runbook vs day-to-day coding assistant)
- User intent boundaries differ and would make one description too broad to target reliably
- One skill is still unstable or untrusted and should not contaminate a stable skill

If one skill is obsolete or fully superseded, **exclude it** instead of merging:
- Fully redundant with better coverage elsewhere
- References deprecated APIs/patterns with no current value
- Trivial body with no unique references or rules

### 2) MERGE Score (weighted rubric)

Score each pair and merge when total is `>= 7`:
- Trigger phrase overlap: `0-3`
- Topic/domain overlap from matrix: `0-3`
- Rule/invariant overlap: `0-2`
- Reference overlap or duplication: `0-2`
- Audience overlap: `0-1`

Hard constraints:
- If trigger overlap is `0`, do not merge.
- If topic overlap is `< 20%`, do not merge unless one skill is a strict subset.

Target outcome:
- Merged skill should be smaller than the sum of sources.
- If size grows without removing duplication, it is concatenation, not merge.

### 3) KEEP SEPARATE (default when uncertain)

Keep separate when:
- The pair fails the merge score threshold
- They solve adjacent but different intents (for example: performance tuning vs security hardening)
- Merging would force vague "catch-all" description text

If uncertain after scoring, keep separate and document why in one sentence.

---

## Writing the Merged Skill

### Merged description rules

The description is the most important part. It must:
1. **Be the union, not the intersection** — cover all trigger phrases from all merged skills
2. **Stay under ~3 sentences** — too long and the agent doesn't read it fully
3. **Name all key topics** explicitly so the triggering system finds it

Bad (intersection — too narrow):
> Use for Supabase database operations and performance optimization.

Good (union — covers all original triggers):
> Supabase expert covering authentication, database design, RLS policies, Edge Functions, Realtime,
> Storage, and query performance optimization. Use for any Supabase task, schema design, connection
> pooling, indexing strategy, or security audit.

### Body structure rules

**Topic-first, not source-first.** Group by what the content is about, not where it came from.

Template:
```markdown
# <Merged Name>

<2-3 line intro explaining the merged scope>

## <Domain A>
<Unified content>

## <Domain B>
<Unified content>

## Rules and Invariants
<All hard rules from all source skills — deduped>

## When to use
<Union of all trigger cases>
```

### Handling conflicts

Use this explicit process for every detected conflict:

1. **Classify conflict type**
- Rule conflict (opposite instructions)
- Scope conflict (same rule, different boundary)
- Freshness conflict (deprecated vs current)
- Terminology conflict (different words for same concept)

2. **Resolve with ordered precedence**
- Safety/compliance rule wins first
- More specific rule wins over general rule
- Newer supported API/pattern wins over deprecated guidance
- If both remain valid, convert to conditional guidance (`use X when Y; use Z when W`)

3. **Record every resolution**

Do not silently drop a rule. Add a short decision note in merged `## Notes`:

```markdown
- Conflict: <rule-a> vs <rule-b>
- Decision: <chosen rule or conditional>
- Why: <specificity | safety | recency | scope>
```

4. **Escalate unresolved conflicts**

If no safe resolution exists, keep skills separate and mark the pair as `do-not-merge`.

---

## Reference Merging

### Same topic, different files

If `skill-a/references/checkout.md` and `skill-b/references/payment-intents.md` cover the
same topic (detected as duplicates by the pre-processor):

1. Read both files
2. Write a single combined file: `references/checkout-and-payment-intents.md`
3. Remove duplication in the body, keep unique content from each
4. Add a header noting the sources

### Same file name, different content

If both skills have `references/security.md` but they cover different aspects:

1. Keep both as `references/security-<skill-a-name>.md` and `references/security-<skill-b-name>.md`
2. OR merge them into `references/security.md` if they're complementary

### Unrelated references

If a reference from skill-a has no overlap with anything in skill-b, copy it as-is.
Don't modify references that don't need merging.

---

## Symlink Management

After merge, the skill must be reachable from both agent paths:

```
~/.claude/skills/<merged-name>   →  <absolute path to merged skill dir>
~/.agents/skills/<merged-name>   →  <absolute path to merged skill dir>
```

For deleted skills:
```
~/.claude/skills/<old-name>   →  REMOVE (dangling)
~/.agents/skills/<old-name>   →  REMOVE (dangling)
```

Check for symlinks using:
```bash
ls -la ~/.claude/skills/
ls -la ~/.agents/skills/
```

Create symlinks:
```bash
ln -sfn /absolute/path/to/merged-skill ~/.claude/skills/<merged-name>
ln -sfn /absolute/path/to/merged-skill ~/.agents/skills/<merged-name>
```

Remove dangling symlinks:
```bash
rm ~/.claude/skills/<old-name>   # if it was a symlink to the deleted dir
```

---

## Token Budget Guidance

A good skill body should be **under 400 lines / ~6,000 tokens**.

After merging, if the result is over this limit:
- Trim examples that duplicate the point of other examples
- Move detailed reference content to `references/` rather than the body
- Use section headers + short summaries in the body, full content in references

The goal is: the body tells Claude *what* to do and *when*, references tell Claude *how*.
