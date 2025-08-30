"""
Tools and file management models for AI assistants.

This module contains models for managing tools, functions, and file assets.
"""

import uuid
from django.db import models
from .models import TenantScopedModel, Assistant


# ============================================================================
# FILE MANAGEMENT
# ============================================================================

class FileAsset(TenantScopedModel):
    """File storage for RAG and knowledge base."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='assistant_files/%Y/%m/')
    file_type = models.CharField(max_length=64)
    size_bytes = models.PositiveIntegerField()
    
    # Processing metadata
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'processing_status']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.client_id})"


class AssistantFile(TenantScopedModel):
    """Many-to-many relationship between assistants and files."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_asset = models.ForeignKey(
        FileAsset,
        on_delete=models.CASCADE,
        related_name='assistants'
    )
    
    # Usage configuration
    use_for_rag = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('assistant', 'file_asset')]
        indexes = [
            models.Index(fields=['client_id', 'assistant']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} -> {self.file_asset.name}"


# ============================================================================
# TOOLS & FUNCTIONS
# ============================================================================

class ToolLibrary(TenantScopedModel):
    """Library of available tools for assistants."""
    name = models.CharField(max_length=128)
    description = models.TextField()
    tool_type = models.CharField(
        max_length=20,
        choices=[
            ('webhook', 'Webhook'),
            ('function', 'Function'),
            ('api', 'API Integration'),
        ]
    )
    schema = models.JSONField(help_text="OpenAPI/JSON schema definition")
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'tool_type', 'is_active']),
        ]
        unique_together = [('client_id', 'name')]

    def __str__(self) -> str:
        return f"{self.name} ({self.tool_type})"


class AssistantTool(TenantScopedModel):
    """Many-to-many relationship for assistant tools with overrides."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='tools'
    )
    tool = models.ForeignKey(
        ToolLibrary,
        on_delete=models.CASCADE,
        related_name='assistant_usages'
    )
    
    # Configuration overrides
    is_enabled = models.BooleanField(default=True)
    config_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text="Assistant-specific tool configuration"
    )
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('assistant', 'tool')]
        indexes = [
            models.Index(fields=['client_id', 'assistant', 'is_enabled']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} -> {self.tool.name}"


class PredefinedFunctions(TenantScopedModel):
    """Built-in function toggles for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='predefined_functions'
    )
    
    # Common predefined functions
    enable_end_call = models.BooleanField(default=False)
    enable_transfer = models.BooleanField(default=False)
    enable_voicemail_detection = models.BooleanField(default=False)
    
    # Integration tools
    email_integration = models.BooleanField(default=False, help_text="Enable email sending capabilities")
    sms_integration = models.BooleanField(default=False, help_text="Enable SMS sending capabilities")

    class Meta:
        indexes = [
            models.Index(fields=['client_id']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - Predefined Functions"


class CustomFunction(TenantScopedModel):
    """Custom function definitions for assistants."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='custom_functions'
    )
    name = models.CharField(max_length=128)
    description = models.TextField()
    
    # Function definition
    function_schema = models.JSONField(help_text="OpenAPI function schema")
    endpoint_url = models.URLField(help_text="Function execution endpoint")
    
    # Configuration
    is_enabled = models.BooleanField(default=True)
    timeout_seconds = models.PositiveIntegerField(default=30)

    class Meta:
        unique_together = [('assistant', 'name')]
        indexes = [
            models.Index(fields=['client_id', 'assistant', 'is_enabled']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - {self.name}"


# ============================================================================
# WEBSITE SCRAPING
# ============================================================================

class WebsiteScraping(TenantScopedModel):
    """Website URLs to scrape for knowledge base enhancement."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='scraped_websites'
    )
    url = models.URLField(help_text="Website URL to scrape")
    name = models.CharField(
        max_length=128,
        help_text="Display name for the website"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the website content"
    )
    
    # Scraping configuration
    is_active = models.BooleanField(default=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    scraping_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('scraping', 'Scraping'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Content storage
    scraped_content = models.TextField(
        blank=True,
        help_text="Scraped content from the website"
    )
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Hash of the scraped content for change detection"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Error message if scraping failed"
    )
    retry_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the website"
    )

    class Meta:
        unique_together = [('assistant', 'url')]
        indexes = [
            models.Index(fields=['client_id', 'assistant', 'is_active']),
            models.Index(fields=['client_id', 'scraping_status']),
            models.Index(fields=['last_scraped']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - {self.name} ({self.url})"

    def get_domain(self):
        """Extract domain from URL for display purposes."""
        from urllib.parse import urlparse
        parsed = urlparse(self.url)
        return parsed.netloc

    def mark_scraped(self, content, content_hash):
        """Mark website as successfully scraped."""
        from django.utils import timezone
        self.scraped_content = content
        self.content_hash = content_hash
        self.scraping_status = 'completed'
        self.last_scraped = timezone.now()
        self.error_message = ''
        self.retry_count = 0
        self.save()

    def mark_failed(self, error_message):
        """Mark website scraping as failed."""
        from django.utils import timezone
        self.scraping_status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()