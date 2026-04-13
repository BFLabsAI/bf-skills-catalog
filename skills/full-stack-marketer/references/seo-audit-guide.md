# SEO Audit Guide

Full technical audit framework, on-page checklist, content quality assessment, and output
templates. Used by the SEO Specialist role.

Sources: seo-audit v1.1.0, seo-geo audit checklist, seo-aeo-best-practices technical-seo.md

---

## Priority Levels

| Level | Meaning | Action |
|---|---|---|
| P0 | Critical | Must fix immediately — blocks indexing or causes major issues |
| P1 | Important | Should fix soon — significant impact on rankings |
| P2 | Recommended | Nice to have — improves visibility and UX |

---

## Technical SEO Audit

### Crawlability (P0)

**Robots.txt**
- Allows all important pages
- No unintentional Disallow blocks
- References sitemap
- Allows key AI bots: GPTBot, PerplexityBot, ClaudeBot, Bingbot

**XML Sitemap**
- Exists and accessible at `/sitemap.xml`
- Submitted to Google Search Console and Bing Webmaster Tools
- Contains only canonical, indexable URLs
- Updated regularly; excludes noindex pages

**Site Architecture**
- Important pages within 3-4 clicks of homepage
- Logical hierarchy; no orphan pages
- Solid internal linking structure

**Crawl Budget (large sites only)**
- Parameterized URLs under control
- Faceted navigation handled (canonicals or noindex)
- No session IDs in URLs

### Indexation

**Index Status Checks**
- `site:domain.com` — compare indexed pages vs expected
- Google Search Console Coverage report — review all categories
- Check for noindex tags on important pages
- Verify canonicals point in the correct direction

**Canonicalization**
- All pages have canonical tags (self-referencing on unique pages)
- HTTP → HTTPS canonicals in place
- www vs. non-www consistency enforced
- Trailing slash consistency enforced
- Redirect chains/loops resolved

### Site Speed & Core Web Vitals

| Metric | Target | Tool |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | PageSpeed Insights |
| INP (Interaction to Next Paint) | < 200ms | PageSpeed Insights |
| CLS (Cumulative Layout Shift) | < 0.1 | PageSpeed Insights |
| TTFB (Time to First Byte) | < 800ms | WebPageTest |

**Speed factors to check:** image optimization (WebP, lazy loading), JavaScript execution,
CSS delivery, caching headers, CDN usage, font loading (use `display: swap`).

**Next.js specific:** Use `next/image` with Sanity URL builder, serve WebP/AVIF, implement LQIP
blur placeholders. Use `next/font/google` to prevent layout shift.

### Mobile-Friendliness (P0)

- Responsive design (not a separate m. subdomain)
- Same content as desktop (mobile-first indexing)
- Viewport meta tag configured
- Tap target sizes adequate
- No horizontal scroll

### Security & HTTPS (P0)

- HTTPS across the entire site
- Valid SSL certificate
- HTTP → HTTPS redirects
- No mixed content
- HSTS header (recommended)

### URL Structure

- Readable, descriptive URLs
- Lowercase, hyphen-separated
- Keywords in URLs where natural
- No unnecessary parameters
- Consistent structure across site

---

## On-Page SEO Audit

### Title Tags (P0)

**Good title:** Unique, primary keyword near beginning, 50-60 characters, compelling.

**Common issues:** Duplicate titles, too long (truncated in SERPs), too short, keyword stuffing,
missing entirely.

### Meta Descriptions (P1)

**Good description:** Unique per page, 150-160 characters, includes primary keyword, clear
value proposition, call to action.

**Common issues:** Duplicate descriptions, auto-generated content, no compelling reason to click.

### Open Graph & Twitter Cards (P2)

```html
<meta property="og:title" content="{Title}">
<meta property="og:description" content="{Description, 150-160 chars}">
<meta property="og:image" content="{URL, 1200x630}">
<meta property="og:url" content="{Canonical URL}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Title}">
<meta name="twitter:description" content="{Description}">
<meta name="twitter:image" content="{URL}">
```

### Heading Structure (P0)

