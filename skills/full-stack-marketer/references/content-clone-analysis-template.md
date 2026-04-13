# Website Clone Analysis Template

Use this template for Phase 2 of the clone-website workflow. Fill out ALL sections before
presenting to the user and asking for confirmation. Do not generate any code until the user
confirms.

Source: clone-website/references/analysis-template.md

---

## Website Analysis Report

**Source URL**: [url]
**Scrape Status**: Success / Partial (with notes) / Failed (with fallback used)

---

### Page Structure

**Sections Detected**:
- [ ] Header/Navigation
- [ ] Hero
- [ ] Features/Benefits
- [ ] Social Proof/Testimonials
- [ ] Pricing
- [ ] FAQ
- [ ] CTA
- [ ] Footer
- [ ] [Other — describe]

**Layout Pattern**: [single-column / two-column / grid / bento / asymmetric]
**Navigation Type**: [sticky / fixed / relative] + [hamburger mobile / full mobile nav]

---

### Design Tokens Extracted

**Colors**:
```css
--color-primary: #______;
--color-secondary: #______;
--color-accent: #______;
--color-background: #______;
--color-foreground: #______;
--color-muted: #______;
--color-border: #______;
```

**Typography**:
- Headings: [Font Family], weights: [400/500/600/700]
- Body: [Font Family], weights: [400/500]
- Scale: h1: [px], h2: [px], h3: [px], body: [px], small: [px]

**Spacing**:
- Base unit: [4px / 8px]
- Section gap: [px]
- Component gap: [px]
- Container max-width: [px]

**Border Radius**:
- Small: [px], Medium: [px], Large: [px]

---

### Component Breakdown

| # | Component | Description | Complexity |
|---|---|---|---|
| 1 | `Header.tsx` | [description] | Low/Med/High |
| 2 | `Hero.tsx` | [description] | Low/Med/High |
| 3 | `Features.tsx` | [description] | Low/Med/High |
| 4 | `[Section].tsx` | [description] | Low/Med/High |
| 5 | `Footer.tsx` | [description] | Low/Med/High |

---

### Images Inventory

| # | Source URL | Target Path | Status |
|---|---|---|---|
| 1 | [url] | `/public/images/hero-bg.jpg` | Will download |
| 2 | [url] | `/public/images/feature-1.png` | Fallback to Unsplash |
| 3 | N/A | `/public/images/avatar-1.jpg` | Using Unsplash |

---

### Proposed File Structure

```
app/
├── layout.tsx          # Root layout + metadata (title, OG, etc.)
├── page.tsx            # Main page composing all components
└── globals.css         # Design tokens as CSS variables

components/
└── landing/
    ├── Header.tsx
    ├── Hero.tsx
    ├── Features.tsx
    ├── [Other].tsx
    └── Footer.tsx

public/
└── images/
    ├── hero-bg.jpg
    └── [other images]
```

---

### Notes & Considerations

- [Any special patterns observed — animations, parallax, custom cursors]
- [Interactions to implement — hover states, scroll reveals, accordions]
- [Missing content that needs realistic placeholders]
- [Accessibility considerations]
- [Performance concerns — large images, heavy JS]

---

**Ready to proceed with code generation? (y/n)**

If modifications needed, specify:
- Sections to skip
- Components to combine or split
- Design token adjustments
- Image handling preferences
- Any sections to add that weren't in the original
