"""
Campaign views with tenant management integration.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone

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
class CampaignListView(CampaignBaseView):
    """List all campaigns for the current tenant."""
    
    def get(self, request):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get campaigns for this tenant
        campaigns = Campaign.objects.filter(tenant_id=tenant_id).order_by('-created_at')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            campaigns = campaigns.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        
        # Filter by status
        status_filter = request.GET.get('status', '')
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)
        
        # Pagination
        paginator = Paginator(campaigns, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get campaign statistics
        stats = {
            'total': campaigns.count(),
            'active': campaigns.filter(status='active').count(),
            'draft': campaigns.filter(status='draft').count(),
            'completed': campaigns.filter(status='completed').count(),
        }
        
        # Log the access
        tenant_audit_log(request, 'campaign_list_view', 'campaigns_list', {
            'tenant_id': tenant_id,
            'search_query': search_query,
            'status_filter': status_filter
        })
        
        context = {
            'campaigns': page_obj,
            'stats': stats,
            'search_query': search_query,
            'status_filter': status_filter,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/campaign_list.html', context)


@method_decorator(login_required, name='dispatch')
class CampaignDetailView(CampaignBaseView):
    """View campaign details and sessions."""
    
    def get(self, request, campaign_id):
        tenant_id = request.tenant_flags['tenant_id']
        
        # Get campaign for this tenant
        campaign = get_object_or_404(Campaign, id=campaign_id, tenant_id=tenant_id)
        
        # Get campaign sessions
        sessions = campaign.sessions.all().order_by('-created_at')
        
        # Get queue items
        queue_items = campaign.queue_items.all().order_by('priority', 'position')
        
        # Log the access
        tenant_audit_log(request, 'campaign_detail_view', f'campaign_{campaign_id}', {
            'tenant_id': tenant_id,
            'campaign_id': campaign_id,
            'campaign_name': campaign.name
        })
        
        context = {
            'campaign': campaign,
            'sessions': sessions,
            'queue_items': queue_items,
            'tenant_info': get_tenant_info(request)
        }
        
        return render(request, 'campaigns/campaign_detail.html', context)


@method_decorator(login_required, name='dispatch')
class CampaignCreateView(CampaignBaseView):
    """Create a new campaign."""
    
    def get(self, request):
        # Check campaign creation limit
        limit_check = check_tenant_limit(request, 'campaigns_per_month')
        
        context = {
            'limit_check': limit_check,
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
            # Create campaign
            campaign = Campaign.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                prompt_template=request.POST.get('prompt_template'),
                voice_id=request.POST.get('voice_id', ''),
                tenant_id=tenant_id,
                created_by=request.user,
                max_calls=int(request.POST.get('max_calls', 1000)),
                max_concurrent=int(request.POST.get('max_concurrent', 10))
            )
            
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
        
        context = {
            'campaign': campaign,
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
            campaign.prompt_template = request.POST.get('prompt_template')
            campaign.voice_id = request.POST.get('voice_id', '')
            campaign.max_calls = int(request.POST.get('max_calls', 1000))
            campaign.max_concurrent = int(request.POST.get('max_concurrent', 10))
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
                'campaign_name': campaign.name
            })
            
            return JsonResponse({'message': 'Campaign launched successfully'})
            
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
