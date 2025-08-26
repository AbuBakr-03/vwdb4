from django.urls import path
from . import views

app_name = 'authorization'

urlpatterns = [
    # Health check (no tenant context required)
    path('health/', views.health_check, name='health_check'),
    
    # Token Management Endpoints
    path('get-token/', views.get_token, name='get_token'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('token-status/', views.token_status, name='token_status'),
    
    # Feature-protected views
    path('watchtower/', views.watchtower_dashboard, name='watchtower_dashboard'),
    path('analytics/pro/', views.pro_analytics, name='pro_analytics'),
    path('ivr/enterprise/', views.enterprise_ivr, name='enterprise_ivr'),
    
    # Tenant context views
    path('status/', views.tenant_status, name='tenant_status'),
    path('usage/update/', views.update_tenant_usage, name='update_tenant_usage'),
    
    # Class-based view
    path('api/', views.TenantAPIView.as_view(), name='tenant_api'),
]
