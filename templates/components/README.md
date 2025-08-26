# Data Table Component

A comprehensive, reusable data table component with advanced features including searching, filtering, sorting, column visibility, and pagination.

## Features

- **Search**: Global search across all searchable columns
- **Filtering**: Multi-select filters with searchable filter options
- **Sorting**: Click column headers to sort (ascending/descending)
- **Column Visibility**: Show/hide columns with searchable column selector
- **Pagination**: Full pagination with items per page selector
- **Stats Cards**: Optional statistics display
- **Responsive**: Mobile-friendly design
- **Customizable**: Highly configurable through context variables

## Usage

### Basic Usage

```django
{% load data_table_tags %}
{% include 'components/data_table.html' with
    table_data=your_data
    columns=your_columns
%}
```

### Full Example

```django
{% load data_table_tags %}
{% include 'components/data_table.html' with
    title="Your Table Title"
    subtitle="Optional subtitle"
    table_data=your_data
    columns=your_columns
    filters=your_filters
    stats=your_stats
    page_obj=page_obj
    paginator=paginator
    current_sort=current_sort
    current_order=current_order
    active_filters=active_filters
    visible_columns=visible_columns
    search_query=request.GET.search
    per_page=per_page
    create_url=create_url
    create_text="Create New Item"
    empty_message="No data found"
    empty_action_url=create_url
    empty_action_text="Create First Item"
%}
```

## Context Variables

### Required Variables

- `table_data`: List of objects to display
- `columns`: List of column definitions

### Optional Variables

- `title`: Table title (string)
- `subtitle`: Table subtitle (string)
- `filters`: Dictionary of available filters
- `stats`: Dictionary of statistics to display
- `page_obj`: Paginator page object
- `paginator`: Paginator object
- `current_sort`: Current sort field (string)
- `current_order`: Current sort order ('asc' or 'desc')
- `active_filters`: Dictionary of active filters
- `visible_columns`: List of visible column keys
- `search_query`: Current search term (string)
- `per_page`: Items per page (integer)
- `create_url`: URL for create button
- `create_text`: Text for create button
- `empty_message`: Message when no data
- `empty_action_url`: URL for empty state action
- `empty_action_text`: Text for empty state action

## Column Configuration

Each column in the `columns` list should be a dictionary with the following structure:

```python
columns = [
    {
        'name': 'Username',           # Display name
        'key': 'username',           # Data key/attribute
        'sortable': True,            # Whether column is sortable
        'searchable': True,          # Whether column is searchable
        'template': None,            # Optional custom template for rendering
    },
    {
        'name': 'Email',
        'key': 'email',
        'sortable': True,
        'searchable': True,
    },
    {
        'name': 'Role',
        'key': 'role',
        'sortable': True,
        'searchable': False,
    },
    {
        'name': 'Created Date',
        'key': 'created_at',
        'sortable': True,
        'searchable': False,
    },
]
```

## Filter Configuration

The `filters` dictionary should have the following structure:

```python
filters = {
    'role': {
        'title': 'User Role',
        'options': [
            {'value': 'root', 'label': 'Root Users', 'search_text': 'root users admin administrator'},
            {'value': 'sub', 'label': 'Sub Users', 'search_text': 'sub users regular standard'},
        ]
    },
    'created_by': {
        'title': 'Created By',
        'options': [
            {'value': 'system', 'label': 'System', 'search_text': 'system automatic auto'},
            # Dynamic options would be populated from backend
        ]
    },
    'date_filter': {
        'title': 'Created Date',
        'options': [
            {'value': 'today', 'label': 'Today', 'search_text': 'today recent current'},
            {'value': 'week', 'label': 'This Week', 'search_text': 'this week recent current seven days'},
            {'value': 'month', 'label': 'This Month', 'search_text': 'this month recent current thirty days'},
        ]
    },
}
```

## Stats Configuration

The `stats` dictionary should have the following structure:

```python
stats = {
    'total_users': {
        'title': 'Total Users',
        'value': total_users,
        'description': 'All company users',
        'color': 'primary'  # Optional: primary, success, info, warning, error
    },
    'root_users': {
        'title': 'Root Users',
        'value': root_users,
        'description': 'Administrators',
        'color': 'success'
    },
    'sub_users': {
        'title': 'Sub Users',
        'value': sub_users,
        'description': 'Regular users',
        'color': 'info'
    },
}
```

## Custom Column Templates

You can create custom templates for rendering specific columns:

