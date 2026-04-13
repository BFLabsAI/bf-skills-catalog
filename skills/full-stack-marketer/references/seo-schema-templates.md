# JSON-LD Schema Templates

Ready-to-use JSON-LD structured data templates for SEO and GEO optimization.

Sources: seo-geo/references/schema-templates.md (primary),
seo-aeo-best-practices/references/structured-data.md (TypeScript patterns).

Schema with proper markup shows 30-40% higher AI visibility. FAQPage schema specifically
adds up to +40% AI citation rate.

---

## FAQPage (+40% AI Visibility)

**Best for:** FAQ sections, knowledge base pages, product pages with Q&A, any page with
common questions.

**JSON-LD (plain):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is [Your Product/Service]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Comprehensive answer with statistics. According to X, 85% of users report Y benefit."
      }
    },
    {
      "@type": "Question",
      "name": "How does [Product/Service] work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Step-by-step explanation. First, you... Then... Finally..."
      }
    }
  ]
}
```

**TypeScript (Next.js with schema-dts):**
```typescript
import { FAQPage, WithContext } from 'schema-dts'

const faqSchema: WithContext<FAQPage> = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.map(faq => ({
    "@type": "Question",
    name: faq.question,
    acceptedAnswer: {
      "@type": "Answer",
      text: faq.answer  // Plain text — use pt::text() in GROQ for Sanity portable text
    }
  }))
}
```

**GROQ for plain text from Sanity:**
```groq
*[_type == "faq"]{ question, "answer": pt::text(answerRichText) }
```

---

## Article / Blog Post

**Best for:** Blog posts, news articles, tutorials. Helps with author identification and
date signaling for freshness ranking.

**JSON-LD:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Article Title — Max 110 characters]",
  "description": "[Article summary]",
  "image": [
    "https://example.com/image-1x1.jpg",
    "https://example.com/image-4x3.jpg",
    "https://example.com/image-16x9.jpg"
  ],
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-12-20T10:30:00+00:00",
  "author": {
    "@type": "Person",
    "name": "[Author Name]",
    "url": "https://example.com/author/name",
    "jobTitle": "[Job Title]",
    "worksFor": { "@type": "Organization", "name": "[Company]" }
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher Name]",
    "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png", "width": 600, "height": 60 }
  },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://example.com/article-url" },
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "articleSection": "[Category]",
  "wordCount": 2500
}
```

**TypeScript:**
```typescript
import { Article, WithContext } from 'schema-dts'

const articleSchema: WithContext<Article> = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: post.title,
  description: post.excerpt,
  image: post.image?.url,
  datePublished: post.publishedAt,
  dateModified: post.updatedAt,
  author: { "@type": "Person", name: post.author.name, url: post.author.url },
  publisher: {
    "@type": "Organization",
    name: "Your Company",
    logo: { "@type": "ImageObject", url: "https://example.com/logo.png" }
  }
}
```

---

## WebPage

**Best for:** Standard content pages, landing pages.

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "[Page Title]",
  "description": "[150-160 character description]",
  "url": "https://example.com/page",
  "datePublished": "2024-01-15",
  "dateModified": "2024-12-20",
  "inLanguage": "en-US",
  "isPartOf": { "@type": "WebSite", "name": "[Site Name]", "url": "https://example.com" },
  "author": { "@type": "Person", "name": "[Author Name]", "url": "https://example.com/about" },
  "publisher": {
    "@type": "Organization",
    "name": "[Organization Name]",
    "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png" }
  },
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": ["h1", ".summary", ".key-points"]
  }
}
```

---

## HowTo

**Best for:** Tutorials, guides, how-to articles. Enables step extraction for process queries.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [Do Something]",
  "description": "[Brief description of what this guide covers]",
  "totalTime": "PT15M",
  "estimatedCost": { "@type": "MonetaryAmount", "currency": "USD", "value": "0" },
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step 1: [Step Name]",
      "text": "[Detailed step instructions]",
      "url": "https://example.com/guide#step1"
    },
    {
      "@type": "HowToStep",
      "name": "Step 2: [Step Name]",
      "text": "[Detailed step instructions]",
      "url": "https://example.com/guide#step2"
    }
  ]
}
```

---

## Product

**Best for:** E-commerce product pages, SaaS product pages.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "description": "[Product description]",
  "image": ["https://example.com/product-image-1.jpg"],
  "brand": { "@type": "Brand", "name": "[Brand Name]" },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "99.99",
    "availability": "https://schema.org/InStock",
    "seller": { "@type": "Organization", "name": "[Seller Name]" }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "89"
  }
}
```

**TypeScript:**
```typescript
import { Product, WithContext } from 'schema-dts'

