from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
import csv
import io
from .models import Contact, Segment, PartyType


@login_required
def contact_list(request):
    """Display list of contacts with search and filtering."""
    # Get search parameters
    search_query = request.GET.get('search', '')
    party_type = request.GET.get('party_type', '')
    segment_id = request.GET.get('segment', '')
    
    # Base queryset (filter by tenant in production)
    contacts = Contact.objects.all()
    
    # Apply filters
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(external_id__icontains=search_query)
        )
    
    if party_type:
        contacts = contacts.filter(party_type=party_type)
    
    if segment_id:
        contacts = contacts.filter(segments__contains=[int(segment_id)])
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get segments for filter dropdown
    segments = Segment.objects.all()
    
    context = {
        'contacts': page_obj,
        'segments': segments,
        'party_types': PartyType.choices,
        'search_query': search_query,
        'selected_party_type': party_type,
        'selected_segment': segment_id,
    }
    
    return render(request, 'people/contact_list.html', context)


@login_required
def contact_create(request):
    """Create a new contact."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create contact
            contact = Contact.objects.create(
                party_type=data.get('party_type', PartyType.PERSON),
                external_id=data.get('external_id', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                name=data.get('name', ''),
                email=data.get('email', ''),
                phones=data.get('phones', []),
                timezone=data.get('timezone', ''),
                company=data.get('company', ''),
                contact_person=data.get('contact_person', ''),
                segments=data.get('segments', []),
                tenant_id=data.get('tenant_id', 'default'),  # In production, get from request
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Contact created successfully',
                'contact_id': contact.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating contact: {str(e)}'
            }, status=400)
    
    # Get segments for the form
    segments = Segment.objects.all()
    
    context = {
        'segments': segments,
        'party_types': PartyType.choices,
    }
    
    return render(request, 'people/contact_create.html', context)


@login_required
def contact_edit(request, contact_id):
    """Edit an existing contact."""
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Update contact fields
            contact.party_type = data.get('party_type', contact.party_type)
            contact.external_id = data.get('external_id', contact.external_id)
            contact.first_name = data.get('first_name', contact.first_name)
            contact.last_name = data.get('last_name', contact.last_name)
            contact.name = data.get('name', contact.name)
            contact.email = data.get('email', contact.email)
            contact.phones = data.get('phones', contact.phones)
            contact.timezone = data.get('timezone', contact.timezone)
            contact.company = data.get('company', contact.company)
            contact.contact_person = data.get('contact_person', contact.contact_person)
            contact.segments = data.get('segments', contact.segments)
            
            contact.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contact updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating contact: {str(e)}'
            }, status=400)
    
    # Get segments for the form
    segments = Segment.objects.all()
    
    context = {
        'contact': contact,
        'segments': segments,
        'party_types': PartyType.choices,
    }
    
    return render(request, 'people/contact_edit.html', context)


@login_required
def contact_delete(request, contact_id):
    """Delete a contact."""
    if request.method == 'POST':
        try:
            contact = get_object_or_404(Contact, id=contact_id)
            contact.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Contact deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting contact: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def contact_import_csv(request):
    """Import contacts from CSV file."""
    if request.method == 'POST':
        try:
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                return JsonResponse({
                    'success': False,
                    'message': 'No CSV file provided'
                }, status=400)
            
            # Read CSV content
            content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    if not row.get('party_type'):
                        errors.append(f"Row {row_num}: Missing party_type")
                        continue
                    
                    if row['party_type'] == 'person' and not (row.get('first_name') or row.get('last_name')):
                        errors.append(f"Row {row_num}: Person must have first_name or last_name")
                        continue
                    
                    if row['party_type'] == 'company' and not row.get('name'):
                        errors.append(f"Row {row_num}: Company must have name")
                        continue
                    
                    # Parse phones (comma-separated)
                    phones = []
                    if row.get('phones'):
                        phones = [phone.strip() for phone in row['phones'].split(',') if phone.strip()]
                    
                    # Parse segments (comma-separated)
                    segments = []
                    if row.get('segments'):
                        segment_names = [s.strip() for s in row['segments'].split(',') if s.strip()]
                        for segment_name in segment_names:
                            segment, created = Segment.objects.get_or_create(
                                name=segment_name,
                                tenant_id=row.get('tenant_id', 'default'),
                                defaults={
                                    'description': f'Auto-created segment: {segment_name}',
                                    'color': 'badge-outline',
                                    'created_by': request.user
                                }
                            )
                            segments.append(segment.id)
                    
                    # Create contact
                    Contact.objects.create(
                        party_type=row['party_type'],
                        external_id=row.get('external_id', ''),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        phones=phones,
                        timezone=row.get('timezone', ''),
                        company=row.get('company', ''),
                        contact_person=row.get('contact_person', ''),
                        segments=segments,
                        tenant_id=row.get('tenant_id', 'default'),
                        created_by=request.user
                    )
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully imported {imported_count} contacts',
                'imported_count': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing CSV: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def segment_list(request):
    """Display list of segments."""
    segments = Segment.objects.all()
    
    context = {
        'segments': segments,
    }
    
    return render(request, 'people/segment_list.html', context)


@login_required
def segment_create(request):
    """Create a new segment."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            segment = Segment.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                color=data.get('color', 'badge-primary'),
                tenant_id=data.get('tenant_id', 'default'),
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Segment created successfully',
                'segment_id': segment.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating segment: {str(e)}'
            }, status=400)
    
    return render(request, 'people/segment_create.html')


@login_required
def placeholder_view(request):
    """Placeholder view for new navigation sections."""
    section_name = request.resolver_match.url_name.replace('_', ' ').title()
    context = {
        'section_name': section_name,
        'message': f'Welcome to the {section_name} section. This feature is coming soon!',
    }
    return render(request, 'people/placeholder.html', context)
