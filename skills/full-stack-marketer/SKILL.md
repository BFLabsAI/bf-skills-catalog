---
name: full-stack-marketer
description: >
  Full-stack marketing skill covering SEO audits, technical SEO, AI search optimization (GEO/AEO/LLMO),
  generative engine optimization, indexing troubleshooting, schema markup, app analytics, tracking setup,
  KPI interpretation, landing page generation, landing page copywriting, website structure planning,
  cloning websites into Next.js, and website builder setup. Use when the user wants to: audit SEO,
  fix indexing issues, optimize for AI search engines (ChatGPT, Perplexity, Gemini, Copilot, Claude),
  improve AI citations, check core web vitals, diagnose why they aren't ranking, set up analytics
  or tracking, interpret app metrics, build a landing page, write high-converting copy, plan site
  architecture, clone a website design, or set up the AI website builder stack.
  Trigger phrases: "SEO audit", "SEO issues", "why am I not ranking", "technical SEO", "meta tags",
  "schema markup", "AI SEO", "AEO", "GEO", "LLMO", "AI Overviews", "optimize for ChatGPT",
  "optimize for Perplexity", "AI citations", "AI visibility", "indexing", "not indexed",
  "crawl errors", "noindex", "Google Indexing API", "analytics", "tracking", "KPIs", "metrics",
  "app analytics", "install tracking", "attribution", "funnel", "landing page", "marketing page",
  "launch page", "coming soon page", "landing page copy", "high-converting page", "hero section",
  "website structure", "which pages do I need", "site architecture", "clone website", "vibe clone",
  "replicate this page", "website builder", "Framer Motion", "21st.dev".
metadata:
  version: 1.0.0
---

# Full-Stack Marketer

Three marketing roles in one skill. When you receive a request, identify which role applies and
adopt that mindset exclusively for the task. Roles do not overlap in execution — pick the most
specific fit.

**Role Quick Reference:**

| Request type | Active role |
|---|---|
| SEO audit, ranking issues, AI visibility, indexing, schema, GEO/AEO | SEO Specialist |
| Analytics setup, metrics interpretation, tracking plan, KPIs | Analytics Analyst |
| Landing pages, copywriting, site structure, cloning, builder setup | Content & Page Builder |

---

## Role 1: SEO Specialist

**Activate when:** user mentions SEO audit, ranking drops, technical SEO, indexing issues, crawl
errors, meta tags, schema markup, AI search optimization, GEO, AEO, LLMO, AI Overviews, appearing
in ChatGPT/Perplexity/Gemini/Copilot/Claude, or any variation of "why isn't my site ranking."

### Context Check (do first)

If `.agents/product-marketing-context.md` or `.claude/product-marketing-context.md` exists, read
it before asking questions. If `.claude/project-context.md` or `.cursor/project-context.md`
exists for indexing tasks, read it for site URL and goals.

### SEO Audit Framework

**Priority order — always work top-down:**
1. Crawlability & Indexation (can search engines find and index it?)
2. Technical Foundations (speed, mobile, HTTPS, Core Web Vitals)
3. On-Page Optimization (titles, H1s, content quality)
4. Content & E-E-A-T (experience, expertise, authority, trust)
5. Authority & Links (backlinks, citations)

**Schema detection warning:** `web_fetch` and `curl` strip `<script>` tags and cannot detect
JSON-LD injected by JavaScript (AIOSEO, Yoast, RankMath). To check schema, use the browser tool
(`document.querySelectorAll('script[type="application/ld+json"]')`), Google Rich Results Test,
or Screaming Frog. Never report "no schema found" from a static fetch alone.

**Core Web Vitals targets:** LCP < 2.5s, INP < 200ms, CLS < 0.1

For the full technical audit checklist (robots.txt, sitemaps, canonicals, on-page, E-E-A-T,
issue tables by site type), see [references/seo-audit-guide.md](references/seo-audit-guide.md).

### Indexing Troubleshooting

| GSC Issue | Fix |
|---|---|
| Crawled - currently not indexed | Improve content quality, fix duplicates, verify canonical, request indexing |
| Excluded by noindex tag | Remove if accidental; keep if intentional |
| Soft-404 | Return proper 404 status OR add real content for 200 pages |
| Blocked by robots.txt | See robots-txt skill; remove Disallow for important paths |
| Vercel static assets (`_next/`) | Normal and expected — do not block `/_next/` |

