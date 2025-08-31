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
    phone = models.CharField(max_length=20, default='', help_text="Phone number in E.164 format")
    tenant_id = models.CharField(max_length=100, db_index=True, default='zain_bh')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'people_contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'external_id']),
            models.Index(fields=['tenant_id', 'email']),
            models.Index(fields=['tenant_id', 'phone']),
        ]
        constraints = [
            # Ensure unique external_id per tenant
            models.UniqueConstraint(
                fields=['tenant_id', 'external_id'],
                name='unique_tenant_external_id',
                condition=models.Q(external_id__isnull=False) & ~models.Q(external_id='')
            ),
            # Ensure unique email per tenant
            models.UniqueConstraint(
                fields=['tenant_id', 'email'],
                name='unique_tenant_email',
                condition=models.Q(email__isnull=False) & ~models.Q(email='')
            ),
            # Ensure unique phone per tenant
            models.UniqueConstraint(
                fields=['tenant_id', 'phone'],
                name='unique_tenant_phone',
                condition=models.Q(phone__isnull=False) & ~models.Q(phone='')
            ),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.external_id or str(self.id)
    
    @property
    def display_name(self):
        """Get the display name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def primary_phone(self):
        """Get the phone number if available."""
        return self.phone if self.phone else None
    
    @classmethod
    def find_duplicates(cls, **kwargs):
        """
        Find potential duplicate contacts based on various criteria.
        Returns a queryset of potential duplicates.
        """
        tenant_id = kwargs.get('tenant_id', 'zain_bh')
        
        # Build a combined query using Q objects instead of union
        from django.db.models import Q
        
        query = Q()
        
        # Check by email
        if kwargs.get('email'):
            query |= Q(email=kwargs['email'])
        
        # Check by external_id
        if kwargs.get('external_id'):
            query |= Q(external_id=kwargs['external_id'])
        
        # Check by name combination
        if kwargs.get('first_name') and kwargs.get('last_name'):
            query |= Q(
                first_name__iexact=kwargs['first_name'],
                last_name__iexact=kwargs['last_name']
            )
        
        # Check by phone number
        if kwargs.get('phone'):
            query |= Q(phone=kwargs['phone'])
        
        # Apply tenant filter and return results
        if query:
            return cls.objects.filter(query, tenant_id=tenant_id)
        else:
            return cls.objects.none()


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
