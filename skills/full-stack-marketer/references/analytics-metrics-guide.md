# Analytics Metrics Guide

Complete metrics reference for the Analytics Analyst role: formulas, benchmarks, App Store
Connect metric definitions, dashboard templates, and event tracking plan detail.

Source: app-analytics/SKILL.md v1.0.0

---

## App Store Connect Analytics

Available at no cost for all App Store apps.

| Metric | Definition | What It Tells You |
|---|---|---|
| Impressions | Times your app appeared in search or browse | Discoverability / visibility |
| Product Page Views | Users who visited your app's product page | Interest after discovery |
| App Units | First-time downloads | Acquisition volume |
| Conversion Rate | Product Page Views → Downloads | Product page effectiveness |
| Proceeds | Revenue after Apple's 30% (or 15%) cut | Actual revenue received |
| Sessions | App opens | Usage frequency |
| Active Devices | Unique devices using the app | Reach |
| Retention | Day 1, Day 7, Day 28 retention rates | Early engagement quality |
| Crash Rate | Crashes per session | Stability |

**Traffic sources in App Store Connect:**
- App Store Search
- App Store Browse
- Web Referral
- App Referral

---

## Acquisition Metrics

| Metric | Formula | What It Measures |
|---|---|---|
| **Impressions** | — | App's visibility in the App Store |
| **Tap-Through Rate (TTR)** | Taps ÷ Impressions | Icon + title effectiveness |
| **Conversion Rate** | Downloads ÷ Product Page Views | Product page effectiveness |
| **Cost Per Install (CPI)** | Ad Spend ÷ Installs | Paid UA cost efficiency |
| **Organic %** | Organic Installs ÷ Total Installs | Health of organic growth |

**Benchmarks:**
- TTR: 3-5% is typical; >7% is strong
- Conversion Rate: 25-35% is typical for a well-optimized product page
- CPI: varies heavily by category; gaming $1-5, productivity $3-10, finance $10-50+

---

## Engagement Metrics

| Metric | Formula | Target |
|---|---|---|
| **DAU** (Daily Active Users) | Unique users in a day | Depends on category |
| **MAU** (Monthly Active Users) | Unique users in a month | Depends on category |
| **DAU/MAU (Stickiness)** | DAU ÷ MAU | >20% is good; >50% is excellent |
| **Sessions per User** | Total Sessions ÷ DAU | Frequency of use |
| **Session Length** | Average time per session | Value delivered per visit |

---

## Retention Metrics

| Metric | Formula | Industry Benchmark |
|---|---|---|
| **Day 1 Retention** | Users on Day 1 ÷ Install Cohort | 25-40% |
| **Day 7 Retention** | Users on Day 7 ÷ Install Cohort | 10-20% |
| **Day 30 Retention** | Users on Day 30 ÷ Install Cohort | 5-10% |
| **Churn Rate** | Lost Users ÷ Start-of-Period Users | < 5% monthly for subscriptions |

**Retention by cohort** is more useful than aggregate retention — analyze by install source,
country, and subscription plan to identify which cohorts retain best.

---

## Revenue Metrics

| Metric | Formula | What It Means |
|---|---|---|
| **ARPU** | Revenue ÷ All Users (including free) | Average value per user |
| **ARPPU** | Revenue ÷ Paying Users only | Paying user value |
| **LTV** (Lifetime Value) | ARPU × Average User Lifetime | Total value of an acquired user |
| **Trial-to-Paid** | Paid Conversions ÷ Trial Starts | Paywall effectiveness |
| **MRR** (Monthly Recurring Revenue) | Sum of active monthly subscription revenue | Subscription health |
| **Churn Revenue** | Lost MRR ÷ MRR at Start of Period | Revenue retention rate |

**LTV : CPI ratio:** LTV should be at least 3× CPI for a sustainable paid UA channel.

---

## Analytics Stack

| Tool | Purpose | Cost | Priority |
|---|---|---|---|
| **App Store Connect** | Store metrics, downloads, conversion | Free | Must have |
| **Firebase Analytics** | In-app events, funnels, audiences | Free | Must have |
| **Mixpanel** | Product analytics, cohort analysis, funnels | Free tier | Recommended |
| **Amplitude** | Product analytics, behavioral analysis | Free tier | Alternative to Mixpanel |
| **RevenueCat** | Subscription analytics, paywall A/B testing | Free tier | Required if subscriptions |
| **Adjust / AppsFlyer** | Attribution, UA campaign measurement | Paid | Required if running paid ads |
| **Crashlytics** | Crash reporting, stability monitoring | Free | Must have |

