"""
Configuration models for AI assistants.

This module contains all the configuration models that relate to Assistant.
Split from main models.py for better organization.
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    TenantScopedModel, Assistant, ModelProvider, FirstMessageMode,
    VoiceProvider, BackgroundSound, TranscriberProvider, SuccessRubric,
    AudioFormat, AmbientSoundType, ThinkingSoundType
)


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

class ModelConfig(TenantScopedModel):
    """AI model configuration for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='model_config'
    )
    
    # Core model settings
    provider = models.CharField(
        max_length=20,
        choices=ModelProvider.choices,
        default=ModelProvider.AZURE_OPENAI
    )
    model_name = models.CharField(
        max_length=64,
        default='gpt-4o-realtime',
        help_text="Specific model version"
    )
    
    # Message configuration
    first_message_mode = models.CharField(
        max_length=20,
        choices=FirstMessageMode.choices,
        default=FirstMessageMode.ASSISTANT_FIRST
    )
    first_message = models.TextField(
        blank=True,
        help_text="Initial message from assistant"
    )
    system_prompt = models.TextField(
        blank=True,
        help_text="System instructions for the AI"
    )
    
    # Model parameters
    max_tokens = models.PositiveIntegerField(
        default=250,
        validators=[MinValueValidator(1), MaxValueValidator(4096)]
    )
    temperature = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.50'),
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Provider-specific settings (JSON for flexibility)
    provider_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific configuration options"
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'provider']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - {self.provider} {self.model_name}"


class Voice(TenantScopedModel):
    """Available voice options for different providers."""
    provider = models.CharField(
        max_length=20,
        choices=VoiceProvider.choices,
        help_text="Voice provider (openai, elevenlabs, etc.)"
    )
    name = models.CharField(
        max_length=64,
        help_text="Display name of the voice"
    )
    voice_id = models.CharField(
        max_length=128,
        help_text="Provider-specific voice identifier"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description for the voice"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('provider', 'voice_id')]
        indexes = [
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['client_id', 'provider']),
        ]

    def __str__(self) -> str:
        return f"{self.provider}: {self.name}"


class VoiceConfig(TenantScopedModel):
    """Voice synthesis configuration for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='voice_config'
    )
    
    # Voice selection
    voice = models.ForeignKey(
        Voice,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        help_text="Selected voice from available options"
    )
    
    # Background audio
    background_sound = models.CharField(
        max_length=20,
        choices=BackgroundSound.choices,
        default=BackgroundSound.DEFAULT
    )
    background_sound_url = models.URLField(
        blank=True,
        help_text="Custom background sound URL"
    )
    
    # Voice processing settings
    input_min_characters = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    punctuation_boundaries = models.JSONField(
        default=list,
        blank=True,
        help_text="Punctuation marks for speech chunking"
    )
    
    # Ambient sound configuration
    ambient_sound_enabled = models.BooleanField(
        default=False,
        help_text="Enable ambient background sound"
    )
    ambient_sound_type = models.CharField(
        max_length=20,
        choices=AmbientSoundType.choices,
        default=AmbientSoundType.OFFICE_AMBIENCE,
        help_text="Type of ambient sound to play"
    )
    ambient_sound_volume = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('10.0'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Ambient sound volume (0-100)"
    )
    ambient_sound_url = models.URLField(
        blank=True,
        help_text="Custom ambient sound URL"
    )
    
    # Thinking sound configuration
    thinking_sound_enabled = models.BooleanField(
        default=False,
        help_text="Enable thinking sound when agent is processing"
    )
    thinking_sound_primary = models.CharField(
        max_length=20,
        choices=ThinkingSoundType.choices,
        default=ThinkingSoundType.KEYBOARD_TYPING,
        help_text="Primary thinking sound"
    )
    thinking_sound_primary_volume = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.8'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Primary thinking sound volume (0-1)"
    )
    thinking_sound_secondary = models.CharField(
        max_length=20,
        choices=ThinkingSoundType.choices,
        default=ThinkingSoundType.KEYBOARD_TYPING2,
        help_text="Secondary thinking sound"
    )
    thinking_sound_secondary_volume = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.7'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Secondary thinking sound volume (0-1)"
    )
    
    # Provider-specific settings
    provider_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific voice configuration"
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id']),
        ]

    def __str__(self) -> str:
        voice_name = self.voice.name if self.voice else "No Voice"
        return f"{self.assistant.name} - {voice_name}"


class TranscriberConfig(TenantScopedModel):
    """Speech-to-text configuration for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='stt_config'
    )
    
    # Provider settings
    provider = models.CharField(
        max_length=20,
        choices=TranscriberProvider.choices,
        default=TranscriberProvider.DEEPGRAM
    )
    language = models.CharField(
        max_length=10,
        default='en',
        help_text="Primary language code (ISO 639-1)"
    )
    model_name = models.CharField(
        max_length=64,
        default='nova-3',
        help_text="Transcription model version"
    )
    
    # Quality settings
    background_denoising = models.BooleanField(default=True)
    confidence_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.40'),
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    use_numerals = models.BooleanField(
        default=True,
        help_text="Convert spoken numbers to digits"
    )
    
    # Domain-specific configuration
    keyterms = models.JSONField(
        default=list,
        blank=True,
        help_text="Important terms for transcription accuracy"
    )
    
    # Provider-specific settings
    provider_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific transcription options"
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'provider']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - {self.provider} {self.model_name}"


