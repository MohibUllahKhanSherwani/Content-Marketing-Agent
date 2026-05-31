from content_marketing_agent.config.settings import get_settings


def default_llm() -> str:
    return get_settings().content_agent_model


def review_llm() -> str:
    return get_settings().content_agent_review_model

