from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from typing import Any, Dict
import json

from .models import Ticket, TicketComment, TicketAttachment, Company, QATester
from .forms import (
    TicketForm, TicketCommentForm, TicketAttachmentForm, 
    CompanyForm, QATesterForm, TicketFilterForm
)
from accounts.models import CompanyUser


class TicketListView(LoginRequiredMixin, ListView):
    """
    View for listing tickets with filtering and search capabilities.
    """
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        """Get filtered queryset based on user role and filters."""
        queryset = Ticket.objects.select_related(
            'submitter', 'assigned_to', 'company'
        ).prefetch_related('attachments')
        
        # Apply user-specific filtering
        if not self.request.user.is_staff:
            # Non-staff users see only their own tickets
            queryset = queryset.filter(submitter=self.request.user)
        
        # Apply filters from form
        form = TicketFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            if form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority=form.cleaned_data['priority'])
            
            if form.cleaned_data.get('issue_location'):
                queryset = queryset.filter(issue_location=form.cleaned_data['issue_location'])
            
            if form.cleaned_data.get('assigned_to'):
                queryset = queryset.filter(assigned_to=form.cleaned_data['assigned_to'])
            
            if form.cleaned_data.get('company'):
                queryset = queryset.filter(company=form.cleaned_data['company'])
            
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(created_at__date__gte=form.cleaned_data['date_from'])
            
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(created_at__date__lte=form.cleaned_data['date_to'])
            
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(description__icontains=search_term) |
                    Q(additional_notes__icontains=search_term) |
                    Q(submitter__username__icontains=search_term) |
                    Q(submitter__first_name__icontains=search_term) |
                    Q(submitter__last_name__icontains=search_term)
                )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add filter form and statistics to context."""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TicketFilterForm(self.request.GET)
        
        # Add statistics
        if self.request.user.is_staff:
            context['stats'] = {
                'total_tickets': Ticket.objects.count(),
                'open_tickets': Ticket.objects.filter(status='open').count(),
                'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
                'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
            }
        else:
            user_tickets = Ticket.objects.filter(submitter=self.request.user)
            context['stats'] = {
                'total_tickets': user_tickets.count(),
                'open_tickets': user_tickets.filter(status='open').count(),
                'in_progress_tickets': user_tickets.filter(status='in_progress').count(),
                'resolved_tickets': user_tickets.filter(status='resolved').count(),
            }
        
        return context


class TicketDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying ticket details with comments and attachments.
    """
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = Ticket.objects.select_related(
            'submitter', 'assigned_to', 'company'
        ).prefetch_related('comments__author', 'attachments')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(submitter=self.request.user)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add forms and related data to context."""
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TicketCommentForm(user=self.request.user)
        context['attachment_form'] = TicketAttachmentForm()
        
        # Filter comments based on user permissions
        if self.request.user.is_staff:
            context['comments'] = self.object.comments.all()
        else:
            context['comments'] = self.object.comments.filter(is_internal=False)
        
        # Add QA users for assignment dropdown
        if self.request.user.is_staff:
            from django.contrib.auth.models import User
            context['qa_users'] = User.objects.filter(
                models.Q(is_staff=True) | 
                models.Q(groups__name='QA Personnel')
            ).distinct()
        
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new tickets.
    """
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    success_url = reverse_lazy('tickets:ticket_list')
    
    def get_form_kwargs(self):
        """Pass user to form for proper field filtering."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Set submitter and company before saving."""
        form.instance.submitter = self.request.user
        
        # Set company if user is a QA tester
        try:
            qa_tester = self.request.user.qa_tester
            form.instance.company = qa_tester.company
        except QATester.DoesNotExist:
            pass
        
        messages.success(self.request, 'Ticket created successfully!')
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating tickets (staff only or ticket submitter).
    """
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def test_func(self):
        """Check if user can edit this ticket."""
        ticket = self.get_object()
        return (
            self.request.user.is_staff or 
            ticket.submitter == self.request.user
        )
    
    def get_form_kwargs(self):
        """Pass user to form for proper field filtering."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Handle status changes and assignment."""
        old_status = self.object.status
        new_status = form.cleaned_data.get('status')
        
        # Set resolved_at timestamp when status changes to resolved
        if old_status != 'resolved' and new_status == 'resolved':
            form.instance.resolved_at = timezone.now()
        
        messages.success(self.request, 'Ticket updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to ticket detail page."""
        return reverse('tickets:ticket_detail', kwargs={'pk': self.object.pk})


@login_required
@require_POST
def add_comment(request, ticket_id):
    """Add a comment to a ticket."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # Check permissions
    if not request.user.is_staff and ticket.submitter != request.user:
        return HttpResponseForbidden("You don't have permission to comment on this ticket.")
    
    form = TicketCommentForm(request.POST, user=request.user)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.author = request.user
        comment.save()
        
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Error adding comment. Please check your input.')
    
    return redirect('tickets:ticket_detail', pk=ticket_id)


@login_required
@require_POST
def add_attachment(request, ticket_id):
    """Add an attachment to a ticket."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # Check permissions
    if not request.user.is_staff and ticket.submitter != request.user:
        return HttpResponseForbidden("You don't have permission to add attachments to this ticket.")
    
    form = TicketAttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        attachment = form.save(commit=False)
        attachment.ticket = ticket
        attachment.uploaded_by = request.user
        attachment.filename = request.FILES['file'].name
        attachment.file_size = request.FILES['file'].size
        attachment.save()
        
        messages.success(request, 'Attachment uploaded successfully!')
    else:
        messages.error(request, 'Error uploading attachment. Please check your file.')
    
    return redirect('tickets:ticket_detail', pk=ticket_id)


class CompanyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View for listing companies (staff only).
    """
    model = Company
    template_name = 'tickets/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        """Add statistics to context."""
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'total_companies': Company.objects.count(),
            'active_companies': Company.objects.filter(is_active=True).count(),
            'total_testers': QATester.objects.filter(is_active=True).count(),
        }
        return context


class CompanyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View for creating companies (staff only).
    """
    model = Company
    form_class = CompanyForm
    template_name = 'tickets/company_form.html'
    success_url = reverse_lazy('tickets:company_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Company created successfully!')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating companies (staff only).
    """
    model = Company
    form_class = CompanyForm
    template_name = 'tickets/company_form.html'
    success_url = reverse_lazy('tickets:company_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Company updated successfully!')
        return super().form_valid(form)


class QATesterListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View for listing QA testers (staff only).
    """
    model = QATester
    template_name = 'tickets/qa_tester_list.html'
    context_object_name = 'qa_testers'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return QATester.objects.select_related('user', 'company').order_by('user__username')


class QATesterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View for creating QA testers (staff only).
    """
    model = QATester
    form_class = QATesterForm
    template_name = 'tickets/qa_tester_form.html'
    success_url = reverse_lazy('tickets:qa_tester_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'QA Tester created successfully!')
        return super().form_valid(form)


@login_required
def dashboard(request):
    """
    Dashboard view showing ticket overview and statistics.
    """
    if not request.user.is_staff:
        # Redirect non-staff users to their ticket list
        return redirect('tickets:ticket_list')
    
    # Get statistics
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    
    # Get recent tickets
    recent_tickets = Ticket.objects.select_related(
        'submitter', 'assigned_to', 'company'
    ).order_by('-created_at')[:10]
    
    # Get tickets by status
    tickets_by_status = Ticket.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Get tickets by priority
    tickets_by_priority = Ticket.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'recent_tickets': recent_tickets,
        'tickets_by_status': tickets_by_status,
        'tickets_by_priority': tickets_by_priority,
    }
    
    return render(request, 'tickets/dashboard.html', context)


@login_required
@require_POST
def update_ticket_status(request, ticket_id):
    """Update ticket status via AJAX."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Ticket.STATUS_CHOICES):
        old_status = ticket.status
        ticket.status = new_status
        
        # Set resolved_at timestamp when status changes to resolved
        if old_status != 'resolved' and new_status == 'resolved':
            ticket.resolved_at = timezone.now()
        
        ticket.save()
        
        return JsonResponse({
            'success': True,
            'status': new_status,
            'status_display': dict(Ticket.STATUS_CHOICES)[new_status]
        })
    
    return JsonResponse({'error': 'Invalid status'}, status=400)


@login_required
@require_POST
def assign_ticket(request, ticket_id):
    """Assign ticket to QA personnel via AJAX."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    user_id = request.POST.get('user_id')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if ticket.can_be_assigned(user):
                ticket.assigned_to = user
                ticket.save()
                return JsonResponse({
                    'success': True,
                    'assigned_to': user.username,
                    'assigned_to_id': user.id
                })
            else:
                return JsonResponse({'error': 'User cannot be assigned to tickets'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        # Unassign ticket
        ticket.assigned_to = None
        ticket.save()
        return JsonResponse({'success': True, 'assigned_to': None})