**noindex rules:** Use `noindex,follow` for login, thank-you, checkout pages. Use
`noindex,nofollow` only for admin, staging, test pages. robots.txt = path-level crawl control;
noindex = page-level index control. Do not block noindex pages in robots.txt — crawlers must
reach the page to read the directive.

**Google Indexing API** — available for JobPosting and BroadcastEvent types only. Requires
service account, Search Console owner permission, and default quota of 200 URLs/day.

### AI Search Optimization (GEO / AEO)

Traditional SEO gets you ranked. AI SEO gets you **cited**. AI systems extract passages, not
pages. A well-structured page on page 2 can be cited in AI Overviews if it has strong structure
and authority signals.

**The Three Pillars:**

**1. Structure — make content extractable**
- Lead every section with a direct answer
- 40-60 word answer blocks (optimal for snippet extraction)
- Use H2/H3 headings that match how users phrase queries
- Tables beat prose for comparisons; numbered lists beat prose for processes
- FAQ blocks, definition blocks, step-by-step blocks, comparison tables

**2. Authority — make content citable**
The Princeton GEO study (KDD 2024) ranked 9 optimization methods tested on Perplexity.ai:

| Method | Visibility Boost | Action |
|---|---|---|
| Cite sources | +40% | Add authoritative references with links |
| Add statistics | +37% | Specific numbers with named sources |
| Add expert quotes | +30% | Name + title + organization |
| Authoritative tone | +25% | Confident, demonstrated expertise |
| Improve clarity | +20% | Simplify complex concepts |
| Technical terms | +18% | Domain-specific terminology |
| Unique vocabulary | +15% | Word diversity |
| Fluency | +15-30% | Readability and flow |
| Keyword stuffing | **-10%** | **Actively hurts AI visibility — avoid** |

Best combination: Fluency + Statistics = maximum boost.

**3. Presence — be where AI looks**
- Wikipedia mentions (7.8% of ChatGPT citations)
- Reddit (1.8%), Forbes (1.1%), industry publications
- Review sites (G2, Capterra for B2B SaaS)
- YouTube (frequently cited by Google AI Overviews)

**Machine-readable files for AI agents:**
Add `/pricing.md` and `/llms.txt` to your site root. AI agents evaluating tools on behalf of
buyers cannot parse JS-rendered pricing pages or "contact sales" walls. A simple markdown file
with your plans, limits, and features is parseable by any LLM.

**AI bot access:** Allow GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, anthropic-ai,
Google-Extended, Bingbot in robots.txt. Blocking any means that platform cannot cite you.
CCBot (Common Crawl) is training-only — safe to block. Full robots.txt template in
[references/seo-platform-ranking.md](references/seo-platform-ranking.md).

For per-platform ranking factors (ChatGPT domain authority signals, Perplexity FAQ schema
preference, Copilot Bing index requirement, Claude Brave Search index), see
[references/seo-platform-ranking.md](references/seo-platform-ranking.md).

For all JSON-LD schema templates (FAQPage, Article, HowTo, Product, Organization, LocalBusiness,
BreadcrumbList, SpeakableSpecification), see
[references/seo-schema-templates.md](references/seo-schema-templates.md).

For AEO content block patterns (definition, step-by-step, comparison, FAQ, GEO citation patterns),
see [references/seo-content-patterns.md](references/seo-content-patterns.md).

For the SEO/GEO Python scripts (seo_audit.py, keyword_research.py, serp_analysis.py, backlinks.py,
domain_overview.py), see [references/seo-scripts-reference.md](references/seo-scripts-reference.md).

### AI Writing Detection

Avoid these patterns that signal AI-generated content. Key tells: em dashes (—) overused, verbs
like "delve," "leverage," "underscore," adjectives like "robust," "pivotal," "seamless," openers
like "In today's fast-paced world..." For the full word list and replacements, see
[references/seo-ai-writing-detection.md](references/seo-ai-writing-detection.md).

### Audit Report Output Format

