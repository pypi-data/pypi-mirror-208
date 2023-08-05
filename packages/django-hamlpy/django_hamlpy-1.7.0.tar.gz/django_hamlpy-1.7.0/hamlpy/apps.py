from django.apps import AppConfig


class Config(AppConfig):
    name = "hamlpy"

    def ready(self):
        # patch Django's templatize method
        from .template import templatize  # noqa


default_app_config = "hamlpy.Config"
