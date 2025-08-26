from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])

@register.filter
def get_attr(obj, attr):
    """Get an attribute from an object"""
    if obj is None:
        return ''
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif hasattr(obj, '__getitem__'):
        return obj.get(attr, '')
    return ''

@register.filter
def format_value(value, format_type=None):
    """Format a value based on type"""
    if value is None:
        return ''
    
    if format_type == 'date':
        try:
            return value.strftime('%M %d, %Y')
        except:
            return str(value)
    elif format_type == 'datetime':
        try:
            return value.strftime('%M %d, %Y %H:%M')
        except:
            return str(value)
    elif format_type == 'currency':
        try:
            return f"${value:,.2f}"
        except:
            return str(value)
    elif format_type == 'number':
        try:
            return f"{value:,}"
        except:
            return str(value)
    else:
        return str(value)
