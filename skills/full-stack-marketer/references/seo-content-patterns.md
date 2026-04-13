# AEO and GEO Content Patterns

Reusable content block patterns for Answer Engine Optimization (AEO) and Generative Engine
Optimization (GEO). These make content extractable by AI systems and citable by AI search engines.

Sources: ai-seo/references/content-patterns.md (primary, comprehensive),
seo-geo/references/geo-research.md (Princeton GEO study detail).

---

## AEO Patterns (Featured Snippets, AI Overviews, Voice Search)

### Definition Block — "What is X?" queries

```markdown
## What is [Term]?

[Term] is [concise 1-sentence definition]. [Expanded 1-2 sentence explanation with key
characteristics]. [Brief context on why it matters or how it's used].
```

**Example:**
```markdown
## What is Answer Engine Optimization?

Answer Engine Optimization (AEO) is the practice of structuring content so AI-powered systems
can easily extract and present it as direct answers to user queries. Unlike traditional SEO
that focuses on ranking in search results, AEO optimizes for featured snippets, AI Overviews,
and voice assistant responses. This approach has become essential as over 60% of Google
searches now end without a click.
```

---

### Step-by-Step Block — "How to X" queries

```markdown
## How to [Action/Goal]

[1-sentence overview of the process]

1. **[Step Name]**: [Clear action description in 1-2 sentences]
2. **[Step Name]**: [Clear action description in 1-2 sentences]
3. **[Step Name]**: [Clear action description in 1-2 sentences]

[Optional: expected outcome or time estimate]
```

---

### Comparison Table Block — "[X] vs [Y]" queries

```markdown
## [Option A] vs [Option B]: [Brief Descriptor]

| Feature | [Option A] | [Option B] |
|---|---|---|
| [Criteria 1] | [Value] | [Value] |
| [Criteria 2] | [Value] | [Value] |
| Best For | [Use case] | [Use case] |

**Bottom line**: [1-2 sentence recommendation based on different needs]
```

---

### Pros and Cons Block — "Is X worth it?" queries

```markdown
## Advantages and Disadvantages of [Topic]

[1-sentence overview]

### Pros
- **[Benefit category]**: [Specific explanation]
- **[Benefit category]**: [Specific explanation]

### Cons
- **[Drawback category]**: [Specific explanation]
- **[Drawback category]**: [Specific explanation]

**Verdict**: [1-2 sentence balanced conclusion with recommendation]
```

---

### FAQ Block — Multiple common questions on a topic

```markdown
## Frequently Asked Questions

### [Question phrased exactly as users search]?

[Direct answer in first sentence]. [Supporting context in 2-3 additional sentences].

### [Question phrased exactly as users search]?

[Direct answer in first sentence]. [Supporting context in 2-3 additional sentences].
```

**FAQ question tips:**
- Phrase naturally ("How do I..." not "How does one...")
- Include question words: what, how, why, when, where, who
- Match "People Also Ask" queries from Google
- Keep answers between 50-100 words
- Pair with FAQPage JSON-LD schema for +40% AI visibility boost

---

### Listicle Block — "Best X," "Top X," "N ways to X" queries

```markdown
## [Number] Best [Items] for [Goal/Purpose]

[1-2 sentence intro with context and selection criteria]

### 1. [Item Name]

[Why included — 2-3 sentences with specific benefits]

### 2. [Item Name]

[Why included — 2-3 sentences with specific benefits]
```

---

## GEO Patterns (AI Citation Optimization)

These increase the likelihood that AI assistants (ChatGPT, Claude, Perplexity, Gemini) will
cite your content when generating answers.

### Statistic Citation Block (+37% citation rate)

```markdown
[Claim statement]. According to [Source/Organization], [specific statistic with number and
timeframe]. [Context for why this matters].
```

**Example:**
```markdown
Mobile optimization is no longer optional for SEO success. According to Google's 2024 Core
Web Vitals report, 70% of web traffic now comes from mobile devices, and pages failing mobile
usability standards see 24% higher bounce rates. This makes mobile-first indexing a critical
ranking factor.
```

---

### Expert Quote Block (+30% citation rate)

```markdown
"[Direct quote from expert]," says [Expert Name], [Title/Role] at [Organization]. [1 sentence
of context or interpretation].
```

**Example:**
```markdown
"The shift from keyword-driven search to intent-driven discovery represents the most
significant change in SEO since mobile-first indexing," says Rand Fishkin, Co-founder of
SparkToro. This perspective highlights why content strategies must evolve beyond traditional
keyword optimization.
```

---

### Authoritative Claim Block (+25% citation rate)

Structure claims for easy AI extraction with clear attribution:

```markdown
[Topic] [verb: is/has/requires] [clear, specific claim]. [Source] [confirms/reports/found]
that [supporting evidence]. This [explains/means/suggests] [implication or action].
```

