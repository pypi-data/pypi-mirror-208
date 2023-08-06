class TranslationKeyNotFound(Exception):
    """Exception thrown for missing translation hash key in Redis for user-provided key."""

    pass


class TranslationObjectNotFound(Exception):
    """Exception thrown for missing translation object in REDIS for user-provided key."""

    pass
