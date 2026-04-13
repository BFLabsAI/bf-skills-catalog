# Website Structure Planning Reference

Full page taxonomy, generic template structure, growth strategy mappings, and planning
workflow for the Content & Page Builder role's website structure sub-skill.

Source: website-structure/SKILL.md v1.5.0
Reference cited: Alignify SEO website structure guide (alignify.co)

---

## Generic Site Template Structure

Applicable to SaaS, tools, and content sites. Adapt by removing unused sections and
adding specific modules (industry, region, product variants).

| Section | Typical Paths | Notes |
|---|---|---|
| **Root** | /, /features, /pricing, /demo, /contact | Core marketing pages |
| **Tools** | /tools, /free-tools; hub + per-tool pages | Free tools for lead gen; often SPA; programmatic |
| **Resources** | /blog, /changelog, /glossary, /faq, /tutorials | Content for SEO and education |
| **Partnership** | /affiliate, /startups, /ambassadors | Conversion-specific landing pages |
| **Legal** | /terms, /privacy, /careers | Required pages |
| **Competitor** | /alternatives, /compare, /migrate | High-intent SEO pages |
| **Standalone** | /dashboard, /login, /signup, /docs, /api, /status, /support | Auth and product pages |

---

## Page Priority Framework

| Priority | Pages |
|---|---|
| **Must Have** | Home, Product/Features, Pricing, Blog, About, Privacy, Terms, Contact |
| **Great to Have** | Testimonials, FAQ, HTML Sitemap, 404, Refund/Returns |
| **Optional** | Search Results, News, Careers, Disclosure |
| **Traffic-driven** | Category/Collection pages (for content-heavy or e-commerce sites) |

**Pricing page placement:**
- Marketing site: `/pricing` in main nav for prospects
- In-app: Settings → Billing in sidebar for logged-in users
- Enterprise-only: "Contact sales" may replace a public pricing page

---

## Growth Strategy → URL Structure Mapping

Structure reflects growth strategy. Sub-directories signal growth channels:

| Goal | Path Example | Notes |
|---|---|---|
| Affiliate conversion | /affiliate | Conversion-focused landing page |
| Education/student plan | /education, /startups, /student-discount | Specific program pages |
| Multi-language | /zh-CN, /ja | Requires hreflang implementation |
| Community | /ambassadors, /showcase | Creator program pages |
| B2B / Enterprise | /solutions/[industry], /use-cases/[scenario], /customers | Solutions = capability-first; use-cases = scenario-first |
| Developer product | /api, /docs, /status | Technical audience pages |
| User feedback | /feedback, /roadmap | External: Canny, FeatureBase |
| Plugins/Integrations | /integrations, /plugins | Category + individual integration pages |
| Giveaway/Contest | /giveaway | Temporary campaign pages |

---

## Features vs. Use Cases (Important Distinction)

These are different pages serving different search intents:

| Type | URL pattern | Content angle | Example |
|---|---|---|---|
| Features | /features/[feature-name] | Capability-first — what the tool CAN do | /features/time-tracking |
| Use cases | /use-cases/[scenario] | Scenario-first — what problem it solves | /use-cases/remote-teams |

**Key rules:**
- Differentiate the content angle — don't duplicate
- Link between them (feature page → relevant use case; use case → relevant feature)
- Avoid overlap to prevent cannibalization

---

## Structure Principles

| Principle | Guideline |
|---|---|
| **Flat structure** | Max 4 clicks from homepage to any page — improves crawlability and link equity distribution |
| **Plan early** | Design structure before building pages; right after domain purchase |
| **Sitelinks** | Good structure + table of contents + authoritative internal links → natural sitelinks in SERP (cannot be forced) |
| **No orphan pages** | Every page needs at least one internal link pointing to it |
| **Clear navigation** | Clear hierarchy and nav improve task completion; users find what they need faster |

---

## Domain Architecture (Multiple Products)

**This skill covers page structure within a single domain.**

When planning across multiple products or brands:
- **Subfolder** (`example.com/product`) — shares domain authority; easier SEO; recommended default
- **Subdomain** (`product.example.com`) — treated as separate domain by Google; use for clearly
  distinct products or audiences
- **Independent domain** (`product.com`) — fully separate; requires building authority from scratch

Use the `domain-architecture` skill for detailed guidance on this decision.

---

## Planning Workflow (7 Steps)

1. **Choose template** — Start from the generic template above; adapt to website type
2. **Trim modules** — Remove irrelevant sections (no API → drop /api, /docs)
3. **Add specifics** — Industry pages, regional variants, product variants
4. **Assign URLs** — Per page; follow URL rules: lowercase, hyphens, short, keyword-rich
5. **Export list** — "Page type + URL + Priority" for development scheduling
6. **Match tech stack** — DNS, auth, CMS, status page, feedback tool per page type
7. **Iterate** — Expand with new features and markets; keep hierarchy clear

---

## URL Structure Rules

- Lowercase only: `/seo-audit` not `/SEOAudit`
- Hyphens to separate words: `/landing-page` not `/landing_page`
- Short and descriptive: `/pricing` not `/our-pricing-plans-and-tiers`
- Keyword-rich where natural: `/seo-audit-tool` is fine; keyword stuffing in URLs is not
- Consistent trailing slash decision (with or without) applied site-wide and enforced with canonicals

---

## Homepage Module Reference

Common homepage sections and what they do:

| Module | Purpose |
|---|---|
| Headline / H1 | Communicate value proposition; primary keyword |
| Subheadline | Expand on headline; secondary benefit |
| Primary CTA | Drive main conversion action |
| Social proof bar | Build immediate trust (logos, user counts, ratings) |
| Benefits / Features | Explain what the product does |
| How it works | Reduce friction by showing simplicity |
| Testimonials | Peer validation |
| Pricing preview | Reduce hesitation for self-serve products |
| Secondary CTA | Re-engage visitors who scrolled past primary CTA |
| Footer | Navigation, legal, contact, SEO links |

---

## Output Format (What to Deliver)

**Provide:**
1. **Page list** — with priority (Must Have / Great to Have / Optional)
2. **URL structure** — paths per section
3. **Website-type fit** — which pages apply given the site type
4. **Growth mapping** — which paths support which acquisition channels
5. **Next steps** — technical implementation (URL rules, sitemap, crawlability audit)
