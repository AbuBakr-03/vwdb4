from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from authorization.utils import get_tenant_info
from datetime import datetime, timedelta
import random
import json
import uuid

from .models import (
    Assistant, PredefinedFunctions, CustomFunction,
    AssistantVersion, AssistantKPI, ModelProvider, 
    TranscriberProvider, VoiceProvider, BackgroundSound,
    FirstMessageMode, SuccessRubric
)
from .tools_models import (
    FileAsset, AssistantFile, WebsiteScraping
)
from .config_models import (
    Voice, VoiceConfig, TranscriberConfig, AnalyticsConfig,
    PrivacyConfig, AdvancedConfig
)


def home(request):
    """Dashboard home view with tenant information and KPIs."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Mock KPI data - replace with real data from your models
    context['kpis'] = {
        'monthly_subscription_cost': {
            'value': 2450.00,
            'change': +12.5,
            'currency': 'USD'
        },
        'active_users': {
            'value': 1847,
            'change': +8.3,
            'unit': 'users'
        },
        'performance_score': {
            'value': 87.5,
            'change': -2.1,
            'unit': 'score',
            'max': 100
        },
        'average_duration': {
            'value': 14.2,
            'change': +15.7,
            'unit': 'minutes'
        },
        'upsell_ratio': {
            'value': 23.8,
            'change': +4.2,
            'unit': '%'
        },
        'peak_hour': {
            'value': '14:00',
            'change': 0,
            'unit': 'hour'
        },
        'busiest_day': {
            'value': '2024-06-10',
            'change': 0,
            'unit': 'date'
        }
    }
    
    # Generate mock time series data for charts (last 30 days)
    def generate_time_series(base_value, variance=0.1):
        data = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            # Add some realistic variation
            variation = 1 + random.uniform(-variance, variance)
            value = round(base_value * variation, 2)
            data.append({'date': date, 'value': value})
        return data
    
    # Convert chart data to JSON for JavaScript consumption
    context['chart_data'] = {
        'active_users': json.dumps(generate_time_series(1847, 0.15)),
        'performance_score': json.dumps(generate_time_series(87.5, 0.05)),
        'average_duration': json.dumps(generate_time_series(14.2, 0.2)),
        'monthly_cost': json.dumps(generate_time_series(2450, 0.1))
    }
    
    return render(request, "dashboard/index.html", context)


def overview(request):
    """Overview page for voice AI agents dashboard."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'active': True}
    ]
    
    # Mock data for overview page - empty state since no calls yet
    context['overview_data'] = {
        'total_calls': 0,
        'success_rate': 0,
        'average_duration': 0,
        'total_cost': 0.00,
        'has_calls': False,
        'assistants': [
            {'name': 'Customer Support', 'active': True},
            {'name': 'Sales Assistant', 'active': False}, 
            {'name': 'Appointment Booking', 'active': True},
        ]
    }
    
    return render(request, "dashboard/Overview.html", context)


