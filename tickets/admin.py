from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Ticket, TicketComment, TicketAttachment, Company, QATester


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'contact_phone', 'is_active', 'created_at', 'tester_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def tester_count(self, obj):
        return obj.get_active_testers_count()
    tester_count.short_description = 'Active Testers'


@admin.register(QATester)
class QATesterAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'company', 'created_at']
    search_fields = ['user__username', 'user__email', 'company__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'get_short_id', 'title', 'submitter', 'status', 'priority', 
        'issue_location', 'assigned_to', 'company', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'issue_location', 'company', 
        'created_at', 'assigned_to'
    ]
    search_fields = [
        'title', 'description', 'submitter__username', 
        'submitter__email', 'assigned_to__username'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'issue_location', 'additional_notes')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('submitter', 'assigned_to', 'company')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_short_id(self, obj):
        return obj.get_short_id()
    get_short_id.short_description = 'Ticket ID'
    get_short_id.admin_order_field = 'id'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at', 'ticket__status']
    search_fields = ['content', 'author__username', 'ticket__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'author')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'ticket', 'uploaded_by', 'file_size_display', 'uploaded_at']
    list_filter = ['uploaded_at', 'ticket__status']
    search_fields = ['filename', 'ticket__title', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_size']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'uploaded_by')
