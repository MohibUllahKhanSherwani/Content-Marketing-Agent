# Ubiquitous Language

## Business Context

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Content Marketing Agent Team** | The CrewAI system that plans, creates, reviews, distributes, and analyzes multi-channel marketing content. | Content bot, writer bot |
| **Agency Client** | The business whose brand, offers, and channels the system creates content for. | Account, customer |
| **Campaign** | A coordinated marketing effort with a goal, audience, channels, schedule, and success metrics. | Project, push |
| **Baseline** | The current or historical performance level used to compare future engagement and conversion results. | Starting point, benchmark |

## Planning

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Client Profile** | A structured record of the agency client's brand, audience, offers, competitors, voice, and constraints. | Brand doc, account profile |
| **Brand Voice Profile** | The rules and examples that define how the agency client should sound across content formats. | Tone guide, voice doc |
| **Campaign Brief** | The approved planning input for a campaign, including goal, audience, offer, CTA, channels, and constraints. | Creative brief, content brief |
| **Content Calendar** | The scheduled plan of content items across channels and dates. | Editorial calendar, posting schedule |
| **Content Slot** | A planned place in the calendar for a specific format, channel, and publish date. | Calendar item, slot |
| **Topic Cluster** | A group of related topics and keywords around a campaign theme. | Content pillar, keyword group |

## Content

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Content Item** | A single deliverable such as a blog post, email, social post, ad variant, landing page, or case study. | Asset, piece |
| **Blog Post** | A long-form article intended for organic search, AI search, and audience education. | Article |
| **Email Campaign** | A marketing email or sequence intended for a segment, offer, and CTA. | Newsletter, email blast |
| **Social Post** | A channel-specific short-form post for LinkedIn, Facebook, Instagram, or another social platform. | Caption, update |
| **Ad Variant** | One version of paid media copy with headline, primary text, description, and CTA. | Ad copy, creative variant |
| **Landing Page Copy** | Conversion-focused page copy with hero, proof, objections, FAQ, and CTA sections. | Sales page copy |
| **Case Study** | A proof asset showing problem, solution, implementation, and results. | Customer story |
| **CTA** | The action the audience should take after consuming the content. | Button text, ask |

## Quality And Review

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Quality Gate** | Automated review that checks brand, SEO/AEO, conversion, compliance, and factuality before human review. | QA check, review step |
| **Approval Gate** | The human decision point required before real scheduling or publishing. | Sign-off, approval step |
| **Review Queue** | The list of content items waiting for human approval or change requests. | Approval inbox |
| **Revision Note** | A specific instruction explaining what must change before approval. | Feedback, edit |
| **Banned Claim** | A claim the system must not make because it is unsupported, illegal, off-brand, or risky. | Forbidden claim |

## Distribution And Analytics

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Platform Connector** | A real or mock integration that creates drafts, publishes content, or retrieves metrics for an external platform. | API adapter, integration |
| **Connector Mode** | The runtime setting that chooses `real`, `mock`, or `auto` behavior for a platform connector. | Integration mode |
| **Real Connector** | A connector that calls an external platform API with actual credentials. | Live connector |
| **Mock Connector** | A connector that simulates an external platform without making API calls. | Fake connector, stub |
| **Auto Connector** | A connector mode that uses real behavior when credentials and permissions pass, otherwise mock behavior. | Hybrid connector |
| **Platform Publication** | The record of an item being drafted, scheduled, or published to a platform. | Published asset, external record |
| **Performance Snapshot** | A normalized set of metrics captured for a content item, channel, or campaign. | Metrics record, analytics row |
| **Monthly Report** | The analytics summary comparing performance against baseline and recommending next actions. | Performance report |

## Relationships

- An **Agency Client** has one or more **Client Profiles** over time.
- A **Client Profile** owns one current **Brand Voice Profile**.
- A **Campaign** is created from one **Campaign Brief**.
- A **Campaign** has one **Content Calendar**.
- A **Content Calendar** contains many **Content Slots**.
- A **Content Slot** produces one or more **Content Items**.
- A **Content Item** must pass a **Quality Gate** before entering the **Review Queue**.
- A **Content Item** must pass the **Approval Gate** before any real **Platform Publication**.
- A **Platform Connector** can create many **Platform Publications**.
- A **Platform Publication** can produce many **Performance Snapshots**.
- A **Monthly Report** summarizes many **Performance Snapshots** against the **Baseline**.

## Example Dialogue

> **Dev:** "When a **Content Item** passes the **Quality Gate**, can the **Platform Connector** publish it?"
>
> **Domain expert:** "No. Passing QA only moves it into the **Review Queue**. A human still needs to pass the **Approval Gate**."
>
> **Dev:** "So in demo mode, if HubSpot is not available, do we fail the **Email Campaign**?"
>
> **Domain expert:** "No. The HubSpot **Platform Connector** should run in **Auto Connector** mode and fall back to a **Mock Connector**."
>
> **Dev:** "And the **Monthly Report** should mix real GA4 data with mock HubSpot data if only GA4 is configured?"
>
> **Domain expert:** "Exactly. Every **Performance Snapshot** should show whether it came from a real or mock source."

## Flagged Ambiguities

- "Agent" can mean the whole **Content Marketing Agent Team** or one CrewAI specialist. Use **Content Marketing Agent Team** for the full product and "CrewAI agent" only for individual specialists.
- "Content brief" and "Campaign Brief" overlap. Use **Campaign Brief** for the strategic input that drives a campaign.
- "Publish" can mean create a draft, schedule, or make public. Use **create draft**, **schedule**, and **publish** as separate operations.
- "Real integration" can imply real publishing. Use **Real Connector** for API access, and require the **Approval Gate** plus `ALLOW_REAL_PUBLISH=true` for public publishing.

