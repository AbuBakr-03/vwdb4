"""
Redis Queue Service for Campaign Publishing.

This service handles publishing campaign messages to the Redis queue
with all necessary metadata for the AI agent to function properly.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
import redis

logger = logging.getLogger(__name__)


class CampaignQueueService:
    """
    Service for publishing campaign messages to Redis queue.
    
    This service ensures that when a campaign is published, all necessary
    metadata is included in the message for the AI agent to function properly.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the queue service.
        
        Args:
            redis_url: Redis connection URL (defaults to Django REDIS_URL setting)
        """
        if redis_url:
            self.redis_url = redis_url
        else:
            # Use Django settings if available, fallback to env var
            try:
                from django.conf import settings
                if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                    self.redis_url = settings.REDIS_URL
                else:
                    # Fallback to environment variable or default
                    self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
            except:
                # Django not available, use env var or default
                self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established for campaign queue service")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _ensure_connection(self):
        """Ensure Redis connection is available."""
        if not self.redis_client:
            self._connect()
        if not self.redis_client:
            raise ConnectionError("Cannot establish Redis connection")
    
    def _get_assistant_metadata(self, assistant) -> Dict[str, Any]:
        """
        Extract all assistant configuration metadata.
        
        Args:
            assistant: Assistant model instance
            
        Returns:
            Dictionary containing all assistant configurations
        """
        try:
            metadata = {
                # Basic assistant info
                'assistant_id': str(assistant.id),
                'external_id': assistant.external_id,
                'name': assistant.name,
                'slug': assistant.slug,
                'description': assistant.description,
                'status': assistant.status,
                'published_at': assistant.published_at.isoformat() if assistant.published_at else None,
                
                # Model configuration
                'model_config': {},
                'voice_config': {},
                'transcriber_config': {},
                'analytics_config': {},
                'privacy_config': {},
                'advanced_config': {},
                'tools_config': {},
                
                # Timestamps
                'created_at': assistant.created_at.isoformat(),
                'updated_at': assistant.updated_at.isoformat(),
            }
            
            # Add model configuration if available
            if hasattr(assistant, 'model_config') and assistant.model_config:
                model_config = assistant.model_config
                metadata['model_config'] = {
                    'provider': getattr(model_config, 'provider', 'openai'),
                    'model_name': getattr(model_config, 'model_name', 'gpt-4'),
                    'first_message_mode': getattr(model_config, 'first_message_mode', 'system'),
                    'first_message': getattr(model_config, 'first_message', ''),
                    'system_prompt': getattr(model_config, 'system_prompt', ''),
                    'provider_settings': getattr(model_config, 'provider_settings', {}),
                }
            
            # Add voice configuration if available
            if hasattr(assistant, 'voice_config'):
                voice_config = assistant.voice_config
                metadata['voice_config'] = {
                    'provider': voice_config.provider_settings.get('provider', 'elevenlabs'),
                    'voice_id': str(voice_config.voice.id) if voice_config.voice else None,
                    'background_sound': getattr(voice_config, 'background_sound', 'default'),
                    'background_sound_url': getattr(voice_config, 'background_sound_url', ''),
                    'ambient_sound_enabled': getattr(voice_config, 'ambient_sound_enabled', False),
                    'ambient_sound_type': getattr(voice_config, 'ambient_sound_type', 'office_ambience'),
                    'ambient_sound_volume': getattr(voice_config, 'ambient_sound_volume', 10.0),
                    'ambient_sound_url': getattr(voice_config, 'ambient_sound_url', ''),
                    'thinking_sound_enabled': getattr(voice_config, 'thinking_sound_enabled', False),
                    'thinking_sound_primary': getattr(voice_config, 'thinking_sound_primary', 'keyboard_typing'),
                    'thinking_sound_primary_volume': getattr(voice_config, 'thinking_sound_primary_volume', 0.8),
                    'thinking_sound_secondary': getattr(voice_config, 'thinking_sound_secondary', 'keyboard_typing2'),
                    'thinking_sound_secondary_volume': getattr(voice_config, 'thinking_sound_secondary_volume', 0.7),
                    'provider_settings': getattr(voice_config, 'provider_settings', {}),
                }
            
            # Add transcriber configuration if available
            if hasattr(assistant, 'transcriber_config') and assistant.transcriber_config:
                transcriber_config = assistant.transcriber_config
                metadata['transcriber_config'] = {
                    'provider': getattr(transcriber_config, 'provider', 'whisper'),
                    'language': getattr(transcriber_config, 'language', 'en-US'),
                    'model': getattr(transcriber_config, 'model', ''),
                    'enable_profanity_filter': getattr(transcriber_config, 'enable_profanity_filter', False),
                    'enable_auto_punctuation': getattr(transcriber_config, 'enable_auto_punctuation', True),
                    'enable_speaker_diarization': getattr(transcriber_config, 'enable_speaker_diarization', False),
                    'provider_settings': getattr(transcriber_config, 'provider_settings', {}),
                }
            
            # Add analytics configuration if available
            if hasattr(assistant, 'analytics_config') and assistant.analytics_config:
                analytics_config = assistant.analytics_config
                metadata['analytics_config'] = {
                    'track_conversation_metrics': getattr(analytics_config, 'track_conversation_metrics', True),
                    'track_sentiment_analysis': getattr(analytics_config, 'track_sentiment_analysis', False),
                    'track_intent_recognition': getattr(analytics_config, 'track_intent_recognition', False),
                    'success_rubric': getattr(analytics_config, 'success_rubric', 'numeric'),
                    'custom_success_criteria': getattr(analytics_config, 'custom_success_criteria', ''),
                    'enable_recording': getattr(analytics_config, 'enable_recording', True),
                    'retention_days': getattr(analytics_config, 'retention_days', 90),
                }
            
            # Add privacy configuration if available
            if hasattr(assistant, 'privacy_config') and assistant.privacy_config:
                privacy_config = assistant.privacy_config
                metadata['privacy_config'] = {
                    'data_retention_days': getattr(privacy_config, 'data_retention_days', 90),
                    'enable_data_anonymization': getattr(privacy_config, 'enable_data_anonymization', False),
                    'compliance_standards': getattr(privacy_config, 'compliance_standards', []),
                    'data_processing_consent': getattr(privacy_config, 'data_processing_consent', True),
                }
            
            # Add advanced configuration if available
            if hasattr(assistant, 'advanced_config') and assistant.advanced_config:
                advanced_config = assistant.advanced_config
                metadata['advanced_config'] = {
                    'max_conversation_turns': getattr(advanced_config, 'max_conversation_turns', 50),
                    'timeout_seconds': getattr(advanced_config, 'timeout_seconds', 300),
                    'enable_fallback_responses': getattr(advanced_config, 'enable_fallback_responses', True),
                    'custom_headers': getattr(advanced_config, 'custom_headers', {}),
                    'webhook_urls': getattr(advanced_config, 'webhook_urls', []),
                }
            
            # Add tools configuration if available
            if hasattr(assistant, 'predefined_functions') and assistant.predefined_functions:
                predefined_functions = assistant.predefined_functions
                metadata['tools_config'] = {
                    'predefined_functions': getattr(predefined_functions, 'enabled_functions', []),
                    'custom_functions': [],
                }
            
            # Add custom functions if available
            if hasattr(assistant, 'assistant_tools') and hasattr(assistant.assistant_tools, 'all'):
                custom_functions = []
                try:
                    for tool in assistant.assistant_tools.all():
                        if hasattr(tool, 'custom_function') and tool.custom_function:
                            custom_functions.append({
                                'name': getattr(tool.custom_function, 'name', ''),
                                'description': getattr(tool.custom_function, 'description', ''),
                                'parameters': getattr(tool.custom_function, 'parameters', {}),
                                'is_active': getattr(tool, 'is_active', True),
                            })
                    if 'tools_config' in metadata:
                        metadata['tools_config']['custom_functions'] = custom_functions
                except Exception as e:
                    logger.warning(f"Error processing assistant tools: {e}")
            
            # Ensure all values are string-safe
            safe_metadata = {}
            for key, value in metadata.items():
                safe_metadata[key] = self._safe_convert_value(value)
            
            return safe_metadata
            
        except Exception as e:
            logger.error(f"Error extracting assistant metadata: {e}")
            return {
                'assistant_id': str(assistant.id),
                'name': assistant.name,
                'error': f"Failed to extract metadata: {str(e)}"
            }
    
    def _get_scheduling_details(self, campaign) -> Dict[str, Any]:
        """
        Extract campaign scheduling details.
        
        Args:
            campaign: Campaign model instance
            
        Returns:
            Dictionary containing scheduling information
        """
        return {
            'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
            'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
            'max_calls': campaign.max_calls,
            'max_concurrent': campaign.max_concurrent,
            'priority': campaign.priority,
            'launched_at': timezone.now().isoformat(),
        }
    
    def publish_campaign(self, campaign, phone_numbers: list) -> Dict[str, Any]:
        """
        Publish a campaign to the Redis queue.
        
        Args:
            campaign: Campaign model instance
            phone_numbers: List of phone numbers to call
            
        Returns:
            Dictionary with publish results
        """
        try:
            self._ensure_connection()
            
            if not campaign.assistant:
                raise ValueError("Campaign must have an associated assistant")
            
            # Extract all necessary data
            campaign_data = {
                'campaign_id': str(campaign.id),
                'campaign_name': campaign.name,
                'description': campaign.description,
                'prompt_template': campaign.prompt_template,
                'voice_id': campaign.voice_id,
                'agent_config': campaign.agent_config,
                'tenant_id': campaign.tenant_id,
                'created_by': campaign.created_by.username,
            }
            
            assistant_metadata = self._get_assistant_metadata(campaign.assistant)
            scheduling_details = self._get_scheduling_details(campaign)
            
            # Create the complete message structure
            message_data = {
                'message_type': 'campaign_launch',
                'timestamp': timezone.now().isoformat(),
                'campaign_data': campaign_data,
                'assistant_metadata': assistant_metadata,
                'scheduling_details': scheduling_details,
                'phone_numbers': phone_numbers,
                'total_calls': len(phone_numbers),
                'status': 'queued',
                'retry_count': 0,
                'max_retries': 3,
                'retry_interval_min': 5,  # 5 minutes between retries
            }
            
            # Publish to Redis stream
            stream_name = f"campaign_queue:{campaign.tenant_id}"
            
            # Add message to stream
            message_id = self.redis_client.xadd(
                stream_name,
                self._flatten_dict(message_data),
                maxlen=1000,  # Keep last 1000 messages
                approximate=True
            )
            
            # Convert bytes message_id to string if needed
            if isinstance(message_id, bytes):
                message_id = message_id.decode('utf-8', errors='ignore')
            
            logger.info(f"Campaign {campaign.id} published to queue with message ID: {message_id}")
            
            return {
                'success': True,
                'message_id': message_id,
                'stream_name': stream_name,
                'total_calls': len(phone_numbers),
                'published_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to publish campaign {campaign.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'campaign_id': campaign.id
            }
    
    def get_queue_status(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get the current status of the campaign queue.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dictionary with queue status information
        """
        try:
            self._ensure_connection()
            
            stream_name = f"campaign_queue:{tenant_id}"
            
            # Get stream length
            stream_length = self.redis_client.xlen(stream_name)
            
            # Get pending messages count
            pending_count = 0
            try:
                # Try to get consumer group info
                groups = self.redis_client.xinfo_groups(stream_name)
                for group in groups:
                    pending_count += group['pending']
            except:
                # Stream or group doesn't exist yet
                pass
            
            return {
                'stream_name': stream_name,
                'total_messages': stream_length,
                'pending_messages': pending_count,
                'status': 'active' if stream_length > 0 else 'empty'
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status for tenant {tenant_id}: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def close(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None

    def _safe_convert_value(self, value):
        """Safely convert any value to a string for Redis compatibility."""
        if value is None:
            return ''
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        elif isinstance(value, (dict, list)):
            return str(value)
        else:
            return str(value)

    def _flatten_dict(self, data, prefix=''):
        """Flatten nested dictionary for Redis compatibility."""
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict):
                flattened.update(self._flatten_dict(value, f"{prefix}{key}_"))
            elif isinstance(value, list):
                flattened[f"{prefix}{key}"] = self._safe_convert_value(value)
            else:
                flattened[f"{prefix}{key}"] = self._safe_convert_value(value)
        return flattened
