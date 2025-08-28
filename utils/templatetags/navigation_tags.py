"""
Template tags for navigation utilities.
"""
from django import template
from utils.navigation import get_active_section, get_section_tabs, get_sidebar_items

register = template.Library()


@register.simple_tag
def get_navigation_context(request):
    """
    Get complete navigation context for the current request.
    
    Returns:
        Dictionary with sidebar_items, active_section, and section_tabs
    """
    request_path = request.path
    active_section = get_active_section(request_path)
    
    return {
        'sidebar_items': get_sidebar_items(request_path),
        'active_section': active_section,
        'section_tabs': get_section_tabs(active_section, request_path)
    }


@register.simple_tag
def get_sidebar_navigation(request):
    """Get sidebar navigation items."""
    return get_sidebar_items(request.path)


@register.simple_tag
def get_tabs_for_section(request, section=None):
    """
    Get tabs for a specific section or auto-detect from request.
    
    Args:
        request: Django request object
        section: Optional section name, auto-detected if not provided
        
    Returns:
        List of tab dictionaries or None
    """
    if section is None:
        section = get_active_section(request.path)
    
    return get_section_tabs(section, request.path)


@register.simple_tag
def is_section_active(request, section_name):
    """Check if a section is currently active."""
    return get_active_section(request.path) == section_name
