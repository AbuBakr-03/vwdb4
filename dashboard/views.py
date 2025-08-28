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
