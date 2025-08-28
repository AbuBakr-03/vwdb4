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

def dashboard_redirect(request):
    """Redirect old dashboard URLs to root."""
    return redirect('/', permanent=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("dashboard.urls")),  # Dashboard at root
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),  # Redirect old URLs
    path("authorization/", include("authorization.urls")),
    path("prompt/", include("prompt.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("accounts/", include("accounts.urls")),
    path("reports/", include("reports.urls")),
    path("tickets/", include("tickets.urls")),
    path("people/", include("people.urls")),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
