from django.views.generic import ListView
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core.paginator import Paginator

from utils.data_table_mixin import DataTableListView
from .models import CompanyUser


class CompanyUsersDataTableView(DataTableListView):
    """
    Example view using the DataTableListView for company users.
    
    This demonstrates how to use the modular data table component
    with all its features: search, filtering, sorting, column visibility, and pagination.
    """
    
    model = CompanyUser
    template_name = 'accounts/company_users_example.html'
    context_object_name = 'company_users'
    
    # Search configuration
    search_fields = ['user__username', 'user__email']
    search_lookup = 'icontains'
    
    # Default sorting
    default_sort = 'user__username'
    default_order = 'asc'
    
    # Pagination
    default_per_page = 25
    
    # Create button configuration
    create_url = 'accounts:create_sub_user'
    create_text = "Create New User"
    
    # Empty state configuration
    empty_message = "No users found"
    empty_action_url = 'accounts:create_sub_user'
    empty_action_text = "Create First User"
    
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
    ]
    
    # Filter configuration
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
    
    # Stats configuration
    stats = {
        'total_users': {
            'title': 'Total Users',
            'value': lambda: CompanyUser.objects.count(),
            'description': 'All company users',
            'color': 'primary'
        },
        'root_users': {
            'title': 'Root Users',
            'value': lambda: CompanyUser.objects.filter(is_root_user=True).count(),
            'description': 'Administrators',
            'color': 'success'
        },
        'sub_users': {
            'title': 'Sub Users',
            'value': lambda: CompanyUser.objects.filter(is_root_user=False).count(),
            'description': 'Regular users',
            'color': 'info'
        },
    }
    
    def get_queryset(self):
        """Get the base queryset with related data."""
        return super().get_queryset().select_related('user', 'created_by')
    
    def get_filters(self):
        """Get filters with dynamic created_by options."""
        filters = super().get_filters()
        
        # Add dynamic created_by options
        if 'created_by' in filters:
            # Get all users who have created company users
            creators = User.objects.filter(
                company_user__isnull=False
            ).distinct().values_list('id', 'username')
            
            creator_options = [
                {'value': str(user_id), 'label': username, 'search_text': username}
                for user_id, username in creators
            ]
            
            filters['created_by']['options'].extend(creator_options)
        
        return filters
    
    def apply_role_filter(self, queryset, filter_values, filter_config):
        """Apply role filter."""
        if 'root' in filter_values:
            queryset = queryset.filter(is_root_user=True)
        if 'sub' in filter_values:
            queryset = queryset.filter(is_root_user=False)
        return queryset
    
    def apply_created_by_filter(self, queryset, filter_values, filter_config):
        """Apply created_by filter."""
        if 'system' in filter_values:
            queryset = queryset.filter(created_by__isnull=True)
        
        # Filter by specific creators
        creator_ids = [v for v in filter_values if v != 'system']
        if creator_ids:
            queryset = queryset.filter(created_by__id__in=creator_ids)
        
        return queryset
    
    def apply_date_filter(self, queryset, filter_values, filter_config):
        """Apply date filter."""
        now = timezone.now()
        
        if 'today' in filter_values:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created_at__gte=today_start)
        
        if 'week' in filter_values:
            week_ago = now - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)
        
        if 'month' in filter_values:
            month_ago = now - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=month_ago)
        
        return queryset


# Alternative: Manual implementation without the mixin
class CompanyUsersManualView(ListView):
    """
    Manual implementation of the data table functionality.
    
    This shows how to implement the data table features without using the mixin,
    giving you full control over the implementation.
    """
    
    model = CompanyUser
    template_name = 'accounts/company_users_example.html'
    context_object_name = 'company_users'
    
    def get_queryset(self):
        """Get queryset with search, filtering, and sorting applied."""
        queryset = CompanyUser.objects.select_related('user', 'created_by')
        
        # Apply search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        # Apply filters
        active_filters = self.get_active_filters()
        queryset = self.apply_filters(queryset, active_filters)
        
        # Apply sorting
        sort_field = self.request.GET.get('sort', 'user__username')
        sort_order = self.request.GET.get('order', 'asc')
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        queryset = queryset.order_by(sort_field)
        
        return queryset
    
    def get_active_filters(self):
        """Get active filters from request."""
        active_filters = {}
        for filter_name in ['role', 'created_by', 'date_filter']:
            values = self.request.GET.getlist(filter_name)
            if values:
                active_filters[filter_name] = values
        return active_filters
    
    def apply_filters(self, queryset, active_filters):
        """Apply filters to queryset."""
        if 'role' in active_filters:
            if 'root' in active_filters['role']:
                queryset = queryset.filter(is_root_user=True)
            if 'sub' in active_filters['role']:
                queryset = queryset.filter(is_root_user=False)
        
        if 'created_by' in active_filters:
            if 'system' in active_filters['created_by']:
                queryset = queryset.filter(created_by__isnull=True)
            creator_ids = [v for v in active_filters['created_by'] if v != 'system']
            if creator_ids:
                queryset = queryset.filter(created_by__id__in=creator_ids)
        
        if 'date_filter' in active_filters:
            now = timezone.now()
            if 'today' in active_filters['date_filter']:
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=today_start)
            if 'week' in active_filters['date_filter']:
                week_ago = now - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=week_ago)
            if 'month' in active_filters['date_filter']:
                month_ago = now - timedelta(days=30)
                queryset = queryset.filter(created_at__gte=month_ago)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Get context data for the template."""
        context = super().get_context_data(**kwargs)
        
        # Get query parameters
        search_query = self.request.GET.get('search', '')
        sort_field = self.request.GET.get('sort', 'user__username')
        sort_order = self.request.GET.get('order', 'asc')
        page_number = self.request.GET.get('page', 1)
        per_page = int(self.request.GET.get('per_page', 25))
        
        # Get visible columns
        visible_columns = self.request.GET.getlist('columns')
        
        # Get active filters
        active_filters = self.get_active_filters()
        
        # Pagination
        paginator = Paginator(self.get_queryset(), per_page)
        page_obj = paginator.get_page(page_number)
        
        # Add data table context
        context.update({
            'company_users': page_obj,
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
            'create_url': reverse('accounts:create_sub_user'),
            'create_text': "Create New User",
            'empty_message': "No users found",
            'empty_action_url': reverse('accounts:create_sub_user'),
            'empty_action_text': "Create First User",
        })
        
        return context
    
    def get_columns(self):
        """Get column configuration."""
        return [
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
        ]
    
    def get_filters(self):
        """Get filter configuration."""
        # Get all users who have created company users
        creators = User.objects.filter(
            company_user__isnull=False
        ).distinct().values_list('id', 'username')
        
        creator_options = [
            {'value': str(user_id), 'label': username, 'search_text': username}
            for user_id, username in creators
        ]
        
        return {
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
                ] + creator_options
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
    
    def get_stats(self):
        """Get stats configuration."""
        return {
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
        }