```
Executive Summary
- Overall health (score or grade)
- Top 3-5 priority issues
- Quick wins

Technical SEO Findings
Issue | Impact (H/M/L) | Evidence | Fix | Priority

On-Page Findings
[same format]

Content Findings
[same format]

Prioritized Action Plan
1. Critical fixes (blocking indexation/ranking)
2. High-impact improvements
3. Quick wins
4. Long-term recommendations
```

### SEO Tools

**Free:** Google Search Console (essential), PageSpeed Insights, Bing Webmaster Tools,
Rich Results Test (use for schema — it renders JS), Mobile-Friendly Test.
**Paid (if available):** Screaming Frog, Ahrefs, Semrush, Sitebulb.
**AI visibility monitoring:** Otterly AI, Peec AI, ZipTie, LLMrefs.

---

## Role 2: Analytics Analyst

**Activate when:** user mentions analytics, tracking, metrics, KPIs, App Store Connect, install
tracking, funnel, attribution, "how is my app performing," DAU, MAU, retention, LTV, MRR,
revenue analytics, or any question about measuring app or product performance.

### Context Check (do first)

Check for `app-marketing-context.md`. Then ask:
1. What analytics tools do you currently use?
2. What are your top 3 questions about your app's performance?
3. What decisions do you need data to make?
4. Do you run paid acquisition? (attribution matters)

### Analytics Stack

| Tool | Purpose | Cost | Priority |
|---|---|---|---|
| App Store Connect | Store metrics, downloads, conversion | Free | Must have |
| Firebase Analytics | In-app events, funnels, audiences | Free | Must have |
| Mixpanel / Amplitude | Product analytics, cohorts, funnels | Free tier | Recommended |
| RevenueCat | Subscription analytics, paywall testing | Free tier | If subscriptions |
| Adjust / AppsFlyer | Attribution, UA measurement | Paid | If running ads |
| Crashlytics | Crash reporting, stability | Free | Must have |

### Key Metrics Framework

**Acquisition:** Impressions, Tap-Through Rate (Taps/Impressions), Conversion Rate
(Downloads/Page Views), CPI (Ad Spend/Installs), Organic %.

**Engagement:** DAU, MAU, DAU/MAU stickiness (>20% is good), Sessions/User, Session Length.

**Retention benchmarks:** Day 1: 25-40%, Day 7: 10-20%, Day 30: 5-10%, Monthly churn < 5%.

**Revenue:** ARPU, ARPPU, LTV (ARPU × Avg Lifetime), Trial-to-Paid rate, MRR, Churn Revenue.

For the complete metrics tables with formulas, benchmarks, and App Store Connect metric
definitions, see [references/analytics-metrics-guide.md](references/analytics-metrics-guide.md).

### Event Tracking Plan

**Event naming:** `snake_case`, format `[object]_[action]`. No PII in properties. Consistent
across platforms. Core events: onboarding_started/completed/skipped, paywall_viewed (source,
variant), purchase_completed (plan, price, source), subscription_cancelled (reason),
feature_used (feature_name), session_started (source). Full event list in
[references/analytics-metrics-guide.md](references/analytics-metrics-guide.md).

**Dashboards:** Executive (weekly: downloads, revenue, DAU, conversion, D1 retention, rating);
Funnel (daily: Impressions → Page Views → Downloads → Activation → Purchase with step rates);
Cohort (monthly: retention curves by install date, source, country, plan).

For full output format templates (audit, tracking plan, metric interpretation), see
[references/analytics-metrics-guide.md](references/analytics-metrics-guide.md).

---

## Role 3: Content & Page Builder

**Activate when:** user mentions landing page, marketing page, product launch page, coming soon
page, high-converting copy, hero section, website structure, which pages to build, site
architecture, cloning a website, vibe clone, replicating a design, or setting up the website
builder stack (UI/UX Pro Max, Framer Motion, 21st.dev).

### 3a. Landing Page Generator

**When to activate:** "landing page," "create a page," "marketing page," "launch page,"
"coming soon page," "one-page site."

**Gather the brief first:**

| Field | Required |
|---|---|
| Business/product name | Yes |
| Value proposition | Yes |
| Target audience | Yes |
| Primary CTA | Yes |
| Brand colours / secondary CTA / logo / phone / sections | No |

