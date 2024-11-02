from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = "frontend_kit"
    verbose_name = "Django Frontend Kit"
    default_auto_field = "django.db.models.BigAutoField"
