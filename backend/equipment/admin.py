"""
Admin configuration for the Equipment application.
Provides an interface for managing datasets and equipment data.
"""

from django.contrib import admin
from .models import Dataset, EquipmentData


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Admin interface for Dataset model."""
    list_display = ['filename', 'user', 'uploaded_at', 'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['uploaded_at', 'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipment_type_distribution']
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'filename', 'file', 'uploaded_at')
        }),
        ('Summary Statistics', {
            'fields': ('total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipment_type_distribution')
        }),
    )


@admin.register(EquipmentData)
class EquipmentDataAdmin(admin.ModelAdmin):
    """Admin interface for EquipmentData model."""
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name', 'equipment_type']
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('dataset', 'equipment_name', 'equipment_type')
        }),
        ('Parameters', {
            'fields': ('flowrate', 'pressure', 'temperature')
        }),
    )
