# Graph Report - .  (2026-05-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 198 nodes · 339 edges · 17 communities detected
- Extraction: 56% EXTRACTED · 44% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `HybridPlaceholderConnector` - 26 edges
2. `ConnectorMode` - 24 edges
3. `MockConnector` - 20 edges
4. `BaseConnector` - 19 edges
5. `Platform` - 19 edges
6. `AppSettings` - 17 edges
7. `ConnectorRegistry` - 16 edges
8. `default_llm()` - 14 edges
9. `build_connector_registry()` - 13 edges
10. `ConnectorCapabilities` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_auto_connector_falls_back_to_mock_when_credentials_missing()` --calls--> `AppSettings`  [INFERRED]
  tests/test_connector_registry.py → src/content_marketing_agent/config/settings.py
- `test_real_connector_fails_loudly_when_credentials_missing()` --calls--> `AppSettings`  [INFERRED]
  tests/test_connector_registry.py → src/content_marketing_agent/config/settings.py
- `make_content_item()` --calls--> `ContentItem`  [INFERRED]
  tests/test_approval_gate.py → src/content_marketing_agent/domain/models.py
- `test_publish_requires_approved_status()` --calls--> `AppSettings`  [INFERRED]
  tests/test_approval_gate.py → src/content_marketing_agent/config/settings.py
- `test_publish_requires_runtime_flag()` --calls--> `AppSettings`  [INFERRED]
  tests/test_approval_gate.py → src/content_marketing_agent/config/settings.py

## Communities (28 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (17): default_llm(), calendar_scheduler(), connector_operator(), DistributionCrew, publication_auditor(), Prepares approved content for platform connectors., blog_writer(), conversion_copywriter() (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (11): GA4Connector, HubSpotConnector, LinkedInConnector, MetaConnector, build_connector_registry(), ConnectorRegistry, SearchConnector, WordPressConnector (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (11): AnalyticsCrew, baseline_analyst(), insights_writer(), performance_analyst(), Turns platform metrics into baseline comparison and recommendations., review_llm(), brand_voice_reviewer(), managing_editor() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.35
Nodes (14): BaseModel, ConnectorMode, ContentFormat, ContentStatus, Platform, PublicationOperation, ApprovalDecision, CampaignBrief (+6 more)

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (14): BaseSettings, AppSettings, get_settings(), Environment-backed runtime settings., ApprovalError, ensure_publish_allowed(), Raised when a content item is not allowed to publish., create_db_and_tables() (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.21
Nodes (3): BaseConnector, MockConnector, Realistic no-network connector used for demos and unavailable integrations.

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (3): ABC, BaseConnector, Base interface for all real, mock, and hybrid platform connectors.

### Community 7 - "Community 7"
Cohesion: 0.22
Nodes (5): kickoff(), plot(), MonthlyContentFlow, MonthlyContentState, Top-level monthly workflow placeholder.      The source package is scaffolded fi

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (4): calendar_demo(), connectors(), demo_calendar_items(), Small deterministic calendar seed for local demos.

### Community 10 - "Community 10"
Cohesion: 0.4
Nodes (4): connectors(), hello(), Show connector modes and capabilities., Smoke command for local setup checks.

## Knowledge Gaps
- **20 isolated node(s):** `Show connector modes and capabilities.`, `Smoke command for local setup checks.`, `Content Marketing Agent Team package.`, `Environment-backed runtime settings.`, `Base interface for all real, mock, and hybrid platform connectors.` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.374) - this node is a cross-community bridge._
- **Why does `default_llm()` connect `Community 0` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `Community 4` to `Community 1`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `HybridPlaceholderConnector` (e.g. with `GA4Connector` and `HubSpotConnector`) actually correct?**
  _`HybridPlaceholderConnector` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `ConnectorMode` (e.g. with `BaseConnector` and `GA4Connector`) actually correct?**
  _`ConnectorMode` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MockConnector` (e.g. with `HybridPlaceholderConnector` and `BaseConnector`) actually correct?**
  _`MockConnector` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `BaseConnector` (e.g. with `ConnectorMode` and `Platform`) actually correct?**
  _`BaseConnector` has 10 INFERRED edges - model-reasoned connections that need verification._