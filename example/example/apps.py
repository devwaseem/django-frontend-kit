from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = "django_frontend_kit_example"
    verbose_name = "Django Frontend Kit Example"
    default_auto_field = "django.db.models.BigAutoField"