If no brand colours, suggest `color-palette` skill or default to slate/blue.

**Output:** Single self-contained HTML file with Tailwind CSS via CDN, responsive (mobile-first,
sm:640px, lg:1024px breakpoints), dark mode toggle (light/dark/system), semantic HTML5, OG and
Twitter card meta tags, Schema.org FAQPage markup in FAQ section, no external fonts, lazy-loaded
images.

**Standard section order:** Nav (sticky, CTA button, mobile hamburger), Hero (H1 = value prop
not business name, subheadline, primary CTA, optional image), Features (3-6 items in responsive
grid), Social Proof (2-3 testimonial cards or logo bar), Pricing (optional, 2-3 tier cards),
FAQ (details/summary accordion), Footer (contact, legal links, copyright).

**Page type variations:**

| Request | Approach |
|---|---|
| Coming soon | Hero + email signup + countdown |
| Product launch | Hero + features + pricing + CTA-heavy |
| Portfolio | Hero + project grid + about + contact |
| Event | Hero + schedule + speakers + venue + register |
| App download | Hero + features + screenshots + app store badges |

**Quality rules:** No lorem ipsum — generate realistic placeholder text. No inline styles — use
Tailwind classes only. Heading hierarchy never skips levels. Accessible by default (4.5:1
contrast, focus-visible, alt text, skip-to-content). Australian conventions if the business
is Australian (+61 format, Australian spelling, ABN placeholder).

After generating: tell user how to preview (`open index.html` or `python3 -m http.server`) and
suggest deployment (Cloudflare Pages, Netlify drop, `wrangler deploy`).

### 3b. Landing Page Copywriting

**When to activate:** "write copy for a landing page," "improve my landing page," "hero section
copy," "conversion optimization," "audit this page," "write a CTA."

**Core Principle:** A landing page has one job — get the visitor to take one action. Every
element must support that single conversion goal. Top performers convert at 25%+ vs 5-15% average.
The difference is almost always copy and structure, not design.

**Universal page structure:**

```
1. HERO — Headline + Subheadline + CTA + Visual
2. PROBLEM — Pain point agitation (3-5 specific points in their language)
3. SOLUTION — Product as THE answer, focus on outcomes not features
4. FEATURES/BENEFITS — FAB formula: Feature → Advantage → Benefit (3-5 max)
5. SOCIAL PROOF — Testimonials (specific results), logos, numbers, case studies
6. OBJECTION HANDLING — FAQ or comparison table or "Is this for you?" section
7. FINAL CTA — Recap transformation, restate benefits, urgency, guarantee
8. FOOTER — Trust signals, secondary links
```

**Hero rules:** Answers "What is this / Who is it for / Why should I care" within 5 seconds.
Headline = clear primary benefit or transformation, 10 words or fewer. Subheadline adds
specificity, 20-30 words max. CTA = value-focused text, high contrast.

**Objection handling patterns:** FAQ (direct Q&A), comparison table (before/after), or
"Is this for you?" (explicit in/out criteria).

For the complete copy templates for each section, example pages (SaaS, lead gen), audit checklist,
landing page brief template, and page structure by goal type, see
[references/content-landing-page-copy.md](references/content-landing-page-copy.md).

### 3c. Website Structure Planning

**When to activate:** "website structure," "site structure," "which pages do I need," "page
planning," "sitemap planning," "site hierarchy," "website architecture."

**Identify first:** website type (SaaS, B2B, e-commerce, portfolio), stage (new vs. existing),
growth strategy (affiliate, education, multi-language, community, developer), constraints.

**Page priority framework:**

| Priority | Pages |
|---|---|
| Must Have | Home, Product/Features, Pricing, Blog, About, Privacy, Terms, Contact |
| Great to Have | Testimonials, FAQ, HTML Sitemap, 404, Refund/Returns |
| Optional | Search Results, News, Careers, Disclosure |
| Traffic-driven | Category/Collection pages |

**Structure principles:**
- Max 4 clicks from homepage to any page (flat structure improves crawlability)
- Plan structure before growth, right after domain purchase
- Every page needs internal links (no orphan pages)
- /features = capability-first; /use-cases = scenario-first (differentiate content, link between)
- Marketing site: /pricing in main nav; in-app: Settings → Billing for logged-in users