class AssistantsView(LoginRequiredMixin, TemplateView):
    """Assistants page with secondary sidebar."""
    template_name = "dashboard/Assistants.html"
    
    def get_client_id(self):
        """Get client_id from tenant info or use default."""
        return getattr(self.request, 'tenant_flags', {}).get('client_id', 'zain_bh')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add tenant info if available
        if hasattr(self.request, 'tenant_flags'):
            context['tenant_info'] = get_tenant_info(self.request)
        
        client_id = self.get_client_id()
        
        # Organization data for breadcrumbs and components
        context['organization'] = {
            'name': 'Zain Telecom',
            'slug': 'zain_bh',
            'plan': 'Enterprise',
            'credits': 25.50
        }
        
        # Dynamic breadcrumb data
        context['breadcrumb_items'] = [
            {'text': 'Organization', 'href': '/dashboard/'},
            {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
            {'text': 'Assistants', 'active': True}
        ]
        
        # Get assistants from database
        assistants_qs = Assistant.objects.filter(
            client_id=client_id,
            owner=self.request.user
        ).select_related(
            'model_config', 'voice_config', 'stt_config', 'analytics',
            'privacy', 'advanced_config', 'predefined_functions'
        ).order_by('-created_at')
        
        # Get selected assistant from URL parameter
        selected_assistant_id = self.request.GET.get('selected')
        
        # Format assistants data for template
        context['assistants'] = []
        selected_assistant = None
        
        for i, assistant in enumerate(assistants_qs):
            # Check if this assistant is selected via URL parameter or default to first
            is_selected = (
                str(assistant.id) == selected_assistant_id if selected_assistant_id 
                else i == 0 and assistants_qs.count() > 0
            )
            if is_selected:
                selected_assistant = assistant
                
            context['assistants'].append({
                'id': assistant.id,
                'name': assistant.name,
                'description': assistant.description or (getattr(assistant, 'voice_config', None) and getattr(assistant.voice_config, 'voice', None) and assistant.voice_config.voice.name) or 'No description',
                'is_active': assistant.status == 'published',
                'selected': is_selected,
                'status': assistant.status,
                'external_id': assistant.external_id
            })
        
        # Add assistant count to context
        context['assistant_count'] = len(context['assistants'])
        
        # If we have a selected assistant, add its configuration to context
        if selected_assistant:
            context['selected_assistant'] = selected_assistant
            context.update(self._get_assistant_config(selected_assistant))
        else:
            # No assistants - show empty state
            context['show_empty_state'] = True
            context['selected_assistant'] = None
        
        return context
    
    def _get_assistant_config(self, assistant):
        """Extract assistant configuration for template."""
        # Safely get configuration objects
        model_config = getattr(assistant, 'model_config', None)
        voice_config = getattr(assistant, 'voice_config', None)
        stt_config = getattr(assistant, 'stt_config', None)
        analytics = getattr(assistant, 'analytics', None)
        privacy = getattr(assistant, 'privacy', None)
        
        # Get privacy configuration
        privacy_config = {
            'audio_recording': privacy.audio_recording if privacy else True,
        } if privacy else {
            'audio_recording': True,
        }
        
        advanced_config = getattr(assistant, 'advanced_config', None)
        
        config = {
            'assistant_config': {
                'name': assistant.name,
                'status': assistant.status,
                'external_id': assistant.external_id[:20] + '...',
                'model': {
                    'provider': model_config.provider if model_config else 'azure_openai',
                    'model_name': model_config.model_name if model_config else 'gpt-4o-realtime',
                    'first_message_mode': model_config.first_message_mode if model_config else 'assistant_first',
                    'first_message': model_config.first_message if model_config else '',
                    'system_prompt': model_config.system_prompt if model_config else '',
                },
                'voice': {
                    'provider': voice_config.voice.provider if (voice_config and voice_config.voice) else None,
                    'voice': voice_config.voice.name if (voice_config and voice_config.voice) else None,
                    'voice_id': voice_config.voice.voice_id if (voice_config and voice_config.voice) else None,
                    'background_sound': voice_config.background_sound if voice_config else 'default',
                    'background_sound_url': voice_config.background_sound_url if voice_config else '',
                    
                    # Ambient sound configuration
                    'ambient_sound_enabled': voice_config.ambient_sound_enabled if voice_config else False,
                    'ambient_sound_type': voice_config.ambient_sound_type if voice_config else 'office_ambience',
                    'ambient_sound_volume': float(voice_config.ambient_sound_volume) if voice_config else 10.0,
                    'ambient_sound_url': voice_config.ambient_sound_url if voice_config else '',
                    # Thinking sound configuration
                    'thinking_sound_enabled': voice_config.thinking_sound_enabled if voice_config else False,
                    'thinking_sound_primary': voice_config.thinking_sound_primary if voice_config else 'keyboard_typing',
                    'thinking_sound_primary_volume': float(voice_config.thinking_sound_primary_volume) if voice_config else 0.8,
                    'thinking_sound_secondary': voice_config.thinking_sound_secondary if voice_config else 'keyboard_typing2',
                    'thinking_sound_secondary_volume': float(voice_config.thinking_sound_secondary_volume) if voice_config else 0.7,
                },
                'stt': {
                    'provider': stt_config.provider if stt_config else 'deepgram',
                    'language': stt_config.language if stt_config else 'en',
                    'model_name': stt_config.model_name if stt_config else 'nova-3',
                    'background_denoising': stt_config.background_denoising if stt_config else True,
                    'confidence_threshold': float(stt_config.confidence_threshold) if stt_config else 0.40,
                    'use_numerals': stt_config.use_numerals if stt_config else True,
                    'keyterms': stt_config.keyterms if stt_config else [],
                },
                'predefined_functions': {
                    'enable_end_call': getattr(assistant, 'predefined_functions', None) and assistant.predefined_functions.enable_end_call or False,
                    'enable_dial_keypad': getattr(assistant, 'predefined_functions', None) and assistant.predefined_functions.enable_dial_keypad or False,
                    'forwarding_country': getattr(assistant, 'predefined_functions', None) and assistant.predefined_functions.forwarding_country or 'us',
                    'forwarding_number': getattr(assistant, 'predefined_functions', None) and assistant.predefined_functions.forwarding_number or '',
                },
                'analytics': {
                    'summary_timeout_sec': analytics.summary_timeout_sec if analytics else 10,
                    'min_messages_for_summary': analytics.min_messages_for_summary if analytics else 2,
                    'success_rubric': analytics.success_rubric if analytics else 'numeric',
                    'success_timeout_sec': analytics.success_timeout_sec if analytics else 11,
                    'structured_prompt': analytics.structured_prompt if analytics else '',
                    'structured_schema': analytics.structured_schema if analytics else [],
                },
                'privacy': privacy_config,
                'advanced': {
                    'turn_detection_threshold': float(advanced_config.turn_detection_threshold) if advanced_config else 0.89,
                    'turn_detection_silence_duration_ms': advanced_config.turn_detection_silence_duration_ms if advanced_config else 1500,
                    'turn_detection_prefix_padding_ms': advanced_config.turn_detection_prefix_padding_ms if advanced_config else 250,
                    'turn_detection_create_response': advanced_config.turn_detection_create_response if advanced_config else True,
                    'turn_detection_interrupt_response': advanced_config.turn_detection_interrupt_response if advanced_config else True,
                },
            }
        }
        
        # Calculate metrics for the metrics strip
        today = datetime.now().date()
        recent_kpis = AssistantKPI.objects.filter(
            assistant=assistant,
            date__gte=today - timedelta(days=7)
        ).order_by('-date')
        
        if recent_kpis.exists():
            latest_kpi = recent_kpis.first()
            config['metrics'] = {
                'cost_per_minute': float(latest_kpi.cost_per_minute),
                'avg_latency': latest_kpi.average_latency_ms / 1000,  # Convert to seconds
                'call_success': (latest_kpi.successful_calls / max(latest_kpi.total_calls, 1)) * 100,
                'asr_wer': float(latest_kpi.asr_word_error_rate),
            }
        else:
            # Default metrics when no KPI data exists
            config['metrics'] = {
                'cost_per_minute': 0.15,
                'avg_latency': 1.05,
                'call_success': 94.2,
                'asr_wer': 2.8,
            }
        
        return config


class CreateAssistantView(LoginRequiredMixin, View):
    """Create a new assistant with default configuration."""
    
    def get_client_id(self):
        """Get client_id from tenant info or use default."""
        return getattr(self.request, 'tenant_flags', {}).get('client_id', 'zain_bh')
    
    def post(self, request, *args, **kwargs):
        try:
            client_id = self.get_client_id()
            assistant_name = request.POST.get('name', 'Maha')
            
            # Create assistant with custom defaults
            assistant = Assistant.objects.create(
                client_id=client_id,
                external_id=f"maha-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                name=assistant_name,
                description="AI assistant created for Zain Telecom",
                owner=request.user
            )
            
            # Configure model with custom defaults
            mc = assistant.model_config
            mc.provider = ModelProvider.AZURE_OPENAI
            mc.model_name = "gpt-4o-realtime"
            mc.first_message = f"Hello! This is {assistant_name}, your AI assistant. How can I help you today?"
            mc.system_prompt = f"""You are {assistant_name}, a friendly and professional AI assistant for Zain Telecom. 
You help customers with their telecom needs, answer questions, and provide excellent customer service. 
Keep your responses concise, helpful, and maintain a professional tone."""
            mc.save()

            # Configure voice with OpenAI "Ash" as default
            vc = assistant.voice_config
            
            # Get the default OpenAI "Ash" voice
            try:
                default_voice = Voice.objects.get(
                    provider=VoiceProvider.OPENAI,
                    voice_id="ash"
                )
                vc.voice = default_voice
            except Voice.DoesNotExist:
                # Fallback: get any OpenAI voice if Ash doesn't exist
                default_voice = Voice.objects.filter(
                    provider=VoiceProvider.OPENAI,
                    is_active=True
                ).first()
                vc.voice = default_voice
            
            vc.background_sound_url = "https://www.soundjay.com/ambient/sounds/office-ambiance.mp3"
            vc.save()

            # Configure transcriber
            stt = assistant.stt_config
            stt.provider = TranscriberProvider.DEEPGRAM
            stt.language = "en"
            stt.keyterms = ["Zain", "telecom", "subscription", "support", "billing"]
            stt.save()

            # Configure predefined functions
            pf = assistant.predefined_functions
            pf.enable_end_call = True
            pf.enable_dial_keypad = True
            pf.forwarding_country = "bh"  # Bahrain
            pf.forwarding_number = "+97317123456"
            pf.save()

            # Configure analytics
            an = assistant.analytics
            an.structured_prompt = "Extract customer intent, issue type, and any specific requests from the conversation."
            an.structured_schema = [
                {"name": "customer_intent", "type": "string", "required": True},
                {"name": "issue_type", "type": "string", "required": False},
                {"name": "subscription_type", "type": "string", "required": False},
                {"name": "callback_number", "type": "string", "required": False},
            ]
            an.save()

            return JsonResponse({
                'success': True,
                'assistant_id': str(assistant.id),
                'message': f'Assistant "{assistant_name}" created successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Invalid request method'}, status=405)


class AssistantDetailView(LoginRequiredMixin, View):
    """Get assistant details via AJAX."""
    
    def get_client_id(self):
        """Get client_id from tenant info or use default."""
        return getattr(self.request, 'tenant_flags', {}).get('client_id', 'zain_bh')
    
    def get(self, request, assistant_id, *args, **kwargs):
        try:
            client_id = self.get_client_id()
            
            assistant = get_object_or_404(
                Assistant.objects.select_related(
                    'model_config', 'voice_config', 'stt_config', 'analytics',
                    'privacy', 'advanced_config', 'predefined_functions'
                ),
                id=assistant_id,
                client_id=client_id,
                owner=request.user
            )
            
            # Safely get configuration objects
            model_config = getattr(assistant, 'model_config', None)
            voice_config = getattr(assistant, 'voice_config', None)
            stt_config = getattr(assistant, 'stt_config', None)
            
            # Return assistant configuration as JSON
            config = {
                'name': assistant.name,
                'status': assistant.status,
                'external_id': assistant.external_id,
                'model': {
                    'provider': model_config.provider if model_config else 'azure_openai',
                    'model_name': model_config.model_name if model_config else 'gpt-4o-realtime',
                    'first_message': model_config.first_message if model_config else '',
                    'system_prompt': model_config.system_prompt if model_config else '',
                },
                'voice': {
                    'provider': voice_config.voice.provider if (voice_config and voice_config.voice) else None,
                    'voice': voice_config.voice.name if (voice_config and voice_config.voice) else None,
                    'voice_id': voice_config.voice.voice_id if (voice_config and voice_config.voice) else None,
                    'background_sound': voice_config.background_sound if voice_config else 'default',
                    'background_sound_url': voice_config.background_sound_url if voice_config else '',
                },
                'stt': {
                    'provider': stt_config.provider if stt_config else 'deepgram',
                    'language': stt_config.language if stt_config else 'en',
                    'model_name': stt_config.model_name if stt_config else 'nova-3',
                    'confidence_threshold': float(stt_config.confidence_threshold) if stt_config else 0.40,
                    'keyterms': stt_config.keyterms if stt_config else [],
                }
            }
            
            return JsonResponse(config)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class SaveAssistantConfigView(LoginRequiredMixin, View):
    """Save assistant configuration via AJAX."""
    
    def get_client_id(self):
        """Get client_id from tenant info or use default."""
        return getattr(self.request, 'tenant_flags', {}).get('client_id', 'zain_bh')
    
    def post(self, request, assistant_id, *args, **kwargs):
        try:
            client_id = self.get_client_id()
            
            assistant = get_object_or_404(
                Assistant.objects.select_related(
                    'model_config', 'voice_config', 'stt_config', 'analytics',
                    'privacy', 'advanced_config', 'predefined_functions'
                ),
                id=assistant_id,
                client_id=client_id,
                owner=request.user
            )
            
            # Parse the configuration data from request
            config_data = json.loads(request.body)
            
            # Update model configuration
            if 'model' in config_data:
                model_data = config_data['model']
                mc = assistant.model_config
                
                if 'provider' in model_data:
                    mc.provider = model_data['provider'].lower()
                if 'model_name' in model_data:
                    mc.model_name = model_data['model_name']
                if 'first_message_mode' in model_data:
                    mc.first_message_mode = model_data['first_message_mode']
                if 'first_message' in model_data:
                    mc.first_message = model_data['first_message']
                if 'system_prompt' in model_data:
                    mc.system_prompt = model_data['system_prompt']

                
                mc.save()
            
            # Update voice configuration
            if 'voice' in config_data:
                voice_data = config_data['voice']
                vc = assistant.voice_config
                
                if 'voice_id' in voice_data:
                    try:
                        # Find the Voice object by voice_id
                        voice_obj = Voice.objects.get(voice_id=voice_data['voice_id'])
                        vc.voice = voice_obj
                    except Voice.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': f'Voice with ID {voice_data["voice_id"]} not found'
                        }, status=400)
                
                # Handle ambient sound configuration
                if 'ambient_sound_enabled' in voice_data:
                    vc.ambient_sound_enabled = voice_data['ambient_sound_enabled']
                if 'ambient_sound_type' in voice_data:
                    vc.ambient_sound_type = voice_data['ambient_sound_type']
                if 'ambient_sound_volume' in voice_data:
                    vc.ambient_sound_volume = float(voice_data['ambient_sound_volume'])
                if 'ambient_sound_url' in voice_data:
                    vc.ambient_sound_url = voice_data['ambient_sound_url']
                
                # Handle thinking sound configuration
                if 'thinking_sound_enabled' in voice_data:
                    vc.thinking_sound_enabled = voice_data['thinking_sound_enabled']
                if 'thinking_sound_primary' in voice_data:
                    vc.thinking_sound_primary = voice_data['thinking_sound_primary']
                if 'thinking_sound_primary_volume' in voice_data:
                    vc.thinking_sound_primary_volume = float(voice_data['thinking_sound_primary_volume'])
                if 'thinking_sound_secondary' in voice_data:
                    vc.thinking_sound_secondary = voice_data['thinking_sound_secondary']
                if 'thinking_sound_secondary_volume' in voice_data:
                    vc.thinking_sound_secondary_volume = float(voice_data['thinking_sound_secondary_volume'])
                
                # Legacy background sound support
                if 'background_sound' in voice_data:
                    vc.background_sound = voice_data['background_sound']
                if 'background_sound_url' in voice_data:
                    vc.background_sound_url = voice_data['background_sound_url']
                
                vc.save()
            
            # Update STT configuration
            if 'stt' in config_data:
                stt_data = config_data['stt']
                stt = assistant.stt_config
                
                if 'provider' in stt_data:
                    stt.provider = stt_data['provider'].lower()
                if 'language' in stt_data:
                    stt.language = stt_data['language']
                if 'model_name' in stt_data:
                    stt.model_name = stt_data['model_name']
                if 'confidence_threshold' in stt_data:
                    stt.confidence_threshold = float(stt_data['confidence_threshold'])
                if 'keyterms' in stt_data:
                    stt.keyterms = stt_data['keyterms']
                
                stt.save()
            
            # Update privacy configuration
            if 'privacy' in config_data:
                privacy_data = config_data['privacy']
                pc = assistant.privacy
                
                if 'audio_recording' in privacy_data:
                    pc.audio_recording = bool(privacy_data['audio_recording'])
                
                pc.save()
            
            # Update advanced configuration
            if 'advanced' in config_data:
                advanced_data = config_data['advanced']
                ac = assistant.advanced_config
                
                if 'turn_detection_threshold' in advanced_data:
                    ac.turn_detection_threshold = float(advanced_data['turn_detection_threshold'])
                if 'turn_detection_silence_duration_ms' in advanced_data:
                    ac.turn_detection_silence_duration_ms = int(advanced_data['turn_detection_silence_duration_ms'])
                if 'turn_detection_prefix_padding_ms' in advanced_data:
                    ac.turn_detection_prefix_padding_ms = int(advanced_data['turn_detection_prefix_padding_ms'])
                if 'turn_detection_create_response' in advanced_data:
                    ac.turn_detection_create_response = bool(advanced_data['turn_detection_create_response'])
                if 'turn_detection_interrupt_response' in advanced_data:
                    ac.turn_detection_interrupt_response = bool(advanced_data['turn_detection_interrupt_response'])

                
                ac.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Configuration saved successfully for {assistant.name}!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


