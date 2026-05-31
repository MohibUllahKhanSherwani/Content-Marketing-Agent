# Content Marketing Agent Team Project Plan

Last updated: 2026-05-31

## 1. What We Are Creating

We are creating a CrewAI-powered Content Marketing Agent Team for a full-stack digital marketing agency role posted by Roman Khaliq on Agent Talent.

The role asks for an AI content agent that can produce and manage multi-channel marketing output:

- 8-12 blog posts per month.
- Weekly email campaigns.
- Daily social posts.
- Ad copy variations.
- Landing-page copy.
- Case studies.
- Monthly performance analysis.
- Content calendar tracking.
- SEO, conversion, and brand voice consistency across formats.

This project should not be just a "content generator." It should behave like a small content marketing department with planning, production, editorial review, approval, publishing, and analytics loops.

## 2. Why We Are Creating It

The goal is to apply for and fulfill the Content Marketing Agent role with a credible production-grade agent team. The system should show that it can handle content volume, maintain quality, adapt tone from technical to conversational, support real channel workflows, and report performance against baseline.

The demo should be useful even before every platform API is approved. Azure OpenAI will run for real. External platforms will run in hybrid mode: real when credentials and permissions exist, mock otherwise.

## 3. Product Outcomes

The system succeeds when it can:

- Accept a client profile and campaign brief.
- Generate a monthly content calendar.
- Produce channel-specific content drafts.
- Run brand, SEO/AEO, conversion, compliance, and factuality checks.
- Queue content for human approval.
- Publish or draft to real platforms when available.
- Mock unavailable integrations without blocking the demo.
- Pull or simulate analytics.
- Produce a monthly performance report with recommendations.

## 4. Architecture

Use a modular monolith first. Keep service boundaries clear enough that connectors, crews, dashboard, and persistence can be split later if needed.

Main layers:

- **Flow Orchestrator:** CrewAI Flow classes coordinate monthly planning, production, QA, approval, distribution, and analytics.
- **Specialist Crews:** CrewAI Crews execute domain work with explicit agents and tasks.
- **Domain Core:** Pydantic/SQLModel models define content items, briefs, statuses, approvals, connectors, and metrics.
- **Connector Registry:** Platform connectors expose consistent methods and capability checks.
- **Persistence:** SQLite for demo and local development, PostgreSQL for production.
- **API and Dashboard:** FastAPI backend with a simple local dashboard for calendar, review queue, connector status, and analytics.
- **Observability:** structured logs, run IDs, token/cost counters, connector traces, and failure reasons.

## 5. CrewAI Design

Use CrewAI Flows as the top-level workflow because Flows hold state and control execution order. Use YAML for agent and task definitions where possible, with Python classes for connector injection and orchestration.

### Strategy Crew

Purpose: turn a client profile and campaign goal into a usable content strategy.

Agents:

- **Market Researcher:** gathers audience, competitor, and topical context.
- **SEO/AEO Strategist:** creates keyword, answer-engine, and citation-readiness guidance.
- **Campaign Planner:** turns goals into channel mix, funnel stages, offers, CTAs, and calendar slots.

Outputs:

- Campaign brief.
- Content calendar draft.
- Topic clusters.
- Keyword and question map.
- CTA and conversion hypothesis.

### Production Crew

Purpose: produce content across formats.

Agents:

- **Blog Writer:** long-form SEO/AEO blog drafts.
- **Email Copywriter:** weekly campaigns and sequences.
- **Social Copywriter:** LinkedIn, Facebook, Instagram variations.
- **Ad Copywriter:** headlines, primary text, descriptions, and CTA variants.
- **Landing Page Copywriter:** hero, sections, proof, objections, FAQ, and CTA.
- **Case Study Writer:** problem, solution, implementation, results, and customer narrative.

Outputs:

- Draft content items with metadata and target channel.
- Channel variations.
- Suggested images or creative briefs where needed.

### Quality Crew

Purpose: protect quality before human review.

Agents:

- **Managing Editor:** structure, clarity, completeness, and tone.
- **Brand Voice Reviewer:** matches brand voice profile and avoids banned claims.
- **SEO/AEO Reviewer:** checks title, slug, meta description, headings, query-fit, answer blocks, citations, and internal linking suggestions.
- **Conversion Reviewer:** checks CTA alignment, funnel stage, offer clarity, and persuasion.
- **Compliance/Factuality Reviewer:** flags claims that need evidence, citations, or human review.

Outputs:

- QA scorecard.
- Revision notes.
- Ready-for-review status or QA-failed status.

### Distribution Crew

Purpose: prepare approved content for platform-specific destinations.

Agents:

- **Calendar Scheduler:** maps content to dates and channel frequency.
- **Connector Operator:** sends drafts or publishes approved items through connectors.
- **Publication Auditor:** records platform IDs, URLs, errors, and retries.

Outputs:

- Draft or published platform records.
- Scheduling records.
- Connector audit trail.

### Analytics Crew

Purpose: measure performance and convert data into recommendations.

Agents:

- **Performance Analyst:** pulls GA4, WordPress, HubSpot, LinkedIn, and Meta metrics where available.
- **Baseline Analyst:** compares current performance against baseline.
- **Insights Writer:** creates monthly report and next-month recommendations.

Outputs:

- Performance snapshots.
- Monthly analytics report.
- Recommendations for topics, channels, CTAs, and content refreshes.

## 6. Core Workflows

### Monthly Planning Flow

1. Load client profile, brand voice, previous performance, and campaign objectives.
2. Strategy Crew creates topic clusters, content mix, and calendar.
3. Save calendar items as `IDEA` or `BRIEFED`.
4. Human can edit calendar before production.

### Content Production Flow

1. Select due items from the calendar.
2. Production Crew drafts channel-specific content.
3. Quality Crew reviews and either passes or sends revision notes.
4. Passed items move to `READY_FOR_REVIEW`.
5. Human approves, requests changes, or archives.

### Publishing Flow

1. Only `APPROVED` items can enter publishing.
2. Connector registry checks target capabilities.
3. Real connector runs if configured and allowed.
4. Mock connector runs if real credentials, plan, permissions, or access are missing.
5. Save platform IDs, URLs, scheduled timestamps, and error details.

### Analytics Flow

1. Pull real metrics where available.
2. Use mock metrics for unavailable connectors.
3. Normalize metrics into `PerformanceSnapshot`.
4. Compare against baseline.
5. Generate monthly report and next-month content recommendations.

## 7. Domain Model

Core statuses:

- `IDEA`
- `BRIEFED`
- `DRAFTED`
- `QA_FAILED`
- `READY_FOR_REVIEW`
- `APPROVED`
- `SCHEDULED`
- `PUBLISHED`
- `PUBLISH_FAILED`
- `ARCHIVED`

Core entities:

- **ClientProfile:** client name, industry, audience, offers, competitors, brand voice, banned claims, preferred CTAs.
- **BrandVoiceProfile:** tone, reading level, vocabulary, examples, avoid list, technical/conversational settings.
- **CampaignBrief:** objective, audience, funnel stage, channels, keywords, offer, CTA, due dates, success metrics.
- **ContentCalendar:** month-level plan containing content slots and channel cadence.
- **ContentItem:** one deliverable such as a blog post, email, social post, ad variant, landing page, or case study.
- **ApprovalDecision:** human approval, rejection, notes, and timestamp.
- **PlatformPublication:** connector result with platform ID, URL, status, and error details.
- **PerformanceSnapshot:** normalized metrics from real or mock analytics sources.
- **MonthlyReport:** summary, baseline comparison, lessons, and recommendations.

## 8. API Surface

Initial FastAPI endpoints:

