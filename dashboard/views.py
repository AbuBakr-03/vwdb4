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
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'active': True}
    ]
    
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
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'Assistants', 'active': True}
    ]
    
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


def phone_numbers(request):
    """Phone Numbers page for managing phone numbers."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'Phone Numbers', 'active': True}
    ]
    
    # Mock phone numbers data - empty state initially
    context['phone_numbers'] = []
    context['has_phone_numbers'] = len(context['phone_numbers']) > 0
    
    return render(request, "dashboard/PhoneNumbers.html", context)


def voice_library(request):
    """Voice Library view with search and filtering."""
    context = {}
    
    # Add tenant info if available
    if hasattr(request, 'tenant_flags'):
        context['tenant_info'] = get_tenant_info(request)
    
    # Organization data for breadcrumbs and components
    context['organization'] = {
        'name': 'Zain Telecom',
        'slug': 'zain_bh',
        'plan': 'Enterprise',
        'credits': 25.50
    }
    
    # Dynamic breadcrumb data
    context['breadcrumb_items'] = [
        {'text': 'Organization', 'href': '/dashboard/'},
        {'text': context['organization']['name'], 'href': '/dashboard/overview/'},
        {'text': 'Voice Library', 'active': True}
    ]
    
    # Mock voice data for demonstration
    recommended_voices = [
        {
            'id': 'aurora-playht',
            'name': 'Aurora',
            'provider': 'PlayHT',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'use_cases': 'Professional, Healthcare',
            'price_min': 0.03,
            'price_max': 0.09,
            'latency_min': 350,
            'latency_max': 600,
            'cover_image': 'https://images.unsplash.com/photo-1494790108755-2616b6ebe55a?w=300&h=300&fit=crop&crop=face',
            'tags': ['Professional', 'Warm', 'Clear']
        },
        {
            'id': 'vits-ara-1',
            'name': 'Vits-ara-1',
            'provider': 'NEETS',
            'gender': 'Male',
            'accent': 'Arabic',
            'language': 'Arabic',
            'use_cases': 'Arabic, Support',
            'price_min': 0.02,
            'price_max': 0.08,
            'latency_min': 300,
            'latency_max': 500,
            'cover_image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face',
            'tags': ['Arabic', 'Native', 'Support']
        },
        {
            'id': 'mady-11labs',
            'name': 'Mady',
            'provider': '11LABS',
            'gender': 'Female',
            'accent': 'Spanish',
            'language': 'Spanish',
            'use_cases': 'Spanish, Commercial',
            'price_min': 0.04,
            'price_max': 0.12,
            'latency_min': 250,
            'latency_max': 450,
            'cover_image': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&h=300&fit=crop&crop=face',
            'tags': ['Commercial', 'Energetic', 'Spanish']
        },
        {
            'id': 'jordan-11labs',
            'name': 'Jordan',
            'provider': '11LABS',
            'gender': 'Male',
            'accent': 'British',
            'language': 'English',
            'use_cases': 'Customer Service, Professional',
            'price_min': 0.04,
            'price_max': 0.12,
            'latency_min': 280,
            'latency_max': 480,
            'cover_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face',
            'tags': ['British', 'Professional', 'Calm']
        }
    ]
    
    # Extended voice library
    all_voices = [
        {
            'id': 'will-playht',
            'name': 'Will',
            'provider': 'PlayHT',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Conversational', 'Friendly'],
            'avatar': 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'charlie-playht',
            'name': 'Charlie',
            'provider': 'PlayHT',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Professional', 'Clear'],
            'avatar': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'beth-gentle',
            'name': 'Beth - Gentle And Nurturing',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Gentle', 'Nurturing', 'Healthcare'],
            'avatar': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'bex-uk-female',
            'name': 'Bex UK Female',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'British',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['UK', 'Professional'],
            'avatar': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'knightley-javier',
            'name': 'Knightley Javier - Calm, Gentle',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'British',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Calm', 'Gentle', 'British'],
            'avatar': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'giovanni-rossi',
            'name': 'Giovanni Rossi - Giovane',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'Italian',
            'language': 'Italian',
            'price': 0.036,
            'latency': 400,
            'tags': ['Italian', 'Youthful'],
            'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'alex-ozwyn',
            'name': 'Alex Ozwyn',
            'provider': 'ElevenLabs',
            'gender': 'Male',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Professional', 'Clear'],
            'avatar': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop&crop=face'
        },
        {
            'id': 'kina-cute-girl',
            'name': 'Kina (Cute Happy Girl) - Perfect For Social Media & Ads',
            'provider': 'ElevenLabs',
            'gender': 'Female',
            'accent': 'American',
            'language': 'English',
            'price': 0.036,
            'latency': 400,
            'tags': ['Happy', 'Social Media', 'Ads'],
            'avatar': 'https://images.unsplash.com/photo-1494790108755-2616b6ebe55a?w=80&h=80&fit=crop&crop=face'
        }
    ]
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    provider_filter = request.GET.getlist('provider')
    gender_filter = request.GET.get('gender', '')
    accent_filter = request.GET.get('accent', '')
    language_filter = request.GET.get('language', '')
    sort_by = request.GET.get('sort', 'popular')
    
    # Apply filters
    filtered_voices = all_voices.copy()
    
    if search_query:
        filtered_voices = [v for v in filtered_voices if 
                          search_query.lower() in v['name'].lower() or 
                          search_query.lower() in v['provider'].lower() or
                          any(search_query.lower() in tag.lower() for tag in v['tags'])]
    
    if provider_filter:
        filtered_voices = [v for v in filtered_voices if v['provider'] in provider_filter]
    
    if gender_filter:
        filtered_voices = [v for v in filtered_voices if v['gender'] == gender_filter]
    
    if accent_filter:
        filtered_voices = [v for v in filtered_voices if v['accent'] == accent_filter]
    
    if language_filter:
        filtered_voices = [v for v in filtered_voices if v['language'] == language_filter]
    
    # Get unique filter options
    providers = list(set(v['provider'] for v in all_voices))
    genders = list(set(v['gender'] for v in all_voices))
    accents = list(set(v['accent'] for v in all_voices))
    languages = list(set(v['language'] for v in all_voices))
    
    context.update({
        'recommended_voices': recommended_voices,
        'all_voices': filtered_voices,
        'search_query': search_query,
        'filters': {
            'providers': providers,
            'genders': genders,
            'accents': accents,
            'languages': languages,
            'selected_provider': provider_filter,
            'selected_gender': gender_filter,
            'selected_accent': accent_filter,
            'selected_language': language_filter,
            'sort_by': sort_by,
        }
    })
    
    return render(request, "dashboard/VoiceLibrary.html", context)