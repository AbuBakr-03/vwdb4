"""
Integration examples showing how to use the authorization module
with existing Django applications.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# Import authorization utilities
from .consumer_middleware import require_feature, require_plan, has_feature
from .utils import get_tenant_info, check_tenant_limit, tenant_audit_log


# Example 1: Dashboard Integration
# ===============================

@require_feature("dashboard")
def dashboard_view(request):
    """
    Example of integrating with your existing dashboard app.
    This view requires the 'dashboard' feature.
    """
    tenant_info = get_tenant_info(request)
    
    # Log the dashboard access
    tenant_audit_log(request, 'feature_access', 'dashboard', {
        'view': 'dashboard_view',
        'tenant_plan': tenant_info['plan']
    })
    
    # Check usage limits
    usage_info = check_tenant_limit(request, 'dashboard_views', 1)
    
    context = {
        'tenant_id': tenant_info['tenant_id'],
        'plan': tenant_info['plan'],
        'features': tenant_info['features'],
        'usage_info': usage_info
    }
    
    return render(request, 'dashboard/index.html', context)


# Example 2: Analytics Integration
# ===============================

@require_feature("analytics")
@require_plan("pro")
def analytics_dashboard(request):
    """
    Example of integrating with your existing analytics app.
    Requires both 'analytics' feature and 'pro' plan.
    """
    tenant_info = get_tenant_info(request)
    
    # Log analytics access
    tenant_audit_log(request, 'feature_access', 'analytics', {
        'plan': 'pro',
        'features_used': ['analytics']
    })
    
    # Check if tenant has additional analytics features
    has_advanced_analytics = has_feature(request, "advanced_analytics")
    has_export = has_feature(request, "data_export")
    
    context = {
        'tenant_info': tenant_info,
        'has_advanced_analytics': has_advanced_analytics,
        'has_export': has_export,
        'plan': tenant_info['plan']
    }
    
    return render(request, 'analytics/dashboard.html', context)


# Example 3: Campaign Management Integration
# =========================================

@require_feature("campaigns")
def campaign_list(request):
    """
    Example of integrating with your existing campaigns app.
    Requires 'campaigns' feature.
    """
    tenant_info = get_tenant_info(request)
    
    # Check campaign limits
    campaign_limits = check_tenant_limit(request, 'campaigns', 5)
    
    # Log campaign access
    tenant_audit_log(request, 'feature_access', 'campaigns', {
        'action': 'list_campaigns',
        'limits': campaign_limits
    })
    
    context = {
        'tenant_info': tenant_info,
        'campaign_limits': campaign_limits,
        'can_create_campaign': campaign_limits['within_limit']
    }
    
    return render(request, 'campaigns/list.html', context)


@require_feature("campaigns")
def create_campaign(request):
    """
    Example of creating a campaign with usage tracking.
    """
    if request.method == 'POST':
        # Check if within campaign limits
        limit_check = check_tenant_limit(request, 'campaigns')
        
        if not limit_check['within_limit']:
            return JsonResponse({
                'error': 'Campaign limit exceeded',
                'limit_info': limit_check
            }, status=429)
        
        # Process campaign creation
        # ... your campaign creation logic here ...
        
        # Log the campaign creation
        tenant_audit_log(request, 'data_access', 'campaigns', {
            'action': 'create_campaign',
            'campaign_name': request.POST.get('name', 'Unknown')
        })
        
        return JsonResponse({'message': 'Campaign created successfully'})
    
    return render(request, 'campaigns/create.html')


# Example 4: API Integration
# ==========================

class CampaignAPIView(View):
    """
    Example of integrating with API endpoints.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if tenant has API access
        if not has_feature(request, "api"):
            return JsonResponse({
                'error': 'API access not available'
            }, status=403)
        
        # Check API rate limits
        api_limits = check_tenant_limit(request, 'api_calls')
        if not api_limits['within_limit']:
            return JsonResponse({
                'error': 'API rate limit exceeded',
                'limit_info': api_limits
            }, status=429)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """GET campaigns - requires 'campaigns' feature."""
        if not has_feature(request, "campaigns"):
            return JsonResponse({'error': 'Campaigns feature not available'}, status=403)
        
        # Log API usage
        tenant_audit_log(request, 'data_access', 'api', {
            'method': 'GET',
            'endpoint': 'campaigns'
        })
        
        # Your API logic here
        return JsonResponse({'campaigns': []})
    
    def post(self, request):
        """POST campaign - requires 'campaigns' feature and plan check."""
        if not has_feature(request, "campaigns"):
            return JsonResponse({'error': 'Campaigns feature not available'}, status=403)
        
        # Check plan for campaign creation
        tenant_plan = get_tenant_info(request)['plan']
        if tenant_plan not in ['pro', 'enterprise']:
            return JsonResponse({
                'error': 'Campaign creation requires Pro or Enterprise plan'
            }, status=403)
        
        # Log API usage
        tenant_audit_log(request, 'data_access', 'api', {
            'method': 'POST',
            'endpoint': 'campaigns',
            'plan_required': 'pro+'
        })
        
        # Your API logic here
        return JsonResponse({'message': 'Campaign created via API'})


