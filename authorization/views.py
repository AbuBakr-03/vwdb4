from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .consumer_middleware import (
    has_feature, 
    require_feature, 
    require_plan, 
    get_tenant_limit
)
from .utils import (
    get_tenant_info, 
    check_tenant_limit, 
    increment_tenant_usage,
    require_tenant_context,
    tenant_audit_log,
    fetch_tenant_token,
    get_cached_token,
    refresh_tenant_token,
    validate_client_credentials
)


# Token Management Views
# =====================

@csrf_exempt
@require_http_methods(["POST"])
def get_token(request):
    """
    Get a JWT token for a tenant from the tenant management system.
    
    This endpoint acts as a proxy to the tenant management system's /v1/token endpoint.
    Accepts both form-encoded and JSON data.
    """
    try:
        # Try to get data from JSON first, then fall back to form data
        if request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                client_id = data.get('client_id')
                client_secret = data.get('client_secret')
                tenant_id = data.get('tenant_id')
                audience = data.get('audience', 'watchtower')
            except (json.JSONDecodeError, AttributeError):
                return JsonResponse({
                    'error': 'Invalid JSON data'
                }, status=400)
        else:
            # Form-encoded data
            client_id = request.POST.get('client_id')
            client_secret = request.POST.get('client_secret')
            tenant_id = request.POST.get('tenant_id')
            audience = request.POST.get('audience', 'watchtower')
        
        # Validate required fields
        if not all([client_id, client_secret, tenant_id]):
            return JsonResponse({
                'error': 'Missing required fields: client_id, client_secret, tenant_id'
            }, status=400)
        
        # Validate client credentials (optional security check)
        if getattr(settings, 'TENANT_VALIDATE_CLIENT_CREDENTIALS', False):
            if not validate_client_credentials(client_id, client_secret):
                return JsonResponse({
                    'error': 'Invalid client credentials'
                }, status=401)
        
        # Check if we have a cached token first
        cached_token = get_cached_token(tenant_id, audience)
        if cached_token:
            return JsonResponse({
                'access_token': cached_token,
                'source': 'cache',
                'message': 'Token retrieved from cache'
            })
        
        # Fetch new token from tenant management system
        token_data = fetch_tenant_token(client_id, client_secret, tenant_id, audience)
        
        # Log the token request
        tenant_audit_log(
            request, 
            'token_request', 
            'get_token',
            {
                'tenant_id': tenant_id,
                'audience': audience,
                'source': 'tenant_management'
            }
        )
        
        return JsonResponse({
            'access_token': token_data['access_token'],
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in', 600),
            'tenant_id': token_data.get('tenant_id', tenant_id),
            'plan': token_data.get('plan'),
            'features': token_data.get('features', []),
            'source': 'tenant_management'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to get token: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    Force refresh a tenant token by fetching a new one.
    Accepts both form-encoded and JSON data.
    """
    try:
        # Try to get data from JSON first, then fall back to form data
        if request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                client_id = data.get('client_id')
                client_secret = data.get('client_secret')
                tenant_id = data.get('tenant_id')
                audience = data.get('audience', 'watchtower')
            except (json.JSONDecodeError, AttributeError):
                return JsonResponse({
                    'error': 'Invalid JSON data'
                }, status=400)
        else:
            # Form-encoded data
            client_id = request.POST.get('client_id')
            client_secret = request.POST.get('client_secret')
            tenant_id = request.POST.get('tenant_id')
            audience = request.POST.get('audience', 'watchtower')
        
        # Validate required fields
        if not all([client_id, client_secret, tenant_id]):
            return JsonResponse({
                'error': 'Missing required fields: client_id, client_secret, tenant_id'
            }, status=400)
        
        # Force refresh the token
        token_data = refresh_tenant_token(client_id, client_secret, tenant_id, audience)
        
        # Log the token refresh
        tenant_audit_log(
            request, 
            'token_refresh', 
            'refresh_token',
            {
                'tenant_id': tenant_id,
                'audience': audience
            }
        )
        
        return JsonResponse({
            'access_token': token_data['access_token'],
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in', 600),
            'tenant_id': token_data.get('tenant_id', tenant_id),
            'plan': token_data.get('plan'),
            'features': token_data.get('features', []),
            'source': 'refreshed'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to refresh token: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def token_status(request):
    """
    Get the status of cached tokens for a tenant.
    """
    tenant_id = request.GET.get('tenant_id')
    audience = request.GET.get('audience', 'watchtower')
    
    if not tenant_id:
        return JsonResponse({
            'error': 'Missing tenant_id parameter'
        }, status=400)
    
    # Check cached token status
    cached_token = get_cached_token(tenant_id, audience)
    
    if cached_token:
        return JsonResponse({
            'tenant_id': tenant_id,
            'audience': audience,
            'has_cached_token': True,
            'token_preview': f"{cached_token[:20]}...",
            'message': 'Token is cached and available'
        })
    else:
        return JsonResponse({
            'tenant_id': tenant_id,
            'audience': audience,
            'has_cached_token': False,
            'message': 'No cached token available'
        })


@require_feature("watchtower")
def watchtower_dashboard(request):
    """
    Example view that requires the 'watchtower' feature.
    """
    tenant_info = get_tenant_info(request)
    
    # Log the feature access
    tenant_audit_log(
        request, 
        'feature_access', 
        'watchtower_dashboard',
        {'view': 'watchtower_dashboard'}
    )
    
    return JsonResponse({
        'message': 'Welcome to Watchtower Dashboard',
        'tenant_info': tenant_info,
        'features': list(request.tenant_flags.get('features', []))
    })


@require_plan("pro")
def pro_analytics(request):
    """
    Example view that requires the 'pro' plan.
    """
    tenant_info = get_tenant_info(request)
    
    # Check usage limits
    usage_info = check_tenant_limit(request, 'api_calls', 150)
    
    # Increment usage
    increment_tenant_usage(request, 'api_calls', 1)
    
    # Log the action
    tenant_audit_log(
        request, 
        'data_access', 
        'pro_analytics',
        {'usage_info': usage_info}
    )
    
    return JsonResponse({
        'message': 'Pro Analytics Dashboard',
        'tenant_info': tenant_info,
        'usage_info': usage_info
    })


@require_tenant_context
def tenant_status(request):
    """
    Example view that requires tenant context but no specific features.
    """
    tenant_info = get_tenant_info(request)
    
    # Get various limits
    limits = {}
    for limit_name in ['seats', 'concurrency', 'api_calls']:
        limits[limit_name] = check_tenant_limit(request, limit_name)
    
    return JsonResponse({
        'message': 'Tenant Status',
        'tenant_info': tenant_info,
        'limits': limits
    })


@require_feature("ivr")
@require_plan("enterprise")
def enterprise_ivr(request):
    """
    Example view that requires both a specific feature and plan.
    """
    tenant_info = get_tenant_info(request)
    
    # Log the premium feature access
    tenant_audit_log(
        request, 
        'feature_access', 
        'enterprise_ivr',
        {'plan': 'enterprise', 'feature': 'ivr'}
    )
    
    return JsonResponse({
        'message': 'Enterprise IVR System',
        'tenant_info': tenant_info,
        'plan': request.tenant_flags.get('plan')
    })


@csrf_exempt
@require_http_methods(["POST"])
def update_tenant_usage(request):
    """
    Example API endpoint for updating tenant usage.
    """
    if not hasattr(request, 'tenant_flags'):
        return JsonResponse({'error': 'Tenant context required'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
        limit_name = data.get('limit_name')
        amount = data.get('amount', 1)
        
        if not limit_name:
            return JsonResponse({'error': 'limit_name is required'}, status=400)
        
        # Check if within limits
        limit_check = check_tenant_limit(request, limit_name)
        if not limit_check['within_limit']:
            tenant_audit_log(
                request, 
                'limit_exceeded', 
                limit_name,
                {'attempted_amount': amount, 'current_limit': limit_check['limit']}
            )
            return JsonResponse({
                'error': f'Limit exceeded for {limit_name}',
                'limit_info': limit_check
            }, status=429)
        
        # Increment usage
        usage_update = increment_tenant_usage(request, limit_name, amount)
        
        # Log the usage update
        tenant_audit_log(
            request, 
            'data_access', 
            limit_name,
            {'usage_update': usage_update}
        )
        
        return JsonResponse({
            'message': f'Usage updated for {limit_name}',
            'usage_info': usage_update
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class TenantAPIView(View):
    """
    Example class-based view with tenant authorization.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if tenant context exists
        if not hasattr(request, 'tenant_flags'):
            return JsonResponse({'error': 'Tenant context required'}, status=401)
        
        # Check if tenant is active
        if not request.tenant_flags.get('system_enabled', False):
            return JsonResponse({'error': 'Tenant access disabled'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """GET method - requires no specific features."""
        tenant_info = get_tenant_info(request)
        
        return JsonResponse({
            'message': 'Tenant API Info',
            'tenant_info': tenant_info
        })
    
    @require_feature("api")
    def post(self, request):
        """POST method - requires 'api' feature."""
        tenant_info = get_tenant_info(request)
        
        # Log the API usage
        tenant_audit_log(
            request, 
            'data_access', 
            'tenant_api_post',
            {'method': 'POST'}
        )
        
        return JsonResponse({
            'message': 'Data posted successfully',
            'tenant_info': tenant_info
        })


def health_check(request):
    """
    Health check endpoint that doesn't require tenant context.
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'tenant_management': 'enabled'
    })


# Import timezone for the health check
from django.utils import timezone
