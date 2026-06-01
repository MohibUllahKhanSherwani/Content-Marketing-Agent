from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.services.content_items import ContentItemStore


def test_create_and_get_client_profile() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    create_response = client.post(
        "/client-profiles",
        json={
            "name": "Acme SaaS",
            "industry": "B2B SaaS",
            "audience": ["CTOs", "VP Engineering"],
            "offers": ["AI migration services"],
        },
    )
    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload["name"] == "Acme SaaS"
    assert payload["industry"] == "B2B SaaS"
    profile_id = payload["id"]

    detail_response = client.get(f"/client-profiles/{profile_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == profile_id
    assert detail["name"] == "Acme SaaS"


def test_create_and_get_campaign() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    profile = client.post(
        "/client-profiles",
        json={"name": "Acme SaaS", "audience": ["CTOs"], "offers": ["Content Ops"]},
    ).json()

    campaign_response = client.post(
        "/campaigns",
        json={
            "client_profile_id": profile["id"],
            "objective": "Increase demos by 20%",
            "audience": "CTOs in US startups",
            "funnel_stage": "MOFU",
            "channels": ["wordpress", "linkedin"],
            "keywords": ["ai automation", "content operations"],
            "cta": "Book a demo",
        },
    )
    assert campaign_response.status_code == 200
    campaign = campaign_response.json()
    assert campaign["objective"] == "Increase demos by 20%"
    campaign_id = campaign["id"]

    campaign_detail = client.get(f"/campaigns/{campaign_id}")
    assert campaign_detail.status_code == 200
    assert campaign_detail.json()["id"] == campaign_id


def test_create_campaign_requires_existing_client_profile() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    response = client.post(
        "/campaigns",
        json={
            "client_profile_id": "missing-profile",
            "objective": "Increase demos",
            "audience": "Technical buyers",
            "funnel_stage": "TOFU",
            "channels": ["wordpress"],
        },
    )
    assert response.status_code == 404
