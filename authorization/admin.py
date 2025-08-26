from django.contrib import admin
from .models import TenantSession, TenantAuditLog, TenantFeatureUsage, TenantLimit


@admin.register(TenantSession)
class TenantSessionAdmin(admin.ModelAdmin):
    list_display = ['tenant_id', 'session_id', 'user', 'started_at', 'last_activity', 'is_active']
    list_filter = ['tenant_id', 'is_active', 'started_at']
    search_fields = ['tenant_id', 'session_id', 'user__username']
    readonly_fields = ['started_at', 'last_activity']
    date_hierarchy = 'started_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TenantAuditLog)
class TenantAuditLogAdmin(admin.ModelAdmin):
    list_display = ['tenant_id', 'action', 'user', 'timestamp', 'ip_address', 'resource']
    list_filter = ['tenant_id', 'action', 'timestamp']
    search_fields = ['tenant_id', 'action', 'user__username', 'resource']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TenantFeatureUsage)
class TenantFeatureUsageAdmin(admin.ModelAdmin):
    list_display = ['tenant_id', 'feature_name', 'usage_count', 'last_used', 'period_start', 'period_end']
    list_filter = ['tenant_id', 'feature_name', 'period_start']
    search_fields = ['tenant_id', 'feature_name']
    readonly_fields = ['last_used']
    date_hierarchy = 'period_start'


@admin.register(TenantLimit)
class TenantLimitAdmin(admin.ModelAdmin):
    list_display = ['tenant_id', 'limit_name', 'current_usage', 'limit_value', 'remaining', 'usage_percentage', 'last_updated']
    list_filter = ['tenant_id', 'limit_name']
    search_fields = ['tenant_id', 'limit_name']
    readonly_fields = ['last_updated', 'remaining', 'usage_percentage']
    
    def remaining(self, obj):
        return obj.remaining
    remaining.short_description = 'Remaining'
    
    def usage_percentage(self, obj):
        return f"{obj.usage_percentage:.1f}%"
    usage_percentage.short_description = 'Usage %'
