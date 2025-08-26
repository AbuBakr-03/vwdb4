# Authorization Module

This module provides tenant-based authorization and authentication for Django applications using JWT tokens from a tenant management system.

## Overview

The authorization module acts as a **consumer** of tenant management tokens. It verifies JWT tokens issued by your tenant management system and provides:

- **Tenant Context**: Automatic tenant identification and validation
- **Feature Flags**: Per-tenant feature access control
- **Plan Management**: Subscription-based access tiers
- **Usage Limits**: Resource usage tracking and enforcement
- **Audit Logging**: Complete action tracking for compliance

## Quick Start

### 1. Install Dependencies

```bash
pip install -r authorization/requirements.txt
```

### 2. Add to Django Settings

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'authorization',
]

MIDDLEWARE = [
    # ... other middleware
    'authorization.consumer_middleware.TenantFlagsMiddleware',
]

# Tenant Management Configuration
TENANT_MGMT_JWKS_URL = "https://your-tenant-mgmt.com/.well-known/jwks.json"
TENANT_AUDIENCE = "your-app-name"  # Must match what tenant mgmt system expects
TENANT_CACHE_SECONDS = 30  # Cache TTL for tenant flags
TENANT_SKIP_PATHS = [
    '/admin/',
    '/static/',
    '/health/',
    '/authorization/health/',
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations authorization
python manage.py migrate
```

### 4. Test the Setup

```bash
# Test health endpoint (no auth required)
curl http://localhost:8000/authorization/health/

# Test protected endpoint (auth required)
curl -H "Authorization: Bearer YOUR_TENANT_TOKEN" \
     http://localhost:8000/authorization/status/
```

## How It Works

### 1. Token Verification Flow

```
Client Request → Middleware → JWT Verification → Tenant Flags → Request Processing
     ↓              ↓            ↓              ↓              ↓
Bearer Token → JWKS Lookup → Token Decode → Feature Check → View Execution
```

### 2. Tenant Token Structure

Your tenant management system should issue tokens with this structure:

```json
{
  "iss": "https://tenant-mgmt.yourdomain.com",
  "aud": "your-app-name",
  "sub": "tenant:tenant-id",
  "tid": "tenant-id",
  "plan": "pro",
  "features": ["watchtower", "analytics", "api"],
  "system_enabled": true,
  "limits": {
    "seats": 25,
    "concurrency": 50,
    "api_calls": 1000
  },
  "jti": "unique-token-id",
  "iat": 1730000000,
  "exp": 1730000600,
  "kid": "key-2025-08"
}
```

## Usage Examples

### Basic Feature Protection

```python
from authorization.consumer_middleware import require_feature

@require_feature("watchtower")
def watchtower_view(request):
    """This view requires the 'watchtower' feature."""
    tenant_id = request.tenant_flags["tenant_id"]
    return JsonResponse({"message": f"Welcome to Watchtower, {tenant_id}!"})
```

### Plan-Based Access Control

```python
from authorization.consumer_middleware import require_plan

@require_plan("enterprise")
def enterprise_feature(request):
    """This view requires the 'enterprise' plan."""
    return JsonResponse({"message": "Enterprise feature accessed"})
```

### Combined Requirements

```python
@require_feature("ivr")
@require_plan("pro")
def pro_ivr_view(request):
    """Requires both 'ivr' feature and 'pro' plan."""
    return JsonResponse({"message": "Pro IVR feature"})
```

### Manual Feature Checks

```python
from authorization.consumer_middleware import has_feature

def flexible_view(request):
    if has_feature(request, "analytics"):
        # Enable analytics features
        return JsonResponse({"analytics": "enabled"})
    else:
        # Basic view without analytics
        return JsonResponse({"analytics": "disabled"})
```

### Usage Limit Checking

```python
from authorization.utils import check_tenant_limit, increment_tenant_usage

def api_endpoint(request):
    # Check if within limits
    limit_check = check_tenant_limit(request, 'api_calls')
    
    if not limit_check['within_limit']:
        return JsonResponse({
            'error': 'API call limit exceeded',
            'limit_info': limit_check
        }, status=429)
    
    # Increment usage
    increment_tenant_usage(request, 'api_calls', 1)
    
    # Process the request
    return JsonResponse({"message": "API call processed"})
```

### Getting Tenant Information

```python
from authorization.utils import get_tenant_info

def tenant_dashboard(request):
    tenant_info = get_tenant_info(request)
    
    return JsonResponse({
        'tenant_id': tenant_info['tenant_id'],
        'plan': tenant_info['plan'],
        'features': tenant_info['features'],
        'limits': tenant_info['limits']
    })
```

## API Endpoints

### Health Check
```
GET /authorization/health/
```
Returns service status (no authentication required).

### Watchtower Dashboard
```
GET /authorization/watchtower/
```
Requires `watchtower` feature.

### Pro Analytics
```
GET /authorization/analytics/pro/
```
Requires `pro` plan.

### Enterprise IVR
```
GET /authorization/ivr/enterprise/
```
Requires both `ivr` feature and `enterprise` plan.

### Tenant Status
```
GET /authorization/status/
```
Returns tenant information and limits (requires tenant context).

### Usage Update
```
POST /authorization/usage/update/
```
Updates tenant usage counters (requires tenant context).

### Tenant API
```
GET/POST /authorization/api/
```
Class-based view with different requirements per method.

## Decorators Reference

### `@require_feature(feature_name)`
Ensures the tenant has access to a specific feature.

### `@require_plan(plan_name)`
Ensures the tenant has a specific subscription plan.

### `@require_tenant_context`
Ensures the request has tenant context (basic authentication).

## Utility Functions

### `has_feature(request, feature_name)`
Check if tenant has access to a specific feature.

### `get_tenant_limit(request, limit_name, default=None)`
Get a specific limit value for the current tenant.

### `get_tenant_info(request)`
Get comprehensive tenant information.

### `check_tenant_limit(request, limit_name, current_usage=None)`
Check if tenant is within their limits.

### `increment_tenant_usage(request, limit_name, amount=1, ttl=300)`
Increment tenant usage for a specific limit.

### `tenant_audit_log(request, action, resource=None, details=None)`
Log tenant actions for audit purposes.

## Models

### TenantSession
Tracks active tenant sessions and usage.

### TenantAuditLog
Logs all tenant actions for compliance.

### TenantFeatureUsage
Tracks feature usage for billing and analytics.

### TenantLimit
Stores tenant-specific limits and current usage.

## Configuration Options

### Required Settings

```python
# URL to your tenant management system's JWKS endpoint
TENANT_MGMT_JWKS_URL = "https://tenant-mgmt.yourdomain.com/.well-known/jwks.json"

# Audience value that your app expects in tokens
TENANT_AUDIENCE = "your-app-name"
```

### Optional Settings

```python
# Cache TTL for tenant flags (default: 30 seconds)
TENANT_CACHE_SECONDS = 30

# Paths to skip token verification
TENANT_SKIP_PATHS = [
    '/admin/',
    '/static/',
    '/health/',
    '/public/',
]

# Redis configuration (optional)
REDIS_URL = "redis://localhost:6379/1"
```

## Error Handling

The middleware automatically handles common errors:

- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Feature not available or plan insufficient
- **429 Too Many Requests**: Usage limits exceeded
- **500 Internal Server Error**: Token verification failure

## Caching

Tenant flags are cached to improve performance:

- **Default TTL**: 30 seconds
- **Negative caching**: 5 seconds for invalid tokens
- **Cache key**: Based on token tail for security

## Security Features

- **JWT Verification**: RS256 algorithm with JWKS
- **Audience Validation**: Ensures tokens are for your app
- **Expiration Checking**: Automatic token expiry validation
- **Audit Logging**: Complete action tracking
- **Rate Limiting**: Per-tenant usage enforcement

## Testing

### Test with Sample Token

```bash
# Get a token from your tenant management system
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/authorization/status/
```

### Test Feature Requirements

```bash
# Test feature-protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/authorization/watchtower/

# Test plan-protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/authorization/analytics/pro/
```

## Troubleshooting

### Common Issues

1. **JWKS Client Initialization Failed**
   - Check `TENANT_MGMT_JWKS_URL` is accessible
   - Verify the URL returns valid JWKS

2. **Token Verification Failed**
   - Ensure `TENANT_AUDIENCE` matches token audience
   - Check token expiration
   - Verify token signature

3. **Feature Not Available**
   - Check if tenant has the required feature
   - Verify tenant plan includes the feature

4. **Cache Issues**
   - Check Redis connection (if using Redis)
   - Verify cache configuration

### Debug Mode

Enable debug logging in Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'authorization': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Deployment

### Environment Variables

```bash
# Required
export TENANT_MGMT_JWKS_URL="https://tenant-mgmt.yourdomain.com/.well-known/jwks.json"
export TENANT_AUDIENCE="your-app-name"

# Optional
export TENANT_CACHE_SECONDS=60
export REDIS_URL="redis://redis:6379/1"
```

### Web Server Configuration

```nginx
# Nginx example
location /authorization/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Integration with Other Apps

### Using in Views

```python
# In any Django app
from authorization.consumer_middleware import has_feature, require_feature

@require_feature("analytics")
def my_analytics_view(request):
    # This view requires analytics feature
    pass
```

### Using in Templates

```python
# In views
def my_view(request):
    context = {
        'has_analytics': has_feature(request, 'analytics'),
        'tenant_plan': request.tenant_flags.get('plan', 'basic')
    }
    return render(request, 'my_template.html', context)

# In templates
{% if has_analytics %}
    <div class="analytics-widget">...</div>
{% endif %}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This module is part of your Django application and follows the same license terms.
