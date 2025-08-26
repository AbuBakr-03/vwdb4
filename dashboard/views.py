from django.shortcuts import render
from authorization.utils import get_tenant_info


def home(request):
    """Dashboard home view with tenant information."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    return render(request, "dashboard/index.html", context)
