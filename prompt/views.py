from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def prompt_list(request):
    """Main prompts view."""
    context = {
        'section_name': 'Prompts',
        'message': 'Welcome to the Prompts section. This feature is coming soon!',
    }
    return render(request, 'prompt/placeholder.html', context)


@login_required
def agent_playground(request):
    """Agent playground view."""
    context = {
        'section_name': 'Agent Playground',
        'message': 'Welcome to the Agent Playground. Test and refine your AI agents here!',
    }
    return render(request, 'prompt/placeholder.html', context)


@login_required
def voices(request):
    """Voice Library view with search and filtering."""
    
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
    
    context = {
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
    }
    return render(request, 'prompt/voice_library.html', context)