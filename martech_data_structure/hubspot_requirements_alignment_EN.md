# HubSpot Alignment Requirements (Marketing Hub + Content Hub)

## Goals and Scope
This document aligns the team on HubSpot implementation scope and functional requirements. HubSpot is confirmed as the core data integration platform. The focus covers Marketing Hub and Content Hub capabilities, ensuring 6 Core Seats can support key business scenarios.

## Assumptions
- Account plan: 6 Core Seats.
- Scope: Marketing Hub + Content Hub (including HubSpot Breeze AI).
- Data integration: HubSpot is the primary data integration entry point.

## Functional Requirements (Must be Native)

### 1. Advanced Email Automation & Workflows
To support events and campaigns, requirements include:
- Behavior-Based Triggers: Automated emails triggered by specific website actions, form submissions, or event registrations.
- Drip Campaigns & Nurture Sequences: Multi-step email journeys designed to move leads through the funnel (Lead → MQL → SQL) without manual intervention.
- Personalization & Tokens: Using customer data to tailor email content dynamically for higher engagement. (Eg: Focus in Industry or job title)
- Automated Internal Notifications: Alerting the team the moment a lead hits a specific "SQL" threshold.

### 2. Social Media Management & Tracking
We need to centralize our social strategy within HubSpot. This must include:
- Multi-channel Publishing & Monitoring: Management of our LinkedIn and YouTube accounts.
- Social Attribution: The ability to track how social media interactions (clicks and engagements) contribute to lead generation and closed-won revenue.

### 3. Full-Funnel Tracking & ROI
We require a dashboard that moves beyond surface-level metrics to show true Marketing ROI:
- Funnel Velocity: Reporting on the time it takes for a lead to progress to MQL and SQL.
- Closed-Loop Reporting: Linking specific event spends and digital campaigns to generated revenue.
- Website Analytics: Integrating site performance data directly into our ROI reports.
- Derived Metrics: Dashboards must support secondary/derived calculations based on raw metrics (e.g., CVR, LTV/CAC, funnel velocity).

### 4. HubSpot Breeze & Content Hub
Using Breeze AI for content "remixing" and lead intelligence (Need check if there is any additional cost):
- Breeze Content Remix: Rewrite, expand, and repurpose existing content for multi-channel outputs.
- Breeze Lead Intelligence: Assist lead scoring and identify high-intent contacts.
- Cost Confirmation: Verify if Breeze AI requires additional fees or add-on packages.

### 5. Content Hub / CMS
Ensure content production, website hosting, and form conversion are closed-loop:
- Content Management: Pages/blogs/landing pages with version control.
- Forms & Conversion: Form fields, progressive profiling, hidden fields for source capture.
- A/B Testing: Page or email experiments with statistical results.
- SEO & Content Optimization: SEO keywords, metadata, readability, and structure guidance.
- Multi-language & Localization: Regional content management and publishing workflows.

### 6. Lifecycle & CRM Alignment
Ensure sales collaboration and lifecycle execution:
- Lifecycle Stages: Lead / MQL / SQL / Opportunity / Customer with standard definitions and change rules.
- Lead Scoring: Behavioral + firmographic scoring with workflow/segment integration.
- Segmentation & Lists: Dynamic/static lists and segmentation rules.
- SLA & Follow-up: MQL → SQL follow-up timing with escalation alerts.

### 7. Paid Media / Ads Integration
Ad data must be tied to conversion and revenue:
- Ad Platform Connections: Connect major ad platforms and sync spend + conversions.
- Ad Attribution: Channel-level ROI attribution for paid media.
- Audience Sync: Push HubSpot segments to ad audiences.

### 8. Events & Campaigns
Support online/offline event data capture:
- Registration & Attendance: Integrate event platforms/forms and record status.
- Event Attribution: Attribute MQL/SQL and revenue impact to events.
- Offline Business Card Import: Batch import with field mapping.

### 9. Compliance & Governance
Ensure data compliance and quality:
- Consent Management: Privacy compliance, subscription preferences, opt-out, audit trails.
- Data Quality: Duplicate detection, field validation, required rules.
- Access Control: Role permissions, field-level visibility, approvals.

## Implementation Support Needs (HubSpot / Oxygen)
- Workflow Architecture: Build automation logic to prevent overlaps and conflicts.
- Lead Scoring & Funnel Definition: Define triggers and thresholds for MQL → SQL.
- Attribution Modeling: Ensure dashboards correctly attribute ROI by channel (Email vs. Social vs. Organic).

## Data Integration & Source Tracking
HubSpot as the core integration platform must cover historical and future data sources:
- Regional Customer Data: Integrate customer data from Angela (by region).
- Historical Website Data: Integrate visitor/customer data from Jessie (legacy sites).
- Future Data Sources: Support campaign/event business cards and offline sources.
- Webflow Forms Integration: Sync Webflow site forms into HubSpot.
- Source Tagging: Mark user sources (Organic / Ads / Referral).
- Link Tracking: Support multiple links for traffic source tracking (short links or UTM).
- Bitly Integration: Connect Bitly for short link generation and click tracking.

## Data Dictionary & Field Alignment
- Field Mapping: Source fields → HubSpot fields (including required fields).
- Standardization Rules: Names, enums, date formats, country/region normalization.
- Deduplication & Primary Keys: Unique IDs and deduping logic.
- Event & Campaign Fields: Unified definitions for events, campaigns, offline cards.
- Attribution Fields: UTM / referrer / source / medium definitions and write rules.

