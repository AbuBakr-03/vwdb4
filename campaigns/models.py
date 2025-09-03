"""
Campaign models for AI agent campaigns.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Campaign(models.Model):
    """Campaign model for managing AI agent campaigns."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic campaign info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Tenant and user info
    tenant_id = models.CharField(max_length=100, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns')
    
    # Campaign configuration
    prompt_template = models.TextField()
    voice_id = models.CharField(max_length=100, blank=True)
    agent_config = models.JSONField(default=dict)
    
    # Assistant relationship
    assistant = models.ForeignKey(
        'dashboard.Assistant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campaigns',
        help_text="AI Assistant to use for this campaign"
    )
    
    # Scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Limits and quotas
    max_calls = models.PositiveIntegerField(default=1000)
    max_concurrent = models.PositiveIntegerField(default=10)
    
    # Statistics
    total_calls = models.PositiveIntegerField(default=0)
    successful_calls = models.PositiveIntegerField(default=0)
    failed_calls = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['tenant_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant_id})"
    
    @property
    def is_active(self):
        """Check if campaign is currently active."""
        if self.status != 'active':
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    @property
    def success_rate(self):
        """Calculate success rate percentage."""
        if self.total_calls == 0:
            return 0
        return (self.successful_calls / self.total_calls) * 100


class CampaignSession(models.Model):
    """Individual session within a campaign."""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Campaign relationship
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='sessions')
    
    # Session info
    session_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    # Call details
    phone_number = models.CharField(max_length=20)
    call_duration = models.PositiveIntegerField(default=0)  # in seconds
    
    # Agent interaction
    agent_response = models.TextField(blank=True)
    user_input = models.TextField(blank=True)
    conversation_log = models.JSONField(default=list)
    
    # Metadata
    tenant_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'campaign_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.campaign.name}"
    
    @property
    def duration_formatted(self):
        """Format duration in human readable format."""
        if self.call_duration < 60:
            return f"{self.call_duration}s"
        minutes = self.call_duration // 60
        seconds = self.call_duration % 60
        return f"{minutes}m {seconds}s"


class CampaignQueue(models.Model):
    """Queue for managing campaign execution order."""
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    # Campaign and session
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='queue_items')
    session = models.ForeignKey(CampaignSession, on_delete=models.CASCADE, related_name='queue_items')
    
    # Queue management
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    position = models.PositiveIntegerField()
    
    # Status
    is_processing = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    queued_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'campaign_queue'
        ordering = ['-priority', 'position', 'queued_at']
        indexes = [
            models.Index(fields=['campaign', 'priority', 'position']),
            models.Index(fields=['is_processing', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"Queue Item {self.position} - {self.campaign.name}"
