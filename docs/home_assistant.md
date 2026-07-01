# Home Assistant Integration

`HomeAgent` can integrate with Home Assistant (REST) when configured.

## Required

- `.env` → `HOME_ASSISTANT_URL`
- `.env` → `HOME_ASSISTANT_TOKEN` (Long-Lived Access Token)

## Notes

Service calls are made via `HomeAgent.call_service(domain, service, entity_id)`.