---

## Core Event Tracking Plan

Minimum viable tracking plan. Expand with app-specific events.

### Onboarding
```
onboarding_started
onboarding_step_completed (properties: step_name, step_number)
onboarding_completed
onboarding_skipped
```

### Core Actions
```
[primary_action]_started
[primary_action]_completed
[primary_action]_failed (properties: error_type)
```

### Monetization
```
paywall_viewed (properties: source, variant)
trial_started (properties: plan, source)
purchase_completed (properties: plan, price, source)
purchase_failed (properties: error_type)
subscription_renewed
subscription_cancelled (properties: reason)
```

### Engagement
```
session_started (properties: source)
feature_used (properties: feature_name)
content_viewed (properties: content_type, content_id)
share_tapped (properties: content_type)
notification_received (properties: type)
notification_tapped (properties: type)
```

### Settings
```
settings_changed (properties: setting_name, old_value, new_value)
notification_permission (properties: granted: boolean)
```

---

## Event Naming Conventions

- Use `snake_case` throughout
- Format: `[object]_[action]` (e.g., `photo_saved`, `workout_completed`)
- Be specific but not too granular (don't create an event for every pixel moved)
- Include relevant properties but never include PII (personal identifiable information)
- Keep naming consistent across iOS and Android platforms

**Good examples:** `paywall_viewed`, `purchase_completed`, `onboarding_step_completed`
**Avoid:** `event1`, `button_click` (too vague), `john_doe_purchased` (PII)

---

## Dashboard Templates

### Executive Dashboard (check weekly)

```
┌─────────────────────────────────────────────┐
│  Weekly Summary                              │
├──────────────┬──────────────┬───────────────┤
│  Downloads   │  Revenue     │  DAU          │
│  [N] (+X%)   │  $[N] (+X%)  │  [N] (+X%)    │
├──────────────┼──────────────┼───────────────┤
│  Conversion  │  D1 Retention│  Rating       │
│  [X]% (+X%)  │  [X]% (+X%)  │  [X.X] ★      │
└──────────────┴──────────────┴───────────────┘
```

Track week-over-week % change for each metric.

### Funnel Dashboard (check daily)

```
Impressions → Page Views → Downloads → Activation → Purchase
   [N]          [N]          [N]          [N]          [N]
        [X]%         [X]%         [X]%          [X]%
```

Any conversion rate below category average is a priority optimization target.

### Cohort Dashboard (check monthly)

Retention curves broken down by:
- Install date cohort (weekly or monthly)
- Acquisition source (organic, paid, referral)
- Country or region
- Subscription plan (free, trial, paid)

---

## Analytics Audit Output Format

```
Current State:
- Tools in use: [list]
- Events tracked: [N total — list key ones]
- Key gaps: [missing events or metrics]
- Data quality issues: [if any]

Recommendations:
1. [highest priority tracking gap to fill]
2. [metric to start monitoring]
3. [dashboard to create or improve]
4. [attribution issue to resolve]
```

---

## Tracking Plan Template

When building or auditing a tracking plan, document each event:

| Event Name | When It Fires | Properties | Tool | Priority |
|---|---|---|---|---|
| `onboarding_started` | User begins onboarding | — | Firebase, Mixpanel | P0 |
| `paywall_viewed` | Paywall screen appears | source, variant | Firebase, RevenueCat | P0 |
| `purchase_completed` | Successful payment | plan, price, source | Firebase, RevenueCat, Adjust | P0 |

---

## Metric Interpretation Guidelines

When the user shares actual data, provide:
1. **Benchmark comparison** — how their metrics compare to industry standards above
2. **Trend analysis** — is the metric improving, declining, or flat? What's the rate of change?
3. **Correlation** — what other metrics moved at the same time? (e.g., retention drop + new
   feature launch = investigate the feature)
4. **Specific actions** — 2-3 concrete next steps based on the data, not generic advice