class AnalyticsConfig(TenantScopedModel):
    """Analytics and evaluation configuration for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    # Summary configuration
    summary_prompt = models.TextField(
        default="You are an expert note-taker. You will be given a transcript of a call. Summarize the call in 2-3 sentences, if applicable.",
        help_text="Prompt for call summarization"
    )
    summary_timeout_sec = models.PositiveIntegerField(default=10)
    min_messages_for_summary = models.PositiveIntegerField(default=2)
    
    # Success evaluation
    success_prompt = models.TextField(
        default="You are an expert call evaluator. You will be given a transcript of a call and the system prompt of the AI participant. Determine if the call was successful based on the objectives inferred from the system prompt.",
        help_text="Prompt for success evaluation"
    )
    success_rubric = models.CharField(
        max_length=20,
        choices=SuccessRubric.choices,
        default=SuccessRubric.NUMERIC
    )
    success_timeout_sec = models.PositiveIntegerField(default=11)
    
    # Structured data extraction
    structured_prompt = models.TextField(
        blank=True,
        help_text="Prompt for extracting structured data"
    )
    structured_schema = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON schema for structured data extraction"
    )
    structured_timeout_sec = models.PositiveIntegerField(default=10)

    class Meta:
        indexes = [
            models.Index(fields=['client_id']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - Analytics"


class PrivacyConfig(TenantScopedModel):
    """Privacy and compliance settings for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='privacy'
    )
    
    # Compliance flags
    hipaa_enabled = models.BooleanField(
        default=False,
        help_text="HIPAA compliance mode - no logs/recordings stored"
    )
    pci_enabled = models.BooleanField(
        default=False,
        help_text="PCI compliance mode - restricted providers only"
    )
    
    # Recording settings
    audio_recording = models.BooleanField(default=True)
    video_recording = models.BooleanField(default=False)
    audio_format = models.CharField(
        max_length=10,
        choices=AudioFormat.choices,
        default=AudioFormat.WAV
    )
    
    # Data retention
    data_retention_days = models.PositiveIntegerField(
        default=90,
        help_text="Days to retain call data (0 = indefinite)"
    )
    auto_delete_recordings = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['client_id', 'hipaa_enabled']),
            models.Index(fields=['client_id', 'pci_enabled']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - Privacy Config"


class AdvancedConfig(TenantScopedModel):
    """Advanced configuration options for assistants."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='advanced_config'
    )
    
    # Speech timing settings
    start_speaking_wait_seconds = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.4'),
        help_text="Seconds to wait before assistant starts speaking"
    )
    smart_endpointing = models.CharField(
        max_length=10,
        choices=[('off', 'Off'), ('on', 'On'), ('auto', 'Auto')],
        default='off'
    )
    on_punctuation_seconds = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.1')
    )
    on_no_punctuation_seconds = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('1.5')
    )
    on_number_seconds = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.5')
    )
    
    # Interruption handling
    stop_speaking_words = models.PositiveIntegerField(default=10)
    stop_speaking_voice_seconds = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('0.2')
    )
    stop_speaking_backoff_seconds = models.PositiveIntegerField(default=1)
    
    # Call timeout settings
    silence_timeout_seconds = models.PositiveIntegerField(default=30)
    max_duration_seconds = models.PositiveIntegerField(default=600)
    
    # Voicemail detection
    voicemail_detection_provider = models.CharField(
        max_length=20,
        choices=[
            ('off', 'Off'),
            ('vapi', 'Vapi'),
            ('google', 'Google'),
            ('openai', 'OpenAI'),
            ('twilio', 'Twilio'),
        ],
        default='off'
    )
    
    # Keypad input
    keypad_input_enabled = models.BooleanField(default=True)
    keypad_timeout_seconds = models.PositiveIntegerField(default=2)
    keypad_delimiter = models.CharField(
        max_length=5,
        default='#,*',
        help_text="Comma-separated delimiters"
    )
    
    # Idle messages
    max_idle_messages = models.PositiveIntegerField(default=3)
    idle_timeout_seconds = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('7.5')
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - Advanced Config"


class MessagingConfig(TenantScopedModel):
    """Message configuration for server and client communication."""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='messaging'
    )
    
    # Server settings
    server_url = models.URLField(blank=True)
    secret_token = models.CharField(max_length=255, blank=True)
    timeout_seconds = models.PositiveIntegerField(default=20)
    
    # HTTP headers for server requests
    http_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom HTTP headers for server requests"
    )
    
    # Message types configuration
    client_messages = models.JSONField(
        default=list,
        blank=True,
        help_text="Message types sent to client SDKs"
    )
    server_messages = models.JSONField(
        default=list,
        blank=True,
        help_text="Message types sent to server URL"
    )
    
    # End-of-call messages
    voicemail_message = models.TextField(
        blank=True,
        help_text="Message for voicemail scenarios"
    )
    end_call_message = models.TextField(
        blank=True,
        help_text="Message when call ends"
    )
    idle_messages = models.JSONField(
        default=list,
        blank=True,
        help_text="Messages for user inactivity"
    )

    class Meta:
        indexes = [
            models.Index(fields=['client_id']),
        ]

    def __str__(self) -> str:
        return f"{self.assistant.name} - Messaging Config"


