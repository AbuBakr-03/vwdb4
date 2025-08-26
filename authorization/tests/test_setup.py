#!/usr/bin/env python
"""
Test script to verify the authorization module setup.
Run this script to check if everything is configured correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.test import RequestFactory
from authorization.consumer_middleware import TenantFlagsMiddleware, has_feature
from authorization.utils import get_tenant_info


def test_settings():
    """Test if tenant management settings are configured."""
    print("🔧 Testing Tenant Management Settings...")
    
    required_settings = [
        'TENANT_MGMT_JWKS_URL',
        'TENANT_AUDIENCE',
        'TENANT_CACHE_SECONDS',
        'TENANT_SKIP_PATHS'
    ]
    
    for setting in required_settings:
        value = getattr(settings, setting, None)
        if value is not None:
            print(f"✅ {setting}: {value}")
        else:
            print(f"❌ {setting}: Not configured")
    
    print()


def test_middleware():
    """Test if the middleware can be instantiated."""
    print("🔧 Testing Middleware...")
    
    try:
        # Create a mock get_response function
        def mock_get_response(request):
            return None
        
        middleware = TenantFlagsMiddleware(mock_get_response)
        print("✅ TenantFlagsMiddleware instantiated successfully")
        
        # Test JWK client initialization
        if middleware.jwk_client:
            print("✅ JWK client initialized")
        else:
            print("⚠️  JWK client not initialized (check TENANT_MGMT_JWKS_URL)")
            
    except Exception as e:
        print(f"❌ Middleware instantiation failed: {e}")
    
    print()


def test_models():
    """Test if authorization models are accessible."""
    print("🔧 Testing Models...")
    
    try:
        from authorization.models import TenantSession, TenantAuditLog, TenantFeatureUsage, TenantLimit
        print("✅ All authorization models imported successfully")
        
        # Test model creation (without saving)
        session = TenantSession(
            tenant_id="test-tenant",
            session_id="test-session-123"
        )
        print("✅ TenantSession model can be instantiated")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
    
    print()


def test_utils():
    """Test utility functions."""
    print("🔧 Testing Utility Functions...")
    
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/test/')
        
        # Test utility functions
        tenant_info = get_tenant_info(request)
        if tenant_info is None:
            print("✅ get_tenant_info returns None for request without tenant context")
        
        has_watchtower = has_feature(request, "watchtower")
        if not has_watchtower:
            print("✅ has_feature returns False for request without tenant context")
            
        print("✅ Utility functions working correctly")
        
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
    
    print()


def test_cache():
    """Test if Django cache is working."""
    print("🔧 Testing Cache...")
    
    try:
        # Test cache operations
        cache.set('test_key', 'test_value', 10)
        value = cache.get('test_key')
        
        if value == 'test_value':
            print("✅ Django cache is working")
        else:
            print("❌ Cache test failed")
            
        # Clean up
        cache.delete('test_key')
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
    
    print()


def test_urls():
    """Test if authorization URLs are accessible."""
    print("🔧 Testing URL Configuration...")
    
    try:
        from django.urls import reverse
        from django.urls.exceptions import NoReverseMatch
        
        # Test health endpoint
        try:
            health_url = reverse('authorization:health_check')
            print(f"✅ Health endpoint URL: {health_url}")
        except NoReverseMatch:
            print("❌ Health endpoint URL not found")
        
        # Test other endpoints
        endpoints = [
            'watchtower_dashboard',
            'pro_analytics',
            'tenant_status',
        ]
        
        for endpoint in endpoints:
            try:
                url = reverse(f'authorization:{endpoint}')
                print(f"✅ {endpoint} URL: {url}")
            except NoReverseMatch:
                print(f"❌ {endpoint} URL not found")
                
    except Exception as e:
        print(f"❌ URL test failed: {e}")
    
    print()


def main():
    """Run all tests."""
    print("🚀 Authorization Module Setup Test")
    print("=" * 50)
    print()
    
    test_settings()
    test_middleware()
    test_models()
    test_utils()
    test_cache()
    test_urls()
    
    print("🏁 Test completed!")
    print()
    print("Next steps:")
    print("1. Update TENANT_MGMT_JWKS_URL to point to your tenant management system")
    print("2. Update TENANT_AUDIENCE to match your app's expected audience")
    print("3. Run migrations: python manage.py makemigrations && python manage.py migrate")
    print("4. Test with a real tenant token from your tenant management system")


if __name__ == '__main__':
    main()
