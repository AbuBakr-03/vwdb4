"""
Consumer middleware for tenant management integration.
Other Django apps can import and use this middleware to verify tenant tokens.
"""

import time
import requests
import jwt
from jwt import PyJWKClient, InvalidTokenError, ExpiredSignatureError
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class TenantFlagsMiddleware(MiddlewareMixin):
    """
    Middleware that verifies tenant tokens and attaches tenant flags to requests.
    
    Settings required in consumer app:
    - TENANT_MGMT_JWKS_URL: URL to the tenant management JWKS endpoint
    - TENANT_AUDIENCE: Audience value for this app
    - TENANT_CACHE_SECONDS: Cache TTL for tenant flags (default: 30)
    """
    
    CACHE_TTL = getattr(settings, 'TENANT_CACHE_SECONDS', 30)
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.jwk_client = None
        self._init_jwk_client()
    
    def _init_jwk_client(self):
        """Initialize the JWK client for token verification"""
        jwks_url = getattr(settings, 'TENANT_MGMT_JWKS_URL', None)
        if jwks_url:
            try:
                self.jwk_client = PyJWKClient(jwks_url)
            except Exception as e:
                print(f"Warning: Failed to initialize JWK client: {e}")
                self.jwk_client = None
    
    def _get_signing_key(self, token):
        """Get the signing key for a token"""
        if not self.jwk_client:
            raise InvalidTokenError("JWK client not initialized")
        
        try:
            return self.jwk_client.get_signing_key_from_jwt(token).key
        except Exception as e:
            raise InvalidTokenError(f"Failed to get signing key: {e}")
    
    def _parse_tenant_token(self, token):
        """Parse and verify a tenant token"""
        try:
            # Get the signing key
            signing_key = self._get_signing_key(token)
            
            # Verify the token
            audience = getattr(settings, 'TENANT_AUDIENCE', 'default')
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=audience,
                options={"require": ["exp", "tid", "kid"]},
                leeway=300  # Allow 5 minutes clock skew for testing
            )
            
            return payload
            
        except (InvalidTokenError, ExpiredSignatureError) as e:
            raise e
        except Exception as e:
            raise InvalidTokenError(f"Token verification failed: {str(e)}")
    
    def _get_tenant_flags(self, token):
        """Get tenant flags from cache or parse token"""
        # Create a cache key based on token tail
        cache_key = f"tflags:{token[-32:]}"
        
        # Try to get from cache first
        flags = cache.get(cache_key)
        if flags:
            return flags
        
        # Parse the token
        try:
            payload = self._parse_tenant_token(token)
            
            # Extract tenant flags
            flags = {
                "tenant_id": payload["tid"],
                "system_enabled": payload.get("system_enabled", False),
                "features": set(payload.get("features", [])),
                "limits": payload.get("limits", {}),
                "plan": payload.get("plan"),
                "jti": payload.get("jti"),
                "exp": payload.get("exp")
            }
            
            # Cache the flags
            cache.set(cache_key, flags, self.CACHE_TTL)
            
            return flags
            
        except Exception as e:
            # Cache negative results briefly to prevent hammering
            cache.set(cache_key, None, 5)
            raise e
    
    def process_request(self, request):
        """Process the request and verify tenant token"""
        # Check if this path should skip token verification
        skip_token_verification = False
        skip_paths = getattr(settings, 'TENANT_SKIP_PATHS', [])
        for skip_path in skip_paths:
            if request.path.startswith(skip_path):
                skip_token_verification = True
                break
        
        # For web-based authentication, allow requests without JWT tokens
        # but still require tenant context for protected views
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        
        # If no JWT token is provided or token verification is skipped, create a company-specific tenant context for web users
        if not auth_header.startswith("Bearer ") or skip_token_verification:
            # Get company-specific tenant ID from settings
            company_tenant_id = getattr(settings, 'TENANT_ID', 'default_company')
            
            # Check if user is authenticated and is a superuser
            is_superuser = False
            if hasattr(request, 'user') and request.user.is_authenticated:
                is_superuser = request.user.is_superuser
            
            # For web requests, create a company-specific tenant context
            # This allows the views to handle authentication themselves
            if is_superuser:
                # Superusers get unlimited access
                request.tenant_flags = {
                    "tenant_id": company_tenant_id,
                    "system_enabled": True,
                    "features": ["campaigns", "dashboard", "admin"],  # Admin features for superusers
                    "limits": {
                        "campaigns_per_month": 999999,  # Effectively unlimited
                        "concurrent_campaigns": 999999,  # Effectively unlimited
                        "max_calls_per_campaign": 999999,  # Effectively unlimited
                    },
                    "plan": "superuser",
                    "jti": None,
                    "exp": None,
                    "is_superuser": True
                }
            else:
                # Regular web users get default limits
                default_limits = getattr(settings, 'TENANT_LIMITS', {}).get('default', {})
                request.tenant_flags = {
                    "tenant_id": company_tenant_id,
                    "system_enabled": True,
                    "features": ["campaigns", "dashboard"],  # Default features for web users
                    "limits": default_limits,
                    "plan": "web",
                    "jti": None,
                    "exp": None,
                    "is_superuser": False
                }
            return None
        
        # Extract the token
        try:
            raw_token = auth_header.split(" ", 1)[1]
        except IndexError:
            return JsonResponse(
                {"detail": "Invalid Authorization header format"}, 
                status=401
            )
        
        # Verify the token and get tenant flags
        try:
            tenant_flags = self._get_tenant_flags(raw_token)
            if not tenant_flags:
                return JsonResponse(
                    {"detail": "Invalid token"}, 
                    status=401
                )
            
            # Attach tenant flags to the request
            request.tenant_flags = tenant_flags
            
            # Check if tenant is system enabled
            if not tenant_flags["system_enabled"]:
                return JsonResponse(
                    {"detail": "Access disabled for this tenant"}, 
                    status=403
                )
            
            # Add tenant ID to response headers for traceability
            request.META['HTTP_X_TENANT_ID'] = tenant_flags["tenant_id"]
            
        except (InvalidTokenError, ExpiredSignatureError) as e:
            return JsonResponse(
                {"detail": str(e)}, 
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {"detail": "Token verification failed"}, 
                status=500
            )
        
        return None
    
    def process_response(self, request, response):
        """Add tenant ID to response headers"""
        if hasattr(request, 'tenant_flags'):
            response['X-Tenant-Id'] = request.tenant_flags["tenant_id"]
        return response


