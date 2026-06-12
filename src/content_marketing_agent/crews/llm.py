import os
from content_marketing_agent.config.settings import get_settings


def default_llm() -> str:
    settings = get_settings()
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    return settings.content_agent_model


def review_llm() -> str:
    settings = get_settings()
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    return settings.content_agent_review_model

