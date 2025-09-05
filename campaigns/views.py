"""
Campaign views with tenant management integration and enhanced dashboard features.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.contrib import messages
import json
import redis
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import tenant management decorators and utilities
from authorization.consumer_middleware import require_feature, require_plan
from authorization.utils import (
    get_tenant_info, 
    check_tenant_limit, 
    increment_tenant_usage,
    tenant_audit_log,
    require_tenant_context
)

from .models import Campaign, CampaignSession, CampaignQueue

# Import Assistant model for campaign relationships
from dashboard.models import Assistant

# Import queue service
from .queue_service import CampaignQueueService

# Redis connection for queue monitoring
import redis
from django.conf import settings

class CampaignBaseView(View):
    """Base view class with tenant context validation."""
    
    def dispatch(self, request, *args, **kwargs):
        # Check if tenant context exists (middleware should have attached tenant_flags)
        if not hasattr(request, 'tenant_flags'):
            return JsonResponse({'error': 'Tenant context required'}, status=401)
        
        # Check if tenant is active
        if not request.tenant_flags.get('system_enabled', False):
            return JsonResponse({'error': 'Tenant access disabled'}, status=403)
        
        # Check if tenant has campaigns feature
        if 'campaigns' not in request.tenant_flags.get('features', []):
            return JsonResponse({'error': 'Campaigns feature not available'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CampaignDashboardView(CampaignBaseView):
    """Enhanced dashboard view with real-time metrics and queue monitoring."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get comprehensive campaign statistics
        campaigns = Campaign.objects.filter(tenant_id=tenant_id)
        
        # Real-time statistics
        stats = {
            'total': campaigns.count(),
            'active': campaigns.filter(status='active').count(),
            'draft': campaigns.filter(status='draft').count(),
            'paused': campaigns.filter(status='paused').count(),
            'completed': campaigns.filter(status='completed').count(),
            'cancelled': campaigns.filter(status='cancelled').count(),
            'total_calls': campaigns.aggregate(Sum('total_calls'))['total_calls__sum'] or 0,
            'successful_calls': campaigns.aggregate(Sum('successful_calls'))['successful_calls__sum'] or 0,
            'failed_calls': campaigns.aggregate(Sum('failed_calls'))['failed_calls__sum'] or 0,
        }
        
        # Calculate success rate
        if stats['total_calls'] > 0:
            stats['success_rate'] = round((stats['successful_calls'] / stats['total_calls']) * 100, 2)
        else:
            stats['success_rate'] = 0
        
        # Get recent campaigns
        recent_campaigns = campaigns.order_by('-created_at')[:5]
        
        # Get active campaigns with real-time status
        active_campaigns = campaigns.filter(status='active').order_by('-created_at')[:10]
        
        # Get campaign performance data for charts
        performance_data = self._get_performance_data(tenant_id)
        
        # Get queue status
        queue_status = self._get_queue_status(tenant_id)
        
        # Get recent sessions
        recent_sessions = CampaignSession.objects.filter(
            tenant_id=tenant_id
        ).select_related('campaign').order_by('-created_at')[:10]
        
        context = {
            'stats': stats,
            'recent_campaigns': recent_campaigns,
            'active_campaigns': active_campaigns,
            'recent_sessions': recent_sessions,
            'performance_data': performance_data,
            'queue_status': queue_status,
        }
        
        return render(request, 'campaigns/dashboard.html', context)
    
    def _get_performance_data(self, tenant_id):
        """Get performance data for charts."""
        # Last 30 days performance
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        daily_stats = []
        for i in range(30):
            date = start_date + timedelta(days=i)
            day_campaigns = Campaign.objects.filter(
                tenant_id=tenant_id,
                created_at__date=date.date()
            )
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'campaigns': day_campaigns.count(),
                'calls': day_campaigns.aggregate(Sum('total_calls'))['total_calls__sum'] or 0,
                'success_rate': self._calculate_daily_success_rate(day_campaigns)
            })
        
        return daily_stats
    
    def _calculate_daily_success_rate(self, campaigns):
        """Calculate success rate for a given set of campaigns."""
        total_calls = campaigns.aggregate(Sum('total_calls'))['total_calls__sum'] or 0
        successful_calls = campaigns.aggregate(Sum('successful_calls'))['successful_calls__sum'] or 0
        
        if total_calls > 0:
            return round((successful_calls / total_calls) * 100, 2)
        return 0
    
    def _get_queue_status(self, tenant_id):
        """Get Redis queue status for real-time monitoring."""
        try:
            # Connect to Redis
            redis_client = redis.Redis.from_url(settings.REDIS_URL)
            stream_name = f"campaign_queue:{tenant_id}"
            
            # Get stream info
            stream_info = redis_client.xinfo_stream(stream_name)
            stream_length = stream_info.get('length', 0)
            
            # Get consumer groups
            groups = redis_client.xinfo_groups(stream_name)
            
            # Get recent messages
            recent_messages = redis_client.xrevrange(stream_name, count=5)
            
            return {
                'stream_length': stream_length,
                'consumer_groups': len(groups),
                'recent_messages': len(recent_messages),
                'status': 'active' if stream_length > 0 else 'idle'
            }
        except Exception as e:
            return {
                'stream_length': 0,
                'consumer_groups': 0,
                'recent_messages': 0,
                'status': 'error',
                'error': str(e)
            }


