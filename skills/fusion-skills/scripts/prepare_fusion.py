#!/usr/bin/env python3
"""
prepare_fusion.py — Fusion Skills Pre-processor

Reads two or more skill directories, parses their SKILL.md files and all
reference documents, then writes a single _fusion_context.md file that
Claude reads before performing the fusion analysis.

Also computes:
  - Pairwise topic overlap matrix (Jaccard similarity)
  - Conflict warnings (contradictory rule pairs)
  - Reference inventory with cross-skill duplicate detection
  - Token estimates per skill

Usage:
    python prepare_fusion.py <skill1_path> <skill2_path> [skill3_path ...]

Output:
    ./_fusion_context.md   (always written in cwd)
"""

import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# SKILL.md parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[str, str, dict]:
    """Parse YAML frontmatter from a SKILL.md string.

    Returns (name, description, extra_fields).
    Handles multiline YAML values (>, |, >-, |-).
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return "", "", {}

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return "", "", {}

    name = ""
    description = ""
    extra: dict = {}
    frontmatter_lines = lines[1:end_idx]
    i = 0

    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]

        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")

        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                parts: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ")
                    or frontmatter_lines[i].startswith("\t")
                ):
                    parts.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(parts)
                continue
            else:
                description = value.strip('"').strip("'")

        elif ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            extra[key.strip()] = val.strip().strip('"').strip("'")

        i += 1

    return name, description, extra


def load_skill(skill_path: Path) -> dict:
    """Load a skill directory into a dict with all its content."""
    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        raise FileNotFoundError(f"No SKILL.md found in {skill_path}")

    raw = skill_md_path.read_text(encoding="utf-8")
    name, description, extra = parse_frontmatter(raw)

    # Body is everything after the closing ---
    body_lines = raw.split("\n")
    close_idx = None
    for i, line in enumerate(body_lines[1:], start=1):
        if line.strip() == "---":
            close_idx = i
            break
    body = "\n".join(body_lines[close_idx + 1:]).strip() if close_idx else raw

    # Load reference files
    references: dict[str, str] = {}
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.rglob("*.md")):
            rel = ref_file.relative_to(skill_path)
            references[str(rel)] = ref_file.read_text(encoding="utf-8")

    # Other notable directories
    has_scripts = (skill_path / "scripts").exists()
    has_data = (skill_path / "data").exists()
    has_assets = (skill_path / "assets").exists()

    return {
        "path": skill_path,
        "name": name or skill_path.name,
        "description": description,
        "extra": extra,
        "body": body,
        "raw_skill_md": raw,
        "references": references,
        "has_scripts": has_scripts,
        "has_data": has_data,
        "has_assets": has_assets,
    }


# ---------------------------------------------------------------------------
# Topic extraction
# ---------------------------------------------------------------------------

# Common English stopwords to exclude from topic analysis
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "do", "does", "will", "would", "could", "should", "may",
    "might", "must", "can", "this", "that", "these", "those", "it", "its",
    "if", "as", "so", "then", "when", "where", "how", "what", "which",
    "all", "any", "each", "every", "both", "not", "no", "nor", "only",
    "own", "same", "than", "too", "very", "just", "about", "after",
    "before", "between", "into", "through", "during", "above", "below",
    "up", "down", "out", "off", "over", "under", "again", "further",
    "there", "here", "once", "use", "used", "using", "your", "you",
    "we", "our", "they", "their", "them", "he", "she", "his", "her",
    "also", "more", "most", "other", "such", "like", "well", "even",
    "make", "made", "get", "set", "run", "add", "new", "see", "need",
    "however", "always", "never", "ensure", "avoid", "note", "example",
    "include", "following", "step", "steps", "section", "sections",
    "please", "first", "second", "third", "e", "g", "i", "ie",
}


def extract_topics(text: str, top_n: int = 60) -> set[str]:
    """Extract meaningful topic keywords from text (no external deps)."""
    # Lowercase, split on non-alphanumeric
    tokens = re.findall(r"[a-z][a-z0-9_\-]{2,}", text.lower())
    # Remove stopwords and very short tokens
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    # Count frequencies
    freq = Counter(tokens)
    # Return top N by frequency
    return {word for word, _ in freq.most_common(top_n)}


def jaccard(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def full_text(skill: dict) -> str:
    """Concatenate all text in a skill (body + all references)."""
    parts = [skill["description"], skill["body"]]
    parts.extend(skill["references"].values())
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

# Pairs of words that often appear in contradictory rules
OPPOSITION_PAIRS = [
    ("always", "never"),
    ("must", "avoid"),
    ("require", "avoid"),
    ("use", "avoid"),
    ("prefer", "avoid"),
    ("recommended", "discouraged"),
    ("do", "don't"),
    ("enable", "disable"),
    ("include", "exclude"),
    ("sync", "async"),
    ("global", "local"),
    ("mutable", "immutable"),
]


def extract_rule_sentences(text: str) -> list[str]:
    """Extract sentences that look like rules (contain directive words)."""
    directive_words = {
        "always", "never", "must", "should", "avoid", "don't", "do not",
        "require", "ensure", "never use", "always use", "prefer", "use only",
    }
    sentences = re.split(r'[.!?\n]', text)
    rules = []
    for s in sentences:
        s = s.strip()
        if len(s) < 15 or len(s) > 300:
            continue
        s_lower = s.lower()
        if any(dw in s_lower for dw in directive_words):
            rules.append(s)
    return rules


def detect_conflicts(skills: list[dict]) -> list[str]:
    """Find likely contradictions between rules across skills."""
    warnings = []

    # Extract rules per skill
    skill_rules: list[tuple[str, list[str]]] = []
    for skill in skills:
        text = full_text(skill)
        rules = extract_rule_sentences(text)
        skill_rules.append((skill["name"], rules))

    # Compare each pair of skills
    for i in range(len(skill_rules)):
        for j in range(i + 1, len(skill_rules)):
            name_a, rules_a = skill_rules[i]
            name_b, rules_b = skill_rules[j]

            for rule_a in rules_a:
                for rule_b in rules_b:
                    # Check for opposition: same subject, opposite directive
                    for pos_word, neg_word in OPPOSITION_PAIRS:
                        a_has_pos = pos_word in rule_a.lower()
                        b_has_neg = neg_word in rule_b.lower()
                        a_has_neg = neg_word in rule_a.lower()
                        b_has_pos = pos_word in rule_b.lower()

                        if (a_has_pos and b_has_neg) or (a_has_neg and b_has_pos):
                            # Check they share a common subject keyword (rough heuristic)
                            words_a = set(re.findall(r"[a-z]{3,}", rule_a.lower())) - STOPWORDS
                            words_b = set(re.findall(r"[a-z]{3,}", rule_b.lower())) - STOPWORDS
                            shared = words_a & words_b
                            # Only report if they share at least 2 meaningful words
                            if len(shared) >= 2:
                                entry = (
                                    f"  **{name_a}** → `{rule_a[:100].strip()}...`\n"
                                    f"  **{name_b}** → `{rule_b[:100].strip()}...`\n"
                                    f"  Shared terms: {', '.join(sorted(shared)[:5])}"
                                )
                                if entry not in warnings:
                                    warnings.append(entry)

    return warnings[:20]  # Cap at 20 to avoid overwhelming output


# ---------------------------------------------------------------------------
# Reference deduplication
# ---------------------------------------------------------------------------

def find_duplicate_references(skills: list[dict]) -> list[str]:
    """Find reference files across skills that likely cover the same topic."""
    duplicates = []

    # Compare reference file names and content topics
    all_refs: list[tuple[str, str, str, str]] = []  # (skill_name, rel_path, basename, text)
    for skill in skills:
        for rel_path, content in skill["references"].items():
            basename = Path(rel_path).stem.lower()
            all_refs.append((skill["name"], rel_path, basename, content))

    # Check for name similarity
    for i in range(len(all_refs)):
        for j in range(i + 1, len(all_refs)):
            name_a, path_a, base_a, text_a = all_refs[i]
            name_b, path_b, base_b, text_b = all_refs[j]

            if name_a == name_b:
                continue  # Same skill

            # Name similarity (shared words after splitting on dashes/underscores)
            words_a = set(re.split(r"[-_]", base_a))
            words_b = set(re.split(r"[-_]", base_b))
            name_overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)

            # Content similarity (topic overlap)
            topics_a = extract_topics(text_a, top_n=30)
            topics_b = extract_topics(text_b, top_n=30)
            content_overlap = jaccard(topics_a, topics_b)

            if name_overlap >= 0.5 or content_overlap >= 0.4:
                score = max(name_overlap, content_overlap)
                duplicates.append(
                    f"  `{name_a}/{path_a}` ≈ `{name_b}/{path_b}`  "
                    f"(similarity: {score:.0%})"
                )

    return duplicates


# ---------------------------------------------------------------------------
# Token estimation (rough: ~4 chars per token)
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def build_overlap_matrix(skills: list[dict]) -> str:
    """Build a markdown table showing pairwise Jaccard overlap."""
    names = [s["name"] for s in skills]
    topic_sets = [extract_topics(full_text(s)) for s in skills]

    # Header
    col_width = max(len(n) for n in names) + 2
    header = "| " + " | ".join(n.ljust(col_width) for n in [""] + names) + " |"
    separator = "|-" + "-|-".join("-" * col_width for _ in [""] + names) + "-|"

    rows = [header, separator]
    for i, name_i in enumerate(names):
        cells = [name_i.ljust(col_width)]
        for j in range(len(names)):
            if i == j:
                cells.append("100%".ljust(col_width))
            else:
                score = jaccard(topic_sets[i], topic_sets[j])
                cells.append(f"{score:.0%}".ljust(col_width))
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join(rows)


def build_context_document(skills: list[dict]) -> str:
    """Build the full _fusion_context.md document."""
    lines: list[str] = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    skill_names = ", ".join(s["name"] for s in skills)

    lines += [
        "# Fusion Analysis Context",
        f"Generated: {ts}  ",
        f"Skills: {skill_names}",
        f"Skills count: {len(skills)}",
        "",
        "---",
        "",
        "## Overview",
        "",
    ]

    # Summary table
    lines.append("| Skill | Description | References | Scripts | Est. Tokens |")
    lines.append("|---|---|---|---|---|")
    for s in skills:
        desc_short = (s["description"][:80] + "...") if len(s["description"]) > 80 else s["description"]
        ref_count = len(s["references"])
        scripts = "yes" if s["has_scripts"] else "—"
        tokens = estimate_tokens(full_text(s))
        lines.append(f"| `{s['name']}` | {desc_short} | {ref_count} files | {scripts} | ~{tokens:,} |")

    total_tokens = sum(estimate_tokens(full_text(s)) for s in skills)
    lines += [
        "",
        f"**Total tokens across all skills: ~{total_tokens:,}**",
        "",
    ]

    # Overlap matrix
    lines += [
        "---",
        "",
        "## Topic Overlap Matrix",
        "",
        "> Jaccard similarity on top-60 topic keywords. "
        ">80% = heavy overlap (strong merge candidate). <20% = distinct domains.",
        "",
        build_overlap_matrix(skills),
        "",
    ]

    # Conflict warnings
    conflicts = detect_conflicts(skills)
    lines += [
        "---",
        "",
        "## Conflict Warnings",
        "",
    ]
    if conflicts:
        lines.append(f"Found {len(conflicts)} potential contradictions (review before merging):\n")
        for i, c in enumerate(conflicts, 1):
            lines.append(f"### Conflict {i}\n{c}\n")
    else:
        lines.append("No contradictory rules detected. Skills appear compatible for merging.")
    lines.append("")

    # Reference inventory
    dup_refs = find_duplicate_references(skills)
    lines += [
        "---",
        "",
        "## Reference Inventory",
        "",
    ]
    for s in skills:
        lines.append(f"### `{s['name']}/references/`")
        if s["references"]:
            for rel_path, content in s["references"].items():
                tok = estimate_tokens(content)
                topics = sorted(extract_topics(content, top_n=5))[:5]
                topic_str = ", ".join(topics) if topics else "—"
                lines.append(f"  - `{rel_path}`  (~{tok:,} tokens | topics: {topic_str})")
        else:
            lines.append("  *(no reference files)*")
        extra_dirs = []
        if s["has_scripts"]:
            extra_dirs.append("`scripts/`")
        if s["has_data"]:
            extra_dirs.append("`data/`")
        if s["has_assets"]:
            extra_dirs.append("`assets/`")
        if extra_dirs:
            lines.append(f"  Other directories: {', '.join(extra_dirs)}")
        lines.append("")

    if dup_refs:
        lines += [
            "### Cross-skill duplicate references (likely same topic, different files)",
            "",
        ]
        lines.extend(dup_refs)
    else:
        lines.append("*No cross-skill reference duplicates detected.*")
    lines.append("")

    # Full content — every SKILL.md body and every reference
    lines += [
        "---",
        "",
        "## Full Skill Content",
        "",
        "> This section contains the complete text of every SKILL.md body and",
        "> every reference file. Use this to make merge decisions.",
        "",
    ]

    for s in skills:
        lines += [
            f"---",
            "",
            f"### {s['name']} — SKILL.md",
            "",
            f"**Path:** `{s['path']}/SKILL.md`  ",
            f"**Name:** `{s['name']}`  ",
            f"**Description:** {s['description']}",
            "",
            "**Body:**",
            "",
            s["body"],
            "",
        ]

        if s["references"]:
            for rel_path, content in s["references"].items():
                lines += [
                    f"---",
                    "",
                    f"### {s['name']} — {rel_path}",
                    "",
                    content,
                    "",
                ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Skill path resolution
# ---------------------------------------------------------------------------

SEARCH_PATHS = [
    Path.cwd(),
    Path.cwd() / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".agents" / "skills",
]


def resolve_skill_path(arg: str) -> Path:
    """Resolve a skill argument to an absolute path."""
    p = Path(arg)
    if p.is_absolute() and p.is_dir():
        return p
    if p.is_dir():
        return p.resolve()
    # Try name-based search
    for search_root in SEARCH_PATHS:
        candidate = search_root / arg
        if candidate.is_dir() and (candidate / "SKILL.md").exists():
            return candidate.resolve()
    raise FileNotFoundError(
        f"Cannot find skill '{arg}'. "
        f"Tried: {', '.join(str(s / arg) for s in SEARCH_PATHS)}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-process skills for fusion analysis. Writes _fusion_context.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prepare_fusion.py supabase supabase-postgres-best-practices
  python prepare_fusion.py ./skills/stripe-manager ./skills/stripe-webhooks
  python prepare_fusion.py /abs/path/to/skill-a skill-b skill-c
        """,
    )
    parser.add_argument(
        "skills",
        nargs="+",
        metavar="SKILL",
        help="Skill names or paths (2 or more required)",
    )
    parser.add_argument(
        "-o", "--output",
        default="_fusion_context.md",
        help="Output file path (default: _fusion_context.md)",
    )
    args = parser.parse_args()

    if len(args.skills) < 2:
        print("ERROR: at least 2 skills required for fusion", file=sys.stderr)
        sys.exit(1)

    # Resolve paths
    resolved: list[Path] = []
    errors: list[str] = []
    for arg in args.skills:
        try:
            resolved.append(resolve_skill_path(arg))
        except FileNotFoundError as e:
            errors.append(str(e))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Load skills
    print(f"\nLoading {len(resolved)} skills...")
    skills: list[dict] = []
    for path in resolved:
        try:
            skill = load_skill(path)
            skills.append(skill)
            ref_count = len(skill["references"])
            print(f"  ✓ {skill['name']}  ({ref_count} reference files, path: {path})")
        except Exception as e:
            print(f"  ✗ {path}: {e}", file=sys.stderr)
            sys.exit(1)

    # Build and write context document
    print(f"\nAnalyzing...")
    doc = build_context_document(skills)

    output_path = Path(args.output)
    output_path.write_text(doc, encoding="utf-8")

    total_tokens = sum(estimate_tokens(full_text(s)) for s in skills)
    print(f"\n  Context document written → {output_path}")
    print(f"  Total content: ~{total_tokens:,} tokens across all skills")
    print(f"  Context doc size: ~{estimate_tokens(doc):,} tokens")
    print()

    # Quick overlap summary to stdout
    if len(skills) == 2:
        topics_a = extract_topics(full_text(skills[0]))
        topics_b = extract_topics(full_text(skills[1]))
        score = jaccard(topics_a, topics_b)
        label = "HIGH" if score > 0.5 else "MEDIUM" if score > 0.25 else "LOW"
        print(f"  Overlap ({skills[0]['name']} ↔ {skills[1]['name']}): {score:.0%} [{label}]")
    else:
        print("  Overlap matrix summary:")
        topic_sets = [extract_topics(full_text(s)) for s in skills]
        for i in range(len(skills)):
            for j in range(i + 1, len(skills)):
                score = jaccard(topic_sets[i], topic_sets[j])
                label = "HIGH" if score > 0.5 else "MEDIUM" if score > 0.25 else "LOW"
                print(f"    {skills[i]['name']} ↔ {skills[j]['name']}: {score:.0%} [{label}]")

    conflicts = detect_conflicts(skills)
    if conflicts:
        print(f"\n  ⚠ {len(conflicts)} potential conflicts detected — review in context doc")
    else:
        print("\n  ✓ No conflicts detected")

    dup_refs = find_duplicate_references(skills)
    if dup_refs:
        print(f"  ⚠ {len(dup_refs)} duplicate reference files detected")
    else:
        print("  ✓ No duplicate references")

    print(f"\nReady. Pass _fusion_context.md to Claude for analysis.\n")


if __name__ == "__main__":
    main()