def has_feature(request, feature_name):
    """
    Check if the current tenant has access to a specific feature.
    
    Usage:
        if has_feature(request, "watchtower"):
            # Enable watchtower functionality
            pass
    """
    if not hasattr(request, 'tenant_flags'):
        return False
    
    return feature_name in request.tenant_flags.get("features", set())


def get_tenant_limit(request, limit_name, default=None):
    """
    Get a specific limit value for the current tenant.
    
    Usage:
        max_seats = get_tenant_limit(request, "seats", 10)
    """
    if not hasattr(request, 'tenant_flags'):
        return default
    
    return request.tenant_flags.get("limits", {}).get(limit_name, default)


def require_feature(feature_name):
    """
    Decorator to require a specific feature for a view.
    
    Usage:
        @require_feature("watchtower")
        def watchtower_view(request):
            # This view requires the watchtower feature
            pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not has_feature(request, feature_name):
                return JsonResponse(
                    {"detail": f"Feature '{feature_name}' not available"}, 
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_plan(plan_name):
    """
    Decorator to require a specific plan for a view.
    
    Usage:
        @require_plan("pro")
        def pro_feature_view(request):
            # This view requires the pro plan
            pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'tenant_flags'):
                return JsonResponse(
                    {"detail": "Tenant token required"}, 
                    status=401
                )
            
            tenant_plan = request.tenant_flags.get("plan")
            if tenant_plan != plan_name:
                return JsonResponse(
                    {"detail": f"Plan '{plan_name}' required"}, 
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
