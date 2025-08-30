"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def dashboard_redirect(request):
    """Redirect old dashboard URLs to root."""
    return redirect('/', permanent=True)

def health_check(request):
    """Health check endpoint for Docker and load balancers."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z',
        'service': 'watchtower-v2'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("dashboard.urls")),  # Dashboard at root
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),  # Redirect old URLs
    path("authorization/", include("authorization.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("accounts/", include("accounts.urls")),
    path("reports/", include("reports.urls")),
    path("people/", include("people.urls")),
    path("tools/", include("tools.urls")),
    path('health/', health_check, name='health_check'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
