"""
Django admin registration for AI Assistant models.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Assistant, ModelConfig, VoiceConfig, TranscriberConfig,
    AnalyticsConfig, PrivacyConfig, AdvancedConfig, MessagingConfig,
    PredefinedFunctions, CustomFunction, AssistantVersion, AssistantKPI
)
from .config_models import Voice
from .tools_models import (
    FileAsset, AssistantFile, ToolLibrary, AssistantTool,
    WebsiteScraping
)


# ============================================================================
# INLINE ADMINS
# ============================================================================

class ModelConfigInline(admin.StackedInline):
    model = ModelConfig
    extra = 0


class VoiceConfigInline(admin.StackedInline):
    model = VoiceConfig
    extra = 0


class TranscriberConfigInline(admin.StackedInline):
    model = TranscriberConfig
    extra = 0


class PredefinedFunctionsInline(admin.StackedInline):
    model = PredefinedFunctions
    extra = 0


# ============================================================================
# MAIN ADMIN CLASSES
# ============================================================================

@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'client_id', 'total_calls', 'published_at')
    list_filter = ('status', 'client_id', 'published_at')
    search_fields = ('name', 'description', 'external_id')
    readonly_fields = ('id', 'external_id', 'slug', 'published_at', 'published_by')
    
    inlines = [
        ModelConfigInline,
        VoiceConfigInline, 
        TranscriberConfigInline,
        PredefinedFunctionsInline,
    ]


@admin.register(ModelConfig)
class ModelConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'provider', 'model_name')
    list_filter = ('provider', 'first_message_mode')


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'voice_id', 'is_active')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'voice_id', 'description')


@admin.register(VoiceConfig)
class VoiceConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'voice', 'background_sound')
    list_filter = ('background_sound',)


@admin.register(TranscriberConfig)
class TranscriberConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'provider', 'language', 'model_name')
    list_filter = ('provider', 'language')


@admin.register(AnalyticsConfig)
class AnalyticsConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'success_rubric', 'summary_timeout_sec')
    list_filter = ('success_rubric',)


@admin.register(PrivacyConfig)
class PrivacyConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'hipaa_enabled', 'pci_enabled', 'audio_recording')
    list_filter = ('hipaa_enabled', 'pci_enabled')


@admin.register(AdvancedConfig)
class AdvancedConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'turn_detection_threshold', 'keypad_input_enabled')
    list_filter = ('turn_detection_create_response', 'turn_detection_interrupt_response', 'keypad_input_enabled')


@admin.register(MessagingConfig)
class MessagingConfigAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'server_url', 'timeout_seconds')
    list_filter = ('timeout_seconds',)


@admin.register(FileAsset)
class FileAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_type', 'size_bytes', 'processing_status')
    list_filter = ('file_type', 'processing_status')


@admin.register(ToolLibrary)
class ToolLibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tool_type', 'is_active')
    list_filter = ('tool_type', 'is_active')


@admin.register(AssistantTool)
class AssistantToolAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'tool', 'is_enabled', 'priority')
    list_filter = ('is_enabled', 'priority')


@admin.register(PredefinedFunctions)
class PredefinedFunctionsAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'enable_end_call', 'enable_dial_keypad')
    list_filter = ('enable_end_call', 'enable_dial_keypad')


@admin.register(CustomFunction)
class CustomFunctionAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'name', 'is_enabled', 'timeout_seconds')
    list_filter = ('is_enabled',)


@admin.register(AssistantVersion)
class AssistantVersionAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'version_number', 'status', 'published_by')
    list_filter = ('status',)
    readonly_fields = ('version_number', 'snapshot_data')


@admin.register(AssistantKPI)
class AssistantKPIAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'date', 'total_calls', 'successful_calls')
    list_filter = ('date',)
    date_hierarchy = 'date'


@admin.register(WebsiteScraping)
class WebsiteScrapingAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'name', 'url', 'scraping_status', 'last_scraped')
    list_filter = ('scraping_status', 'is_active')
    search_fields = ('name', 'url', 'description')
    readonly_fields = ('last_scraped', 'content_hash', 'retry_count')


# Customize admin site
admin.site.site_header = "Watchtower AI Assistant Management"
admin.site.site_title = "Watchtower Admin"
admin.site.index_title = "AI Assistant Management"