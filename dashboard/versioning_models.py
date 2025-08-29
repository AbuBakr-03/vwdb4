"""
Versioning and KPI tracking models for AI assistants.

This module contains models for version snapshots and performance metrics.
"""

from decimal import Decimal
from typing import Dict, Any
from django.db import models
from django.contrib.auth.models import User
from .models import TenantScopedModel, Assistant, AssistantStatus


# ============================================================================
# VERSIONING & KPI TRACKING
# ============================================================================

class AssistantVersion(TenantScopedModel):
    """Immutable snapshots of assistant configurations."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=AssistantStatus.choices
    )
    
    # Snapshot of all configurations at publish time
    snapshot_data = models.JSONField(
        help_text="Complete configuration snapshot"
    )
    
    # Metadata
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [('assistant', 'version_number')]
        indexes = [
            models.Index(fields=['client_id', 'assistant', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} v{self.version_number}"

    @classmethod
    def create_from_assistant(cls, assistant: Assistant) -> 'AssistantVersion':
        """Create a version snapshot from current assistant state."""
        latest_version = cls.objects.filter(assistant=assistant).order_by('-version_number').first()
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        # Create snapshot of all related configurations
        snapshot = {
            'assistant': {
                'name': assistant.name,
                'description': assistant.description,
                'status': assistant.status,
            },
            'model_config': cls._serialize_config(getattr(assistant, 'model_config', None)),
            'voice_config': cls._serialize_config(getattr(assistant, 'voice_config', None)),
            'stt_config': cls._serialize_config(getattr(assistant, 'stt_config', None)),
            'analytics': cls._serialize_config(getattr(assistant, 'analytics', None)),
            'privacy': cls._serialize_config(getattr(assistant, 'privacy', None)),
            'advanced_config': cls._serialize_config(getattr(assistant, 'advanced_config', None)),
            'messaging': cls._serialize_config(getattr(assistant, 'messaging', None)),
        }
        
        return cls.objects.create(
            assistant=assistant,
            client_id=assistant.client_id,
            version_number=next_version,
            status=assistant.status,
            snapshot_data=snapshot,
            published_by=assistant.published_by
        )

    @staticmethod
    def _serialize_config(config_obj) -> Dict[str, Any]:
        """Serialize a configuration object to dict."""
        if not config_obj:
            return {}
        
        data = {}
        for field in config_obj._meta.fields:
            if field.name in ['id', 'assistant', 'client_id', 'created_at', 'updated_at']:
                continue
            value = getattr(config_obj, field.name)
            if isinstance(value, Decimal):
                data[field.name] = float(value)
            else:
                data[field.name] = value
        return data


class AssistantKPI(TenantScopedModel):
    """Daily KPI rollups for assistant performance metrics."""
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='kpis'
    )
    date = models.DateField(db_index=True)
    
    # Call metrics
    total_calls = models.PositiveIntegerField(default=0)
    successful_calls = models.PositiveIntegerField(default=0)
    failed_calls = models.PositiveIntegerField(default=0)
    
    # Duration metrics
    total_duration_seconds = models.PositiveIntegerField(default=0)
    average_duration_seconds = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Quality metrics
    average_latency_ms = models.PositiveIntegerField(default=0)
    asr_word_error_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Cost metrics
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.00')
    )
    cost_per_minute = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.00')
    )

    class Meta:
        unique_together = [('assistant', 'date')]
        indexes = [
            models.Index(fields=['client_id', 'date']),
            models.Index(fields=['assistant', 'date']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - {self.date}"


