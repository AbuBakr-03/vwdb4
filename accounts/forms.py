from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Enter your email address'
        })
    )
    
    tenant_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full bg-gray-100',
            'readonly': 'readonly',
            'placeholder': 'Tenant ID will be automatically set'
        }),
        help_text="The tenant/company you will be registering for"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'tenant_id', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Update field widgets to match dashboard styling
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirm your password'
        })
        
        # Set tenant ID from request if available
        if request and hasattr(request, 'tenant_flags'):
            self.fields['tenant_id'].initial = request.tenant_flags['tenant_id']
            self.fields['tenant_id'].widget.attrs['value'] = request.tenant_flags['tenant_id']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SubUserCreationForm(UserCreationForm):
    """
    Form for root users to create sub-users in their company.
    Similar to CustomUserCreationForm but for internal user creation.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Enter email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update field widgets to match dashboard styling
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email
    
    def save(self, created_by_user, commit=True):
        """
        Save the sub-user and link them to the company.
        created_by_user should be the root user creating this sub-user.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            # Create CompanyUser record for the sub-user
            from .models import CompanyUser
            CompanyUser.objects.create(
                user=user,
                company_tenant_id=created_by_user.company_user.company_tenant_id,
                is_root_user=False,  # Sub-users are never root users
                created_by=created_by_user
            )
        
        return user