- `GET /health`
- `GET /connectors`
- `POST /client-profiles`
- `GET /client-profiles/{id}`
- `POST /campaigns`
- `GET /campaigns/{id}`
- `POST /runs/monthly-plan`
- `POST /runs/produce-content`
- `POST /runs/monthly-analytics`
- `GET /calendar`
- `GET /content-items`
- `GET /content-items/{id}`
- `POST /content-items/{id}/approve`
- `POST /content-items/{id}/request-changes`
- `POST /content-items/{id}/publish`
- `GET /analytics/monthly-summary`

Dashboard views:

- Connector capability/status page.
- Monthly content calendar.
- Review queue.
- Content item detail and approval page.
- Publishing audit page.
- Analytics dashboard.

## 9. Integration Strategy

Use connector modes for every external service:

- `real`: require valid credentials and fail loudly if unavailable.
- `mock`: never call the external API; return realistic fake data.
- `auto`: use real only if credential and capability checks pass; otherwise use mock.

Default demo config:

- Azure OpenAI: `real`
- WordPress: `auto`
- HubSpot: `auto`
- LinkedIn: `auto`
- Meta: `auto`
- GA4: `auto`
- Search: `mock` unless a search API key exists

See `docs/INTEGRATIONS.md` for detailed API notes.

## 10. Cost And Access Strategy

Azure OpenAI credits should be enough for a demo if we control loops and use mini models for high-volume work.

Cost controls:

- Prefer `azure/gpt-4o-mini` for drafts, extraction, summarization, and routine QA.
- Use `azure/gpt-4o` only for high-value final review and strategy.
- Set per-run max iterations.
- Set max tokens per task.
- Track token usage and estimated cost per run.
- Cache research and brand context.
- Avoid web search unless required.

Non-LLM cost considerations:

- WordPress can be free if using an existing site or local/test site.
- HubSpot real marketing email publishing can require paid tiers or add-ons.
- LinkedIn/Meta API calls usually do not have direct API fees, but permissions/app review and ad spend can be blockers.
- GA4 reporting is read-only and quota-limited.
- Search tools such as Serper may require free credits or paid usage after the free allowance.

## 11. Testing Strategy

Unit tests:

- Domain model validation.
- Status transitions.
- Approval gate enforcement.
- Connector mode selection.
- Cost budget checks.
- Calendar volume rules.
- QA guardrail functions.

Mock connector tests:

- WordPress draft creation and publish blocked.
- HubSpot missing capability falls back to mock.
- LinkedIn missing org token falls back to mock.
- Meta app/permission missing falls back to mock.
- GA4 missing credentials falls back to mock analytics.

Crew/Flow tests:

- Monthly planning creates expected volume.
- Production moves items through draft and QA states.
- Publishing refuses non-approved items.
- Analytics report can run with mixed real/mock sources.

Manual acceptance demo:

- Configure Azure OpenAI.
- Run monthly plan.
- Generate at least one blog, one email, multiple social posts, one ad set, and one landing page.
- Approve a content item.
- Publish to mock or real draft connector.
- Show connector status page and monthly analytics report.

## 12. Implementation Phases

### Phase 1: Repo Scaffold And Domain Core

- Create CrewAI Python project with `uv`.
- Add domain models and database schema.
- Add connector interface and mock connectors.
- Add AGENTS/project docs and `.env.example`.

### Phase 2: CrewAI Workflow MVP

- Add Strategy, Production, Quality, Distribution, and Analytics crews.
- Add Flows for planning, production, publishing, and analytics.
- Use Azure OpenAI as the real LLM provider.
- Add token and cost logging.

### Phase 3: Dashboard Demo

- Add FastAPI endpoints.
- Add local dashboard for calendar, review queue, connector status, and analytics.
- Make demo runnable with only Azure OpenAI configured.

### Phase 4: Real Connectors

- WordPress drafts first.
- GA4 read-only analytics.
- HubSpot draft/create if account supports it.
- LinkedIn and Meta publishing after app/token/permission checks.

### Phase 5: Production Hardening

- PostgreSQL migration.
- Auth for dashboard.
- Background jobs.
- Retry and dead-letter handling.
- Deployment documentation.
- Integration sandbox tests.

