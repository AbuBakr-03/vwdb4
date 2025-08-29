"""
Django models for AI Assistant management system.

Follows the Watchtower project guidelines with proper indexing,
multi-tenant support, and comprehensive configuration options.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid


# ============================================================================
# ENUMS & CHOICES
# ============================================================================

class AssistantStatus(models.TextChoices):
    """Status options for assistants."""
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class ModelProvider(models.TextChoices):
    """AI model provider options."""
    OPENAI = 'openai', 'OpenAI'
    ANTHROPIC = 'anthropic', 'Anthropic'
    GOOGLE = 'google', 'Google'
    AZURE = 'azure', 'Azure'


class FirstMessageMode(models.TextChoices):
    """First message behavior options."""
    ASSISTANT_FIRST = 'assistant_first', 'Assistant speaks first'
    USER_FIRST = 'user_first', 'User speaks first'
    BOTH_SPEAK = 'both_speak', 'Both speak'


class VoiceProvider(models.TextChoices):
    """Voice synthesis provider options."""
    VAPI = 'vapi', 'Vapi'
    ELEVENLABS = 'elevenlabs', 'ElevenLabs'
    AZURE = 'azure', 'Azure'
    AWS = 'aws', 'AWS Polly'
    GOOGLE = 'google', 'Google'


class BackgroundSound(models.TextChoices):
    """Background sound options."""
    DEFAULT = 'default', 'Default'
    OFFICE = 'office', 'Office Ambiance'
    CAFE = 'cafe', 'Cafe Noise'
    NATURE = 'nature', 'Nature Sounds'
    RAIN = 'rain', 'Rain'
    NONE = 'none', 'None'
    CUSTOM = 'custom', 'Custom URL'


class TranscriberProvider(models.TextChoices):
    """Speech-to-text provider options."""
    DEEPGRAM = 'deepgram', 'Deepgram'
    OPENAI = 'openai', 'OpenAI Whisper'
    ASSEMBLYAI = 'assemblyai', 'AssemblyAI'
    AZURE = 'azure', 'Azure Speech'
    GOOGLE = 'google', 'Google Speech'


class SuccessRubric(models.TextChoices):
    """Success evaluation rubric options."""
    NUMERIC = 'numeric', 'Numeric Scale (1-10)'
    BINARY = 'binary', 'Binary (Success/Failure)'
    PERCENTAGE = 'percentage', 'Percentage (0-100%)'
    CUSTOM = 'custom', 'Custom'


class AudioFormat(models.TextChoices):
    """Audio recording format options."""
    WAV = 'wav', 'WAV'
    MP3 = 'mp3', 'MP3'
    FLAC = 'flac', 'FLAC'
    OGG = 'ogg', 'OGG'


# ============================================================================
# BASE MODELS
# ============================================================================

class TimestampedModel(models.Model):
    """Base model with timestamps for all entities."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class TenantScopedModel(TimestampedModel):
    """Base model with client scoping for multi-tenant support."""
    client_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Tenant/client identifier for multi-tenant scoping"
    )

    class Meta:
        abstract = True


# ============================================================================
# CORE ASSISTANT MODEL
# ============================================================================

