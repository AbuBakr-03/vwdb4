"""
Campaigns app configuration.
"""

from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'campaigns'
    verbose_name = 'Campaigns'
    
    def ready(self):
        """App ready hook."""
        try:
            import campaigns.signals  # noqa
        except ImportError:
            pass
