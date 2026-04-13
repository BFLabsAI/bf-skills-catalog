# AI Platform Ranking Factors

How each AI search platform selects sources and what to optimize per platform.

Sources: ai-seo/references/platform-ranking-factors.md (primary, more detailed),
supplemented by seo-geo/references/platform-algorithms.md.
Princeton GEO study (KDD 2024, arXiv:2311.09735), SE Ranking 129K domain study,
ZipTie 400K page content-answer fit analysis.

---

## The Fundamentals (Every Platform)

1. **Your content must be in their index** — each platform uses a different search backend.
   If you're not indexed there, you can't be cited.
2. **Your content must be crawlable** — AI bots need access via robots.txt. Block the bot,
   lose the citation.
3. **Your content must be extractable** — AI systems pull passages, not pages. Clear structure
   and self-contained paragraphs win.

---

## Google AI Overviews

**Index:** Google's own index (same as traditional Google).
**Appears in:** ~45% of Google searches.
**Overlap with traditional Top 10:** Only ~15%. Pages not on page 1 can still be cited.

**What makes AI Overviews different from traditional Google:** They already have your standard
SEO signals. The added AI layer weights structured data and cited sources heavily.
Research shows: authoritative citations → +132% visibility; authoritative tone → +89%.

**What matters most:**
- Schema markup (Article, FAQPage, HowTo, Product) — single biggest lever, 30-40% visibility boost
- Topical authority through content clusters + strong internal linking
- Named, sourced citations in content (not just claims)
- Author bios with real credentials (E-E-A-T heavily weighted)
- Google Knowledge Graph inclusion (accurate Wikipedia entry helps)
- Target "how to" and "what is" query patterns — these trigger AI Overviews most often

**Architecture:** PaLM2 (language understanding) + MUM (multimodal) + Gemini (reasoning).
5-stage pipeline: Retrieval → Semantic Ranking → LLM Re-ranking → E-E-A-T Evaluation →
Data Fusion.

---

## ChatGPT

**Index:** Bing-based web index + training knowledge.

