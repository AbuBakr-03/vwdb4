from .decorators import is_root_user, can_manage_users


def user_permissions(request):
    """
    Context processor to make user permission information available in all templates.
    """
    if request.user.is_authenticated:
        return {
            'is_root_user': is_root_user(request.user),
            'can_manage_users': can_manage_users(request.user),
        }
    return {
        'is_root_user': False,
        'can_manage_users': False,
    }






