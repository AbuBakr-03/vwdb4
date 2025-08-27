from django.db import models
from django.contrib.auth.models import User


class PartyType(models.TextChoices):
    PERSON = "person", "Person"
    COMPANY = "company", "Company"


class Contact(models.Model):
    """Contact model for managing people and companies in the address book."""
    
    party_type = models.CharField(
        max_length=20, 
        choices=PartyType.choices, 
        default=PartyType.PERSON
    )
    external_id = models.CharField(
        max_length=128, 
        blank=True, 
        db_index=True,
        help_text="CRM/HRIS/Bank core ID"
    )
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    name = models.CharField(max_length=200, blank=True, help_text="Company name for company type")
    email = models.EmailField(blank=True)
    phones = models.JSONField(default=list, blank=True, help_text="Array of phone numbers in E.164 format")
    timezone = models.CharField(max_length=64, blank=True)
    company = models.CharField(max_length=200, blank=True, help_text="Company name for person type")
    contact_person = models.CharField(max_length=200, blank=True, help_text="Contact person for company type")
    segments = models.JSONField(default=list, blank=True, help_text="Array of segment IDs")
    tenant_id = models.CharField(max_length=100, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'people_contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'party_type']),
            models.Index(fields=['tenant_id', 'external_id']),
            models.Index(fields=['tenant_id', 'email']),
        ]
    
    def __str__(self):
        if self.party_type == PartyType.PERSON:
            return f"{self.first_name} {self.last_name}".strip() or self.external_id or str(self.id)
        else:
            return self.name or self.external_id or str(self.id)
    
    @property
    def display_name(self):
        """Get the display name based on party type."""
        if self.party_type == PartyType.PERSON:
            return f"{self.first_name} {self.last_name}".strip()
        else:
            return self.name
    
    @property
    def primary_phone(self):
        """Get the first phone number if available."""
        return self.phones[0] if self.phones else None


class Segment(models.Model):
    """Segment model for categorizing contacts."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='badge-primary', help_text="daisyUI badge color class")
    tenant_id = models.CharField(max_length=100, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_segments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'people_segments'
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant_id', 'name']),
        ]
        unique_together = ['tenant_id', 'name']
    
    def __str__(self):
        return self.name