**What makes ChatGPT different:**
- Domain authority is the strongest baseline signal (~40% of citation determination)
- Content quality accounts for ~35%, platform trust ~25%
- Sites with 350K+ referring domains average 8.4 citations; 91-96 trust score = 6 citations
- **Content updated within 30 days gets cited 3.2x more** — freshness is a major differentiator
- Content-answer fit (how well your content style matches ChatGPT's response format) accounts
  for **~55% of citation likelihood** — more important than domain authority (12%) or
  on-page structure (14%) alone

**Where ChatGPT looks beyond your site:**
Wikipedia: 7.8% of all citations. Reddit: 1.8%. Forbes: 1.1%.

**What to focus on:**
- Invest in backlinks and domain authority — strongest baseline signal
- Update competitive content at least monthly
- Write the way ChatGPT structures its answers: conversational, direct, well-organized
- Include verifiable statistics with named sources
- Clean H1 > H2 > H3 heading structure with descriptive headings

---

## Perplexity

**Index:** Own index + Google. Three-layer reranking: L1 (basic relevance) → L2 (traditional
ranking factors) → L3 (ML quality evaluation — can discard entire result sets).

**What makes Perplexity different:**
- Most research-oriented AI search engine; always cites sources with clickable links
- Curated authoritative domain lists (Amazon, GitHub, major academic sites get inherent boost)
- Time-decay algorithm evaluates new content quickly
- **PDF documents** (publicly hosted) are prioritized — consider making whitepapers public

**Unique content preferences:**
- FAQ Schema (JSON-LD) — pages with FAQ blocks cited noticeably more often
- Publishing velocity matters more than keyword density
- Self-contained, atomic paragraphs preferred — Perplexity extracts them cleanly
- Semantic relevance over keyword matching

**What to focus on:**
- Allow PerplexityBot in robots.txt
- Implement FAQPage schema on any page with Q&A content
- Host PDF resources publicly (whitepapers, guides, reports)
- Add Article schema with publication and modification timestamps
- Write in clear, self-contained paragraphs that work as standalone answers

---

## Microsoft Copilot

**Index:** Bing entirely. Must be in Bing's index to be cited by Copilot.

**What makes Copilot different:**
- Microsoft ecosystem creates unique opportunities — LinkedIn and GitHub mentions provide
  ranking boosts no other platform offers
- Page speed threshold: sub-2-second load times are a clear signal
- IndexNow protocol for faster indexing of new/updated content

**What to focus on:**
- Submit site to Bing Webmaster Tools (many sites only submit to Google Search Console)
- Use IndexNow for new and updated content
- Optimize page speed to under 2 seconds
- Write clear entity definitions — make them explicit and extractable
- Build LinkedIn presence (publish articles, maintain company page) and GitHub if relevant
- Allow Bingbot full crawl access

---

## Claude

**Index:** Brave Search — not Google, not Bing. Brave Search visibility directly determines
whether Claude can find and cite you.

**Claude crawl-to-refer ratio: 38,065:1.** Claude processes enormous amounts of content but
is extremely selective — it cites only the most factually accurate, well-sourced content.

**What to focus on:**
- Verify your content appears in Brave Search (`search.brave.com`)
- Allow ClaudeBot and anthropic-ai in robots.txt
- Maximize factual density: specific numbers, named sources, dated statistics
- Clear, extractable structure with descriptive headings
- Cite authoritative sources within your content
- Be the most factually accurate source on your topic — Claude rewards precision

---

## Gemini

**Index:** Google index + Knowledge Graph.

**What to focus on:** Same as Google AI Overviews (E-E-A-T, structured data, topical authority,
Knowledge Graph presence). Gemini pulls from Google's ecosystem.

---

## robots.txt Configuration for AI Bots

```
# Search Engines
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /

# AI Bots — allow all for full citation potential
User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: Google-Extended
Allow: /

# Training-only — safe to block without affecting citations
# User-agent: CCBot
# Disallow: /

Sitemap: https://example.com/sitemap.xml
```

**Training vs. search bots:** GPTBot handles both training and search for OpenAI. Blocking it
removes you from both. CCBot (Common Crawl) is training-dataset only — blocking it has no
effect on any AI search citations.

---

## Traditional Google SEO (2026)

| Factor | Weight/Details |
|---|---|
| Backlinks | Quality referring domains — core ranking system |
| E-E-A-T | Experience, Expertise, Authority, Trust |
| Content Quality | Original, comprehensive, helpful content |
| Page Experience | Core Web Vitals (LCP, INP, CLS) |
| Mobile-First | Non-mobile sites risk not being indexed |
| Search Intent Match | Content must match user query intent |
| Content Freshness | Regular substantive updates |
| Technical SEO | Crawlable, indexable, HTTPS |
| Structured Data | Schema markup for rich results |

---

## Cross-Platform Optimization Summary

| Platform | Primary Index | Key Differentiator |
|---|---|---|
| Google AI Overviews | Google | E-E-A-T + schema markup |
| ChatGPT | Bing-based | Freshness + content-answer fit |
| Perplexity | Own + Google | FAQ schema + PDF resources |
| Copilot | Bing | Bing indexing + IndexNow |
| Claude | Brave | Factual density + Brave indexing |
| Gemini | Google | Same as Google AI Overviews |

**Actions that help every platform:**
1. Allow all AI bots in robots.txt
2. Schema markup: FAQPage, Article, Organization at minimum
3. Statistics with named sources in content
4. Update content regularly — monthly for competitive topics
5. Clear heading structure (H1 > H2 > H3)
6. Page load time under 2 seconds
7. Author bios with credentials (E-E-A-T)

---

## AI Visibility Monitoring

| Tool | Platforms Covered | Best For |
|---|---|---|
| Otterly AI | ChatGPT, Perplexity, Google AI Overviews | Share of AI voice tracking |
| Peec AI | ChatGPT, Gemini, Perplexity, Claude, Copilot | Multi-platform monitoring at scale |
| ZipTie | Google AI Overviews, ChatGPT, Perplexity | Brand mention + sentiment |
| LLMrefs | ChatGPT, Perplexity, AI Overviews, Gemini | SEO keyword → AI visibility mapping |
| Profound | ChatGPT, Perplexity, Claude, Gemini | Enterprise-level brand tracking |

**DIY monitoring (no tools):** Pick your top 20 queries. Run each through ChatGPT, Perplexity,
and Google monthly. Record: cited? who is? which page? Log in a spreadsheet.

---

## Where to Start

1. **Google AI Overviews first** — reaches most users (45%+ of Google searches) and you likely
   have Google SEO foundations. Add schema markup, cited sources, strengthen E-E-A-T.
2. **Then ChatGPT** — most-used standalone AI search for tech and business. Focus on freshness
   (update monthly), domain authority, content-answer fit.
3. **Then Perplexity** — especially valuable if audience includes researchers or tech
   professionals. Add FAQ schema, publish PDFs, write self-contained paragraphs.
4. **Copilot and Claude** — lower priority unless your audience skews enterprise (Copilot) or
   developer/analyst (Claude). The fundamentals help everywhere anyway.
