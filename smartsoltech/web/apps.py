from django.apps import AppConfig

from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals

class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'
