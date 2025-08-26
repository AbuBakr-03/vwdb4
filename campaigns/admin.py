"""
Campaigns admin interface.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, CampaignSession, CampaignQueue


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign model."""
    
    list_display = [
        'name', 'tenant_id', 'status', 'priority', 'total_calls', 
        'success_rate_display', 'created_at', 'created_by'
    ]
    
    list_filter = [
        'status', 'priority', 'tenant_id', 'created_at', 'start_date', 'end_date'
    ]
    
    search_fields = ['name', 'description', 'tenant_id', 'created_by__username']
    
    readonly_fields = [
        'total_calls', 'successful_calls', 'failed_calls', 'last_activity',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status', 'priority')
        }),
        ('Tenant & User', {
            'fields': ('tenant_id', 'created_by')
        }),
        ('Configuration', {
            'fields': ('prompt_template', 'voice_id', 'agent_config')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date')
        }),
        ('Limits', {
            'fields': ('max_calls', 'max_concurrent')
        }),
        ('Statistics', {
            'fields': ('total_calls', 'successful_calls', 'failed_calls', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def get_queryset(self, request):
        """Filter campaigns by tenant if user has tenant restrictions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Add tenant filtering logic here if needed
        return qs


@admin.register(CampaignSession)
class CampaignSessionAdmin(admin.ModelAdmin):
    """Admin interface for CampaignSession model."""
    
    list_display = [
        'session_id', 'campaign', 'status', 'phone_number', 
        'call_duration_display', 'tenant_id', 'created_at'
    ]
    
    list_filter = [
        'status', 'tenant_id', 'created_at', 'started_at', 'completed_at'
    ]
    
    search_fields = [
        'session_id', 'phone_number', 'campaign__name', 'tenant_id'
    ]
    
    readonly_fields = [
        'session_id', 'created_at', 'started_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'campaign', 'status')
        }),
        ('Call Details', {
            'fields': ('phone_number', 'call_duration')
        }),
        ('Agent Interaction', {
            'fields': ('agent_response', 'user_input', 'conversation_log')
        }),
        ('Metadata', {
            'fields': ('tenant_id', 'error_message', 'retry_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def call_duration_display(self, obj):
        """Display call duration in human readable format."""
        return obj.duration_formatted
    call_duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Filter sessions by tenant if user has tenant restrictions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Add tenant filtering logic here if needed
        return qs


@admin.register(CampaignQueue)
class CampaignQueueAdmin(admin.ModelAdmin):
    """Admin interface for CampaignQueue model."""
    
    list_display = [
        'campaign', 'session', 'priority', 'position', 'is_processing',
        'scheduled_for', 'queued_at'
    ]
    
    list_filter = [
        'priority', 'is_processing', 'queued_at', 'scheduled_for'
    ]
    
    search_fields = [
        'campaign__name', 'session__session_id'
    ]
    
    readonly_fields = [
        'queued_at', 'started_at'
    ]
    
    fieldsets = (
        ('Queue Information', {
            'fields': ('campaign', 'session', 'priority', 'position')
        }),
        ('Status', {
            'fields': ('is_processing', 'scheduled_for')
        }),
        ('Timestamps', {
            'fields': ('queued_at', 'started_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter queue items by tenant if user has tenant restrictions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Add tenant filtering logic here if needed
        return qs
