from backend.app.schemas.settings import AppSettings

_CURRENT = AppSettings()

def get_model_settings() -> AppSettings:
    return _CURRENT

def update_model_settings(settings: AppSettings) -> AppSettings:
    global _CURRENT
    _CURRENT = settings
    return _CURRENT
