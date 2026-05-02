---
name: fusion-skills
description: >
  Merge two or more Claude Code skills into a single, leaner skill. Use when you
  want to consolidate overlapping skills, reduce redundancy in your skill set, or
  combine related skills that share triggers, topics, or rules. Runs a pre-processor
  to compute overlap scores, detect rule conflicts, and flag duplicate references
  before writing the merged output. Also use when asked to "fuse", "combine",
  "merge", or "consolidate" skills.
version: "1.0.0"
tags:
  - skills
  - merge
  - fusion
  - consolidation
  - optimization
---

# Fusion Skills

Merges two or more Claude Code skills into a single, deduplicated skill.
Uses a structured decision framework and a Python pre-processor to detect overlap,
score merge candidates, surface rule conflicts, and flag duplicate reference files
before writing the final merged output.

## When to Use This Skill

- Consolidating overlapping or redundant skills
- Combining skills that share triggers, topics, or rules
- Shrinking a large skill set without losing coverage
- Resolving duplicate reference files across skills
- Any request to "fuse", "combine", "merge", or "consolidate" skills

---

## Workflow

### Step 1 — Run the pre-processor

Run `scripts/prepare_fusion.py` with the skill directories as arguments:

```bash
python scripts/prepare_fusion.py <skill1_path> <skill2_path> [skill3_path ...]
```

This writes `_fusion_context.md` in the current directory. Read it before proceeding.
It contains:
- Pairwise topic-overlap matrix (Jaccard similarity)
- Rule conflict warnings
- Reference inventory with cross-skill duplicate detection
- Token estimates per skill

### Step 2 — Apply the merge decision framework

Read `references/merge-strategies.md` and apply the decision framework in order:

1. **DO-NOT-MERGE gate** — hard stop if safety/regulatory boundaries differ, lifecycle boundaries differ, or intent would become too broad.
2. **MERGE score** — score each pair (trigger overlap 0–3, topic overlap 0–3, rule overlap 0–2, reference overlap 0–2, audience overlap 0–1). Merge when total ≥ 7.
3. **KEEP SEPARATE fallback** — when uncertain, keep separate and document why.

### Step 3 — Write the merged SKILL.md

- Description must be the **union**, not the intersection, of all trigger phrases.
- Group body by **topic**, not by source skill.
- Deduplicate all rules and references.
- Resolve every detected conflict using the ordered precedence in `references/merge-strategies.md`.
- Record conflict resolutions in a `## Notes` section.

### Step 4 — Merge reference files

- Same topic, different files → write one combined file.
- Same filename, different content → keep as `<name>-<skill>.md` or merge if complementary.
- Unrelated references → copy as-is.

### Step 5 — Update symlinks

After installing the merged skill, update symlinks so it is reachable from all agent paths:

```bash
ln -sfn /absolute/path/to/merged-skill ~/.claude/skills/<merged-name>
ln -sfn /absolute/path/to/merged-skill ~/.agents/skills/<merged-name>
```

Remove any dangling symlinks for deleted skills:

```bash
rm ~/.claude/skills/<old-name>
rm ~/.agents/skills/<old-name>
```

---

## Quality Rules

- Merged skill must be **smaller** than the sum of sources. If it grows, you are concatenating, not merging.
- Body should stay under **400 lines / ~6 000 tokens**. Move detail to `references/` if needed.
- Do **not** silently drop rules. Every conflict resolution must be documented.
- If no safe resolution exists, keep skills separate and mark the pair `do-not-merge`.
