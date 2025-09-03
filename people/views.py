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
    
    # Base queryset for contacts (filter by tenant in production)
    contacts = Contact.objects.all()
    
    # Apply filters
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(external_id__icontains=search_query)
        )
    
    # Pagination for contacts
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contacts': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'people/address_book.html', context)


@login_required
def contact_list(request):
    """Display list of contacts with search and filtering."""
    # Get search parameters
    search_query = request.GET.get('search', '')
    
    # Base queryset (filter by tenant in production)
    contacts = Contact.objects.all()
    
    # Apply filters
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(external_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contacts': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'people/contact_list.html', context)


@login_required
def contact_create(request):
    """Create a new contact."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('phone'):
                return JsonResponse({
                    'success': False,
                    'message': 'Phone number is required'
                }, status=400)
            
            # Check for duplicates before creating
            tenant_id = data.get('tenant_id', 'zain_bh')
            phone = data.get('phone', '').strip()
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            external_id = data.get('external_id', '').strip()
            
            # Check for phone duplicates first (most important)
            if phone:
                existing_phone = Contact.objects.filter(
                    tenant_id=tenant_id,
                    phone=phone
                ).first()
                if existing_phone:
                    return JsonResponse({
                        'success': False,
                        'message': f'Contact already exists with phone number "{phone}" ({existing_phone.display_name})'
                    }, status=400)
            
            # Check for email duplicates
            if email:
                existing_email = Contact.objects.filter(
                    tenant_id=tenant_id,
                    email=email
                ).first()
                if existing_email:
                    return JsonResponse({
                        'success': False,
                        'message': f'Contact already exists with email "{email}" ({existing_email.display_name})'
                    }, status=400)
            
            # Check for external_id duplicates
            if external_id:
                existing_external_id = Contact.objects.filter(
                    tenant_id=tenant_id,
                    external_id=external_id
                ).first()
                if existing_external_id:
                    return JsonResponse({
                        'success': False,
                        'message': f'Contact already exists with external ID "{external_id}" ({existing_external_id.display_name})'
                    }, status=400)
            

            
            # Create contact
            contact = Contact.objects.create(
                external_id=data.get('external_id', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                phone=data.get('phone'),
                tenant_id=tenant_id,
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
    
    context = {}
    return render(request, 'people/contact_create.html', context)


@login_required
def contact_edit(request, contact_id):
    """Edit an existing contact."""
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Update contact fields
            contact.external_id = data.get('external_id', contact.external_id)
            contact.first_name = data.get('first_name', contact.first_name)
            contact.last_name = data.get('last_name', contact.last_name)
            contact.email = data.get('email', contact.email)
            contact.phone = data.get('phone', contact.phone)
            
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
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'people/contact_edit.html', context)


@login_required
def contact_delete(request, contact_id):
    """Delete a contact."""
    if request.method == 'POST':
        try:
            contact = get_object_or_404(Contact, id=contact_id)
            contact.delete()
            return JsonResponse({'success': True, 'message': 'Contact deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def contacts_api(request):
    """API endpoint for fetching contacts for campaigns."""
    try:
        # Get search parameters
        search_query = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        # Base queryset - filter by tenant in production
        contacts = Contact.objects.all()
        
        # Apply search filter
        if search_query:
            contacts = contacts.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(external_id__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(contacts, per_page)
        page_obj = paginator.get_page(page)
        
        # Prepare contacts data
        contacts_data = []
        for contact in page_obj:
            contact_data = {
                'id': contact.id,
                'first_name': contact.first_name or '',
                'last_name': contact.last_name or '',
                'name': '',  # Not used for person type
                'email': contact.email or '',
                'company': '',  # Removed
                'contact_person': '',  # Not used for person type
                'party_type': 'person',  # All contacts are persons in current model
                'phones': [contact.phone] if contact.phone else [],
                'external_id': contact.external_id or '',
                'segments': [],  # Removed
                'display_name': contact.display_name,
                'primary_phone': contact.primary_phone
            }
            contacts_data.append(contact_data)
        
        return JsonResponse({
            'success': True,
            'contacts': contacts_data,
            'segments': [],  # Removed segments
            'pagination': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
                    # Parse phone number
                    phone = row.get('phone_number', '').strip()
                    if not phone and row.get('phones'):  # Fallback for backward compatibility
                        phone = row['phones'].strip()
                    
                    # Validate required fields
                    if not (row.get('first_name') or row.get('last_name')):
                        errors.append(f"Row {row_num}: Contact must have first_name or last_name")
                        continue
                    
                    # Validate phone number is required
                    if not phone:
                        errors.append(f"Row {row_num}: Phone number is required")
                        continue
                    
                    # Check for duplicates before creating
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    email = row.get('email', '').strip()
                    external_id = row.get('external_id', '').strip()
                    tenant_id = row.get('tenant_id', 'zain_bh')
                    
                    # Check for phone duplicates first (most important)
                    if phone:
                        existing_phone = Contact.objects.filter(
                            tenant_id=tenant_id,
                            phone=phone
                        ).first()
                        if existing_phone:
                            errors.append(f"Row {row_num}: Contact already exists with phone number '{phone}' ({existing_phone.display_name})")
                            continue
                    
                    # Check for email duplicates
                    if email:
                        existing_email = Contact.objects.filter(
                            tenant_id=tenant_id,
                            email=email
                        ).first()
                        if existing_email:
                            errors.append(f"Row {row_num}: Contact already exists with email '{email}' ({existing_email.display_name})")
                            continue
                    
                    # Check for external_id duplicates
                    if external_id:
                        existing_external_id = Contact.objects.filter(
                            tenant_id=tenant_id,
                            external_id=external_id
                        ).first()
                        if existing_external_id:
                            errors.append(f"Row {row_num}: Contact already exists with external ID '{external_id}' ({existing_external_id.display_name})")
                            continue
                    

                    
                    # Create contact
                    Contact.objects.create(
                        external_id=row.get('external_id', ''),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        email=row.get('email', ''),
                        phone=phone,
                        tenant_id=row.get('tenant_id', 'zain_bh'),
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


@login_required
def placeholder_view(request):
    """Placeholder view for new navigation sections."""
    section_name = request.resolver_match.url_name.replace('_', ' ').title()
    context = {
        'section_name': section_name,
        'message': f'Welcome to the {section_name} section. This feature is coming soon!',
    }
    return render(request, 'people/placeholder.html', context)
