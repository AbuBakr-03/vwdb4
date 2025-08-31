from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, Segment


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for Contact model."""
    
    list_display = [
        'display_name', 'email', 'primary_phone_display', 'external_id', 'tenant_id', 'created_at'
    ]
    
    list_filter = [
        'tenant_id', 'created_at'
    ]
    
    search_fields = [
        'first_name', 'last_name', 'email', 'external_id', 'tenant_id'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('external_id', 'email')
        }),
        ('Contact Details', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Metadata', {
            'fields': ('tenant_id', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_name(self, obj):
        """Display the contact name."""
        return obj.display_name
    display_name.short_description = 'Name'
    
    def primary_phone_display(self, obj):
        """Display primary phone number."""
        phone = obj.primary_phone
        if phone:
            return format_html('<span class="font-mono">{}</span>', phone)
        return '-'
    primary_phone_display.short_description = 'Primary Phone'
    
    def get_queryset(self, request):
        """Filter contacts by tenant if user has tenant restrictions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Add tenant filtering logic here if needed
        return qs


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    """Admin interface for Segment model."""
    
    list_display = [
        'name', 'color_display', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'color')
        }),
        ('Metadata', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        """Display color as a colored badge."""
        return format_html(
            '<span class="badge {} badge-sm">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'
    
    def get_queryset(self, request):
        """Filter segments by tenant if user has tenant restrictions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Add tenant filtering logic here if needed
        return qs