def phone_numbers(request):
    """Phone Numbers page for managing phone numbers."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'Phone Numbers', 'active': True}
    ]
    
    # Mock phone numbers data - empty state initially
    context['phone_numbers'] = []
    context['has_phone_numbers'] = len(context['phone_numbers']) > 0
    
    return render(request, "dashboard/PhoneNumbers.html", context)


def voice_library(request):
    """Voice Library view with search and filtering."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'Voice Library', 'active': True}
    ]
    
    # Mock voice data for demonstration
    recommended_voices = [
        {
            'id': 'aurora-playht',
            'name': 'Aurora',
            'provider': 'PlayHT',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'use_cases': 'Professional, Healthcare',
            'price_min': 0.03,
            'price_max': 0.09,
            'latency_min': 350,
            'latency_max': 600,
            'cover_image': 'https://images.unsplash.com/photo-1494790108755-2616b6ebe55a?w=300&h=300&fit=crop&crop=face',
            'tags': ['Professional', 'Warm', 'Clear']
        },
        {
            'id': 'vits-ara-1',
            'name': 'Vits-ara-1',
            'provider': 'NEETS',
            'gender': 'Male',
            'accent': 'Arabic',
            'language': 'Arabic',
            'use_cases': 'Arabic, Support',
            'price_min': 0.02,
            'price_max': 0.08,
            'latency_min': 300,
            'latency_max': 500,
            'cover_image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face',
            'tags': ['Arabic', 'Native', 'Support']
        },
        {
            'id': 'mady-11labs',
            'name': 'Mady',
            'provider': '11LABS',
            'gender': 'Female',
            'accent': 'Spanish',
            'language': 'Spanish',
            'use_cases': 'Spanish, Commercial',
            'price_min': 0.04,
            'price_max': 0.12,
            'latency_min': 250,
            'latency_max': 450,
            'cover_image': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&h=300&fit=crop&crop=face',
            'tags': ['Commercial', 'Energetic', 'Spanish']
        },
        {
            'id': 'jordan-11labs',
            'name': 'Jordan',
            'provider': '11LABS',
            'gender': 'Male',
            'accent': 'British',
            'language': 'English',
            'use_cases': 'Customer Service, Professional',
            'price_min': 0.04,
            'price_max': 0.12,
            'latency_min': 280,
            'latency_max': 480,
            'cover_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face',
            'tags': ['British', 'Professional', 'Calm']
        }
    ]
    
    # Extended voice library
    all_voices = [
        {
            'id': 'will-playht',
            'name': 'Will',
            'provider': 'PlayHT',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Conversational', 'Friendly'],
            'avatar': 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'charlie-playht',
            'name': 'Charlie',
            'provider': 'PlayHT',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Professional', 'Clear'],
            'avatar': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'beth-gentle',
            'name': 'Beth - Gentle And Nurturing',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Gentle', 'Nurturing', 'Healthcare'],
            'avatar': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'bex-uk-female',
            'name': 'Bex UK Female',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'British',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['UK', 'Professional'],
            'avatar': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'knightley-javier',
            'name': 'Knightley Javier - Calm, Gentle',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'British',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Calm', 'Gentle', 'British'],
            'avatar': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'giovanni-rossi',
            'name': 'Giovanni Rossi - Giovane',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'Italian',
            'language': 'Italian',
            'price': 0.036,
            'latency': 400,
            'tags': ['Italian', 'Youthful'],
            'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'alex-ozwyn',
            'name': 'Alex Ozwyn',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Professional', 'Clear'],
            'avatar': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'kina-cute-girl',
            'name': 'Kina (Cute Happy Girl) - Perfect For Social Media & Ads',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Happy', 'Social Media', 'Ads'],
            'avatar': 'https://images.unsplash.com/photo-1494790108755-2616b6ebe55a?w=80&h=80&fit=crop&crop=face'
        }
    ]
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    provider_filter = request.GET.getlist('provider')
    gender_filter = request.GET.get('gender', '')
    accent_filter = request.GET.get('accent', '')
    language_filter = request.GET.get('language', '')
    sort_by = request.GET.get('sort', 'popular')
    
    # Apply filters
    filtered_voices = all_voices.copy()
    
    if search_query:
        filtered_voices = [v for v in filtered_voices if 
                          search_query.lower() in v['name'].lower() or 
                          search_query.lower() in v['provider'].lower() or
                          any(search_query.lower() in tag.lower() for tag in v['tags'])]
    
    if provider_filter:
        filtered_voices = [v for v in filtered_voices if v['provider'] in provider_filter]
    
    if gender_filter:
        filtered_voices = [v for v in filtered_voices if v['gender'] == gender_filter]
    
    if accent_filter:
        filtered_voices = [v for v in filtered_voices if v['accent'] == accent_filter]
    
    if language_filter:
        filtered_voices = [v for v in filtered_voices if v['language'] == language_filter]
    
    # Get unique filter options
    providers = list(set(v['provider'] for v in all_voices))
    genders = list(set(v['gender'] for v in all_voices))
    accents = list(set(v['accent'] for v in all_voices))
    languages = list(set(v['language'] for v in all_voices))
    
    context.update({
        'recommended_voices': recommended_voices,
        'all_voices': filtered_voices,
        'search_query': search_query,
        'filters': {
            'providers': providers,
            'genders': genders,
            'accents': accents,
            'languages': languages,
            'selected_provider': provider_filter,
            'selected_gender': gender_filter,
            'selected_accent': accent_filter,
            'selected_language': language_filter,
            'sort_by': sort_by,
        }
    })
    
    return render(request, "dashboard/VoiceLibrary.html", context)


