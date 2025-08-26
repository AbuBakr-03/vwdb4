"""
Utility functions for tenant authorization and management.
"""

from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import requests
import time


def fetch_tenant_token(client_id, client_secret, tenant_id, audience):
    """
    Fetch a JWT token from the tenant management system.
    
    Args:
        client_id: Client ID for authentication
        client_secret: Client secret for authentication
        tenant_id: ID of the tenant requesting the token
        audience: Audience value for the token
    
    Returns:
        dict: Token response with access_token, expires_in, etc.
    
    Raises:
        Exception: If token fetch fails
    """
    token_url = getattr(settings, 'TENANT_MGMT_TOKEN_URL', 
                       'https://web-production-72006.up.railway.app/v1/token')
    
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'tenant_id': tenant_id,
        'audience': audience
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Cache the token for reuse
        cache_key = f"token:{tenant_id}:{audience}"
        cache.set(cache_key, token_data, token_data.get('expires_in', 600))
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch token: {str(e)}")
    except ValueError as e:
        raise Exception(f"Invalid response from token endpoint: {str(e)}")


def get_cached_token(tenant_id, audience):
    """
    Get a cached token if available and not expired.
    
    Args:
        tenant_id: ID of the tenant
        audience: Audience value for the token
    
    Returns:
        str: Cached token if valid, None otherwise
    """
    cache_key = f"token:{tenant_id}:{audience}"
    token_data = cache.get(cache_key)
    
    if token_data and 'access_token' in token_data:
        return token_data['access_token']
    
    return None


def refresh_tenant_token(client_id, client_secret, tenant_id, audience):
    """
    Force refresh a tenant token by fetching a new one.
    
    Args:
        client_id: Client ID for authentication
        client_secret: Client secret for authentication
        tenant_id: ID of the tenant
        audience: Audience value for the token
    
    Returns:
        dict: New token response
    """
    # Clear any cached token first
    cache_key = f"token:{tenant_id}:{audience}"
    cache.delete(cache_key)
    
    # Fetch new token
    return fetch_tenant_token(client_id, client_secret, tenant_id, audience)


def validate_client_credentials(client_id, client_secret):
    """
    Validate client credentials against configured values.
    
    Args:
        client_id: Client ID to validate
        client_secret: Client secret to validate
    
    Returns:
        bool: True if credentials are valid
    """
    # Get configured credentials from settings
    configured_client_id = getattr(settings, 'TENANT_CLIENT_ID', None)
    configured_client_secret = getattr(settings, 'TENANT_CLIENT_SECRET', None)
    
    if not configured_client_id or not configured_client_secret:
        return False
    
    return (client_id == configured_client_id and 
            client_secret == configured_client_secret)


def get_tenant_info(request):
    """
    Get comprehensive tenant information from the request.
    
    Returns:
        dict: Tenant information including ID, features, limits, and plan
        None: If no tenant flags are attached to the request
    """
    if not hasattr(request, 'tenant_flags'):
        return None
    
    return {
        'tenant_id': request.tenant_flags.get('tenant_id'),
        'features': list(request.tenant_flags.get('features', [])),
        'limits': request.tenant_flags.get('limits', {}),
        'plan': request.tenant_flags.get('plan'),
        'system_enabled': request.tenant_flags.get('system_enabled', False),
        'expires_at': request.tenant_flags.get('exp'),
        'token_id': request.tenant_flags.get('jti')
    }


def check_tenant_limit(request, limit_name, current_usage=None):
    """
    Check if the current tenant is within their limits for a specific resource.
    
    Args:
        request: Django request object
        limit_name: Name of the limit to check (e.g., 'seats', 'concurrency')
        current_usage: Current usage count (optional, for dynamic checking)
    
    Returns:
        dict: Contains 'within_limit' (bool), 'limit' (int), 'usage' (int), 'remaining' (int)
    """
    if not hasattr(request, 'tenant_flags'):
        return {
            'within_limit': False,
            'limit': 0,
            'usage': 0,
            'remaining': 0,
            'error': 'No tenant context'
        }
    
    tenant_limits = request.tenant_flags.get('limits', {})
    limit_value = tenant_limits.get(limit_name, 0)
    
    if current_usage is None:
        # Try to get from cache if not provided
        cache_key = f"usage:{request.tenant_flags['tenant_id']}:{limit_name}"
        current_usage = cache.get(cache_key, 0)
    
    remaining = max(0, limit_value - current_usage)
    within_limit = current_usage < limit_value
    
    return {
        'within_limit': within_limit,
        'limit': limit_value,
        'usage': current_usage,
        'remaining': remaining
    }