const productSchema: WithContext<Product> = {
  "@context": "https://schema.org",
  "@type": "Product",
  name: product.name,
  description: product.description,
  image: product.images,
  offers: {
    "@type": "Offer",
    price: product.price,
    priceCurrency: "USD",
    availability: "https://schema.org/InStock"
  },
  aggregateRating: product.rating ? {
    "@type": "AggregateRating",
    ratingValue: product.rating.average,
    reviewCount: product.rating.count
  } : undefined
}
```

---

## SoftwareApplication

**Best for:** Tools, apps, SaaS products.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[App Name]",
  "description": "[App description]",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Cross-platform",
  "url": "https://example.com",
  "featureList": ["Feature 1 description", "Feature 2 description"],
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "150",
    "bestRating": "5"
  }
}
```

---

## Organization

**Best for:** About pages, company pages, homepage.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Organization Name]",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "[Organization description]",
  "contactPoint": { "@type": "ContactPoint", "contactType": "customer service", "email": "support@example.com" },
  "sameAs": [
    "https://twitter.com/example",
    "https://github.com/example",
    "https://linkedin.com/company/example"
  ]
}
```

**TypeScript:**
```typescript
import { Organization, WithContext } from 'schema-dts'

const orgSchema: WithContext<Organization> = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Your Company",
  url: "https://example.com",
  logo: "https://example.com/logo.png",
  sameAs: ["https://twitter.com/company", "https://linkedin.com/company/company"],
  contactPoint: { "@type": "ContactPoint", telephone: "+1-555-555-5555", contactType: "customer service" }
}
```

---

## LocalBusiness

**Best for:** Local business pages.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "telephone": "+1-555-555-5555",
  "email": "contact@example.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street Address]",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "postalCode": "[ZIP]",
    "addressCountry": "US"
  },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "09:00",
    "closes": "17:00"
  }],
  "priceRange": "$$"
}
```

---

## BreadcrumbList

**Best for:** All pages with navigation hierarchy.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com" },
    { "@type": "ListItem", "position": 2, "name": "[Category]", "item": "https://example.com/category" },
    { "@type": "ListItem", "position": 3, "name": "[Current Page]", "item": "https://example.com/category/page" }
  ]
}
```

**TypeScript:**
```typescript
import { BreadcrumbList, WithContext } from 'schema-dts'

const breadcrumbSchema: WithContext<BreadcrumbList> = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: breadcrumbs.map((crumb, index) => ({
    "@type": "ListItem",
    position: index + 1,  // schema.org positions are 1-based
    name: crumb.title,
    item: `https://example.com${crumb.path}`
  }))
}
```

---

## SpeakableSpecification (GEO Voice Enhancement)

**Best for:** Voice search optimization and AI extraction. Marks which CSS selectors contain
the most important, speakable content.

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "[Page Title]",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": ["h1", ".summary", ".key-takeaways", ".faq-answer"]
  }
}
```

---

## Combining Multiple Schemas (@graph)

Real-world pages often need multiple schema types. Use `@graph` to combine them. `@context`
is defined once at the top level — omit it from individual schemas inside `@graph`.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "name": "Product Name",
      "url": "https://example.com",
      "dateModified": "2024-12-20",
      "speakable": { "@type": "SpeakableSpecification", "cssSelector": ["h1", ".hero-description", ".faq-answer"] }
    },
    {
      "@type": "SoftwareApplication",
      "name": "Product Name",
      "applicationCategory": "DeveloperApplication",
      "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        { "@type": "Question", "name": "What is [Product]?", "acceptedAnswer": { "@type": "Answer", "text": "[Answer]" } }
      ]
    },
    { "@type": "Organization", "name": "Company Name", "url": "https://example.com" }
  ]
}
```

**Next.js rendering component:**
```typescript
// Note: only pass trusted data from your CMS. Strip HTML and escape if content
// could contain user-generated input before passing to JSON.stringify.
function JsonLd({ data }: { data: WithContext<Thing> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}

// Usage in page
export default function PostPage({ post }) {
  return (
    <>
      <JsonLd data={generateArticleSchema(post)} />
      <article>...</article>
    </>
  )
}
```

---

## Validation Tools

| Tool | URL | Notes |
|---|---|---|
| Google Rich Results Test | search.google.com/test/rich-results | Renders JavaScript — use for accuracy |
| Schema.org Validator | validator.schema.org | Full spec compliance check |
| Google Search Console | search.google.com/search-console | "Enhancements" tab for live schema issues |
