"""
Models for the Equipment application.
Handles dataset storage and equipment data management.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import json


class Dataset(models.Model):
    """
    Model to store uploaded datasets.
    Only the last 5 datasets are kept in the database.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Summary statistics (stored as JSON for efficiency)
    total_count = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    equipment_type_distribution = models.JSONField(default=dict)
    
    # Raw data stored as JSON for quick retrieval
    raw_data = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['user', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_summary(self):
        """Return a dictionary with summary statistics."""
        return {
            'id': self.id,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at.isoformat(),
            'total_count': self.total_count,
            'avg_flowrate': self.avg_flowrate,
            'avg_pressure': self.avg_pressure,
            'avg_temperature': self.avg_temperature,
            'equipment_type_distribution': self.equipment_type_distribution,
        }


class EquipmentData(models.Model):
    """
    Model to store individual equipment data entries.
    Linked to a Dataset for organization.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment_items')
    equipment_name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)
    flowrate = models.FloatField(validators=[MinValueValidator(0.0)])
    pressure = models.FloatField(validators=[MinValueValidator(0.0)])
    temperature = models.FloatField()
    
    class Meta:
        ordering = ['equipment_name']
        indexes = [
            models.Index(fields=['dataset', 'equipment_type']),
            models.Index(fields=['equipment_type']),
        ]
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
    
    def to_dict(self):
        """Return a dictionary representation of the equipment."""
        return {
            'equipment_name': self.equipment_name,
            'type': self.equipment_type,
            'flowrate': self.flowrate,
            'pressure': self.pressure,
            'temperature': self.temperature,
        }
