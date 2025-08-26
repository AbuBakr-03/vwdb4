from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import JsonResponse


def require_root_user(view_func):
    """
    Decorator to require root user access.
    Only root users can access views decorated with this.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Check if user is root user
        if hasattr(request.user, 'company_user') and request.user.company_user.is_root_user:
            return view_func(request, *args, **kwargs)
        else:
            # Show access denied page instead of redirecting
            from .views import access_denied_view
            return access_denied_view(request, 'Root user privileges required to access this page.')
    
    return wrapper


def require_root_user_api(view_func):
    """
    API decorator to require root user access.
    Returns JSON response for API views.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check if user is root user
        if hasattr(request.user, 'company_user') and request.user.company_user.is_root_user:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'Root user privileges required'}, status=403)
    
    return wrapper


def can_manage_users(user):
    """
    Utility function to check if user can manage other users.
    Currently only root users can manage users.
    """
    return hasattr(user, 'company_user') and user.company_user.is_root_user


def is_root_user(user):
    """
    Utility function to check if user is a root user.
    """
    return hasattr(user, 'company_user') and user.company_user.is_root_user


def get_company_users(user):
    """
    Utility function to get all users in the same company.
    """
    if not hasattr(user, 'company_user'):
        return []
    
    from .models import CompanyUser
    return CompanyUser.objects.filter(
        company_tenant_id=user.company_user.company_tenant_id
    ).select_related('user')