## Research Alignment Notes
- Unified Event Model: Website behavior, forms, events, ad clicks should share a consistent event taxonomy.
- Cross-Channel Attribution: Email / Social / Ads / Organic must be comparable and attributable.
- Extensible Integration: New sites and campaigns should be low-cost to integrate.
- Data Traceability: Core metrics must be traceable to source events.

## Funnel Stages & Metrics Framework
Funnel stages: Awareness → Consideration → Lead Generation.

### Channel Metrics (Merged Table)
Note: If metrics come from external platforms, they must sync into HubSpot or the data warehouse and align with source fields.

| Channel | Metric | Funnel Stage | Definition / Goal | Why Important | Recommended Frequency | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| LinkedIn (Organic) | Impressions | Awareness | Times posts were shown | Raw visibility of organic content | Weekly/Monthly | - |
| LinkedIn (Organic) | Engagement rate | Consideration | Likes/comments/shares rate | Content quality and resonance | Weekly/Monthly | - |
| LinkedIn (Organic) | Clicks (post→link) | Consideration | Post-to-link clicks | Traffic driving ability | Weekly/Monthly | - |
| LinkedIn (Organic) | Followers / Followers Growth | Consideration | Followers and growth | Brand growth | Monthly | - |
| LinkedIn (Organic) | Shares | Awareness/Consideration | Share count | Content amplification | Weekly/Monthly | - |
| LinkedIn (Paid) | Impressions | Awareness | Ad impressions | Paid reach | Weekly/Monthly | - |
| LinkedIn (Paid) | CTR | Consideration | Click-through rate | Creative effectiveness | Weekly/Monthly | - |
| LinkedIn (Paid) | CPL | Lead gen | Cost per lead | Acquisition efficiency | Weekly/Monthly | - |
| LinkedIn (Paid) | Leads | Lead gen | Ad leads | Lead output | Weekly/Monthly | - |
| LinkedIn (Paid) | Ads spend (total) | N/A | Total spend | Cost control | Weekly/Monthly | - |
| YouTube | Impressions | Awareness | Impressions | Reach scale | Monthly | - |
| YouTube | Video views | Awareness/Consideration | Views | Content appeal | Monthly | - |
| YouTube | Avg. video duration / Watch time | Consideration | Avg watch time | Content depth | Monthly | - |
| YouTube | Subscribers | Consideration | Subscribers | Brand retention | Monthly | - |
| YouTube | Traffic to Website / CTA clicks | Consideration | Site traffic / CTA clicks | Conversion precursor | Monthly | - |
| EDM | Deliverability rate | Awareness | Deliverability | Baseline reachability | Weekly/Monthly | - |
| EDM | Open rate | Awareness/Consideration | Open rate | Subject/content pull | Weekly/Monthly | - |
| EDM | CTR | Consideration | Click-through rate | Traffic driving ability | Weekly/Monthly | - |
| EDM | Subscribers | Consideration | Subscribers | Owned audience growth | Monthly | - |
| EDM | Conversion rate (email → goal) | Lead gen | Email-to-goal conversion | Lead output | Weekly/Monthly | - |
| Google Ads | Total impressions | Awareness | Impressions | Reach | Weekly/Monthly | - |
| Google Ads | Total clicks | Consideration | Clicks | Traffic | Weekly/Monthly | - |
| Google Ads | CTR | Consideration | Click-through rate | Creative quality | Weekly/Monthly | - |
| Google Ads | CPA | Lead gen | Cost per acquisition | Efficiency | Weekly/Monthly | - |
| Google Ads | Leads | Lead gen | Leads | Output | Weekly/Monthly | - |
| Google Ads | Conversion rate | Lead gen | Conversion rate | Effectiveness | Weekly/Monthly | - |
| Google Ads | Ads spend (total) | N/A | Total spend | Cost control | Weekly/Monthly | - |
| Website (GA4) | Users | Awareness | Unique visitors | Traffic baseline | Weekly/Monthly | - |
| Website (GA4) | Sessions | Awareness/Consideration | Sessions | Traffic volume | Weekly/Monthly | - |
| Website (GA4) | Engagement Rate | Consideration | Engagement rate | Content stickiness | Weekly/Monthly | - |
| Website (GA4) | Pageviews | Consideration | Pageviews | Content consumption | Weekly/Monthly | - |
| Website (GA4) | Avg. session duration | Consideration | Avg session duration | Content quality | Weekly/Monthly | - |
| Website (GA4) | Bounce rate | Consideration | Bounce rate | Page relevance | Weekly/Monthly | - |
| Website (GA4) | Conversion / Key Events | Lead gen | Form submits, inquiry clicks | Lead output | Weekly/Monthly | - |
| Website (GA4) | By-source metrics | N/A | Source breakdown | Channel attribution | Weekly/Monthly | - |
| Events | Registration (Google Form) | Lead gen | Event registrations | Event lead flow | Per event | - |

### Tracking Implementation Requirements
- Unified URL Generation: Need to check in with Angela, Jessie, and Judy about the URL links generation and attribution parameter strategy (short links/UTM).
- Source Layering: Define Channel / Source / Medium / Campaign naming and write rules.
- Metric Landing: Align the above metrics into HubSpot reports or data warehouse dashboards with support for derived metrics.

## Open Items
- Breeze AI pricing, tiers, and add-on costs.
- Content Hub module scope and permissions for 6 Core Seats.