def increment_tenant_usage(request, limit_name, amount=1, ttl=300):
    """
    Increment tenant usage for a specific limit.
    
    Args:
        request: Django request object
        limit_name: Name of the limit to increment
        amount: Amount to increment (default: 1)
        ttl: Cache TTL in seconds (default: 5 minutes)
    
    Returns:
        dict: Updated usage information
    """
    if not hasattr(request, 'tenant_flags'):
        return {'error': 'No tenant context'}
    
    tenant_id = request.tenant_flags['tenant_id']
    cache_key = f"usage:{tenant_id}:{limit_name}"
    
    # Get current usage
    current_usage = cache.get(cache_key, 0)
    new_usage = current_usage + amount
    
    # Set new usage with TTL
    cache.set(cache_key, new_usage, ttl)
    
    return {
        'previous_usage': current_usage,
        'new_usage': new_usage,
        'incremented_by': amount,
        'cache_key': cache_key,
        'ttl': ttl
    }


def require_tenant_context(view_func):
    """
    Decorator to ensure a view has tenant context.
    
    Usage:
        @require_tenant_context
        def my_view(request):
            # This view requires tenant context
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant_flags'):
            return JsonResponse(
                {"detail": "Tenant context required"}, 
                status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def tenant_audit_log(request, action, resource=None, details=None):
    """
    Log tenant actions for audit purposes.
    
    Args:
        request: Django request object
        action: Action being performed (e.g., 'login', 'data_access', 'feature_use')
        resource: Resource being accessed (optional)
        details: Additional details (optional)
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    if not hasattr(request, 'tenant_flags'):
        return False
    
    try:
        audit_data = {
            'tenant_id': request.tenant_flags.get('tenant_id'),
            'action': action,
            'resource': resource,
            'details': details,
            'timestamp': time.time(),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'token_id': request.tenant_flags.get('jti')
        }
        
        # Store in cache for now (in production, you might want to use a database)
        cache_key = f"audit:{request.tenant_flags['tenant_id']}:{int(time.time())}"
        cache.set(cache_key, audit_data, 86400)  # 24 hours
        
        return True
        
    except Exception as e:
        print(f"Failed to log audit: {e}")
        return False


def get_tenant_features(request):
    """
    Get a list of features available to the current tenant.
    
    Returns:
        list: List of feature names
        None: If no tenant context
    """
    if not hasattr(request, 'tenant_flags'):
        return None
    
    return list(request.tenant_flags.get('features', []))


def is_tenant_active(request):
    """
    Check if the current tenant is active and enabled.
    
    Returns:
        bool: True if tenant is active, False otherwise
    """
    if not hasattr(request, 'tenant_flags'):
        return False
    
    return request.tenant_flags.get('system_enabled', False)


def get_tenant_plan(request):
    """
    Get the current tenant's subscription plan.
    
    Returns:
        str: Plan name (e.g., 'basic', 'pro', 'enterprise')
        None: If no tenant context or plan
    """
    if not hasattr(request, 'tenant_flags'):
        return None
    
    return request.tenant_flags.get('plan')


def validate_tenant_token(token, jwks_url, audience):
    """
    Validate a tenant token manually (useful for testing or external validation).
    
    Args:
        token: JWT token string
        jwks_url: URL to the JWKS endpoint
        audience: Expected audience value
    
    Returns:
        dict: Token payload if valid
        None: If invalid
    """
    try:
        # Fetch JWKS
        response = requests.get(jwks_url)
        response.raise_for_status()
        jwks = response.json()
        
        # Find the key
        header = jwt.get_unverified_header(token)
        key_id = header.get('kid')
        
        if not key_id:
            return None
        
        # Find the key in JWKS
        signing_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == key_id:
                signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not signing_key:
            return None
        
        # Verify the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=audience,
            options={"require": ["exp", "tid", "kid"]}
        )
        
        return payload
        
    except Exception as e:
        print(f"Token validation failed: {e}")
        return None


def get_token_for_internal_use(tenant_id, audience='watchtower'):
    """
    Get a token for internal use by the Django app.
    This function uses configured client credentials.
    
    Args:
        tenant_id: ID of the tenant
        audience: Audience value for the token
    
    Returns:
        str: JWT token for internal use
    
    Raises:
        Exception: If token fetch fails or credentials not configured
    """
    client_id = getattr(settings, 'TENANT_CLIENT_ID', None)
    client_secret = getattr(settings, 'TENANT_CLIENT_SECRET', None)
    
    if not client_id or not client_secret:
        raise Exception("TENANT_CLIENT_ID and TENANT_CLIENT_SECRET must be configured for internal token fetching")
    
    # Check cache first
    cached_token = get_cached_token(tenant_id, audience)
    if cached_token:
        return cached_token
    
    # Fetch new token
    token_data = fetch_tenant_token(client_id, client_secret, tenant_id, audience)
    return token_data['access_token']


def get_tenant_token_with_fallback(tenant_id, audience='watchtower'):
    """
    Get a tenant token with fallback to internal credentials.
    Useful for background tasks or internal operations.
    
    Args:
        tenant_id: ID of the tenant
        audience: Audience value for the token
    
    Returns:
        str: JWT token or None if not available
    """
    try:
        # Try to get from cache first
        cached_token = get_cached_token(tenant_id, audience)
        if cached_token:
            return cached_token
        
        # Try to get with internal credentials
        return get_token_for_internal_use(tenant_id, audience)
        
    except Exception as e:
        print(f"Failed to get token for tenant {tenant_id}: {e}")
        return None
