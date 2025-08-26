from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from .models import Ticket, TicketComment, TicketAttachment, Company, QATester


class TicketForm(forms.ModelForm):
    """
    Form for creating and editing tickets.
    """
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'issue_location', 'additional_notes', 
            'priority', 'status', 'assigned_to'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-32',
                'placeholder': 'Detailed explanation of the problem...'
            }),
            'issue_location': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-24',
                'placeholder': 'Optional notes or clarifications...'
            }),
            'priority': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to choices to only QA personnel
        if user and not user.is_staff:
            # For non-staff users, hide assignment field
            self.fields.pop('assigned_to', None)
            self.fields.pop('status', None)
        else:
            # For staff users, show only QA personnel in assignment
            qa_users = User.objects.filter(
                models.Q(is_staff=True) | 
                models.Q(groups__name='QA Personnel')
            ).distinct()
            self.fields['assigned_to'].queryset = qa_users
            self.fields['assigned_to'].empty_label = "Select QA personnel..."
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        
        # If status is 'in_progress' or 'resolved', require assignment
        if status in ['in_progress', 'resolved'] and not assigned_to:
            raise ValidationError(
                "Tickets must be assigned to QA personnel when status is 'In Progress' or 'Resolved'"
            )
        
        return cleaned_data


class TicketCommentForm(forms.ModelForm):
    """
    Form for adding comments to tickets.
    """
    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-24',
                'placeholder': 'Add your comment...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only staff users can create internal comments
        if not user or not user.is_staff:
            self.fields.pop('is_internal', None)


class TicketAttachmentForm(forms.ModelForm):
    """
    Form for uploading file attachments to tickets.
    """
    class Meta:
        model = TicketAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': '.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt'
            }),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size must be less than 10MB.")
            
            # Check file extension
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return file


class CompanyForm(forms.ModelForm):
    """
    Form for creating and editing companies.
    """
    class Meta:
        model = Company
        fields = ['name', 'description', 'contact_email', 'contact_phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Company name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-24',
                'placeholder': 'Company description...'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'contact@company.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '+1234567890'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }


class QATesterForm(forms.ModelForm):
    """
    Form for creating QA testers.
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        }),
        help_text="Select the user to assign as QA tester"
    )
    
    class Meta:
        model = QATester
        fields = ['user', 'company', 'is_active']
        widgets = {
            'company': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        company = cleaned_data.get('company')
        
        # Check if user is already a QA tester
        if user and QATester.objects.filter(user=user).exists():
            raise ValidationError(
                f"User {user.username} is already assigned as a QA tester."
            )
        
        return cleaned_data


class TicketFilterForm(forms.Form):
    """
    Form for filtering tickets in the dashboard.
    """
    STATUS_CHOICES = [('', 'All Statuses')] + Ticket.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'All Priorities')] + Ticket.PRIORITY_CHOICES
    MODULE_CHOICES = [('', 'All Modules')] + Ticket.MODULE_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    issue_location = forms.ChoiceField(
        choices=MODULE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(
            models.Q(is_staff=True) | 
            models.Q(groups__name='QA Personnel')
        ).distinct(),
        required=False,
        empty_label="All Assignees",
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        empty_label="All Companies",
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Search tickets...'
        })
    )
