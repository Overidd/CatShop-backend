from django.apps import AppConfig

class ProfileClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_client'

    def ready(self):
        import profile_client.signals