@method_decorator(login_required, name='dispatch')
class CampaignListView(CampaignBaseView):
    """Enhanced list view with advanced filtering and real-time updates."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get campaigns for this tenant
        campaigns = Campaign.objects.filter(tenant_id=tenant_id).select_related('assistant')
        
        # Enhanced search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            campaigns = campaigns.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(assistant__name__icontains=search_query) |
                Q(tenant_id__icontains=search_query)
            )
        
        # Advanced filtering
        status_filter = request.GET.get('status', '')
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)
        
        assistant_filter = request.GET.get('assistant', '')
        if assistant_filter:
            campaigns = campaigns.filter(assistant_id=assistant_filter)
        
        priority_filter = request.GET.get('priority', '')
        if priority_filter:
            campaigns = campaigns.filter(priority=priority_filter)
        
        date_filter = request.GET.get('date', '')
        if date_filter:
            if date_filter == 'today':
                campaigns = campaigns.filter(created_at__date=timezone.now().date())
            elif date_filter == 'week':
                campaigns = campaigns.filter(created_at__gte=timezone.now() - timedelta(days=7))
            elif date_filter == 'month':
                campaigns = campaigns.filter(created_at__gte=timezone.now() - timedelta(days=30))
        
        # Sorting
        sort_by = request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'status', '-status', 'priority', '-priority', 'created_at', '-created_at']:
            campaigns = campaigns.order_by(sort_by)
        else:
            campaigns = campaigns.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(campaigns, 25)  # Increased page size
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Enhanced statistics
        stats = {
            'total': campaigns.count(),
            'active': campaigns.filter(status='active').count(),
            'draft': campaigns.filter(status='draft').count(),
            'paused': campaigns.filter(status='paused').count(),
            'completed': campaigns.filter(status='completed').count(),
            'cancelled': campaigns.filter(status='cancelled').count(),
            'total_calls': campaigns.aggregate(Sum('total_calls'))['total_calls__sum'] or 0,
            'successful_calls': campaigns.aggregate(Sum('successful_calls'))['successful_calls__sum'] or 0,
            'failed_calls': campaigns.aggregate(Sum('failed_calls'))['failed_calls__sum'] or 0,
        }
        
        # Get assistants for filtering
        assistants = Assistant.objects.filter(
            client_id=tenant_id,
            status='published'
        ).order_by('name')
        
        # Get queue status for real-time updates
        queue_status = self._get_queue_status(tenant_id)
        
        context = {
            'campaigns': page_obj,
            'stats': stats,
            'assistants': assistants,
            'search_query': search_query,
            'status_filter': status_filter,
            'assistant_filter': assistant_filter,
            'priority_filter': priority_filter,
            'date_filter': date_filter,
            'sort_by': sort_by,
            'queue_status': queue_status,
        }
        
        return render(request, 'campaigns/campaign_list.html', context)
    
    def _get_queue_status(self, tenant_id):
        """Get Redis queue status."""
        try:
            redis_client = redis.Redis.from_url(settings.REDIS_URL)
            stream_name = f"campaign_queue:{tenant_id}"
            stream_info = redis_client.xinfo_stream(stream_name)
            return {
                'stream_length': stream_info.get('length', 0),
                'status': 'active' if stream_info.get('length', 0) > 0 else 'idle'
            }
        except:
            return {'stream_length': 0, 'status': 'error'}


@method_decorator(login_required, name='dispatch')
class CampaignDetailView(CampaignBaseView):
    """Enhanced detail view with real-time session monitoring."""
    
    def get(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        # Get campaign sessions
        sessions = CampaignSession.objects.filter(campaign=campaign).order_by('-created_at')
        
        # Get session statistics
        session_stats = {
            'total': sessions.count(),
            'queued': sessions.filter(status='queued').count(),
            'in_progress': sessions.filter(status='in_progress').count(),
            'completed': sessions.filter(status='completed').count(),
            'failed': sessions.filter(status='failed').count(),
        }
        
        # Get recent sessions
        recent_sessions = sessions[:10]
        
        # Get queue position if campaign is queued
        queue_position = None
        if campaign.status == 'active':
            try:
                queue_item = CampaignQueue.objects.filter(
                    campaign=campaign,
                    is_processing=False
                ).order_by('priority', 'position').first()
                if queue_item:
                    queue_position = queue_item.position
            except:
                pass
        
        # Get performance metrics
        performance_metrics = self._get_performance_metrics(campaign)
        
        context = {
            'campaign': campaign,
            'sessions': sessions,
            'session_stats': session_stats,
            'recent_sessions': recent_sessions,
            'queue_position': queue_position,
            'performance_metrics': performance_metrics,
        }
        
        return render(request, 'campaigns/campaign_detail.html', context)
    
    def _get_performance_metrics(self, campaign):
        """Get detailed performance metrics for the campaign."""
        sessions = CampaignSession.objects.filter(campaign=campaign)
        
        # Calculate average call duration
        avg_duration = sessions.aggregate(Avg('call_duration'))['call_duration__avg'] or 0
        
        # Calculate success rate over time
        daily_success = []
        for i in range(7):  # Last 7 days
            date = timezone.now() - timedelta(days=i)
            day_sessions = sessions.filter(created_at__date=date.date())
            if day_sessions.exists():
                success_count = day_sessions.filter(status='completed').count()
                total_count = day_sessions.count()
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                daily_success.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'success_rate': round(success_rate, 2)
                })
        
        return {
            'avg_duration': avg_duration,
            'daily_success': daily_success,
            'total_sessions': sessions.count(),
            'success_rate': campaign.success_rate,
        }


@method_decorator(login_required, name='dispatch')
class CampaignQueueView(CampaignBaseView):
    """Real-time queue monitoring view."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get Redis queue information
        queue_status = self._get_detailed_queue_status(tenant_id)
        
        # Get campaigns in queue
        queued_campaigns = Campaign.objects.filter(
            tenant_id=tenant_id,
            status='active'
        ).order_by('-created_at')
        
        # Get recent sessions
        recent_sessions = CampaignSession.objects.filter(
            tenant_id=tenant_id
        ).select_related('campaign').order_by('-created_at')[:20]
        
        context = {
            'queue_status': queue_status,
            'queued_campaigns': queued_campaigns,
            'recent_sessions': recent_sessions,
        }
        
        return render(request, 'campaigns/queue_monitor.html', context)
    
    def _get_detailed_queue_status(self, tenant_id):
        """Get detailed Redis queue status."""
        try:
            redis_client = redis.Redis.from_url(settings.REDIS_URL)
            stream_name = f"campaign_queue:{tenant_id}"
            
            # Get stream info
            stream_info = redis_client.xinfo_stream(stream_name)
            stream_length = stream_info.get('length', 0)
            
            # Get consumer groups
            groups = redis_client.xinfo_groups(stream_name)
            
            # Get recent messages
            recent_messages = redis_client.xrevrange(stream_name, count=10)
            
            # Parse message data
            parsed_messages = []
            for msg_id, fields in recent_messages:
                message_data = {}
                for i in range(0, len(fields), 2):
                    key = fields[i].decode('utf-8') if isinstance(fields[i], bytes) else fields[i]
                    value = fields[i+1].decode('utf-8') if isinstance(fields[i+1], bytes) else fields[i+1]
                    message_data[key] = value
                
                parsed_messages.append({
                    'id': msg_id.decode('utf-8') if isinstance(msg_id, bytes) else msg_id,
                    'data': message_data
                })
            
            return {
                'stream_length': stream_length,
                'consumer_groups': len(groups),
                'recent_messages': parsed_messages,
                'status': 'active' if stream_length > 0 else 'idle',
                'last_updated': timezone.now()
            }
        except Exception as e:
            return {
                'stream_length': 0,
                'consumer_groups': 0,
                'recent_messages': [],
                'status': 'error',
                'error': str(e),
                'last_updated': timezone.now()
            }


