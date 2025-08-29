from django.shortcuts import render
from authorization.utils import get_tenant_info
from datetime import datetime, timedelta
import random
import json


def home(request):
    """Dashboard home view with tenant information and KPIs."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Mock KPI data - replace with real data from your models
    context['kpis'] = {
        'monthly_subscription_cost': {
            'value': 2450.00,
            'change': +12.5,
            'currency': 'USD'
        },
        'active_users': {
            'value': 1847,
            'change': +8.3,
            'unit': 'users'
        },
        'performance_score': {
            'value': 87.5,
            'change': -2.1,
            'unit': 'score',
            'max': 100
        },
        'average_duration': {
            'value': 14.2,
            'change': +15.7,
            'unit': 'minutes'
        },
        'upsell_ratio': {
            'value': 23.8,
            'change': +4.2,
            'unit': '%'
        },
        'peak_hour': {
            'value': '14:00',
            'change': 0,
            'unit': 'hour'
        },
        'busiest_day': {
            'value': '2024-06-10',
            'change': 0,
            'unit': 'date'
        }
    }
    
    # Generate mock time series data for charts (last 30 days)
    def generate_time_series(base_value, variance=0.1):
        data = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            # Add some realistic variation
            variation = 1 + random.uniform(-variance, variance)
            value = round(base_value * variation, 2)
            data.append({'date': date, 'value': value})
        return data
    
    # Convert chart data to JSON for JavaScript consumption
    context['chart_data'] = {
        'active_users': json.dumps(generate_time_series(1847, 0.15)),
        'performance_score': json.dumps(generate_time_series(87.5, 0.05)),
        'average_duration': json.dumps(generate_time_series(14.2, 0.2)),
        'monthly_cost': json.dumps(generate_time_series(2450, 0.1))
    }
    
    return render(request, "dashboard/index.html", context)


def overview(request):
    """Overview page for voice AI agents dashboard."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Mock data for overview page - empty state since no calls yet
    context['overview_data'] = {
        'total_calls': 0,
        'success_rate': 0,
        'average_duration': 0,
        'total_cost': 0.00,
        'has_calls': False,
        'assistants': [
            {'name': 'Customer Support', 'active': True},
            {'name': 'Sales Assistant', 'active': False}, 
            {'name': 'Appointment Booking', 'active': True},
        ]
    }
    
    return render(request, "dashboard/Overview.html", context)


def assistants(request):
    """Assistants page with secondary sidebar."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Mock assistants data
    context['assistants'] = [
        {
            'id': 1,
            'name': 'Riley',
            'description': 'Elliot',
            'is_active': True,
            'selected': True
        },
        {
            'id': 2,
            'name': 'Customer Support',
            'description': 'General Support Agent',
            'is_active': True,
            'selected': False
        },
        {
            'id': 3,
            'name': 'Sales Assistant',
            'description': 'Sales Inquiry Handler',
            'is_active': False,
            'selected': False
        },
        {
            'id': 4,
            'name': 'Appointment Booking',
            'description': 'Schedule Management',
            'is_active': True,
            'selected': False
        },
        {
            'id': 5,
            'name': 'Technical Support',
            'description': 'Technical Issue Resolver',
            'is_active': True,
            'selected': False
        },
        {
            'id': 6,
            'name': 'Lead Qualification',
            'description': 'Lead Scoring Agent',
            'is_active': True,
            'selected': False
        }
    ]
    
    return render(request, "dashboard/Assistants.html", context)