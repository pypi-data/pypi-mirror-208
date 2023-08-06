from aleksis.core.settings import _settings

if _settings.get("untis.database.enabled"):
    DATABASES = {
        "untis": {
            "ENGINE": "django_prometheus.db.backends.mysql",
            "NAME": _settings.get("untis.database.name", "untis"),
            "USER": _settings.get("untis.database.user", "untis"),
            "PASSWORD": _settings.get("untis.database.password", None),
            "HOST": _settings.get("untis.database.host", "127.0.0.1"),
            "PORT": _settings.get("untis.database.port", 3306),
            "CONN_MAX_AGE": _settings.get("untis.database.conn_max_age", 0),
            "OPTIONS": _settings.get("untis.database.options", {}),
        }
    }
