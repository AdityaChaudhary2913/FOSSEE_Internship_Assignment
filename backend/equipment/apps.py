"""
App configuration for Equipment application.
"""

from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment'
    verbose_name = 'Chemical Equipment Data'
