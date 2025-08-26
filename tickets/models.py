from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid


class Company(models.Model):
    """
    Represents partner companies that have external QA testers.
    """
    name = models.CharField(max_length=200, help_text="Company name")
    description = models.TextField(blank=True, help_text="Company description")
    contact_email = models.EmailField(help_text="Primary contact email")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    is_active = models.BooleanField(default=True, help_text="Whether the company is active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tickets_company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_active_testers_count(self):
        """Get count of active QA testers for this company."""
        return self.qa_testers.filter(is_active=True).count()


class QATester(models.Model):
    """
    External QA testers from partner companies.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='qa_tester')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='qa_testers')
    is_active = models.BooleanField(default=True, help_text="Whether the tester is active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tickets_qa_tester'
        verbose_name = 'QA Tester'
        verbose_name_plural = 'QA Testers'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name}"


class Ticket(models.Model):
    """
    Represents a ticket submitted by users for QA issues.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('campaigns', 'Campaigns'),
        ('analytics', 'Analytics'),
        ('accounts', 'Accounts'),
        ('authorization', 'Authorization'),
        ('tenants', 'Tenants'),
        ('other', 'Other'),
    ]
    
    # Basic ticket information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Short description of the issue")
    description = models.TextField(help_text="Detailed explanation of the problem")
    issue_location = models.CharField(
        max_length=50, 
        choices=MODULE_CHOICES, 
        default='other',
        help_text="Module where the issue occurred"
    )
    additional_notes = models.TextField(blank=True, help_text="Optional notes or clarifications")
    
    # Status and priority
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open',
        help_text="Current status of the ticket"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        help_text="Priority level of the ticket"
    )
    
    # User and company information
    submitter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='submitted_tickets',
        help_text="User who submitted the ticket"
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        null=True, 
        blank=True,
        help_text="Company associated with the ticket (for external testers)"
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='assigned_tickets',
        null=True, 
        blank=True,
        help_text="QA personnel assigned to resolve the ticket"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tickets_ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['issue_location']),
            models.Index(fields=['created_at']),
            models.Index(fields=['submitter']),
            models.Index(fields=['company']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"#{self.id.hex[:8]} - {self.title}"
    
    def get_short_id(self):
        """Get shortened version of ticket ID for display."""
        return self.id.hex[:8].upper()
    
    def is_resolved(self):
        """Check if ticket is resolved."""
        return self.status in ['resolved', 'closed']
    
    def can_be_assigned(self, user):
        """Check if user can be assigned to this ticket."""
        # Only QA personnel can be assigned
        return user.is_staff or user.groups.filter(name='QA Personnel').exists()
    
    def get_resolution_time(self):
        """Calculate time taken to resolve the ticket."""
        if self.resolved_at and self.created_at:
            return self.resolved_at - self.created_at
        return None


class TicketComment(models.Model):
    """
    Comments added to tickets for communication between users.
    """
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="Ticket this comment belongs to"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ticket_comments',
        help_text="User who wrote the comment"
    )
    content = models.TextField(help_text="Comment content")
    is_internal = models.BooleanField(
        default=False, 
        help_text="Internal comment only visible to QA personnel"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tickets_ticket_comment'
        verbose_name = 'Ticket Comment'
        verbose_name_plural = 'Ticket Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.get_short_id()}"


class TicketAttachment(models.Model):
    """
    File attachments for tickets (screenshots, documents, etc.).
    """
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        help_text="Ticket this attachment belongs to"
    )
    file = models.FileField(
        upload_to='ticket_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
        )],
        help_text="Uploaded file (screenshots, documents, etc.)"
    )
    filename = models.CharField(max_length=255, help_text="Original filename")
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ticket_attachments',
        help_text="User who uploaded the file"
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'tickets_ticket_attachment'
        verbose_name = 'Ticket Attachment'
        verbose_name_plural = 'Ticket Attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.ticket.get_short_id()}"
    
    def get_file_size_display(self):
        """Get human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
