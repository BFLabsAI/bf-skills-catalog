# SEO/GEO Python Scripts Reference

Python scripts for SEO auditing and keyword research. Located in the original seo-geo skill's
`scripts/` folder. These are referenced here for portability — if running from the original
skill install location, use the paths below.

Source: seo-geo/scripts/

---

## Setup (DataForSEO API — required for most scripts except seo_audit.py)

```bash
export DATAFORSEO_LOGIN=your_login
export DATAFORSEO_PASSWORD=your_password
```

DataForSEO is a pay-per-use API. Scripts that use it are marked below.
Get credentials at: dataforseo.com

---

## seo_audit.py — No API Required

Full SEO audit: meta tags, robots.txt, sitemap, load time, schema markup detection (static
HTML only — cannot detect JS-injected schema), AI bot access configuration.

```bash
python3 scripts/seo_audit.py "https://example.com"
```

**Output:** Checks title, meta description, H1, robots.txt, sitemap, page load time,
Open Graph tags, basic schema presence, AI bot allowance in robots.txt.

**Limitation:** Uses static HTML fetch. Cannot detect JS-injected JSON-LD. For schema
validation, use Google Rich Results Test.

---

## keyword_research.py — DataForSEO API

Get keyword ideas, search volume, and difficulty.

```bash
python3 scripts/keyword_research.py "seo tools" --limit 20
python3 scripts/keyword_research.py "seo tools" --location 2826  # UK
python3 scripts/keyword_research.py "landing page" --limit 50 --location 2840  # US
```

**Output:** Keyword list with monthly search volume, difficulty score, CPC, competition level.

Common location codes:
- 2840 = United States
- 2826 = United Kingdom
- 2036 = Australia
- 2124 = Canada

---

## serp_analysis.py — DataForSEO API

Analyze top Google results for a keyword.

```bash
python3 scripts/serp_analysis.py "best seo tools" --depth 20
python3 scripts/serp_analysis.py "landing page builder" --depth 10
```

**Output:** Top N URLs, their titles, descriptions, estimated traffic. Useful for
understanding what content types rank for a given keyword.

---

## backlinks.py — DataForSEO API

Get backlink profile for a domain.

```bash
python3 scripts/backlinks.py "example.com" --limit 20
python3 scripts/backlinks.py "competitor.com" --limit 50
```

**Output:** Referring domains, anchor text distribution, do-follow vs no-follow ratio,
domain trust score.

---

## domain_overview.py — DataForSEO API

Get domain-level metrics: traffic estimates, keyword count, rankings.

```bash
python3 scripts/domain_overview.py "example.com"
```

**Output:** Organic traffic estimate, total keywords ranking, visibility score, top pages.

---

## related_keywords.py — DataForSEO API

Find semantically related keywords for a seed term.

```bash
python3 scripts/related_keywords.py "seo audit" --limit 30
```

**Output:** Related keyword list with volume, useful for topical cluster planning.

---

## competitor_gap.py — DataForSEO API

Find keywords competitors rank for that you don't.

```bash
python3 scripts/competitor_gap.py "yourdomain.com" "competitor.com" --limit 20
```

**Output:** Gap keywords with volume and difficulty — prioritize by volume × (1/difficulty).

---

## autocomplete_ideas.py — No API Required

Generate keyword ideas using Google Autocomplete patterns.

```bash
python3 scripts/autocomplete_ideas.py "landing page" --modifier "how to"
```

**Output:** List of autocomplete suggestions — useful for content ideation and long-tail
keyword discovery with zero API cost.

---

## credential.py

Helper module used internally by DataForSEO scripts. Reads the `DATAFORSEO_LOGIN` and
`DATAFORSEO_PASSWORD` environment variables. Not run directly.

---

## dataforseo_api.py

Base API wrapper for DataForSEO. Used internally by all DataForSEO scripts.
Not run directly.

---

## Automation Ideas

1. **Weekly SEO audit** — Schedule `seo_audit.py` against your site; compare output to prior
   week for regressions.
2. **Rank tracking** — Use `serp_analysis.py` weekly on your target keywords; track position
   of your domain in results.
3. **Content freshness monitoring** — Flag pages not updated in 90+ days using Search Console
   API or internal CMS query.
4. **Competitor monitoring** — Run `domain_overview.py` on competitors monthly; track their
   traffic trends.
5. **Schema monitoring** — Validate schema after deploys using Rich Results Test API or a
   curl-based health check.

---

## GEO Monitoring Tools (Third-Party)

When scripts aren't enough and you need ongoing AI visibility monitoring:

| Tool | Focus | Cost |
|---|---|---|
| Otterly.ai | ChatGPT, Perplexity, Google AI Overviews | Free trial |
| Peec AI | ChatGPT, Gemini, Perplexity, Claude, Copilot | Mid-tier paid |
| ZipTie | Google AI Overviews, ChatGPT, Perplexity | Paid |
| LLMrefs | Keyword → AI visibility mapping | Paid |
| Profound | ChatGPT, Perplexity, Claude, Gemini | Enterprise ($499/mo+) |
| Semrush AI Visibility | Google AIO, ChatGPT | Included in Semrush |
| SE Ranking AI Toolkit | AI Overviews, ChatGPT | Included in SE Ranking |
