from app.models.ai_provider_key import AIProviderKey


def get_api_key(provider: str):
    provider = provider.lower().strip()

    record = AIProviderKey.query.filter_by(
        provider=provider,
        is_active=True
    ).first()

    if not record:
        return None

    return record.api_key
