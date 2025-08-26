from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CompanyUser(models.Model):
    """
    Links Django users to their company tenant for on-premise deployments.
    Each company gets their own Watchtower instance with a unique client ID.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_user')
    company_tenant_id = models.CharField(max_length=100, help_text="Company-specific tenant identifier")
    is_root_user = models.BooleanField(default=False, help_text="First user who registered becomes root user")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_sub_users',
        help_text="Root user who created this sub-user"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_company_user'
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'
    
    def __str__(self):
        role = "Root User" if self.is_root_user else "Sub User"
        return f"{self.user.username} - {self.company_tenant_id} ({role})"
    
    @classmethod
    def get_root_user(cls, company_tenant_id):
        """Get the root user for a specific company."""
        try:
            return cls.objects.get(
                company_tenant_id=company_tenant_id,
                is_root_user=True
            ).user
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def is_first_user(cls, company_tenant_id):
        """Check if this would be the first user for the company."""
        return not cls.objects.filter(company_tenant_id=company_tenant_id).exists()
    
    def can_manage_users(self):
        """Check if this user can manage other users."""
        return self.is_root_user
    
    def get_company_users(self):
        """Get all users in the same company."""
        return CompanyUser.objects.filter(
            company_tenant_id=self.company_tenant_id
        ).select_related('user').order_by('created_at')
    
    def get_sub_users(self):
        """Get all sub-users in the company (excluding root user)."""
        return CompanyUser.objects.filter(
            company_tenant_id=self.company_tenant_id,
            is_root_user=False
        ).select_related('user').order_by('created_at')
