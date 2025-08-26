from django.db import models
from django.utils import timezone


class TenantSession(models.Model):
    """
    Model to track tenant sessions and usage for audit purposes.
    """
    tenant_id = models.CharField(max_length=100, db_index=True)
    session_id = models.CharField(max_length=100, unique=True)
    # Use string reference to avoid circular imports
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    features_used = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'authorization_tenant_session'
        indexes = [
            models.Index(fields=['tenant_id', 'started_at']),
            models.Index(fields=['tenant_id', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.tenant_id} - {self.session_id}"


class TenantAuditLog(models.Model):
    """
    Model to log tenant actions for compliance and monitoring.
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('feature_access', 'Feature Access'),
        ('data_access', 'Data Access'),
        ('limit_exceeded', 'Limit Exceeded'),
        ('plan_change', 'Plan Change'),
        ('admin_action', 'Admin Action'),
    ]
    
    tenant_id = models.CharField(max_length=100, db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    # Use string reference to avoid circular imports
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    resource = models.CharField(max_length=200, blank=True)
    details = models.JSONField(default=dict)
    token_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'authorization_tenant_audit_log'
        indexes = [
            models.Index(fields=['tenant_id', 'timestamp']),
            models.Index(fields=['tenant_id', 'action']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tenant_id} - {self.action} - {self.timestamp}"


class TenantFeatureUsage(models.Model):
    """
    Model to track feature usage for billing and analytics.
    """
    tenant_id = models.CharField(max_length=100, db_index=True)
    feature_name = models.CharField(max_length=100)
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(default=timezone.now)
    period_start = models.DateField()
    period_end = models.DateField()
    
    class Meta:
        db_table = 'authorization_tenant_feature_usage'
        unique_together = ['tenant_id', 'feature_name', 'period_start']
        indexes = [
            models.Index(fields=['tenant_id', 'feature_name']),
            models.Index(fields=['tenant_id', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.tenant_id} - {self.feature_name} - {self.period_start}"


class TenantLimit(models.Model):
    """
    Model to store tenant-specific limits and current usage.
    """
    tenant_id = models.CharField(max_length=100, db_index=True)
    limit_name = models.CharField(max_length=100)
    limit_value = models.PositiveIntegerField()
    current_usage = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'authorization_tenant_limit'
        unique_together = ['tenant_id', 'limit_name']
        indexes = [
            models.Index(fields=['tenant_id', 'limit_name']),
        ]
    
    def __str__(self):
        return f"{self.tenant_id} - {self.limit_name}: {self.current_usage}/{self.limit_value}"
    
    @property
    def remaining(self):
        """Calculate remaining capacity."""
        return max(0, self.limit_value - self.current_usage)
    
    @property
    def usage_percentage(self):
        """Calculate usage as a percentage."""
        if self.limit_value == 0:
            return 0
        return min(100, (self.current_usage / self.limit_value) * 100)