**Example:**
```markdown
E-E-A-T is the cornerstone of Google's content quality evaluation. Google's Search Quality
Rater Guidelines confirm that trust is the most critical factor, stating that "untrustworthy
pages have low E-E-A-T no matter how experienced, expert, or authoritative they may seem."
This means content creators must prioritize transparency and accuracy above all other
optimization tactics.
```

---

### Self-Contained Answer Block

Create quotable, standalone statements that AI can extract without surrounding context:

```markdown
**[Topic/Question]**: [Complete answer that makes sense without additional context. Include
specific details, numbers, or examples in 2-3 sentences.]
```

**Example:**
```markdown
**Ideal blog post length for SEO**: The optimal length for SEO blog posts is 1,500-2,500 words
for competitive topics. This range allows comprehensive topic coverage while maintaining reader
engagement. HubSpot research shows long-form content earns 77% more backlinks than short
articles, directly impacting search rankings.
```

---

### Evidence Sandwich Block

```markdown
[Opening claim statement].

Evidence supporting this includes:
- [Data point 1 with source]
- [Data point 2 with source]
- [Data point 3 with source]

[Concluding statement connecting evidence to actionable insight].
```

---

## Princeton GEO Study Summary (KDD 2024)

**Paper:** "GEO: Generative Engine Optimization" — Princeton, IIT Delhi, Georgia Tech,
Allen Institute for AI. arXiv:2311.09735. Validated on Perplexity.ai.

| Method | Visibility Boost | Application |
|---|---|---|
| Cite sources | +40% | Add authoritative references with links |
| Add statistics | +37% | Specific numbers with sources and dates |
| Add expert quotes | +30% | Name + title + organization |
| Authoritative tone | +25% | Confident, demonstrated expertise |
| Improve clarity | +20% | Simplify complex concepts |
| Technical terms | +18% | Domain-specific terminology |
| Unique vocabulary | +15% | Increase word diversity |
| Fluency | +15-30% | Readability and flow |
| Keyword stuffing | **-10%** | **Actively hurts AI visibility** |

**Best combinations:**
- Fluency + Statistics = highest overall boost
- Citations + Authoritative Tone = best for professional content
- Easy Language + Statistics = best for consumer content
- Technical Terms + Citations = best for academic/scientific

**Low-ranking site benefit:** Combining citations with other methods can produce up to 115%
visibility increase for sites that don't rank in the traditional top results.

---

## Domain-Specific GEO Tactics

### Technology Content
- Emphasize technical precision and correct terminology
- Include version numbers and dates for software/tools
- Reference official documentation
- Add code examples where relevant

### Business/Marketing Content
- Include case studies with measurable results
- Reference industry research and reports
- Add percentage changes with timeframes
- Quote recognized thought leaders

### Health/Medical Content
- Cite peer-reviewed studies with publication details
- Include expert credentials (MD, RN, etc.)
- Note study limitations and context
- Add "last reviewed" dates

### Financial Content
- Reference regulatory bodies (SEC, FTC, etc.)
- Include specific numbers with timeframes
- Cite recognized financial institutions

### Legal Content
- Cite specific laws, statutes, and regulations
- Reference jurisdiction clearly
- Include professional disclaimers

---

## Voice Search Optimization

Voice queries are conversational and question-based.

**Question formats for voice:**
- "What is..."
- "How do I..."
- "Where can I find..."
- "Why does..."
- "When should I..."

**Voice-optimized answer structure:**
- Lead with direct answer (under 30 words ideal)
- Use natural, conversational language
- Avoid jargon unless targeting expert audience
- Include local context where relevant
- Structure for single spoken response

---

## Structural Rules for AI Extractability

- Lead every section with a direct answer (don't bury it)
- Keep key answer passages to 40-60 words (optimal for snippet extraction)
- Use H2/H3 headings that match how people phrase queries
- Tables beat prose for comparison content
- Numbered lists beat paragraphs for process content
- Each paragraph should convey one clear idea
- Self-contained paragraphs — don't rely on surrounding context for meaning

---

## Content Types by Citation Rate (AI systems)

| Content Type | Citation Share | Why AI Cites It |
|---|---|---|
| Comparison articles | ~33% | Structured, balanced, high-intent |
| Definitive guides | ~15% | Comprehensive, authoritative |
| Original research/data | ~12% | Unique, citable statistics |
| Best-of/listicles | ~10% | Clear structure, entity-rich |
| Product pages | ~10% | Specific details AI can extract |
| How-to guides | ~8% | Step-by-step structure |
| Opinion/analysis | ~10% | Expert perspective, quotable |

**Underperformers for AI citation:**
- Generic blog posts without structure
- Thin product pages with marketing fluff
- Gated content (AI can't access it)
- Content without dates or author attribution
- PDF-only content (harder for AI to parse — unless on Perplexity)
