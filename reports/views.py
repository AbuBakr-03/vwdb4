from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def reports_overview(request):
    """Reports overview view."""
    context = {
        'section_name': 'Reports Overview',
        'message': 'Welcome to the Reports section. Analytics and insights coming soon!',
    }
    return render(request, 'reports/placeholder.html', context)


@login_required
def exports(request):
    """Reports exports view."""
    context = {
        'section_name': 'Reports Exports',
        'message': 'Welcome to the Exports section. Download your data and reports here!',
    }
    return render(request, 'reports/placeholder.html', context)