# Example 5: Template Integration
# ===============================

def dashboard_with_features(request):
    """
    Example of passing tenant information to templates.
    """
    # Get tenant context
    tenant_info = get_tenant_info(request)
    
    # Check various features
    features = {
        'has_analytics': has_feature(request, "analytics"),
        'has_campaigns': has_feature(request, "campaigns"),
        'has_api': has_feature(request, "api"),
        'has_webhooks': has_feature(request, "webhooks"),
        'has_audit_logs': has_feature(request, "audit_logs"),
    }
    
    # Check plan-based features
    plan_features = {
        'is_pro': tenant_info['plan'] in ['pro', 'enterprise'],
        'is_enterprise': tenant_info['plan'] == 'enterprise',
        'can_export': has_feature(request, "data_export"),
        'can_integrate': has_feature(request, "third_party_integration"),
    }
    
    # Check usage limits
    limits = {
        'campaigns': check_tenant_limit(request, 'campaigns'),
        'api_calls': check_tenant_limit(request, 'api_calls'),
        'users': check_tenant_limit(request, 'seats'),
    }
    
    context = {
        'tenant_info': tenant_info,
        'features': features,
        'plan_features': plan_features,
        'limits': limits,
    }
    
    return render(request, 'dashboard/features.html', context)


# Example 6: Conditional Feature Rendering
# ========================================

def conditional_dashboard(request):
    """
    Example of conditionally rendering features based on tenant capabilities.
    """
    tenant_info = get_tenant_info(request)
    
    # Determine which widgets to show
    widgets = []
    
    if has_feature(request, "watchtower"):
        widgets.append({
            'name': 'watchtower',
            'title': 'System Monitoring',
            'icon': 'monitor',
            'enabled': True
        })
    
    if has_feature(request, "analytics"):
        widgets.append({
            'name': 'analytics',
            'title': 'Analytics Dashboard',
            'icon': 'chart',
            'enabled': True
        })
    
    if has_feature(request, "campaigns"):
        widgets.append({
            'name': 'campaigns',
            'title': 'Campaign Manager',
            'icon': 'megaphone',
            'enabled': True
        })
    
    # Add plan-specific widgets
    if tenant_info['plan'] in ['pro', 'enterprise']:
        widgets.append({
            'name': 'advanced_features',
            'title': 'Advanced Features',
            'icon': 'star',
            'enabled': True
        })
    
    if tenant_info['plan'] == 'enterprise':
        widgets.append({
            'name': 'enterprise_tools',
            'title': 'Enterprise Tools',
            'icon': 'crown',
            'enabled': True
        })
    
    context = {
        'tenant_info': tenant_info,
        'widgets': widgets,
        'total_widgets': len(widgets)
    }
    
    return render(request, 'dashboard/widgets.html', context)


# Example 7: Usage Tracking Integration
# ====================================

def track_feature_usage(request, feature_name):
    """
    Example of tracking feature usage for billing and analytics.
    """
    from .utils import increment_tenant_usage
    
    # Increment usage for the feature
    usage_update = increment_tenant_usage(request, f'{feature_name}_usage', 1)
    
    # Log the usage
    tenant_audit_log(request, 'feature_use', feature_name, {
        'usage_update': usage_update,
        'feature': feature_name
    })
    
    return JsonResponse({
        'message': f'{feature_name} usage tracked',
        'usage_info': usage_update
    })


# Example 8: Error Handling with Tenant Context
# =============================================

def handle_tenant_error(request, error_type, details=None):
    """
    Example of handling errors with tenant context.
    """
    tenant_info = get_tenant_info(request)
    
    # Log the error
    tenant_audit_log(request, 'error', error_type, {
        'error_type': error_type,
        'details': details,
        'tenant_plan': tenant_info['plan'] if tenant_info else 'unknown'
    })
    
    # Return appropriate error response
    error_response = {
        'error': error_type,
        'tenant_id': tenant_info['tenant_id'] if tenant_info else None,
        'timestamp': timezone.now().isoformat()
    }
    
    if details:
        error_response['details'] = details
    
    return JsonResponse(error_response, status=400)


# Import timezone for error handling
from django.utils import timezone
