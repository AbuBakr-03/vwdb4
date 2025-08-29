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
    Assistant, ModelConfig, VoiceConfig, TranscriberConfig,
    AnalyticsConfig, PrivacyConfig, AdvancedConfig, MessagingConfig,
    PredefinedFunctions, AssistantKPI, seed_example_assistant,
    ModelProvider, VoiceProvider, TranscriberProvider
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
            'privacy', 'advanced_config', 'messaging', 'predefined_functions'
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
                'description': assistant.description or assistant.voice_config.voice,
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
        config = {
            'assistant_config': {
                'name': assistant.name,
                'status': assistant.status,
                'external_id': assistant.external_id[:20] + '...',
                'model': {
                    'provider': assistant.model_config.provider,
                    'model_name': assistant.model_config.model_name,
                    'first_message_mode': assistant.model_config.first_message_mode,
                    'first_message': assistant.model_config.first_message,
                    'system_prompt': assistant.model_config.system_prompt,
                    'max_tokens': assistant.model_config.max_tokens,
                    'temperature': float(assistant.model_config.temperature),
                },
                'voice': {
                    'provider': assistant.voice_config.provider,
                    'voice': assistant.voice_config.voice,
                    'background_sound': assistant.voice_config.background_sound,
                    'background_sound_url': assistant.voice_config.background_sound_url,
                    'input_min_characters': assistant.voice_config.input_min_characters,
                    'punctuation_boundaries': assistant.voice_config.punctuation_boundaries,
                },
                'stt': {
                    'provider': assistant.stt_config.provider,
                    'language': assistant.stt_config.language,
                    'model_name': assistant.stt_config.model_name,
                    'background_denoising': assistant.stt_config.background_denoising,
                    'confidence_threshold': float(assistant.stt_config.confidence_threshold),
                    'use_numerals': assistant.stt_config.use_numerals,
                    'keyterms': assistant.stt_config.keyterms,
                },
                'predefined_functions': {
                    'enable_end_call': assistant.predefined_functions.enable_end_call,
                    'enable_dial_keypad': assistant.predefined_functions.enable_dial_keypad,
                    'forwarding_country': assistant.predefined_functions.forwarding_country,
                    'forwarding_number': assistant.predefined_functions.forwarding_number,
                },
                'analytics': {
                    'summary_timeout_sec': assistant.analytics.summary_timeout_sec,
                    'min_messages_for_summary': assistant.analytics.min_messages_for_summary,
                    'success_rubric': assistant.analytics.success_rubric,
                    'success_timeout_sec': assistant.analytics.success_timeout_sec,
                    'structured_prompt': assistant.analytics.structured_prompt,
                    'structured_schema': assistant.analytics.structured_schema,
                },
                'privacy': {
                    'hipaa_enabled': assistant.privacy.hipaa_enabled,
                    'pci_enabled': assistant.privacy.pci_enabled,
                    'audio_recording': assistant.privacy.audio_recording,
                    'video_recording': assistant.privacy.video_recording,
                    'audio_format': assistant.privacy.audio_format,
                },
                'advanced': {
                    'start_speaking_wait_seconds': float(assistant.advanced_config.start_speaking_wait_seconds),
                    'smart_endpointing': assistant.advanced_config.smart_endpointing,
                    'on_punctuation_seconds': float(assistant.advanced_config.on_punctuation_seconds),
                    'on_no_punctuation_seconds': float(assistant.advanced_config.on_no_punctuation_seconds),
                    'on_number_seconds': float(assistant.advanced_config.on_number_seconds),
                    'stop_speaking_words': assistant.advanced_config.stop_speaking_words,
                    'stop_speaking_voice_seconds': float(assistant.advanced_config.stop_speaking_voice_seconds),
                    'stop_speaking_backoff_seconds': assistant.advanced_config.stop_speaking_backoff_seconds,
                    'silence_timeout_seconds': assistant.advanced_config.silence_timeout_seconds,
                    'max_duration_seconds': assistant.advanced_config.max_duration_seconds,
                    'voicemail_detection_provider': assistant.advanced_config.voicemail_detection_provider,
                    'keypad_input_enabled': assistant.advanced_config.keypad_input_enabled,
                    'keypad_timeout_seconds': assistant.advanced_config.keypad_timeout_seconds,
                    'keypad_delimiter': assistant.advanced_config.keypad_delimiter,
                    'max_idle_messages': assistant.advanced_config.max_idle_messages,
                    'idle_timeout_seconds': float(assistant.advanced_config.idle_timeout_seconds),
                },
                'messaging': {
                    'server_url': assistant.messaging.server_url,
                    'timeout_seconds': assistant.messaging.timeout_seconds,
                    'voicemail_message': assistant.messaging.voicemail_message,
                    'end_call_message': assistant.messaging.end_call_message,
                    'idle_messages': assistant.messaging.idle_messages,
                }
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
            mc.provider = ModelProvider.OPENAI
            mc.model_name = "gpt-4o-realtime"
            mc.first_message = f"Hello! This is {assistant_name}, your AI assistant. How can I help you today?"
            mc.system_prompt = f"""You are {assistant_name}, a friendly and professional AI assistant for Zain Telecom. 
You help customers with their telecom needs, answer questions, and provide excellent customer service. 
Keep your responses concise, helpful, and maintain a professional tone."""
            mc.save()

            # Configure voice with ElevenLabs
            vc = assistant.voice_config
            vc.provider = VoiceProvider.ELEVENLABS
            vc.voice = "Maha"  # Custom voice name
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
                    'privacy', 'advanced_config', 'messaging', 'predefined_functions'
                ),
                id=assistant_id,
                client_id=client_id,
                owner=request.user
            )
            
            # Return assistant configuration as JSON
            config = {
                'name': assistant.name,
                'status': assistant.status,
                'external_id': assistant.external_id,
                'model': {
                    'provider': assistant.model_config.provider,
                    'model_name': assistant.model_config.model_name,
                    'first_message': assistant.model_config.first_message,
                    'system_prompt': assistant.model_config.system_prompt,
                    'max_tokens': assistant.model_config.max_tokens,
                    'temperature': float(assistant.model_config.temperature),
                },
                'voice': {
                    'provider': assistant.voice_config.provider,
                    'voice': assistant.voice_config.voice,
                    'background_sound': assistant.voice_config.background_sound,
                    'background_sound_url': assistant.voice_config.background_sound_url,
                },
                'stt': {
                    'provider': assistant.stt_config.provider,
                    'language': assistant.stt_config.language,
                    'model_name': assistant.stt_config.model_name,
                    'confidence_threshold': float(assistant.stt_config.confidence_threshold),
                    'keyterms': assistant.stt_config.keyterms,
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
                    'privacy', 'advanced_config', 'messaging', 'predefined_functions'
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
                if 'max_tokens' in model_data:
                    mc.max_tokens = int(model_data['max_tokens'])
                if 'temperature' in model_data:
                    mc.temperature = float(model_data['temperature'])
                
                mc.save()
            
            # Update voice configuration
            if 'voice' in config_data:
                voice_data = config_data['voice']
                vc = assistant.voice_config
                
                if 'provider' in voice_data:
                    vc.provider = voice_data['provider'].lower()
                if 'voice' in voice_data:
                    vc.voice = voice_data['voice']
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