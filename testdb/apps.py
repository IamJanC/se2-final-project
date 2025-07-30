from django.apps import AppConfig           # type: ignore


class TestdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testdb'
