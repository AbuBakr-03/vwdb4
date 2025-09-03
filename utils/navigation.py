from django.urls import reverse

def get_active_section(request):
    """
    Determine the active section based on the request path.
    """
    if not request:
        return None
    
    # Get the path without leading/trailing slashes
    path = request.path.strip('/')
    
    if not path:
        return 'dashboard'
    elif path == 'dashboard' or path.startswith('dashboard/'):
        return 'dashboard'
    elif path == 'assistants' or path.startswith('assistants/'):
        return 'assistants'
    elif path == 'phone-numbers' or path.startswith('phone-numbers/'):
        return 'phone_numbers'
    elif path == 'voice-library' or path.startswith('voice-library/'):
        return 'voice_library'
    elif path.startswith('prompt/'):
        return 'prompt'
    elif path.startswith('campaigns/'):
        return 'campaigns'
    elif path.startswith('accounts/'):
        return 'accounts'
    elif path.startswith('reports/'):
        return 'reports'
    elif path.startswith('people/'):
        return 'people'
    elif path.startswith('tools/'):
        return 'tools'
    elif path == 'api-keys' or path.startswith('api-keys/'):
        return 'api_keys'
    
    return None

def get_section_tabs(section):
    """
    Get the tabs for a specific section.
    """
    tabs_config = {
        'prompt': [
            {'label': 'Prompts', 'href': '/prompt/', 'name': 'prompts'},
            {'label': 'Agent Playground', 'href': '/prompt/playground/', 'name': 'playground'},
            {'label': 'Voices', 'href': '/prompt/voices/', 'name': 'voices'},
        ],
        'campaigns': [
            {'label': 'All Campaigns', 'href': '/campaigns/', 'name': 'list'},
            {'label': 'Create Campaign', 'href': '/campaigns/new/', 'name': 'create'},
            {'label': 'Queue Tracker', 'href': '/campaigns/queue/', 'name': 'queue'},
            {'label': 'Sessions', 'href': '/campaigns/sessions/', 'name': 'sessions'},
        ],
        'accounts': [
            {'label': 'Company Users', 'href': '/accounts/users/', 'name': 'users'},
            {'label': 'Create User', 'href': '/accounts/users/new/', 'name': 'create_user'},
            {'label': 'Teams', 'href': '/accounts/teams/', 'name': 'teams'},
            {'label': 'Permissions', 'href': '/accounts/permissions/', 'name': 'permissions'},
        ],
        'reports': [
            {'label': 'Overview', 'href': '/reports/', 'name': 'overview'},
            {'label': 'Exports', 'href': '/reports/exports/', 'name': 'exports'},
        ],
        'people': [
            {'label': 'Directory', 'href': '/people/', 'name': 'directory'},
            {'label': 'Roles', 'href': '/people/roles/', 'name': 'roles'},
        ],
    }
    
    return tabs_config.get(section, [])

def get_tabs_for_section(request):
    """
    Get tabs for the current section based on request.
    """
    active_section = get_active_section(request)
    if not active_section:
        return []
    
    tabs = get_section_tabs(active_section)
    
    # Mark the active tab
    current_path = request.path
    for tab in tabs:
        tab['active'] = current_path == tab['href'] or (
            tab['href'] != '/' and current_path.startswith(tab['href'])
        )
    
    return tabs

def get_sidebar_items(request):
    """
    Get the sidebar navigation items with active states.
    """
    active_section = get_active_section(request)
    
    return [
        {
            'label': 'Dashboard',
            'href': '/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5zM8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5z"></path>
            </svg>''',
            'active': active_section == 'dashboard'
        },
        {
            'label': 'Assistants',
            'href': '/assistants/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>''',
            'active': active_section == 'assistants'
        },
        {
            'label': 'Phone Numbers',
            'href': '/phone-numbers/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
            </svg>''',
            'active': active_section == 'phone_numbers'
        },
        {
            'label': 'Prompt Management',
            'href': '/prompt/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>''',
            'active': active_section == 'prompt'
        },
        {
            'label': 'Campaigns',
            'href': '/campaigns/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
            </svg>''',
            'active': active_section == 'campaigns'
        },
        {
            'label': 'People',
            'href': '/people/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>''',
            'active': active_section == 'people'
        },
        {
            'label': 'Company Users',
            'href': '/accounts/users/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
            </svg>''',
            'active': active_section == 'accounts'
        },
        {
            'label': 'Reports',
            'href': '/reports/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>''',
            'active': active_section == 'reports'
        },
        {
            'label': 'Tools',
            'href': '/tools/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>''',
            'active': active_section == 'tools'
        },
        {
            'label': 'Voice Library',
            'href': '/voice-library/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
            </svg>''',
            'active': active_section == 'voice_library'
        },
        {
            'label': 'API Keys',
            'href': '/api-keys/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v-2H7v-2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M18 10h.01"></path>
            </svg>''',
            'active': active_section == 'api_keys'
        },

    ]