from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CustomUserCreationForm, SubUserCreationForm
from .models import CompanyUser
from django.contrib.auth.models import User
from .decorators import require_root_user

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/campaigns/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            
            # Get tenant ID from middleware (proper tenant management integration)
            if hasattr(request, 'tenant_flags') and request.tenant_flags:
                tenant_id = request.tenant_flags['tenant_id']
            else:
                # Fallback to default tenant ID from settings
                from django.conf import settings
                tenant_id = getattr(settings, 'TENANT_ID', 'default_company')
            
            # Check if this is the first user for this company (root user)
            is_root_user = CompanyUser.is_first_user(tenant_id)
            
            # Create company user record
            CompanyUser.objects.create(
                user=user,
                company_tenant_id=tenant_id,
                is_root_user=is_root_user,
                created_by=None if is_root_user else None  # Root users have no creator
            )
            
            login(request, user)
            
            if is_root_user:
                messages.success(request, 'Account created successfully! You are the root user for this company.')
            else:
                messages.success(request, 'Account created successfully!')
            
            return redirect('/campaigns/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm(request=request)
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('/accounts/login/')

def access_denied_view(request, error_message=None):
    """Display access denied page for users without proper permissions."""
    context = {
        'error_message': error_message or 'This area requires elevated privileges that your account doesn\'t have.'
    }
    return render(request, 'accounts/access_denied.html', context)

# User Management Views (Root Users Only)

@login_required
@require_root_user
def company_users(request):
    """List all users in the company with sorting, search, and filter capabilities."""
    # Get parameters from URL
    sort_by = request.GET.get('sort', 'created_at')  # Default sort by creation date
    order = request.GET.get('order', 'asc')  # Default ascending order
    
    # Fix malformed sort parameter (in case URL has sort=fieldorder=asc)
    if 'order=' in sort_by:
        sort_by = sort_by.split('order=')[0]
    search_query = request.GET.get('search', '').strip()  # Get search query
    
    # Get filter parameters using getlist for multiple selections
    role_filters = request.GET.getlist('role')
    created_by_filters = request.GET.getlist('created_by')
    date_filters = request.GET.getlist('date_filter')
    
    # Get column visibility parameters
    visible_columns = request.GET.getlist('columns')
    
    # Get pagination parameters
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)  # Default 10 items per page
    
    # Validate sort_by parameter to prevent injection
    valid_sort_fields = {
        'username': 'user__username',
        'email': 'user__email', 
        'role': 'is_root_user',
        'created_at': 'created_at',
        'created_by': 'created_by__username'
    }
    
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'  # Default if invalid
    
    # Get the actual field name for sorting
    sort_field = valid_sort_fields[sort_by]
    
    # Apply sorting
    if order == 'desc':
        sort_field = f'-{sort_field}'
    
    # Get company users base queryset
    company_users_list = request.user.company_user.get_company_users()
    
    # Apply search filtering if search query is provided
    if search_query:
        # Create comprehensive search query across multiple fields
        search_filters = Q(
            # Search in username
            user__username__icontains=search_query
        ) | Q(
            # Search in email
            user__email__icontains=search_query
        ) | Q(
            # Search in created_by username
            created_by__username__icontains=search_query
        )
        
        # Handle role-based searches
        search_lower = search_query.lower()
        if search_lower in ['root', 'admin', 'administrator', 'root user']:
            search_filters |= Q(is_root_user=True)
        elif search_lower in ['sub', 'user', 'regular', 'sub user', 'regular user']:
            search_filters |= Q(is_root_user=False)
        
        # Apply search filter
        company_users_list = company_users_list.filter(search_filters)
    
    # Apply role filters
    if role_filters:
        role_conditions = Q()
        
        for role in role_filters:
            if role == 'root':
                role_conditions |= Q(is_root_user=True)
            elif role == 'sub':
                role_conditions |= Q(is_root_user=False)
        
        if role_conditions:
            company_users_list = company_users_list.filter(role_conditions)
    
    # Apply created_by filters
    if created_by_filters:
        created_by_conditions = Q()
        
        for creator in created_by_filters:
            if creator == 'system':
                created_by_conditions |= Q(created_by__isnull=True)
            else:
                try:
                    creator_id = int(creator)
                    created_by_conditions |= Q(created_by_id=creator_id)
                except ValueError:
                    # Skip invalid creator IDs
                    pass
        
        if created_by_conditions:
            company_users_list = company_users_list.filter(created_by_conditions)
    
    # Apply date filters
    if date_filters:
        date_conditions = Q()
        now = timezone.now()
        
        for date_filter in date_filters:
            if date_filter == 'today':
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                date_conditions |= Q(created_at__gte=today_start)
            elif date_filter == 'week':
                week_start = now - timedelta(days=now.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                date_conditions |= Q(created_at__gte=week_start)
            elif date_filter == 'month':
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                date_conditions |= Q(created_at__gte=month_start)
        
        if date_conditions:
            company_users_list = company_users_list.filter(date_conditions)
    
    # Apply sorting to the filtered queryset
    company_users_list = company_users_list.order_by(sort_field)
    
    # Pagination
    try:
        per_page = int(per_page)
        if per_page < 1:
            per_page = 5
        elif per_page > 100:  # Limit maximum items per page
            per_page = 100
    except (ValueError, TypeError):
        per_page = 5
    
    paginator = Paginator(company_users_list, per_page)
    
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    try:
        company_users_page = paginator.page(page)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        company_users_page = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        company_users_page = paginator.page(1)
    
    # Get available creators for filter dropdown
    available_creators = User.objects.filter(
        company_user__company_tenant_id=request.user.company_user.company_tenant_id,
        company_user__is_root_user=True
    ).distinct()
    
    # Prepare active filters for template
    active_filters = {}
    if role_filters:
        active_filters['role'] = role_filters
    if created_by_filters:
        active_filters['created_by'] = created_by_filters
    if date_filters:
        active_filters['date_filter'] = date_filters
    
    context = {
        'company_users': company_users_page,
        'total_users': company_users_list.count(),
        'root_users': company_users_list.filter(is_root_user=True).count(),
        'sub_users': company_users_list.filter(is_root_user=False).count(),
        'current_sort': sort_by,
        'current_order': order,
        'search_query': search_query,
        'active_filters': active_filters,
        'available_creators': available_creators,
        'visible_columns': visible_columns,
        'role_filters': role_filters,
        'created_by_filters': created_by_filters,
        'date_filters': date_filters,
        'paginator': paginator,
        'page_obj': company_users_page,
        'current_page': page,
        'per_page': per_page,
    }
    
    return render(request, 'accounts/company_users.html', context)

@login_required
@require_root_user
def create_sub_user(request):
    """Create a new sub-user in the company."""
    if request.method == 'POST':
        form = SubUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create the sub-user
                user = form.save(created_by_user=request.user)
                messages.success(request, f'User "{user.username}" created successfully!')
                return redirect('accounts:company_users')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubUserCreationForm()
    
    # Get company name from tenant flags or fallback to user's company
    if hasattr(request, 'tenant_flags') and request.tenant_flags:
        company_name = request.tenant_flags['tenant_id'].replace('_', ' ').title()
    elif hasattr(request.user, 'company_user') and request.user.company_user:
        company_name = request.user.company_user.company_tenant_id.replace('_', ' ').title()
    else:
        company_name = 'Company'  # Fallback
    
    context = {
        'form': form,
        'company_name': company_name,
    }
    
    return render(request, 'accounts/create_sub_user.html', context)

# Test view for the new data table component
@login_required
@require_root_user
def company_users_data_table_test(request):
    """Test view for the new modular data table component."""
    from utils.data_table_mixin import DataTableListView
    from django.views.generic import View
    from django.contrib.auth.models import User
    
    # Get query parameters
    search_query = request.GET.get('search', '')
    sort_field = request.GET.get('sort', 'user__username')
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
    queryset = CompanyUser.objects.select_related('user', 'created_by')
    
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
    
    # Apply sorting
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'
    queryset = queryset.order_by(sort_field)
    
    # Pagination
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Get all users who have created company users for filter options
    creators = User.objects.filter(
        company_user__isnull=False
    ).distinct().values_list('id', 'username')
    
    creator_options = [
        {'value': str(user_id), 'label': username, 'search_text': username}
        for user_id, username in creators
    ]
    
    # Prepare context
    context = {
        'table_data': page_obj,  # Changed from company_users to table_data
        'page_obj': page_obj,
        'paginator': paginator,
        'current_sort': request.GET.get('sort', 'user__username'),
        'current_order': request.GET.get('order', 'asc'),
        'active_filters': active_filters,
        'visible_columns': visible_columns,
        'per_page': per_page,
        'search_query': search_query,  # This is already correct
        'create_url': '/accounts/users/create/',
        
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
    

    return render(request, 'accounts/company_users_example.html', context)