- One H1 per page containing the primary keyword
- Logical hierarchy: H1 → H2 → H3 (never skip levels)
- Headings describe content, not used for styling only

### Content Optimization (P1)

- Primary keyword in first 100 words
- Related keywords used naturally
- Sufficient depth/length for topic
- Content answers the search intent
- Content is better than top-ranking competitors for the query

**Thin content triggers:** Pages with little unique value, tag/category pages with no editorial
content, doorway pages, duplicate or near-duplicate content.

### Image Optimization (P1-P2)

- Descriptive file names (not img001.jpg)
- Alt text on all images; alt text describes the image
- Compressed file sizes; modern formats (WebP)
- Lazy loading implemented
- Responsive images with correct dimensions

### Internal Linking (P1)

- Important pages are well-linked from other pages
- Descriptive anchor text (not "click here")
- Logical link relationships
- No broken internal links
- No orphan pages (every page has at least one internal link in)

### Keyword Targeting (P1)

Per page: clear primary keyword, title/H1/URL aligned, content satisfies search intent.
Site-wide: keyword mapping document, no cannibalization (two pages targeting the same keyword),
logical topical clusters.

---

## E-E-A-T Assessment (P1)

### Experience
- First-hand experience demonstrated
- Original insights, data, and case studies
- Real examples — not just theory

### Expertise
- Author credentials visible (bio, credentials section)
- Accurate, detailed information
- Properly sourced claims with links to primary sources

### Authoritativeness
- Recognized in the space; cited by other publications
- Industry credentials and recognitions listed

### Trustworthiness
- Accurate information; transparent about the business
- Contact information visible
- Privacy policy and terms pages present
- HTTPS enabled
- Publication and update dates displayed

### Implementation (Sanity CMS example)

```typescript
// Author with EEAT signals
defineType({
  name: 'author',
  fields: [
    defineField({ name: 'name', type: 'string' }),
    defineField({ name: 'role', type: 'string' }),
    defineField({ name: 'bio', type: 'text' }),
    defineField({ name: 'credentials', type: 'array', of: [{ type: 'string' }] }),
    defineField({ name: 'image', type: 'image' }),
    defineField({ name: 'sameAs', type: 'array', of: [{ type: 'url' }],
      description: 'Canonical profile URLs for schema.org Person (LinkedIn, Twitter, etc.)'
    }),
  ]
})

// Content with EEAT metadata
defineType({
  name: 'post',
  fields: [
    defineField({ name: 'author', type: 'reference', to: [{ type: 'author' }] }),
    defineField({ name: 'publishedAt', type: 'datetime' }),
    defineField({ name: 'updatedAt', type: 'datetime' }),
    defineField({ name: 'reviewedBy', type: 'reference', to: [{ type: 'author' }] }),
    defineField({ name: 'sources', type: 'array', of: [{ type: 'url' }] }),
  ]
})
```

**YMYL topics** (health, finance, legal, safety) require extra E-E-A-T: professional review,
certifications, clear disclaimers.

---

## Common Issues by Site Type

### SaaS / Product Sites
- Product pages lack content depth
- Blog not internally linked from product pages
- Missing comparison/alternative pages
- Feature pages thin on content
- No glossary or educational content

### E-commerce
- Thin category pages
- Duplicate product descriptions from manufacturer
- Missing Product schema
- Faceted navigation creating thousands of duplicate URLs
- Out-of-stock pages mishandled (should return 404 or redirect, not soft-404)

### Content / Blog Sites
- Outdated content not refreshed
- Keyword cannibalization across posts
- No topical clustering
- Poor internal linking between related posts
- Missing author pages

### Local Business
- Inconsistent NAP (Name, Address, Phone) across directories
- Missing LocalBusiness schema
- No Google Business Profile optimization
- Missing location-specific pages
- No local content (city/neighborhood-specific articles)

---

## Audit Report Structure

