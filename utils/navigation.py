"""
Navigation utility for handling sidebar and tab navigation.
"""
from typing import List, Dict, Optional


def get_active_section(request_path: str) -> str:
    """
    Determine the active section based on request path.
    
    Args:
        request_path: The current request path
        
    Returns:
        The active section name
    """
    path = request_path.strip('/')
    
    if not path:
        return 'dashboard'
    elif path.startswith('prompt'):
        return 'prompt'
    elif path.startswith('campaigns'):
        return 'campaigns'
    elif path.startswith('accounts'):
        return 'accounts'
    elif path.startswith('reports'):
        return 'reports'
    elif path.startswith('people'):
        return 'people'
    else:
        return 'dashboard'


def get_section_tabs(section: str, request_path: str) -> Optional[List[Dict]]:
    """
    Get the tab configuration for a given section.
    
    Args:
        section: The section name
        request_path: Current request path for determining active tab
        
    Returns:
        List of tab dictionaries or None if section has no tabs
    """
    tab_configs = {
        'prompt': [
            {'label': 'Prompts', 'href': '/prompt/', 'path_prefix': '/prompt/$'},
            {'label': 'Agent Playground', 'href': '/prompt/playground/', 'path_prefix': '/prompt/playground/'},
            {'label': 'Voices', 'href': '/prompt/voices/', 'path_prefix': '/prompt/voices/'},
        ],
        'campaigns': [
            {'label': 'All Campaigns', 'href': '/campaigns/', 'path_prefix': '/campaigns/$'},
            {'label': 'Create Campaign', 'href': '/campaigns/new/', 'path_prefix': '/campaigns/new/'},
            {'label': 'Queue Tracker', 'href': '/campaigns/queue/', 'path_prefix': '/campaigns/queue/'},
            {'label': 'Sessions', 'href': '/campaigns/sessions/', 'path_prefix': '/campaigns/sessions/'},
        ],
        'accounts': [
            {'label': 'Company Users', 'href': '/accounts/users/', 'path_prefix': '/accounts/users/'},
            {'label': 'Create User', 'href': '/accounts/users/new/', 'path_prefix': '/accounts/users/new/'},
            {'label': 'Teams', 'href': '/accounts/teams/', 'path_prefix': '/accounts/teams/'},
            {'label': 'Permissions', 'href': '/accounts/permissions/', 'path_prefix': '/accounts/permissions/'},
        ],
        'reports': [
            {'label': 'Overview', 'href': '/reports/', 'path_prefix': '/reports/$'},
            {'label': 'Exports', 'href': '/reports/exports/', 'path_prefix': '/reports/exports/'},
        ],
        'people': [
            {'label': 'Directory', 'href': '/people/', 'path_prefix': '/people/$'},
            {'label': 'Roles', 'href': '/people/roles/', 'path_prefix': '/people/roles/'},
        ],
    }
    
    if section not in tab_configs:
        return None
    
    tabs = tab_configs[section].copy()
    
    # Determine active tab based on request path
    for tab in tabs:
        path_prefix = tab['path_prefix']
        
        # Handle exact match patterns (marked with $)
        if path_prefix.endswith('$'):
            exact_path = path_prefix[:-1].rstrip('/')
            if request_path.rstrip('/') == exact_path:
                tab['active'] = True
            else:
                tab['active'] = False
        # Handle prefix patterns
        elif request_path.startswith(path_prefix):
            tab['active'] = True
        else:
            tab['active'] = False
    
    # If no tab is active, activate the first one (overview/main tab)
    if not any(tab.get('active') for tab in tabs):
        tabs[0]['active'] = True
    
    return tabs


def get_sidebar_items(request_path: str) -> List[Dict]:
    """
    Get the flat sidebar navigation items.
    
    Args:
        request_path: Current request path for determining active section
        
    Returns:
        List of sidebar item dictionaries
    """
    active_section = get_active_section(request_path)
    
    return [
        {
            'label': 'Dashboard',
            'href': '/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z"></path>
            </svg>''',
            'active': active_section == 'dashboard'
        },
        {
            'label': 'Prompts',
            'href': '/prompt/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
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
            'label': 'Company',
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
            'label': 'People',
            'href': '/people/',
            'icon': '''<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>''',
            'active': active_section == 'people'
        },
    ]
