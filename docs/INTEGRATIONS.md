# Integrations And API Strategy

Last updated: 2026-05-31

## Guiding Rule

Use real integrations wherever credentials, permissions, and account capabilities are available. Use mocks everywhere else. The demo must not be blocked by HubSpot plan limits, Meta app review, LinkedIn access tiers, or missing GA4 credentials.

All connectors implement the same broad shape:

- `check_capabilities()`
- `create_draft(content_item)`
- `schedule(content_item)`
- `publish(content_item)`
- `fetch_metrics(query)`
- `healthcheck()`

Each connector returns:

- `mode`: `real` or `mock`
- `capabilities`: what the connector can do now
- `platform_id`: external ID or realistic mock ID
- `platform_url`: external URL or realistic mock URL
- `status`
- `error_code`
- `human_message`
- `raw_response` for audit/debug when safe

## Connector Modes

### `real`

Use external API. Credentials and capability checks must pass. Fail loudly if the connector cannot perform the requested operation.

### `mock`

Never call external API. Return realistic data and simulated metrics.

### `auto`

Attempt real capability checks. Use real if available; otherwise use mock and record why the fallback happened.

## Azure OpenAI

Purpose:

- Real LLM generation and review.
- Strategy, drafting, QA, analytics explanation, and report generation.

Package:

- Use CrewAI native Azure support.
- Prefer `crewai[azure]` or the current CrewAI provider extra required by the installed version.

Environment:

- `AZURE_API_KEY`
- `AZURE_ENDPOINT`
- `AZURE_API_VERSION`
- `CONTENT_AGENT_MODEL=azure/gpt-4o-mini`
- `CONTENT_AGENT_REVIEW_MODEL=azure/gpt-4o`

Model routing:

- `gpt-4o-mini`: high-volume drafting, summarization, extraction, routine QA, mock data generation.
- `gpt-4o`: final quality review, strategic reasoning, sensitive claim review, proposal polish.

Controls:

- Max iterations per crew.
- Max tokens per task.
- Monthly budget.
- Token usage logging.
- Retry limit and timeout.

Relevant docs:

- https://docs.crewai.com/en/concepts/llms
- https://docs.crewai.com/en/enterprise/guides/azure-openai-setup

## WordPress

Purpose:

- Blog post drafts.
- Landing-page drafts if the site exposes pages through REST.
- Optional scheduled or published posts after approval.

API:

- WordPress REST API.
- Posts endpoint: `/wp-json/wp/v2/posts`
- Pages endpoint: `/wp-json/wp/v2/pages`
- Media endpoint: `/wp-json/wp/v2/media`

Environment:

- `WORDPRESS_MODE=auto`
- `WORDPRESS_BASE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`
- `WORDPRESS_DEFAULT_AUTHOR_ID`

Real connector behavior:

- `create_draft`: create post/page with `status=draft`.
- `schedule`: set `status=future` and date only after approval.
- `publish`: set `status=publish` only when `ALLOW_REAL_PUBLISH=true` and item is `APPROVED`.
- Store returned WordPress ID and link.

Mock connector behavior:

- Return IDs like `wp_mock_post_12345`.
- Return URLs like `https://mock.wordpress.local/posts/topic-slug`.
- Simulate draft, scheduled, and published status.

Risk notes:

- Application password permissions depend on the WordPress user role.
- Different themes/builders may store landing pages differently.
- Real publishing must remain gated.

Relevant docs:

- https://developer.wordpress.org/rest-api/reference/posts/

## HubSpot

Purpose:

- Weekly marketing emails.
- Email sequence drafts.
- Optional landing-page or campaign association later if account supports it.
- Email performance metrics if available.

API:

- HubSpot Marketing Emails API.
- HubSpot endpoints and capabilities depend on account tier and product access.

Environment:

- `HUBSPOT_MODE=auto`
- `HUBSPOT_PRIVATE_APP_TOKEN`
- `HUBSPOT_BUSINESS_UNIT_ID`
- `HUBSPOT_EMAIL_TEMPLATE_PATH`

Real connector behavior:

- Check token validity and marketing email API access.
- Create/update marketing email drafts if supported.
- Do not assume publish/send is available.
- If publish/send endpoint requires Marketing Hub Enterprise or an add-on, fall back to mock for sending.

Mock connector behavior:

- Return IDs like `hs_mock_email_12345`.
- Return preview URLs like `https://mock.hubspot.local/email/12345`.
- Simulate opens, clicks, click-through rate, and unsubscribe rate.

Risk notes:

- HubSpot is the most likely paid-plan blocker.
- Publishing/sending marketing emails may require paid HubSpot tiers.
- Transactional email is a separate add-on and is not the same as normal marketing email.

Relevant docs:

- https://developers.hubspot.com/docs/api-reference/legacy/marketing/marketing-emails/guide