```
EXECUTIVE SUMMARY
- Overall health: [Good / Needs Work / Critical Issues]
- Top 3-5 priority issues (brief, action-oriented)
- Quick wins identified

TECHNICAL SEO FINDINGS
Issue: [what's wrong]
Impact: [High / Medium / Low]
Evidence: [how found / URL]
Fix: [specific recommendation]
Priority: [P0 / P1 / P2]

ON-PAGE FINDINGS
[same format]

CONTENT FINDINGS
[same format]

PRIORITIZED ACTION PLAN
P0: Critical fixes (blocking indexation or ranking)
P1: High-impact improvements
P2: Quick wins and long-term recommendations
```

---

## Quick Audit Commands

```bash
# Check meta tags and basic on-page elements
curl -sL "https://example.com" | grep -E "<title>|<meta name=\"description\"|<meta property=\"og:|<h1"

# Check robots.txt
curl -s "https://example.com/robots.txt"

# Check sitemap
curl -s "https://example.com/sitemap.xml" | head -50

# Check HTTP headers and redirect chain
curl -sIL "https://example.com" | grep -E "HTTP|Location|X-Robots"

# Check load time
curl -o /dev/null -s -w "Total: %{time_total}s\n" "https://example.com"

# Check page size
curl -sL "https://example.com" | wc -c
```

**Schema detection — do NOT use curl:** Use browser tool or Google Rich Results Test.
`curl` and `web_fetch` strip `<script>` tags and miss all JS-injected JSON-LD.

```bash
# Open Google Rich Results Test for schema validation
open "https://search.google.com/test/rich-results?url=YOUR_URL"

# Open Schema.org Validator
open "https://validator.schema.org/?url=YOUR_URL"

# Check Google indexing
open "https://www.google.com/search?q=site:yourdomain.com"

# Check Bing indexing
open "https://www.bing.com/search?q=site:yourdomain.com"
```

---

## Next.js / Sanity Implementation Patterns

### generateMetadata (metadata, OG, robots, canonical)

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { data } = await sanityFetch({ query: PAGE_QUERY, stega: false }) // No stega in metadata
  return {
    title: data.seo?.title || data.title,
    description: data.seo?.description,
    openGraph: {
      images: data.seo?.image ? [{
        url: urlFor(data.seo.image).width(1200).height(630).url(),
        width: 1200, height: 630,
      }] : [],
    },
    robots: data.seo?.noIndex ? 'noindex' : undefined,
    alternates: { canonical: `https://example.com/${params.slug}` },
  }
}
```

### Dynamic Sitemap

```typescript
// app/sitemap.ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await client.fetch(`
    *[_type in ["page", "post"] && defined(slug.current) && seo.noIndex != true]{
      "url": select(
        _type == "page" => "/" + slug.current,
        _type == "post" => "/blog/" + slug.current
      ),
      _updatedAt
    }
  `)
  return pages.map(page => ({
    url: `https://example.com${page.url}`,
    lastModified: new Date(page._updatedAt),
  }))
}
```

### Canonical URL

```typescript
alternates: { canonical: `https://example.com/${params.slug}` }
```

### CMS-Managed Redirects

```typescript
// next.config.ts
async redirects() {
  const redirects = await client.fetch(`
    *[_type == "redirect" && isEnabled == true]{ source, destination, permanent }
  `)
  return redirects
}
```

### International SEO (hreflang)

```typescript
alternates: {
  canonical: `https://example.com/${lang}/${slug}`,
  languages: {
    'en': `https://example.com/en/${slug}`,
    'de': `https://example.com/de/${slug}`,
    'x-default': `https://example.com/en/${slug}`,
  },
}
```

---

## Official Tools Reference

| Tool | URL | Purpose |
|---|---|---|
| Google Search Console | search.google.com/search-console | Indexing data, Core Web Vitals, Coverage |
| Google Rich Results Test | search.google.com/test/rich-results | Schema validation (renders JS) |
| PageSpeed Insights | pagespeed.web.dev | Core Web Vitals, speed |
| Bing Webmaster Tools | bing.com/webmasters | Bing indexing and crawl data |
| Schema.org Validator | validator.schema.org | Schema validation |
| Screaming Frog | screamingfrog.co.uk | Full site crawl (free up to 500 URLs) |
| Ahrefs / Semrush | — | Backlinks, keyword research, AI Overview tracking |