class Assistant(TenantScopedModel):
    """
    Core assistant model with versioning and multi-tenant support.
    
    Represents an AI assistant configuration with all related settings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(
        max_length=128,
        unique=True,
        help_text="External identifier for API integrations"
    )
    name = models.CharField(max_length=128, help_text="Human-readable assistant name")
    slug = models.SlugField(
        max_length=128,
        help_text="URL-friendly identifier, auto-generated from name"
    )
    description = models.TextField(blank=True, help_text="Assistant description")
    
    # Status and publishing
    status = models.CharField(
        max_length=20,
        choices=AssistantStatus.choices,
        default=AssistantStatus.DRAFT,
        db_index=True
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_assistants'
    )
    
    # Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_assistants',
        db_index=True
    )
    
    # Dashboard KPI fields
    total_calls = models.PositiveIntegerField(default=0)
    total_duration_seconds = models.PositiveIntegerField(default=0)
    average_cost_per_minute = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.00')
    )
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'status']),
            models.Index(fields=['client_id', 'owner']),
            models.Index(fields=['external_id']),
            models.Index(fields=['slug']),
        ]
        unique_together = [('client_id', 'slug')]

    def __str__(self) -> str:
        return f"{self.name} ({self.client_id})"

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            base_slug = slugify(self.name)
            
            # Check if slug already exists for this client_id
            counter = 1
            slug = base_slug
            while Assistant.objects.filter(client_id=self.client_id, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)

    def publish(self, user: Optional[User] = None) -> None:
        """Publish the assistant and create a version snapshot."""
        self.status = AssistantStatus.PUBLISHED
        self.published_at = timezone.now()
        self.published_by = user
        self.save()
        
        # Create version snapshot
        from .versioning_models import AssistantVersion  # Avoid circular import
        AssistantVersion.create_from_assistant(self)

    @property
    def current_version(self) -> Optional['AssistantVersion']:
        """Get the latest published version."""
        return self.versions.filter(
            status=AssistantStatus.PUBLISHED
        ).order_by('-created_at').first()


# ============================================================================
# IMPORT ALL RELATED MODELS
# ============================================================================

# Import all configuration models
from .config_models import (
    ModelConfig, VoiceConfig, TranscriberConfig, AnalyticsConfig,
    PrivacyConfig, AdvancedConfig, MessagingConfig
)

# Import tools and file models
from .tools_models import (
    FileAsset, AssistantFile, ToolLibrary, AssistantTool,
    PredefinedFunctions, CustomFunction
)

# Import versioning models
from .versioning_models import AssistantVersion, AssistantKPI


# ============================================================================
# SIGNAL HANDLERS FOR AUTO-CREATION
# ============================================================================

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Assistant)
def create_assistant_configs(sender, instance: Assistant, created: bool, **kwargs):
    """Auto-create related configuration objects when assistant is created."""
    if created:
        # Create all OneToOne related configurations
        ModelConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        VoiceConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        TranscriberConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        AnalyticsConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        PrivacyConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        AdvancedConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        MessagingConfig.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )
        
        PredefinedFunctions.objects.get_or_create(
            assistant=instance,
            client_id=instance.client_id,
            defaults={}
        )


# ============================================================================
# SEED FUNCTION
# ============================================================================

def seed_example_assistant(client_id: str, owner: Optional[User] = None) -> Assistant:
    """
    Create example assistant with realistic configuration.
    
    Args:
        client_id: Tenant identifier
        owner: User who owns the assistant (uses first superuser if None)
    
    Returns:
        Created Assistant instance
    """
    if owner is None:
        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            raise ValueError("No owner provided and no superuser found")
    
    # Create assistant
    assistant = Assistant.objects.create(
        client_id=client_id,
        external_id="dc8d68a4-3d4c-48b8-b0f5",
        name="Riley",
        description="Friendly scheduling assistant for Wellness Partners",
        owner=owner
    )
    
    # Configure model
    mc = assistant.model_config
    mc.provider = ModelProvider.OPENAI
    mc.model_name = "gpt-4o-realtime"
    mc.first_message_mode = FirstMessageMode.ASSISTANT_FIRST
    mc.first_message = (
        "Thank you for calling Wellness Partners. This is Riley, your scheduling assistant. How may I help you today?"
    )
    mc.system_prompt = """You are Riley, a friendly scheduling assistant. Keep answers concise and confirm details."""
    mc.max_tokens = 250
    mc.temperature = Decimal("0.50")
    mc.save()

    # Configure voice
    vc = assistant.voice_config
    vc.provider = VoiceProvider.VAPI
    vc.voice = "Elliot"
    vc.background_sound = BackgroundSound.DEFAULT
    vc.background_sound_url = "https://www.soundjay.com/ambient/sounds/people-in-lounge-1.mp3"
    vc.input_min_characters = 30
    vc.punctuation_boundaries = [".", ",", ";", "?", "!"]
    vc.save()

    # Configure STT
    stt = assistant.stt_config
    stt.provider = TranscriberProvider.DEEPGRAM
    stt.language = "en"
    stt.model_name = "nova-3"
    stt.background_denoising = True
    stt.confidence_threshold = Decimal("0.40")
    stt.use_numerals = True
    stt.keyterms = ["appointment", "ID", "policy"]
    stt.save()

    # Configure predefined functions
    pf = assistant.predefined_functions
    pf.enable_end_call = True
    pf.enable_dial_keypad = True
    pf.forwarding_country = "us"
    pf.forwarding_number = "4257623355"
    pf.save()

    # Configure analytics
    an = assistant.analytics
    an.summary_timeout_sec = 10
    an.min_messages_for_summary = 2
    an.success_rubric = SuccessRubric.NUMERIC
    an.success_timeout_sec = 11
    an.structured_prompt = "Extract appointment date, time, patient name, and callback number if provided."
    an.structured_schema = [
        {"name": "patient_name", "type": "string", "required": True},
        {"name": "appointment_date", "type": "date", "required": False},
        {"name": "appointment_time", "type": "string", "required": False},
        {"name": "callback_number", "type": "string", "required": False},
    ]
    an.save()

    # Publish the assistant
    assistant.publish(owner)
    
    return assistant