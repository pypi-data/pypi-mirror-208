from django.apps import AppConfig


class HumansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'humans'
    def ready(self) -> None:
        import humans.signals.humans