```django
<!-- templates/components/columns/user_avatar.html -->
<div class="flex items-center space-x-3">
    <div class="avatar placeholder">
        <div class="bg-primary text-primary-content rounded-full w-8">
            <span class="text-sm">
                {{ item.user.username|first|upper }}
            </span>
        </div>
    </div>
    <div>
        <div class="font-bold">
            {{ item.user.username }}
        </div>
    </div>
</div>
```

Then reference it in your column configuration:

```python
columns = [
    {
        'name': 'User',
        'key': 'username',
        'sortable': True,
        'searchable': True,
        'template': 'components/columns/user_avatar.html',
    },
    # ... other columns
]
```

## Backend Integration

### View Example

```python
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

def company_users_view(request):
    # Get query parameters
    search_query = request.GET.get('search', '')
    sort_field = request.GET.get('sort', 'username')
    sort_order = request.GET.get('order', 'asc')
    page_number = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 25))

    # Get visible columns
    visible_columns = request.GET.getlist('columns')

    # Get active filters
    active_filters = {}
    for filter_name in ['role', 'created_by', 'date_filter']:
        values = request.GET.getlist(filter_name)
        if values:
            active_filters[filter_name] = values

    # Build queryset
    queryset = CompanyUser.objects.all()

    # Apply search
    if search_query:
        queryset = queryset.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Apply filters
    if 'role' in active_filters:
        if 'root' in active_filters['role']:
            queryset = queryset.filter(is_root_user=True)
        if 'sub' in active_filters['role']:
            queryset = queryset.filter(is_root_user=False)

    # Apply sorting
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'
    queryset = queryset.order_by(sort_field)

    # Pagination
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)

    # Prepare context
    context = {
        'company_users': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'current_sort': request.GET.get('sort', 'username'),
        'current_order': request.GET.get('order', 'asc'),
        'active_filters': active_filters,
        'visible_columns': visible_columns,
        'per_page': per_page,
        'create_url': reverse('accounts:create_sub_user'),

        # Column configuration
        'columns': [
            {
                'name': 'User',
                'key': 'username',
                'sortable': True,
                'searchable': True,
                'template': 'components/columns/user_avatar.html',
            },
            {
                'name': 'Email',
                'key': 'email',
                'sortable': True,
                'searchable': True,
            },
            {
                'name': 'Role',
                'key': 'role',
                'sortable': True,
                'searchable': False,
            },
            {
                'name': 'Created Date',
                'key': 'created_at',
                'sortable': True,
                'searchable': False,
            },
            {
                'name': 'Created By',
                'key': 'created_by',
                'sortable': True,
                'searchable': False,
            },
        ],

        # Filter configuration
        'filters': {
            'role': {
                'title': 'User Role',
                'options': [
                    {'value': 'root', 'label': 'Root Users', 'search_text': 'root users admin administrator'},
                    {'value': 'sub', 'label': 'Sub Users', 'search_text': 'sub users regular standard'},
                ]
            },
            'created_by': {
                'title': 'Created By',
                'options': [
                    {'value': 'system', 'label': 'System', 'search_text': 'system automatic auto'},
                ] + [{'value': str(user.id), 'label': user.username, 'search_text': user.username}
                     for user in User.objects.filter(companyuser__isnull=False).distinct()]
            },
            'date_filter': {
                'title': 'Created Date',
                'options': [
                    {'value': 'today', 'label': 'Today', 'search_text': 'today recent current'},
                    {'value': 'week', 'label': 'This Week', 'search_text': 'this week recent current seven days'},
                    {'value': 'month', 'label': 'This Month', 'search_text': 'this month recent current thirty days'},
                ]
            },
        },

        # Stats configuration
        'stats': {
            'total_users': {
                'title': 'Total Users',
                'value': CompanyUser.objects.count(),
                'description': 'All company users',
                'color': 'primary'
            },
            'root_users': {
                'title': 'Root Users',
                'value': CompanyUser.objects.filter(is_root_user=True).count(),
                'description': 'Administrators',
                'color': 'success'
            },
            'sub_users': {
                'title': 'Sub Users',
                'value': CompanyUser.objects.filter(is_root_user=False).count(),
                'description': 'Regular users',
                'color': 'info'
            },
        },
    }

    return render(request, 'accounts/company_users.html', context)
```

## Customization

### CSS Customization

The component uses DaisyUI classes and can be customized by overriding CSS variables or adding custom styles.

### JavaScript Customization

The component includes JavaScript for dropdown functionality. You can extend or modify the functions as needed.

### Template Customization

You can override specific parts of the component by creating your own version or extending the base template.

## Dependencies

- Django
- DaisyUI
- Tailwind CSS
- Custom template tags (`data_table_tags`)

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive
- Progressive enhancement (works without JavaScript for basic functionality)
