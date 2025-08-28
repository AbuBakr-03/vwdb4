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
    """Voices management view."""
    context = {
        'section_name': 'Voices',
        'message': 'Welcome to the Voices section. Manage your AI voice settings here!',
    }
    return render(request, 'prompt/placeholder.html', context)