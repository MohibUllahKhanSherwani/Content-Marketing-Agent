# Security

## Secrets

- Never commit `.env` files or API credentials.
- Store Gemini, WordPress, HubSpot, LinkedIn, Meta, and Google credentials in local `.env` files or deployment secret stores.
- Keep `.env.example` as documentation only.

## Publishing Safety

- Real publishing requires both an approved content item and `ALLOW_REAL_PUBLISH=true`.
- Connector implementations must reject publish operations for non-approved content.
- Demo runs should prefer drafts or mock publications.

## Reporting Issues

This repository is currently private/local. If it moves to GitHub, use private security reporting for credential exposure, publishing bypasses, or data leakage issues.

