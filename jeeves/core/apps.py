from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'jeeves.core'
    verbose_name = "Jeeves Core"

    def ready(self):
        import jeeves.core.handlers.signals  # noqa
        import jeeves.github.handlers.signals  # noqa
