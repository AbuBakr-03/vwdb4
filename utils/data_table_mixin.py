from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.functional import cached_property


class DataTableMixin:
    """
    Mixin to provide common data table functionality for Django views.
    
    This mixin handles:
    - Search functionality
    - Filtering
    - Sorting
    - Pagination
    - Column visibility
    """
    
    # Override these in your view
    model = None
    template_name = None
    context_object_name = 'table_data'
    
    # Search configuration
    search_fields = []
    search_lookup = 'icontains'
    
    # Default sorting
    default_sort = 'id'
    default_order = 'asc'
    
    # Pagination
    default_per_page = 25
    per_page_options = [10, 25, 50, 100]
    
    # Column configuration
    columns = []
    
    # Filter configuration
    filters = {}
    
    # Stats configuration
    stats = {}
    
    # Create button configuration
    create_url = None
    create_text = "Create New"
    
    # Empty state configuration
    empty_message = "No data found"
    empty_action_url = None
    empty_action_text = "Create First Item"
    
    def get_queryset(self):
        """Get the base queryset for the data table."""
        if self.model:
            return self.model.objects.all()
        return super().get_queryset()
    
    def get_search_fields(self):
        """Get the fields to search in."""
        return self.search_fields
    
    def get_search_lookup(self):
        """Get the lookup type for search (e.g., 'icontains', 'exact')."""
        return self.search_lookup
    
    def get_columns(self):
        """Get the column configuration."""
        return self.columns
    
    def get_filters(self):
        """Get the filter configuration."""
        return self.filters
    
    def get_stats(self):
        """Get the stats configuration."""
        return self.stats
    
    def apply_search(self, queryset, search_query):
        """Apply search to the queryset."""
        if not search_query or not self.get_search_fields():
            return queryset
        
        search_fields = self.get_search_fields()
        lookup = self.get_search_lookup()
        
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__{lookup}": search_query})
        
        return queryset.filter(q_objects)
    
    def apply_filters(self, queryset, active_filters):
        """Apply filters to the queryset."""
        if not active_filters:
            return queryset
        
        for filter_name, filter_values in active_filters.items():
            if filter_name in self.get_filters():
                filter_config = self.get_filters()[filter_name]
                queryset = self._apply_filter(queryset, filter_name, filter_values, filter_config)
        
        return queryset
    
    def _apply_filter(self, queryset, filter_name, filter_values, filter_config):
        """Apply a specific filter to the queryset."""
        # This is a basic implementation - override in subclasses for custom filter logic
        if hasattr(self, f'apply_{filter_name}_filter'):
            return getattr(self, f'apply_{filter_name}_filter')(queryset, filter_values, filter_config)
        
        # Default behavior: assume filter_values are field values to filter by
        if filter_values:
            q_objects = Q()
            for value in filter_values:
                q_objects |= Q(**{filter_name: value})
            queryset = queryset.filter(q_objects)
        
        return queryset
    
    def apply_sorting(self, queryset, sort_field, sort_order):
        """Apply sorting to the queryset."""
        if not sort_field:
            sort_field = self.default_sort
        
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        
        return queryset.order_by(sort_field)
    
    def get_paginator(self, queryset, per_page):
        """Get paginator for the queryset."""
        return Paginator(queryset, per_page)
    
    def get_context_data(self, **kwargs):
        """Get context data for the template."""
        context = super().get_context_data(**kwargs)
        
        # Get query parameters
        search_query = self.request.GET.get('search', '')
        sort_field = self.request.GET.get('sort', self.default_sort)
        sort_order = self.request.GET.get('order', self.default_order)
        page_number = self.request.GET.get('page', 1)
        per_page = int(self.request.GET.get('per_page', self.default_per_page))
        
        # Get visible columns
        visible_columns = self.request.GET.getlist('columns')
        
        # Get active filters
        active_filters = {}
        for filter_name in self.get_filters().keys():
            values = self.request.GET.getlist(filter_name)
            if values:
                active_filters[filter_name] = values
        
        # Build queryset
        queryset = self.get_queryset()
        
        # Apply search
        queryset = self.apply_search(queryset, search_query)
        
        # Apply filters
        queryset = self.apply_filters(queryset, active_filters)
        
        # Apply sorting
        queryset = self.apply_sorting(queryset, sort_field, sort_order)
        
        # Pagination
        paginator = self.get_paginator(queryset, per_page)
        page_obj = paginator.get_page(page_number)
        
        # Add data table context
        context.update({
            'table_data': page_obj,
            'page_obj': page_obj,
            'paginator': paginator,
            'current_sort': sort_field,
            'current_order': sort_order,
            'active_filters': active_filters,
            'visible_columns': visible_columns,
            'per_page': per_page,
            'search_query': search_query,
            
            # Configuration
            'columns': self.get_columns(),
            'filters': self.get_filters(),
            'stats': self.get_stats(),
            
            # UI configuration
            'create_url': self.create_url,
            'create_text': self.create_text,
            'empty_message': self.empty_message,
            'empty_action_url': self.empty_action_url,
            'empty_action_text': self.empty_action_text,
        })
        
        return context


class DataTableListView(DataTableMixin):
    """
    A ListView that includes data table functionality.
    
    Example usage:
    
    class CompanyUsersView(DataTableListView):
        model = CompanyUser
        template_name = 'accounts/company_users.html'
        context_object_name = 'company_users'
        
        # Search configuration
        search_fields = ['user__username', 'user__email']
        
        # Column configuration
        columns = [
            {
                'name': 'User',
                'key': 'username',
                'sortable': True,
                'searchable': True,
                'template': 'components/columns/user_avatar.html',
            },
            {
                'name': 'Email',
                'key': 'user__email',
                'sortable': True,
                'searchable': True,
            },
            {
                'name': 'Role',
                'key': 'is_root_user',
                'sortable': True,
                'searchable': False,
                'template': 'components/columns/role_badge.html',
            },
        ]
        
        # Filter configuration
        filters = {
            'role': {
                'title': 'User Role',
                'options': [
                    {'value': 'root', 'label': 'Root Users'},
                    {'value': 'sub', 'label': 'Sub Users'},
                ]
            },
        }
        
        # Stats configuration
        stats = {
            'total_users': {
                'title': 'Total Users',
                'value': lambda: CompanyUser.objects.count(),
                'description': 'All company users',
                'color': 'primary'
            },
        }
        
        def apply_role_filter(self, queryset, filter_values, filter_config):
            if 'root' in filter_values:
                queryset = queryset.filter(is_root_user=True)
            if 'sub' in filter_values:
                queryset = queryset.filter(is_root_user=False)
            return queryset
    """
    
    def get_stats(self):
        """Get stats with dynamic values."""
        stats = super().get_stats()
        
        # Evaluate callable values
        for key, stat in stats.items():
            if callable(stat.get('value')):
                stat['value'] = stat['value']()
        
        return stats
