# Data Table Component - Quick Usage Guide

## Quick Start

### 1. Include the Component

```django
{% load data_table_tags %}
{% include 'components/data_table.html' with
    table_data=your_data
    columns=your_columns
%}
```

### 2. Basic View Implementation

```python
from django.views.generic import ListView
from utils.data_table_mixin import DataTableListView

class MyDataTableView(DataTableListView):
    model = YourModel
    template_name = 'your_template.html'

    # Search fields
    search_fields = ['name', 'email']

    # Column configuration
    columns = [
        {'name': 'Name', 'key': 'name', 'sortable': True, 'searchable': True},
        {'name': 'Email', 'key': 'email', 'sortable': True, 'searchable': True},
        {'name': 'Status', 'key': 'status', 'sortable': True, 'searchable': False},
    ]

    # Optional: Filters
    filters = {
        'status': {
            'title': 'Status',
            'options': [
                {'value': 'active', 'label': 'Active'},
                {'value': 'inactive', 'label': 'Inactive'},
            ]
        }
    }

    # Optional: Stats
    stats = {
        'total': {
            'title': 'Total Items',
            'value': lambda: YourModel.objects.count(),
            'description': 'All items',
            'color': 'primary'
        }
    }
```

### 3. Template Setup

```django
{% extends 'base.html' %}
{% load data_table_tags %}

{% block content %}
{% include 'components/data_table.html' with
    title="My Data"
    table_data=your_data
    columns=columns
    filters=filters
    stats=stats
    page_obj=page_obj
    paginator=paginator
    current_sort=current_sort
    current_order=current_order
    active_filters=active_filters
    visible_columns=visible_columns
    search_query=search_query
    per_page=per_page
    create_url=create_url
%}
{% endblock %}
```

## Key Features

### Search

- Global search across specified fields
- Configurable search fields and lookup types

### Filtering

- Multi-select filters with searchable options
- Custom filter logic support
- Active filter display with remove options

### Sorting

- Click column headers to sort
- Ascending/descending toggle
- Visual sort indicators

### Column Visibility

- Show/hide columns
- Searchable column selector
- Persistent column preferences

### Pagination

- Full pagination controls
- Items per page selector
- Page number display

### Stats Cards

- Optional statistics display
- Configurable colors and descriptions
- Dynamic value calculation

## Configuration Options

### Required

- `table_data`: Your data list
- `columns`: Column definitions

### Optional

- `title`, `subtitle`: Page headers
- `filters`: Filter configurations
- `stats`: Statistics cards
- `create_url`: Create button URL
- `empty_message`: Empty state message

## Custom Column Templates

Create custom templates for complex column rendering:

```django
<!-- templates/components/columns/status_badge.html -->
{% if item.status == 'active' %}
    <div class="badge badge-success">Active</div>
{% else %}
    <div class="badge badge-error">Inactive</div>
{% endif %}
```

Reference in column config:

```python
{
    'name': 'Status',
    'key': 'status',
    'template': 'components/columns/status_badge.html'
}
```

## Custom Filters

Override filter methods in your view:

```python
def apply_status_filter(self, queryset, filter_values, filter_config):
    if 'active' in filter_values:
        queryset = queryset.filter(status='active')
    if 'inactive' in filter_values:
        queryset = queryset.filter(status='inactive')
    return queryset
```

## Dependencies

- Django
- DaisyUI
- Tailwind CSS
- Custom template tags (`data_table_tags`)

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive
- Progressive enhancement