@method_decorator(login_required, name='dispatch')
class CampaignActionView(CampaignBaseView):
    """Handle campaign actions (launch, pause, stop, etc.)."""
    
    def post(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        action = request.POST.get('action')
        
        if action == 'launch':
            return self._launch_campaign(request, campaign)
        elif action == 'pause':
            return self._pause_campaign(request, campaign)
        elif action == 'resume':
            return self._resume_campaign(request, campaign)
        elif action == 'stop':
            return self._stop_campaign(request, campaign)
        elif action == 'retry_failed':
            return self._retry_failed_sessions(request, campaign)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    
    def _launch_campaign(self, request, campaign):
        """Launch a campaign."""
        try:
            if campaign.status != 'draft':
                return JsonResponse({'error': 'Only draft campaigns can be launched'}, status=400)
            
            # Update campaign status
            campaign.status = 'active'
            campaign.save()
            
            # Launch campaign using queue service
            queue_service = CampaignQueueService()
            success = queue_service.launch_campaign(campaign)
            
            if success:
                messages.success(request, f'Campaign "{campaign.name}" launched successfully!')
                return JsonResponse({'success': True, 'message': 'Campaign launched successfully'})
            else:
                campaign.status = 'draft'
                campaign.save()
                return JsonResponse({'error': 'Failed to launch campaign'}, status=500)
                
        except Exception as e:
            campaign.status = 'draft'
            campaign.save()
            return JsonResponse({'error': f'Error launching campaign: {str(e)}'}, status=500)
    
    def _pause_campaign(self, request, campaign):
        """Pause a campaign."""
        if campaign.status != 'active':
            return JsonResponse({'error': 'Only active campaigns can be paused'}, status=400)
        
        campaign.status = 'paused'
        campaign.save()
        
        messages.success(request, f'Campaign "{campaign.name}" paused successfully!')
        return JsonResponse({'success': True, 'message': 'Campaign paused successfully'})
    
    def _resume_campaign(self, request, campaign):
        """Resume a paused campaign."""
        if campaign.status != 'paused':
            return JsonResponse({'error': 'Only paused campaigns can be resumed'}, status=400)
        
        campaign.status = 'active'
        campaign.save()
        
        messages.success(request, f'Campaign "{campaign.name}" resumed successfully!')
        return JsonResponse({'success': True, 'message': 'Campaign resumed successfully'})
    
    def _stop_campaign(self, request, campaign):
        """Stop an active campaign."""
        if campaign.status not in ['active', 'paused']:
            return JsonResponse({'error': 'Only active or paused campaigns can be stopped'}, status=400)
        
        campaign.status = 'cancelled'
        campaign.save()
        
        messages.success(request, f'Campaign "{campaign.name}" stopped successfully!')
        return JsonResponse({'success': True, 'message': 'Campaign stopped successfully'})
    
    def _retry_failed_sessions(self, request, campaign):
        """Retry failed sessions for a campaign."""
        try:
            failed_sessions = CampaignSession.objects.filter(
                campaign=campaign,
                status='failed'
            )
            
            retry_count = 0
            for session in failed_sessions:
                session.status = 'queued'
                session.retry_count += 1
                session.error_message = ''
                session.save()
                retry_count += 1
            
            messages.success(request, f'Retried {retry_count} failed sessions for campaign "{campaign.name}"!')
            return JsonResponse({'success': True, 'message': f'Retried {retry_count} failed sessions'})
            
        except Exception as e:
            return JsonResponse({'error': f'Error retrying sessions: {str(e)}'}, status=500)


@method_decorator(login_required, name='dispatch')
class CampaignCreateView(CampaignBaseView):
    """Create a new campaign."""
    
    def get(self, request):
        # Check campaign creation limit
        limit_check = check_tenant_limit(request, 'campaigns_per_month')
        
        # Get assistants for this tenant (including all statuses for flexibility)
        tenant_id = request.tenant_flags['tenant_id']
        assistants = Assistant.objects.filter(
            client_id=tenant_id,
        ).order_by('name')
        
        context = {
            'limit_check': limit_check,
            'assistants': assistants,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/campaign_create.html', context)
    
    def post(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Check if within campaign limit
        limit_check = check_tenant_limit(request, 'campaigns_per_month')
        if not limit_check['within_limit']:
            return JsonResponse({
                'error': 'Campaign limit exceeded',
                'limit_info': limit_check
            }, status=429)
        
        try:
            # Debug: Log the received form data
            logger.info(f"Creating campaign with form data: {dict(request.POST)}")
            logger.info(f"Contacts data received: {request.POST.get('contacts_data', '[]')}")
            
            # Create campaign
            campaign = Campaign.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                prompt_template=request.POST.get('script_template'),  # Map script_template to prompt_template
                voice_id=request.POST.get('voice_id', ''),
                tenant_id=tenant_id,
                created_by=request.user,
                max_calls=int(request.POST.get('max_calls', 1000)),
                max_concurrent=int(request.POST.get('max_concurrent', 10))
            )
            
            # Set assistant if provided
            assistant_id = request.POST.get('assistant')
            if assistant_id:
                try:
                    # Accept both draft and published assistants for flexibility
                    assistant = Assistant.objects.get(
                        id=assistant_id,
                        client_id=tenant_id,
                        status__in=['draft', 'published']
                    )
                    campaign.assistant = assistant
                    campaign.save()
                except Assistant.DoesNotExist:
                    pass  # Assistant not found, continue without it
            
            # Store additional campaign data in agent_config
            campaign.agent_config = {
                'use_case': request.POST.get('use_case', ''),
                'channel': request.POST.get('channel', 'voice'),
                'language': request.POST.get('language', 'en'),
                'priority': request.POST.get('priority', 'normal'),
                'campaign_variables': request.POST.get('campaign_variables', ''),
                'start_date': request.POST.get('start_date', ''),
                'end_date': request.POST.get('end_date', ''),
                'start_local_time': request.POST.get('start_local_time', ''),
                'end_local_time': request.POST.get('end_local_time', ''),
                'days_of_week': request.POST.getlist('days_of_week'),
                'max_attempts': int(request.POST.get('max_attempts', 3)),
                'retry_on': request.POST.getlist('retry_on'),
                'backoff_seconds': request.POST.get('backoff_seconds', '60, 180, 600')
            }
            
            # Store contacts data
            contacts_data = request.POST.get('contacts_data', '[]')
            logger.info(f"Raw contacts_data: {contacts_data}")
            
            try:
                campaign.contacts = json.loads(contacts_data)
                logger.info(f"Parsed contacts: {campaign.contacts}")
                
                # Ensure contacts have the required structure
                if campaign.contacts:
                    # Extract phone numbers for validation
                    phone_numbers = []
                    for contact in campaign.contacts:
                        logger.info(f"Processing contact: {contact}")
                        if isinstance(contact, dict) and contact.get('phone'):
                            phone_numbers.append(contact['phone'])
                            logger.info(f"Added phone number: {contact['phone']}")
                        elif isinstance(contact, str):
                            phone_numbers.append(contact)
                            logger.info(f"Added string phone: {contact}")
                    
                    # Store phone numbers separately for easy access
                    # Ensure phone_numbers is stored as a proper list, not a string
                    campaign.agent_config['phone_numbers'] = phone_numbers
                    campaign.agent_config['total_contacts'] = len(campaign.contacts)
                    
                    logger.info(f"Stored phone_numbers in agent_config: {phone_numbers} (type: {type(phone_numbers)})")
                    
                    logger.info(f"Campaign {campaign.id} created with {len(phone_numbers)} phone numbers: {phone_numbers}")
                else:
                    logger.warning(f"Campaign {campaign.id} created with no contacts")
                    
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to parse contacts data for campaign {campaign.id}: {e}")
                campaign.contacts = []
                campaign.agent_config['phone_numbers'] = []
                campaign.agent_config['total_contacts'] = 0
            
            campaign.save()
            logger.info(f"Final campaign.contacts: {campaign.contacts}")
            logger.info(f"Final campaign.agent_config: {campaign.agent_config}")
            
            # Increment usage
            increment_tenant_usage(request, 'campaigns_per_month', 1)
            
            # Log the creation
            tenant_audit_log(request, 'campaign_created', f'campaign_{campaign.id}', {
                'tenant_id': tenant_id,
                'campaign_id': campaign.id,
                'campaign_name': campaign.name
            })
            
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to create campaign: {str(e)}'}, status=500)


@method_decorator(login_required, name='dispatch')
class CampaignEditView(CampaignBaseView):
    """Edit an existing campaign."""
    
    def get(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        # Get assistants for this tenant (including draft for flexibility)
        assistants = Assistant.objects.filter(
            client_id=tenant_id,
            status__in=['draft', 'published']
        ).order_by('name')
        
        context = {
            'campaign': campaign,
            'assistants': assistants,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/campaign_edit.html', context)
    
    def post(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        try:
            # Update campaign
            campaign.name = request.POST.get('name')
            campaign.description = request.POST.get('description', '')
            campaign.prompt_template = request.POST.get('script_template', '')  # Map script_template to prompt_template
            campaign.voice_id = request.POST.get('voice_id', '')
            campaign.max_calls = int(request.POST.get('max_calls', 1000))
            campaign.max_concurrent = int(request.POST.get('max_concurrent', 10))
            
            # Update assistant if provided
            assistant_id = request.POST.get('assistant')
            if assistant_id:
                try:
                    # Accept both draft and published assistants for flexibility
                    assistant = Assistant.objects.get(
                        id=assistant_id,
                        client_id=tenant_id,
                        status__in=['draft', 'published']
                    )
                    campaign.assistant = assistant
                except Assistant.DoesNotExist:
                    campaign.assistant = None
            else:
                campaign.assistant = None
            
            # Update additional campaign data in agent_config
            campaign.agent_config.update({
                'use_case': request.POST.get('use_case', ''),
                'channel': request.POST.get('channel', 'voice'),
                'language': request.POST.get('language', 'en'),
                'priority': request.POST.get('priority', 'normal'),
                'campaign_variables': request.POST.get('campaign_variables', ''),
                'start_date': request.POST.get('start_date', ''),
                'end_date': request.POST.get('end_date', ''),
                'start_local_time': request.POST.get('start_local_time', ''),
                'end_local_time': request.POST.get('end_local_time', ''),
                'days_of_week': request.POST.getlist('days_of_week'),
                'max_attempts': int(request.POST.get('max_attempts', 3)),
                'retry_on': request.POST.getlist('retry_on'),
                'backoff_seconds': request.POST.get('backoff_seconds', '60, 180, 600')
            })
            campaign.save()
            
            # Log the update
            tenant_audit_log(request, 'campaign_updated', f'campaign_{campaign.id}', {
                'tenant_id': tenant_id,
                'campaign_id': campaign.id,
                'campaign_name': campaign.name
            })
            
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to update campaign: {str(e)}'}, status=500)


@method_decorator(login_required, name='dispatch')
class CampaignLaunchView(CampaignBaseView):
    """Launch a campaign."""
    
    def post(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        # Check concurrent campaign limit
        limit_check = check_tenant_limit(request, 'concurrent_campaigns')
        if not limit_check['within_limit']:
            return JsonResponse({
                'error': 'Concurrent campaign limit exceeded',
                'limit_info': limit_check
            }, status=429)
        
        try:
            # Debug: Log campaign data
            logger.info(f"Launching campaign {campaign.id}")
            logger.info(f"Campaign contacts: {campaign.contacts}")
            logger.info(f"Campaign agent_config: {campaign.agent_config}")
            
            print(f"DEBUG: Campaign {campaign.id} agent_config: {campaign.agent_config}")
            print(f"DEBUG: Campaign {campaign.id} agent_config keys: {list(campaign.agent_config.keys())}")
            
            # Get phone numbers from the campaign's stored contacts
            phone_numbers = []
            
            # First try to get from contacts field
            if campaign.contacts:
                logger.info(f"Processing {len(campaign.contacts)} contacts from contacts field")
                for contact in campaign.contacts:
                    logger.info(f"Processing contact: {contact}")
                    if isinstance(contact, dict) and contact.get('phone'):
                        phone_numbers.append(contact['phone'])
                        logger.info(f"Added phone from dict: {contact['phone']}")
                    elif isinstance(contact, str):
                        phone_numbers.append(contact)
                        logger.info(f"Added phone from string: {contact}")
            
            # Fallback to agent_config if no phone numbers found in contacts
            # Check both possible keys for phone numbers
            logger.info(f"Checking agent_config keys: {list(campaign.agent_config.keys())}")
            logger.info(f"Looking for phone numbers in agent_config...")
            
            agent_phone_numbers = None
            if campaign.agent_config.get('phone_numbers'):
                agent_phone_numbers = campaign.agent_config['phone_numbers']
                logger.info(f"Found phone numbers in agent_config['phone_numbers']: {agent_phone_numbers}")
            elif campaign.agent_config.get('agent_config_phone_numbers'):
                agent_phone_numbers = campaign.agent_config['agent_config_phone_numbers']
                logger.info(f"Found phone numbers in agent_config['agent_config_phone_numbers']: {agent_phone_numbers}")
            else:
                logger.warning(f"No phone numbers found in agent_config. Available keys: {list(campaign.agent_config.keys())}")
            
            if agent_phone_numbers:
                print(f"DEBUG: Found agent_phone_numbers: {agent_phone_numbers} (type: {type(agent_phone_numbers)})")
                
                # Handle both list and string representations
                if isinstance(agent_phone_numbers, str):
                    try:
                        # Try to parse as JSON if it's a string
                        import ast
                        phone_numbers = ast.literal_eval(agent_phone_numbers)
                        print(f"DEBUG: Parsed phone numbers from string: {phone_numbers}")
                        logger.info(f"Parsed phone numbers from string: {phone_numbers}")
                    except (ValueError, SyntaxError) as e:
                        print(f"DEBUG: Failed to parse phone numbers string: {e}")
                        logger.error(f"Failed to parse phone numbers string: {e}")
                        phone_numbers = []
                elif isinstance(agent_phone_numbers, list):
                    phone_numbers = agent_phone_numbers
                    print(f"DEBUG: Using phone numbers from list: {phone_numbers}")
                    logger.info(f"Using phone numbers from list: {phone_numbers}")
                else:
                    print(f"DEBUG: Unexpected phone_numbers type: {type(agent_phone_numbers)}")
                    logger.error(f"Unexpected phone_numbers type: {type(agent_phone_numbers)}")
                    phone_numbers = []
            else:
                print(f"DEBUG: No agent_phone_numbers found")
            
            logger.info(f"Final phone_numbers list: {phone_numbers}")
            
            if not phone_numbers:
                logger.error(f"Campaign {campaign.id} has no phone numbers. Contacts: {campaign.contacts}, Agent config: {campaign.agent_config}")
                return JsonResponse({
                    'error': 'No phone numbers provided for campaign. Please add contacts before launching.'
                }, status=400)
            
            # Initialize queue service
            queue_service = CampaignQueueService()
            
            try:
                # Publish campaign to Redis queue
                publish_result = queue_service.publish_campaign(campaign, phone_numbers)
                
                if not publish_result['success']:
                    return JsonResponse({
                        'error': f'Failed to publish campaign to queue: {publish_result["error"]}'
                    }, status=500)
                
                # Update campaign status
                campaign.status = 'active'
                campaign.start_date = timezone.now()
                campaign.save()
                
                # Increment concurrent usage
                increment_tenant_usage(request, 'concurrent_campaigns', 1)
                
                # Log the launch
                tenant_audit_log(request, 'campaign_launched', f'campaign_{campaign.id}', {
                    'tenant_id': tenant_id,
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'queue_message_id': publish_result['message_id'],
                    'total_calls': publish_result['total_calls']
                })
                
                return JsonResponse({
                    'message': 'Campaign launched successfully',
                    'queue_info': {
                        'message_id': publish_result['message_id'],
                        'stream_name': publish_result['stream_name'],
                        'total_calls': publish_result['total_calls'],
                        'published_at': publish_result['published_at']
                    }
                })
                
            finally:
                # Always close the queue service connection
                queue_service.close()
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to launch campaign: {str(e)}'}, status=500)


@method_decorator(login_required, name='dispatch')
class QueueTrackerView(CampaignBaseView):
    """View campaign queue and track execution."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get active campaigns
        active_campaigns = Campaign.objects.filter(
            tenant_id=tenant_id, 
            status='active'
        )
        
        # Get queue items
        queue_items = CampaignQueue.objects.filter(
            campaign__tenant_id=tenant_id
        ).select_related('campaign', 'session').order_by('priority', 'position')
        
        # Get processing statistics
        stats = {
            'queued': queue_items.filter(is_processing=False).count(),
            'processing': queue_items.filter(is_processing=True).count(),
            'total': queue_items.count()
        }
        
        # Log the access
        tenant_audit_log(request, 'queue_tracker_view', 'queue_tracker', {
            'tenant_id': tenant_id
        })
        
        context = {
            'active_campaigns': active_campaigns,
            'queue_items': queue_items,
            'stats': stats,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/queue_tracker.html', context)


@method_decorator(login_required, name='dispatch')
class QueueStatusView(CampaignBaseView):
    """Get real-time status of the Redis queue for campaigns."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        try:
            # Initialize queue service
            queue_service = CampaignQueueService()
            
            try:
                # Get queue status
                queue_status = queue_service.get_queue_status(tenant_id)
                
                return JsonResponse({
                    'success': True,
                    'queue_status': queue_status,
                    'tenant_id': tenant_id
                })
                
            finally:
                # Always close the queue service connection
                queue_service.close()
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SessionsView(CampaignBaseView):
    """View campaign sessions with filtering and search."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get sessions for this tenant
        sessions = CampaignSession.objects.filter(
            tenant_id=tenant_id
        ).select_related('campaign').order_by('-created_at')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            sessions = sessions.filter(
                Q(session_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(campaign__name__icontains=search_query)
            )
        
        # Filter by status
        status_filter = request.GET.get('status', '')
        if status_filter:
            sessions = sessions.filter(status=status_filter)
        
        # Filter by campaign
        campaign_filter = request.GET.get('campaign', '')
        if campaign_filter:
            sessions = sessions.filter(campaign_id=campaign_filter)
        
        # Pagination
        paginator = Paginator(sessions, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get campaigns for filter dropdown
        campaigns = Campaign.objects.filter(tenant_id=tenant_id).values('id', 'name')
        
        # Log the access
        tenant_audit_log(request, 'sessions_view', 'sessions_list', {
            'tenant_id': tenant_id,
            'search_query': search_query,
            'status_filter': status_filter,
            'campaign_filter': campaign_filter
        })
        
        context = {
            'sessions': page_obj,
            'campaigns': campaigns,
            'search_query': search_query,
            'status_filter': status_filter,
            'campaign_filter': campaign_filter,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/sessions.html', context)


# API endpoints for AJAX calls
@require_tenant_context
def campaign_stats_api(request):
    """Get campaign statistics for the current tenant."""
    tenant_id = request.tenant_flags['tenant_id']
    
    # Get campaign statistics
    campaigns = Campaign.objects.filter(tenant_id=tenant_id)
    
    stats = {
        'total_campaigns': campaigns.count(),
        'active_campaigns': campaigns.filter(status='active').count(),
        'total_calls': sum(c.total_calls for c in campaigns),
        'successful_calls': sum(c.successful_calls for c in campaigns),
        'failed_calls': sum(c.failed_calls for c in campaigns),
        'avg_success_rate': campaigns.aggregate(avg_rate=Avg('success_rate'))['avg_rate'] or 0
    }
    
    return JsonResponse(stats)


@require_tenant_context
def queue_status_api(request):
    """Get queue status for the current tenant."""
    tenant_id = request.tenant_flags['tenant_id']
    
    # Get queue statistics
    queue_items = CampaignQueue.objects.filter(campaign__tenant_id=tenant_id)
    
    status = {
        'queued': queue_items.filter(is_processing=False).count(),
        'processing': queue_items.filter(is_processing=True).count(),
        'total': queue_items.count(),
        'by_priority': {
            'urgent': queue_items.filter(priority=4).count(),
            'high': queue_items.filter(priority=3).count(),
            'normal': queue_items.filter(priority=2).count(),
            'low': queue_items.filter(priority=1).count(),
        }
    }
    
    return JsonResponse(status)