@login_required
def api_keys(request):
    """API Keys management page."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'API Keys', 'active': True}
    ]
    
    # TODO: Replace with actual API key model retrieval
    # For now, using mock data - replace with your actual model
    context['api_keys'] = {
        'azure_openai_realtime_endpoint': '',
        'azure_openai_realtime_key': '',
        'azure_gpt5_mini_endpoint': '',
        'azure_gpt5_mini_key': '',
        'elevenlabs_key': ''
    }
    
    return render(request, "dashboard/api_keys.html", context)


@login_required
def save_api_keys(request):
    """Save API keys configuration."""
    if request.method == 'POST':
        try:
            # Extract form data
            api_keys_data = {
                'azure_openai_realtime_endpoint': request.POST.get('azure_openai_realtime_endpoint', ''),
                'azure_openai_realtime_key': request.POST.get('azure_openai_realtime_key', ''),
                'azure_gpt5_mini_endpoint': request.POST.get('azure_gpt5_mini_endpoint', ''),
                'azure_gpt5_mini_key': request.POST.get('azure_gpt5_mini_key', ''),
                'elevenlabs_key': request.POST.get('elevenlabs_key', '')
            }
            
            # TODO: Save to your API keys model
            # For now, just simulate successful save
            # Example:
            # api_keys_obj, created = APIKeys.objects.get_or_create(user=request.user)
            # api_keys_obj.azure_openai_realtime_endpoint = api_keys_data['azure_openai_realtime_endpoint']
            # ... set other fields ...
            # api_keys_obj.save()
            
            messages.success(request, 'API keys saved successfully!')
            return redirect('dashboard:api_keys')
            
        except Exception as e:
            messages.error(request, f'Error saving API keys: {str(e)}')
            return redirect('dashboard:api_keys')
    
    return redirect('dashboard:api_keys')

# ============================================================================
# KNOWLEDGE BASE VIEWS
# ============================================================================

@login_required
def upload_file(request, assistant_id):
    """Handle file uploads for RAG."""
    if request.method == 'POST':
        try:
            # Validate UUID format
            try:
                uuid.UUID(str(assistant_id))
            except ValueError:
                return JsonResponse({'error': 'Invalid assistant ID format'}, status=400)
                
            assistant = get_object_or_404(Assistant, id=assistant_id)
            
            # Check if user has permission to modify this assistant
            if not request.user.is_superuser and assistant.owner != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file provided'}, status=400)
            
            # Create FileAsset
            file_asset = FileAsset.objects.create(
                client_id=assistant.client_id,
                name=uploaded_file.name,
                file=uploaded_file,
                file_type=uploaded_file.name.split('.')[-1].lower(),
                size_bytes=uploaded_file.size,
                processing_status='pending'
            )
            
            # Create AssistantFile relationship
            assistant_file = AssistantFile.objects.create(
                client_id=assistant.client_id,
                assistant=assistant,
                file_asset=file_asset,
                use_for_rag=True
            )
            
            return JsonResponse({
                'success': True,
                'file_id': str(file_asset.id),
                'name': file_asset.name,
                'size': file_asset.size_bytes,
                'status': file_asset.processing_status
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def delete_file(request, assistant_id, file_id):
    """Delete a file from the assistant's knowledge base."""
    if request.method == 'POST':
        try:
            # Validate UUID formats
            try:
                uuid.UUID(str(assistant_id))
                uuid.UUID(str(file_id))
            except ValueError:
                return JsonResponse({'error': 'Invalid ID format'}, status=400)
                
            assistant = get_object_or_404(Assistant, id=assistant_id)
            
            # Check if user has permission to modify this assistant
            if not request.user.is_superuser and assistant.owner != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Find and delete the file
            assistant_file = get_object_or_404(AssistantFile, 
                                             assistant=assistant, 
                                             file_asset_id=file_id)
            file_asset = assistant_file.file_asset
            
            # Delete the file relationship first
            assistant_file.delete()
            
            # Delete the actual file asset
            file_asset.delete()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def add_website(request, assistant_id):
    """Add a website for scraping."""
    if request.method == 'POST':
        try:
            # Validate UUID format
            try:
                uuid.UUID(str(assistant_id))
            except ValueError:
                return JsonResponse({'error': 'Invalid assistant ID format'}, status=400)
                
            assistant = get_object_or_404(Assistant, id=assistant_id)
            
            # Check if user has permission to modify this assistant
            if not request.user.is_superuser and assistant.owner != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            url = request.POST.get('url')
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # Extract name from URL if not provided
            if not name:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                name = parsed.netloc
            
            # Create website scraping entry
            website = WebsiteScraping.objects.create(
                client_id=assistant.client_id,
                assistant=assistant,
                url=url,
                name=name,
                description=description,
                scraping_status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'website_id': website.id,
                'name': website.name,
                'url': website.url,
                'status': website.scraping_status
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def delete_website(request, assistant_id, website_id):
    """Delete a website from the assistant's knowledge base."""
    if request.method == 'POST':
        try:
            # Validate UUID format for assistant_id
            try:
                uuid.UUID(str(assistant_id))
            except ValueError:
                return JsonResponse({'error': 'Invalid assistant ID format'}, status=400)
                
            assistant = get_object_or_404(Assistant, id=assistant_id)
            
            # Check if user has permission to modify this assistant
            if not request.user.is_superuser and assistant.owner != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            website = get_object_or_404(WebsiteScraping, 
                                      id=website_id, 
                                      assistant=assistant)
            website.delete()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_knowledge_base(request, assistant_id):
    """Get the current knowledge base status for an assistant."""
    try:
        # Validate UUID format
        try:
            uuid.UUID(str(assistant_id))
        except ValueError:
            return JsonResponse({'error': 'Invalid assistant ID format'}, status=400)
            
        assistant = get_object_or_404(Assistant, id=assistant_id)
        
        # Check if user has permission to view this assistant
        if not request.user.is_superuser and assistant.owner != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get files
        files = []
        for assistant_file in assistant.files.all():
            files.append({
                'id': str(assistant_file.file_asset.id),
                'name': assistant_file.file_asset.name,
                'size': assistant_file.file_asset.size_bytes,
                'status': assistant_file.file_asset.processing_status,
                'uploaded_at': assistant_file.file_asset.created_at.isoformat()
            })
        
        # Get websites
        websites = []
        for website in assistant.scraped_websites.all():
            websites.append({
                'id': website.id,
                'name': website.name,
                'url': website.url,
                'status': website.scraping_status,
                'last_scraped': website.last_scraped.isoformat() if website.last_scraped else None
            })
        
        return JsonResponse({
            'files': files,
            'websites': websites,
            'file_count': len(files),
            'website_count': len(websites)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)