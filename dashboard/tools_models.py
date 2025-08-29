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
    enable_dial_keypad = models.BooleanField(default=False)
    enable_transfer = models.BooleanField(default=False)
    enable_voicemail_detection = models.BooleanField(default=False)
    
    # Forwarding configuration
    forwarding_country = models.CharField(
        max_length=2,
        default='us',
        help_text="ISO country code"
    )
    forwarding_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number for call forwarding"
    )

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


