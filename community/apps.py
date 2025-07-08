from django.apps import AppConfig


class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'community'
    verbose_name = 'Bulshada Garaad'  # Community in Somali
    
    def ready(self):
        # Import signals to ensure they are registered
        import community.signals 