from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    """Contact model for managing people in the address book."""
    
    external_id = models.CharField(
        max_length=128, 
        blank=True, 
        db_index=True,
        help_text="CRM/HRIS/Bank core ID"
    )
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phones = models.JSONField(default=list, blank=True, help_text="Array of phone numbers in E.164 format")
    timezone = models.CharField(max_length=64, blank=True)
    company = models.CharField(max_length=200, blank=True, help_text="Company name")
    segment_id = models.CharField(max_length=100, blank=True, help_text="Optional segment identifier for auto-creation")
    segments = models.JSONField(default=list, blank=True, help_text="Array of segment IDs")
    tenant_id = models.CharField(max_length=100, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'people_contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'external_id']),
            models.Index(fields=['tenant_id', 'email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.external_id or str(self.id)
    
    @property
    def display_name(self):
        """Get the display name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def primary_phone(self):
        """Get the first phone number if available."""
        return self.phones[0] if self.phones else None


class Segment(models.Model):
    """Segment model for categorizing contacts."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='badge-primary', help_text="daisyUI badge color class")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_segments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'people_segments'
        ordering = ['name']
    
    def __str__(self):
        return self.name