## LinkedIn

Purpose:

- LinkedIn organization posts.
- Thought leadership posts.
- Optional post performance metrics.

API:

- LinkedIn Posts API and Marketing/Community Management APIs.

Environment:

- `LINKEDIN_MODE=auto`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_ORG_URN`

Real connector behavior:

- Check token scopes and organization access.
- Create organization posts only when permissions support it.
- Store LinkedIn post URN returned by API.
- Publish only after human approval and `ALLOW_REAL_PUBLISH=true`.

Mock connector behavior:

- Return URNs like `urn:li:share:mock12345`.
- Return URLs like `https://www.linkedin.com/feed/update/urn:li:share:mock12345`.
- Simulate impressions, reactions, comments, shares, and clicks.

Risk notes:

- LinkedIn permissions and access tiers can require approval.
- Some open permissions support member posting, while organization and marketing workflows need stronger access.
- All real publishing should be conservative.

Relevant docs:

- https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api

## Meta

Purpose:

- Facebook Page posts.
- Instagram business/creator posts where supported.
- Meta ad copy draft records.
- Optional Page, Instagram, or ad performance metrics.

API:

- Meta Graph API.
- Instagram Graph API / Instagram Platform publishing.
- Marketing API for ads and insights.

Environment:

- `META_MODE=auto`
- `META_ACCESS_TOKEN`
- `META_PAGE_ID`
- `META_IG_USER_ID`
- `META_AD_ACCOUNT_ID`

Real connector behavior:

- Check token validity and target asset access.
- Use read-only metrics first when possible.
- Create/publish posts only after permissions are confirmed.
- Publish only after human approval and `ALLOW_REAL_PUBLISH=true`.

Mock connector behavior:

- Return IDs like `meta_mock_post_12345`.
- Return URLs like `https://mock.meta.local/posts/12345`.
- Simulate reach, impressions, clicks, comments, shares, and spend.

Risk notes:

- Meta app review and permissions can take time.
- Facebook Page and Instagram account linkage can break publishing.
- Ad spend is separate from API calls; never create live ads by default.

Relevant docs:

- https://developers.facebook.com/docs/graph-api/
- https://developers.facebook.com/docs/marketing-api/

## Google Analytics 4

Purpose:

- Website traffic.
- Blog and landing page performance.
- Conversion metrics.
- Baseline comparison.

API:

- Google Analytics Data API.

Environment:

- `GA4_MODE=auto`
- `GA4_PROPERTY_ID`
- `GOOGLE_APPLICATION_CREDENTIALS`

Real connector behavior:

- Read-only queries.
- Pull page views, users, sessions, engagement rate, conversions, and traffic source where configured.
- Normalize metrics into `PerformanceSnapshot`.

Mock connector behavior:

- Generate monthly trend data.
- Simulate baseline comparison.
- Return plausible traffic and conversion metrics.

Risk notes:

- Requires GA4 property access and service account setup.
- Metrics depend on the client's configured events and conversions.
- Use read-only permissions.

Relevant docs:

- https://developers.google.com/analytics/devguides/reporting/data/v1

## Search And Research

Purpose:

- Current market research.
- Competitor and SERP context.
- Source discovery for blog content.

Default:

- `SEARCH_MODE=mock` for demo.

Optional API:

- Serper or another search API.

Environment:

- `SEARCH_MODE=auto`
- `SERPER_API_KEY`

Real connector behavior:

- Search only when needed.
- Cache results by query and date.
- Store source URL, title, snippet, and retrieval timestamp.

Mock connector behavior:

- Return static research fixtures or generated plausible results.

Risk notes:

- Search APIs may require paid usage after free credits.
- Web research should include source capture and freshness metadata.
- Avoid relying on unsupported scraping for production.

Relevant docs:

- https://docs.crewai.com/en/quickstart

## Demo Capability Matrix

| Service | Default | Real when available | Mock fallback |
| --- | --- | --- | --- |
| Azure OpenAI | Real | Generates all content | No, unless local fake LLM is later added |
| WordPress | Auto | Drafts/schedules/publishes gated content | Mock drafts and links |
| HubSpot | Auto | Email drafts if API access supports it | Mock email IDs and metrics |
| LinkedIn | Auto | Organization posts after approval | Mock post URNs and metrics |
| Meta | Auto | Page/Instagram posts after approval | Mock post IDs and metrics |
| GA4 | Auto | Read-only analytics | Mock performance snapshots |
| Search | Mock | Serper or chosen search API | Fixture/generated research |

## Approval And Publishing Rules

- `publish()` must reject any content item that is not `APPROVED`.
- `publish()` must reject when `ALLOW_REAL_PUBLISH=false`.
- Real connectors must validate capabilities before performing writes.
- Mock connectors must clearly mark output as mock.
- Every connector result must be auditable.

