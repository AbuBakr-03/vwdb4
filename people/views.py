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
from .models import Contact, Segment


@login_required
def address_book(request):
    """Main address book page with tabs for contacts and segments."""
    # Get search parameters
    search_query = request.GET.get('search', '')
    segment_id = request.GET.get('segment', '')
    
    # Base queryset for contacts (filter by tenant in production)
    contacts = Contact.objects.all()
    
    # Apply filters
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(external_id__icontains=search_query)
        )
    
    if segment_id:
        contacts = contacts.filter(segments__contains=[int(segment_id)])
    
    # Pagination for contacts
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all segments
    segments = Segment.objects.all()
    
    context = {
        'contacts': page_obj,
        'segments': segments,
        'search_query': search_query,
        'selected_segment': segment_id,
    }
    
    return render(request, 'people/address_book.html', context)


@login_required
def contact_list(request):
    """Display list of contacts with search and filtering."""
    # Get search parameters
    search_query = request.GET.get('search', '')
    segment_id = request.GET.get('segment', '')
    
    # Base queryset (filter by tenant in production)
    contacts = Contact.objects.all()
    
    # Apply filters
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(external_id__icontains=search_query)
        )
    
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
        'search_query': search_query,
        'selected_segment': segment_id,
    }
    
    return render(request, 'people/contact_list.html', context)


@login_required
def contact_create(request):
    """Create a new contact."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Handle segment creation/selection
            segment_ids = data.get('segments', [])
            new_segment_names = data.get('new_segment_names', [])
            
            # Create new segments if they don't exist
            if new_segment_names:
                for segment_name in new_segment_names:
                    segment_name = segment_name.strip()
                    if segment_name:
                        # Check if segment already exists
                        segment, created = Segment.objects.get_or_create(
                            name=segment_name,
                            defaults={
                                'description': f'Auto-created segment: {segment_name}',
                                'color': 'badge-primary',  # Default color
                                'created_by': request.user
                            }
                        )
                        # Add the segment ID to the segments list if not already present
                        if segment.id not in segment_ids:
                            segment_ids.append(segment.id)
            
            # Create contact
            contact = Contact.objects.create(
                external_id=data.get('external_id', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                phones=data.get('phones', []),
                timezone=data.get('timezone', ''),
                company=data.get('company', ''),
                segments=segment_ids,
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
    }
    
    return render(request, 'people/contact_create.html', context)


@login_required
def contact_edit(request, contact_id):
    """Edit an existing contact."""
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Handle segment creation/selection
            segment_ids = data.get('segments', contact.segments)
            new_segment_names = data.get('new_segment_names', [])
            
            # Create new segments if they don't exist
            if new_segment_names:
                for segment_name in new_segment_names:
                    segment_name = segment_name.strip()
                    if segment_name:
                        # Check if segment already exists
                        segment, created = Segment.objects.get_or_create(
                            name=segment_name,
                            defaults={
                                'description': f'Auto-created segment: {segment_name}',
                                'color': 'badge-primary',  # Default color
                                'created_by': request.user
                            }
                        )
                        # Add the segment ID to the segments list if not already present
                        if segment.id not in segment_ids:
                            segment_ids.append(segment.id)
            
            # Update contact fields
            contact.external_id = data.get('external_id', contact.external_id)
            contact.first_name = data.get('first_name', contact.first_name)
            contact.last_name = data.get('last_name', contact.last_name)
            contact.email = data.get('email', contact.email)
            contact.phones = data.get('phones', contact.phones)
            contact.timezone = data.get('timezone', contact.timezone)
            contact.company = data.get('company', contact.company)
            contact.segments = segment_ids
            
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
                    if not (row.get('first_name') or row.get('last_name')):
                        errors.append(f"Row {row_num}: Contact must have first_name or last_name")
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
                                defaults={
                                    'description': f'Auto-created segment: {segment_name}',
                                    'color': 'badge-primary',
                                    'created_by': request.user
                                }
                            )
                            segments.append(segment.id)
                    
                    # Create contact
                    Contact.objects.create(
                        external_id=row.get('external_id', ''),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        email=row.get('email', ''),
                        phones=phones,
                        timezone=row.get('timezone', ''),
                        company=row.get('company', ''),
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