For the full generic template structure by section (Root, Tools, Resources, Partnership, Legal,
Competitor, Standalone), growth strategy to path mapping, and planning workflow, see
[references/content-website-structure.md](references/content-website-structure.md).

### 3d. Clone Website

**When to activate:** "clone this website," "vibe clone [url]," "replicate this landing page,"
"rebuild this site in Next.js," "clone the hero/pricing/footer from [url]," "copy this design."

**Tech stack (fixed):** Next.js 16 App Router, TypeScript (strict), Tailwind CSS v4, Shadcn UI,
Lucide React icons, Geist Sans font.

**Three phases — never skip Phase 2:**

**Phase 1: Scrape** — Use `firecrawl-mcp___firecrawl_scrape` (formats: markdown+html,
onlyMainContent: true). Fallback: `firecrawl-mcp___firecrawl_crawl` if scrape fails.

**Phase 2: Analysis (MANDATORY — stop here, present to user)**
Read [references/content-clone-analysis-template.md](references/content-clone-analysis-template.md).
Fill out: detected sections, design tokens (colors, typography, spacing), image inventory, proposed
file structure. Ask user to confirm before any code generation.

**Phase 3: Code Generation** (after user confirms)
Files in order: `app/globals.css`, `app/layout.tsx`, `components/landing/[Section].tsx`,
`app/page.tsx`, download images to `public/images/`.

**Image handling:** Extract URLs → attempt download → on failure use Unsplash fallback
(heroes: 1920x1080, avatars: 100x100, features: prefer Lucide icons over images).

**Code standards:** Mobile-first, Tailwind arbitrary values for pixel-perfection
(`w-[347px]`), repeated colors to CSS variables, `cn()` for conditional classes, `gap-*`
over margins for flex/grid, `size-*` over `w-* h-*` when values match.

For Next.js 16 file structure conventions, Tailwind v4 globals.css pattern, Shadcn setup, and
component patterns (Header, Hero variants, Features grid/bento, Testimonials, Pricing, CTA,
Footer), see [references/content-clone-tech-stack.md](references/content-clone-tech-stack.md) and
[references/content-clone-component-patterns.md](references/content-clone-component-patterns.md).

### 3e. Website Builder Setup

**When to activate:** "website builder setup," "install UI/UX Pro Max," "set up Framer Motion,"
"21st.dev setup," "install the website builder stack."

Walks the user through 3 tools, one step at a time. Never dump all steps at once.

**What gets installed:**
- **UI/UX Pro Max** — 50+ styles, 161 palettes, 57 font pairings. `npm install -g uipro-cli && uipro init --ai claude`
- **Framer Motion** — animations, transitions, scroll reveals. `claude install-skill https://github.com/secondsky/claude-skills -- --name motion`
- **21st.dev Magic** — 100+ React components. Free API key from 21st.dev/magic/console; add to `~/.claude.json` mcpServers.

**Rules:** One step at a time. If any install fails, acknowledge + give manual command + keep moving.
Assume zero coding experience. Restart Claude Code after 21st.dev install.

---

## Rules and Invariants

- **Always check for context files first** (`product-marketing-context.md`, `project-context.md`,
  `app-marketing-context.md`) before asking questions — read what's already there.
- **Schema detection:** Never report "no schema found" from `web_fetch` or `curl` alone — they
  cannot see JS-injected JSON-LD. Use browser tool or Rich Results Test.
- **noindex + robots.txt:** Do not block noindex pages in robots.txt — crawlers must reach the
  page to read the noindex directive.
- **AI bot access:** Blocking GPTBot, PerplexityBot, or ClaudeBot in robots.txt means that
  platform cannot cite you. CCBot is safe to block (training only).
- **Keyword stuffing hurts AI visibility** by -10% (Princeton GEO study) — avoid it even where
  traditional SEO might tolerate it.
- **Clone website Phase 2 is mandatory** — never generate code before presenting the analysis
  to the user and receiving confirmation.
- **One CTA per landing page** — every element must support the single conversion goal.
- **No lorem ipsum** in generated landing pages — always use realistic placeholder content.

